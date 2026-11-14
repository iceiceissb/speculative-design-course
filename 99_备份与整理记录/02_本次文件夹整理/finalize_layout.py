"""Repair generated navigation metadata and active tool paths after physical moves.
Historical scripts, Demo runtime code, images and original backup ZIP stay intact.
"""
from pathlib import Path
import json, os, re, csv, hashlib
from urllib.parse import unquote, urlparse

ROOT=Path(__file__).resolve().parents[2]
HERE=Path(__file__).resolve().parent
OLD_RECORD=ROOT/'99_备份与整理记录/01_首次整理记录'
PLAN=json.loads((HERE/'迁移计划.json').read_text(encoding='utf-8'))
MOVES=PLAN['moves']

def mapped(value):
    value=value.replace('\\','/')
    for m in MOVES:
        source=m['source'];dest=m['destination']
        if value==source or value.startswith(source+'/'):
            value=dest+value[len(source):]
    return value

def link(label,target,base):
    return f'[{label}](<{os.path.relpath(target,base).replace(chr(92),"/")}>)'

def save(p,text):
    p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(text.rstrip()+'\n',encoding='utf-8')

def hashfile(p):
    h=hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda:f.read(8*1024*1024),b''):h.update(b)
    return h.hexdigest()

# The previous audit is a historical record. Write a new table for the new paths.
catalog=json.loads((OLD_RECORD/'版本总表.json').read_text(encoding='utf-8'))
for v in catalog:
    for key in ['source','target']:
        v[key+'_before_move']=v[key]
        v[key]=mapped(v[key])
    if 'aliases' in v:v['aliases']=[mapped(p) for p in v['aliases']]
    if v['id']=='T01':
        v['target']='06_制作工具/T01_AI视频工作流/README_先看这里.md'
        v['note']='实际运行项目，含现有候选、时间线、导入与剪辑工具；归档快照另存历史目录。'
    elif v['id']=='T02':
        v['target']='06_制作工具/T02_Bodystorming_Agent/README.md'
        v['note']='独立 Bodystorming 研究原型的实际运行项目，含源码、dist、数据和启动入口。'
(HERE/'版本总表_新路径.json').write_text(json.dumps(catalog,ensure_ascii=False,indent=2),encoding='utf-8')
with (HERE/'版本总表_新路径.csv').open('w',encoding='utf-8-sig',newline='') as f:
    fields=['id','category','title','note','source','target','source_before_move','target_before_move']
    w=csv.DictWriter(f,fieldnames=fields,extrasaction='ignore');w.writeheader();w.writerows(catalog)

# Repair only generated explanatory files, using their original locations.
tracked=json.loads((HERE/'移动前说明文件.json').read_text(encoding='utf-8'))
repaired=[]
pattern=re.compile(r'\[([^\]]*)\]\((?:<([^>]+)>|([^\s)]+))\)')
for item in tracked:
    original=ROOT/item['path'];target=ROOT/mapped(item['path'])
    def replace_match(m):
        url=m.group(2) or m.group(3)
        u=urlparse(url)
        if u.scheme or u.netloc or not u.path:return m.group(0)
        old_dest=(original.parent/unquote(u.path)).resolve()
        try:r=old_dest.relative_to(ROOT).as_posix()
        except ValueError:return m.group(0)
        new_dest=ROOT/mapped(r)
        out=os.path.relpath(new_dest,target.parent).replace('\\','/')
        if u.fragment:out+='#'+u.fragment
        return f'[{m.group(1)}](<{out}>)'
    updated=pattern.sub(replace_match,item['text'])
    # Correct operational wording in generated version descriptions.
    if target.name=='版本说明.md' and '02_工具归档快照' in target.parts:
        updated+='\n\n2026-10-17：这是上次归档留下的工具快照。实际运行项目已移入 `06_制作工具`。\n'
    if updated!=item['text']:save(target,updated);repaired.append(str(target.relative_to(ROOT)))

# Active storyboard references now resolve inside its own portable package.
f07=next(v for v in catalog if v['id']=='F07')
fhome=(ROOT/f07['target']).parent
jsonpath=fhome/'storyboard.json';buildpath=fhome/'build_package.py'
back=HERE/'路径修复前文件'
back.mkdir(exist_ok=True)
for p in [jsonpath,buildpath]:
    q=back/('F07_'+p.name)
    if not q.exists():q.write_bytes(p.read_bytes())
data=json.loads(jsonpath.read_text(encoding='utf-8'))
before_prompts={s['id']:s.get('video_prompt') for s in data['shots']}
data['references']=['references/'+Path(p.replace('\\','/')).name for p in data['references']]
for p in data['references']:assert (fhome/p).exists(),p
jsonpath.write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')
text=buildpath.read_text(encoding='utf-8')
old="    path = Path(source)\n    shutil.copy2(path, ref_dir / path.name)"
new="    path = Path(source)\n    if not path.is_absolute():\n        path = ROOT / path\n    destination = ref_dir / path.name\n    if path.resolve() != destination.resolve():\n        shutil.copy2(path, destination)"
assert old in text,'Unexpected storyboard builder baseline'
buildpath.write_text(text.replace(old,new),encoding='utf-8')
assert before_prompts=={s['id']:s.get('video_prompt') for s in json.loads(jsonpath.read_text(encoding='utf-8'))['shots']}

# Replace embedded absolute workspace paths only in active production tool files.
# External installed Jianying drafts are self-contained and are not modified.
tool=ROOT/'06_制作工具/T01_AI视频工作流'
oldtool='output/AI视频工作流';newtool='06_制作工具/T01_AI视频工作流'
replacements=[]
for m in sorted(MOVES,key=lambda m:len(m['source']),reverse=True):
    old_abs=str(ROOT/m['source']);new_abs=str(ROOT/m['destination'])
    replacements.extend([(old_abs.replace('\\','/'),new_abs.replace('\\','/')),
                         (old_abs.replace('\\','\\\\'),new_abs.replace('\\','\\\\')),
                         (old_abs,new_abs)])
tool_fixed=[]
skip={'.venv-jianying','__pycache__','node_modules'}
for p in tool.rglob('*'):
    if not p.is_file() or any(s in skip for s in p.relative_to(tool).parts):continue
    if p.suffix.lower() not in {'.json','.txt','.md','.py','.js','.ps1','.cmd','.bat','.srt','.vtt'}:continue
    if p.name.startswith('.env'):continue
    try:text=p.read_text(encoding='utf-8-sig')
    except UnicodeDecodeError:continue
    updated=text
    for old,new in replacements:updated=updated.replace(old,new)
    if p.name=='finecut_slope.py':
        updated=updated.replace("ROOT.parents[1] / 'tmp/video-workflow/contact/index.json'", "ROOT.parents[1] / '90_历史工程与旧提交/01_整理前原目录/tmp/video-workflow/contact/index.json'")
    if p==tool/'skill/ai-video-workflow/SKILL.md':
        updated=updated.replace('output/AI视频工作流','06_制作工具/T01_AI视频工作流')
    if updated!=text:
        b=back/'AI视频工作流'/p.relative_to(tool);b.parent.mkdir(parents=True,exist_ok=True);b.write_bytes(p.read_bytes())
        p.write_text(updated,encoding='utf-8');tool_fixed.append(str(p.relative_to(ROOT)))

# Root project guidance overrides a global Skill's historical project path.
agents=ROOT/'AGENTS.md';atext=agents.read_text(encoding='utf-8')
save(back/'AGENTS.md',atext)
atext+='''

## 工作区文件位置（2026-10-17 更新）

- 工作区已按 00—07、90、99 号文件夹实际整理；根目录的 `00_目录说明.md` 是目录说明。
- 当前讨论在 `00_当前创作`，剧本在 `01_剧本版本`，Demo 在 `02_Demo版本`，分镜在 `03_分镜与角色`。
- 本地 AI 视频工作流的实际路径是 `06_制作工具/T01_AI视频工作流`。如果已安装 Skill 仍写 `output/AI视频工作流`，以这里的新路径运行同名文件，不另建旧目录。
- Bodystorming 研究原型位于 `06_制作工具/T02_Bodystorming_Agent`。
- 旧 `output`、`作业二`、`scripts`、`tmp` 已移入 `90_历史工程与旧提交/01_整理前原目录`，作为历史来源保留。
- 整理前 ZIP 在 `99_备份与整理记录/00_整理前备份`；本次实际移动的路径对照在 `99_备份与整理记录/02_本次文件夹整理/迁移计划.json`。
- 修改当前作品时使用上述正式目录，不在历史来源或旧网页目录中继续制作。
'''
save(agents,atext)

folders={
 '00_当前创作':'保存人物共识、待定问题与新一轮讨论；新故事还未定稿。',
 '01_剧本版本':'32 份编号剧本／叙事稿，按早期轮椅、医院与让行、城市礼仪、两位老友四个阶段分文件夹；原文内容保留。',
 '02_Demo版本':'7 个不同运行代码的 Demo，按 D01—D07 排列。每个文件夹的 原型/index.html 是体验入口，运行依赖随包保留。',
 '03_分镜与角色':'分镜 F01—F10、人物与轮椅造型 V01—V03，以及早期散图。F07 是现有 v6 最新 36 镜制作材料。',
 '04_研究资料':'课程要求、作业一与案例库、研究过程和论文原文。',
 '05_汇报与成片':'最终作业原提交、9 月 28 日汇报、早期视频；90 号子目录存上次整理的资料副本。',
 '06_制作工具':'实际使用的 AI 视频工作流与 Bodystorming 研究原型。工具快照另存 90 号历史目录。',
 '07_面试准备':'面向 AI 产品经理和 Agent Harness 两个方向的项目讲法、证据与待补实验。',
 '90_历史工程与旧提交':'整理前的 output、作业二、脚本和临时过程目录，以及工具归档快照。保留原内部结构，用于追溯旧版本。',
 '99_备份与整理记录':'整理前总备份、首次归档记录、本次移动表与路径修复记录；旧网页只作历史留存。',
}
for name,note in folders.items():
    home=ROOT/name;home.mkdir(exist_ok=True)
    save(home/'00_文件夹说明.md',f'# {name}\n\n{note}')

save(ROOT/'00_目录说明.md', '# 思辨设计工作区\n\n已按用途实际移动文件夹，直接在资源管理器中按名称排序即可。\n\n'+ '\n'.join('- '+link(name,ROOT/name,ROOT)+'：'+note for name,note in folders.items())+'\n\n## 现在继续做什么\n\n- 先看 `00_当前创作/01_讨论共识与待定问题.md`。\n- 现有 v6 剧本是 S32；已完成的分镜是 F07；反馈修订 Demo 是 D07。三者是此前不同阶段的材料，新一轮跳舞与照看孙辈的故事仍在讨论。\n- 新文件放入对应正式目录；历史工程用于追溯，复制新稿后再继续创作。')

# List scripts and runnable Demos in simple folder-local text tables.
for kind,folder in [('剧本','01_剧本版本'),('Demo','02_Demo版本')]:
    home=ROOT/folder
    lines=[f'# {kind}版本顺序','', '| 编号 | 版本 | 内容 |','| --- | --- | --- |']
    for v in catalog:
        if v['category']==kind:
            lines.append(f'| {v["id"]} | {link(v["title"],ROOT/v["target"],home)} | {v["note"]} |')
    save(home/'00_版本顺序.md','\n'.join(lines))

# Active tool note for the moved originals.
save(ROOT/'06_制作工具/00_运行位置.md', '''# 实际运行位置

- `T01_AI视频工作流/启动工作流.cmd`：现有素材选片、时间线和剪辑。运行前可在该文件夹执行 `python -X utf8 workflow.py doctor`。
- `T02_Bodystorming_Agent/启动场外.cmd`：场外研究原型；已有构建结果，不要求先重新安装 npm 依赖。
- 这两个文件夹是移动后的原运行项目，包含原有数据。历史目录中的工具快照只用于备份。
- 视频线上生成、Agent 真实模型模式和插件连接状态，以各工具实际测试为准；本次文件整理未进行付费调用。
''')

save(ROOT/'99_备份与整理记录/03_旧网页导航/00_历史说明.md', '# 旧网页导航\n\n此处保存首次整理生成的网页和 Markdown 导航。它们指向当时的目录，不作为现在的工作入口。请在工作区根目录按编号文件夹查找，或看 `00_目录说明.md`。')

summary=dict(moves_planned=len(MOVES),generated_markdown_links_repaired=len(repaired),
             repaired_metadata_files=repaired,active_tool_files_rebased=tool_fixed,
             active_storyboard_reference_paths=data['references'],catalogue_count=len(catalog),
             literary_scripts_modified=False,demo_runtime_code_modified=False,
             external_installed_skill_modified=False,
             global_skill_old_path_handled_by='项目 AGENTS.md 显式指定实际视频工作流路径')
(HERE/'路径修复记录.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({k:v for k,v in summary.items() if k not in ['repaired_metadata_files','active_tool_files_rebased']},ensure_ascii=False))
print('active_tool_files_rebased',len(tool_fixed))
