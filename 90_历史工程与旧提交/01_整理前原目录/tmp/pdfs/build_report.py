from pathlib import Path
import re,json,html
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import SimpleDocTemplate,Paragraph,Spacer,Table,TableStyle,PageBreak,KeepTogether,Flowable,Image
from PIL import Image as PILImage

ROOT=Path('D:/课/大四上/思辨设计'); TMP=ROOT/'tmp/pdfs'; OUT=ROOT/'output/pdf'; OUT.mkdir(parents=True,exist_ok=True)
pdfmetrics.registerFont(TTFont('YH','C:/Windows/Fonts/msyh.ttc'))
pdfmetrics.registerFont(TTFont('YHB','C:/Windows/Fonts/msyhbd.ttc'))
pdfmetrics.registerFontFamily('YH',normal='YH',bold='YHB',italic='YH',boldItalic='YHB')
W,H=595.276,841.89; M=46; CW=W-2*M
INK=colors.HexColor('#202C32'); TEAL=colors.HexColor('#266F70'); MUTED=colors.HexColor('#67777C'); LIGHT=colors.HexColor('#EDF3F2'); LINE=colors.HexColor('#D6E0DE')
styles={
 'body':ParagraphStyle('body',fontName='YH',fontSize=10.2,leading=16,textColor=INK,spaceAfter=7,wordWrap='CJK'),
 'h1':ParagraphStyle('h1',fontName='YHB',fontSize=23,leading=33,textColor=INK,spaceAfter=20,keepWithNext=True,wordWrap='CJK'),
 'h2':ParagraphStyle('h2',fontName='YHB',fontSize=13,leading=21,textColor=TEAL,spaceBefore=9,spaceAfter=9,keepWithNext=True,wordWrap='CJK'),
 'small':ParagraphStyle('small',fontName='YH',fontSize=8.1,leading=12,textColor=MUTED,spaceAfter=7,wordWrap='CJK'),
 'cell':ParagraphStyle('cell',fontName='YH',fontSize=9,leading=14,textColor=INK,wordWrap='CJK'),
 'tiny':ParagraphStyle('tiny',fontName='YH',fontSize=8.3,leading=12,textColor=INK,wordWrap='CJK'),
 'quote':ParagraphStyle('quote',fontName='YHB',fontSize=12,leading=21,textColor=TEAL,backColor=LIGHT,borderPadding=12,spaceBefore=10,spaceAfter=16,wordWrap='CJK')}
def fmt(s):
 s=html.escape(s.replace('——',' / ').replace('—','-').replace('–','-'))
 s=re.sub(r'\[([^\]]+)\]\((https?://[^)]+)\)',lambda m:'<link href="'+m[2]+'" color="#266F70">'+m[1]+'</link>',s)
 s=re.sub(r'\*\*(.+?)\*\*',r'<b>\1</b>',s)
 return s.replace('&lt;br/&gt;','<br/>')
def P(s,style='body'):return Paragraph(fmt(s),styles[style])
story=[]
def add(s,style='body'):story.append(P(s,style))
def new(title,kicker='RESEARCH / 机器人自我修养'):
 if story:story.append(PageBreak())
 add(kicker,'small');add(title,'h1')
def tab(rows,widths=None,small=False):
 st='tiny' if small else 'cell'; data=[[P(x,st) for x in r] for r in rows]
 t=Table(data,colWidths=widths or [CW/len(rows[0])]*len(rows[0]),repeatRows=1,hAlign='LEFT')
 t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),LIGHT),('VALIGN',(0,0),(-1,-1),'TOP'),('LINEBELOW',(0,0),(-1,0),.8,TEAL),('LINEBELOW',(0,1),(-1,-1),.35,LINE),('LEFTPADDING',(0,0),(-1,-1),8),('RIGHTPADDING',(0,0),(-1,-1),8),('TOPPADDING',(0,0),(-1,-1),4 if small else 5),('BOTTOMPADDING',(0,0),(-1,-1),4 if small else 5)]))
 story.extend([t,Spacer(1,12)])
def md(txt):
 lines=txt.strip().splitlines(); i=0
 while i<len(lines):
  l=lines[i].strip();i+=1
  if not l or l=='---':continue
  if l.startswith('```'):
   while i<len(lines) and not lines[i].startswith('```'):i+=1
   i+=1;continue
  if l.startswith('|'):
   rows=[l.strip('|').split('|')]
   while i<len(lines) and lines[i].strip().startswith('|'):
    z=lines[i].strip().strip('|').split('|');i+=1
    if not all(re.match(r'^\s*:?-+:?\s*$',c) for c in z):rows.append(z)
   rows=[[c.strip() for c in row] for row in rows]
   if len(rows[0])==2: widths=[145,CW-145]
   elif len(rows[0])==3:widths=[90,265,CW-355]
   else:widths=None
   tab(rows,widths);continue
  if l.startswith('### '):add(l[4:],'h2')
  elif l.startswith('## '):add(l[3:],'h1')
  elif l.startswith('> '):add(l[2:],'quote')
  elif l.startswith('- '):add('• '+l[2:])
  else:add(l)

class Diagram(Flowable):
 def __init__(self,kind):Flowable.__init__(self);self.kind=kind;self.width=CW;self.height=390 if kind=='flow' else 222
 def draw(self):
  c=self.canv
  def box(x,y,w,h,title,sub='',accent=False):
   c.setFillColor(TEAL if accent else LIGHT);c.setStrokeColor(LINE);c.roundRect(x,y,w,h,6,fill=1,stroke=0)
   p=Paragraph(html.escape(title),ParagraphStyle('d',fontName='YHB',fontSize=10.5,leading=16,textColor=colors.white if accent else INK,alignment=1,wordWrap='CJK'));_,ph=p.wrap(w-18,h);p.drawOn(c,x+9,y+h-12-ph)
   if sub:
    p=Paragraph(html.escape(sub).replace('&lt;br/&gt;','<br/>'),ParagraphStyle('ds',fontName='YH',fontSize=8.4,leading=12,textColor=colors.white if accent else MUTED,alignment=1,wordWrap='CJK'));_,ph=p.wrap(w-18,h);p.drawOn(c,x+9,y+9)
  def arrow(x,y,x2,y2):
   c.setStrokeColor(TEAL);c.setLineWidth(.9);c.line(x,y,x2,y2)
   c.setFillColor(TEAL);p=c.beginPath();p.moveTo(x2,y2);p.lineTo(x2-3,y2+5);p.lineTo(x2+3,y2+5);p.close();c.drawPath(p,fill=1,stroke=0)
  if self.kind=='flow':
   ys=[336,270,204,138,72,6]
   labels=[('探索性网络检索','60条检索式'),('既有候选库','63项 / 本轮再去重移除0项'),('范围与代表性筛选','63项'),('来源核查与适配性比较','18项'),('纳入课堂案例','12项'),('研究 8项 + 设计虚构 4项','保留反面与边界案例')]
   for j,((a,b),y) in enumerate(zip(labels,ys)):
    box(0,y,290,53,a,b,j==4)
    if j<5:arrow(145,y,145,ys[j+1]+53)
   box(314,336,189,53,'理论／综述10项','单列，不进入案例计数')
   box(314,204,189,60,'不纳入45项','范围22 / 代表性16 / 科幻7')
   box(314,131,189,60,'不纳入6项','角色重叠或情境匹配较弱')
   c.setStrokeColor(LINE)
   for y in [360,229,164]:c.line(290,y,314,y)
  else:
   for j,(letter,title,ids,q) in enumerate([('A','边界辨认','C14 / C45 / C62','我依据谁的规则？'),('B','澄清协商','C07 / C08 / C42','我是否理解了要求？'),('C','拒绝表达','C01 / C16','怎样说明不能继续？'),('D','反馈修正','C10 / C29 / C36 / C61','我为什么改变？')]):
    x=(j%2)*258;y=117-(j//2)*108;box(x,y,245,96,letter+'  '+title,q+'<br/>'+ids)
   c.setFont('YH',8.5);c.setFillColor(TEAL);c.drawString(0,0,'反馈使边界得到重审；分类依据为主导行为，每个案例只计一次。')

class Placeholder(Flowable):
 def __init__(self):Flowable.__init__(self);self.width=CW;self.height=242
 def draw(self):
  c=self.canv;c.setFillColor(colors.HexColor('#F7F9F8'));c.setStrokeColor(LINE);c.setDash(4,3);c.roundRect(0,0,CW,238,8,fill=1,stroke=1);c.setDash()
  for y,s,size in [(142,'待补截图  /  CLARA · Failure Cases',13),(112,'请截“Redbull被识别成Coca-Cola，机器人停止”的画面',10),(89,'保留物品、人物以及识别／拒绝说明，建议使用横向截图',9)]:
   c.setFont('YH',size);c.setFillColor(MUTED);c.drawCentredString(CW/2,y,s)
  c.linkURL('https://clararobot.github.io/',(0,0,CW,238),relative=1)

source=(ROOT/'output/作业1_内容定稿/作业一_服从的边界_完整内容稿.md').read_text(encoding='utf-8')
source=source.replace('第三节流程图＋附录逐项筛选台账＋前轮原始日志','第5页流程图＋附录A、B＋工作区原始日志').replace('第四节12项案例表','第6-9页12项案例表').replace('第四、五节，共四类','第6-10页，共四类').replace('第六节，CLARA的可申诉复核记录','第11-13页，CLARA的可申诉复核记录').replace('第一节题目与研究问题已确定','第1-2页题目与研究问题已确定')
def between(a,b=None):return source.split(a,1)[1].split(b,1)[0] if b else source.split(a,1)[1]
def pagepart(title,a,b):new(title);md(between(a,b))

# Cover
add('SPECULATIVE DESIGN  /  ASSIGNMENT 01','small');story.append(Spacer(1,75))
story.append(Paragraph('服从的边界',ParagraphStyle('cover',fontName='YHB',fontSize=40,leading=54,textColor=INK)))
story.append(Spacer(1,18));add('机器人拒绝之后，<br/>如何解释、接受质疑并修正行为','h1')
story.append(Spacer(1,25));add('建立机器人的自我修养库','h2');add('从“该不该听话”出发，研究可理解、可质疑、可追溯的人机判断。')
story.append(Spacer(1,45));tab([['63 项候选','12 项案例','4 类行为','1 项改进']], [CW/4]*4)
story.append(Spacer(1,38));add('筛选流程 / 案例表 / 分类图 / 改进建议','small');add('探索性案例研究与代表性比较','small');add('资料检索：2026.09.15    整理：2026.09.16','small');add('依据：《作业一》及《思辨设计2026-WEEK01-导论》','small')
pagepart('01  从听话到纠错','## 一、选题缘起：从“该不该听话”到“谁可以纠正判断”','## 二、')
pagepart('02  两本书，两个提问入口','## 二、两本书如何成为研究起点','## 三、')
pagepart('03  资料收集与筛选','## 三、资料收集与筛选','### 3.3')
new('04  筛选流程','METHOD / 参照PRISMA的课堂案例筛选')
add('计数起点是已整理的63项候选，不是搜索引擎的全部网页结果。');story.append(Diagram('flow'));story.append(Spacer(1,16))
add('63 = 45 + 18    /    18 = 6 + 12    /    12 = 8 + 4','h2')
add('原始网页总数及前期合并数未可靠统计，保持未知。本轮63项内未再次移除重复项；这个“0”不代替前期版本去重数。','small')
add('采用代表性抽样，来源核查包括项目说明、摘要和相关正文，未完成全库全文质量评价。由AI辅助整理与编码，尚无第二位独立筛选者；不填写虚构一致率。','small')

# Case tables become consistent vertical records, preserving all five required fields.
groups=[('A','边界辨认','### A类：','### B类：'),('B','澄清协商','### B类：','### C类：'),('C','拒绝表达','### C类：','### D类：'),('D','反馈修正','### D类：','## 五、')]
for letter,title,start,end in groups:
 new(letter+'  '+title,'CASE LIBRARY / 案例表')
 if letter=='A':add('证据标记：F0 未见机器人修正证据；F1 当次调整；F2 后续策略学习；F想 叙事设想。标记不是道德评分。','small')
 part=between(start,end)
 for line in part.splitlines():
  if re.match(r'^\| C\d+',line):
   cells=[x.strip() for x in line.strip('|').split('|')]
   data=[[P(cells[0],'cell'),'']]+[[P(label,'small'),P(value,'cell')] for label,value in zip(['场景','具体行为','修养特点','反馈证据'],cells[1:])]
   t=Table(data,colWidths=[60,CW-60],hAlign='LEFT')
   t.setStyle(TableStyle([('SPAN',(0,0),(-1,0)),('BACKGROUND',(0,0),(-1,0),LIGHT),('VALIGN',(0,0),(-1,-1),'TOP'),('TOPPADDING',(0,0),(-1,-1),4),('BOTTOMPADDING',(0,0),(-1,-1),4),('LEFTPADDING',(0,0),(-1,-1),9),('RIGHTPADDING',(0,0),(-1,-1),9),('LINEBELOW',(0,-1),(-1,-1),.5,LINE)]))
   story.extend([KeepTogether([t]),Spacer(1,10)])
 reason=re.search(r'\*\*归类理由：\*\*(.*)',part)
 if reason:add('归类理由：'+reason[1],'small')
 if letter=='C':
  add('拒绝产生关系效果，并不能证明拒绝理由正确。','quote')

new('05  分类与综合发现');story.append(Diagram('class'));story.append(Spacer(1,15));md(between('### 5.2 从比较中得到的三个发现','## 六、'))
new('06  为误拒绝留下复核通道','DESIGN PROPOSAL / 一项具体改进')
md(between('### 6.1 改进对象与问题','### 6.2'))
story.append(Spacer(1,12));story.append(Placeholder());story.append(Spacer(1,9))
add('图3（待补）｜原案例的失败情境。入口：https://clararobot.github.io/ → Failure Cases。点击图框可打开项目页。','small')
new('07  从质疑到下一次改变');md('### 改进的交互过程\n'+between('### 6.2 改进的交互过程','### 6.3'))
md('### 记录什么，改变什么\n'+between('### 6.3 记录什么，改变什么','### 6.4'))
new('08  思辨价值与评价');md('### 改进为何具有思辨性\n'+between('### 6.4 改进为何具有思辨性','## 七、'));md('### 结论\n'+between('## 七、结论','## 八、'))

# Existing course screenshots, extracted only from the supplied local PDF.
new('图像参照  /  命令关系中的日常物件','VISUAL REFERENCES / 图像来自课程提供材料')
for num,name,file,bbox,caption in [
 (1,'Uninvited Guests','course-76.png',(52,267,741,655),'图1｜Superflux，2015。照护物件进入老人的日常生活。图片截自课程PDF第76页，仅截取作品画面。'),
 (2,'Our Friends Electric','course-81.png',(107,267,687,655),'图2｜Superflux，2017。三种虚构语音助手。图片截自课程PDF第81页，仅截取作品画面。')]:
 add(name,'h2');im=PILImage.open(TMP/file).crop(bbox);dest=TMP/('figure'+str(num)+'.png');im.save(dest);w=380;h=w*im.height/im.width;story.append(Image(str(dest),width=w,height=h,hAlign='LEFT'));add(caption,'small')
add('两张图均为设计虚构作品画面，不用作机器人实际性能的证明。原作者来源见案例C45、C42。','small')
pagepart('作业要求与资料说明','## 八、与作业要求的对应及资料说明','## 九、')
new('课堂分享  /  简述稿');md(between('## 九、课堂简述稿'))
add('阅读导航','h2');add('正文回答研究问题；以下附录保留63项筛选去向、完整检索式及来源核查范围，便于复核。')

records=json.loads((ROOT/'output/作业1_内容定稿/63项筛选台账.json').read_text(encoding='utf-8'))['records']
reasoncodes={}
for r in records:
 if r['stage2']=='纳入内容稿':code='纳入';detail=r['reason'].split('：')[0]
 elif r['stage1']=='进入来源核查':code='二轮不纳入';detail=r['reason']
 else:code='一轮不纳入';detail=r['reason'].split('：')[0]
 reasoncodes[r['id']]=(code,detail)
for off,end in [(0,14),(14,28),(28,42),(42,63)]:
 new('附录A  /  63项候选筛选台账','AUDIT TRAIL / '+str(off+1)+'-'+str(end))
 add('E1 范围偏离（22项）；E2 代表性选择（16项）；E3 商业科幻（7项）。代表性选择不表示研究质量较低。','small')
 rows=[['编号','项目（点击名称打开来源）','去向／理由']]
 for r in records[off:end]:
  code,detail=reasoncodes[r['id']];rows.append([r['id'],'['+r['title']+']('+r['source']+')',code+'；'+detail])
 tab(rows,[36,273,CW-309],True)
 if off==42:add('本轮：63 → 18 → 12。完整逐项文字理由和机器可读台账同步保留于工作区。第二位独立筛选者尚未实施。','small')

querytxt=(ROOT/'output/服从的边界_广泛调研/02_检索方法与筛选记录.md').read_text(encoding='utf-8')
qs=[]
for l in querytxt.splitlines():
 if re.match(r'^\| B\d',l):qs.append([x.strip() for x in l.strip('|').split('|')])
for off in [0,20,40]:
 new('附录B  /  实际检索式','SEARCH LOG / '+str(off+1)+'-'+str(off+20)+' / 2026.09.15')
 add('以下保留原始输入，包括效果不佳的检索式。60是查询数，不能替代文献数或搜索结果数。','small');tab([['编号','检索式']]+qs[off:off+20],[48,CW-48],True)

new('附录C  /  来源核查与证据边界','SOURCE NOTES / 18项来源核查')
audit=(ROOT/'output/作业1_内容定稿/附录_证据核查记录.md').read_text(encoding='utf-8')
rows=[]
for l in audit.splitlines():
 if l.startswith('| [C'):rows.append([x.strip() for x in l.strip('|').split('|')])
tab([['编号／来源','核查范围','证据边界']]+rows,[46,173,CW-219],True)
add('书籍入口见第二节；图像出处见图像参照页。所有链接均可点击打开。未开展用户实验或原型测试。','small')

class NumberedCanvas(canvas.Canvas):
 def __init__(self,*a,**kw):canvas.Canvas.__init__(self,*a,**kw);self.saved=[]
 def showPage(self):self.saved.append(dict(self.__dict__));self._startPage()
 def save(self):
  total=len(self.saved)
  for s in self.saved:
   self.__dict__.update(s);self.setStrokeColor(LINE);self.setLineWidth(.5);self.line(M,44,W-M,44);self.setFont('YH',8);self.setFillColor(MUTED);self.drawString(M,29,'服从的边界  /  作业一');self.drawRightString(W-M,29,f'{self._pageNumber:02d} / {total:02d}');canvas.Canvas.showPage(self)
  canvas.Canvas.save(self)
pdf=OUT/'作业一_服从的边界.pdf'
doc=SimpleDocTemplate(str(pdf),pagesize=(W,H),leftMargin=M,rightMargin=M,topMargin=43,bottomMargin=61,title='服从的边界：机器人的自我修养库',author='课程作业',pageCompression=1)
doc.build(story,canvasmaker=NumberedCanvas)
print(pdf)
