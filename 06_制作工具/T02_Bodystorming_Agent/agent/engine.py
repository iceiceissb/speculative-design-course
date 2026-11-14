import copy
import json
import threading
import time
import uuid
from pathlib import Path

from . import demo
from .knowledge import retrieve
from .model import AgentError
from .storage import now

ROOT = Path(__file__).resolve().parent.parent
NODES = [
    dict(id='distill', name='剧情提炼', kind='模型', description='保留目标、角色、实际道具与硬限制。', prompt='distill.md'),
    dict(id='retrieve_events', name='资料检索', kind='本地检索', description='中文双字与英文词检索资料片段，保留来源。', prompt=None),
    dict(id='events', name='事件生成', kind='模型', description='生成五个不同的课堂扰动，绑定原始约束和检索片段。', prompt='events.md'),
    dict(id='validate', name='输出检查', kind='程序', description='检查数量、事件编号、字段和引用 ID；失败即停止。', prompt=None),
    dict(id='select', name='人工选择', kind='人', description='选中完整事件，切换事件时清空当前提示历史。', prompt=None),
    dict(id='observe', name='观察整理', kind='人 / 可选视觉', description='勾选实际观察、补充对话或确认照片描述；不自动诊断情绪。', prompt='observe.md'),
    dict(id='policy', name='介入决策', kind='规则', description='参与者指定当前状态；系统选择 L0、待确认或 L1–L3。', prompt=None),
    dict(id='retrieve_guide', name='支持检索', kind='本地检索', description='依据选中事件和最新观察重新检索，避免只使用初始剧情。', prompt=None),
    dict(id='guide', name='分级提示', kind='模型 / 规则', description='L0 与待确认直接返回；其余按级别生成，不替学生写完整方案。', prompt='guide.md'),
    dict(id='reflect', name='记录反思', kind='程序', description='记录提示、采纳与拒绝，并按实际记录导出反思问题。', prompt=None),
]


def prompt(name):
    return (ROOT / 'prompts' / name).read_text(encoding='utf-8')


def required_text(result, names):
    if not isinstance(result, dict) or any(not isinstance(result.get(k), str) or not result[k].strip() for k in names):
        raise AgentError('节点输出缺少必要文本字段，请在运行记录查看失败节点后重试。')


def check_references(result, evidence):
    refs = result.get('evidence_ids', [])
    allowed = {item['id'] for item in evidence}
    if not isinstance(refs, list) or any(not isinstance(ref, str) or ref not in allowed for ref in refs):
        raise AgentError('节点引用了本次检索中不存在的资料 ID。本次输出未被采用。')


class Engine:
    def __init__(self, store, model):
        self.store, self.model = store, model
        self.locks = {}
        self.guard = threading.Lock()

    def lock(self, sid):
        with self.guard:
            lock = self.locks.setdefault(sid, threading.Lock())
        if not lock.acquire(blocking=False):
            raise AgentError('这组演练正在运行，请等待当前步骤完成。')
        return lock

    def trace(self, doc, node, inputs, fn, kind=None):
        info = next(n for n in NODES if n['id'] == node)
        record = dict(id=uuid.uuid4().hex, node=node, name=info['name'], kind=kind or info['kind'],
                      mode=doc['mode'], started_at=now(), status='running', inputs=copy.deepcopy(inputs), output=None)
        if record['kind'] == '模型' and hasattr(self.model, 'public'):
            record['model_config'] = self.model.public()
        doc['logs'].append(record)
        self.store.save(doc)
        started = time.monotonic()
        try:
            output = fn()
            record.update(status='done', output=copy.deepcopy(output))
            return output
        except Exception as exc:
            record.update(status='error', error=str(exc) if isinstance(exc, AgentError) else '本地节点执行失败。')
            raise
        finally:
            record['duration_ms'] = round((time.monotonic()-started)*1000)
            self.store.save(doc)

    def generate(self, sid):
        lock = self.lock(sid)
        try:
            doc = self.store.get(sid)
            if not doc['story'].strip() or not doc['constraints'].strip():
                raise AgentError('请先填写剧本与课堂约束。')
            doc.update(events=[], selected_event=None, hints=[], summary=None, presentation=None)
            doc['revision'] += 1
            self.store.save(doc)
            payload = {k: doc[k] for k in ('story', 'constraints', 'participants', 'remaining')}
            payload['activity_config'] = doc.get('activity_config')
            summary = self.trace(doc, 'distill', payload,
                lambda: demo.summary(payload) if doc['mode'] == 'demo' else self.model.complete(prompt('distill.md'), payload),
                kind='手写演示' if doc['mode'] == 'demo' else '模型')
            required_text(summary, ('scene', 'goal', 'constraints', 'resources', 'missing'))
            doc['summary'] = summary
            evidence = self.trace(doc, 'retrieve_events', {'query': doc['story'] + doc['constraints']},
                lambda: retrieve(self.store.documents(), doc['story'] + doc['constraints']))
            inputs = payload | dict(summary=summary, evidence=evidence)
            result = self.trace(doc, 'events', inputs,
                lambda: {'events': copy.deepcopy(demo.EVENTS)} if doc['mode'] == 'demo' else self.model.complete(prompt('events.md'), inputs),
                kind='手写演示' if doc['mode'] == 'demo' else '模型')

            def validate():
                events = result.get('events')
                if not isinstance(events, list) or len(events) != 5:
                    raise AgentError('事件节点没有返回恰好 5 个事件，请重新生成。')
                for i, event in enumerate(events):
                    required_text(event, ('id', 'title', 'type', 'content', 'body_hint', 'fiction'))
                    if event['id'] != f'E{i+1}':
                        raise AgentError('事件编号必须依次为 E1 至 E5。')
                    check_references(event, evidence)
                if len({event['type'] for event in events}) < 3:
                    raise AgentError('候选事件至少需要 3 个类型标签；标签不同仍不保证实质多样，需要人工复核。')
                return {'count': 5, 'references': '引用 ID 存在性检查通过；来源能否支撑断言仍需人工核对。'}

            self.trace(doc, 'validate', {'result': result}, validate)
            doc['events'] = result['events']
            self.store.save(doc)
            return doc
        finally:
            lock.release()

    def select(self, sid, event_id):
        lock = self.lock(sid)
        try:
            doc = self.store.get(sid)
            found = next((e for e in doc['events'] if e['id'] == event_id), None)
            if not found:
                raise AgentError('请选择本次真实生成的一个完整事件。')
            if doc['selected_event'] != found:
                doc['selected_event'], doc['hints'], doc['observation'] = found, [], ''
                doc['presentation'] = None
            self.trace(doc, 'select', {'event_id': event_id}, lambda: found)
            return doc
        finally:
            lock.release()

    def guide(self, sid, observation, state):
        lock = self.lock(sid)
        try:
            doc = self.store.get(sid)
            if not doc['selected_event']:
                raise AgentError('请先选择一个突发事件。')
            if not observation.strip():
                raise AgentError('请填写一句现场观察，不能凭空推断表演状态。')
            if state not in ('exploring', 'uncertain', 'help', 'more', 'example'):
                raise AgentError('请选择当前需要的支持程度。')
            doc['observation'] = observation
            history = [{k: h[k] for k in ('message', 'level', 'feedback')} for h in doc['hints']]
            self.trace(doc, 'observe', {'origin': '人工输入或用户确认的转写/照片描述'}, lambda: {'observation': observation})
            previous_l1 = any(h['level'] in ('L1', 'L2', 'L3') and h['feedback'] != 'not_shown' for h in doc['hints'])
            level = {'exploring': 'L0', 'uncertain': 'confirm', 'help': 'L1', 'more': 'L2' if previous_l1 else 'L1', 'example': 'L3'}[state]
            self.trace(doc, 'policy', {'state': state, 'prior_support': previous_l1},
                       lambda: {'level': level, 'reason': '依据用户选择的现场状态；未自动识别停滞或情绪。'})
            evidence = self.trace(doc, 'retrieve_guide', {'query': doc['selected_event']['content'] + observation},
                lambda: retrieve(self.store.documents(), doc['selected_event']['content'] + observation))
            payload = dict(story=doc['story'], constraints=doc['constraints'], participants=doc['participants'], remaining=doc['remaining'],
                           selected_event=doc['selected_event'], observation=observation, previous_hints=history, level=level, evidence=evidence,
                           activity_config=doc.get('activity_config'))

            def produce():
                if doc['mode'] == 'demo':
                    return demo.guidance(level, doc['selected_event'], observation)
                if level in ('L0', 'confirm'):
                    return dict(understanding=doc['selected_event']['content'], basis=observation, level=level,
                        message='继续当前探索，暂不追加提示。' if level == 'L0' else '你们希望继续自主探索，还是需要一点提示？',
                        next_observation='团队是否主动提出需要帮助。', knowledge_status='程序规则输出，未调用模型，不涉及新的领域结论。', evidence_ids=[])
                return self.model.complete(prompt('guide.md'), payload)

            rule = level in ('L0', 'confirm') and doc['mode'] != 'demo'
            answer = self.trace(doc, 'guide', payload, produce, kind='规则' if rule else ('手写演示' if doc['mode'] == 'demo' else '模型'))
            def validate_answer():
                required_text(answer, ('understanding', 'basis', 'level', 'message', 'next_observation', 'knowledge_status'))
                if answer['level'] != level:
                    raise AgentError('模型返回的支持级别与本次决策不符，已停止采用这条提示。')
                check_references(answer, evidence)
                return {'level': level, 'checked': True, 'note': '字段与引用 ID 检查，不代表领域事实验证。'}
            self.trace(doc, 'validate', {'result': answer}, validate_answer)
            answer.update(id=uuid.uuid4().hex, feedback='not_shown', created_at=now(), observation=observation, evidence=evidence)
            doc['hints'].append(answer)
            self.trace(doc, 'reflect', {'hint_id': answer['id']}, lambda: {'recorded': True, 'reflection': '你采纳、修改或拒绝了哪一部分？它改变了哪些动作或设计选择？'})
            self.store.save(doc)
            return doc
        finally:
            lock.release()

    def feedback(self, sid, hint_id, feedback):
        if feedback not in ('offered', 'adopted', 'rejected', 'not_shown'):
            raise AgentError('反馈类型不正确。')
        lock = self.lock(sid)
        try:
            doc = self.store.get(sid)
            found = next((h for h in doc['hints'] if h['id'] == hint_id), None)
            if not found:
                raise AgentError('找不到这条提示。')
            found['feedback'] = feedback
            self.store.save(doc)
            return doc
        finally:
            lock.release()

    def present(self, sid, kind, hint_id=None):
        lock = self.lock(sid)
        try:
            doc = self.store.get(sid)
            if kind not in ('event', 'hint', 'blank'):
                raise AgentError('请选择投屏事件、提示或留白。')
            if kind != 'blank' and not doc['selected_event']:
                raise AgentError('先由学生选定一个事件。')
            view = dict(kind=kind, published_at=now())
            if kind != 'blank':
                view['event'] = {k: doc['selected_event'][k] for k in ('title', 'content', 'fiction')}
            if kind == 'hint':
                hint = next((h for h in doc['hints'] if h['id'] == hint_id), None)
                if not hint or hint['level'] == 'L0':
                    raise AgentError('没有可展示的提示；自主探索时可以让投屏留白。')
                view['hint'] = {k: hint[k] for k in ('message', 'level')}
                view['hint_id'] = hint_id
                hint['presented_at'] = view['published_at']
                if hint['feedback'] == 'not_shown':
                    hint['feedback'] = 'offered'
            doc['presentation'] = view
            doc.setdefault('presentation_history', []).append(copy.deepcopy(view))
            self.store.save(doc)
            return doc
        finally:
            lock.release()


def classroom_view(doc):
    """A curated display payload; never send observations, node logs or unreleased hints."""
    return dict(title=doc['title'], mode=doc['mode'], constraints=doc['constraints'],
                presentation=doc.get('presentation'))


def export_markdown(doc):
    lines = ['# 场外 · 演练记录', '', f"演练：{doc['title']}", f"模式：{'手写演示，非模型生成' if doc['mode']=='demo' else '真实模型模式'}", f"创建时间（UTC）：{doc['created_at']}", '', '## 剧本', doc['story'], '', '## 课堂约束', doc['constraints'], '', '## 所选事件', json.dumps(doc['selected_event'], ensure_ascii=False, indent=2), '', '## 提示与反馈']
    for h in doc['hints']:
        lines += ['', f"### {h['level']} · {h['feedback']}", f"观察：{h['observation']}", h['message'], f"知识边界：{h['knowledge_status']}"]
    lines += ['', '## 活动配置', '```json', json.dumps(doc.get('activity_config'), ensure_ascii=False, indent=2), '```',
              '', '## 人工确认的投屏记录', '```json', json.dumps(doc.get('presentation_history', []), ensure_ascii=False, indent=2), '```']
    lines += ['', '## 反思', '你采纳、修改或拒绝了哪些提示？', '身体、空间或道具关系发生了哪些变化？', '哪些事实还需要核查？', '', '## 节点记录（不含模型密钥）', '```json', json.dumps(doc['logs'], ensure_ascii=False, indent=2), '```']
    return '\n'.join(lines)

