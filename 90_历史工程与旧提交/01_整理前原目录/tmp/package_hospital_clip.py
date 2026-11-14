from pathlib import Path
import json, shutil, html, zipfile
from PIL import Image
root=Path(r'D:/课/大四上/思辨设计/output/医院16秒试片_四镜头素材包')
data=json.loads((root/'素材清单.json').read_text(encoding='utf-8'))
(root/'图片').mkdir(exist_ok=True)
for s in data['shots']:
    dst=root/'图片'/s['file']
    shutil.copy2(s['source'],dst)
    with Image.open(dst) as im:
        s['dimensions']=list(im.size)
        assert im.width>=1600 and 1.76<im.width/im.height<1.79
(root/'素材清单.json').write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')
esc=html.escape
sections=[]
for s in data['shots']:
    f='图片/'+s['file']
    textfile='提示词/'+s['id']+'_'+s['title']+'.txt'
    sections.append(f'<section id="shot{s["id"]}"><div class="eyebrow">SHOT {s["id"]} / {s["edit"]}</div><h2>{esc(s["title"])}</h2><a href="{esc(f)}"><img src="{esc(f)}" alt="{esc(s["title"])}"></a><p class="caption">{esc(s["caption"])}</p><p><b>制作：</b>{esc(s["method"])}</p><p><b>声音：</b>{esc(s["audio"])}</p><details open><summary>即梦动作提示词</summary><pre>{esc(s["prompt"])}</pre><a href="{esc(textfile)}" download>下载本镜提示词 TXT</a></details><p class="check"><b>验收：</b>{esc(s["check"])}</p></section>')
page='''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>医院16秒试片 · 四镜头配图配文</title><style>
*{box-sizing:border-box}body{margin:0;background:#faf7f0;color:#293d37;font:17px/1.8 "Microsoft YaHei",sans-serif}main{max-width:1100px;margin:55px auto;padding:0 30px}h1{font-size:38px;line-height:1.35;margin:12px 0}h2{font-size:28px;margin:8px 0 22px}.eyebrow{font-size:13px;letter-spacing:1.5px;color:#a27c3e}header{padding-bottom:35px;border-bottom:1px solid #ded9ce}nav{display:flex;gap:18px;flex-wrap:wrap;margin-top:22px}a{color:#3f7165}section{padding:45px 0;border-bottom:1px solid #ded9ce}img{display:block;width:100%;height:auto;border-radius:5px}.caption{font-size:22px;color:#69464f;font-weight:600}details{background:#eeece4;padding:18px 24px;border-radius:6px}summary{cursor:pointer;font-weight:700}pre{white-space:pre-wrap;overflow-wrap:anywhere;font:15px/1.9 "Microsoft YaHei",sans-serif}.check{font-size:15px;color:#626c64}.notice{background:#ecefe7;padding:16px 22px;margin-top:22px}footer{padding:35px 0;font-size:14px;color:#69716a}@media(max-width:650px){main{padding:0 18px;margin-top:25px}h1{font-size:29px}h2{font-size:23px}}
</style><main><header><div class="eyebrow">请不要让我永远第一个 / SHOT PACKAGE</div><h1>她在等朋友。<br>所有人却在等她。</h1><p>16 秒 · 四个镜头 · 配图、动作提示词、对白与剪辑说明</p><div class="notice">默认只生成镜头 02、03；镜头 01、04 直接用图片剪辑。四张图都是独立原图，点击图片可打开。当前交付为制作素材，尚非 AI 成片。</div><nav><a href="#shot01">01 全景</a><a href="#shot02">02 林遥</a><a href="#shot03">03 乘客</a><a href="#shot04">04 等待</a><a href="00_四镜头配图配文与操作.md">完整操作说明</a><a href="对白字幕.srt" download>对白字幕 SRT</a></nav></header>'''+''.join(sections)+'''<footer>在即梦每次只上传本镜头的单张图片；不要上传本页截图。人物动作和道具须在视频生成后复核。静帧与提示词由 OpenAI 内置图片工具及文字协作制作。</footer></main></html>'''
(root/'打开这里_四镜头配图配文.html').write_text(page,encoding='utf-8')
# Validate all deliverables before packaging.
for s in data['shots']:
    assert (root/'图片'/s['file']).is_file()
    assert (root/'提示词'/(s['id']+'_'+s['title']+'.txt')).read_text(encoding='utf-8').strip()==s['prompt']
assert (root/'对白字幕.srt').is_file()
archive=root.parent/(root.name+'.zip')
with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED) as z:
    for p in root.rglob('*'):
        if p.is_file():z.write(p,Path(root.name)/p.relative_to(root))
print(json.dumps({'images':[(s['file'],s['dimensions']) for s in data['shots']],'zip_bytes':archive.stat().st_size,'files':len(list(root.rglob('*')))},ensure_ascii=True))

