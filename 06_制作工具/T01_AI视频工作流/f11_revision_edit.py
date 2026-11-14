"""V02 deterministic edit. Reuses V01 shots; regenerates only requested motion."""
import argparse
from copy import deepcopy
import hashlib
import json
import math
import os
from pathlib import Path
import shutil
import subprocess
import sys
import time
import uuid
import wave

import numpy as np
from PIL import Image,ImageDraw,ImageFont

import f11_edit as base
from f11_revision import ROOT,RUN,OLD_RUN,OUT,OLD_OUT,UI
from workflow import read_json,write_json,Workflow

base.OUT=OUT
FPS=24;SR=48000
CHANGED={'03','14','39','70'}
END_TEXT=['愿有一天，','每个人都能自由出门，平安回家。']


def select_rows(partial=False):
    rows=deepcopy(read_json(OLD_OUT/'剪辑时间线.json'))
    selected={}
    for c in read_json(RUN/'state.json',{'candidates':[]})['candidates']:
        if c.get('file') and c['status']=='succeeded':
            sid=c.get('snapshot',{}).get('job',{}).get('source_shot',c['job_id'])
            selected[sid]=c
    cursor=0
    for r in rows:
        sid=r['id']
        if sid in CHANGED:
            if sid not in selected:
                if partial:continue
                raise RuntimeError('所需重做镜头未完成：'+sid)
            c=selected[sid];full=float(c['media']['duration'])
            r.update(kind='video',source=str(RUN/c['file']),source_start=0,
                     candidate=c['id'],task_id=c['task_id'],provenance='Seedance 2.5·本轮动作修订')
            r['duration']=base.quant(min({'03':3.9,'14':3.8,'39':4.9,'70':6.9}[sid],full-.065))
            r['speech']=[]
            p=RUN/'检查/台词识别'/f"{c['job_id']}_{c['id']}.json"
            if r['dialogue']:
                if not p.exists():
                    if not partial:raise RuntimeError('新对白尚未识别对时：'+sid)
                else:r['speech']=read_json(p)['segments']
        if sid in UI:
            r.update(kind='post',source=str(OUT/'后期界面'/f'{sid}.png'),provenance='原生1080p静帧，零API调用')
        if sid=='72':
            r.update(title='片尾寄语',duration=5.0,source=str(OUT/'后期界面/72.png'),kind='post',provenance='本地排版片尾寄语')
        r['start']=base.quant(cursor);r['end']=base.quant(cursor+r['duration']);cursor=r['end']
    if partial:return [r for r in rows if r['id'] in selected]
    return rows


def enhanced_path(row):
    if row['id'] not in CHANGED:
        return base.enhanced_path(row)
    values={k:row.get(k) for k in ['id','source','source_start','duration','candidate']}
    key=hashlib.sha256(json.dumps(values,sort_keys=True,ensure_ascii=False).encode()).hexdigest()[:16]
    return RUN/'高清镜头缓存'/f"{row['id']}_{key}.mp4"


def prepare_static():
    (OUT/'后期界面').mkdir(parents=True,exist_ok=True)
    for sid in UI:shutil.copy2(OLD_OUT/'后期界面'/f'{sid}.png',OUT/'后期界面'/f'{sid}.png')
    image=Image.new('RGB',(1920,1080),'#090b09');draw=ImageDraw.Draw(image)
    f1=ImageFont.truetype('C:/Windows/Fonts/simsun.ttc',64)
    f2=ImageFont.truetype('C:/Windows/Fonts/simsun.ttc',67)
    for text,y,font,color in [(END_TEXT[0],433,f1,'#d4d5c9'),(END_TEXT[1],548,f2,'#f2eee3')]:
        bbox=draw.textbbox((0,0),text,font=font);draw.text(((1920-(bbox[2]-bbox[0]))/2,y),text,font=font,fill=color)
    image.save(OUT/'后期界面/72.png')
    write_json(OUT/'片尾文案.json',{'text':''.join(END_TEXT),'hold_seconds':5,'previous_title_card_removed':True})


def render(rows):
    folder=OUT/'剪辑素材';folder.mkdir(parents=True,exist_ok=True)
    prepare_static()
    old={r['id']:r for r in read_json(OLD_OUT/'剪辑时间线.json')}
    for r in rows:
        sid=r['id'];target=folder/f'{sid}.mp4'
        if sid not in CHANGED|UI|{'11','55','71','72'}:
            for ext in ['mp4','wav']:
                p=OLD_OUT/'剪辑素材'/f'{sid}.{ext}'
                if p.exists() and not (folder/p.name).exists():shutil.copy2(p,folder/p.name)
            continue
        if r['kind']!='video':
            filters=['scale=1920:1080:force_original_aspect_ratio=increase:flags=lanczos','crop=1920:1080','setsar=1']
            if sid=='72':filters+=['fade=t=in:st=0:d=1.0',f"fade=t=out:st={r['duration']-1:.3f}:d=1.0"]
            base.ff(['-y','-loop','1','-framerate','24','-i',r['source'],'-t',base.fmt(r['duration']),
                     '-an','-vf',','.join(filters),'-c:v','libx264','-preset','fast','-threads','4','-crf','18',
                     '-pix_fmt','yuv420p','-r','24','-movflags','+faststart',str(target)])
            write_json(folder/f'{sid}.json',{**r,'static_image_hold':True,'camera_motion':False,'api_generated':False})
        else:
            original_enhanced=base.enhanced_path
            try:
                base.enhanced_path=enhanced_path_for_base
                base.render_row(r)
            finally:base.enhanced_path=original_enhanced
        print(json.dumps({'revised_visual':sid,'duration':r['duration']},ensure_ascii=False),flush=True)


# Save the old implementation before the base renderer is temporarily bound.
OLD_ENHANCED=base.enhanced_path
def enhanced_path_for_base(row):
    return enhanced_path(row) if row['id'] in CHANGED else OLD_ENHANCED(row)


def wav_read(path):
    with wave.open(str(path),'rb') as f:
        assert f.getsampwidth()==2 and f.getframerate()==SR and f.getnchannels()==2
        return np.frombuffer(f.readframes(f.getnframes()),dtype='<i2').reshape(-1,2).astype(np.float32)/32768


def wav_write(path,data):
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
    with wave.open(str(path),'wb') as f:
        f.setnchannels(2);f.setsampwidth(2);f.setframerate(SR)
        f.writeframes((np.clip(data,-1,1)*32767).astype('<i2').tobytes())
    return path


def fade(data,begin=.5,end=.5):
    a=min(len(data),round(begin*SR));b=min(len(data),round(end*SR))
    if a:data[:a]*=np.linspace(0,1,a,dtype=np.float32)[:,None]
    if b:data[-b:]*=np.linspace(1,0,b,dtype=np.float32)[:,None]
    return data


def loop_crossfade(data,count,cross=.55):
    if len(data)>=count:return data[:count].copy()
    overlap=min(round(cross*SR),len(data)//3);step=len(data)-overlap
    out=np.zeros((count,2),np.float32);t=0
    while t<count:
        piece=data[:min(len(data),count-t)].copy()
        if t:fade(piece,cross,0)
        if t+len(piece)<count:fade(piece,0,cross)
        out[t:t+len(piece)]+=piece;t+=step
    return out


def decode_music(musicid):
    path=OUT/'声音/配乐候选'/f'{musicid}.m4a';out=OUT/'声音/配乐候选'/f'{musicid}_48k.wav'
    if not out.exists():
        base.ff(['-y','-i',str(path),'-vn','-af','loudnorm=I=-25:TP=-2:LRA=9,aresample=48000',
                 '-ar','48000','-ac','2','-c:a','pcm_s16le',str(out)])
    return wav_read(out)


def audio(rows,subs):
    count=round(rows[-1]['end']*SR);byid={r['id']:r for r in rows}
    native=np.zeros((count,2),np.float32)
    for r in rows:
        path=OUT/'剪辑素材'/f"{r['id']}.wav"
        if path.exists():
            data=wav_read(path);a=round(r['start']*SR);n=min(len(data),count-a);native[a:a+n]+=data[:n]
    # A pair of actual Jianying music-library recordings, crossfaded at the city-work montage.
    music=np.zeros_like(native)
    one=decode_music('7274154019756820538');two=decode_music('7378223391197399051')
    change=byid['47']['start'];overlap=3.0
    # Loop within the body of the first track, avoiding its closing cadence in mid-film.
    a=loop_crossfade(one[:round(142*SR)],round((change+overlap/2)*SR),cross=3.0)
    fade(a,2.0,overlap);music[:len(a)]+=a
    second_start=round((change-overlap/2)*SR);need=count-second_start
    b=two[max(0,len(two)-need):].copy();b=loop_crossfade(b,need,cross=3)
    fade(b,overlap,4.3);music[second_start:second_start+len(b)]+=b
    # Rise gently through the repairs and final park scene; duck smoothly under actual words.
    gain=np.ones(count,np.float32)
    gain[:round(byid['29']['start']*SR)]*=.83
    gain[round(byid['59']['start']*SR):]*=1.12
    for sub in subs:
        a=max(0,round((sub['start']-.2)*SR));b=min(count,round((sub['end']+.25)*SR))
        if b<=a:continue
        gain[a:b]=np.minimum(gain[a:b],.32)
        attack=round(.3*SR);release=round(.48*SR)
        x=max(0,a-attack);y=min(count,b+release)
        gain[x:a]=np.minimum(gain[x:a],np.linspace(1,.32,a-x))
        gain[b:y]=np.minimum(gain[b:y],np.linspace(.32,1,y-b))
    music*=gain[:,None]
    # Source location tones are taken only from clips without any scripted speech.
    # Low-pass and crossfades suppress obvious repeated foreground transients.
    ambience=np.zeros_like(native);beds={}
    sources={'home':'08','shop':'50','street':'59','park':'64'}
    for env,sid in sources.items():
        r=byid[sid];assert not r['dialogue']
        dest=OUT/'声音/环境底声'/f'{env}.wav';dest.parent.mkdir(parents=True,exist_ok=True)
        base.ff(['-y','-ss',str(r['source_start']),'-i',r['source'],'-t',str(r['duration']),'-vn',
                 '-af','highpass=f=150,lowpass=f=4000,aresample=48000','-ar','48000','-ac','2','-c:a','pcm_s16le',str(dest)])
        data=wav_read(dest);rms=float(np.sqrt(np.mean(data*data)))
        data*=.0075/max(.0001,rms);data=np.clip(data,-.06,.06);beds[env]=data
    # All visual inserts, plus nearby clips, share the same location bed.
    groups=[('01','07','shop'),('08','14','home'),('15','17','street'),('18','34','shop'),
            ('35','36','home'),('37','41','street'),('42','46','shop'),('47','50','street'),
            ('51','51','home'),('52','58','shop'),('59','63','street'),('64','71','park')]
    for first,last,env in groups:
        a=max(0,round((byid[first]['start']-.25)*SR));b=min(count,round((byid[last]['end']+.25)*SR))
        data=loop_crossfade(beds[env],b-a,.65);fade(data,.4,.6);ambience[a:b]+=data
    # Bring the tone up slightly beneath UI holds, keeping it comfortably under the music.
    for r in rows:
        if r['kind']!='video' and r['id']!='72':
            a=round(r['start']*SR);b=round(r['end']*SR);ambience[a:b]*=1.35
    fade(ambience,.4,1.0)
    # Skill's default BGM volume is .6; bake the intentional ducking before that gain.
    score=wav_write(OUT/'声音/剪映配乐_已避让对白.wav',music/.6)
    env=wav_write(OUT/'声音/连续环境声.wav',ambience)
    mix=native+music+ambience;peak=float(np.max(np.abs(mix)));master_gain=min(1,.965/max(.001,peak))
    mix*=master_gain
    master=wav_write(OUT/'声音/全片混音.wav',mix)
    report={'music_source':'已安装剪映Skill曲库，按素材ID从官方素材解析接口取得',
            'music':[{'id':'7274154019756820538','title':'Soft Inspirational Piano'},
                     {'id':'7378223391197399051','title':'Where We Belong'}],
            'crossfade_seconds':overlap,'music_duck_under_dialogue_db':round(20*math.log10(.32),2),
            'master_gain':master_gain,'native_tracks_untouched':True,'ambience_sources':sources,
            'ui_audio_checks':[],'licence_scope':'剪映曲库素材用于当前课程短片；其他发行范围需按剪映对应素材条款核对'}
    for r in rows:
        if r['id'] in UI|{'11','14','55'}:
            a=round((r['start']+.1)*SR);b=round((r['end']-.1)*SR);block=mix[a:b]
            frames=[block[i:i+round(.25*SR)] for i in range(0,len(block),round(.25*SR))]
            rms=[float(np.sqrt(np.mean(x*x))) for x in frames if len(x)]
            report['ui_audio_checks'].append({'shot':r['id'],'rms_dbfs':round(20*np.log10(max(1e-9,float(np.sqrt(np.mean(block*block))))),2),
                                             'quietest_250ms_dbfs':round(20*np.log10(max(1e-9,min(rms))),2)})
    write_json(OUT/'声音/混音检查.json',report)
    return score,env,master,master_gain


def make_draft(rows,subs,score,env,master_gain):
    sys.path.insert(0,str(ROOT/'vendor'));import pyJianYingDraft as draft
    skill=Path.home()/'.codex/skills/jianying-editor';os.environ['JY_SKILL_ROOT']=str(skill);sys.path.insert(0,str(skill/'scripts'))
    from jy_wrapper import JyProject
    name='不用麻烦她_V02_动作声音精修_'+time.strftime('%m%d_%H%M%S')
    project=JyProject(name,width=1920,height=1080,drafts_root=str(OUT/'剪映草稿'),overwrite=False)
    project._explicit_res=True;project.script.fps=24
    for r in rows:
        sid=r['id'];path=Path(r['source']) if sid in UI|{'72'} else OUT/'剪辑素材'/f'{sid}.mp4'
        start_us=round(r['start']*1e6);duration_us=round(r['end']*1e6)-start_us
        if sid in UI|{'72'}:
            # ffprobe describes PNG streams as codec_type=video. Register these
            # explicitly as photos, so native Jianying never treats them as movies.
            staged=project._stage_local_asset(str(path.resolve()))
            mat=draft.VideoMaterial(staged,duration=duration_us)
            mat.material_type='photo';mat.duration=duration_us
            project._ensure_track(draft.TrackType.video,'全片画面')
            seg=draft.VideoSegment(mat,draft.trange(start_us,duration_us),
                                   source_timerange=draft.trange(0,duration_us))
            project.script.add_segment(seg,'全片画面')
        else:
            seg=project.add_media_safe(str(path.resolve()),start_time=start_us,duration=duration_us,track_name='全片画面')
        if seg is None:raise RuntimeError('草稿画面导入失败：'+sid)
        seg.volume=0
        if sid=='72':
            # PNG is truly static. Use alpha fades only for the final typography.
            try:
                seg.add_keyframe(draft.KeyframeProperty.alpha,'0s',0)
                seg.add_keyframe(draft.KeyframeProperty.alpha,'1s',1)
                seg.add_keyframe(draft.KeyframeProperty.alpha,'4s',1)
                seg.add_keyframe(draft.KeyframeProperty.alpha,'5s',0)
            except (AttributeError,TypeError):pass
        p=OUT/'剪辑素材'/f'{sid}.wav'
        if p.exists():
            # Spoken overlaps from shots 24 and 34 remain separate tracks.
            t='门外呼喊与承接' if sid in {'24','34'} else '对白与现场声'
            a=project.add_media_safe(str(p.resolve()),start_time=start_us,track_name=t)
            if a is None:raise RuntimeError('草稿声音导入失败：'+sid)
            a.volume=master_gain
    for x in subs:
        project.add_text_simple(x['text'],start_time=f"{x['start']}s",duration=f"{max(.25,x['end']-x['start'])}s",track_name='对白字幕',
                                style=draft.TextStyle(size=5.2),clip_settings=draft.ClipSettings(transform_y=-.84))
    for sid,label in [('12','几天后'),('42','数周后'),('47','此后数月'),('55','几天后'),('66','两年后的春天')]:
        r=next(x for x in rows if x['id']==sid)
        project.add_text_simple(label,start_time=f"{r['start']+.15}s",duration=f"{min(2.35,r['duration']-.25)}s",track_name='时间提示',
                                style=draft.TextStyle(size=4.5),clip_settings=draft.ClipSettings(transform_y=.8,transform_x=-.65))
    bgm=project.add_media_safe(str(score.resolve()),start_time='0s',track_name='剪映曲库配乐_已避让对白');bgm.volume=.6*master_gain
    amb=project.add_media_safe(str(env.resolve()),start_time='0s',track_name='连续环境声');amb.volume=master_gain
    saved=project.save();folder=Path(saved['draft_path']);content=read_json(folder/'draft_info.json')
    content.update(id=str(uuid.uuid4()).upper(),name=name,fps=24)
    for m in content['materials'].get('videos',[])+content['materials'].get('audios',[]):m['local_material_id']=m.get('local_material_id') or str(uuid.uuid4()).upper()
    write_json(folder/'draft_info.json',content);write_json(folder/'draft_content.json',content)
    cover=folder/'draft_cover.jpg';base.ff(['-y','-ss','1','-i',str(OUT/'剪辑素材/71.mp4'),'-frames:v','1','-vf','scale=480:-1',str(cover)])
    meta=read_json(folder/'draft_meta_info.json');now=int(time.time()*1e6)
    meta.update(draft_name=name,draft_id=content['id'],draft_fold_path=str(folder),draft_root_path=str(folder.parent),draft_cover=str(cover),tm_draft_create=now,tm_draft_modified=now,tm_duration=round(rows[-1]['end']*1e6))
    write_json(folder/'draft_meta_info.json',meta)
    for m in content['materials'].get('videos',[])+content['materials'].get('audios',[]):
        if m.get('path'):assert Path(m['path']).is_file() and Path(m['path']).is_relative_to(folder)
    n=sum(len(t['segments']) for t in content['tracks'] if t['type']=='video');assert n==72
    write_json(OUT/'剪映草稿验证.json',{'saved':True,'path':str(folder),'video_segments':n,'text_segments':sum(len(t['segments']) for t in content['tracks'] if t['type']=='text'),
               'ui_imported_as_still_photos':sorted(UI),'bgm_audio_track':True,'separate_continuous_ambience_track':True,'self_contained':True,'native_ui_export_verified':False})
    return folder


def gather(rows):
    dest=OUT/'原始视频';dest.mkdir(exist_ok=True);records=[]
    old=read_json(OLD_OUT/'素材索引.json');new=read_json(RUN/'state.json')['candidates']
    for r in rows:
        if r['kind']!='video':continue
        cid=r['candidate'];prev=next((x for x in old if x['candidate']==cid),None)
        source=Path(prev['file']) if prev else Path(r['source']);target=dest/(r['id']+'_'+cid+'.mp4')
        if not target.exists():shutil.copy2(source,target)
        c=next((x for x in new if x['id']==cid),None)
        records.append({'shot':r['id'],'candidate':cid,'file':str(target),'source':r['provenance'],'task_id':r.get('task_id'),
                        'selected':True,'charged_in_this_revision':c is not None,'usage':c.get('usage') if c else prev.get('usage') if prev else None})
    write_json(OUT/'素材索引.json',records)
    import csv
    with (OUT/'素材索引.csv').open('w',encoding='utf-8-sig',newline='') as f:
        w=csv.DictWriter(f,fieldnames=['shot','candidate','file','source','task_id','selected','charged_in_this_revision'],extrasaction='ignore');w.writeheader();w.writerows(records)


def assemble():
    rows=select_rows();assert len(rows)==72 and rows[-1]['end']<300
    write_json(OUT/'剪辑时间线.json',rows);render(rows)
    subs=base.save_subtitles(rows);score,env,master,gain=audio(rows,subs);gather(rows)
    listing=OUT/'concat.txt';listing.write_text('\n'.join("file '"+(OUT/'剪辑素材'/f"{r['id']}.mp4").as_posix().replace("'","'\\''")+"'" for r in rows),'utf-8')
    clean=OUT/'不用麻烦她_1080p_无字幕.mp4'
    base.ff(['-y','-f','concat','-safe','0','-i',str(listing),'-i',str(master),'-map','0:v','-map','1:a','-c:v','copy','-c:a','aac','-b:a','192k','-shortest','-movflags','+faststart',str(clean)])
    film=OUT/'不用麻烦她_1080p_字幕版.mp4'
    base.ff(['-y','-i',str(clean),'-vf',"ass=filename='"+(OUT/'film.ass').as_posix().replace(':','\\:')+"'",'-c:v','libx264','-preset','fast','-threads','6','-crf','18','-c:a','copy','-movflags','+faststart',str(film)])
    finalize()


def finalize():
    # Resume a draft-only failure without re-encoding an already completed movie.
    rows=read_json(OUT/'剪辑时间线.json');subs=read_json(OUT/'字幕时间线.json')
    sound=read_json(OUT/'声音/混音检查.json');gain=sound['master_gain']
    score=OUT/'声音/剪映配乐_已避让对白.wav';env=OUT/'声音/连续环境声.wav'
    folder=make_draft(rows,subs,score,env,gain)
    film=OUT/'不用麻烦她_1080p_字幕版.mp4'
    base.ff(['-i',str(film),'-f','null','-'])
    write_json(OUT/'交付验证.json',{'full_decode_passed':True,'probe':base.read_probe(film),'timeline_seconds':rows[-1]['end'],'shots':len(rows),'subtitle_chunks':len(subs),'draft':str(folder),
                'new_motion_shots':sorted(CHANGED),'static_ui_shots':sorted(UI),'previous_version_preserved':True})
    print(json.dumps({'film':str(film),'draft':str(folder),'duration':rows[-1]['end']},ensure_ascii=False),flush=True)


def upscale():
    # Reuse the installed offline GPU pipeline only for the four new cuts.
    import f11_upscale
    old_sel=base.select_rows;old_path=base.enhanced_path
    try:
        base.select_rows=select_rows;base.enhanced_path=enhanced_path_for_base;f11_upscale.RUN=RUN
        f11_upscale.enhance_selected(False)
    finally:base.select_rows=old_sel;base.enhanced_path=old_path


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('action',choices=['static','upscale','assemble','finalize']);a=p.parse_args()
    if a.action=='static':prepare_static()
    elif a.action=='upscale':upscale()
    elif a.action=='finalize':finalize()
    else:assemble()
