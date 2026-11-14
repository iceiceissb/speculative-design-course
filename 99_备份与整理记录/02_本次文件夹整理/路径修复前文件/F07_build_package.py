"""Build local storyboard reading and production files; does not alter any image."""
from pathlib import Path
import csv
import html
import json
import shutil

ROOT = Path(__file__).resolve().parent
data = json.loads((ROOT / 'storyboard.json').read_text(encoding='utf-8'))
shots = data['shots']
assert len(shots) == 36
assert len({s['id'] for s in shots}) == len(shots)
assert sum(s['duration'] for s in shots) == 180
assert all(a['end'] == b['start'] for a, b in zip(shots, shots[1:]))

def tc(seconds):
    return f'{int(seconds)//60:02d}:{int(seconds)%60:02d}'

def esc(value):
    return html.escape(str(value), quote=True)

ref_dir = ROOT / 'references'
ref_dir.mkdir(exist_ok=True)
for source in data['references']:
    path = Path(source)
    shutil.copy2(path, ref_dir / path.name)

continuity = '''## 人物、空间与道具连续性

- 造型沿用现有定格人偶：邱懿贞短银灰发、砖红开衫；徐月禾低发髻、眼镜、赭黄外套、蓝条纹上衣、砖红围巾；秀秀灰绿折面、两条机械臂、无脸无眼。床边及洗漱时邱穿米白上衣，05 镜已穿好开衫，后续服装不变。角色参考存于 `references/`。
- 客厅固定：窗在画面左，门在后右，浅木茶桌居中；邱坐轮椅在桌左，徐在桌右。近景仍保持相向视线，不突然换边。
- 橘色茶罐：06 机械手轻松开合；23 闭合；24 徐打开；25—36 罐身与罐盖分开放桌。茶罐无品牌或文字。
- 两只米白斑点旧陶杯：清晨为空，回家仍为空；26—31 一只杯碟由机械手托着，徐没有接；32 收回落桌再泡茶；33 起有茶。28、29 的人手不抢先把杯碟接走。
- 两份独立纸包早餐放在同一个牛皮纸提袋：08 徐拿出门；09 放桌；12 提回；16 前挂到轮椅后钩，腾出双手推行；23 全部回桌；25 只拆第一份；33 才拆第二份并分饼。不能把“纸袋”和两份内包装混成同一个物件。
- 买菜后的菜袋挂椅后侧。坡道两段均是同一回程方向向画面右上方，平平台居中；徐推行时在左后方握双推把。到平地停稳才熄灯，第二坡先确认再开灯，松推把前得到主人自动行驶确认。
- 行驶时轮椅支撑脚收起。机械臂始终从车身伸出，不借人的胳膊做动作；脚踏、脚、车轮保持接触合理。
- 手机文字、对白、字幕在剪辑中添加。分镜图无字是制作安排；只有 07 需要后期可读手机文字。

## 节奏与声音

开场 27 秒无对白，闹钟、牙刷、杯罐、口红盖构成节拍。轻快配乐如需使用，音量低，不能用配乐替代动作笑点。到 26 镜第三次递物时收掉配乐，保留徐不接的半拍。27 的机器人回答保持平常语气，不能用恐怖音效提前替观众判案。29—31 不铺煽情弦乐，让坦白与老友的笑话有空间。36 最后一句后留半拍切黑，不加价值总结字幕。

## 可见的反馈闭环

1. 13 抢先代选 → 15 换菜后等点头。
2. 17 隐瞒助力 → 18 朋友提出反馈 → 22 同类坡段先问再开灯。
3. 21 接受“给她留点事” → 24—27 把反馈错误执行成派家务 → 28—31 人澄清 → 32 撤回派活、自己泡茶 → 33 朋友主动参与时才退让。
4. 23 说只有十分钟 → 34 到时起身 → 35 拒绝明天，由朋友主动提出周四。机器人没有把离开或拒绝当成失败。

## 生视频与剪辑用法

每张 PNG 是对应镜头的一个关键画面，不是完整动作视频。上传同号 PNG，复制同号完整即梦提示词，再按分镜时间截取。逐镜提示词仅描述实际入画的人物；不要再拼接全员外貌模板，单人镜头不要一并上传其他人物设定。对白、字幕、跳切及手机文字另做后期。2—4 秒的镜头可先生成较长素材后选取短段；`建议生成秒数`是本项目制作建议，不代表平台当前提供的固定选项。实际以即梦界面可选时长为准。

一个生成任务只承担同号动作。涉及递物、灯亮、拒接的镜头应优先保证起止状态，必要时重生成同号候选。03 洗漱、05 口红、32 倒水等复杂动作不要求一次生成所有细节，可取最可信的一段。34 的时间流逝由剪辑跳切完成，不让模型把杯水位凭空变低。

180 秒是这份分镜的剪辑目标，不是已验证成片时长。先录对白再校准停顿；优先调整进出门、菜摊转场和生活动作，保留三次递物、朋友的拒绝、两次实际调整及结尾半拍。
'''

intro = '''# 《不用麻烦她》v6 完整分镜制作包

基于《思辨喜剧重构稿 v6》，36 镜，计划剪辑时长 180 秒，16:9，无旁白。以“秀秀把给朋友留点事学成派家务”为主冲突。

打开 [分镜预览](index.html) 可按剧情看图、逐镜阅读或复制提示词。每镜画面独立保存在 `frames/`；制作表同时提供 CSV 和 JSON。

本包中的画面是分镜参考，不是已生成的视频。清晨照护与轮椅动作是设计设想，不能据此声称现有 Demo 具有真实轮椅控制或自主学习能力。

'''

table = ['## 全片镜头表', '', '| 镜号 | 时间 | 秒 | 场景／景别 | 画面与动作 | 对白／文字 | 声音与剪辑 |', '|---|---|---:|---|---|---|---|']
for s in shots:
    row = [f"[{s['id']} · {s['title']}]({s['image']})", f"{tc(s['start'])}—{tc(s['end'])}", s['duration'], s['scene']+'；'+s['camera'], s['action'], s['dialogue'], s['sound']+' '+s['edit']]
    table.append('| '+' | '.join(str(v).replace('|', '／').replace('\n', '<br>') for v in row)+' |')
(ROOT / '01_完整分镜表.md').write_text(intro+'\n'.join(table)+'\n\n'+continuity, encoding='utf-8')

def build_video_prompt(shot):
    # Keep the shared block free of cast descriptions. Partial and offscreen
    # characters must never be expanded by a global appearance template.
    return '\n'.join([
        data['video_prompt_common'],
        '本镜入画：' + shot['video_visible_subjects'],
        '场景：' + shot['scene'] + '。机位：' + shot['video_camera_prompt'],
        '动作：' + shot['video_action_prompt'],
        '连续性：' + shot['video_constraints'],
        '声音：' + shot['video_audio'],
        data['video_prompt_output'],
    ])

prompts = [
    '# v6 即梦逐镜画面与动作提示词', '',
    '36 条与现有分镜图一一对应，已按实际入画人物重新编写。', '',
    '## 使用方法', '',
    '1. 上传同号 PNG，复制该镜 `text` 框内的完整提示词。',
    '2. 提示词已包含本镜需要的风格、人物范围、动作和声音，无须再拼接全员外貌模板。',
    '3. 角色设定图供核对身份；单人镜头不要一并上传其他人物设定。画边衣袖、背影和虚焦人物保持原入画范围。',
    '4. 框外的对白、手机文字和剪辑要点用于后期，不复制进生视频指令。', '',
    '## 逐镜提示词', '',
]
for s in shots:
    prompt = build_video_prompt(s)
    s['video_prompt'] = prompt
    prompts.extend([
        f"### {s['id']}｜{s['title']}｜{tc(s['start'])}—{tc(s['end'])}", '',
        f"参考图：[{s['id']}_{s['title']}.png]({s['image']})；剪辑取 {s['duration']} 秒。", '',
        '**入画范围：** ' + s['video_visible_subjects'], '',
        '```text', prompt, '```', '',
        '**后期对白／文字：** ' + s['dialogue'], '',
        '**剪辑要点：** ' + s['edit'], '',
    ])
(ROOT / '02_即梦逐镜提示词.md').write_text('\n'.join(prompts), encoding='utf-8')

image_prompts = ['# v6 分镜画面生成提示词', '', '生成工具：内置 imagegen。角色身份与定格材质参考来自现有项目；各镜为新生成的独立画面。', '', '## 共用英文规范', '', data['image_prompt_common'], '', '## 逐镜画面规范', '']
for s in shots:
    image_prompts.extend([f"### {s['id']}｜{s['title']}", '', s['keyframe'], ''])
(ROOT / '03_分镜画面提示词.md').write_text('\n'.join(image_prompts), encoding='utf-8')

fields = ['镜号', '镜名', '入点', '出点', '剪辑秒数', '场景', '景别与机位', '动作', '对白或文字', '音效', '剪辑', '参考图', '建议生成秒数', '即梦提示词']
with (ROOT / '分镜制作表.csv').open('w', encoding='utf-8-sig', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(fields)
    for s in shots:
        writer.writerow([s['id'],s['title'],tc(s['start']),tc(s['end']),s['duration'],s['scene'],s['camera'],s['action'],s['dialogue'],s['sound'],s['edit'],s['image'],s['generation_seconds'],s['video_prompt']])

def asset_url(shot):
    revision = shot.get('image_revision')
    return shot['image'] + ('?v=' + revision if revision else '')

cards=[]
for s in shots:
    cards.append(f'''<article class="card" id="shot-{s['id']}" data-id="{s['id']}">
<button class="frame" data-view="{s['id']}" aria-label="查看第{s['id']}镜"><img src="{esc(asset_url(s))}" alt="第{s['id']}镜 {esc(s['title'])}" loading="lazy"><span class="stamp">{s['id']}</span></button>
<div class="card-body"><div class="meta">{tc(s['start'])} — {tc(s['end'])}<span>{s['duration']} 秒</span></div><h2>{esc(s['title'])}</h2><div class="scene">{esc(s['scene'])} · {esc(s['camera'])}</div><p>{esc(s['action'])}</p><blockquote>{esc(s['dialogue'])}</blockquote><details><summary>声音、剪辑与制作提示词</summary><p><b>声音</b> {esc(s['sound'])}</p><p><b>剪辑</b> {esc(s['edit'])}</p><p class="intent">{esc(s['intent'])}</p><p><b>本镜入画</b> {esc(s['video_visible_subjects'])}</p><p>上传同号 PNG，直接复制下方完整提示词；对白与剪辑说明另做后期。</p><textarea readonly aria-label="第{s['id']}镜即梦提示词">{esc(s['video_prompt'])}</textarea><button class="copy" data-copy="{s['id']}">复制即梦提示词</button><a href="{esc(asset_url(s))}" target="_blank">打开原图 ↗</a></details></div></article>''')

page='''<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>不用麻烦她 · v6 完整分镜</title>
<style>
:root{color-scheme:light;--paper:#f4f1e9;--ink:#262d25;--sage:#536650;--line:#d5d7cb;--muted:#6b7267}*{box-sizing:border-box}body{margin:0;background:var(--paper);color:var(--ink);font-family:"Microsoft YaHei","PingFang SC",system-ui,sans-serif;line-height:1.7}header{max-width:1440px;margin:auto;padding:46px 32px 26px}.eyebrow{font:600 12px system-ui;letter-spacing:.2em;color:var(--sage)}h1{font-size:clamp(30px,4vw,50px);font-weight:600;letter-spacing:.04em;margin:10px 0 9px}.intro{max-width:800px;color:var(--muted);margin:0 0 18px}.links{display:flex;flex-wrap:wrap;gap:12px}a{color:var(--sage);text-underline-offset:4px}.bar{position:sticky;top:0;z-index:5;border-top:1px solid var(--line);border-bottom:1px solid var(--line);background:rgba(244,241,233,.97);padding:12px 32px;display:flex;align-items:center;gap:14px;flex-wrap:wrap}.bar-inner{max-width:1376px;display:flex;align-items:center;gap:15px;flex-wrap:wrap;width:100%;margin:auto}button{font:inherit;cursor:pointer}.mode,.copy{border:1px solid #bcc5b6;background:transparent;color:var(--sage);border-radius:5px;padding:7px 13px}.mode.active{background:var(--sage);color:white}#status{font-size:13px;color:var(--muted);margin-left:auto}main{max-width:1440px;margin:auto;padding:28px 32px 72px}.grid{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:26px}.card{border:1px solid var(--line);border-radius:7px;background:#faf8f3;overflow:hidden;scroll-margin-top:90px}.frame{display:block;border:0;width:100%;padding:0;position:relative;aspect-ratio:16/9;background:#e5e3d9;overflow:hidden}.frame img{width:100%;height:100%;object-fit:contain;display:block}.stamp{position:absolute;left:10px;top:10px;background:rgba(27,35,25,.76);color:white;border-radius:3px;padding:1px 8px;font:600 12px/23px system-ui}.card-body{padding:18px 20px 22px}.meta{font:12px/1.5 system-ui;color:var(--muted);display:flex;justify-content:space-between}.card h2{font-size:19px;line-height:1.4;margin:8px 0}.scene{font-size:12px;color:var(--muted)}p{font-size:14px}blockquote{margin:14px 0 0;border-left:2px solid #9aa88f;padding:5px 0 5px 12px;font-size:14px;color:#40513d}details{margin-top:16px;border-top:1px solid var(--line);padding-top:11px;font-size:13px}summary{cursor:pointer;color:var(--sage)}details p{font-size:13px}textarea{width:100%;min-height:180px;font:12px/1.7 inherit;resize:vertical;padding:9px;background:#f1f0e7;border:1px solid var(--line);border-radius:4px;color:var(--ink)}details .copy{font-size:12px;margin:9px 12px 0 0}details a{font-size:12px}.intent{color:var(--muted)}.grid.reading{grid-template-columns:1fr;max-width:1100px;margin:auto}.reading .card{display:grid;grid-template-columns:1.15fr 1fr}.reading .frame{height:100%;aspect-ratio:auto;min-height:270px}.reading .frame img{object-fit:contain}.footer{font-size:13px;color:var(--muted);margin-top:32px;border-top:1px solid var(--line);padding-top:18px}dialog{border:0;padding:0;background:#f7f5ef;color:var(--ink);max-width:1200px;width:94vw;max-height:94vh;border-radius:8px;box-shadow:0 24px 80px #0005}dialog::backdrop{background:#172014c9}.viewer-top{padding:11px 18px;display:flex;align-items:center;gap:12px}.viewer-top strong{margin-right:auto}.viewer-top button{border:1px solid #bbc4b5;border-radius:4px;background:none;padding:4px 13px;color:var(--sage)}#large{display:block;width:100%;max-height:65vh;object-fit:contain;background:#e5e3d9}.viewer-caption{padding:12px 22px 22px;font-size:14px}#viewerDialogue{color:var(--sage);margin:7px 0}@media(max-width:1050px){.grid{grid-template-columns:repeat(2,minmax(0,1fr))}}@media(max-width:660px){header{padding:30px 18px 22px}.bar{padding:10px 18px}main{padding:20px 18px 40px}.grid{grid-template-columns:1fr}.grid.reading .card{display:block}.reading .frame{aspect-ratio:16/9;min-height:0}#status{margin-left:0}.viewer-top{gap:7px}.viewer-top button{padding:4px 9px}}@media print{header{padding:10mm}.bar,.links,details,dialog{display:none!important}main{padding:0}.grid{display:block}.card{display:grid;grid-template-columns:1fr 1fr;break-inside:avoid;page-break-inside:avoid;margin:0 0 8mm}.frame{height:100%;min-height:180px}.card-body{padding:8px 14px}.card p,blockquote{font-size:11px}.card h2{font-size:16px}.footer{display:none}}
</style></head><body><header><div class="eyebrow">STORYBOARD / VERSION 06</div><h1>不用麻烦她</h1><p class="intro">秀秀照着“给她留点事”的要求，给老友分起了家务。老友却早就知道轮椅没坏，只是愿意陪她演这个借口。</p><div class="links"><a href="01_完整分镜表.md">完整分镜表</a><a href="02_即梦逐镜提示词.md">即梦逐镜提示词</a><a href="分镜制作表.csv" download>下载制作表 CSV</a><a href="storyboard.json" download>JSON</a></div></header>
<nav class="bar"><div class="bar-inner"><button class="mode active" id="gridMode">总览</button><button class="mode" id="readMode">逐镜阅读</button><button class="mode" id="print">打印</button><span id="status">36 镜 · 180 秒 · 16:9</span></div></nav><main><section class="grid" id="shots">__CARDS__</section><p class="footer">画面为内置 imagegen 生成的分镜参考。对白、手机文字与字幕后期添加；关键帧尚不是视频，180 秒为剪辑规划。所有生成记录与提示词保存在本文件夹。</p></main>
<dialog id="viewer"><div class="viewer-top"><strong id="viewerTitle"></strong><button id="prev" aria-label="上一镜">←</button><button id="next" aria-label="下一镜">→</button><button id="close">关闭</button></div><img id="large" alt="分镜大图"><div class="viewer-caption"><div id="viewerAction"></div><div id="viewerDialogue"></div><div id="viewerEdit"></div></div></dialog>
<script>
const shots=__DATA__;const byId=Object.fromEntries(shots.map(s=>[s.id,s]));const root=document.querySelector('#shots');let current=0;const viewer=document.querySelector('#viewer');
function show(i){current=(i+shots.length)%shots.length;const s=shots[current];document.querySelector('#large').src=s.image;document.querySelector('#large').alt=s.title;document.querySelector('#viewerTitle').textContent=s.id+' · '+s.title+' · '+s.duration+' 秒';document.querySelector('#viewerAction').textContent=s.action;document.querySelector('#viewerDialogue').textContent=s.dialogue;document.querySelector('#viewerEdit').textContent='剪辑：'+s.edit;if(!viewer.open)viewer.showModal()}
document.querySelectorAll('[data-view]').forEach(b=>b.onclick=()=>show(shots.findIndex(s=>s.id===b.dataset.view)));
document.querySelector('#prev').onclick=()=>show(current-1);document.querySelector('#next').onclick=()=>show(current+1);document.querySelector('#close').onclick=()=>viewer.close();viewer.addEventListener('click',e=>{if(e.target===viewer)viewer.close()});document.addEventListener('keydown',e=>{if(viewer.open&&e.key==='ArrowRight')show(current+1);if(viewer.open&&e.key==='ArrowLeft')show(current-1)});
document.querySelector('#gridMode').onclick=()=>{root.classList.remove('reading');document.querySelector('#gridMode').classList.add('active');document.querySelector('#readMode').classList.remove('active')};document.querySelector('#readMode').onclick=()=>{root.classList.add('reading');document.querySelector('#readMode').classList.add('active');document.querySelector('#gridMode').classList.remove('active')};document.querySelector('#print').onclick=()=>window.print();
document.querySelectorAll('[data-copy]').forEach(b=>b.onclick=async()=>{const t=byId[b.dataset.copy].video_prompt;try{await navigator.clipboard.writeText(t)}catch(e){const a=document.createElement('textarea');a.value=t;document.body.appendChild(a);a.select();document.execCommand('copy');a.remove()}b.textContent='已复制';setTimeout(()=>b.textContent='复制即梦提示词',1200)});
</script></body></html>'''
embedded=json.dumps([{**s, 'image': asset_url(s)} for s in shots], ensure_ascii=False).replace('</', '<\\/')
(ROOT / 'index.html').write_text(page.replace('__CARDS__','\n'.join(cards)).replace('__DATA__',embedded), encoding='utf-8')

ready = [s for s in shots if (ROOT / s['image']).exists()]
readme = intro+f"当前已有 {len(ready)}/36 张独立分镜图。\n\n"+'''## 文件

- `index.html`：可离线打开的看图与制作页，含放大、键盘翻镜和复制提示词。
- `01_完整分镜表.md`：36 镜时间线、对白、动作、声音、剪辑及连续性。
- `02_即梦逐镜提示词.md`：可逐条复制的生视频提示词。
- `03_分镜画面提示词.md`：画面共用规范与逐镜构图。
- `分镜制作表.csv`：可用 Excel 打开的制作表，UTF-8 BOM 编码。
- `storyboard.json`：结构化分镜与提示词。
- `frames/`：按镜号排序的独立 PNG。
- `references/`：现有人物与轮椅参考图。

计划总时长为 180 秒。素材图用于构图、表情、动作起止参考；未生成或剪辑视频。
'''
readme += '\n## 复制视频提示词\n\n上传同号 PNG，复制预览页或 `02_即梦逐镜提示词.md` 中同号的完整提示词，无须再附全员外貌模板。单人镜头不要一并上传其他人物设定；画边局部与虚焦人物按原构图保留。对白、字幕和剪辑要点另做后期。\n'
readme += '\n## 生成与修正记录\n\n[来源与 AI 使用](04_生成记录.md) · [机械手检查与修正](05_机械手检查与修正.md)。\n'
(ROOT / '00_先看这里.md').write_text(readme, encoding='utf-8')
(ROOT / 'storyboard.json').write_text(json.dumps(data,ensure_ascii=False,indent=2), encoding='utf-8')
print(json.dumps({'shots':len(shots),'seconds':sum(s['duration'] for s in shots),'images_ready':len(ready),'preview':str(ROOT/'index.html')},ensure_ascii=False))
