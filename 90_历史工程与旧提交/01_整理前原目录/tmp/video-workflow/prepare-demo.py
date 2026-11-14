from pathlib import Path
import json, sys
ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'output/AI视频工作流'
sys.path.insert(0,str(OUT))
from workflow import Workflow, run_tool, write_json, probe
a=json.loads((ROOT/'tmp/video-workflow/contact/index.json').read_text(encoding='utf-8'))
demo=ROOT/'tmp/video-workflow/demo';demo.mkdir(exist_ok=True)
for index,duration,name in [(31,5,'before'),(12,5,'after')]:
    run_tool(['ffmpeg','-hide_banner','-loglevel','error','-i',a[index]['path'],'-vf',
              'scale=1280:720,setsar=1,tpad=stop_mode=clone:stop_duration=1',
              '-af','apad','-t',str(duration),'-r','24','-c:v','libx264','-crf','19',
              '-pix_fmt','yuv420p','-c:a','aac','-ar','48000','-ac','2','-y',str(demo/(name+'.mp4'))])
(demo/'concat.txt').write_text("file 'before.mp4'\nfile 'after.mp4'\n",encoding='ascii')
merged=demo/'E_已有即梦素材_本地拼接演示.mp4'
run_tool(['ffmpeg','-hide_banner','-loglevel','error','-f','concat','-safe','0','-i',str(demo/'concat.txt'),
          '-c','copy','-movflags','+faststart','-y',str(merged)])
w=Workflow(OUT);results=[]
for job,file in [('E',merged),('22',Path(a[11]['path'])),('35',Path(a[26]['path'])),('24',Path(a[12]['path']))]:
    c=w.import_video(job,file);w.select(job,c['id']);results.append({'job':job,'file':str(file),'candidate_id':c['id']})
w.update_timing('22',.6,3);w.update_timing('24',.6,3)
write_json(OUT/'reports/演示素材来源.json',{'purpose':'已有素材验证，非本次API生成，示例选择可更换',
 'E_assembly':{'first_5_seconds':a[31]['path'],'last_5_seconds':a[12]['path'],
                'note':'后半段原片约4.096秒，末尾约0.9秒停帧补至5秒，仅用于测试10秒首尾片段交接'},
 'imports':results})
print(json.dumps({'imported':len(results),'selection':w.state()['selection'],'E_media':probe(merged)},ensure_ascii=False))
print(json.dumps(w.assemble('both'),ensure_ascii=False,indent=2))
