from pathlib import Path
import json
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.colors import HexColor
from reportlab.lib.utils import ImageReader

base=Path(__file__).resolve().parent
root=Path(r'D:\课\大四上\思辨设计\作业二\下一次汇报_剧本与规则\第五版_会协商的医院')
slides=json.loads((base/'deck-manifest.json').read_text(encoding='utf-8'))
pdfmetrics.registerFont(TTFont('YaHei',r'C:\Windows\Fonts\msyh.ttc',subfontIndex=0))
pdfmetrics.registerFont(TTFont('YaHeiBold',r'C:\Windows\Fonts\msyhbd.ttc',subfontIndex=0))
out=root/'演示文稿/请等下一班_v5_会协商的医院.pdf'
c=canvas.Canvas(str(out),pagesize=(1280,720),pageCompression=1)
c.setTitle('请等下一班 · 会协商的医院')
c.setAuthor('思辨设计课程作品')
issues=[]
def wrap(text,font,size,width):
    lines=[]
    for paragraph in text.split('\n'):
        line=''
        for char in paragraph:
            if line and pdfmetrics.stringWidth(line+char,font,size)>width:
                lines.append(line);line=char
            else: line+=char
        lines.append(line)
    return lines
def draw_text(e,page):
    font='YaHeiBold' if e.get('bold') else 'YaHei';size=e['size'];lines=wrap(e['text'],font,size,e['w']);leading=size*1.27
    if len(lines)*leading>e['h']+size*.35:issues.append({'page':page,'text':e['text'],'used':len(lines)*leading,'height':e['h']})
    c.setFont(font,size);c.setFillColor(HexColor(e['color']))
    for i,line in enumerate(lines):c.drawString(e['x'],720-e['y']-size-i*leading,line)
    if e.get('url'):c.linkURL(e['url'],(e['x'],720-e['y']-e['h'],e['x']+e['w'],720-e['y']),relative=0,thickness=0)
for page,s in enumerate(slides,1):
    c.setFillColor(HexColor(s['bg']));c.rect(0,0,1280,720,fill=1,stroke=0)
    for e in s['elements']:
        if e['type']=='text':draw_text(e,page)
        elif e['type']=='image':
            im=ImageReader(e['file']);iw,ih=im.getSize();scale=(max if e['fit']=='cover' else min)(e['w']/iw,e['h']/ih);w,h=iw*scale,ih*scale;x=e['x']+(e['w']-w)/2;y=720-e['y']-e['h']+(e['h']-h)/2
            c.saveState();p=c.beginPath();p.rect(e['x'],720-e['y']-e['h'],e['w'],e['h']);c.clipPath(p,stroke=0,fill=0);c.drawImage(im,x,y,width=w,height=h,mask='auto');c.restoreState()
        elif e['type']=='table':
            rh=e['h']/len(e['rows'])
            for r,row in enumerate(e['rows']):
                x=e['x'];y=e['y']+r*rh
                for col,value in enumerate(row):
                    w=e['widths'][col];c.setFillColor(HexColor('#173D46' if r==0 else '#0A172A'));c.setStrokeColor(HexColor('#30465A'));c.setLineWidth(1);c.rect(x,720-y-rh,w,rh,fill=1,stroke=1)
                    font='YaHeiBold' if r==0 else 'YaHei';lines=wrap(value,font,e['size'],w-32);text_height=len(lines)*e['size']*1.27
                    draw_text({'text':value,'x':x+16,'y':y+(rh-text_height)/2,'w':w-32,'h':rh-6,'size':e['size'],'bold':r==0,'color':'#87F5D7' if r==0 else '#EEF3FF'},page);x+=w
    c.showPage()
c.save()
(base/'pdf-fit-check.json').write_text(json.dumps(issues,ensure_ascii=False,indent=2),encoding='utf-8')
print('PDF pages:',len(slides),'fit concerns:',len(issues))
if issues:print(json.dumps(issues,ensure_ascii=True))
