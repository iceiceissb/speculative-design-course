"""Full-film production. Shared local credential; durable task IDs; no POST retries."""
import argparse
from copy import deepcopy
import json
from pathlib import Path
import shutil
import sys
import time

from workflow import ROOT, Workflow, SeedanceClient, load_key, read_json, write_json, stamp

SOURCE = ROOT.parents[1] / '03_分镜与角色/F11_不用麻烦她_v9_视频生成分镜'
PILOT = ROOT / 'projects/F11_2026-10-18_首轮试片'
RUN = ROOT / 'projects/F11_2026-10-19_480p全片'
REUSE = {'20', '21', '53'}
VOICES = {
    '邱': '邱：明确的七十岁左右老年女性普通话，中低音，温暖略沙哑，气息稳，吐字清楚，语气干脆亲近。',
    '徐': '徐：明确的七十岁左右老年女性普通话，中音稍亮，清晰亲切，带一点笑意和活气，保留年长声线。',
    '秀秀': '秀秀：声音只从轮椅扶手扬声器传出，清澈中性女声，平稳简洁。',
    '店主': '店主：中年男性普通话，温和质朴，正常交谈语速。',
    '来客': '来客：成年女性普通话，中音，清晰直接，自然交谈。',
    '广告声': '广告声：电视扬声器传出的成年女声普通话，清楚轻快，简短产品介绍口吻。',
    '工作人员': '工作人员：成年女性普通话，清楚平实，交谈语气。',
}


def make_prompt(s, duration):
    sid = s['id']
    action = s['action'].replace('两级台阶', '首帧可见的三级石台阶')
    # Metadata was checked against all six actual 12-frame contact sheets.
    if sid == '09':
        action = '沿首帧现有的踏步，轮椅支撑脚交替承重，车轮上移，座面保持水平，最后稳稳停住。匿名乘坐者始终只露肩以下。'
    if sid == '13':
        action = '猫已经在旧轮椅座面上，轻踩两下布垫，蜷身趴好，尾巴慢慢收起。'
    if sid == '15':
        action = '沿首帧正面机位，轮椅两侧原有支撑机构贴向座面下方收好，轮胎转动，整辆轮椅从两根柱间向镜头前行，驶出柱口。'
    if sid == '16':
        action = '轮椅从首帧位置开始，原有支撑脚接触踏面承重，前轮上移、后轮跟进，连续登上画面现有三级石台阶；座面始终水平；最后车身到达店门前平台并停稳。动作利落连续。'
    if sid == '23':
        action = '徐已经把蓝灰舞裙贴在身前，跟着心中的节拍轻转半圈，邱用手指敲两下扶手，二人对视笑起来。现场只有敲击、脚步、轻笑和布料声。'
    if sid == '24':
        action += ' 来客的呼喊从店门外传入，店内画面始终只保留首帧的店主，呼喊者不进入此镜。'
    if sid == '29':
        action = '邱坐在平台上，清楚说完台词，指向门外的台阶，听到轮椅答复后把手放回扶手。徐保持首帧蹲坐位置安静听。轮椅上的小摄像头转向入口。'
    if sid == '31':
        action = '邱听扶手扬声器问话，看一下屏幕里的照片，抬眼回答，然后食指移向屏幕的提交位置。'
    if sid == '39':
        action = action.replace('他', '她')
    if sid == '51':
        action = '邱把首帧站在旧轮椅座面上的猫轻轻扶稳，猫踩两下布垫趴下，邱松手回头看桌上的红布。'
    if sid == '56':
        action = '来客自己转动手轮，从首帧位置转向敞开的店门，脚踏与门边保持清楚间隙，驶进店内并伸手轻摸身旁布架上的布料。'
    if sid == '61':
        action = '首帧公交坡板已经展开并落稳，轮椅前轮沿坡板向右驶入敞开的车门，后轮跟进，乘客进入车厢。保持坡板与车门几何不动。'
    if sid == '66':
        action = '邱穿着亮红新外衣，沿首帧留出的宽通道向镜头前行，轮椅机构全程收好；旁边手动轮椅使用者也沿平路前行，两人相视点头，各自继续走。'
    if sid == '70':
        action = '徐说完台词，邱拨控制杆，轮椅原地平稳转过半圈，让新红衣后背可见，徐原地跟着节拍轻转身，重新看向邱。'
    lines = deepcopy(s['dialogue'])
    who = list(dict.fromkeys(d['speaker'] for d in lines))
    scope = []
    if sid in {'04','06','07','19','20','23','28','29','36'}:
        scope.append('画面内短灰发、红开衫、坐轮椅的是邱；戴眼镜、赭黄色外套、低灰发髻的是徐。只按本镜实际说话顺序开口。')
    elif sid in {'68','69','70','71'}:
        scope.append('坐轮椅、亮红外衣的是邱；站立、戴眼镜、蓝灰舞裙的是徐，两人都是老年女性。')
    elif sid == '05':
        scope.append('坐轮椅的老年女性是邱；穿围裙、端扣子盒的中年男性是店主。')
    elif sid in {'26','33'}:
        scope.append('短黑发、雾蓝外套、坐手动轮椅的成年女性是来客；靛蓝围裙男性是店主。')
    elif sid == '34':
        scope.append('坐智能轮椅、红开衫的老年女性是邱；蹲在台阶下、围裙男性是店主。')
    elif sid == '52':
        scope.append('坐智能轮椅的红开衫老年女性是邱；门边围裙男性是店主。')
    elif sid == '42':
        scope.append('浅灰外套、短棕发、戴眼镜、拿笔指向地图的成年女性是工作人员，本镜仅她讲话。其余首帧人物安静看图。')
    if sid in {'12','22','35','50'}:
        scope.append('严格保留首帧的取景范围，近景只表现已可见的手、衣料、工具和身体局部，不补全画外人物。')
    out = ['保持所给首帧的手工微缩定格人偶质感、人物身份与服饰、物体数量、场景布置和构图。一个连续机位镜头。',
           *scope, '动作：' + action,
           '节奏：开头即进入动作，去掉等待与长停顿，动作自然清楚；手掌先接触物件再取放，轮胎贴地滚动，结构不增生，物件不穿透。']
    if lines:
        out += ['声音只使用以下本镜台词与现场动作声，人物说话时对应人物自然开口；没有台词的人不加口型。',
                *[VOICES.get(w, w+'：自然普通话。') for w in who],
                '台词按顺序完整说出，从约0.3秒开始，句间只保留自然换气，不拖长尾音，不添加其他语言：',
                *[d['speaker']+'：“'+d['text']+'”' for d in lines]]
        if '秀秀' in who:
            out.append('秀秀的台词由轮椅设备发声，画内其他人闭口聆听，不增加发声人形或画外人物。')
        if sid == '24':
            out.append('来客的声音只在店门外，画内店主听见并抬眼，不张嘴说这句。')
        if sid == '09':
            out.append('广告配音作为产品展示的画外解说，匿名乘坐者不说话。')
    else:
        out.append('本镜没有对白或旁白，仅有与动作对应的自然现场环境声。')
    out.append('不生成背景音乐，不生成字幕、标题、界面新文字或水印。保持首帧的小字原样，后期另做可读信息。')
    return '\n'.join(out)


def prepare():
    if (RUN / 'project.json').exists():
        return
    s = read_json(SOURCE / 'storyboard.json')
    speed = {x['id']: x for x in read_json(PILOT / '节奏对比/全片稍快版预算.json')['jobs']}
    api = deepcopy(read_json(ROOT / 'project.json')['api'])
    api.update(resolution='480p', ratio='adaptive', generate_audio=True, watermark=False,
               poll_seconds=8, wait_seconds=1200)
    jobs, timeline = [], []
    (RUN / 'assets').mkdir(parents=True, exist_ok=True)
    for shot in s['shots']:
        sid = shot['id']
        if shot['method'] != 'video':
            continue
        b = speed[sid]
        frame = SOURCE / shot['storyboard_image']
        shutil.copy2(frame, RUN / 'assets' / frame.name)
        dur = b['proposed_generation_seconds']
        # The TV narration needs 10 seconds to avoid compressed diction.
        if sid == '09':
            dur = 10
        jobs.append({'id': sid, 'title': shot['title'], 'duration': dur,
                     'frames': [{'file': frame.name, 'role': 'first_frame'}],
                     'prompt': make_prompt(shot, dur), 'dialogue': shot['dialogue'],
                     'reuse_preferred': sid in REUSE, 'source_shot': sid})
        timeline.append({'id': sid, 'job_id': sid, 'title': shot['title'], 'source_start': 0,
                         'duration': b['proposed_edit_seconds']})
    project = {'schema_version': 1, 'title': '不用麻烦她 · 480p全片制作', 'api': api,
               'limits': {'max_total_api_tasks': 90, 'max_total_generated_seconds': 410},
               'jobs': jobs, 'timeline': timeline, 'audio_tracks': [], 'subtitles': [],
               'authorization': {'date': '2026-10-19', 'scope': '用户充值后授权全片付费生成、复用样片、剪映剪辑',
                                 'estimated_new_generation_budget_rmb': 280,
                                 'wallet_balance_live_verified': False}}
    write_json(RUN / 'project.json', project)
    w = Workflow(RUN)
    p = Workflow(PILOT / '五镜试片')
    for old in p.state()['candidates']:
        if old['job_id'] not in REUSE or not old.get('file'):
            continue
        c = w.import_video(old['job_id'], p.local(old['file']))
        w.select(old['job_id'], c['id'])
    write_json(RUN / '制作说明.json', {'created_at': stamp(), 'source': str(SOURCE),
               'all_72_reference_frames_reviewed_in_contact_sheets': True,
               'three_steps_match_existing_images': True,
               'reused_pilot_shots': sorted(REUSE),
               'post_shots': [x for x in s['shots'] if x['method'] != 'video'],
               'voices': VOICES, 'no_global_cast_in_prompts': True})


def ledger(w):
    state = w.state()
    rows = []
    for c in state['candidates']:
        if c['source'] != 'seedance':
            continue
        tokens = c.get('usage', {}).get('completion_tokens', 0)
        actual = round(tokens * 70 / 1e6, 5)
        reserved = 0 if c['status'] in {'succeeded','failed','cancelled','expired','rejected'} else c['requested_duration'] * .67095 + .028
        rows.append({'id': c['job_id'], 'candidate': c['id'], 'task_id': c.get('task_id'),
                     'status': c['status'], 'duration': c['requested_duration'],
                     'completion_tokens': tokens, 'usage_estimated_rmb': actual, 'reserved_rmb': round(reserved,3)})
    report = {'updated_at': stamp(), 'new_api_tasks': len(rows),
              'usage_estimated_rmb': round(sum(x['usage_estimated_rmb'] for x in rows), 4),
              'reserved_rmb': round(sum(x['reserved_rmb'] for x in rows), 4),
              'rate_rmb_per_million': 70, 'actual_invoice_verified': False, 'tasks': rows}
    write_json(RUN / '费用与进度.json', report)
    return report


def refine_unsubmitted():
    w=Workflow(RUN)
    submitted={c['job_id'] for c in w.state()['candidates'] if c['source']=='seedance'}
    shots={s['id']:s for s in read_json(SOURCE/'storyboard.json')['shots']}
    people={'Q0','Q1','VISITOR','HOME_RESIDENT','RESIDENT1','RESIDENT2','RESIDENT3','YOUNG','PARK_ELDER1','PARK_ELDER2','DEMO'}
    for j in w.project['jobs']:
        sid=j['id']
        if sid in submitted or sid not in shots:
            continue
        if people.intersection(shots[sid]['cast']) and sid not in {'12','22','35','50'}:
            j['prompt']+='\n乘坐者全程保持坐姿，臀部贴住坐垫，双脚留在脚踏上；移动由轮椅车轮完成，乘坐者始终不站起、不步行。'
    if '02R' not in w.jobs:
        j=deepcopy(w.jobs['02'])
        j['id']='02R';j['title']='柱口阻挡 · 修正坐姿'
        j['prompt']=('保持首帧手工定格人偶和固定正面构图，两根石柱位置不动。'
          '红开衫老年女性邱全程坐在蓝色手动轮椅上，臀部始终贴着座垫，脚始终放在脚踏，躯干不抬离坐垫。'
          '她用双手转动手轮，轮椅仅前移几厘米，外侧轮圈碰到石柱便停住。'
          '身后黄色外套戴眼镜的徐俯身看向轮圈被挡住的位置，邱松开手轮，仍坐在原处。'
          '全程保持两位老年女性的人物外貌和服装、轮椅大小与零件连接，轮椅不穿过石柱。'
          '没有人站起来或步行，只有轮圈碰到柱子后停止的小动作。无对白、旁白、音乐、字幕，仅有街道和轮圈接触声。')
        w.project['jobs'].append(j)
    write_json(RUN/'project.json',w.project)
    print(json.dumps({'seated_rule_added_to_unsubmitted_only':True,'targeted_quality_retake':'02R'},ensure_ascii=False),flush=True)


def generate_all(only=None):
    w = Workflow(RUN)
    key = load_key(ROOT)
    if not key:
        raise RuntimeError('本地未配置密钥')
    client = SeedanceClient(w.project['api']['base_url'], key)
    ids = only or [j['id'] for j in w.project['jobs'] if not j.get('reuse_preferred')]
    for start in range(0, len(ids), 6):
        batch = ids[start:start+6]
        plan = w.plan(only=batch, max_new_tasks=6)
        money = ledger(w)
        estimate = sum(t['duration']*.67095+.028 for t in plan['new_tasks'])
        if money['usage_estimated_rmb'] + money['reserved_rmb'] + estimate > 280:
            raise RuntimeError('触及本轮280元保守生成上限，停止新增；已有视频保留。')
        print(json.dumps({'event': 'batch_start', 'shots': batch, 'new_tasks': len(plan['new_tasks']),
                          'new_seconds': plan['new_generated_seconds'], 'usage_so_far_rmb': money['usage_estimated_rmb']}, ensure_ascii=False), flush=True)
        # A definitive image rejection is never resubmitted. Continue the other
        # independent shots and later use an explicitly labelled local still cut.
        for attempt in range(len(batch)+1):
            try:
                result = w.generate(only=batch, max_new_tasks=6, client=client)
                break
            except RuntimeError:
                latest = w.state()['candidates'][-1]
                if latest['status'] != 'rejected':
                    raise
                print(json.dumps({'event':'definitive_rejection_no_retry',
                                  'shot':latest['job_id'],'error':latest.get('error')},ensure_ascii=False),flush=True)
        else:
            raise RuntimeError('批次未收敛；停止新增。')
        for c in w.state()['candidates']:
            if c['job_id'] in batch and c.get('file') and c['status'] == 'succeeded':
                w.select(c['job_id'], c['id'])
        print(json.dumps({'event':'batch_end','shots':batch,'result':result,
                          'cost':ledger(w)['usage_estimated_rmb']}, ensure_ascii=False), flush=True)
        if result['uncertain'] or result['pending']:
            raise RuntimeError('需要先核对已有任务，停止新增以免重复计费。')


def main():
    p = argparse.ArgumentParser()
    p.add_argument('action', choices=['prepare','plan','generate','status','refine'])
    p.add_argument('--only', nargs='+')
    a = p.parse_args()
    prepare()
    w = Workflow(RUN)
    if a.action == 'refine':
        refine_unsubmitted()
    elif a.action in {'prepare','plan'}:
        remaining = [j for j in w.project['jobs'] if not j.get('reuse_preferred')]
        print(json.dumps({'doctor': dict(w.doctor(), api_key_configured=bool(load_key(ROOT))),
                          'new_tasks':len(remaining),'requested_seconds':sum(j['duration'] for j in remaining),
                          'estimated_rmb':round(sum(j['duration']*.67095+.028 for j in remaining),2),
                          'reused':sorted(REUSE)},ensure_ascii=False),flush=True)
    elif a.action == 'generate':
        generate_all(a.only)
    else:
        print(json.dumps(ledger(w),ensure_ascii=False),flush=True)


if __name__ == '__main__':
    try:
        main()
    except Exception as error:
        secret = load_key(ROOT)
        msg = str(error)
        if secret:
            msg = msg.replace(secret, '[REDACTED]')
        print(json.dumps({'error':msg},ensure_ascii=False),flush=True)
        sys.exit(1)
