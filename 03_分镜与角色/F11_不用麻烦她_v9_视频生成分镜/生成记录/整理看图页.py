from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageStat
import json, hashlib, html, re

ROOT = Path(__file__).resolve().parent.parent
manifest = json.loads((ROOT / '分镜图片索引.json').read_text(encoding='utf-8-sig'))
story_path = ROOT / 'storyboard.json'
story = json.loads(story_path.read_text(encoding='utf-8-sig'))
shots = {s['id']: s for s in story['shots']}
frames = manifest['frames']
assert len(frames) == 72 and {f['id'] for f in frames} == {f'{i:02d}' for i in range(1,73)}
out = ROOT / '总览'
thumbs = out / '缩略图'
thumbs.mkdir(parents=True, exist_ok=True)
font_file = 'C:/Windows/Fonts/msyh.ttc'
font_bold = 'C:/Windows/Fonts/msyhbd.ttc'
def font(size, bold=False):
    return ImageFont.truetype(font_bold if bold else font_file, size)

technical = []
for f in frames:
    path = ROOT / f['image']
    assert path.is_file(), path
    with Image.open(path) as check:
        check.verify()
    with Image.open(path) as source:
        width, height = source.size
        assert width >= 1200 and height >= 675
        assert abs((width / height) / (16 / 9) - 1) < .015
        preview = source.convert('RGB')
        preview.thumbnail((768,432), Image.Resampling.LANCZOS)
        preview.save(thumbs / (f['id'] + '.jpg'), quality=87)
        variance = sum(ImageStat.Stat(source.convert('RGB').resize((64,36))).var)
        assert variance > 1, f['id']
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    f.update(width=width, height=height, bytes=path.stat().st_size, sha256=digest)
    technical.append({k:f[k] for k in ['id','image','width','height','bytes','sha256']})
assert len({f['sha256'] for f in frames}) == 72, 'duplicate selected image files'

def sheet(items, filename, columns=3, tile_width=564, heading=''):
    pad, gap, top = 36, 18, 112
    image_height = round(tile_width * 9 / 16)
    cell_height = image_height + 42
    rows = (len(items) + columns - 1) // columns
    canvas = Image.new('RGB', (pad*2+columns*tile_width+(columns-1)*gap, top+rows*cell_height+(rows-1)*gap+pad), '#f3f0e9')
    draw = ImageDraw.Draw(canvas)
    draw.text((pad,24), '不用麻烦她', font=font(34,True), fill='#283e35')
    draw.text((pad,70), heading or '72 镜分镜审阅版', font=font(20), fill='#58665d')
    for n, f in enumerate(items):
        x = pad + (n % columns) * (tile_width+gap)
        y = top + (n // columns) * (cell_height+gap)
        with Image.open(ROOT/f['image']) as image:
            view = image.convert('RGB')
            view.thumbnail((tile_width,image_height),Image.Resampling.LANCZOS)
            canvas.paste(view,(x+(tile_width-view.width)//2,y+(image_height-view.height)//2))
        caption = f"{f['id']}  {f['title']}"
        while draw.textlength(caption,font=font(19)) > tile_width-8:
            caption = caption[:-2] + '…'
        draw.text((x,y+image_height+9),caption,font=font(19),fill='#29392f')
    canvas.save(out/filename,quality=91,subsampling=0)

for page in range(6):
    part = frames[page*12:(page+1)*12]
    sheet(part,f"总览_{page+1:02d}_{part[0]['id']}-{part[-1]['id']}.jpg",heading=f"分镜审阅版  /  {part[0]['id']}—{part[-1]['id']}  /  {page+1} of 6")
sheet(frames,'全片72镜总览.jpg',columns=6,tile_width=320,heading='全片72镜  /  图片按故事顺序排列')
key_ids = ['02','04','08','15','16','20','25','42','53','56','66','71']
sheet([next(f for f in frames if f['id']==sid) for sid in key_ids],'关键镜头总览.jpg',heading='关键镜头预览  /  完整72镜见看图页')

data=[]
for f in frames:
    s=shots[f['id']]
    data.append({**{k:f[k] for k in ['id','title','image','review_notes']},'scene':s['scene'],'seconds':s['edit_seconds'],'action':s['action'],'dialogue':'  '.join(d['speaker']+'：'+d['text'] for d in s.get('dialogue',[]))})
gallery='''<!doctype html><html lang="zh-CN"><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>不用麻烦她 · 72镜分镜</title>
<style>
*{box-sizing:border-box}body{margin:0;background:#f3f0e9;color:#263b31;font:16px/1.65 system-ui,"Microsoft Yahei",sans-serif}header{max-width:1440px;margin:auto;padding:48px 32px 24px}h1{font-family:serif;font-size:42px;margin:0}header p{color:#68756c;margin:9px 0}nav{display:flex;gap:10px;flex-wrap:wrap;align-items:center;margin:24px 0 10px}a{color:#3c6754}button,select{font:inherit;background:#fffdf7;color:#344d3f;border:1px solid #cfD6ca;border-radius:5px;padding:8px 14px;cursor:pointer}button:hover{background:#e1e8db}main{max-width:1440px;padding:0 32px 48px;margin:auto;display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:28px}article{background:#fffdf8;border:1px solid #dedfd4;border-radius:7px;overflow:hidden}article img{width:100%;aspect-ratio:16/9;object-fit:contain;display:block;background:#111;cursor:zoom-in}.info{padding:16px 20px 20px}.row{display:flex;justify-content:space-between;gap:14px}h2{font-size:19px;margin:0}.meta{font-size:13px;color:#738074;white-space:nowrap}.info p{margin:10px 0;font-size:15px}.dialogue{color:#536d59;border-left:2px solid #b9c8ae;padding-left:12px}details{color:#8b643e;font-size:13px;margin-top:12px}details p{font-size:13px!important}dialog{border:0;padding:0;background:#141914;color:#eee;max-width:96vw;width:1400px;max-height:96vh;border-radius:6px}dialog::backdrop{background:#000d}dialog img{display:block;width:100%;max-height:78vh;object-fit:contain}dialog .bar{padding:12px 18px;display:flex;align-items:center;justify-content:space-between;gap:12px}dialog p{font-size:14px;margin:0}.close{margin-left:auto}footer{max-width:1440px;padding:0 32px 40px;margin:auto;color:#7c857a;font-size:13px}@media(max-width:760px){main{grid-template-columns:1fr;padding:0 14px 30px;gap:18px}header{padding:28px 16px 20px}h1{font-size:32px}.row{display:block}.meta{margin-top:5px}dialog .bar{flex-wrap:wrap}}
</style>
<header><h1>不用麻烦她</h1><p>72 镜 · 定格人偶风格 · 图片审阅版 · 剪辑预算 4′54″</p><p>点击图片放大，左右方向键换镜。每张图下附镜号、动作与对白。</p><nav><select id="scene"><option value="all">全部场次</option></select><button id="issues">只看有制作备注的镜头</button><a href="总览/全片72镜总览.jpg">全片总览</a><a href="05_分镜图片审阅说明.md">审阅说明</a><a href="frames/">原图文件夹</a></nav></header><main id="grid"></main><footer>原图与当前选用版本均保存在本项目。图片用于审阅叙事与构图；机构与场景锁定事项见每镜制作备注。</footer>
<dialog id="lightbox"><img id="large" alt=""><div class="bar"><button id="prev">← 上一镜</button><p id="caption"></p><button id="next">下一镜 →</button><button class="close" id="close">关闭 Esc</button></div></dialog>
<script id="frames-data" type="application/json">__DATA__</script><script>
const data=JSON.parse(document.getElementById('frames-data').textContent);let current=0,onlyIssues=false;const grid=document.getElementById('grid'),scene=document.getElementById('scene'),box=document.getElementById('lightbox');for(const n of [...new Set(data.map(x=>x.scene))])scene.add(new Option('第 '+n+' 场',String(n)));
function openFrame(i){current=(i+data.length)%data.length;const s=data[current];document.getElementById('large').src=s.image;document.getElementById('large').alt=s.id+' '+s.title;document.getElementById('caption').textContent=s.id+' · '+s.title+'　'+s.action;if(!box.open)box.showModal()}
function render(){grid.replaceChildren();data.forEach((s,i)=>{if(scene.value!=='all'&&String(s.scene)!==scene.value)return;if(onlyIssues&&!s.review_notes.length)return;const a=document.createElement('article');a.id='shot-'+s.id;const im=document.createElement('img');im.src='总览/缩略图/'+s.id+'.jpg';im.alt=s.id+' '+s.title;im.loading='lazy';im.onclick=()=>openFrame(i);a.append(im);const info=document.createElement('div');info.className='info';const row=document.createElement('div');row.className='row';const h=document.createElement('h2');h.textContent=s.id+'　'+s.title;const meta=document.createElement('span');meta.className='meta';meta.textContent='第'+s.scene+'场 · '+s.seconds+'秒';row.append(h,meta);info.append(row);const p=document.createElement('p');p.textContent=s.action;info.append(p);if(s.dialogue){const d=document.createElement('p');d.className='dialogue';d.textContent=s.dialogue;info.append(d)}if(s.review_notes.length){const d=document.createElement('details');const su=document.createElement('summary');su.textContent='制作备注';d.append(su);for(const n of s.review_notes){const p=document.createElement('p');p.textContent=n;d.append(p)}info.append(d)}a.append(info);grid.append(a)})}
scene.onchange=render;document.getElementById('issues').onclick=()=>{onlyIssues=!onlyIssues;document.getElementById('issues').textContent=onlyIssues?'显示全部镜头':'只看有制作备注的镜头';render()};document.getElementById('prev').onclick=()=>openFrame(current-1);document.getElementById('next').onclick=()=>openFrame(current+1);document.getElementById('close').onclick=()=>box.close();document.addEventListener('keydown',e=>{if(!box.open)return;if(e.key==='ArrowRight')openFrame(current+1);if(e.key==='ArrowLeft')openFrame(current-1)});render();
</script></html>'''
gallery=gallery.replace('__DATA__',json.dumps(data,ensure_ascii=False).replace('</','<\\/'))
(ROOT/'看图.html').write_text(gallery,encoding='utf-8')

lines=['# 《不用麻烦她》· 72镜图片', '', '图片审阅版；点击每张图可打开原图。完整动作与对白见 [看图页](看图.html)。','']
for f in frames:
    lines += [f"## {f['id']} {f['title']}",'',f"![{f['id']} {f['title']}]({f['image']})",'',shots[f['id']]['action'],'']
(ROOT/'逐镜图片.md').write_text('\n'.join(lines),encoding='utf-8')

for s in story['shots']:
    f=next(f for f in frames if f['id']==s['id'])
    s['storyboard_image']=f['image']
    s['reference_status']='generated_for_review'
    s['visual_review_notes']=f['review_notes']
story['status']='text_storyboard_prompts_and_72_review_images'
story['image_generation_authorized']=True
story['image_generation_mode']='builtin_imagegen'
story['visual_frames_generated']=72
story['visual_approval_status']='awaiting_user_review_and_scene_lock'
story['reference_state']='72镜图片审阅版已生成；人物、轮椅机构及场景几何尚未整体锁定。'
story['workflow_state']='已完成分镜出图；未向视频平台提交任务。'
story['ready_for_generation']=False
story_path.write_text(json.dumps(story,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
plan_path=ROOT/'generation_plan.json'
plan=json.loads(plan_path.read_text(encoding='utf-8-sig'))
for job in plan['jobs']:
    f=next(f for f in frames if f['id']==job['id'])
    job['storyboard_image']=f['image']
    job['storyboard_image_status']='generated_for_review'
    job.setdefault('first_frame_legacy_placeholder',job.get('first_frame_placeholder'))
    job['first_frame_placeholder']=f['image']
    job['media_ready']=False
plan['note']='72镜分镜图片已生成并关联，仍待审阅与场景/机构锁定；未提交视频任务。导入T01前需适配，不直接替换旧project.json。'
plan_path.write_text(json.dumps(plan,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

source=(ROOT/story['source_script']).resolve()
source_hash=hashlib.sha256(source.read_bytes()).hexdigest().upper()
assert source_hash==story['source_sha256'].upper()
check_path=ROOT/'检查记录.json'
check=json.loads(check_path.read_text(encoding='utf-8-sig'))
check.update(VisualFramesGenerated=True,VisualFrameCount=72,ImageFilesDecoded=72,UniqueSelectedImages=72,VisualProductionApproved=False,VideoJobsSubmitted=0,ActualRuntimeVerified=False,ValidationScope='原Passed字段为文本结构检查；图片文件完整性已检查，视觉制作待定事项见分镜图片索引.json',SourceHashMatches=True)
check_path.write_text(json.dumps(check,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
manifest['technical_checks']={'files_decoded':72,'unique_images':72,'source_script_hash_matches':True,'all_landscape_approximately_16_9':True,'original_images_unchanged':True}
(ROOT/'分镜图片索引.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
(ROOT/'生成记录/图像文件检查.json').write_text(json.dumps({'selected_images':technical,'source_script_hash':source_hash,'contact_sheets':6,'video_tasks_submitted':0},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'selected_images':72,'total_generated_images':manifest['total_generated_images'],'dimensions':sorted(set((f['width'],f['height']) for f in frames)),'selected_size_mb':round(sum(f['bytes'] for f in frames)/1024**2,1),'contact_sheets':6,'gallery':'看图.html','source_hash_matches':True},ensure_ascii=True))
