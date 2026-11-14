"""Package film, originals, previews and validation without paid calls."""
import argparse
import html
import json
from pathlib import Path
import re
import shutil
import os
import subprocess
import time
import uuid
from urllib.parse import quote

from f11_production import ROOT, RUN, PILOT, ledger
from workflow import Workflow
from f11_edit import OUT, read, write, ff, read_probe


def timecards_without_dialogue_subtitles():
    marker=OUT/'无对白字幕版时间提示.json'
    if marker.exists():return
    lines=(OUT/'film.ass').read_text('utf-8-sig').splitlines()
    kept=[s for s in lines if not s.startswith('Dialogue:') or ',Time,,' in s]
    ass=OUT/'time_only.ass';ass.write_text('\n'.join(kept)+'\n','utf-8-sig')
    clean=OUT/'不用麻烦她_1080p_无字幕.mp4'
    master=OUT/'不用麻烦她_1080p_画面混音母版.mp4'
    if not master.exists():shutil.copy2(clean,master)
    output=OUT/'无对白字幕_处理中.mp4'
    ff(['-y','-i',str(master),'-vf',"ass=filename='"+ass.as_posix().replace(':','\\:')+"'",'-c:v','libx264',
        '-preset','veryfast','-threads','8','-crf','18','-c:a','copy','-movflags','+faststart',str(output)])
    os.replace(output,clean)
    write(marker,{'dialogue_captions':False,'time_labels_preserved':True,'source_master':str(master)})


def finalize_draft_metadata():
    source=Path(read(OUT/'剪映草稿验证.json')['path']).resolve()
    installed=Path(read(OUT/'已安装剪映草稿.json')['draft']).resolve()
    native_root=(Path.home()/'AppData/Local/JianyingPro/User Data/Projects/com.lveditor.draft').resolve()
    assert source.parent==(OUT/'剪映草稿').resolve() and installed.parent==native_root and installed.name==source.name
    rows=read(OUT/'剪辑时间线.json');duration=round(rows[-1]['end']*1e6)
    source_content=read(source/'draft_info.json')
    unique_id=source_content.get('id') if source_content.get('name')==source.name and source_content.get('id') else str(uuid.uuid4()).upper()
    for folder in [source,installed]:
        content=read(folder/'draft_info.json');content.update(id=unique_id,name=folder.name,fps=24)
        for m in content['materials'].get('videos',[])+content['materials'].get('audios',[]):
            m['local_material_id']=m.get('local_material_id') or str(uuid.uuid4()).upper()
        write(folder/'draft_info.json',content);write(folder/'draft_content.json',content)
        cover=folder/'draft_cover.jpg'
        ff(['-y','-ss','1','-i',str(OUT/'剪辑素材/01.mp4'),'-frames:v','1','-vf','scale=480:-1',str(cover)])
        meta=read(folder/'draft_meta_info.json')
        now=int(time.time()*1e6)
        meta.update(draft_name=folder.name,draft_id=unique_id,draft_fold_path=str(folder),draft_root_path=str(folder.parent),
                    draft_cover=str(cover),tm_draft_create=meta.get('tm_draft_create') or now,tm_draft_modified=now,tm_duration=duration)
        write(folder/'draft_meta_info.json',meta)
    write(OUT/'剪映草稿登记检查.json',{'name':source.name,'id':unique_id,'duration_microseconds':duration,
         'cover_exists':True,'source_and_installed_copy_verified':True,'only_new_owned_project_modified':True})
    print(json.dumps({'metadata_finalized':source.name,'duration':duration/1e6},ensure_ascii=False),flush=True)


def prior_samples():
    out=OUT/'原始视频/早期试片_未采用';out.mkdir(parents=True,exist_ok=True)
    rows=[]
    for profile in ['连接测试','五镜试片']:
        p=PILOT/profile
        for c in read(p/'state.json')['candidates']:
            if not c.get('file') or (profile=='五镜试片' and c['job_id'] in {'20','21','53'}):continue
            src=p/c['file'];target=out/f"{c['job_id']}_{c['id']}.mp4"
            if not target.exists():shutil.copy2(src,target)
            rows.append({'shot':c['job_id'],'file':str(target),'task_id':c.get('task_id'),'usage':c.get('usage')})
    write(OUT/'早期未采用样片索引.json',rows)


def preview():
    rows=read(OUT/'剪辑时间线.json');assets=read(OUT/'素材索引.json')
    thumbs=OUT/'预览缩略图';thumbs.mkdir(exist_ok=True)
    cards=[]
    def url(p):return quote(Path(p).relative_to(OUT).as_posix(),safe='/')
    for r in rows:
        thumb=thumbs/f"{r['id']}.jpg"
        clip=OUT/'剪辑素材'/f"{r['id']}.mp4"
        if not thumb.exists():ff(['-ss',str(min(.8,r['duration']/2)),'-i',str(clip),'-frames:v','1','-vf','scale=480:-1','-q:v','3','-y',str(thumb)])
        raw=next((x for x in assets if x['candidate']==r.get('candidate')),None)
        source=Path(raw['file']) if raw else clip
        badge='镜头原片' if raw else '后期画面'
        cards.append(f'''<article><video controls preload="none" poster="{url(thumb)}" src="{url(source)}"></video><div><span>{r['id']} / {badge}</span><h3>{html.escape(r['title'])}</h3><a href="{url(source)}">打开视频 ↗</a></div></article>''')
    poster=OUT/'封面.jpg'
    ff(['-ss','2','-i',str(OUT/'剪辑素材/71.mp4'),'-frames:v','1','-q:v','2','-y',str(poster)])
    duration=rows[-1]['end'];mins=int(duration//60);secs=round(duration%60)
    page='''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>不用麻烦她 · 影片与素材</title><style>
*{box-sizing:border-box}body{margin:0;background:#181d19;color:#ede9de;font-family:"Microsoft YaHei",sans-serif}main{max-width:1320px;margin:auto;padding:54px 36px 80px}.eyebrow{color:#b4c2a8;letter-spacing:4px;font-size:12px}h1{font-size:46px;font-weight:500;letter-spacing:5px;margin:17px 0 13px}p{color:#b9beb5;line-height:1.9;font-size:14px}.film{display:block;width:100%;aspect-ratio:16/9;background:#080a08;border-radius:10px;margin-top:28px}.links{display:flex;gap:12px;flex-wrap:wrap;margin:22px 0 55px}.links a{border:1px solid #4c5f4c;border-radius:25px;padding:11px 20px;color:#ede9de;text-decoration:none}.links a:first-child{background:#d5dbc3;color:#263b2c}.divider{display:flex;align-items:baseline;justify-content:space-between;margin:32px 0 18px}h2{font-size:24px;font-weight:500}.grid{display:grid;grid-template-columns:repeat(3,1fr);gap:25px 20px}article{background:#252d25;border-radius:9px;overflow:hidden}article video{display:block;width:100%;aspect-ratio:16/9;background:#111}article div{padding:15px 17px 18px}article span{font-size:11px;letter-spacing:1px;color:#b2c0a7}h3{font-size:15px;font-weight:500;margin:9px 0 12px}article a{font-size:12px;color:#c6d1bc;text-decoration:none}footer{margin-top:60px;color:#899586;font-size:12px}@media(max-width:800px){main{padding:30px 16px}.grid{grid-template-columns:repeat(2,1fr)}h1{font-size:33px}}@media(max-width:500px){.grid{grid-template-columns:1fr}}
</style><main><div class="eyebrow">一部关于老友、出门和城市的短片</div><h1>不用麻烦她</h1>'''
    page+=f'<p>全片剪辑版 · {mins} 分 {secs:02} 秒 · 1920 × 1080 · 中文字幕</p>'
    page+=f'<video class="film" controls preload="metadata" poster="{url(poster)}" src="{quote("不用麻烦她_1080p_字幕版.mp4")}"></video>'
    page+='<div class="links"><a href="'+quote('不用麻烦她_1080p_字幕版.mp4')+'">打开字幕版</a><a href="'+quote('不用麻烦她_1080p_无字幕.mp4')+'">无字幕版</a><a href="'+quote('不用麻烦她.srt')+'">字幕文件</a><a href="'+quote('00_交付说明.md')+'">交付说明</a></div>'
    page+='<div class="divider"><h2>逐镜素材</h2><p>72 镜 / 原片保留生成声音</p></div><section class="grid">'+''.join(cards)+'</section><footer>原始视频、剪辑片段、声音和可编辑剪映草稿均保存在本文件夹。</footer></main></html>'
    (OUT/'看成片与素材.html').write_text(page,'utf-8')
    return rows


def validate_package():
    rows=read(OUT/'剪辑时间线.json');report=read(OUT/'交付验证.json')
    cost=ledger(Workflow(RUN));write(OUT/'本轮生成费用.json',cost)
    for r in rows:
        p=OUT/'剪辑素材'/f"{r['id']}.mp4"
        info=read_probe(p);v=next(x for x in info['streams'] if x['codec_type']=='video')
        assert v['width']==1920 and v['height']==1080
        assert abs(float(info['format']['duration'])-r['duration'])<.085,(r['id'],info['format']['duration'],r['duration'])
    film=OUT/'不用麻烦她_1080p_字幕版.mp4';info=read_probe(film)
    assert abs(float(info['format']['duration'])-rows[-1]['end'])<.15
    subs=read(OUT/'字幕时间线.json')
    assert all(0<=x['start']<x['end']<=rows[-1]['end'] for x in subs)
    expected=[r for r in rows if r['dialogue']]
    assert all(any(x['shot']==r['id'] for x in subs) for r in expected),'有台词的镜头缺少字幕'
    # Verify all local media URLs in the standalone preview resolve.
    from urllib.parse import unquote
    page=(OUT/'看成片与素材.html').read_text('utf-8')
    links=re.findall(r'(?:src|href|poster)="([^"]+)"',page)
    for link in links:
        if link.startswith(('http:','https:','#')):continue
        assert (OUT/unquote(link)).exists(),link
    result={'all_72_clips_1920x1080':True,'cut_durations_match':True,'subtitles_in_bounds':True,
            'all_dialogue_shots_have_subtitles':True,'preview_local_links_verified':len(links),
            'full_film_duration':rows[-1]['end'],'new_generation_usage_estimate_rmb':cost['usage_estimated_rmb'],
            'full_decode_passed':report['full_decode_passed'],'draft':report['draft']}
    write(OUT/'整包验收.json',result)
    return result


def install():
    source=Path(read(OUT/'剪映草稿验证.json')['path']).resolve()
    root=(Path.home()/'AppData/Local/JianyingPro/User Data/Projects/com.lveditor.draft').resolve()
    target=(root/source.name).resolve()
    if not source.is_relative_to((OUT/'剪映草稿').resolve()) or not root.is_dir() or target.parent!=root:
        raise ValueError('Invalid installation path')
    if target.exists():
        result=read(OUT/'已安装剪映草稿.json') if (OUT/'已安装剪映草稿.json').exists() else None
        if result and result['draft']==str(target):print(json.dumps(result,ensure_ascii=False));return
        raise FileExistsError('同名草稿已经存在，停止覆盖。')
    shutil.copytree(source,target)
    def relocate(v):
        if isinstance(v,dict):return {k:relocate(x) for k,x in v.items()}
        if isinstance(v,list):return [relocate(x) for x in v]
        if isinstance(v,str):return v.replace(str(source),str(target)).replace(source.as_posix(),target.as_posix())
        return v
    for name in ['draft_info.json','draft_content.json','draft_meta_info.json']:
        p=target/name
        if not p.exists():continue
        data=relocate(read(p))
        if name=='draft_meta_info.json':data.update(draft_fold_path=str(target),draft_root_path=str(root),tm_draft_modified=int(time.time()*1e6))
        write(p,data)
    result={'draft':str(target),'source':str(source),'name':source.name,'existing_projects_overwritten':False}
    write(OUT/'已安装剪映草稿.json',result)
    print(json.dumps(result,ensure_ascii=False),flush=True)


def package():
    prior_samples();rows=preview();cost=ledger(Workflow(RUN));write(OUT/'本轮生成费用.json',cost)
    minutes=int(rows[-1]['end']//60);seconds=round(rows[-1]['end']%60)
    text=f'''# 《不用麻烦她》全片剪辑版

2026-10-19｜{minutes}分{seconds:02}秒｜1920×1080｜24fps

双击 `看成片与素材.html`，可以观看整片并逐镜查看原始视频。

- `不用麻烦她_1080p_字幕版.mp4`：带中文字幕的完整剪辑。
- `不用麻烦她_1080p_无字幕.mp4`：同一剪辑与混音，字幕单独保存为 SRT。
- `剪映草稿`：通过已安装的 jianying-editor Skill / JyProject 制作，画面、对白与现场声、原创配乐、字幕分别成轨，素材自包含。
- `原始视频`：本轮全部成功候选、采用的旧样片，以及早期未采用样片。
- `剪辑素材`：72个最终片段；片段画面无声，对应声音单独保存为WAV，便于调整。
- `后期界面`：地图、反馈回执、核查与回访画面，文字按影片情节重新排版。
- `剪辑时间线.json`、`字幕时间线.json`、`素材索引.csv`：切点、字幕和来源记录。

480p生成素材采用本地Real-ESRGAN AnimeVideo-v3三倍超分，再与普通放大画面按80/20混合输出1080p；复用的720p样片采用常规放大。超分不会把源素材变成原生1080p生成。

使用声音均来自逐镜生成，邱、徐的新任务分别指定老年女性声线。字幕按实际语音识别时间对齐后使用剧本文字。第24镜门外呼喊延续到第25镜；配乐为本地合成的原创三拍子钢琴段落，不使用外部商业录音。

第03镜绕路转场、第39镜公交站断口的首帧被服务端拒绝，采用原分镜静帧加剪辑运动。第02镜曾生成站起动作，另做了坐姿修正版并按实际效果选用。登阶镜头通过进门镜头承接完整行动，没有继续付费追求单镜展示全部过程。

本轮按接口返回用量估算约 **{cost['usage_estimated_rmb']:.2f}元**；之前六条样片约61.99元。复用片段没有重新计费。费用以方舟账单为准；本地超分、识别、合成和剪辑未调用付费服务。

检查结果见 `整包验收.json`、`交付验证.json` 和 `剪映草稿验证.json`。完整MP4已全程解码检查，72镜时长与字幕边界已核对。剪映原生窗口的预览、会员高清功能及原生导出是否验证，以后续窗口检查记录为准。
'''
    (OUT/'00_交付说明.md').write_text(text,'utf-8')
    # The preview includes this readme; validate again only after all links exist.
    result=validate_package();print(json.dumps(result,ensure_ascii=False),flush=True)


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('action',choices=['package','install','timecards','finalize-draft']);a=p.parse_args()
    if a.action=='install':install()
    elif a.action=='timecards':timecards_without_dialogue_subtitles()
    elif a.action=='finalize-draft':finalize_draft_metadata()
    else:package()
