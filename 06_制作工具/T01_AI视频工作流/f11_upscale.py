"""Optional local GPU super-resolution; no paid calls or media uploads."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import time
import shutil
import tempfile
import urllib.request
import zipfile
from f11_production import ROOT, RUN

TOOL = ROOT/'runtime/realesrgan'
URL='https://github.com/xinntao/Real-ESRGAN/releases/download/v0.2.5.0/realesrgan-ncnn-vulkan-20220424-windows.zip'


def install():
    TOOL.mkdir(parents=True,exist_ok=True)
    exe=TOOL/'realesrgan-ncnn-vulkan.exe'
    if exe.is_file(): return
    archive=TOOL/'official_windows.zip'
    if not archive.is_file():
        urllib.request.urlretrieve(URL+'?download=1',archive)
    with zipfile.ZipFile(archive) as z:
        for name in z.namelist():
            if not (TOOL/name).resolve().is_relative_to(TOOL.resolve()):
                raise ValueError('Unsafe archive path')
        z.extractall(TOOL)
    print(json.dumps({'installed':str(exe),'source':URL,'sha256':hashlib.sha256(archive.read_bytes()).hexdigest()},ensure_ascii=False),flush=True)


def trial():
    install()
    out=RUN/'检查/高清试验';out.mkdir(parents=True,exist_ok=True)
    state=json.loads((RUN/'state.json').read_text('utf-8'))
    c=next(x for x in state['candidates'] if x['job_id']=='01' and x.get('file'))
    source=out/'input.png'
    subprocess.run(['ffmpeg','-hide_banner','-loglevel','error','-ss','2','-i',str(RUN/c['file']),'-frames:v','1','-y',str(source)],check=True)
    shutil.copy2(source,TOOL/'trial_input.png')
    results=[]
    for model,scale in [('realesr-animevideov3',3),('realesrgan-x4plus',4)]:
        start=time.monotonic()
        dest=out/(model+'.png')
        localout=TOOL/(model+'.png')
        r=subprocess.run([str(TOOL/'realesrgan-ncnn-vulkan.exe'),'-i','trial_input.png','-o',localout.name,
                     '-m','models','-n',model,'-s',str(scale),'-t','128','-j','1:1:1'],cwd=TOOL,capture_output=True,text=True)
        if localout.exists():shutil.copy2(localout,dest)
        results.append({'model':model,'seconds':round(time.monotonic()-start,3),'returncode':r.returncode,'ok':r.returncode==0 and dest.exists(),'log':r.stderr[-1600:]})
        print(json.dumps(results[-1],ensure_ascii=False),flush=True)
    (out/'trial.json').write_text(json.dumps(results,ensure_ascii=False,indent=2),'utf-8')


def ascii_runtime():
    stage=Path(tempfile.gettempdir())/'codex_f11_sr'
    stage.mkdir(exist_ok=True)
    shutil.copy2(TOOL/'realesrgan-ncnn-vulkan.exe',stage/'realesrgan-ncnn-vulkan.exe')
    shutil.copytree(TOOL/'models',stage/'models',dirs_exist_ok=True)
    return stage


def batch_trial():
    stage=ascii_runtime()
    inp=stage/'trial_in';dest=stage/'trial_out'
    inp.mkdir(exist_ok=True);dest.mkdir(exist_ok=True)
    state=json.loads((RUN/'state.json').read_text('utf-8'))
    c=next(x for x in state['candidates'] if x['job_id']=='01' and x.get('file'))
    subprocess.run(['ffmpeg','-hide_banner','-loglevel','error','-i',str(RUN/c['file']),'-t','1','-vf','fps=24','-y',str(inp/'%08d.png')],check=True)
    start=time.monotonic()
    r=subprocess.run([str(stage/'realesrgan-ncnn-vulkan.exe'),'-i',inp.name,'-o',dest.name,'-n','realesr-animevideov3',
                      '-s','3','-t','0','-f','jpg','-j','2:2:2'],cwd=stage,capture_output=True,text=True)
    output=RUN/'检查/高清试验/一秒连续超分.mp4'
    if r.returncode==0:
        subprocess.run(['ffmpeg','-hide_banner','-loglevel','error','-framerate','24','-start_number','1','-i',str(dest/'%08d.jpg'),'-vf','scale=1920:1080:flags=lanczos','-c:v','libx264','-crf','18','-pix_fmt','yuv420p','-y',str(output)],check=True)
    report={'returncode':r.returncode,'seconds':round(time.monotonic()-start,3),'input_frames':len(list(inp.glob('*.png'))),
            'output_frames':len(list(dest.glob('*.jpg'))),'log_tail':r.stderr[-600:],'preview':str(output)}
    (RUN/'检查/高清试验/连续超分试验.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),'utf-8')
    print(json.dumps(report,ensure_ascii=False),flush=True)


def enhance_selected(watch=False):
    from f11_edit import select_rows, enhanced_path, read_probe, ff, quant
    stage=ascii_runtime()
    inp=stage/'film_in';dest=stage/'film_out'
    inp.mkdir(exist_ok=True);dest.mkdir(exist_ok=True)
    # All temporary frame deletion is restricted to these verified task folders.
    for folder in (inp,dest):
        if folder.resolve().parent!=stage.resolve():raise ValueError('Unsafe temp folder')
    reports=[]
    while True:
        rows=select_rows(partial=True)
        work=[]
        for row in rows:
            if row['kind']!='video' or enhanced_path(row).exists():continue
            info=read_probe(row['source']);v=next(x for x in info['streams'] if x['codec_type']=='video')
            if v['width']>=1000:continue
            work.append(row)
        for row in work:
            target=enhanced_path(row);target.parent.mkdir(parents=True,exist_ok=True)
            for folder,ext in [(inp,'png'),(dest,'jpg')]:
                for old in folder.glob('*.'+ext):
                    if old.stem.isdigit() and len(old.stem)==8:old.unlink()
            start=time.monotonic()
            ff(['-y','-ss',str(row['source_start']),'-i',row['source'],'-t',str(row['duration']),'-an','-vf','fps=24','-start_number','1',str(inp/'%08d.png')])
            r=subprocess.run([str(stage/'realesrgan-ncnn-vulkan.exe'),'-i',inp.name,'-o',dest.name,
                      '-n','realesr-animevideov3','-s','3','-t','0','-f','jpg','-j','2:2:2'],cwd=stage,capture_output=True,text=True)
            count=len(list(inp.glob('*.png')))
            if r.returncode or len(list(dest.glob('*.jpg')))!=count:
                raise RuntimeError('Local super-resolution failed on '+row['id']+': '+r.stderr[-200:])
            filt='[0:v]scale=1920:1080:flags=lanczos,setsar=1,hqdn3d=0.2:0.2:1.2:1.2[sr];[1:v]fps=24,scale=1920:1080:flags=lanczos,setsar=1[base];[sr][base]blend=all_expr=\'A*0.8+B*0.2\',eq=contrast=1.012:saturation=1.012'
            if row['id']=='01':filt+=',fade=t=in:st=0:d=0.28'
            if row['id']=='71':filt+=f",fade=t=out:st={row['duration']-.7:.4f}:d=0.7"
            filt+='[v]'
            ff(['-y','-framerate','24','-start_number','1','-i',str(dest/'%08d.jpg'),'-ss',str(row['source_start']),'-i',row['source'],
                '-filter_complex',filt,'-map','[v]','-an','-t',str(row['duration']),'-c:v','libx264','-preset','fast','-threads','4',
                '-crf','18','-pix_fmt','yuv420p','-r','24','-movflags','+faststart',str(target)])
            report={'shot':row['id'],'candidate':row['candidate'],'frames':count,'seconds':round(time.monotonic()-start,2),
                    'model':'realesr-animevideov3','scale':3,'blend_sr_fraction':.8,'file':str(target)}
            reports.append(report)
            target.with_suffix('.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),'utf-8')
            print(json.dumps(report,ensure_ascii=False),flush=True)
        if not watch or (RUN/'generation_finished.json').exists():break
        time.sleep(10)


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('action',choices=['install','trial','batch-trial','enhance']);p.add_argument('--watch',action='store_true');a=p.parse_args()
    if a.action=='enhance':enhance_selected(a.watch)
    elif a.action=='batch-trial':batch_trial()
    elif a.action=='trial':trial()
    else:install()
