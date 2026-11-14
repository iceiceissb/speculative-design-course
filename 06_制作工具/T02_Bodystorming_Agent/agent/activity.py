"""Turn a teacher's selections into the constraints used by every agent node."""
from .model import AgentError

SPACES = {
    'fixed': '在固定活动区域内完成，不跨组移动。',
    'open': '可在教师指定的教室空地移动。',
    'table': '在指定桌面及周边完成。',
}
FOCUSES = ('身体与空间', '角色与叙事', '即兴与协作')


def prepare_fields(fields):
    result = {k: fields.get(k, '') for k in ('title', 'story', 'constraints')}
    result.update(participants=fields.get('participants', '3'), remaining=fields.get('remaining', '3'))
    if any(not isinstance(v, str) for v in result.values()):
        raise AgentError('活动名称、情境、人数与时长必须是文本。')
    result['mode'] = fields.get('mode', 'demo')
    if result['mode'] not in ('demo', 'live'):
        raise AgentError('请选择演示或真实模型模式。')
    config = fields.get('activity_config')
    if config is None:  # Older saved runs remain usable without reinterpretation.
        return result
    if not isinstance(config, dict):
        raise AgentError('活动条件格式不正确。')
    materials = config.get('materials', [])
    if (not isinstance(materials, list) or not materials or len(materials) > 20
            or any(not isinstance(m, str) or not m.strip() or len(m) > 40 for m in materials)):
        raise AgentError('请选择现场材料，或选择「仅用身体」；最多 20 项，每项最多 40 字。')
    materials = list(dict.fromkeys(m.strip() for m in materials))
    if '仅用身体' in materials and len(materials) != 1:
        raise AgentError('「仅用身体」不能与其他材料同时选择。')
    space, focus = config.get('space', 'fixed'), config.get('focus', '即兴与协作')
    if space not in SPACES or focus not in FOCUSES:
        raise AgentError('请选择有效的空间条件和学习重点。')
    rules = config.get('rules', {})
    if not isinstance(rules, dict) or any(not isinstance(v, bool) for v in rules.values()):
        raise AgentError('活动规则必须为勾选项。')
    rules = {k: rules.get(k, default) for k, default in (('only_materials', True), ('symbolic', True), ('standing', False))}
    notes = config.get('notes', '')
    if not isinstance(notes, str) or len(notes) > 2000:
        raise AgentError('补充要求最多 2000 字。')
    try:
        if not 1 <= int(result['participants']) <= 40 or not 1 <= int(result['remaining']) <= 60:
            raise ValueError()
    except ValueError:
        raise AgentError('每组人数需为 1–40 人，本轮时长需为 1–60 分钟。')
    result['activity_config'] = dict(version=1, materials=materials, space=space, focus=focus, rules=rules, notes=notes.strip())
    lines = [f"每组 {result['participants']} 人，本轮表演时长 {result['remaining']} 分钟。",
             '现场材料：' + '、'.join(materials) + '。', '空间条件：' + SPACES[space], '学习重点：' + focus + '。']
    if rules['only_materials']:
        lines.append('只使用上述现场材料，不引入额外实物。')
    if rules['symbolic']:
        lines.append('故事中的设备或环境通过身体动作和道具象征性表达，不要求真实实现。')
    if rules['standing']:
        lines.append('全程站立完成。')
    if notes.strip():
        lines.append('补充要求：' + notes.strip())
    result['constraints'] = '\n'.join(lines)
    return result
