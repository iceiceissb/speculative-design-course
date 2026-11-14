"""Local QA artifacts for generated media; no paid calls."""
import argparse
import json
from pathlib import Path
import subprocess
import sys
from PIL import Image, ImageDraw, ImageFont, ImageOps
from f11_production import RUN, SOURCE


def sheets():
    state = json.loads((RUN/'state.json').read_text('utf-8'))
    out = RUN/'检查'
    out.mkdir(exist_ok=True)
    font = ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',17)
    rows=[]
    for c in state['candidates']:
        if not c.get('file'):
            continue
        video=RUN/c['file']
        contact=out/(c['job_id']+'_'+c['id']+'.jpg')
        if not contact.exists():
            dur=c['media']['duration']
            canvas=Image.new('RGB',(1500,310),(241,237,228))
            d=ImageDraw.Draw(canvas)
            d.text((12,8),c['job_id']+' · '+c['id']+' · '+str(round(dur,2))+'s',font=font,fill='#223d32')
            for i,t in enumerate([.15,dur*.25,dur*.5,dur*.75,max(.1,dur-.15)]):
                p=out/(c['id']+'_'+str(i)+'.jpg')
                subprocess.run(['ffmpeg','-hide_banner','-loglevel','error','-ss',str(t),'-i',str(video),'-frames:v','1','-vf','scale=300:-1','-y',str(p)],check=True)
                im=Image.open(p).convert('RGB');canvas.paste(im,(i*300,40))
                d.text((i*300+8,222),f'{t:.2f}s',font=font,fill='#223d32')
            canvas.save(contact,quality=88)
        rows.append((c,contact))
    for n in range(0,len(rows),6):
        page=Image.new('RGB',(1500,310*len(rows[n:n+6])),(241,237,228))
        for i,(_,p) in enumerate(rows[n:n+6]):
            page.paste(Image.open(p),(0,i*310))
        page.save(out/f'动作总览_{n//6+1:02}.jpg',quality=90)
    print(json.dumps({'available_clips':len(rows),'pages':(len(rows)+5)//6},ensure_ascii=False),flush=True)


def transcribe(watch=False):
    import os
    import time
    packages=Path(__file__).parent/'runtime/edit_packages'
    sys.path.insert(0,str(packages))
    os.environ['HF_HOME']=str(Path(__file__).parent/'runtime/huggingface')
    os.environ['HF_HUB_DISABLE_XET']='1'
    from faster_whisper import WhisperModel
    print('Loading local CPU speech recognition model (no video uploads).',flush=True)
    model=WhisperModel('small',device='cpu',compute_type='int8',cpu_threads=6,
                       download_root=str(Path(__file__).parent/'runtime/whisper_models'))
    out=RUN/'检查/台词识别'
    out.mkdir(parents=True,exist_ok=True)
    print('Speech model ready.',flush=True)
    while True:
        jobs={j['id']:j for j in json.loads((RUN/'project.json').read_text('utf-8'))['jobs']}
        candidates=json.loads((RUN/'state.json').read_text('utf-8'))['candidates']
        for c in candidates:
            j=jobs[c['job_id']]
            path=out/(c['job_id']+'_'+c['id']+'.json')
            if not j['dialogue'] or not c.get('file') or path.exists():
                continue
            import numpy as np
            raw=subprocess.run(['ffmpeg','-hide_banner','-loglevel','error','-i',str(RUN/c['file']),
                                '-vn','-ac','1','-ar','16000','-f','f32le','pipe:1'],check=True,capture_output=True).stdout
            audio=np.frombuffer(raw,dtype=np.float32).copy()
            segments,info=model.transcribe(audio,language='zh',beam_size=5,
                         word_timestamps=True,vad_filter=False,
                         initial_prompt='邱，徐，秀秀，智能轮椅，青禾布店。',condition_on_previous_text=False)
            result={'shot':c['job_id'],'candidate':c['id'],'expected':j['dialogue'],
                    'language':info.language,'segments':[]}
            for s in segments:
                result['segments'].append({'start':s.start,'end':s.end,'text':s.text,
                     'avg_logprob':s.avg_logprob,'words':[{'start':w.start,'end':w.end,'word':w.word,'probability':w.probability} for w in (s.words or [])]})
            path.write_text(json.dumps(result,ensure_ascii=False,indent=2),'utf-8')
            print(json.dumps({'shot':c['job_id'],'recognized':' '.join(x['text'] for x in result['segments'])},ensure_ascii=False),flush=True)
        if not watch or (RUN/'generation_finished.json').exists():
            break
        time.sleep(10)


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('action',choices=['sheets','speech']);p.add_argument('--watch',action='store_true');a=p.parse_args()
    sheets() if a.action=='sheets' else transcribe(a.watch)
