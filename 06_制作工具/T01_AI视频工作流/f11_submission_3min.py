"""180-second course submission cut, using only accepted V02 local materials."""
from pathlib import Path
import json,shutil,sys,uuid,time,wave,math,subprocess
import numpy as np
import f11_edit as base
from f11_revision import OLD_OUT,OUT as V02,ROOT

OUT=ROOT.parents[1]/'05_汇报与成片/V03_三分钟提交版_2026-10-22'
SUBMIT=ROOT.parents[1]/'05_汇报与成片/04_最终提交作业'
FPS=24;SR=48000
PLAN={'01':1.5,'02':2.6,'03':2.6,'04':3.583333,'08':1.3,'09':7.5,'12':1.1,'13':1.5,'14':2.6,'15':3.8,'16':3.8,'17':1.4,'18':2.5,'19':2.667,'20':4.5,'21':2,'22':1.8333,'23':2,'24':1.792,'25':2.8,'26':4.458,'27':4.458,'28':4.5,'29':8.0833,'30':3.6,'31':8.0833,'32':2.1,'35':1.6,'37':2.4,'38':1.3,'39':4.916667,'40':1.5,'41':2.5,'42':5.375,'43':1.5,'45':1.5,'47':1.3,'48':1.3,'49':1.7,'50':1.5,'51':1.5,'52':5.4167,'53':5.666667,'54':1.8,'55':1,'56':3.2,'57':2.8,'58':2.1,'59':1.5,'60':1.5,'61':3.5,'62':1.5,'64':1.5,'65':4,'66':3.3,'67':1.4,'69':2.708,'70':6.916667,'71':6.708333,'72':5}

def read(p):return json.loads(Path(p).read_text('utf-8-sig'))
def write(p,x):Path(p).parent.mkdir(parents=True,exist_ok=True);Path(p).write_text(json.dumps(x,ensure_ascii=False,indent=2),'utf-8')
def audio_read(p):
    with wave.open(str(p),'rb') as f:
        assert f.getframerate()==SR and f.getnchannels()==2 and f.getsampwidth()==2
        return np.frombuffer(f.readframes(f.getnframes()),dtype='<i2').reshape(-1,2).astype(np.float32)/32768
def audio_write(p,a):
    Path(p).parent.mkdir(parents=True,exist_ok=True)
    with wave.open(str(p),'wb') as f:f.setframerate(SR);f.setnchannels(2);f.setsampwidth(2);f.writeframes((np.clip(a,-1,1)*32767).astype('<i2').tobytes())
    return p

def plan():
    OUT.mkdir(parents=True,exist_ok=True)
    old=read(V02/'剪辑时间线.json');rows=[]
    for r in old:
        if r['id'] not in PLAN:continue
        r=dict(r);r['v02_start']=r['start'];r['local_source_start']=0
        frames=min(round(PLAN[r['id']]*FPS),round(r['duration']*FPS))
        r.update(duration=frames/FPS,frames=frames,edited_source=str(V02/'剪辑素材'/f"{r['id']}.mp4"))
        rows.append(r)
    delta=4320-sum(r['frames'] for r in rows)
    # The corrected route map is a readable still and may hold a few more/fewer frames.
    r=next(r for r in rows if r['id']=='30');r['frames']+=delta;r['duration']=r['frames']/FPS
    assert r['duration']>=3 and sum(r['frames'] for r in rows)==4320
    cursor=0
    for r in rows:r['start']=cursor/FPS;cursor+=r['frames'];r['end']=cursor/FPS
    for r in rows:
        if r['dialogue'] and r['id']!='24':
            assert max(s['end']-r['source_start'] for s in r['speech'])<=r['duration']+.02,(r['id'],'对白被截断')
    write(OUT/'剪辑时间线.json',rows)
    write(OUT/'三分钟剪辑说明.json',{'duration':180,'frames':4320,'fps':24,'kept_shots':len(rows),'removed_shots':[r['id'] for r in old if r['id'] not in PLAN],
        'method':'保留已确认镜头，删减支线和重复街景；对白正常速度，无新付费生成','original_V02_preserved':True})
    print({'shots':len(rows),'frames':cursor,'duration':cursor/FPS,'route_map_hold':next(r['duration'] for r in rows if r['id']=='30')},flush=True)
    return rows

def render(rows):
    folder=OUT/'剪辑素材';folder.mkdir(exist_ok=True)
    for r in rows:
        sid=r['id'];p=folder/f'{sid}.mp4'
        if not p.exists():
            base.ff(['-y','-i',r['edited_source'],'-frames:v',str(r['frames']),'-an','-vf','setsar=1','-c:v','libx264','-preset','fast','-threads','4','-crf','18','-pix_fmt','yuv420p','-r','24',str(p)])
        a=V02/'剪辑素材'/f'{sid}.wav'
        if a.exists():
            data=audio_read(a)
            n=round(r['duration']*SR)
            if sid in {'24','34'}:n=max(n,len(data))
            data=data[:n].copy()
            fade=min(round(.04*SR),len(data))
            if fade:data[-fade:]*=np.linspace(1,0,fade)[:,None]
            audio_write(folder/f'{sid}.wav',data)
    print('Video cuts prepared.',flush=True)

def mix(rows,subs):
    n=180*SR;native=np.zeros((n,2),np.float32);amb=np.zeros_like(native)
    old_amb=audio_read(V02/'声音/连续环境声.wav')
    for r in rows:
        a=round(r['start']*SR);b=round(r['end']*SR)
        p=OUT/'剪辑素材'/f"{r['id']}.wav"
        if p.exists():
            x=audio_read(p);m=min(len(x),n-a);native[a:a+m]+=x[:m]
        start=round(r['v02_start']*SR);x=old_amb[start:start+(b-a)].copy()
        if len(x)<b-a:x=np.pad(x,((0,b-a-len(x)),(0,0)))
        amb[a:b]=x
    # Renew continuous music rather than cutting the old music at every picture cut.
    music=np.zeros_like(native);one=audio_read(V02/'声音/配乐候选/7274154019756820538_48k.wav');two=audio_read(V02/'声音/配乐候选/7378223391197399051_48k.wav')
    change=next(r['start'] for r in rows if r['id']=='47');cross=3
    c=round((change+cross/2)*SR);x=one[:c].copy()
    x[:2*SR]*=np.linspace(0,1,2*SR)[:,None];x[-cross*SR:]*=np.linspace(1,0,cross*SR)[:,None];music[:c]+=x
    a=round((change-cross/2)*SR);length=n-a;x=two[-length:].copy();x[:cross*SR]*=np.linspace(0,1,cross*SR)[:,None];x[-4*SR:]*=np.linspace(1,0,4*SR)[:,None];music[a:]+=x
    gain=np.ones(n,np.float32)
    for s in subs:
        a=max(0,round((s['start']-.15)*SR));b=min(n,round((s['end']+.2)*SR));gain[a:b]=np.minimum(gain[a:b],.32)
        lo=max(0,a-round(.25*SR));hi=min(n,b+round(.4*SR))
        gain[lo:a]=np.minimum(gain[lo:a],np.linspace(1,.32,a-lo));gain[b:hi]=np.minimum(gain[b:hi],np.linspace(.32,1,hi-b))
    music*=gain[:,None];mix=native+music+amb;master_gain=min(1,.965/max(.001,float(np.max(np.abs(mix)))))
    audio_write(OUT/'声音/全片混音.wav',mix*master_gain)
    audio_write(OUT/'声音/连续配乐.wav',music/.6);audio_write(OUT/'声音/连续环境声.wav',amb)
    write(OUT/'声音/混音记录.json',{'music_ids':['7274154019756820538','7378223391197399051'],'master_gain':master_gain,'music_ducking_db':-9.9,'continuous_music':True})
    return master_gain

def draft(rows,subs,gain):
    sys.path.insert(0,str(ROOT/'vendor'));import pyJianYingDraft as d
    import os
    skill=Path.home()/'.codex/skills/jianying-editor';os.environ['JY_SKILL_ROOT']=str(skill);sys.path.insert(0,str(skill/'scripts'))
    from jy_wrapper import JyProject
    name='不用麻烦她_三分钟提交版_1022_'+time.strftime('%H%M%S');p=JyProject(name,width=1920,height=1080,drafts_root=str(OUT/'剪映草稿'),overwrite=False)
    p._explicit_res=True;p.script.fps=24
    for r in rows:
        a=round(r['start']*1e6);dur=round(r['end']*1e6)-a
        seg=p.add_media_safe(str(OUT/'剪辑素材'/f"{r['id']}.mp4"),start_time=a,duration=dur,track_name='三分钟画面');assert seg is not None;seg.volume=0
        ap=OUT/'剪辑素材'/f"{r['id']}.wav"
        if ap.exists():
            seg=p.add_media_safe(str(ap),start_time=a,track_name='对白与现场声');assert seg is not None;seg.volume=gain
    for s in subs:p.add_text_simple(s['text'],start_time=f"{s['start']}s",duration=f"{s['end']-s['start']}s",track_name='对白字幕',style=d.TextStyle(size=5.2),clip_settings=d.ClipSettings(transform_y=-.84))
    for sid,label in [('12','几天后'),('42','数周后'),('47','此后数月'),('55','几天后'),('66','两年后的春天')]:
        r=next(x for x in rows if x['id']==sid);p.add_text_simple(label,start_time=round((r['start']+.1)*1e6),duration=round(min(2.3,r['duration']-.15)*1e6),track_name='时间提示',style=d.TextStyle(size=4.5),clip_settings=d.ClipSettings(transform_y=.8,transform_x=-.65))
    s=p.add_media_safe(str(OUT/'声音/连续配乐.wav'),start_time=0,track_name='连续配乐');s.volume=.6*gain
    s=p.add_media_safe(str(OUT/'声音/连续环境声.wav'),start_time=0,track_name='连续环境声');s.volume=gain
    saved=p.save();folder=Path(saved['draft_path']);content=read(folder/'draft_info.json');content.update(id=str(uuid.uuid4()).upper(),name=name,fps=24)
    write(folder/'draft_info.json',content);write(folder/'draft_content.json',content)
    cover=folder/'draft_cover.jpg';base.ff(['-y','-ss','2','-i',str(OUT/'剪辑素材/71.mp4'),'-frames:v','1','-vf','scale=480:-1',str(cover)])
    meta=read(folder/'draft_meta_info.json');now=int(time.time()*1e6);meta.update(draft_name=name,draft_id=content['id'],draft_fold_path=str(folder),draft_root_path=str(folder.parent),draft_cover=str(cover),tm_duration=180000000,tm_draft_create=now,tm_draft_modified=now);write(folder/'draft_meta_info.json',meta)
    write(OUT/'剪映草稿验证.json',{'saved':True,'path':str(folder),'native_ui_export_verified':False,'duration_seconds':180,'video_segments':len(rows)})

def main():
    rows=plan();base.OUT=OUT;render(rows);subs=base.save_subtitles(rows);gain=mix(rows,subs)
    listing=OUT/'concat.txt';listing.write_text('\n'.join("file '"+(OUT/'剪辑素材'/f"{r['id']}.mp4").as_posix()+"'" for r in rows),'utf-8')
    master=OUT/'无字幕母版.mp4';film=OUT/'不用麻烦她_3分钟提交版.mp4'
    base.ff(['-y','-f','concat','-safe','0','-i',str(listing),'-i',str(OUT/'声音/全片混音.wav'),'-map','0:v','-map','1:a','-t','180','-c:v','copy','-c:a','aac','-b:a','192k','-movflags','+faststart',str(master)])
    base.ff(['-y','-i',str(master),'-vf',"ass=filename='"+(OUT/'film.ass').as_posix().replace(':','\\:')+"'",'-frames:v','4320','-t','180','-c:v','libx264','-preset','fast','-threads','6','-crf','18','-c:a','copy','-movflags','+faststart',str(film)])
    draft(rows,subs,gain);base.ff(['-i',str(film),'-f','null','-'])
    probe=base.read_probe(film);v=next(x for x in probe['streams'] if x['codec_type']=='video')
    assert int(v['nb_frames'])==4320 and abs(float(probe['format']['duration'])-180)<.05
    assert all(0<=x['start']<x['end']<=180 for x in subs)
    write(OUT/'交付验证.json',{'full_decode_passed':True,'duration':180,'frames':4320,'resolution':[1920,1080],'caption_chunks':len(subs),'zero_new_paid_generation':True,'probe':probe})
    shutil.copy2(film,SUBMIT/film.name)
    print(json.dumps({'film':str(film),'submitted':str(SUBMIT/film.name),'duration':180},ensure_ascii=False),flush=True)

if __name__=='__main__':
    raise SystemExit('该三分钟方案已按用户要求停用；最终提交继续采用V02的4分37秒影片。')
