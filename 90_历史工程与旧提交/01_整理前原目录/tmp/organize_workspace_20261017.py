"""Create a byte-preserving local archive and numbered project catalogue.

Reads the inventory captured before this task. Never moves or deletes sources.
Run first with 'plan', then with 'build'. A completed archive is not overwritten.
"""
from __future__ import annotations
import csv
import hashlib
import html
import io
import json
import os
from pathlib import Path, PurePosixPath
import shutil
import sys
import time
from datetime import datetime
from urllib.parse import quote
import zipfile

ROOT = Path(__file__).resolve().parents[1]
DEST = ROOT / '创作工作区'
DATE = '2026-10-17'
RECORD = DEST / '99_整理记录'
SNAPSHOT = DEST / '90_原始备份' / f'{DATE}_整理前工作文件.zip'
INV = ROOT / 'tmp/workspace_inventory_20261017.json'
SKIP_PARTS = {'.git','node_modules','__pycache__','.venv','venv','.next','.cache',
              '.venv-jianying','.browser-cache','.npm-cache','chrome-test',
              'chrome-profile','jianying-editor-skill'}
SKIP_NAMES = {'.env','.operation.lock'}

def allowed(rel):
    parts = PurePosixPath(rel).parts
    return not any(p in SKIP_PARTS for p in parts) and not any(
        p in SKIP_NAMES or (p.startswith('.env.') and p != '.env.example') for p in parts)

def sha(b): return hashlib.sha256(b).hexdigest()
def file_sha(p):
    h=hashlib.sha256()
    with Path(p).open('rb') as f:
        for b in iter(lambda:f.read(8*1024*1024),b''):h.update(b)
    return h.hexdigest()
def emit(s): print(s, flush=True)
def rel(p): return Path(p).relative_to(ROOT).as_posix()
def mdlink(label, target, base):
    path = os.path.relpath(target, base).replace('\\','/')
    return f'[{label}](<{path}>)'
def safe_target(base, name):
    pp = PurePosixPath(name)
    if pp.is_absolute() or '..' in pp.parts or ':' in name or '\\' in name:
        raise ValueError(f'Unsafe archive name: {name}')
    p = (base / Path(*pp.parts)).resolve()
    p.relative_to(base.resolve())
    return p

S = []
def script(title, path, stage, note, member=None):
    S.append(dict(id=f'S{len(S)+1:02}', title=title, source=path,
                  member=member, stage=stage, note=note))

script('这一次轮椅该听谁的_v1', '作业二/作业二_轮椅机器人_完整提交包_v1.zip', '01_早期轮椅', '最早四幕分镜；从旧 ZIP 恢复。', '提交_这一次轮椅该听谁的/研究与过程/分镜脚本与课堂记录.md')
script('这一次轮椅该听谁的_v1.1', '作业二/提交_这一次轮椅该听谁的/研究与过程/分镜脚本与课堂记录.md', '01_早期轮椅', '更换底盘后，解释、核验和留档的劳动由谁承担。')
script('请别替我让路_内容稿', '作业二/请别替我让路_内容稿/01_PPT叙事内容.md', '01_早期轮椅', '逐页叙事内容稿，非独立电影剧本；轮椅替乘坐者后退。')
b='作业二/下一次汇报_剧本与规则/'
for title, name, note in [
 ('请别替我退场_v1','01_作品调研与剧本v1_请别替我退场.md','机构散场规则被当作本人返程授权。'),
 ('请别替我让路_v2','02_作品调研与剧本v2_请别替我让路.md','走廊、电梯与社交中的礼让是否能用同一条规则。'),
 ('总有人会让_v3','04_作品调研与剧本v3_总有人会让.md','从人流学习谁会让路，是否会固化现实中的不平等。'),
 ('总有人会让_v3.1','05_总有人会让_v3.1_林岚版完整剧本与规则及文字分镜.md','林岚版，补充规则、行动授权与文字分镜。'),
 ('总有人会让_v3.2','06_总有人会让_v3.2_电梯与制度版完整剧本及文字分镜.md','转向电梯容量、候梯次序与制度责任。'),
 ('总有人会让_v3.3','07_总有人会让_v3.3_人格互补与反转版完整剧本及文字分镜.md','轮椅替主人出头，又被机构要求安抚主人。'),
 ('总有人会让_v4','08_总有人会让_v4_医院电梯_完整剧本与故事板.md','医院电梯五段故事，冲突落在等待如何转移。'),
 ('请等下一班_v4.1','09_请等下一班_v4.1_完整剧本与法规修订.md','更新片名、对白和法规调研。'),
 ('请等下一班_v5','第五版_会协商的医院/作品剧本与交互分支.md','医院设备协商出行的分支剧本。'),
 ('请等下一班_v6','第六版_导演讨论稿/请等下一班_v6_电影短片剧本.md','赶往花园合照，却发现自己的位置来自别人的退让。'),
]: script(title,b+name,'02_医院与让行',note)
p=b+'请不要让我永远第一个/'
for title, name, note in [
 ('请不要让我永远第一个_v1','请不要让我永远第一个_完整剧情与剧本.md','15—18 分钟讨论整合稿。'),
 ('请不要让我永远第一个_v2','请不要让我永远第一个_v2_三分钟完整剧本.md','压缩为三分钟，优先服务与一起出行发生冲突。'),
 ('请不要让我永远第一个_v3','请不要让我永远第一个_v3_三分钟完整剧本.md','增加反馈后的协商与光鱼路线调整。'),
 ('请不要让我永远第一个_v4','请不要让我永远第一个_v4_候梯厅重构稿.md','她只是想等朋友，系统却让所有人都等她。'),
 ('请不要让我永远第一个_v5','请不要让我永远第一个_v5_时间寓言版完整剧本.md','把节省时间推进到由谁决定时间用途。'),
 ('请不要让我永远第一个_v6','请不要让我永远第一个_v6_电影叙事版.md','城市入屋序幕与三次机器人第一视角。'),
 ('请不要让我永远第一个_v7','请不要让我永远第一个_v7_积分版完整剧本.md','文明积分兑换优先待遇；机器人承担有理由的差评。'),
]: script(title,p+name,'03_城市礼仪',note)
script('请不要让我永远第一个_v7.1','output/pdf/请不要让我永远第一个_图文剧本/请不要让我永远第一个_v7.1_完整剧本.md','03_城市礼仪','让行视觉修订版，对应图文 PDF。')
script('请不要让我永远第一个_横版汇报文字','output/pdf/请不要让我永远第一个_横版汇报/完整剧本_纯文字.md','03_城市礼仪','横版汇报中的文字稿，原文件未标版本，独立保留。')
p='output/10月8日汇报_剧本重构/'
script('请不要让我永远第一个_v8',p+'02_请不要让我永远第一个_v8_完整剧本.md','03_城市礼仪','城市礼仪系统视角，邱懿贞、徐月禾、秀秀改名后的版本。')
script('被学习的例外_v9提案',p+'04_v9戏剧性重构提案_被学习的例外.md','03_城市礼仪','比较用的重构提案；原文明确不是确定拍摄稿。')
script('不用麻烦她_早期梗概',p+'05_不用麻烦她_剧本梗概.md','04_两位老友','钓鱼与日常照护；轮椅想让主人不用麻烦别人。')
script('不用麻烦她_分镜审阅稿','output/pdf/不用麻烦她_完整分镜审阅版/分镜剧本文字.md','04_两位老友','钓鱼故事的分镜文字稿，与后来早市版分别保存。')
script('不用麻烦她_三分钟修订稿',p+'06_不用麻烦她_三分钟修订剧本.md','04_两位老友','主要场景改为小区、早市和缓坡。')
script('不用麻烦她_v2',p+'07_不用麻烦她_三分钟修订剧本_v2.md','04_两位老友','用相同机位、停顿和助力反馈表现两人的关系。')
p='output/10月10日剧本修订/'
for title,name,note in [
 ('不用麻烦她_v3','不用麻烦她_三分钟导演修订稿_v3.md','增加清晨照护；两段缓坡之间立刻检验调整。'),
 ('不用麻烦她_v4','不用麻烦她_三分钟冲突加强稿_v4.md','轮椅把不用朋友推误解成结束同行，并拒绝假故障。'),
 ('不用麻烦她_v5','不用麻烦她_轻喜剧重构稿_v5.md','假故障引来维修预约，借口险些变成真送修。'),
 ('不用麻烦她_v6','不用麻烦她_思辨喜剧重构稿_v6.md','把给朋友留点事学成分派家务；已有完整 36 镜制作包。'),
]: script(title,p+name,'04_两位老友',note)

D=[]
def demo(title, source, note, prefix=None, aliases=None):
    D.append(dict(id=f'D{len(D)+1:02}',title=title,source=source,prefix=prefix,
                  note=note,aliases=aliases or []))
demo('这一次轮椅该听谁的_v1','作业二/作业二_轮椅机器人_完整提交包_v1.zip','从旧提交包恢复的 v1；与 v1.1 分开保存。','提交_这一次轮椅该听谁的/交互原型v1/')
demo('这一次轮椅该听谁的_v1.1','作业二/提交_这一次轮椅该听谁的/交互原型v1','现有文件夹与 v1.1 提交包的顶层运行代码一致。',aliases=['作业二/作业二_轮椅机器人_完整提交包_v1.1.zip'])
demo('请别替我让路_3D','作业二/提交_请别替我让路/3D交互原型','礼让与乘坐者选择的 3D 交互原型。',aliases=['作业二/请别替我让路_作业二提交包.zip'])
demo('请等下一班_v4.1_电梯','作业二/下一次汇报_剧本与规则/第四版_汇报提交/电梯3D交互原型','医院电梯交互；另一个汇报目录中也保存了相同运行代码。',aliases=['作业二/李晴芳_2023012028/9.24汇报版本/Demo','作业二/下一次汇报_剧本与规则/第四版_汇报提交/请等下一班_电梯3D原型.zip','作业二/李晴芳_2023012028.zip'])
demo('请等下一班_v5_会协商的医院','作业二/下一次汇报_剧本与规则/第五版_会协商的医院/3D交互短篇','医院协商的分支演示；保留原来的未最终定稿说明。',aliases=['作业二/李晴芳_2023012028/新版（故事不是最终版）/Demo','作业二/下一次汇报_剧本与规则/第五版_会协商的医院_完整提交.zip','作业二/李晴芳_2023012028.zip'])
demo('不用麻烦她_早期打包版','output/最终作业_不用麻烦她_3D交互原型.zip','从早期 ZIP 恢复；用于比较加入结尾规则反馈之前的实现。','最终作业_不用麻烦她_3D交互原型/')
demo('不用麻烦她_反馈修订版','output/最终作业_不用麻烦她_3D交互原型','当前原型：六幕选择、跨幕记忆、下一次行动对照及结尾规则。它对应此前早市故事，尚未改成新讨论的跳舞故事。',aliases=['output/最终作业_不用麻烦她_3D交互原型_2026-10-08_修订.zip'])

F=[]
def visual(title, source, note, entry=None):
    F.append(dict(id=f'F{len(F)+1:02}',title=title,source=source,note=note,entry=entry))
visual('城市礼仪_定格故事板','output/故事板_定格版','完整故事板提示词、首批五张与完整分镜图片。')
visual('医院_四镜头试片素材','output/医院16秒试片_四镜头素材包','16 秒试片的四镜头图片与提示词。','打开这里_四镜头配图配文.html')
visual('永远第一个_v7.1_图文剧本','output/pdf/请不要让我永远第一个_图文剧本','图文剧本 PDF 与制作文字。','请不要让我永远第一个_图文剧本_v7.1.pdf')
visual('永远第一个_横版汇报','output/pdf/请不要让我永远第一个_横版汇报','横版 PDF、对应讲稿与图像提示词。','请不要让我永远第一个_16比9横版汇报.pdf')
visual('不用麻烦她_早期分镜审阅','output/pdf/不用麻烦她_完整分镜审阅版','早期钓鱼故事的图文审阅稿。','不用麻烦她_完整分镜与剧本.pdf')
visual('不用麻烦她_18镜至36帧制作','output/最终作业_不用麻烦她_3D交互原型/分镜图','这一阶段的分镜随 D07 一起保留，避免重复复制。','30帧制作版/即梦制作台.html')
visual('不用麻烦她_v6_完整36镜','output/10月10日剧本修订/v6_完整分镜','截至本次整理已完成的最新分镜包，含机械手修正与按出镜人物优化的视频提示词。','index.html')
visual('v6_机械手第一次修正记录','output/10月10日剧本修订/v6_机械手修正_2026-10-11','局部旧图和旧文件备份，不是独立完整画廊。')
visual('v6_洗漱机械手复修记录','output/10月10日剧本修订/v6_洗漱机械手复修_2026-10-11','洗漱镜头的修改前文件与验证记录。')
visual('v6_视频提示词修改前后','output/10月10日剧本修订/v6_视频提示词优化_2026-10-11','提示词修改前快照及一次性修订脚本；旧页面依赖不完整，不作体验入口。')

V=[('V01_人物设定_定格版','output/人物设定_定格版'),('V02_秀秀定格造型三选','output/秀秀_定格造型三选'),('V03_秀秀轮椅造型候选','output/秀秀_轮椅造型候选')]
T=[dict(id='T01',title='AI视频工作流',source='output/AI视频工作流',note='本地选片与剪映制作工具。原始运行目录继续用于后续工作，归档副本用于备份。',entry='README_先看这里.md'),
   dict(id='T02',title='场外_Bodystorming_Agent',source='bodystorm-agent',note='独立研究原型，不属于轮椅剧情的一个版本。含源码、已构建 dist 和启动入口；不复制 npm、浏览器缓存及 node_modules。',entry='README.md')]

def plan():
    rows=json.loads(INV.read_text(encoding='utf-8'))
    chosen=[r for r in rows if allowed(r['path'])]
    for a in S:
        assert (ROOT/a['source']).is_file(),a
    for a in D+F+T:
        assert (ROOT/a['source']).exists(),a
    data=dict(date=DATE,source_root=str(ROOT),snapshot_file=rel(SNAPSHOT),
              snapshot_files=len(chosen),snapshot_bytes=sum(r['size'] for r in chosen),
              scripts=S,demos=D,visuals=F,visual_references=V,tools=T,
              policy='复制归档；保留原路径；从旧 ZIP 恢复独有版本；不改写剧本与 Demo 内容；不启动付费生成。',
              exclusions=sorted(SKIP_PARTS|SKIP_NAMES),files=chosen)
    (ROOT/'tmp/workspace_organization_plan_20261017.json').write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')
    emit({k:data[k] for k in ['snapshot_files','snapshot_bytes','policy']})
    emit(f'Scripts {len(S)}, Demos {len(D)}, visuals {len(F)}, tools {len(T)}')
    return data

class Archive:
    def __init__(self,z):self.z=z;self.names=set(z.namelist());self.copied=[]
    def one(self, source, dest):
        b=self.z.read(source)
        dest.parent.mkdir(parents=True,exist_ok=True)
        if dest.exists(): raise FileExistsError(dest)
        dest.write_bytes(b)
        zi=self.z.getinfo(source)
        t=time.mktime((*zi.date_time,0,0,-1));os.utime(dest,(t,t))
        self.copied.append(dict(source=source,target=rel(dest),sha256=sha(b),size=len(b)))
    def folder(self, source, dest, extra_skip=()):
        prefix=source.rstrip('/')+'/'
        for n in sorted(self.names):
            if n.startswith(prefix):
                sub=n[len(prefix):]
                if any(p in extra_skip for p in PurePosixPath(sub).parts):continue
                self.one(n,safe_target(dest,sub))
    def nested(self, source, prefix, dest):
        with zipfile.ZipFile(io.BytesIO(self.z.read(source))) as subz:
            for n in subz.namelist():
                if n.startswith(prefix) and not n.endswith('/'):
                    suffix=n[len(prefix):]
                    if not allowed(suffix):continue
                    p=safe_target(dest,suffix);p.parent.mkdir(parents=True,exist_ok=True)
                    if p.exists():raise FileExistsError(p)
                    b=subz.read(n);p.write_bytes(b)
                    zi=subz.getinfo(n);t=time.mktime((*zi.date_time,0,0,-1));os.utime(p,(t,t))
                    self.copied.append(dict(source=source+'::'+n,target=rel(p),sha256=sha(b),size=len(b)))

def write_md(p,text):
    p.parent.mkdir(parents=True,exist_ok=True)
    if p.exists():raise FileExistsError(p)
    p.write_text(text.rstrip()+'\n',encoding='utf-8')

def build():
    if DEST.exists(): raise FileExistsError('创作工作区已经存在，停止以防覆盖。')
    data=plan();RECORD.mkdir(parents=True)
    (RECORD/'整理方案.json').write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')
    SNAPSHOT.parent.mkdir(parents=True)
    originals=[]
    emit('Creating snapshot before organized copies...')
    store_ext={'.zip','.mp4','.mov','.mp3','.wav','.png','.jpg','.jpeg','.webp','.pptx','.xlsx','.docx','.pdf','.7z','.gif','.woff','.woff2'}
    with zipfile.ZipFile(SNAPSHOT,'x',allowZip64=True) as z:
        for i,r in enumerate(data['files']):
            p=ROOT/r['path'];s0=p.stat();b=p.read_bytes();s1=p.stat()
            if s0.st_size!=s1.st_size or s0.st_mtime_ns!=s1.st_mtime_ns:raise RuntimeError('File changed during read: '+str(p))
            zi=zipfile.ZipInfo.from_file(p,arcname=r['path'])
            z.writestr(zi,b,compress_type=zipfile.ZIP_STORED if p.suffix.lower() in store_ext else zipfile.ZIP_DEFLATED,compresslevel=6)
            originals.append(dict(path=r['path'],size=len(b),sha256=sha(b),mtime_ns=s1.st_mtime_ns))
            if i%200==0:emit(f'Backed up {i+1}/{len(data["files"])}')
    (RECORD/'原始文件清单_SHA256.json').write_text(json.dumps(originals,ensure_ascii=False,indent=2),encoding='utf-8')
    emit('Verifying snapshot CRC and per-file SHA256...')
    with zipfile.ZipFile(SNAPSHOT) as z:
        for r in originals:
            assert sha(z.read(r['path']))==r['sha256'],r['path']
    emit('Snapshot verified. Creating numbered folders...')
    with zipfile.ZipFile(SNAPSHOT) as z:
        a=Archive(z)
        for v in S:
            home=DEST/'01_剧本版本'/v['stage']/(v['id']+'_'+v['title'])
            if v['member']:
                with zipfile.ZipFile(io.BytesIO(z.read(v['source']))) as sub:
                    b=sub.read(v['member'])
                target=home/Path(v['member']).name;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(b)
                a.copied.append(dict(source=v['source']+'::'+v['member'],target=rel(target),sha256=sha(b),size=len(b)))
            else:
                target=home/Path(v['source']).name;a.one(v['source'],target)
            v['target']=rel(target);v['sha256']=sha(target.read_bytes())
            write_md(home/'版本说明.md',f'# {v["id"]} · {v["title"]}\n\n{v["note"]}\n\n原始版本名沿用原稿，档案号仅用于检索，不代表同一条连续版本线。\n\n- {mdlink("阅读原稿",target,home)}\n- {mdlink("查看原来源",ROOT/v["source"],home)}\n- 原来源路径：`{v["source"]}`'+(f'\n- ZIP 内文件：`{v["member"]}`' if v['member'] else '')+'\n\n原稿按字节保存，文中的“当前主稿”等表述属于当时的历史状态。旧相对链接请从原来源或整理前备份中查看。')
        for v in D:
            home=DEST/'02_Demo版本'/(v['id']+'_'+v['title']);target=home/'原型'
            if v['prefix']:a.nested(v['source'],v['prefix'],target)
            else:a.folder(v['source'],target,extra_skip={'.ppt_build','.video_build'})
            v['target']=rel(target/'index.html')
            assert (target/'index.html').exists()
            aliases='\n'.join('- '+mdlink(Path(x).name,ROOT/x,home) for x in v['aliases'])
            write_md(home/'版本说明.md',f'# {v["id"]} · {v["title"]}\n\n{v["note"]}\n\n- {mdlink("打开 Demo",target/"index.html",home)}\n- {mdlink("原来源",ROOT/v["source"],home)}\n\n复制了整套运行目录与素材；程序内容未改写。PPT 和视频构建临时文件保存在整理前总备份中。\n\n## 同运行代码的其他来源\n\n'+(aliases or '此次没有合并其他运行代码来源。')+'\n\n“同运行代码”按顶层 HTML、JS、CSS 的文件名和 SHA256 核对，不把同代码的重复提交计成一个新 Demo 版本。关联的其他提交文件仍在总备份中。')
        for v in F:
            home=DEST/'03_分镜与视觉'/(v['id']+'_'+v['title'])
            if v['id']=='F06':target=ROOT/D[-1]['target'];target=target.parent/'分镜图'
            else:
                target=home/'原始材料';a.folder(v['source'],target)
            v['target']=rel(target/(v['entry'] or ''))
            write_md(home/'版本说明.md',f'# {v["id"]} · {v["title"]}\n\n{v["note"]}\n\n- {mdlink("查看归档材料",ROOT/v["target"],home)}\n- {mdlink("原来源",ROOT/v["source"],home)}\n\n历史修正文件夹中的脚本保留当时路径与基线，需阅读后再运行。归档过程未执行任何生图、生视频或原包重建脚本。')
        for title,source in V:a.folder(source,DEST/'03_分镜与视觉'/title)
        for v in T:
            home=DEST/'05_制作工具'/(v['id']+'_'+v['title']);target=home/'工具快照'
            a.folder(v['source'],target)
            v['target']=rel(target/v['entry'])
            write_md(home/'版本说明.md',f'# {v["id"]} · {v["title"]}\n\n{v["note"]}\n\n- {mdlink("阅读工具快照说明",target/v["entry"],home)}\n- {mdlink("打开原运行目录",ROOT/v["source"],home)}\n\n原目录作为实际运行位置，避免已有工程配置失效；快照保留相对路径与现有数据。依赖环境和凭据不属于可移植源码。')
        # Small research and delivery files retain their original hierarchy.
        resource_roots=['作业二/教师反馈后调研_轮椅具身智能','作业二/请别替我让路_内容稿','作业二/提交_这一次轮椅该听谁的/研究与过程','作业二/提交_请别替我让路/研究与讲稿','output/10月8日汇报_剧本重构','output/作业1','output/作业1_5分钟汇报','output/作业1_内容定稿','output/作业1_教师反馈后补充调研','output/作业1_更新汇报','output/作业一_智能轮椅','output/服从的边界_广泛调研','output/机器人自我修养数据库','output/主题筛选与具体场景定稿','output/论文阅读','最终作业','9.28汇报']
        support=DEST/'04_研究与交付'/'原目录资料'
        for source in resource_roots:
            prefix=source+'/'
            for n in sorted(a.names):
                if n.startswith(prefix) and Path(n).suffix.lower() in {'.md','.txt','.docx','.pdf','.pptx','.xlsx','.json','.csv'}:
                    a.one(n,safe_target(support,n))
        write_md(DEST/'04_研究与交付'/'资料入口.md', '# 研究与交付资料\n\n'+ '\n'.join('- '+mdlink(source,support/source,DEST/'04_研究与交付') for source in resource_roots)+'\n\n视频原件继续保留在原目录，并已纳入整理前总备份。当前课堂 PPT 和最新 10 月 8 日修订 PPT 都保留，文件名中的“最终”属于各次提交。')
        (RECORD/'归档副本清单_SHA256.json').write_text(json.dumps(a.copied,ensure_ascii=False,indent=2),encoding='utf-8')
    emit('Writing current discussion and navigation...')
    current=DEST/'00_当前创作'
    write_md(current/'01_讨论共识与待定问题.md', '''# 《不用麻烦她》· 当前讨论记录

更新：2026-10-17。依据本次聊天中的明确回答整理，尚未形成新剧本。

## 已明确的人物与关系

- 邱懿贞原本外向、跳舞很厉害，喜欢和徐月禾及伙伴一起跳舞。后来开始使用轮椅。
- 她渴望陪伴，也怕麻烦别人。向亲人提出过几次见面，得到“下次吧”以后，渐渐不再开口。
- 她希望与徐聊以前的事，一起打扮、出门，也愿意听徐最近的烦恼；她在关系中有付出的愿望。
- 徐的儿女工作忙，需要她帮忙照看孙辈。她愿意帮忙，也感到自己的时间和精力被不断占用，因此减少了跳舞。
- 徐觉得邱已经够不容易，只报喜、不讲自己的难处。邱已经察觉徐很累，所以更不敢约她。
- 邱不是靠阴阳怪气表达不满的人，不能为了笑点改坏人物性格。

## 已提出、还需要确认

- 舞伴是否因为怕她触景生情而不再邀请她；邱没有问过原因。这个解释尚未成为确定事实。
- 两人听懂彼此却仍被现实拉开，是想保留的结尾方向；具体事件、行动与最后一个画面还没决定。
- 希望节奏更快、有冲突、有转折，有生活气，不靠讲道理把主题说完。
- 智能轮椅必须推动冲突。接下来需要决定：它具体做了什么，谁因此失去了什么选择，反馈又怎样改变它下一次的行动。

## 尚未采用的想法

- 徐因为跳舞受伤、被医生禁止跳舞：已被照顾孙辈的设定替代。
- 把两人关系写成见面、谈心、理解、分别：用户认为平淡，而且轮椅被边缘化，不能直接沿用。
- 轮椅变形成跳舞外骨骼，以及轮椅与另一个外骨骼争宠：聊天中的发散想法，未确定采用。
- 不强迫老人融入、交流或跳舞；她也应有拒绝参与的权利。

## 老师建议留下的检查点

- 围绕轮椅如何介入两位老友的关系展开。
- 把代选、隐瞒助力、解释、采纳反馈后的变化写清楚。
- 修养要变成看得见的动作；反馈要改变后一次行动。
- 代际连接可作为后续研究，不必在这一部短片中增加新的完整支线。

## 当前已有材料与新讨论的关系

S32 是已有的 v6 文学稿；F07 是已完成的最新 36 镜分镜包。它们的主冲突仍是把“给朋友留点事”理解成派家务。

D07 是已有的六幕反馈修订 Demo，对应更早的早市故事。它已经包含结尾规则与下一次行动对照，但尚未体现这次新讨论的跳舞、孙辈照护等设定。

这些材料可用来比较与复用，不视为新故事已经确定。

## 下一步讨论

先围绕一件轮椅主动介入的具体事件，确定冲突、反馈和有代价的结尾；确认故事后再改剧本、分镜与 Demo，然后生成视频。
''')
    write_md(current/'02_后续文件命名与归档约定.md', '''# 后续文件约定

- 新故事确认前，讨论材料写在 `00_当前创作`，标明“讨论稿”与待定事项。
- 新剧本沿用《不用麻烦她》的版本线，确认要续用时从 v7 开始；不要覆盖 S32 的 v6。
- 新版本形成后新增档案号，S 用于剧本，D 用于可运行原型，F 用于分镜与视觉制作，T 用于制作工具。
- 对同一版本的小修订写清日期、修订内容和上一个基线；不要只写“最终版”。
- Demo 每次归档保留整套运行文件和素材。分镜保存 JSON、提示词、图片和生成记录。
- 当前归档目录中的原稿是历史快照。继续修改时建立新稿，并在导航页记录它对应的档案号。
''')
    for group in [S,D,F,T]:
        for v in group:
            if v['id'].startswith('S'):v['category']='剧本'
            elif v['id'].startswith('D'):v['category']='Demo'
            elif v['id'].startswith('F'):v['category']='分镜与视觉'
            else:v['category']='制作工具'
    catalog=S+D+F+T
    (RECORD/'版本总表.json').write_text(json.dumps(catalog,ensure_ascii=False,indent=2),encoding='utf-8')
    with (RECORD/'版本总表.csv').open('w',encoding='utf-8-sig',newline='') as f:
        w=csv.DictWriter(f,fieldnames=['id','category','title','note','source','member','target'],extrasaction='ignore');w.writeheader();w.writerows(catalog)
    page=['# 思辨设计工作区导航',f'\n整理日期：{DATE}。先从这份导航进入。',f'\n已汇总 **{len(S)} 份剧本／叙事稿、{len(D)} 个不同运行代码的 Demo、{len(F)} 组分镜材料和 {len(T)} 个制作工具**。编号用于检索，原始版本名与内容保留。', '\n## 当前创作\n']
    for label,target in [('讨论共识与待定问题',current/'01_讨论共识与待定问题.md'),('已有最新剧本 S32',ROOT/S[-1]['target']),('已有最新 36 镜分镜 F07',ROOT/F[6]['target']),('已有反馈修订 Demo D07',ROOT/D[-1]['target']),('后续命名约定',current/'02_后续文件命名与归档约定.md')]:page.append('- '+mdlink(label,target,ROOT))
    page.append('\n已有剧本、分镜和 Demo 分属不同阶段；跳舞与孙辈照护的新讨论还没有确定拍摄稿。\n')
    for heading,group in [('剧本版本',S),('Demo 版本',D),('分镜与视觉',F),('制作工具',T)]:
        page.append(f'## {heading}\n\n| 编号 | 名称 | 内容 |\n| --- | --- | --- |')
        for v in group:page.append(f'| {v["id"]} | {mdlink(v["title"],ROOT/v["target"],ROOT)} | {v["note"]} |')
        page.append('')
    page.append('## 研究、汇报与原视频\n')
    for label,target in [('研究与交付资料入口',DEST/'04_研究与交付'/'资料入口.md'),('当前课堂 Pre PPT',DEST/'04_研究与交付'/'原目录资料/最终作业/简介PPT_不用麻烦她_Pre.pptx'),('Pre 讲稿',DEST/'04_研究与交付'/'原目录资料/最终作业/不用麻烦她_最终Pre讲稿.md'),('已完成的原视频',ROOT/'最终作业/最终视频.mp4'),('案例库',DEST/'04_研究与交付'/'原目录资料/output/机器人自我修养数据库')]:page.append('- '+mdlink(label,target,ROOT))
    page.append('\n## 备份与整理范围\n')
    page.append('- '+mdlink('整理前工作文件 ZIP',SNAPSHOT,ROOT))
    page.append('- '+mdlink('原始文件 SHA256 清单',RECORD/'原始文件清单_SHA256.json',ROOT))
    page.append('- '+mdlink('版本总表 CSV',RECORD/'版本总表.csv',ROOT))
    page.append('- '+mdlink('核对结果',RECORD/'整理核对结果.json',ROOT))
    page.append('\n原目录作为来源保留，后续查找统一从新导航进入。总备份保留原有文件相对路径，包含旧 ZIP、视频、制作脚本和过程记录；未复制 node_modules、虚拟环境、浏览器与 npm 缓存、下载的第三方 Skill、运行锁和实际 .env 凭据。原稿内的历史“当前／最终”表述不改写。\n\n恢复备份时请先解压到新目录，按原路径对照；不要直接覆盖当前创作文件。')
    write_md(ROOT/'00_工作区导航.md','\n'.join(page))
    build_html(catalog)
    # Verify every materialized byte against its source hash, and ensure no original changed.
    emit('Verifying organized files and unchanged original files...')
    for r in a.copied:assert sha((ROOT/r['target']).read_bytes())==r['sha256'],r['target']
    changed=[]
    for r in originals:
        p=ROOT/r['path']
        if not p.exists() or sha(p.read_bytes())!=r['sha256']:changed.append(r['path'])
    result=dict(date=DATE,scripts=len(S),unique_story_demos=len(D),visual_groups=len(F),tools=len(T),
                snapshot_files=len(originals),snapshot_size=SNAPSHOT.stat().st_size,
                snapshot_sha256=file_sha(SNAPSHOT),snapshot_content_hashes_verified=True,
                organized_files=len(a.copied),organized_content_hashes_verified=True,
                original_changed=changed,originals_moved=0,originals_deleted=0,
                remaining_validation='Demo 本地依赖与浏览器打开检查另记。')
    (RECORD/'整理核对结果.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
    write_md(DEST/'90_原始备份'/'备份说明.md',f'# 整理前备份\n\n日期：{DATE}\n\n{len(originals)} 个工作文件，保留原相对路径。包含原有提交 ZIP 和视频。排除可重新安装的依赖、缓存和实际 .env 凭据。\n\nZIP SHA256：`{result["snapshot_sha256"]}`\n\nCRC 与逐文件 SHA256 已检查；副本与原文件内容一致。原目录未移动、未删除。恢复时先解压到一个空目录。\n\n独有的 v1 剧本与 Demo 来自备份内的旧提交 ZIP，在编号目录中已额外恢复为可直接阅读／打开的文件。')
    emit(result)

def build_html(catalog):
    def url(target):return quote(os.path.relpath(ROOT/target,ROOT).replace('\\','/'),safe='/')
    rows=[]
    for v in catalog:
        rows.append(f'<article data-kind="{html.escape(v["category"])}"><div class="eyebrow">{v["id"]} · {html.escape(v["category"])}</div><h3><a href="{url(v["target"])}">{html.escape(v["title"])}</a></h3><p>{html.escape(v["note"])}</p><small>原来源：{html.escape(v["source"])}</small></article>')
    body='''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>思辨设计 · 创作工作区</title>
<style>:root{color-scheme:light;--ink:#26332e;--muted:#64726a;--paper:#f5f3ed;--line:#d9ded5;--green:#315841}*{box-sizing:border-box}body{margin:0;background:var(--paper);color:var(--ink);font-family:"Microsoft YaHei",system-ui,sans-serif;line-height:1.7}main{max-width:1180px;margin:auto;padding:44px 28px 70px}header{border-bottom:1px solid var(--line);padding-bottom:28px}h1{font-size:34px;line-height:1.3;margin:8px 0 12px}h2{font-size:22px;margin-top:34px}h3{font-size:17px;line-height:1.5;margin:6px 0 12px}p{margin:0 0 12px}a{color:var(--green);text-underline-offset:4px}a:hover{color:#142a1c}.eyebrow{font-size:12px;letter-spacing:.08em;color:var(--muted)}.intro{max-width:820px;color:var(--muted)}.current{display:grid;grid-template-columns:repeat(4,1fr);gap:12px;margin:20px 0}.current a{display:block;background:#e5ece1;border:1px solid #b8c6b4;border-radius:10px;padding:18px;text-decoration:none}.current strong{display:block;font-size:17px}.current span{display:block;font-size:12px;color:var(--muted);margin-top:5px}.controls{display:flex;flex-wrap:wrap;gap:8px;position:sticky;top:0;padding:14px 0;background:var(--paper);z-index:2}input{flex:1;min-width:220px;padding:10px 13px;border:1px solid #aab7ac;border-radius:6px;font:inherit}button{font:inherit;border:1px solid #aab7ac;background:transparent;padding:8px 13px;border-radius:6px;cursor:pointer}button[aria-pressed=true]{background:var(--green);color:white}.grid{display:grid;grid-template-columns:repeat(3,1fr);gap:14px}article{background:#fffefa;border:1px solid var(--line);border-radius:10px;padding:20px;overflow-wrap:anywhere}article p{font-size:14px}small{font-size:11px;color:var(--muted)}[hidden]{display:none!important}.notice{border-left:3px solid #799277;padding:8px 16px;margin:20px 0}.footer{font-size:13px;color:var(--muted);margin-top:32px}.links{display:flex;flex-wrap:wrap;gap:10px 24px}#count{font-size:13px;color:var(--muted);margin:4px 0 14px}@media(max-width:850px){.grid{grid-template-columns:repeat(2,1fr)}.current{grid-template-columns:repeat(2,1fr)}}@media(max-width:540px){main{padding:28px 16px}.grid,.current{grid-template-columns:1fr}h1{font-size:28px}}</style>
<main><header><div class="eyebrow">思辨设计 / 版本档案 / 2026.10.17</div><h1>《不用麻烦她》与此前的创作</h1><p class="intro">32 份剧本与叙事稿，7 个不同运行代码的 Demo，10 组分镜材料。原版本名保留，重复提交列为同一档案的来源。先从下方四个入口继续。</p></header>
<section><h2>当前创作</h2><div class="current">
<a href="__CURRENT__"><strong>继续讨论故事</strong><span>已明确的人物、待定冲突与结尾</span></a>
<a href="__SCRIPT__"><strong>S32 · 已有 v6 剧本</strong><span>“给朋友留点事”与派家务</span></a>
<a href="__STORYBOARD__"><strong>F07 · 已有 36 镜分镜</strong><span>最新机械手修正与视频提示词</span></a>
<a href="__DEMO__"><strong>D07 · 反馈修订 Demo</strong><span>六幕选择、记忆与下一次行动</span></a></div>
<p class="notice">跳舞、照看孙辈与更有余味的结尾，仍在讨论中。已有剧本、分镜和 Demo 分属此前不同阶段，不能视为新故事已经定稿。</p></section>
<h2>全部版本</h2><div class="controls"><input id="search" type="search" placeholder="搜索片名、版本、关键词" aria-label="搜索版本"><button data-filter="全部" aria-pressed="true">全部</button><button data-filter="剧本" aria-pressed="false">剧本</button><button data-filter="Demo" aria-pressed="false">Demo</button><button data-filter="分镜与视觉" aria-pressed="false">分镜</button><button data-filter="制作工具" aria-pressed="false">工具</button></div><div id="count" aria-live="polite"></div><div class="grid">__CARDS__</div>
<h2>资料与备份</h2><div class="links"><a href="__RESOURCES__">研究与交付资料</a><a href="__MD__">Markdown 总导航</a><a href="__CSV__">版本总表 CSV</a><a href="__BACKUP__">整理前总备份</a><a href="__CHECKS__">整理核对记录</a><a href="__VIDEO__">原有最终视频</a></div>
<p class="footer">归档只复制文件，没有修改原剧本、Demo 或分镜内容。原路径继续保留。备份包括工作文件与原有 ZIP；不含依赖环境、浏览器与 npm 缓存、实际 .env 凭据。S / D / F / T 是检索编号，不代表一条统一剧情版本线。历史稿中的“当前”“最终”以当时语境为准。</p></main>
<script>const cards=[...document.querySelectorAll('article')],search=document.querySelector('#search'),count=document.querySelector('#count');let filter='全部';function update(){const q=search.value.trim().toLocaleLowerCase();let n=0;for(const card of cards){const show=(filter==='全部'||card.dataset.kind===filter)&&card.textContent.toLocaleLowerCase().includes(q);card.hidden=!show;if(show)n++}count.textContent=`显示 ${n} / ${cards.length} 个档案`}search.addEventListener('input',update);for(const button of document.querySelectorAll('[data-filter]'))button.addEventListener('click',()=>{filter=button.dataset.filter;for(const b of document.querySelectorAll('[data-filter]'))b.setAttribute('aria-pressed',String(b===button));update()});update();</script></html>'''
    targets={'CURRENT':'创作工作区/00_当前创作/01_讨论共识与待定问题.md','SCRIPT':S[-1]['target'],'STORYBOARD':F[6]['target'],'DEMO':D[-1]['target'],'RESOURCES':'创作工作区/04_研究与交付/资料入口.md','MD':'00_工作区导航.md','CSV':'创作工作区/99_整理记录/版本总表.csv','BACKUP':rel(SNAPSHOT),'CHECKS':'创作工作区/99_整理记录/整理核对结果.json','VIDEO':'最终作业/最终视频.mp4'}
    for k,v in targets.items():body=body.replace('__'+k+'__',url(v))
    body=body.replace('__CARDS__','\n'.join(rows))
    p=ROOT/'00_打开工作区.html'
    if p.exists():raise FileExistsError(p)
    p.write_text(body,encoding='utf-8')

if __name__=='__main__':
    if sys.argv[1:] == ['plan']:plan()
    elif sys.argv[1:] == ['build']:build()
    else:raise SystemExit('Use plan or build')
