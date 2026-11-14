from pathlib import Path
import re, json, shutil, math
from xml.sax.saxutils import escape
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import Paragraph
from reportlab.lib.utils import ImageReader
from PIL import Image
from pypdf import PdfReader

ROOT=Path(r'D:/课/大四上/思辨设计')
PROJECT=ROOT/'作业二/下一次汇报_剧本与规则/请不要让我永远第一个'
OUT=ROOT/'output/pdf/请不要让我永远第一个_图文剧本'
OUT.mkdir(parents=True,exist_ok=True)
ASSETS=OUT/'图片'; ASSETS.mkdir(exist_ok=True)
GEN=Path(r'C:/Users/22602/.codex/generated_images/01a0dd6f-fc98-7cd3-adc0-e3e188a1d8b6')
files={
 'cast':('exec-6ed6289a-ec56-4bb5-bb66-52ca61c440d2.png','01_人物与材质.png'),
 'splash':('exec-413a8e64-1635-4372-bc1f-1bb6cc3c84f0.png','02_雨后挡水.png'),
 'hall':('exec-a83e5a0a-5890-4066-b988-cb4d67760579.png','03_候梯厅_让行边界修订.png'),
 'climax':('exec-a293e831-76c3-4cc2-96fb-6dc9d689a99d.png','04_两只手_礼遇撤销修订.png'),
 'river':('exec-7135dd86-8480-4503-b94c-6d9b99609bbd.png','05_抄网.png')}
for k,(src,dst) in files.items(): shutil.copy2(GEN/src,ASSETS/dst)
assets={k:ASSETS/v[1] for k,v in files.items()}

source=(PROJECT/'请不要让我永远第一个_v7_积分版完整剧本.md').read_text(encoding='utf-8')
replacements={
 '## v7｜积分版完整剧本：文明不合格':'## v7.1｜图文剧本：文明不合格（让行视觉修订）',
 '另一条鱼绕着行李箱画了一个弧线，像在邀请大家给通路留一点空间。':'几条鱼在行李箱前横向聚成一小簇，停住，摆尾。箱子拉回半步，鱼群就从刚空出的缝隙中穿过，随即散开；脚前没有留下通往电梯的路线。',
 '有人低头看见，笑了笑，把箱子拉回身边。':'箱子的主人低头看见，笑了笑，把箱子再往身边收了一点。',
 '原来散漫、灵活的蓝色小鱼，被公共导引图层编成整齐的金色队列。':'原来会散开的蓝色小鱼，被公共导引图层接管，变成整齐、等距的金色小鱼。它们是贴地的简洁光影，不是悬浮在空中的实体鱼。',
 '它们从四扇门前游过来，围着林遥画出四条“请先行”的路线。':'金色鱼群停在人群鞋尖前，横在他们准备迈步的方向上，形成一条不肯散去的等待边界。人群与电梯之间的通路空着；林遥也停在通路旁。没有鱼线把她牵向任何一部电梯。',
 '有人想迈过去，一条鱼准确地停在他的鞋前。那个人又把脚收回去。':'有人试着向空着的电梯迈步。几条鱼在他鞋尖前聚拢，折折同时合拢一侧扇面，做出“请稍候”的动作。那个人把脚收回去，转头等林遥先走。',
 '公共系统的金色引导线仍然留在地面上。':'公共系统的金色鱼群仍然停在人群鞋尖前，维持着那条等待边界。',
 '地面上的金色光带依次消退。':'人群鞋尖前的金色鱼群散开、熄灭。地面不再留下任何礼遇边界。',
 '**内景／医院普通客梯候梯厅／稍后**':'**内景／医院三楼普通客梯候梯厅／稍后**',
 '本次只处理剧本和美术方向。':'本次图文版只处理剧本、人物与世界观介绍，以及关键分镜。',
}
for a,b in replacements.items():
    assert a in source,a
    source=source.replace(a,b,1)
(OUT/'请不要让我永远第一个_v7.1_完整剧本.md').write_text(source,encoding='utf-8')

pdfmetrics.registerFont(TTFont('YaHei',r'C:/Windows/Fonts/msyh.ttc',subfontIndex=0))
pdfmetrics.registerFont(TTFont('YaHeiB',r'C:/Windows/Fonts/msyhbd.ttc',subfontIndex=0))
pdfmetrics.registerFontFamily('YaHei',normal='YaHei',bold='YaHeiB',italic='YaHei',boldItalic='YaHeiB')
W,H=595.276,841.89
M=43; CW=W-2*M
INK='#263C37'; MUTED='#6B716A'; GOLD='#B38A46'; PLUM='#68434E'; BLUE='#43878E'; PAPER='#FAF7F0'; LINE='#DAD8CF'
styles={
 'body':ParagraphStyle('body',fontName='YaHei',fontSize=10.7,leading=17.2,wordWrap='CJK',textColor=colors.HexColor(INK)),
 'dialog':ParagraphStyle('dialog',fontName='YaHei',fontSize=10.9,leading=17.7,wordWrap='CJK',textColor=colors.HexColor(PLUM)),
 'small':ParagraphStyle('small',fontName='YaHei',fontSize=8.4,leading=13.8,wordWrap='CJK',textColor=colors.HexColor(MUTED)),
 'sub':ParagraphStyle('sub',fontName='YaHeiB',fontSize=12.3,leading=19.5,wordWrap='CJK',textColor=colors.HexColor(INK)),
 'quote':ParagraphStyle('quote',fontName='YaHeiB',fontSize=20,leading=30,wordWrap='CJK',textColor=colors.HexColor(INK)),
 'ui':ParagraphStyle('ui',fontName='YaHei',fontSize=9.3,leading=15.2,wordWrap='CJK',textColor=colors.HexColor(INK)),
}
def rich(s):
    return re.sub(r'\*\*(.*?)\*\*',r'<b>\1</b>',escape(s)).replace('\n','<br/>')

class Book:
    def __init__(self,path):
        self.c=canvas.Canvas(str(path),pagesize=(W,H),pageCompression=1)
        self.c.setTitle('请不要让我永远第一个 | 图文剧本 v7.1')
        self.c.setAuthor('思辨设计课程项目')
        self.c.setSubject('人物设计、主旨、世界观与八场完整剧本；让行光鱼视觉修订')
        self.n=0; self.y=0; self.section=''; self.pages=[]; self.boxes=[]
    def new(self,section,title=None,kicker=None):
        if self.n:self.c.showPage()
        self.n+=1; self.section=section; self.pages.append({'page':self.n,'section':section})
        self.c.bookmarkPage(f'page{self.n}')
        self.c.addOutlineEntry(title or section,f'page{self.n}',level=0,closed=False)
        c=self.c;c.setFillColor(colors.HexColor(PAPER));c.rect(0,0,W,H,fill=1,stroke=0)
        c.setStrokeColor(colors.HexColor(LINE));c.setLineWidth(.6);c.line(M,42,W-M,42)
        c.setFillColor(colors.HexColor(MUTED));c.setFont('YaHei',7.1)
        c.drawString(M,27,'请不要让我永远第一个  /  图文剧本 v7.1')
        c.drawRightString(W-M,27,f'{self.n:02d}')
        if self.n>1:
            c.setFont('YaHei',7.3);c.drawString(M,H-30,'STORY & DESIGN   /   '+section)
            c.drawRightString(W-M,H-30,'2026.09')
        self.y=H-61
        if kicker:self.label(kicker)
        if title:self.title(title)
    def label(self,text):
        self.c.setFont('YaHeiB',8.1);self.c.setFillColor(colors.HexColor(GOLD));self.c.drawString(M,self.y,text);self.y-=20
    def title(self,text):
        self.c.setFont('YaHeiB',23);self.c.setFillColor(colors.HexColor(INK));self.c.drawString(M,self.y-20,text);self.y-=44
    def p(self,text,style='body',x=None,w=None,gap=7,auto=True):
        x=M if x is None else x;w=CW if w is None else w
        p=Paragraph(rich(text),styles[style]);_,h=p.wrap(w,10000)
        if auto and self.y-h<57:
            sec=self.section;self.new(sec,sec+' · 续')
        assert self.y-h>=48,(self.n,text[:50],self.y,h)
        p.drawOn(self.c,x,self.y-h);self.boxes.append((self.n,x,self.y-h,w,h));self.y-=h+gap
        return h
    def sub(self,text):self.p(text,'sub',gap=6)
    def gap(self,h=10):self.y-=h
    def rule(self):
        self.c.setStrokeColor(colors.HexColor(LINE));self.c.line(M,self.y,W-M,self.y);self.y-=17
    def image(self,key,height=None,caption=None):
        im=Image.open(assets[key]);iw,ih=im.size
        h=height or CW*ih/iw;w=h*iw/ih
        if w>CW:w=CW;h=w*ih/iw
        self.c.drawImage(str(assets[key]),M+(CW-w)/2,self.y-h,width=w,height=h)
        self.y-=h+8
        if caption:self.p(caption,'small',gap=10)
    def crop(self,key,x,top,w,h,region):
        # Layout-only clipping of the original image; no raster edits.
        im=Image.open(assets[key]);iw,ih=im.size
        l,t,r,b=region; scale=max(w/((r-l)*iw),h/((b-t)*ih))
        dw,dh=iw*scale,ih*scale
        c=self.c;c.saveState();p=c.beginPath();p.rect(x,top-h,w,h);c.clipPath(p,stroke=0,fill=0)
        c.drawImage(str(assets[key]),x-l*dw,top-h-(1-b)*dh,width=dw,height=dh)
        c.restoreState()
    def note(self,text):
        self.gap(4);self.p('拍摄提示  /  '+text,'small',gap=10)
    def quote(self,text):
        self.gap(10);self.p(text,'quote',gap=16)
    def save(self):self.c.save()

def fish(c,x,y,color=BLUE,size=1):
    c.saveState();c.translate(x,y);c.scale(size,size);c.setStrokeColor(colors.HexColor(color));c.setLineWidth(.9)
    c.ellipse(-6,-2.8,4,2.8,stroke=1,fill=0)
    p=c.beginPath();p.moveTo(4,0);p.lineTo(8,3);p.lineTo(8,-3);p.close();c.drawPath(p,stroke=1,fill=0);c.restoreState()

def fish_diagram(book):
    c=book.c;top=book.y;g=12;bw=(CW-2*g)/3;bh=152
    labels=['01  看见','02  退开','03  放行']
    for i in range(3):
        x=M+i*(bw+g);c.setFillColor(colors.HexColor('#F0EEE6'));c.roundRect(x,top-bh,bw,bh,5,stroke=0,fill=1)
        c.setFillColor(colors.HexColor(INK));c.setFont('YaHeiB',10);c.drawString(x+12,top-20,labels[i])
        c.setFillColor(colors.HexColor('#7A8078'))
        feetx=x+49-(13 if i>0 else 0)
        c.roundRect(feetx,top-71,9,22,4,fill=1,stroke=0);c.roundRect(feetx+14,top-73,9,22,4,fill=1,stroke=0)
        if i<2:
            for j in range(3):fish(c,x+58+j*16,top-88,BLUE,.8)
        else:
            for dx,dy in [(82,-76),(103,-85),(118,-65)]:fish(c,x+dx,top+dy,BLUE,.65)
        c.setStrokeColor(colors.HexColor('#A9B4A2'));c.setDash(2,3);c.line(x+100,top-43,x+100,top-108);c.setDash()
        c.setFont('YaHei',8);c.setFillColor(colors.HexColor(MUTED))
        for j,line in enumerate([['鱼在鞋前停住','吸引低头者注意'],['人或箱子退半步','让出实际通行空间'],['鱼穿过空隙后散开','不留下进梯指引']][i]):c.drawString(x+12,top-127-13*j,line)
    book.y-=bh+15

PDF=OUT/'请不要让我永远第一个_图文剧本_v7.1.pdf'
b=Book(PDF)
b.new('封面')
b.label('SPECULATIVE DESIGN  /  ANIMATED SHORT')
b.gap(8)
b.c.setFillColor(colors.HexColor(INK));b.c.setFont('YaHeiB',37)
b.c.drawString(M,b.y-38,'请不要让我')
b.c.drawString(M,b.y-89,'永远第一个')
b.y-=115
b.p('一座过度礼让的城市。一个只想等朋友的人。','sub',gap=24)
b.image('hall',caption='关键分镜：通路明明空着，所有人却在等她先走。')
b.gap(8)
b.p('城市把机器人的文明积分兑换成主人的优先待遇。老人林遥越礼让，越被安排第一个。为了让她安静地等朋友，她的护理轮椅决定做一件会让自己“不合格”的事。',gap=18)
b.p('人物与世界观  ·  完整剧本  ·  关键分镜\n成人动画 / 荒诞喜剧 / 近未来寓言\nv7.1 图文阅读版 · 2026.09.27','small')

b.new('故事核心','她要的，只是等一会儿','01  THE QUESTION')
b.quote('好的照护，应该容得下\n“我现在不需要”。')
b.p('本片讨论机器人的修养如何在具体关系中形成：它既要有能力主动帮助，也要听懂帮助何时变成负担；当评分与人的处境冲突时，它需要作出判断，并承担判断的后果。')
b.p('林遥没有要摆脱小满。她还需要它挡水、拿抄网、协调开门。她争取的是对自己生活节奏的决定权。')
b.rule()
for title,text in [
 ('世界规则 01｜文明分属于机器人','公共系统为服务机器人评分。达到 90 分可获得“文明示范”资格，并替服务对象触发额外优先。小满开场 95 分，珍惜这枚徽章。'),
 ('世界规则 02｜礼让会换来更多优先','人的礼让由服务设备代为申报，加到设备分上。分数提高，更多设施主动接待；取消接梯预约，不会即时取消资格触发的公共礼遇。'),
 ('世界规则 03｜礼遇可以失去，基本支持照常','资格跌破 90 分，额外礼遇暂停。轮椅通行空间、实际上下梯所需的开门时间、医疗与安全支持继续提供，不与文明分绑定。')]:
    b.sub(title);b.p(text)
b.rule()
b.sub('讽刺如何发生')
b.p('她越说“你们先”，就越被奖励第一个；系统准确记录“暂不出发”，却仍然继续优先；所有人都在等，指标上却显示“等待 0 秒”。虚构系统把礼让时长排除在服务等待统计之外。')
b.p('核心戏发生在普通门诊客梯区。规则为思辨设计虚构，不描述现实电梯系统；急救与病床运输不进入这个喜剧故障。','small')

b.new('人物设计','三个人，三种生活节奏','02  CHARACTERS')
b.image('cast',height=319)
b.p('人物造型参考：陶偶式概括面部、真实织物、带磨损的家电外壳。图中文字为生成草稿，人物与设定以本页正文为准。','small')
for title,text in [
 ('林遥｜72 岁','长期使用轮椅，爱漂亮，略急，钓鱼不服输。紫红针织衫、锈色围巾、银发与眼镜构成识别点。她会享受便利，也会拒绝不合时宜的安排；她先是一个有偏好的人。'),
 ('陈禾｜74 岁','能独立行走的钓友。橄榄绿马甲、渔夫帽、钓竿和饵盒；与林遥有不同轮廓。她会搭把手，也会把鱼放跑。两人是平等的朋友，不预设职业，也不把她写成劝购轮椅的工具。'),
 ('小满｜护理轮椅机器人','一把被认真使用多年的扶手椅，长出工具臂与移动底盘。机灵、护短、爱准备东西，也在意好评。它必须从“把礼遇都接下来”，学会判断对方此刻究竟需要什么。')]:
    b.sub(title);b.p(text)

b.new('机器人设计','有本领，也有自己的脾气','03  ROBOT PERSONALITY')
b.crop('splash',M,b.y,190,219,(0,.06,.43,.94))
saved=b.y
rx=M+208;rw=CW-208
for title,text in [
 ('情绪来自身体','扶手旁的柔性小鳍：得意时立起，受挫时下垂。工具臂的停顿、收纳速度与短促机械声辅助表演，不再加一张人脸。'),
 ('能力有清楚边界','能协助洗脸、刷牙、护肤、收拾钓具、撑伞与支撑；能够记录异常并停止不适动作。补牙交给医生。'),
 ('“自我”通过取舍被看见','开头仔细擦徽章，结尾仍习惯性看它一眼。失去资格是它在意的损失；影片保留对其主观意识的开放问题。')]:
    b.p(title,'sub',x=rx,w=rw);b.p(text,x=rx,w=rw,gap=12)
b.y=min(b.y,saved-333)
b.rule()
b.sub('同一个城市，不同的机器人形态')
for title,text in [
 ('折折 / 医院礼仪机器人','细长立柱和两片折扇。展开表示邀请，侧合表示稍候。礼貌认真，越想服务好，越把空间安排得满满当当。'),
 ('阿团 / 排水机器人','低矮圆盘、胡须般的刷毛和短鼻吸水管。动作忙碌、有点笨拙；负责把宏大的自动化城市里那一小摊水吸干。'),
 ('电梯与自动驾驶车 / 环境里的角色','电梯以门缝、楼层灯和提示音回应；车用车尾屏幕表达感谢。它们不必都长出四肢与脸。')]:
    b.p('**'+title+'**\n'+text)
b.p('设计原则：情绪器官不干扰制动与身体支撑；无障碍支持不成为文明评分的奖品。','small')

b.new('美术与光鱼','让行，必须通过人的动作读出来','04  VISUAL LANGUAGE')
b.p('全片采用有手工痕迹的风格化三维动画。奶油白与灰绿的城市、陶土式人物、织物与旧物，叠加精确的二维评分图形。空间始终友好、明亮，压迫发生在服务行为中。')
fish_diagram(b)
b.sub('公共系统接管以后：边界不再散开')
b.image('hall',height=250,caption='修订分镜：小鱼缩成脚边的简洁光影；中央通道保持空白。人群的退步、停顿和目光共同完成“让行”。')
b.p('蓝色：小满当日钓鱼主题的私人投影，短暂提示，得到回应就收回。金色：公共系统接管的礼遇图层，停在人群脚前，持续要求大家等待。颜色之外，还要改变聚散方式和人的反应。')
b.p('删去四条指向电梯的鱼形路线，避免“导航进梯”的误读。小鱼只贴在地面上，不做悬浮实体，不用密集鱼鳞抢走人物表演。','small')

body=source.split('## 二、完整剧本',1)[1].split('## 三、',1)[0]
raw_scenes=re.split(r'(?m)^### ',body)[1:]
assert len(raw_scenes)==8

def parse_scene(raw):
    lines=raw.strip().splitlines();title=lines[0].strip();setting=lines[1].strip('* ')
    body='\n'.join(lines[2:]).strip()
    blocks=[p.strip() for p in re.split(r'\n\s*\n',body) if p.strip() and p.strip()!='---']
    parsed=[];stage=[]
    def flush():
        if stage:parsed.append(('body',''.join(stage)));stage.clear()
    for block in blocks:
        if block=='---':continue
        m=re.match(r'^\*\*([^*]+)\*\*\s*\n(.+)$',block,re.S)
        if m:
            flush();parsed.append(('dialog','**'+m.group(1)+'**　'+m.group(2).strip().replace('\n','')))
        elif block.startswith('>'):
            flush();parsed.append(('ui','\n'.join(l.lstrip('> ').strip() for l in block.splitlines())))
        else:
            t=block.replace('\n','')
            if sum(map(len,stage))+len(t)>115:flush()
            stage.append(t)
    flush()
    return title,setting,parsed

scene_images={3:('splash','关键分镜 01｜它挡住了水，也没忍住脾气。'),5:('hall','关键分镜 02｜四扇门都开着，大家却越来越走不了。'),6:('climax','关键分镜 03｜评分看见了一根手指，观众看见两只手。'),8:('river','关键分镜 04｜人决定往哪里抄，机器人托住重量。')}
scene_notes={
 1:'从城市全景进入机器人的小动作，再进入家庭。给分提示音接成洗漱声，把宏观规则接到生活。',
 2:'先呈现小满确实能干，再让它在补牙上承认局限。蓝鱼来自今天的钓鱼安排，徽章来自它自己的在意。',
 3:'先挡水，后手势，再取证；三件事各有节拍。保护与泄愤不能在一个瞬间糊成同一个动作。',
 4:'先看见鞋、鱼和行李箱的互动，再切回全景。轮椅已经停在侧边；让路成功后，投影应当散开。',
 5:'四扇门依次累积，不在第一个镜头全部打开。“请您先行”保持温柔，林遥的尴尬逐渐加重。',
 6:'先拍完整的两只手，再切评分端的局部框选。此处不放胜利配乐；扣分提示音依然愉快。',
 7:'这一场不能省。礼遇撤销后，延长开门仍然有效，观众才能看懂她争取的是什么。',
 8:'抄网递到林遥手里，她决定方向，小满承担重量。鱼跑掉后不补一个胜利结局，让她们继续过日子。'}

scene_pages=[]
for idx,raw in enumerate(raw_scenes,1):
    title,setting,blocks=parse_scene(raw)
    sec=f'{idx:02d}  '+title.split('　',1)[-1]
    b.new(sec,title.split('　',1)[-1],f'SCENE {idx:02d}  /  完整剧本')
    scene_pages.append({'scene':idx,'title':title,'start':b.n})
    b.p(setting,'small',gap=15)
    if idx in scene_images:
        key,cap=scene_images[idx];b.image(key,height=248,caption=cap)
    if idx==1:
        b.quote('文明，让生活更快一点。')
    if idx==7:
        b.p('资格失去以后，照护仍然继续。','sub',gap=17)
    for typ,txt in blocks:
        if typ=='ui':
            b.p('系统显示  /  '+txt,'ui',gap=9)
        elif typ=='dialog':
            b.p(txt,'dialog',x=M+17,w=CW-27,gap=9)
        else:b.p(txt,'body',gap=8)
    b.note(scene_notes[idx])
    scene_pages[-1]['end']=b.n

b.new('创作说明','小满究竟学会了什么','05  ACTION / FEEDBACK / CHANGE')
b.p('故事的变化落在具体行为上：先享受好评，再看见礼遇造成的负担，尝试撤回，承担差评，最后继续提供合适的帮助。它没有变成一个事事请示、什么都不敢做的机器人。')
for title,text in [
 ('承认局限','牙齿不适时立即停下护理，说明补牙需要医生。能干不等于无所不能。'),
 ('尊重意愿','听见“我等个人”，撤销接梯请求、收回私人投影；最终让她能够安静地等待。'),
 ('纠正自己的参与','小满承认自己也接入了多余礼遇。它调整行动，释放公共空间，而不是只说一句抱歉。'),
 ('合理拒绝与承担后果','它拒绝公共评分端的纠正，失去珍视的示范资格。这一选择有具体理由，也保留被观众质疑的余地。'),
 ('继续承担照护责任','普通乘梯时延长开门；河边递抄网、托重量、调整伞。自主权与有效帮助同时成立。')]:
    b.sub(title);b.p(text)
b.rule()
b.sub('两个相同的手势，两次不同的判断')
b.p('路边：愤怒、快速、被提醒后收回。\n医院：先尝试正常退出，观察他人负担，再主动承担资格损失。另一只手同时照护林遥。')
b.p('讽刺对象是把修养压缩为可见动作和分数的制度。最后的手势是这个虚构困境中的争议性选择，不是“粗鲁就正确”的普遍结论。','small')

b.new('汇报与制作边界','这一版定下什么，还要验证什么','06  DIRECTOR DISCUSSION')
b.sub('本次已修订')
b.p('① 光鱼从进梯路线改为脚前让行提示，并在公共接管后形成等待边界。\n② 候梯厅统一为三楼，支撑补牙后下楼去河边的行程。\n③ 85 分的高潮图撤去金色投影，让资格失效与通行恢复一致。\n④ 保留完整八场对白与动作，补入人物、世界规则及修养行为说明。')
b.sub('最需要导演检验的三件事')
b.p('四部电梯的累积能否一眼看懂：先 A，礼让后 B，满分后 C、D；如果仍然费解，减成两三部，保留因果。\n小满失去徽章是否让人有感觉：靠开头擦拭、中间犹豫、结尾习惯性回望支撑，不追加停机或报废的新危机。\n林遥是否始终是行动者：她选择口红、说明等待、要求保留开门支持、判断是否制止小满，并决定如何抄网。')
b.sub('片长与完成度')
b.p('暂按 5 至 6 分钟进行讨论，尚未通过对白试读或动态分镜验证。课程任务写明约 3 分钟视频，创作讨论稿暂按更长版本推进；最终提交时长仍需与教师确认。剧本已安排不少于三项可观察修养行为及反馈调整过程。')
b.p('此 PDF 是图文剧本，不等于完成整项作业。AI 成片、可运行交互原型、真实案例依据及实现边界说明，仍属于后续交付。','small')
b.rule()
b.sub('图像与文本使用说明')
b.p('正文承接项目内 v7 积分版完整剧本，v7.1 只修订让行视觉及相关连续性。现有角色与关键场景由 OpenAI 图片生成工具创作，本次用内置图片工具修订候梯厅及高潮两张图；三步让行示意为程序绘制。PDF 使用 ReportLab 排版。')
b.p('关键分镜用于明确构图、表演关系与美术方向，不是逐帧连续镜头。原始图像约 1.5K 至 1.7K 宽，文档内保留原图清晰度，不标称 4K。前期片例讨论不替代真实机器人案例论证。','small')
b.p('本版暂缓视频生成。下一轮先把“看见—退开—放行”拆成可验证的镜头，再确定图生视频动作提示与剪辑。','small')
b.save()

reader=PdfReader(str(PDF));texts=[p.extract_text() or '' for p in reader.pages];joined='\n'.join(texts)
for phrase in ['抄网！这还用问！','可我只是想等个人。','本次不改正。','别计时啊。','文明礼遇自动生效。','先让他们走。','这个得找医生。']:
    assert phrase in joined,phrase
assert len(reader.pages)==b.n
assert all(t.strip() for t in texts)
# All screenplay dialogue blocks should remain present in PDF text.
dialogue_count=0
for raw in raw_scenes:
    _,_,blocks=parse_scene(raw)
    for kind,t in blocks:
        if kind=='dialog':
            speech=re.sub(r'^\*\*[^*]+\*\*\s*','',t)
            assert re.sub(r'\s','',speech) in re.sub(r'\s','',joined),speech
            dialogue_count+=1
checks={'pdf':str(PDF),'pages':b.n,'scene_pages':scene_pages,'dialogue_blocks_verified':dialogue_count,'page_characters':[len(t) for t in texts],'images':{k:{'file':str(v),'size':Image.open(v).size} for k,v in assets.items()},'layout_bounds_checked':True}
(Path(__file__).parent/'checks.json').write_text(json.dumps(checks,ensure_ascii=False,indent=2),encoding='utf-8')
(OUT/'阅读说明.md').write_text('# 《请不要让我永远第一个》图文剧本 v7.1\n\nPDF 为主要阅读文件。完整剧本文字保留在同目录 Markdown 中，图片已复制到“图片”子目录。\n\n本次修订：光鱼改为脚前让行边界；医院三楼连续性；资格撤销后的投影熄灭。原 v7 文件未覆盖。\n\n文档包含主旨、世界观、人物和机器人设计、完整八场剧本、关键分镜与导演讨论事项。视频制作暂缓。\n',encoding='utf-8')
print(json.dumps(checks,ensure_ascii=True,indent=2))
