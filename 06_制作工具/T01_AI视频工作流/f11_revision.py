"""V02: bounded motion retakes and a separate, reproducible sound/edit revision."""
import argparse
from copy import deepcopy
import csv
import json
from pathlib import Path
import shutil
import sys
import time

from workflow import ROOT, Workflow, SeedanceClient, load_key, read_json, write_json, stamp
from f11_production import SOURCE, VOICES, ledger

RUN = ROOT/'projects/F11_2026-10-19_动作与声音修订'
OLD_RUN = ROOT/'projects/F11_2026-10-19_480p全片'
OLD_OUT = ROOT.parents[1]/'05_汇报与成片/V01_不用麻烦她_2026-10-19'
OUT = ROOT.parents[1]/'05_汇报与成片/V02_不用麻烦她_动作与声音修订_2026-10-19'
UI = {'18','30','32','41','57','58','65'}

PROMPTS = {
 '14': '''手工微缩动画短片的手部特写，锁定镜头，保持首帧轮椅、扶手、屏幕、红针织袖子与手的方位。画面中只有这一只老年女性的右手和首帧现有身体局部，不切出人物脸。
动作立即开始：食指向前移动约两厘米，用指腹清楚按下屏幕已有的绿色“允许”按钮，指尖接触屏幕，停留半秒后松开并收回手，最后手指自然搭在扶手上。这是一次真实的点击动作，手指的关节弯曲自然，其他手指跟随微动。屏幕已有文字与布局全程保持，按钮仅在按下时略微变暗，松开恢复。
现场仅有轻触屏幕的轻声和室内自然底噪；没有说话、旁白、背景音乐、新字幕。镜头不推拉、不平移，动作由手和手指完成。''',
 '70': '''保持首帧手工微缩人偶动画的质感、两名老年女性的脸、服装、轮椅外形与场景。双人全景，摄像机固定，地面与所有轮子完整可见。
人物分工：左侧穿亮红外衣、短银发的是邱，她全程坐在原有轮椅座面，背部靠着椅背；右侧戴眼镜、灰发髻、蓝灰裙子的是徐，她双脚始终留在首帧所在的地面位置，身体正对邱，站着看朋友的新衣服。
0.2—2.2秒：徐保持原地站姿，嘴部自然说完一句“转过去，我看看后面。” 邱看着她听。
2.2—5.8秒：邱右手拨动原有控制杆，轮椅左右轮差速滚动，邱与整张轮椅一起在地面缓慢转过半圈，红外衣的后背转向徐与镜头，随后轮椅停稳。邱仍然坐在同一张座垫上，腿脚始终在原有脚踏上。徐双脚仍在原地，裙摆自然下垂，身体一直朝着轮椅，只用目光跟随邱，微笑端详衣服。
5.8—7秒：轮椅停稳，徐略微低头看红衣后背，微笑点一下头。两人位置关系清楚。
只有徐说话。'''+VOICES['徐']+'''
现场是轻微轮胎滚动、衣料摩擦和公园自然环境声。没有额外对白、背景音乐、字幕或标题。徐始终保持原地看衣服的站姿，不跳舞。转动动作只来自轮椅车轮，邱全程坐着。''',
 '03': '''保持首帧的手工微缩人偶动画风格、石板小街和两位老年女性服装。中全景固定机位，轮椅轮子与两人的运动完整入画。
穿赭黄外衣、戴眼镜、灰发髻的徐先指向画面左侧已经存在的宽旁路，放下手，迈开双脚沿旁路走出两三步；红开衫、短银发的邱始终坐在手动轮椅上，双手握住现有大轮手推圈，一边推动一边转向左侧宽旁路，车轮真实滚动约一米，跟上徐。两人沿同一条宽路离开柱口，步幅和轮速协调。石柱保持原位，轮椅绕开石柱。邱的臀部始终在同一座垫上，脚在脚踏上。
开头立即开始动作，四秒内完成指路、起步、随行。固定镜头，人物产生明显位移，不用镜头缩放代替人物行动。
仅有鞋底踏石板、手轮与轮胎滚动、室外微风和远处街声。无对白、旁白、配乐、字幕。''',
 '39': '''手工微缩人偶动画。保持首帧中黑短发、戴眼镜、灰围巾的成年女性、电动轮椅、手机和公交站断裂人行道。固定中全景，人物全程坐在轮椅上，车轮保持停稳，与前方断口保持首帧已有安全距离。
动作从第一秒开始：她右手拿稳手机，抬高约十五厘米，身体略向前倾，把手机镜头朝向前方断裂路面；左手食指伸出，轻点手机屏幕拍一张照，随后再点一次确认，把手机缓缓放回扶手位置，抬眼看向前方。全程保留明显、自然、连续的手臂和手指动作，手机跟着手移动。轮椅留在原地，不驶向断口。远处公交车在道路上缓缓前行，树叶轻动。
五秒一个连续镜头；固定摄影机，动的是手、手机和背景公交，不用推近镜头替代动作。现场只有轻触手机声、远处低沉车流声、公交车声和微风。无对白、旁白、背景音乐、字幕。'''
}


def prepare():
    OUT.mkdir(parents=True,exist_ok=True)
    (RUN/'assets').mkdir(parents=True,exist_ok=True)
    if (RUN/'project.json').exists(): return
    story={x['id']:x for x in read_json(SOURCE/'storyboard.json')['shots']}
    api=deepcopy(read_json(OLD_RUN/'project.json')['api'])
    jobs=[]
    for sid,dur in [('14',4),('70',7)]:
        frame=SOURCE/story[sid]['storyboard_image'];shutil.copy2(frame,RUN/'assets'/frame.name)
        jobs.append({'id':sid,'title':story[sid]['title']+'·动作修订','duration':dur,
                     'frames':[{'file':frame.name,'role':'first_frame'}],
                     'prompt':PROMPTS[sid],'dialogue':story[sid]['dialogue'],'source_shot':sid})
    p={'schema_version':1,'title':'F11·动作与声音修订 V02','api':api,
       'limits':{'max_total_api_tasks':8,'max_total_generated_seconds':48},
       'jobs':jobs,'timeline':[{'id':x['id'],'job_id':x['id'],'title':x['title'],'source_start':0,'duration':x['duration']} for x in jobs],
       'audio_tracks':[],'subtitles':[],
       'authorization':{'date':'2026-10-19','scope':'用户明确要求重生成缺少动作的剧情镜头、修复转身、替换与精剪',
                        'initial_shots':['03','14','39','70'],'initial_estimated_rmb':13.53,
                        'retake_budget_rmb':33,'ui_paid_generation':False,'old_submitted_requests_unchanged':True}}
    write_json(RUN/'project.json',p)
    audit={'ui_shots':sorted(UI),'old_api_job_ids':[x['id'] for x in read_json(OLD_RUN/'project.json')['jobs']],
           'ui_submitted_to_api':False,'new_ui_paid_jobs':0,'static_ui_will_be_native_1080p_images':True,
           'old_03_39': '原始输入被供应商判为可能包含真人，未生成成功，旧输入不重发',
           '70_error': '旧提示词错误地要求徐同时转身；新提示词限定徐站在原地，只有邱与轮椅转动'}
    assert not UI.intersection(audit['old_api_job_ids'])
    write_json(OUT/'修订计划与费用核对.json',audit)
    write_json(RUN/'doctor.json',{**Workflow(RUN).doctor(),'shared_credential_configured':bool(load_key(ROOT))})
    write_json(RUN/'生成计划.json',Workflow(RUN).plan(max_new_tasks=4))
    print(json.dumps({'prepared':str(RUN),'first_batch':['14','70'],'shared_key_ready':bool(load_key(ROOT))},ensure_ascii=False),flush=True)


def add_frame(sid,path):
    assert sid in {'03','39'}
    p=read_json(RUN/'project.json')
    assert not any(x['id']==sid for x in p['jobs'])
    dst=RUN/'assets'/f'{sid}_动作首帧_v2.png';shutil.copy2(path,dst)
    j={'id':sid,'title':('绕路起步' if sid=='03' else '公交断口拍照')+'·动作修订','duration':4 if sid=='03' else 5,
       'frames':[{'file':dst.name,'role':'first_frame'}],'prompt':PROMPTS[sid],'dialogue':[],'source_shot':sid}
    p['jobs'].append(j);p['timeline'].append({'id':sid,'job_id':sid,'title':j['title'],'source_start':0,'duration':j['duration']})
    write_json(RUN/'project.json',p)


def generate(ids):
    w=Workflow(RUN);plan=w.plan(ids,max_new_tasks=4)
    booked=ledger(w)['usage_estimated_rmb'];estimate=sum(x['duration']*.67095+.028 for x in plan['new_tasks'])
    if booked+estimate>33:raise ValueError('本轮修订预算上限已到')
    write_json(RUN/('生成计划_'+''.join(ids)+'.json'),{**plan,'estimated_rmb':round(estimate,2)})
    client=SeedanceClient(w.project['api']['base_url'],load_key(ROOT))
    try:
        result=w.generate(ids,max_new_tasks=4,client=client);print(json.dumps(result,ensure_ascii=False),flush=True)
    finally:
        report=ledger(w);write_json(OUT/'本轮修订费用.json',report)
        print(json.dumps({'charged_usage_estimate':report['usage_estimated_rmb'],'tasks':report['new_api_tasks']},ensure_ascii=False),flush=True)


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('action',choices=['prepare','generate','add-frame']);p.add_argument('--ids',nargs='+');p.add_argument('--frame');a=p.parse_args()
    if a.action=='prepare':prepare()
    elif a.action=='generate':generate(a.ids)
    else:add_frame(a.ids[0],Path(a.frame))
