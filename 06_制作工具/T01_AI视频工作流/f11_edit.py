"""Deterministic full-film edit, original score, subtitles, and installed JyProject skill draft."""
import argparse
import csv
import difflib
import hashlib
import json
import math
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import time
import uuid
import wave

import numpy as np
from PIL import Image, ImageDraw, ImageFont
from f11_production import ROOT, RUN, SOURCE, PILOT

OUT=ROOT.parents[1]/'05_汇报与成片/V01_不用麻烦她_2026-10-19'
FPS=24
FONT='C:/Windows/Fonts/msyh.ttc'


def read(p): return json.loads(Path(p).read_text('utf-8-sig'))
def write(p,v):
    Path(p).parent.mkdir(parents=True,exist_ok=True)
    Path(p).write_text(json.dumps(v,ensure_ascii=False,indent=2),'utf-8')
def command(args):
    r=subprocess.run(args,capture_output=True,text=True,encoding='utf-8',errors='replace')
    if r.returncode: raise RuntimeError(r.stderr[-3500:])
    return r.stdout
def ff(args): return command(['ffmpeg','-hide_banner','-loglevel','error',*args])
def quant(s): return round(s*FPS)/FPS
def fmt(s): return f'{s:.6f}'
def clean(s): return ''.join(re.findall(r'[\u4e00-\u9fffA-Za-z0-9]',s))


def enhanced_path(row):
    data={k:row.get(k) for k in ['id','source','source_start','duration','candidate']}
    key=hashlib.sha256(json.dumps(data,sort_keys=True,ensure_ascii=False).encode()).hexdigest()[:16]
    return RUN/'高清镜头缓存'/f"{row['id']}_{key}.mp4"


def speech(c):
    p=RUN/'检查/台词识别'/f"{c['job_id']}_{c['id']}.json"
    return read(p)['segments'] if p.exists() else []


def select_rows(partial=False):
    story=read(SOURCE/'storyboard.json')['shots']
    speed={r['id']:r for r in read(PILOT/'节奏对比/全片稍快版预算.json')['jobs']}
    state=read(RUN/'state.json')
    selected={}
    for c in state['candidates']:
        if c.get('file') and c['status']=='succeeded': selected[c['job_id']]=c
    overrides=read(RUN/'剪辑修订.json') if (RUN/'剪辑修订.json').exists() else {}
    rows=[];cursor=0
    for s in story:
        sid=s['id'];dur=speed[sid]['proposed_edit_seconds'] if sid in speed else s['edit_seconds']
        c=selected.get('02R' if sid=='02' and '02R' in selected else sid)
        override=overrides.get(sid,{})
        if c:
            full=float(c['media']['duration']);sp=speech(c)
            start=min(.35,max(0,full-dur))
            if sp and sid!='24':
                first=min(x['start'] for x in sp);last=max(x['end'] for x in sp)
                start=max(0,min(first-.45,full-dur))
                dur=max(dur,last+.22-start)
            if sid=='15': start=1.4;dur=5.4
            if sid=='16': start=1.3;dur=min(4.9,full-1.4)
            if sid=='17':start=.65;dur=2.7
            if sid=='21':start=.65;dur=4.3
            if sid=='23':start=.6;dur=3.8
            if sid=='24':start=0;dur=1.8
            if sid=='25':start=1.0;dur=3.7
            if sid=='37':start=1.2;dur=4.6
            if sid=='38':start=0;dur=2.1
            if sid=='53':start=2.2;dur=5.65
            if sid=='61':start=.4;dur=min(5.5,full-.5)
            if sid=='70':start=.1;dur=min(6.8,full-.2)
            if sid=='71':start=.15;dur=min(6.7,full-.25)
            start=override.get('source_start',start);dur=override.get('duration',dur)
            if sp and sid not in {'24','34'}:
                dur=max(dur,max(x['end'] for x in sp)+.15-start)
            dur=min(dur,full-start-.025)
            if sid=='02' and c['job_id']=='02':dur=min(dur,1.75)
            row={'id':sid,'title':s['title'],'kind':'video','candidate':c['id'],
                 'source':str((RUN/c['file']).resolve()),'source_start':start,
                 'duration':quant(dur),'dialogue':s['dialogue'],'speech':sp,
                 'provenance':c['source'],'task_id':c.get('task_id')}
        else:
            if sid=='72':dur=3.0
            terminal=any(x['job_id']==sid and x['status'] in {'rejected','failed','cancelled','expired'} for x in state['candidates'])
            if s['method']=='video' and not terminal:
                if partial: continue
                raise RuntimeError('镜头尚未完成：'+sid)
            row={'id':sid,'title':s['title'],'kind':'post' if s['method']!='video' else 'still_fallback',
                 'source':str((SOURCE/s['storyboard_image']).resolve()),'source_start':0,
                 'duration':quant(dur),'dialogue':s['dialogue'],'speech':[],
                 'provenance':'本地界面合成' if s['method']!='video' else '服务端拒绝后使用分镜静帧剪辑'}
        row['start']=quant(cursor);row['end']=quant(cursor+row['duration']);cursor=row['end'];rows.append(row)
    return rows


def ui_graphic(sid):
    p=OUT/'后期界面'/f'{sid}.png';p.parent.mkdir(parents=True,exist_ok=True)
    im=Image.new('RGB',(1920,1080),'#f1ecdf');d=ImageDraw.Draw(im)
    green='#365b48';ink='#293f34';muted='#8d958b';orange='#c27543'
    def font(n):return ImageFont.truetype(FONT,n)
    def text(x,y,t,n=36,fill=ink):d.text((x,y),t,font=font(n),fill=fill)
    def panel(box,fill='#fcf9f1',radius=24):d.rounded_rectangle(box,radius,fill=fill)
    text(84,49,'市民服务',30,green);d.line((84,110,1836,110),fill='#d4d4c5',width=2)
    def city():
        panel((655,150,1840,982),'#e6e4d5')
        rng=np.random.default_rng(38)
        for x in range(690,1800,125):
            for y in range(190,930,120):
                w=int(rng.integers(48,86));h=int(rng.integers(40,73))
                d.rounded_rectangle((x,y,x+w,y+h),8,fill=['#d3d1bb','#ced2bb','#d7ccb4'][int(rng.integers(0,3))])
        d.line([(660,850),(850,810),(1080,890),(1330,760),(1600,850),(1840,760)],fill='#b4ccca',width=80)
        d.line([(720,345),(1050,345),(1050,595),(1420,595),(1420,300),(1770,300)],fill='#fffaf0',width=45,joint='curve')
        d.line([(810,950),(810,530),(1720,530),(1720,900)],fill='#fffaf0',width=35,joint='curve')
    def point(x,y,label,color):
        d.ellipse((x-18,y-18,x+18,y+18),fill=color,outline='#fcf9f1',width=5)
        panel((x-60,y-82,x+220,y-26),'#fcf9f1',14);text(x-39,y-77,label,27,color)
    if sid in {'18','30','41','57','58'}:
        city()
        titles={'18':'本次通行完成','30':'更新沿途路况','41':'居民反馈','57':'入口核查完成','58':'继续处理下一处'}
        text(86,160,titles[sid],52)
        if sid=='18':
            text(88,244,'入口可通行，已共享',34,green)
            text(88,326,'西街柱口',37);text(88,378,'本次通行成功',29,muted)
            text(88,484,'青禾布店',37);text(88,536,'本次通行成功',29,muted)
            d.line([(820,345),(1050,345),(1050,595),(1420,595)],fill=green,width=10)
            point(820,345,'西街柱口',green);point(1420,595,'青禾布店',green)
            panel((86,788,570,948),'#e0e8d9');text(118,820,'共享记录已更新',34,green)
        elif sid=='30':
            text(88,245,'保留入口的实际情况',31,muted)
            text(88,341,'青禾布店',38);text(88,409,'入口有三级台阶',34,orange);text(88,460,'侧面坡道较陡',34,orange)
            text(88,607,'西街柱口',38);text(88,675,'柱口较窄，需绕行',34,orange)
            point(820,345,'柱口较窄',orange);point(1420,595,'台阶 · 陡坡',orange)
        elif sid=='41':
            text(88,244,'待核查 · 12 条反馈',31,orange)
            for i,(name,note) in enumerate([('西街柱口','4 次反馈 · 轮椅无法通过'),('青禾布店','台阶与陡坡'),('诊所入口','门槛过高'),('公交站','人行道断开')]):
                yy=335+i*143;panel((84,yy,581,yy+116));text(108,yy+13,name,34);text(108,yy+65,note,26,muted)
            for x,y,label in [(820,345,'西街柱口'),(1420,595,'青禾布店'),(1690,530,'诊所'),(1050,750,'公交站')]:point(x,y,label,orange)
        elif sid=='57':
            text(88,257,'青禾布店',40);text(88,336,'普通轮椅试用通过',34,green)
            text(88,400,'坡道、转弯平台已复查',29,muted)
            panel((88,550,580,912),'#e0e8d9');text(122,598,'核查完成',45,green);text(122,697,'入口信息已更新',30,green)
            for x,y,label in [(820,345,'西街柱口'),(1690,530,'诊所'),(1050,750,'公交站')]:point(x,y,label,orange)
            point(1420,595,'青禾布店 · 可通行',green)
        else:
            text(88,250,'青禾布店 · 已完成',32,green)
            for i,(name,note) in enumerate([('诊所入口','待现场测量'),('公交站','待核查'),('西街路口','已安排施工')]):
                yy=370+i*175;panel((84,yy,581,yy+144));text(110,yy+22,name,35);text(110,yy+83,note,29,orange)
            point(1420,595,'青禾布店',green);point(1690,530,'下一处 · 诊所',orange)
    elif sid=='32':
        panel((280,165,1640,941));text(370,236,'障碍反馈',55)
        for i,name in enumerate(['西街柱口 · 通道过窄','青禾布店 · 台阶与陡坡']):
            yy=370+i*137;panel((365,yy,1548,yy+103),'#eeede2');text(405,yy+25,name,37)
        panel((365,710,1548,846),'#e0e8d9');text(688,748,'已接收，待核查',45,green)
    elif sid=='65':
        text(92,160,'无障碍设施回访',54)
        entries=[('第1年 · 秋','入口回访','通道保持畅通',green),('第2年 · 春','坡道扶手松动','居民提交维修记录',orange),('维修后复查','扶手已重新固定','照片与复查记录已更新',green)]
        d.line((154,337,154,892),fill='#bac4b5',width=5)
        for i,(date,title,note,col) in enumerate(entries):
            y=314+i*204;d.ellipse((137,y+26,171,y+60),fill=col)
            panel((210,y,1815,y+169));text(246,y+23,date,31,col);text(655,y+23,title,39);text(657,y+91,note,31,muted)
    else:
        raise ValueError(sid)
    im.save(p);return p


def render_row(row):
    folder=OUT/'剪辑素材';folder.mkdir(parents=True,exist_ok=True)
    sid=row['id'];target=folder/f'{sid}.mp4';meta=folder/f'{sid}.json'
    enhanced=enhanced_path(row)
    visual={k:row.get(k) for k in ['id','source','source_start','duration','candidate','kind']}
    visual['enhanced']=enhanced.is_file()
    if sid=='71':visual['entry_blend_seconds']=.32
    if row['id'] in {'24','34'}:visual['speech']=row['speech']
    sig=hashlib.sha256(json.dumps(visual,ensure_ascii=False,sort_keys=True).encode()).hexdigest()
    if target.exists() and meta.exists() and read(meta).get('signature')==sig:return
    duration=row['duration'];source=row['source'];filters=[]
    if sid in {'18','30','32','41','57','58','65'}:source=str(ui_graphic(sid))
    still=row['kind']!='video'
    args=['-y']
    if still:args+=['-loop','1','-framerate',str(FPS),'-i',source]
    else:args+=['-ss',fmt(row['source_start']),'-i',source]
    if still:
        filters += [f"scale=2112:1188:force_original_aspect_ratio=increase,crop=2112:1188,zoompan=z='1.005+0.00012*on':x='iw/2-iw/zoom/2':y='ih/2-ih/zoom/2':d=1:s=1920x1080:fps={FPS}"]
    else:
        filters += ['scale=1920:1080:flags=lanczos,setsar=1','unsharp=5:5:0.22:3:3:0','eq=contrast=1.012:saturation=1.012']
    if sid=='01':filters += ['fade=t=in:st=0:d=0.28']
    if sid=='71':filters += [f'fade=t=out:st={max(0,duration-.7):.3f}:d=0.7']
    if sid=='72':
        # Rebuild as native-resolution title so no generated small glyphs remain.
        p=OUT/'后期界面/72.png';p.parent.mkdir(parents=True,exist_ok=True)
        im=Image.new('RGB',(1920,1080),'#080907');d=ImageDraw.Draw(im)
        f=ImageFont.truetype('C:/Windows/Fonts/simsun.ttc',100)
        t='不用麻烦她';box=d.textbbox((0,0),t,font=f);d.text(((1920-box[2])/2,465),t,font=f,fill='#eeeade');im.save(p)
        args=['-y','-loop','1','-framerate',str(FPS),'-i',str(p)]
        filters=['setsar=1','fade=t=in:st=0:d=0.5',f'fade=t=out:st={duration-.5:.3f}:d=0.5']
    if enhanced.is_file() and row['kind']=='video':
        backup=OUT/'剪辑素材_常规放大版'/target.name
        backup.parent.mkdir(parents=True,exist_ok=True)
        if target.exists() and not backup.exists():shutil.copy2(target,backup)
        shutil.copy2(enhanced,target)
    else:
        ff(args+['-t',fmt(duration),'-an','-vf',','.join(filters),'-r',str(FPS),'-c:v','libx264','-preset','fast','-threads','4','-crf','18','-pix_fmt','yuv420p','-movflags','+faststart',str(target)])
    if sid=='71':
        # A short dissolve from the preceding rear view lets the final wide shot
        # resume the shared dance without a harsh change of chair orientation.
        previous=folder/'70.mp4';tail=folder/'70_tail.png';soft=folder/'71_soft.mp4'
        if previous.exists():
            ff(['-y','-sseof','-0.05','-i',str(previous),'-frames:v','1',str(tail)])
            blend="[0:v]setsar=1[a];[1:v]setsar=1[b];[a][b]blend=all_expr='if(lt(T,0.32),A*(T/0.32)+B*(1-T/0.32),A)'[v]"
            ff(['-y','-i',str(target),'-loop','1','-framerate','24','-i',str(tail),'-filter_complex',blend,'-map','[v]',
                '-t',fmt(duration),'-an','-c:v','libx264','-preset','fast','-threads','4','-crf','18','-pix_fmt','yuv420p',str(soft)])
            os.replace(soft,target)
    audio=None
    if row['kind']=='video':
        audio=folder/f'{sid}.wav'
        audio_duration=duration
        if sid in {'24','34'} and row['speech']:
            audio_duration=max(duration,max(s['end'] for s in row['speech'])+.18-row['source_start'])
        loud=-19 if row['dialogue'] else -30
        af=f'highpass=f=70,lowpass=f=14000,loudnorm=I={loud}:TP=-2:LRA=9,aresample=48000,afade=t=in:d=0.025,afade=t=out:st={max(.03,audio_duration-.05):.5f}:d=0.05'
        ff(['-y','-ss',fmt(row['source_start']),'-i',row['source'],'-t',fmt(audio_duration),'-vn','-af',af,'-ac','2','-ar','48000','-c:a','pcm_s16le',str(audio)])
    write(meta,{'signature':sig,'enhancement':'Real-ESRGAN AnimeVideo-v3 x3, 80% blend' if enhanced.exists() else None,'video':str(target),'audio':str(audio) if audio else None,**row})
    print(json.dumps({'rendered':sid,'duration':duration,'kind':row['kind']},ensure_ascii=False),flush=True)


def subtitles(rows):
    output=[]
    for row in rows:
        lines=row['dialogue'];sp=row['speech']
        if not lines or not sp:continue
        expected=''.join(clean(x['text']) for x in lines)
        recognized='';times=[]
        for segment in sp:
            for w in segment['words']:
                cc=clean(w['word'])
                for i,ch in enumerate(cc):
                    recognized+=ch;times.append(w['start']+(w['end']-w['start'])*(i+.5)/max(1,len(cc)))
        if not times:continue
        mapping={}
        for a,b,n in difflib.SequenceMatcher(None,expected,recognized,autojunk=False).get_matching_blocks():
            for i in range(n):mapping[a+i]=times[b+i]
        if mapping:
            keys=sorted(mapping);aligned=np.interp(np.arange(len(expected)),keys,[mapping[k] for k in keys]).tolist()
        else:aligned=np.linspace(sp[0]['start'],sp[-1]['end'],len(expected)).tolist()
        index=0
        for line in lines:
            chunks=[t for t in re.split(r'[，。？！；…,.?!;]+',line['text']) if t]
            for chunk in chunks:
                count=len(clean(chunk));start=max(0,aligned[min(index,len(aligned)-1)]-.13-row['source_start'])
                end=aligned[min(index+count-1,len(aligned)-1)]+.25-row['source_start'];index+=count
                start=row['start']+start;end=row['start']+end
                end=min(end,row['end']+(3.0 if row['id'] in {'24','34'} else 0))
                if end-start<.35:end=start+.65
                output.append({'text':chunk,'start':round(start,3),'end':round(end,3),'speaker':line['speaker'],'shot':row['id']})
    # Prevent captions from stacking at speaker changes.
    output.sort(key=lambda x:x['start'])
    for a,b in zip(output,output[1:]):
        if a['end']>b['start']:a['end']=max(a['start']+.25,b['start']-.035)
    return output


def stamp_time(s,ass=False):
    unit=100 if ass else 1000
    value=round(s*unit);whole,frac=divmod(value,unit);h,rem=divmod(whole,3600);m,sec=divmod(rem,60)
    return f'{h}:{m:02}:{sec:02}.{frac:02}' if ass else f'{h:02}:{m:02}:{sec:02},{frac:03}'


def save_subtitles(rows):
    subs=subtitles(rows);write(OUT/'字幕时间线.json',subs)
    (OUT/'不用麻烦她.srt').write_text('\n\n'.join(f"{i+1}\n{stamp_time(x['start'])} --> {stamp_time(x['end'])}\n{x['text']}" for i,x in enumerate(subs))+'\n','utf-8-sig')
    events=[]
    for x in subs:events.append(f"Dialogue: 0,{stamp_time(x['start'],True)},{stamp_time(x['end'],True)},Default,,0,0,0,,{x['text']}")
    for sid,label in [('12','几天后'),('42','数周后'),('47','此后数月'),('55','几天后'),('66','两年后的春天')]:
        r=next(x for x in rows if x['id']==sid)
        events.append(f"Dialogue: 1,{stamp_time(r['start']+.15,True)},{stamp_time(r['start']+min(2.5,r['duration']-.1),True)},Time,,0,0,0,,{label}")
    header='[Script Info]\nScriptType: v4.00+\nPlayResX: 1920\nPlayResY: 1080\nWrapStyle: 0\n\n[V4+ Styles]\nFormat: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding\nStyle: Default,Microsoft YaHei,43,&H00F2F5F4,&H000000FF,&H00202521,&H60000000,0,0,0,0,100,100,1,0,1,1.7,0.7,2,105,105,60,1\nStyle: Time,Microsoft YaHei,35,&H00F3F0E5,&H000000FF,&H00343B31,&H60000000,0,0,0,0,100,100,2,0,1,1,0.5,7,100,100,90,1\n\n[Events]\nFormat: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text\n'
    (OUT/'film.ass').write_text(header+'\n'.join(events)+'\n','utf-8-sig')
    return subs


def original_score(rows):
    sr=48000;length=rows[-1]['end'];mix=np.zeros((round(length*sr)+sr*2,2),np.float32)
    rng=np.random.default_rng(271)
    def note(at,midi,duration,amp):
        count=round(duration*sr);t=np.arange(count,dtype=np.float32)/sr;f=440*2**((midi-69)/12)
        sound=np.zeros(count,np.float32)
        for harmonic,weight in [(1,1),(2,.29),(3,.12),(4,.052),(6,.018)]:
            sound+=weight*np.sin(2*np.pi*f*harmonic*t)*np.exp(-t*(1.9+harmonic*.48))
        sound*=np.minimum(t/.009,1)*np.minimum((duration-t)/.1,1)
        sound+=rng.standard_normal(count).astype(np.float32)*.006*np.exp(-t*65)
        pos=round(at*sr)
        if pos<0 or pos+count>len(mix):return
        pan=(midi-60)/60;mix[pos:pos+count,0]+=sound*amp*(.7-pan);mix[pos:pos+count,1]+=sound*amp*(.7+pan)
    byid={x['id']:x for x in rows}
    cues=[('23','24',.014),('38','51',.009),('59','65',.011),('67','72',.018)]
    for begin,end,amp in cues:
        a=byid[begin]['start'];b=byid[end]['start']+(byid[end]['duration'] if end=='72' else 0)
        beat=60/86;bar=beat*3
        chords=[(48,55,60),(45,52,57),(53,57,60),(43,50,55)]
        melody=[[76,79,81],[79,76,74],[72,76,77],[74,71,72]]
        t=a;idx=0
        while t+1<b:
            c=chords[idx%4];note(t,c[0],min(2.1,b-t),amp*.75)
            for j in (1,2):
                if t+j*beat+.8<b:
                    for pitch in c[1:]:note(t+j*beat,pitch,1.1,amp*.32)
            if idx%2==0 or end=='72':
                for j,pitch in enumerate(melody[idx%4]):
                    if t+j*beat+1<b:note(t+j*beat,pitch,1.35,amp*.65)
            t+=bar;idx+=1
        aa=round(a*sr);bb=round(b*sr);fade=min(sr,round((b-a)*sr/3))
        mix[aa:aa+fade]*=np.linspace(0,1,fade)[:,None];mix[bb-fade:bb]*=np.linspace(1,0,fade)[:,None]
    for delay,gain in [(.073,.15),(.127,.1),(.219,.055)]:
        offset=round(delay*sr);mix[offset:]+=mix[:-offset]*gain
    mix=mix[:round(length*sr)]
    active=np.mean(mix**2,axis=1)>1e-8
    if np.any(active):
        rms=float(np.sqrt(np.mean(mix[active]**2)))
        mix*=min(20,.028/max(.0001,rms))
    mix=np.clip(mix,-.35,.35)
    path=OUT/'声音/原创钢琴配乐.wav';path.parent.mkdir(parents=True,exist_ok=True)
    with wave.open(str(path),'wb') as f:f.setnchannels(2);f.setsampwidth(2);f.setframerate(sr);f.writeframes((mix*32767).astype('<i2').tobytes())
    write(OUT/'声音/配乐说明.json',{'original_procedural_composition':True,'tempo_bpm':86,'meter':'3/4','no_external_recording':True,'cues':cues,'draft_volume':.6})
    return path


def gather(rows):
    folder=OUT/'原始视频';folder.mkdir(parents=True,exist_ok=True);manifest=[]
    old={c['job_id']:c for c in read(PILOT/'五镜试片/state.json')['candidates'] if c.get('file')}
    for c in read(RUN/'state.json')['candidates']:
        if not c.get('file'):continue
        src=RUN/c['file'];dest=folder/f"{c['job_id']}_{c['id']}.mp4"
        if not dest.exists():shutil.copy2(src,dest)
        provenance=old.get(c['job_id'],{}) if c['source']=='imported' else c
        manifest.append({'shot':c['job_id'],'candidate':c['id'],'file':str(dest),'source':c['source'],
                         'task_id':provenance.get('task_id'),'usage':provenance.get('usage'),
                         'charged_in_this_run':c['source']=='seedance','selected':any(x.get('candidate')==c['id'] for x in rows)})
    write(OUT/'素材索引.json',manifest)
    with (OUT/'素材索引.csv').open('w',encoding='utf-8-sig',newline='') as f:
        w=csv.DictWriter(f,fieldnames=['shot','candidate','file','source','task_id','selected'],extrasaction='ignore');w.writeheader();w.writerows(manifest)


def mix_sound(rows,score):
    sr=48000;total=round(rows[-1]['end']*sr);mix=np.zeros((total,2),np.float32)
    for row in rows:
        p=OUT/'剪辑素材'/f"{row['id']}.wav"
        if not p.exists():continue
        with wave.open(str(p),'rb') as f:
            samples=np.frombuffer(f.readframes(f.getnframes()),dtype='<i2').reshape(-1,2).astype(np.float32)/32768
        start=round(row['start']*sr);n=min(len(samples),total-start);mix[start:start+n]+=samples[:n]
    with wave.open(str(score),'rb') as f:music=np.frombuffer(f.readframes(f.getnframes()),dtype='<i2').reshape(-1,2).astype(np.float32)/32768
    mix+=music[:total]*.6;peak=np.max(np.abs(mix));mix*=min(1,.95/max(.001,peak))
    path=OUT/'声音/全片混音.wav'
    with wave.open(str(path),'wb') as f:f.setnchannels(2);f.setsampwidth(2);f.setframerate(sr);f.writeframes((np.clip(mix,-1,1)*32767).astype('<i2').tobytes())
    return path


def make_draft(rows,subs,score):
    sys.path.insert(0,str(ROOT/'vendor'));import pyJianYingDraft as draft
    skill=Path.home()/'.codex/skills/jianying-editor'
    os.environ['JY_SKILL_ROOT']=str(skill);sys.path.insert(0,str(skill/'scripts'))
    from jy_wrapper import JyProject
    name='不用麻烦她_全片剪辑_'+time.strftime('%m%d_%H%M%S')
    project=JyProject(name,width=1920,height=1080,drafts_root=str(OUT/'剪映草稿'),overwrite=False)
    project._explicit_res=True
    project.script.fps=24
    for row in rows:
        p=OUT/'剪辑素材'/f"{row['id']}.mp4"
        seg=project.add_media_safe(str(p.resolve()),start_time=f"{row['start']}s",duration=f"{row['duration']}s",track_name='全片画面')
        if seg is None:raise RuntimeError('剪映导入失败：'+row['id'])
        seg.volume=0
        audio=OUT/'剪辑素材'/f"{row['id']}.wav"
        if audio.exists():
            a=project.add_media_safe(str(audio.resolve()),start_time=f"{row['start']}s",track_name='对白与现场声')
            if a is None:raise RuntimeError('剪映声音导入失败：'+row['id'])
    for x in subs:
        project.add_text_simple(x['text'],start_time=f"{x['start']}s",duration=f"{max(.25,x['end']-x['start'])}s",track_name='对白字幕',style=draft.TextStyle(size=5.2),clip_settings=draft.ClipSettings(transform_y=-.84))
    for sid,label in [('12','几天后'),('42','数周后'),('47','此后数月'),('55','几天后'),('66','两年后的春天')]:
        r=next(x for x in rows if x['id']==sid)
        project.add_text_simple(label,start_time=f"{r['start']+.15}s",duration=f"{min(2.35,r['duration']-.25)}s",track_name='时间提示',style=draft.TextStyle(size=4.5),clip_settings=draft.ClipSettings(transform_y=.8,transform_x=-.65))
    bgm=project.add_media_safe(str(score.resolve()),start_time='0s',track_name='原创配乐');bgm.volume=.6
    saved=project.save();folder=Path(saved['draft_path']);content=read(folder/'draft_info.json')
    content.update(id=str(uuid.uuid4()).upper(),name=name,fps=24)
    for m in content['materials'].get('videos',[])+content['materials'].get('audios',[]):
        m['local_material_id']=m.get('local_material_id') or str(uuid.uuid4()).upper()
    write(folder/'draft_info.json',content);write(folder/'draft_content.json',content)
    cover=folder/'draft_cover.jpg'
    ff(['-y','-ss','1','-i',str(OUT/'剪辑素材/01.mp4'),'-frames:v','1','-vf','scale=480:-1',str(cover)])
    now=int(time.time()*1e6);meta=read(folder/'draft_meta_info.json')
    meta.update(draft_name=name,draft_id=content['id'],draft_fold_path=str(folder),draft_root_path=str(folder.parent),
                draft_cover=str(cover),tm_draft_create=now,tm_draft_modified=now,tm_duration=round(rows[-1]['end']*1e6))
    write(folder/'draft_meta_info.json',meta)
    video_count=sum(len(t['segments']) for t in content['tracks'] if t['type']=='video')
    text_count=sum(len(t['segments']) for t in content['tracks'] if t['type']=='text')
    assert video_count==72 and text_count>=len(subs)
    for m in content['materials'].get('videos',[])+content['materials'].get('audios',[]):
        if m.get('path'):assert Path(m['path']).is_file() and Path(m['path']).is_relative_to(folder)
    write(OUT/'剪映草稿验证.json',{'saved':True,'path':str(folder),'video_segments':video_count,'text_segments':text_count,
                                  'bgm_audio_track':True,'self_contained':True,'native_ui_export_verified':False})
    return folder


def assemble():
    rows=select_rows();write(OUT/'剪辑时间线.json',rows)
    assert rows[-1]['end']<300,'成片超过五分钟'
    for row in rows:render_row(row)
    subs=save_subtitles(rows);score=original_score(rows);audio=mix_sound(rows,score);gather(rows)
    listing=OUT/'concat.txt';listing.write_text('\n'.join("file '"+(OUT/'剪辑素材'/f"{r['id']}.mp4").resolve().as_posix().replace("'","'\\''")+"'" for r in rows),'utf-8')
    cleanfilm=OUT/'不用麻烦她_1080p_无字幕.mp4'
    ff(['-y','-f','concat','-safe','0','-i',str(listing),'-i',str(audio),'-map','0:v','-map','1:a','-c:v','copy','-c:a','aac','-b:a','192k','-shortest','-movflags','+faststart',str(cleanfilm)])
    film=OUT/'不用麻烦她_1080p_字幕版.mp4'
    command(['ffmpeg','-hide_banner','-loglevel','error','-y','-i',str(cleanfilm),'-vf',"ass=filename='"+(OUT/'film.ass').as_posix().replace(':','\\:')+"'",'-c:v','libx264','-preset','fast','-threads','4','-crf','18','-c:a','copy','-movflags','+faststart',str(film)])
    folder=make_draft(rows,subs,score)
    ff(['-i',str(film),'-f','null','-'])
    probe=read_probe(film)
    write(OUT/'交付验证.json',{'full_decode_passed':True,'probe':probe,'timeline_seconds':rows[-1]['end'],
                              'shots':len(rows),'subtitle_chunks':len(subs),'draft':str(folder),
                              'enhanced_shots':[r['id'] for r in rows if enhanced_path(r).exists()],
                              'resolution_note':'480p生成素材经本地Real-ESRGAN超分与原片混合；复用720p样片常规放大；后期界面为原生1080p'})
    print(json.dumps({'film':str(film),'draft':str(folder),'duration':rows[-1]['end']},ensure_ascii=False),flush=True)


def read_probe(p):return json.loads(command(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(p)]))


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('action',choices=['prepare','render','assemble']);a=p.parse_args();OUT.mkdir(parents=True,exist_ok=True)
    if a.action=='assemble':assemble()
    else:
        rows=select_rows(partial=True);write(OUT/'剪辑时间线_制作中.json',rows)
        print(json.dumps({'available_shots':len(rows),'partial_seconds':rows[-1]['end'] if rows else 0},ensure_ascii=False),flush=True)
        if a.action=='render':
            for row in rows:render_row(row)
