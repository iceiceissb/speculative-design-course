"""Bounded F11 API pilot. Reads the shared local key; never prints or copies it."""
import argparse
from copy import deepcopy
import json
from pathlib import Path
import shutil

from workflow import ROOT, Workflow, SeedanceClient, load_key, write_json, read_json, stamp


SOURCE = ROOT.parents[1] / '03_分镜与角色/F11_不用麻烦她_v9_视频生成分镜'
RUN = ROOT / 'projects/F11_2026-10-18_首轮试片'
PRIORITY = ['15', '16', '20', '21', '53']


def prepare():
    plan = read_json(SOURCE / 'generation_plan.json')
    original = {job['id']: job for job in plan['jobs']}
    common = deepcopy(read_json(ROOT / 'project.json')['api'])
    common.update(ratio='adaptive', watermark=False, poll_seconds=8, wait_seconds=1200)
    for profile in ('连接测试', '五镜试片'):
        folder = RUN / profile
        if (folder / 'project.json').exists():
            continue
        assets = folder / 'assets'
        assets.mkdir(parents=True, exist_ok=True)
        ids = ['20'] if profile == '连接测试' else PRIORITY
        jobs, timeline = [], []
        for shot_id in ids:
            source = original[shot_id]
            frame = SOURCE / source['first_frame_placeholder']
            shutil.copy2(frame, assets / frame.name)
            prompt = source['prompt']
            prompt = prompt.replace('收拢、普通轮行与越阶结构以待确认母版为准。',
                                    '轮椅的零件数量、外壳与关节连接以首帧为准。')
            prompt = prompt.replace('使用该角色确认过的声音参考：', '本轮试片使用自然的临时人物声音：')
            duration = source['duration']
            job_id = shot_id
            if profile == '连接测试':
                duration, job_id = 4, 'T20'
                prompt = ('保持首帧的手工定格人偶、两位老年女性、服装、轮椅和布店陈设。'
                          '固定机位，单个连续镜头。坐轮椅的邱轻轻抬起手中的红布一角，'
                          '旁边戴眼镜的徐微笑看着她；布料自然落下，两人的脸和手保持稳定。'
                          '现场仅有轻微衣料摩擦与室内环境声，无对白、旁白、音乐和字幕。')
            elif shot_id == '15':
                prompt = prompt.replace('与02相同机位的侧前方中全景，固定。',
                                        '严格保持首帧的正面中全景，固定机位。')
                prompt = prompt.replace('秀秀朝右停在原柱口外，邱膝上是待补扣舞裙。',
                                        '秀秀正朝镜头，停在首帧两根柱之间，邱膝上放着舞裙。')
                prompt += ('\n本镜按首帧朝向继续：两侧机械臂贴拢扶手，轮胎转动，轮椅缓慢向镜头前行，'
                           '直到整辆车穿过柱口。石柱固定，座椅和人体保持原大小。')
            elif shot_id == '16':
                prompt = prompt.replace('旧入口：临街正门前两级台阶', '旧入口：临街正门前的石台阶')
                prompt = prompt.replace('升上两级台阶', '逐级升上首帧可见的石台阶')
                prompt = prompt.replace('台阶数量固定为两级。', '台阶数量和几何保持首帧不变。')
                prompt += ('\n本轮只检验现有首帧的越阶运动，入口台阶数量仍待后续统一。'
                           '沿首帧已存在的支撑脚交替承重抬升，前轮先到上一阶，后轮再跟进；'
                           '支撑脚贴住踏面后才抬升另一侧，座面平稳，车身不增加新轮子。')
            elif shot_id == '21':
                prompt = prompt.replace('机械臂与高处盒子中近景，固定。', '保持首帧的双人与机械臂中景，固定。')
                prompt = prompt.replace('秀秀空机械手已抬至盒前。', '秀秀同一只机械手已托住扣子盒。')
                prompt = prompt.replace('同一只机械手夹住盒子侧面，提离架面，缓慢递到邱手边并放稳。',
                                        '同一只机械手稳稳托住盒子，肘关节缓慢弯曲，将盒子从架前降到邱手边。')
                prompt = prompt.replace('盒子落在托盘上，机械手松开。', '邱伸手接稳扣子盒后，机械手再松开。')
                prompt += '\n保持首帧已存在的徐在邱身旁，人物数量、外观和各自位置不变。'
            api = dict(common, resolution='480p' if profile == '连接测试' else '720p')
            jobs.append({'id': job_id, 'title': source['title'], 'duration': duration,
                         'frames': [{'file': frame.name, 'role': 'first_frame'}], 'prompt': prompt,
                         'dialogue': [] if profile == '连接测试' else source['dialogue'],
                         'source_shot': shot_id, 'source_frame': str(frame)})
            timeline.append({'id': job_id, 'job_id': job_id, 'title': source['title'],
                             'source_start': 0, 'duration': min(duration, source['edit_seconds'])})
        project = {'schema_version': 1, 'title': 'F11 · ' + profile, 'api': api,
                   'limits': {'max_total_api_tasks': len(jobs),
                              'max_total_generated_seconds': sum(j['duration'] for j in jobs)},
                   'jobs': jobs, 'timeline': timeline,
                   'audio_tracks': [], 'subtitles': [],
                   'note': '用户2026-10-18授权测试成功后开始生成；首轮候选，不自动重抽。'}
        write_json(folder / 'project.json', project)
    manifest = RUN / '本轮计划.json'
    if not manifest.exists():
        write_json(manifest, {'created_at': stamp(), 'authorized': True,
                             'profiles': {'连接测试': {'tasks': 1, 'seconds': 4, 'resolution': '480p'},
                                          '五镜试片': {'tasks': 5, 'seconds': 39, 'resolution': '720p'}},
                             'estimated_rmb': 61.66, 'estimated_only': True,
                             'note': '实际费用以usage与账单为准；没有自动重抽。台阶结构尚未锁定。'})


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('action', choices=['prepare', 'auth', 'probe', 'pilot', 'status'])
    args = parser.parse_args()
    if args.action == 'prepare':
        prepare()
        for profile in ('连接测试', '五镜试片'):
            w = Workflow(RUN / profile)
            print(json.dumps({'profile': profile, 'plan': w.plan(max_new_tasks=5)}, ensure_ascii=False), flush=True)
        return
    key = load_key(ROOT)
    if not key:
        raise RuntimeError('尚未在本地配置 API Key。')
    client = SeedanceClient(read_json(ROOT / 'project.json')['api']['base_url'], key)
    if args.action == 'auth':
        result = client.request('GET', '/contents/generations/tasks?page_num=1&page_size=1')
        report = {'checked_at': stamp(), 'authenticated': True, 'jobs_submitted': 0,
                  'response_fields': list(result)}
        write_json(RUN / '鉴权结果.json', report)
        print(json.dumps(report, ensure_ascii=False), flush=True)
    elif args.action == 'status':
        for profile in ('连接测试', '五镜试片'):
            w = Workflow(RUN / profile)
            rows = [{k: c[k] for k in ('id', 'job_id', 'status', 'task_id', 'file', 'media', 'usage', 'error') if k in c}
                    for c in w.state()['candidates']]
            print(json.dumps({'profile': profile, 'candidates': rows}, ensure_ascii=False), flush=True)
    else:
        if args.action == 'pilot':
            successful = Workflow(RUN / '连接测试').state()['candidates']
            if not any(c['status'] == 'succeeded' and c.get('file') for c in successful):
                raise RuntimeError('先完成真实连通样片并检查后，再提交五镜试片。')
        profile = '连接测试' if args.action == 'probe' else '五镜试片'
        w = Workflow(RUN / profile)
        print(json.dumps({'starting': profile, 'plan': w.plan(max_new_tasks=5)}, ensure_ascii=False), flush=True)
        result = w.generate(max_new_tasks=5, client=client)
        print(json.dumps(result, ensure_ascii=False), flush=True)


if __name__ == '__main__':
    try:
        main()
    except Exception as error:
        key = load_key(ROOT)
        message = str(error).replace(key, '[REDACTED]') if key else str(error)
        print(json.dumps({'error': message}, ensure_ascii=False), flush=True)
        raise SystemExit(1)
