from pathlib import Path
import re
import json
from xml.sax.saxutils import escape
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, KeepTogether
from pypdf import PdfReader

root=Path(r'D:\课\大四上\思辨设计\作业二\下一次汇报_剧本与规则\第六版_导演讨论稿')
source=root/'请等下一班_v6_电影短片剧本.md'
out=root/'请等下一班_v6_导演阅读版.pdf'
private=Path(__file__).resolve().parent
pdfmetrics.registerFont(TTFont('Script',r'C:\Windows\Fonts\msyh.ttc',subfontIndex=0))
pdfmetrics.registerFont(TTFont('ScriptBold',r'C:\Windows\Fonts\msyhbd.ttc',subfontIndex=0))
pdfmetrics.registerFontFamily('Script',normal='Script',bold='ScriptBold',italic='Script',boldItalic='ScriptBold')
ink=colors.HexColor('#20252A')
muted=colors.HexColor('#65716C')
accent=colors.HexColor('#235F57')
base=dict(fontName='Script',fontSize=11,leading=18,alignment=TA_LEFT,wordWrap='CJK',textColor=ink)
styles={
 'body':ParagraphStyle('body',**base,spaceAfter=7),
 'dialogue':ParagraphStyle('dialogue',**base,leftIndent=28,rightIndent=15,spaceBefore=1,spaceAfter=7),
 'small':ParagraphStyle('small',fontName='Script',fontSize=9.5,leading=15,wordWrap='CJK',textColor=muted,spaceAfter=7),
 'character':ParagraphStyle('character',fontName='Script',fontSize=10.5,leading=17,wordWrap='CJK',textColor=ink,spaceAfter=7),
 'title':ParagraphStyle('title',fontName='ScriptBold',fontSize=29,leading=38,textColor=ink,spaceAfter=13),
 'heading':ParagraphStyle('heading',fontName='ScriptBold',fontSize=15,leading=23,wordWrap='CJK',textColor=accent,spaceBefore=10,spaceAfter=11,keepWithNext=True),
 'coverheading':ParagraphStyle('coverheading',fontName='ScriptBold',fontSize=12,leading=20,textColor=accent,spaceBefore=9,spaceAfter=6,keepWithNext=True),
}

def rich(s):
    s=escape(s)
    return re.sub(r'\*\*(.*?)\*\*',r'<b>\1</b>',s)

def footer(canvas,doc):
    canvas.saveState()
    canvas.setFillColor(muted)
    canvas.setFont('Script',8)
    canvas.drawString(58,31,'请等下一班 / v6 / 2026.09.26')
    canvas.drawRightString(A4[0]-58,31,str(doc.page))
    canvas.restoreState()

text=source.read_text(encoding='utf-8')
blocks=text.split('\n---\n')
flow=[]
scene_metrics=[]
for idx,block in enumerate(blocks):
    if idx: flow.append(PageBreak())
    lines=[line.strip() for line in block.strip().splitlines() if line.strip()]
    scene_metrics.append({'block':idx,'characters':len(block),'paragraphs':len(lines)})
    for line in lines:
        if line.startswith('# '):
            flow.append(Paragraph(rich(line[2:]),styles['title']))
        elif line.startswith('## '):
            label=line[3:]
            if label=='片尾': flow.append(Spacer(1,8))
            flow.append(Paragraph(rich(label),styles['coverheading' if idx==0 else 'heading']))
        elif re.match(r'^\d\d:\d\d',line) or (idx==0 and (line.startswith(('电影短片','2026年','目标片长','类型','以下为')))):
            flow.append(Paragraph(rich(line),styles['small']))
        elif idx==0:
            flow.append(Paragraph(rich(line),styles['character']))
        elif line.startswith('**'):
            flow.append(Paragraph(rich(line),styles['dialogue']))
        else:
            flow.append(Paragraph(rich(line),styles['body']))

doc=SimpleDocTemplate(str(out),pagesize=A4,rightMargin=58,leftMargin=58,topMargin=48,bottomMargin=49,
    title='请等下一班 · 第六版电影短片剧本',author='思辨设计课程作品',subject='6分30秒 / 导演讨论稿')
doc.build(flow,onFirstPage=footer,onLaterPages=footer)
pdf=PdfReader(str(out))
page_text=[p.extract_text() for p in pdf.pages]
assert len(pdf.pages)>=7
assert all(x.strip() for x in page_text)
for phrase in ['把我的光收回来','太阳就别搬了','你也抬头','下次先问我']:
    assert phrase in ''.join(page_text),phrase
stats={'pages':len(pdf.pages),'page_characters':[len(x) for x in page_text],
       'scene_metrics':scene_metrics,'script_characters':len(text),
       'dialogue_characters':sum(len(re.sub(r'\*\*.*?\*\*：','',line)) for line in text.splitlines() if line.startswith('**') and '：' in line),
       'duration_budget_seconds':390,'readthrough_performed':False}
(private/'reading-checks.json').write_text(json.dumps(stats,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(stats,ensure_ascii=True))
