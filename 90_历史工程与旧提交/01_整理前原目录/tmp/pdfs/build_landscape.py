from pathlib import Path
import re
p=Path('D:/课/大四上/思辨设计/tmp/pdfs/build_report.py')
s=p.read_text(encoding='utf-8')
s=s.replace('W,H=595.276,841.89','W,H=841.89,595.276')
s=s.replace("fontSize=10.2,leading=16","fontSize=10.2,leading=15")
s=s.replace("spaceAfter=20,keepWithNext=True","spaceAfter=14,keepWithNext=True")
s=s.replace("4 if small else 5","3 if small else 5")
s=s.replace("elif len(rows[0])==3:widths=[90,265,CW-355]","elif len(rows[0])==3:widths=[110,390,CW-500]")
s=s.replace('Spacer(1,75)','Spacer(1,25)').replace('Spacer(1,45)','Spacer(1,18)').replace('Spacer(1,38)','Spacer(1,14)').replace('Spacer(1,25)','Spacer(1,14)')
s=s.replace("'第5页流程图＋附录A、B＋工作区原始日志'","'筛选流程页＋附录A、B＋工作区原始日志'")
s=s.replace("'第6-9页12项案例表'","'A-D四类案例表，共12项'").replace("'第6-10页，共四类'","'A-D案例表及分类图，共四类'").replace("'第11-13页，CLARA的可申诉复核记录'","'改进建议：CLARA的可申诉复核记录'")
start=s.index('# Case tables become');end=s.index("new('05  分类与综合发现')",start)
s=s[:start]+'''# Landscape case matrix
groups=[('A','边界辨认','### A类：','### B类：'),('B','澄清协商','### B类：','### C类：'),('C','拒绝表达','### C类：','### D类：'),('D','反馈修正','### D类：','## 五、')]
for letter,title,start,end in groups:
 new(letter+'  '+title,'CASE LIBRARY / 案例表')
 if letter=='A':add('证据标记：F0 未见机器人修正证据；F1 当次调整；F2 后续策略学习；F想 叙事设想。标记不是道德评分。','small')
 part=between(start,end)
 rows=[['编号／来源','场景','具体行为','修养特点','反馈与改进证据']]
 for line in part.splitlines():
  if re.match(r'^\\| C\\d+',line):rows.append([x.strip() for x in line.strip('|').split('|')])
 tab(rows,[151,104,157,149,CW-561])
 reason=re.search(r'\\*\\*归类理由：\\*\\*(.*)',part)
 if reason:add('归类理由：'+reason[1],'body')
 if letter=='C':add('拒绝产生关系效果，并不能证明拒绝理由正确。','quote')

'''+s[end:]
s=s.replace("md('### 记录什么，改变什么\\n'","new('07 / 续  让修正可追溯');md('### 记录什么，改变什么\\n'")
start=s.index("for num,name,file,bbox,caption in [");end=s.index("pagepart('作业要求与资料说明'",start)
s=s[:start]+'''panels=[]
for num,name,file,bbox,caption in [
 (1,'Uninvited Guests','course-76.png',(52,267,741,655),'图1｜Superflux，2015。照护物件进入老人的日常生活。截自课程PDF第76页。'),
 (2,'Our Friends Electric','course-81.png',(107,267,687,655),'图2｜Superflux，2017。三种虚构语音助手。截自课程PDF第81页。')]:
 im=PILImage.open(TMP/file).crop(bbox);dest=TMP/('figure'+str(num)+'.png');im.save(dest);w=350;h=w*im.height/im.width
 panels.append([P(name,'h2'),Image(str(dest),width=w,height=h,hAlign='LEFT'),Spacer(1,10),P(caption,'small')])
t=Table([panels],colWidths=[CW/2,CW/2]);t.setStyle(TableStyle([('VALIGN',(0,0),(-1,-1),'TOP'),('LEFTPADDING',(0,0),(-1,-1),0),('RIGHTPADDING',(0,0),(-1,-1),16)]));story.extend([t,Spacer(1,16)])
add('两张图均为设计虚构作品画面，不用作机器人实际性能的证明。原作者来源见案例C45、C42。','small')
'''+s[end:]
s=s.replace('[(0,14),(14,28),(28,42),(42,63)]','[(0,14),(14,28),(28,42),(42,56),(56,63)]')
s=s.replace('tab(rows,[36,273,CW-309],True)','tab(rows,[40,410,CW-450],True)')
s=s.replace('if off==42:add','if off==56:add')
s=s.replace("tab([['编号／来源','核查范围','证据边界']]+rows,[46,173,CW-219],True)","tab([['编号／来源','核查范围','证据边界']]+rows,[55,270,CW-325],True)")
s=s.replace("pdf=OUT/'作业一_服从的边界.pdf'","pdf=OUT/'作业一_服从的边界_横版.pdf'")
s=s.replace('topMargin=43,bottomMargin=61','topMargin=32,bottomMargin=55')
custom='''
class Diagram(Flowable):
 def __init__(self,kind):Flowable.__init__(self);self.kind=kind;self.width=CW;self.height=245 if kind=='flow' else 120
 def draw(self):
  c=self.canv
  def box(x,y,w,h,title,sub,accent=False):
   c.setFillColor(TEAL if accent else LIGHT);c.roundRect(x,y,w,h,6,fill=1,stroke=0)
   for text,style,yy in [(title,'h2',y+h-32),(sub,'small',y+13)]:
    sty=ParagraphStyle('node',parent=styles[style],alignment=1,textColor=colors.white if accent else INK,fontSize=10 if style=='h2' else 8.4,leading=13)
    p=Paragraph(fmt(text),sty);_,ph=p.wrap(w-16,h);p.drawOn(c,x+8,yy-ph+12)
  if self.kind=='flow':
   bw=(CW-54)/4;gap=18
   nodes=[('探索性网络检索','60条检索式'),('既有候选库与初筛','63项 / 再去重移除0项'),('来源核查与适配性','18项'),('纳入课堂案例','12项 / 研究8 + 设计虚构4')]
   for j,(a,b) in enumerate(nodes):
    x=j*(bw+gap);box(x,147,bw, seventy if False else 70,a,b,j==3)
    if j<3:
     c.setStrokeColor(TEAL);c.line(x+bw,182,x+bw+gap,182);c.line(x+bw+gap,182,x+bw+gap-5,185);c.line(x+bw+gap,182,x+bw+gap-5,179)
   for j,(a,b) in enumerate([('理论／综述10项','单列，不进入案例计数'),('第一轮不纳入45项','范围22 / 代表性16 / 科幻7'),('第二轮不纳入6项','角色重叠或情境匹配较弱')]):
    x=j*(bw+gap);box(x, thirty if False else 30,bw,72,a,b);c.setStrokeColor(LINE);c.line(x+bw/2,147,x+bw/2,102)
  else:
   bw=(CW-36)/4
   vals=[('A 边界辨认','我依据谁的规则？<br/>C14 / C45 / C62'),('B 澄清协商','我是否理解了要求？<br/>C07 / C08 / C42'),('C 拒绝表达','怎样说明不能继续？<br/>C01 / C16'),('D 反馈修正','我为什么改变？<br/>C10 / C29 / C36 / C61')]
   for j,(a,b) in enumerate(vals):box(j*(bw+12),25,bw,90,a,b)
   c.setFont('YH',8.5);c.setFillColor(TEAL);c.drawString(0,7,'反馈使边界得到重审；分类依据为主导行为，每个案例只计一次。')

'''.replace('seventy if False else 70','70').replace('thirty if False else 30','30')
s=s.replace('class Placeholder(Flowable):',custom+'class Placeholder(Flowable):')
exec(compile(s,str(p.with_name('landscape_generated.py')),'exec'))
