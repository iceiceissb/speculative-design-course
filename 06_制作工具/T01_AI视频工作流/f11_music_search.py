"""Resolve a small shortlist from the installed Jianying Skill's music index."""
import csv
import json
from pathlib import Path
import sys
import urllib.request
from f11_revision import OUT,ROOT

SKILL=Path.home()/'.codex/skills/jianying-editor'
TARGETS=['7274154019756820538','7378223391197399051','7491911270162827274','7273832735306434618']

def get_json(url,body):
    req=urllib.request.Request(url,json.dumps(body).encode(),{'Content-Type':'application/json','User-Agent':'JianyingPro/5.9.0.11632 (Windows 10.0.19045; app_id:3704)','Accept':'application/json'})
    with urllib.request.urlopen(req,timeout=22) as res:return json.load(res)

def urls(data):
    if isinstance(data,dict):
        for k,v in data.items():
            if k in {'url','download_url','video_url'} and isinstance(v,str) and v.startswith('https://'):yield v
            elif k=='item_urls' and isinstance(v,list):yield from (x for x in v if isinstance(x,str) and x.startswith('https://'))
            else:yield from urls(v)
    elif isinstance(data,list):
        for x in data:yield from urls(x)

def main():
    records=list(csv.DictReader(l for l in (SKILL/'data/cloud_music_library.csv').read_text('utf-8-sig').splitlines() if not l.startswith('#')))
    src=(SKILL/'scripts/cloud_manager.py').read_text('utf-8')
    # Reuse the Skill's official material-resolution endpoint. No account tokens are read.
    import ast
    tree=ast.parse(src)
    endpoint=next(ast.literal_eval(n.value) for n in tree.body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='JY_MGET_ITEM_URL' for t in n.targets))
    out=OUT/'声音/配乐候选';out.mkdir(parents=True,exist_ok=True);report=[]
    for musicid in TARGETS:
        row=next(x for x in records if x['music_id']==musicid);entry={k:row[k] for k in ['music_id','title','duration_s']};entry['index']=str(SKILL/'data/cloud_music_library.csv');entry['attempts']=[]
        candidates=[row['url']] if row['url'] else []
        try:
            response=get_json(endpoint,{'items':[{'id':musicid,'effect_type':4,'source':3}]})
            candidates.extend(urls(response))
            entry['resolver_code']=response.get('ret',response.get('status_code'))
        except Exception as e:entry['resolver_error']=type(e).__name__+':'+str(e)[:100]
        for url in dict.fromkeys(candidates):
            try:
                req=urllib.request.Request(url,headers={'User-Agent':'JianyingPro/11.5.0'})
                with urllib.request.urlopen(req,timeout=25) as res:
                    if res.headers.get('Content-Type','').startswith(('text/','application/json')):raise ValueError('Non-audio response')
                    data=res.read(30*1024*1024)
                if len(data)<10000:raise ValueError('Audio response too short')
                dest=out/(musicid+'.m4a');dest.write_bytes(data);entry.update(file=str(dest),bytes=len(data),source_url=url);break
            except Exception as e:entry['attempts'].append(type(e).__name__+':'+str(e)[:110])
        report.append(entry);(OUT/'声音/剪映曲库检索.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),'utf-8')
        print(json.dumps({k:v for k,v in entry.items() if k not in ['source_url','index']},ensure_ascii=False),flush=True)

if __name__=='__main__':main()
