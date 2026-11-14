"""Focused corrections to the supplied five-page design note, preserving its layout."""
from pathlib import Path
import json
import fitz

ROOT=Path(__file__).resolve().parents[2]
WORK=Path(__file__).resolve().parent
SOURCE=ROOT/'05_汇报与成片/04_最终提交作业/不用麻烦她_简要设计说明.pdf'
TARGET=WORK/'不用麻烦她_简要设计说明_修订.pdf'
FONT='C:/Windows/Fonts/msyh.ttc'

doc=fitz.open(SOURCE)
changes=[]
def background(page,x=20,y=20):return tuple(v/255 for v in page.get_pixmap().pixel(x,y)[:3])
def remove(page,rect,fill):
    page.add_redact_annot(rect,fill=fill)
    page.apply_redactions(images=0,graphics=0)
def box(page,rect,text,size=9.2,color=(.25,.31,.28),bold=False):
    fontfile='C:/Windows/Fonts/msyhbd.ttc' if bold else FONT
    name='RevisionYaHeiBold' if bold else 'RevisionYaHei'
    page.insert_font(fontname=name,fontfile=fontfile)
    font=fitz.Font(fontfile=fontfile)
    # Explicit CJK line wrapping avoids long mixed English/Chinese tokens
    # being moved wholesale to the next line by the textbox's word wrapper.
    lines=[]
    for para in text.split('\n'):
        current=''
        for ch in para:
            if current and font.text_length(current+ch,fontsize=size)>rect.width-2:
                lines.append(current);current=ch
            else:current+=ch
        lines.append(current)
    needed=(font.ascender-font.descender)*size+max(0,len(lines)-1)*size*1.45
    assert needed<=rect.height,('PDF text overflow',text[:35],needed,rect.height)
    for i,line in enumerate(lines):
        page.insert_text((rect.x0,rect.y0+font.ascender*size+i*size*1.45),line,fontname=name,fontsize=size,color=color)

page=doc[0]
old='越阶前确认；报修前询问“要报吗？”'
rects=page.search_for(old);assert len(rects)==1
r=rects[0];fill=background(page,400,514)
remove(page,fitz.Rect(r.x0-1,r.y0-1,550,r.y1+2),fill)
box(page,fitz.Rect(r.x0,r.y0-1,550,r.y1+8),'共享记录可选择允许；报修前询问“要报吗？”',9.5)
changes.append({'page':1,'change':'将未经画面支持的“越阶前确认”改为实际出现的共享与报修授权'})

page=doc[2];fill=background(page)
remove(page,fitz.Rect(44,666,552,686),fill)
box(page,fitz.Rect(45,666.7,552,689),'设想、模拟与实际实现',13.0,(.13,.25,.21),bold=True)
remove(page,fitz.Rect(44,690,552,790),fill)
text=('视频设想：当前V02影片4分37秒，呈现越阶、路况共享、街道核查、施工与复测；越阶机构与公共系统联动尚未完成实物验证。\n'
      '脚本模拟：完成目的地任务后，程序处理已确认上报的地点；点“先不提交”不生成待处理记录。修复时间在游戏中压缩。\n'
      '实际实现：轮椅控制、双视角、现场截图、确认或拒绝上报、道路与碰撞更新、本地存档。没有真实政务接口、多人同步或模型自主学习；影片中的完整错标纠正对话未接入此Demo。')
box(page,fitz.Rect(45,692,550,790),text,9.1)
changes.append({'page':3,'change':'更新为V02/4分37秒；分开说明视频设想、脚本模拟、实际实现，写明确认与拒绝的不同程序结果'})

page=doc[3]
blocks=page.get_text('blocks');related=[b for b in blocks if 'S35 v9' in b[4]];assert related
top=related[0][1]-1
remove(page,fitz.Rect(44,top,552,780),background(page))
box(page,fitz.Rect(45,top,550,780),
    '《不用麻烦她》S35 v9剧本；F11分镜与V02成片制作记录；D10的README、BUILD_NOTES和CREDITS；当前创作目录中的讨论共识及修订记录。本文影片画面为AI生成，游戏画面为Unity实机截图。',9.0)
links={
 'arXiv:2507.11716':'https://arxiv.org/abs/2507.11716',
 'robot-help.github.io':'https://robot-help.github.io/',
 'doi:10.1007/s00521-022-08118-z':'https://link.springer.com/article/10.1007/s00521-022-08118-z',
 'superflux.in / Uninvited Guests':'https://superflux.in/index.php/work/uninvited-guests/',
 'spp.gov.cn / 2023.11.13 典型案例':'https://www.spp.gov.cn/xwfbh/dxal/202311/t20231113_633718.shtml',
 'lyjs.linyi.gov.cn / 第20260358号建议答复':'https://lyjs.linyi.gov.cn/info/1343/84196.htm',
 'quaternius.com / Ultimate Animated Character Pack':'https://quaternius.com/packs/ultimateanimatedcharacter.html'
}
existing={l.get('uri') for l in page.get_links()}
added=0
for label,url in links.items():
    if url in existing:continue
    for r in page.search_for(label):page.insert_link({'kind':fitz.LINK_URI,'from':r,'uri':url});added+=1
changes.append({'page':4,'change':'工作区依据更新为V02，补齐来源文字的可点击链接','links_added':added})

page=doc[4];fill=background(page)
remove(page,fitz.Rect(44,526,552,750),fill)
text=('我按F11的72镜制作分镜首帧，再通过Seedance 2.5官方API逐镜生成视频。每镜限定出场人物、动作、台词与音色；审阅后重做了绕路、按钮点击、公交站拍照和转身等镜头。\n'
      '后期用FFmpeg合成MP4，剪映Skill保留分轨草稿；本地语音识别辅助字幕对时，Real-ESRGAN辅助将多数480p源片放大到1080p。地图与回执直接使用静帧，音乐来自剪映曲库。\n'
      '当前提交为V02，4分37秒。人物声音、手部和机械动作仍有生成局限；影片中的越阶和公共设施改造尚未在真实环境验证。')
box(page,fitz.Rect(45,529,550,744),text,10.6)
changes.append({'page':5,'change':'更新实际AI工具和V02修订流程，说明曲库音乐、静帧及480p放大，不夸大实物能力'})

doc.save(TARGET,garbage=4,deflate=True)
check=fitz.open(TARGET);assert len(check)==5
assert '4分32秒' not in ''.join(p.get_text() for p in check)
assert '越阶前确认' not in check[0].get_text()
render=WORK/'说明修改后';render.mkdir(exist_ok=True)
for i,p in enumerate(check):p.get_pixmap(matrix=fitz.Matrix(1.35,1.35)).save(render/f'{i+1}.png')
(WORK/'设计说明改动记录.json').write_text(json.dumps({'output':str(TARGET),'pages':len(check),'changes':changes},ensure_ascii=False,indent=2),'utf-8')
print(json.dumps({'output':str(TARGET),'pages':len(check),'changed_pages':[1,3,4,5]},ensure_ascii=False))
