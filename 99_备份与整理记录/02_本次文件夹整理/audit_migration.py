from pathlib import Path
import hashlib, json, re
from urllib.parse import urlparse, unquote
from html.parser import HTMLParser

ROOT=Path(__file__).resolve().parents[2]
HERE=Path(__file__).resolve().parent
OLD=ROOT/'99_备份与整理记录/01_首次整理记录'
MOVES=json.loads((HERE/'迁移计划.json').read_text(encoding='utf-8'))['moves']
def mapped(s):
    for m in MOVES:
        if s==m['source'] or s.startswith(m['source']+'/'):
            s=m['destination']+s[len(m['source']):]
    return s
def sha(p):
    h=hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda:f.read(8*1024*1024),b''):h.update(b)
    return h.hexdigest()

originals=json.loads((OLD/'原始文件清单_SHA256.json').read_text(encoding='utf-8'))
repair=json.loads((HERE/'路径修复记录.json').read_text(encoding='utf-8'))
expected={p.replace('\\','/') for p in repair['active_tool_files_rebased']}|{'AGENTS.md'}
missing=[];unexpected=[];changed=[]
for i,r in enumerate(originals):
    new=mapped(r['path']);p=ROOT/new
    if not p.is_file():missing.append(new);continue
    if sha(p)!=r['sha256']:
        changed.append(new)
        if new not in expected:unexpected.append(new)
    if i%400==0:print('Original files checked',i+1,flush=True)

copies=json.loads((OLD/'归档副本清单_SHA256.json').read_text(encoding='utf-8'))
bad_scripts=[];bad_demo=[];bad_images=[];script_count=0;demo_count=0;image_count=0
for r in copies:
    target=mapped(r['target']);p=ROOT/target
    kind=None
    if target.startswith('01_剧本版本/') and p.suffix=='.md':kind='script';script_count+=1
    elif target.startswith('02_Demo版本/'):kind='demo';demo_count+=1
    elif '/F07_' in target and '/frames/' in target:kind='image';image_count+=1
    if not kind:continue
    if not p.exists() or sha(p)!=r['sha256']:
        {'script':bad_scripts,'demo':bad_demo,'image':bad_images}[kind].append(target)

previous=json.loads((OLD/'整理核对结果.json').read_text(encoding='utf-8'))
backup=ROOT/'99_备份与整理记录/00_整理前备份/2026-10-17_整理前工作文件.zip'
print('Checking pre-existing backup SHA256...',flush=True)
backup_ok=sha(backup)==previous['snapshot_sha256']

cat=json.loads((HERE/'版本总表_新路径.json').read_text(encoding='utf-8'))
target_missing=[v['target'] for v in cat if not (ROOT/v['target']).exists()]
class Parser(HTMLParser):
    def __init__(self):super().__init__();self.urls=[]
    def handle_starttag(self,t,attrs):
        for k,v in attrs:
            if k in {'src','href','poster'} and v:self.urls.append(v)
link_missing=[];link_checked=0
def check_link(source,url):
    global link_checked
    u=urlparse(url)
    if u.scheme or u.netloc or not u.path:return
    link_checked+=1
    if not (source.parent/unquote(u.path)).exists():link_missing.append({'file':str(source.relative_to(ROOT)),'target':url})
for v in cat:
    if v['category']!='Demo' and v['id']!='F07':continue
    p=ROOT/v['target'];parser=Parser();parser.feed(p.read_text(encoding='utf-8'))
    for u in parser.urls:check_link(p,u)
for p in list(ROOT.glob('00_目录说明.md'))+list((ROOT/'01_剧本版本').rglob('版本说明.md'))+list((ROOT/'02_Demo版本').rglob('版本说明.md'))+list((ROOT/'03_分镜与角色').rglob('版本说明.md'))+list((ROOT/'07_面试准备').glob('*.md')):
    for m in re.finditer(r'\[[^\]]*\]\((?:<([^>]+)>|([^\s)]+))\)',p.read_text(encoding='utf-8')):check_link(p,m.group(1) or m.group(2))

# Check relocated media paths in the editable workflow exports.
tool=ROOT/'06_制作工具/T01_AI视频工作流'
media_missing=[];media_checked=0
def walk_values(d):
    if isinstance(d,dict):
        for k,v in d.items():
            if k in {'path','draft_cover','draft_fold_path','draft_root_path'} and isinstance(v,str):yield v
            yield from walk_values(v)
    elif isinstance(d,list):
        for v in d:yield from walk_values(v)
for p in (tool/'exports').rglob('*.json'):
    if p.name not in {'draft_info.json','draft_content.json','draft_meta_info.json'}:continue
    for value in walk_values(json.loads(p.read_text(encoding='utf-8-sig'))):
        if value.replace('\\','/').startswith(str(tool).replace('\\','/')):
            media_checked+=1
            if not Path(value).exists():media_missing.append({'file':str(p.relative_to(ROOT)),'path':value})

result=dict(original_files_checked=len(originals),missing_originals=missing,
            changed_original_files=changed,unexpected_original_changes=unexpected,
            expected_path_repairs=len(changed),backup_sha256_unchanged=backup_ok,
            literary_script_copies_checked=script_count,literary_script_copies_changed=bad_scripts,
            demo_files_checked=demo_count,demo_files_changed=bad_demo,
            latest_storyboard_images_checked=image_count,latest_storyboard_images_changed=bad_images,
            catalog_targets_missing=target_missing,local_links_checked=link_checked,local_links_missing=link_missing,
            relocated_draft_paths_checked=media_checked,relocated_draft_paths_missing=media_missing,
            root_entries=sorted(p.name for p in ROOT.iterdir()))
(HERE/'文件夹迁移核对.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({k:v for k,v in result.items() if k not in {'changed_original_files','root_entries'}},ensure_ascii=False),flush=True)
assert not any([missing,unexpected,bad_scripts,bad_demo,bad_images,target_missing,link_missing,media_missing]) and backup_ok
