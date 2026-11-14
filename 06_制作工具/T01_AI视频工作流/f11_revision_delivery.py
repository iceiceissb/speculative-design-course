"""Validate, package and register the separately owned V02 Jianying draft."""
import argparse
import html
import json
import os
from pathlib import Path
import re
import shutil
import time
from urllib.parse import quote,unquote

import numpy as np
from f11_revision import OUT,OLD_OUT,RUN,ROOT,UI
from workflow import read_json,write_json,stamp
import f11_edit as base


def timecards():
    import f11_delivery
    f11_delivery.OUT=OUT
    f11_delivery.timecards_without_dialogue_subtitles()


def preview():
    rows=read_json(OUT/'剪辑时间线.json');assets=read_json(OUT/'素材索引.json')
    def url(path):return quote(Path(path).relative_to(OUT).as_posix(),safe='/')
    thumbs=OUT/'预览缩略图';thumbs.mkdir(exist_ok=True);cards=[]
    for r in rows:
        sid=r['id'];clip=OUT/'剪辑素材'/f'{sid}.mp4';thumb=thumbs/f'{sid}.jpg'
        if not thumb.exists():base.ff(['-y','-ss',str(min(.8,r['duration']/2)),'-i',str(clip),'-frames:v','1','-vf','scale=480:-1','-q:v','3',str(thumb)])
        if sid in UI|{'72'}:
            src=Path(r['source']);media=f'<img loading="lazy" src="{url(src)}" alt="{html.escape(r["title"])}">'
            label='静态图片 · 本地排版';link=f'<a href="{url(src)}">打开图片</a>'
        else:
            raw=next((x for x in assets if x['candidate']==r.get('candidate')),None)
            src=Path(raw['file']) if raw else clip
            label='本轮重做' if raw and raw['charged_in_this_revision'] else '沿用镜头' if raw else '短暂静帧'
            media=f'<video controls preload="none" poster="{url(thumb)}" src="{url(src)}"></video>'
            link=f'<a href="{url(src)}">打开片段</a>'
        cards.append(f'<article>{media}<div><small>{sid} · {label}</small><h3>{html.escape(r["title"])}</h3>{link}</div></article>')
    poster=OUT/'封面.jpg';base.ff(['-y','-ss','2','-i',str(OUT/'剪辑素材/71.mp4'),'-frames:v','1','-q:v','2',str(poster)])
    seconds=rows[-1]['end'];cost=read_json(OUT/'本轮修订费用.json')
    page='''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>短片修订版 · 影片与素材</title><style>
    *{box-sizing:border-box}body{margin:0;background:#171d19;color:#eeeade;font-family:"Microsoft YaHei",sans-serif}main{max-width:1300px;margin:auto;padding:46px 30px 80px}.tag{color:#b3c3ab;font-size:12px;letter-spacing:3px}h1{font-size:37px;font-weight:500;line-height:1.7;margin:18px 0}p{color:#b8c0b5;font-size:14px;line-height:1.9}.film{width:100%;aspect-ratio:16/9;background:#000;border-radius:8px}.links{display:flex;gap:15px;flex-wrap:wrap;margin:24px 0 45px}a{color:#d8dfc8;text-decoration:none}.links a{border:1px solid #536650;border-radius:22px;padding:10px 18px}h2{font-size:23px;font-weight:500}.grid{display:grid;grid-template-columns:repeat(3,1fr);gap:20px}article{background:#252e26;border-radius:8px;overflow:hidden}article video,article img{display:block;width:100%;aspect-ratio:16/9;object-fit:contain;background:#090c09}article div{padding:15px 17px 19px}small{font-size:11px;color:#b5c4a9}h3{font-size:15px;font-weight:500}article a{font-size:12px}footer{font-size:12px;color:#899985;margin-top:45px}@media(max-width:800px){.grid{grid-template-columns:repeat(2,1fr)}main{padding:25px 15px}h1{font-size:27px}}@media(max-width:500px){.grid{grid-template-columns:1fr}}
    </style><main><div class="tag">动作与声音修订 · V02</div><h1>愿有一天，<br>每个人都能自由出门，平安回家。</h1>'''
    page+=f'<p>{int(seconds//60)}分{round(seconds%60):02}秒 · 1920×1080 · 24fps<br>四幕动作已替换；地图和回执保持静止，补入连续的环境声与剪映曲库配乐。仅四次新视频生成，用量估算约{cost["usage_estimated_rmb"]:.2f}元。</p>'
    page+=f'<video class="film" controls preload="metadata" poster="{url(poster)}" src="{quote("不用麻烦她_1080p_字幕版.mp4")}"></video>'
    page+='<div class="links">'+''.join(f'<a href="{quote(path)}">{label}</a>' for path,label in [('不用麻烦她_1080p_字幕版.mp4','打开完整修订版'),('不用麻烦她_1080p_无字幕.mp4','无对白字幕版'),('不用麻烦她.srt','字幕文件'),('00_交付说明.md','修订说明')])+'</div>'
    page+='<h2>逐镜素材</h2><p>视频原片保留生成现场声。静态界面直接显示原图；完整混音请看上方成片。</p><section class="grid">'+''.join(cards)+'</section>'
    page+='<footer>V01保留在原目录。本版的视频、声音、静态界面、字幕及自包含剪映草稿均保存在此文件夹。</footer></main></html>'
    (OUT/'看成片与素材.html').write_text(page,'utf-8')


def readme():
    rows=read_json(OUT/'剪辑时间线.json');cost=read_json(OUT/'本轮修订费用.json');draft=read_json(OUT/'剪映草稿验证.json')
    text=f'''# 影片修订版 V02

2026-10-19｜{int(rows[-1]['end']//60)}分{round(rows[-1]['end']%60):02}秒｜1920×1080｜24fps

打开 `看成片与素材.html` 可看完整修订版及逐镜素材。

本次已按反馈处理：

- 03：两位朋友实际沿旁路起步，轮椅滚动、徐迈步。
- 14：食指实际按下按钮，再松开收回。
- 39：使用者抬起手机拍摄断口、确认后放下；轮椅保持安全距离。
- 70：只有邱随轮椅转过半圈，徐留在原地看衣服。对白重新生成并按实际语音时间对齐。
- 18、30、32、41、57、58、65：使用原生1080p图片静止显示，剪映里登记为照片素材；没有付费生成这些界面。
- 原片尾片名已替换为“愿有一天，每个人都能自由出门，平安回家。”，缓慢浮现并淡出。
- 使用剪映曲库的《Soft Inspirational Piano》《Where We Belong》，音乐跨镜头连续，实际对白下方降低约10dB；另加独立、连续的场景环境声。

完整影片在 `不用麻烦她_1080p_字幕版.mp4`。`不用麻烦她_1080p_无字幕.mp4` 保留时间提示，移除对白字幕。SRT与可编辑字幕时间线同时保留。

剪映草稿通过已安装 `jianying-editor` Skill / JyProject 输出。画面、对白与现场声、配乐、连续环境声和字幕分别成轨。源草稿：`{Path(draft['path']).name}`。素材自包含，V01及其他草稿不覆盖。

本轮新建成功视频任务4个，480p素材共20秒，按接口返回用量估算约 **{cost['usage_estimated_rmb']:.2f}元**，以方舟实际账单为准。首次网络中断经两次任务列表查询核对未创建任务，核对记录保存在制作工具子项目中。图片首帧调整使用内置图像生成工具，不计入方舟视频用量。本地超分、字幕对时、静帧排版与剪辑未调用付费服务。

四个新480p镜头采用本地Real-ESRGAN超分与常规放大按80/20混合；其他高清镜头沿用V01。超分不会恢复源片里不存在的真实细节。图像生成提示词与首帧位于 `06_制作工具/T01_AI视频工作流/projects/F11_2026-10-19_动作与声音修订` 及 `f11_revision.py`。

音乐文件来自剪映Skill索引并经官方素材解析接口下载，记录见 `声音/剪映曲库检索.json`。用于当前课程短片；其他发行范围按对应曲目及剪映条款核对。

完整MP4、72镜时长、七张静态界面、字幕边界与界面段落音量由本地检查验证。剪映草稿结构与素材路径已检查，原生窗口播放/原生导出未验证；成片MP4由本地编码输出。
'''
    (OUT/'00_交付说明.md').write_text(text,'utf-8')


def validate():
    rows=read_json(OUT/'剪辑时间线.json');subs=read_json(OUT/'字幕时间线.json');info=base.read_probe(OUT/'不用麻烦她_1080p_字幕版.mp4')
    video=next(x for x in info['streams'] if x['codec_type']=='video')
    assert len(rows)==72 and rows[-1]['end']<300
    assert video['width']==1920 and video['height']==1080 and video['avg_frame_rate']=='24/1'
    assert abs(float(info['format']['duration'])-rows[-1]['end'])<.15
    for r in rows:
        p=OUT/'剪辑素材'/f"{r['id']}.mp4";probe=base.read_probe(p)
        assert abs(float(probe['format']['duration'])-r['duration'])<.085,r['id']
    ui=[]
    for r in rows:
        if r['id'] not in UI:continue
        frames=[]
        for t in [.5,r['duration']/2,r['duration']-.3]:
            import subprocess
            raw=subprocess.check_output(['ffmpeg','-hide_banner','-loglevel','error','-ss',str(t),'-i',str(OUT/'剪辑素材'/f"{r['id']}.mp4"),'-frames:v','1','-vf','scale=960:540','-pix_fmt','rgb24','-f','rawvideo','pipe:1'])
            frames.append(np.frombuffer(raw,dtype=np.uint8).astype(np.float32))
        delta=max(float(np.abs(f-frames[0]).mean()) for f in frames[1:])
        assert delta<.5,(r['id'],delta)
        ui.append({'shot':r['id'],'mean_decoded_pixel_change':round(delta,6),'static_hold_verified':True})
    assert all(0<=s['start']<s['end']<=rows[-1]['end'] for s in subs)
    assert all(any(s['shot']==r['id'] for s in subs) for r in rows if r['dialogue'])
    page=(OUT/'看成片与素材.html').read_text('utf-8');links=re.findall(r'(?:src|href|poster)="([^"]+)"',page)
    assert all((OUT/unquote(l)).exists() for l in links if not l.startswith(('http:','https:','#')))
    sound=read_json(OUT/'声音/混音检查.json')
    assert all(x['quietest_250ms_dbfs']>-50 for x in sound['ui_audio_checks'])
    draft=read_json(OUT/'剪映草稿验证.json');content=read_json(Path(draft['path'])/'draft_info.json')
    photos=[x for x in content['materials']['videos'] if x.get('type')=='photo']
    assert len(photos)==8,[(x.get('path'),x.get('type')) for x in content['materials']['videos'] if x.get('path','').endswith('.png')]
    report={'full_decode_passed':read_json(OUT/'交付验证.json')['full_decode_passed'],'72_clips_durations_match':True,'duration':rows[-1]['end'],
            '1920x1080_24fps':True,'ui_static_checks':ui,'ui_audio_has_no_quiet_250ms_below_minus_50_dbfs':True,
            'subtitle_chunks':len(subs),'subtitle_bounds_verified':True,'all_dialogue_shots_have_subtitles':True,
            'preview_links_verified':len(links),'draft_photo_materials':len(photos),'draft_tracks':[t.get('name') for t in content['tracks']],
            'new_motion_review':'03行进、14手指按下收回、39抬放手机拍照、70仅邱及轮椅转动；已人工查看逐时抽帧',
            'new_api_cost':read_json(OUT/'本轮修订费用.json')['usage_estimated_rmb'],'old_version_preserved':True}
    write_json(OUT/'整包验收.json',report);print(json.dumps(report,ensure_ascii=False),flush=True)


def install():
    import f11_delivery
    f11_delivery.OUT=OUT;f11_delivery.install()
    record=read_json(OUT/'已安装剪映草稿.json');target=Path(record['draft']).resolve();root=target.parent
    index=root/'root_meta_info.json';raw=index.read_bytes();data=json.loads(raw.decode('utf-8-sig'))
    meta=read_json(target/'draft_meta_info.json')
    matches=[x for x in data['all_draft_store'] if x.get('draft_id')==meta['draft_id'] or x.get('draft_fold_path','').replace('\\','/')==target.as_posix()]
    if not matches:
        # Append the new owned draft only, preserving every existing entry and counter.
        backup=OUT/'剪映草稿根索引_修改前备份.json';backup.write_bytes(raw)
        meta.update(draft_fold_path=target.as_posix(),draft_root_path=root.as_posix(),draft_cover=(target/'draft_cover.jpg').as_posix(),
                    draft_is_invisible=False,tm_draft_removed=0,tm_draft_modified=int(time.time()*1e6))
        data['all_draft_store'].insert(0,meta)
        if isinstance(data.get('draft_ids'),int):data['draft_ids']+=1
        if index.read_bytes()!=raw:raise RuntimeError('剪映根索引在读取后发生变化，保留新草稿，停止本次索引写入')
        write_json(index,data)
    after=read_json(index)
    assert any(x.get('draft_id')==meta['draft_id'] for x in after['all_draft_store'])
    for m in read_json(target/'draft_info.json')['materials'].get('videos',[])+read_json(target/'draft_info.json')['materials'].get('audios',[]):
        if m.get('path'):assert Path(m['path']).is_file() and Path(m['path']).is_relative_to(target)
    write_json(OUT/'剪映草稿登记检查.json',{'installed':True,'registered_in_native_home_index':True,'name':target.name,'draft_id':meta['draft_id'],
                                          'self_contained_paths_verified':True,'existing_draft_entries_preserved':True,'native_window_playback_verified':False})
    print(json.dumps({'registered':target.name},ensure_ascii=False),flush=True)


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('action',choices=['package','install','timecards','validate']);a=p.parse_args()
    if a.action=='install':install()
    elif a.action=='timecards':timecards()
    elif a.action=='validate':validate()
    else:readme();preview();validate()
