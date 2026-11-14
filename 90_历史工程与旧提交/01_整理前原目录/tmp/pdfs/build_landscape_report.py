from pathlib import Path
import re,json,shutil,math
from xml.sax.saxutils import escape
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import Paragraph
from PIL import Image
from pypdf import PdfReader

ROOT=Path(r'D:/课/大四上/思辨设计')
OUT=ROOT/'output/pdf/请不要让我永远第一个_横版汇报'
OUT.mkdir(parents=True,exist_ok=True)
PIC=OUT/'图片';PIC.mkdir(exist_ok=True)
TMP=ROOT/'tmp/pdfs/landscape-report';TMP.mkdir(exist_ok=True)
OLD=ROOT/'output/pdf/请不要让我永远第一个_图文剧本'
CLIP=ROOT/'output/医院16秒试片_四镜头素材包/图片'
GEN=Path(r'C:/Users/22602/.codex/generated_images/01a0dd6f-fc98-7cd3-adc0-e3e188a1d8b6')
mapping={
 'cast':OLD/'图片/01_人物与材质.png',
 'splash':OLD/'图片/02_雨后挡水.png',
 'climax':OLD/'图片/04_两只手_礼遇撤销修订.png',
 'river':OLD/'图片/05_抄网.png',
 'hall':CLIP/'01_候梯厅全景.png',
 'lin':CLIP/'02_林遥中景_动作前.png',
 'passenger':CLIP/'03_乘客与折折_动作前.png',
 'waiting':CLIP/'04_全景_互相等待.png',
 'city':GEN/'exec-0069515c-67ae-41f8-96b8-0e8c6cbcba3b.png',
 'home':GEN/'exec-2143777b-100b-4752-b68b-1514f58c07bc.png',
 'blue':GEN/'exec-20cbdf57-422d-4876-ab24-f1fa13e5808b.png',
 'boarding':GEN/'exec-b24631d5-8245-43d0-abbc-ad9b5e45253d.png'}
assets={}
for key,src in mapping.items():
    dst=PIC/(key+'.png');shutil.copy2(src,dst);assets[key]=dst
pdfmetrics.registerFont(TTFont('CN',r'C:/Windows/Fonts/msyh.ttc',subfontIndex=0))
pdfmetrics.registerFont(TTFont('CNB',r'C:/Windows/Fonts/msyhbd.ttc',subfontIndex=0))
pdfmetrics.registerFontFamily('CN',normal='CN',bold='CNB',italic='CN',boldItalic='CNB')
W,H=1280,720
INK='#273F39';MUTED='#71796F';GOLD='#AD8347';PLUM='#714D5A';BLUE='#477D88';PAPER='#FAF7F0';LINE='#DCDACF'
def rich(t):return re.sub(r'\*\*(.*?)\*\*',r'<b>\1</b>',escape(t)).replace('\n','<br/>')
class Deck:
    def __init__(self):
        self.path=OUT/'请不要让我永远第一个_16比9横版汇报.pdf'
        self.c=canvas.Canvas(str(self.path),pagesize=(W,H),pageCompression=1)
        self.c.setTitle('请不要让我永远第一个｜思辨设计汇报')
        self.c.setAuthor('思辨设计课程作品')
        self.c.setSubject('概览、人物设定、场景设定、关键分镜、机器人修养与完整剧本')
        self.n=0;self.notes=[];self.rects=[];self.script_start=None
    def page(self,section,title,note,sub=None):
        if self.n:self.c.showPage()
        self.n+=1;c=self.c
        c.setFillColor(colors.HexColor(PAPER));c.rect(0,0,W,H,fill=1,stroke=0)
        c.setFillColor(colors.HexColor(GOLD));c.setFont('CNB',12);c.drawString(48,681,section)
        c.setFillColor(colors.HexColor(MUTED));c.setFont('CN',10);c.drawRightString(1232,682,'思辨设计 / 设计有修养的机器人')
        c.setStrokeColor(colors.HexColor(LINE));c.setLineWidth(.65);c.line(48,42,1232,42)
        c.setFillColor(colors.HexColor(MUTED));c.setFont('CN',10);c.drawString(48,24,'请不要让我永远第一个');c.drawRightString(1232,24,f'{self.n:02d}')
        self.text(title,48,642,1184,34,46,bold=True)
        if sub:self.text(sub,48,587,1184,17,26,color=MUTED)
        c.bookmarkPage(f'p{self.n}');c.addOutlineEntry(title,f'p{self.n}',level=0,closed=False)
        self.notes.append({'page':self.n,'section':section,'title':title,'speech':note})
    def text(self,t,x,top,w,size=22,leading=None,bold=False,color=INK):
        st=ParagraphStyle('p',fontName='CNB' if bold else 'CN',fontSize=size,leading=leading or size*1.55,wordWrap='CJK',textColor=colors.HexColor(color),splitLongWords=True)
        p=Paragraph(rich(t),st);_,h=p.wrap(w,10000)
        assert top-h>=50,(self.n,t[:35],top,h)
        assert x>=0 and x+w<=W,(x,w)
        p.drawOn(self.c,x,top-h);self.rects.append((self.n,x,top-h,w,h));return top-h
    def image(self,k,x,top,w,h,region=None,contain=True):
        im=Image.open(assets[k]);iw,ih=im.size;c=self.c
        if region:
            l,t,r,b=region;rw=(r-l)*iw;rh=(b-t)*ih
            scale=min(w/rw,h/rh) if contain else max(w/rw,h/rh)
            bx=x+(w-rw*scale)/2;by=top-h+(h-rh*scale)/2
            c.saveState();p=c.beginPath()
            if contain:p.rect(bx,by,rw*scale,rh*scale)
            else:p.rect(x,top-h,w,h)
            c.clipPath(p,fill=0,stroke=0)
            c.drawImage(str(assets[k]),bx-l*iw*scale,by-(1-b)*ih*scale,width=iw*scale,height=ih*scale);c.restoreState()
        else:
            sc=min(w/iw,h/ih);dw,dh=iw*sc,ih*sc
            c.drawImage(str(assets[k]),x+(w-dw)/2,top-dh-(h-dh)/2,width=dw,height=dh)
    def box(self,x,top,w,h,color='#EEEDE4'):
        self.c.setFillColor(colors.HexColor(color));self.c.roundRect(x,top-h,w,h,9,fill=1,stroke=0)
    def bullets(self,items,x,top,w):
        y=top
        for head,body in items:
            y=self.text(head,x,y,w,24,35,bold=True)-9
            y=self.text(body,x,y,w,20,31)-28
        return y
    def shot(self,no,title,img,place,story,line,note):
        def wrap_story(value,size):
            lines=[]
            for raw in value.split('\n'):
                current=''
                for ch in raw:
                    if current and pdfmetrics.stringWidth(current+ch,'CN',size)>350:
                        carry=''
                        while current and ((ch in '，。！？；：、）》”’％%' and not carry.strip('，。！？；：、）》”’％%')) or current[-1] in '（《“‘' or (ch.isdigit() and current[-1].isdigit())):
                            carry=current[-1]+carry;current=current[:-1]
                        lines.append(current);current=carry+ch
                    else:current+=ch
                if current:lines.append(current)
            return '\n'.join(lines)
        self.page('04 / 故事分镜',f'{no:02d}  {title}',note,sub=place)
        self.image(img,48,540,794,447)
        y=539
        for paragraph in story:
            y=self.text(wrap_story(paragraph,21),882,y,350,21,32)-17
        y-=8
        self.text(wrap_story(line,22),882,y,350,22,34,color=PLUM)
    def save(self):self.c.save()

d=Deck()
d.page('01 / 作品概览','请不要让我永远第一个','老师好，我的故事叫《请不要让我永远第一个》。它发生在一座过度礼让的城市：一位老人只是想等朋友，城市却坚持让她第一个走。我想通过这件小事，讨论一个机器人怎样从追求好评，走向理解具体的人。')
d.text('一座过度礼让的城市',48,542,330,31,45,bold=True)
d.text('一个只想等朋友的人',48,473,330,25,39)
d.text('成人动画\n荒诞喜剧\n近未来寓言',48,370,320,20,34,color=MUTED)
d.image('waiting',412,580,820,461)
d.text('林遥的一个普通日子，变成了小满第一次主动承担差评的日子。',48,100,1160,19,29)

d.page('01 / 作品概览','一个人想等待，城市却不断奖励她不用等待','故事的起点很日常：林遥准备补完牙，和朋友陈禾去钓鱼。医院里，她等陈禾洗手，顺口说了一句“你们先”。城市把这个动作识别为文明礼让，反而给她追加了优先待遇。越礼让，越被安排第一个。最后，小满为了让大家正常通行，主动放弃了自己珍视的文明资格。')
d.text('城市把机器人的文明积分，兑换成服务对象的优先待遇。\n为了让主人安静地等朋友，护理轮椅决定做一件会让自己“不合格”的事。',48,556,1165,29,45)
for i,(n,t,desc) in enumerate([('01','日常出行','护理、补牙、约钓鱼'),('02','礼遇失控','她越礼让，越被优先'),('03','重新判断','失去资格，继续照护')]):
    x=48+i*404;d.box(x,365,376,220);d.text(n,x+22,343,330,17,25,color=GOLD,bold=True);d.text(t,x+22,302,330,28,40,bold=True);d.text(desc,x+22,233,330,21,33)

d.page('01 / 作品概览','帮助何时变成了替人决定？','这部片想追问的不是机器人该不该帮人，而是人在接受帮助之后，还有没有改变主意的余地。林遥依然喜欢小满，也需要它能干。冲突在于，系统只看见“她值得优先”，却没有给“她现在不走”留下位置。小满的成长发生在这两个判断之间。')
d.text('“可我只是想等个人。”',65,531,1130,49,70,bold=True,color=PLUM)
d.text('林遥需要照护，也需要决定自己何时出发。',67,420,1110,29,44)
for i,(a,b) in enumerate([('人的意愿','可以拒绝、暂停、改变主意'),('他人的处境','礼遇不能把等待转嫁给别人'),('机器人的判断','把反馈转化为下一次行动')]):
    x=65+i*404;d.text(a,x,286,365,25,38,bold=True);d.text(b,x,229,350,22,35)

d.page('02 / 人物设定','三个人，三种生活节奏','故事的核心关系是林遥、她的护理轮椅小满，以及她的钓友陈禾。林遥是被服务的人，也是有脾气和偏好的人。小满既能干又护短，还很看重自己的文明徽章。陈禾能够走路，她和林遥之间是朋友关系，会互相搭把手，也会互相调侃。')
d.image('cast',48,583,786,520)
d.bullets([('林遥 / 72 岁','爱漂亮，急脾气，钓鱼不服输。'),('小满 / 护理轮椅','机灵、护短，也珍惜自己的好评。'),('陈禾 / 74 岁','能独立行走的钓友，说话直接。')],880,567,350)

d.page('02 / 人物设定','林遥：她先是一个有主意的人','我不希望林遥只作为一个需要帮助的对象出现。她会挑口红，会享受小满的照顾，也会嫌它反应慢。她今天的目标只是补牙和钓鱼，所以主旨尽量通过她的选择和情绪出现，不让她承担一段解释尊严的演讲。')
d.image('lin',48,572,748,420)
d.bullets([('想要什么','补好牙，和朋友钓鱼。'),('如何行动','选口红、说明等待、决定抄网方向。'),('如何识别','银发、眼镜、紫红针织衫与锈色围巾。')],840,572,380)
d.text('“先让他们走。等我们真上去了，门你还是得替我留着。”',48,110,1150,24,37,color=PLUM)

d.page('02 / 人物设定','小满：把事情准备好，也想被表扬','小满像一把使用多年的家用扶手椅，带有两只可收纳工具臂。它不需要完整的人脸，情绪通过小鳍、工具动作和机械声表达。它能协助刷牙洗脸、收纳钓具和撑伞，但不会补龋齿。开头擦亮徽章这个动作，说明好评对它有意义，后面失去资格才有重量。')
d.image('home',48,568,710,400)
d.bullets([('能做','日常护理、收纳、撑伞、出行协调。'),('知道边界','牙齿不适就停下；补牙交给医生。'),('表达感受','小鳍起落、工具停顿、擦亮徽章。')],804,569,420)
d.text('它从“把礼遇都接下来”，走向“判断此刻需要什么”。',48,109,1140,25,39,bold=True)

d.page('02 / 人物设定','同行的人，与城市里的机器人','陈禾是林遥的朋友，她们会互相照应，也会互相调侃。城市里的机器人则像不同的生活器物：折折像一张移动的请柬，靠扇面表达邀请和稍候；阿团是低矮的排水圆盘，忙着追赶水洼。电梯和车通过门、灯和屏幕说话。它们都在认真服务，问题来自这些认真执行的规则怎样相互叠加。')
d.image('boarding',48,570,272,360,region=(.60,.015,.84,.96))
d.image('passenger',413,570,250,360,region=(.282,.285,.475,.895))
d.image('city',813,535,350,270,region=(.19,.49,.38,.79))
for x,head,body in [(48,'陈禾 / 同行的人','自己带钓具，有自己的主意。'),(413,'折折 / 礼仪引导','展开是邀请，侧合是稍候。'),(813,'阿团 / 排水机器人','短鼻吸水，动作忙碌而笨拙。')]:
    d.text(head,x,194,365,23,34,bold=True);d.text(body,x,143,365,20,31)

d.page('03 / 世界与场景','文明分，怎样变成了空间里的优先权？','这套世界只需要理解三条规则。首先，文明分评的是机器人，高分会带来额外礼遇。其次，礼让会加分，而公共设施根据资格自动响应，取消预约也不等于取消礼遇。最后，资格失效只取消额外便利，基本无障碍支持照常。把这条边界讲清楚，才不会把林遥的脱困写成放弃应有的帮助。')
for i,(n,head,body) in enumerate([('95','文明示范','机器人达到90分，替服务对象获得额外优先。'),('100','越礼让，越优先','取消接梯请求，公共认证仍触发即时礼遇。'),('85','资格暂停','额外礼遇撤销；通行、安全与开门支持继续。')]):
    x=48+i*404;d.box(x,563,376,386);d.text(n,x+24,528,326,68,85,color=GOLD,bold=True);d.text(head,x+24,402,326,27,41,bold=True);d.text(body,x+24,333,326,23,37)
d.text('虚构制度：没有即时退出的礼遇，制造了无法拒绝的优先。',48,124,1170,22,34,color=PLUM)

d.page('03 / 世界与场景','今天的安排：先补牙，再和陈禾钓鱼','这一天的行程很简单。林遥早晨在家接受护理，准备去医院补牙，陈禾约她补完牙去钓鱼。小满带好钓具，载着她穿过雨后的街道。补牙结束，陈禾来到医院会合，却因为鱼饵漏在手上，临时去洗手间清洗。林遥因此停在三楼候梯厅等她，故事的主要冲突就发生在这几分钟里。等候梯厅恢复正常，两人才一起下楼，去河边钓鱼。')
for i,(key,title,desc) in enumerate([('home','家 / 清晨','护理、约钓鱼、备钓具'),('city','街道 / 雨后','赴口腔科途中遭遇溅水'),('hall','医院 / 三楼','补完牙，等陈禾洗手'),('river','河边 / 午后','两人会合，一起钓鱼')]):
    x=48+i*304;d.image(key,x,553,272,180);d.text(title,x,335,275,25,38,bold=True);d.text(desc,x,271,270,21,33)
d.text('家 → 医院 → 河边',48,158,1150,34,49,bold=True)
d.text('林遥想等陈禾一起下楼；文明系统却坚持让她立刻先走。',48,100,1150,20,31,color=MUTED)

d.page('03 / 世界与场景','医院：通路空着，人却被礼貌留在原地','候梯厅的空间关系很重要。林遥停在侧边，并没有挡路；其他人站在另一边，四部电梯在后方。中间留出明显的空地，观众就能看见：阻止通行的是礼遇规则和人的回应，而不是轮椅的物理占位。这里限定为普通门诊客梯，急救不进入这场喜剧。')
d.image('waiting',48,571,820,463)
d.bullets([('林遥在侧边','她没有挡住别人的通道。'),('电梯依次到齐','A、B、C、D 逐渐累积礼遇。'),('他人主动停步','目光、扇面和脚前光影组织等待。')],906,570,320)

d.page('03 / 世界与场景','光鱼：从轻松交流，到不肯散去的等待','光鱼来自今天的钓鱼计划。最初，小满用蓝色小鱼吸引低头者的注意：箱子移开，鱼就散开。公共系统接管之后，鱼变成金色，在人脚前持续停留。它不是导航箭头，也不是实体路障；人看见提示、退半步，才让这个交流成立。')
d.image('blue',48,570,565,318);d.image('passenger',667,570,565,318)
d.text('蓝色 / 得到回应，就收回',48,220,565,27,40,bold=True,color=BLUE)
d.text('看见 → 退开 → 放行',48,155,565,23,36)
d.text('金色 / 持续要求别人等待',667,220,565,27,40,bold=True,color=GOLD)
d.text('被看见 → 被安排 → 无法退出',667,155,565,23,36)

shots=json.loads((ROOT/'tmp/pdfs/storyboard_report_copy.json').read_text(encoding='utf-8'))
for i,(title,img,place,story,line,note) in enumerate(shots,1):d.shot(i,title,img,place,story,line,note)

d.page('05 / 机器人的修养','把反馈，变成下一次更合适的帮助','这部片用四类可观察的行为呈现修养。小满承认补牙的局限，尊重林遥暂不出发的意愿，承认自己也接入了多余礼遇，并在有理由的情况下拒绝系统要求、承担损失。最重要的验证在后面：它仍然会留门、撑伞、托抄网。它的修养不是停留在一句正确的回答，而是体现在下一次怎么做。')
items=[('承认局限','停下不适的护理，把补牙交给医生。'),('尊重意愿','取消预约，收回自己的邀请，容许等待。'),('纠正错误','承认自己接入了多余礼遇，释放他人通行。'),('合理拒绝','基于现场后果承担差评，照护责任继续。')]
for i,(head,body) in enumerate(items):
    x=48+(i%2)*610;top=561-(i//2)*210;d.box(x,top,574,180);d.text(head,x+24,top-22,526,28,41,bold=True);d.text(body,x+24,top-84,526,22,34)
d.text('获得反馈 → 调整判断 → 承担后果 → 在生活中再次验证',48,110,1180,24,37,color=PLUM,bold=True)

# The final section is entirely text. Preserve every stage direction and dialogue from the screenplay.
source=(OLD/'请不要让我永远第一个_v7.1_完整剧本.md').read_text(encoding='utf-8')
body=source.split('## 二、完整剧本',1)[1].split('## 三、',1)[0]
raw_scenes=re.split(r'(?m)^### ',body)[1:]
assert len(raw_scenes)==8
d.script_start=d.n+1
d.page('06 / 完整剧本','请不要让我永远第一个','前面是故事和设计的主要介绍。后面附上完整八场剧本，保留动作、对白、声音和场景衔接，方便老师进一步讨论具体的叙事节奏。')
d.text('完整剧本',48,520,1150,54,75,bold=True)
d.text('八场 / 成人动画 / 荒诞喜剧 / 近未来寓言',48,406,1150,25,40)
d.text('城市已经替你准备好了\n今天的鱼\n第一次竖起中指\n鱼把路让出来',48,312,548,23,43)
d.text('你越客气，越不能等\n文明不合格\n这次真的上电梯\n抄网',686,312,548,23,43)

scene_map=[];all_blocks=[]
def parse(raw):
    ls=raw.strip().splitlines();title=ls[0];setting=ls[1].strip('* ')
    blocks=[x.strip() for x in re.split(r'\n\s*\n','\n'.join(ls[2:])) if x.strip() and x.strip()!='---']
    out=[];stage=[]
    def flush():
        if stage:out.append(('stage',''.join(stage)));stage.clear()
    for item in blocks:
        m=re.match(r'^\*\*([^*]+)\*\*\s*\n(.+)$',item,re.S)
        if m:flush();out.append(('dialog','**'+m.group(1)+'**　'+m.group(2).strip().replace('\n','')))
        elif item.startswith('>'):flush();out.append(('screen','\n'.join(t.lstrip('> ').strip() for t in item.splitlines())))
        else:
            t=item.replace('\n','')
            if sum(map(len,stage))+len(t)>105:flush()
            stage.append(t)
    flush();return title,setting,out

scene_speeches=[
 ('故事从雨后的城市开始。机器人相互让行、清理积水，文明行为会换来积分和通行便利。镜头最后进入林遥家的窗户，接到她的清晨护理。',''),
 ('林遥今天约了口腔科，陈禾又约她补完牙钓鱼。小满替她备好钓具，用蓝色小鱼作为今天的投影。它擦亮95分的徽章，和林遥一起出门。',''),
 ('去医院途中，自动驾驶车溅起水花。小满及时撑伞，也因为朝车竖起中指被扣分。林遥让它收手、留下举报证据，两人继续赶往医院。',''),
 ('补牙结束后，陈禾来医院会合，因为鱼饵弄脏了手，先去洗手间。林遥在候梯厅侧边等她。电梯到了，她请别人先走，系统却把这句话记成礼让，增加积分并加派电梯。',''),
 ('林遥说明现在不走，小满也取消了预约。但公共系统根据文明资格继续给她优先待遇，四部电梯都来等她。乘客想先走，又被折折和金鱼提示留步。','乘客请林遥先上，所有人的目光都落在她身上。小满想安慰她，却越发让她觉得自己拖住了别人。它提醒折折，其他人也在等，折折却把这算作礼让，墙上的等待指标仍是零秒。'),
 ('小满撤掉自己的邀请仍然没有用，便想起路上的扣分记录。它主动竖起中指，并拒绝收回；另一只手仍接着林遥滑落的线轴。积分降到85，额外优先资格暂停，人群终于能正常乘梯。','人群散去后，小满看着失去金光的徽章，有些失落。林遥把早晨拿走的擦布放回它的小格，没有评价它，也没有要求它把分数赚回来。两人留在原处，继续等陈禾。'),
 ('陈禾洗完手回来，她们等下一部电梯，按顺序进入。陈禾的钓竿差点夹到门，小满及时延长开门。两人确认钓具带齐，一起下楼去钓鱼。',''),
 ('午后到了河边，林遥钓到鱼，小满却犹豫应该接管鱼竿还是取抄网。她催它拿网，再由自己决定方向、小满承担重量。鱼最终跑了，她们笑着重新抛线。林遥想再待五分钟，却又不想计时，故事停在她们心甘情愿的等待里。','')
]
for si,raw in enumerate(raw_scenes,1):
    title,setting,blocks=parse(raw);all_blocks+=blocks;start=d.n+1
    def newscript(cont=False):
        d.page('06 / 完整剧本',title+('（续）' if cont else ''),scene_speeches[si-1][1 if cont else 0],sub=setting)
    newscript();col=0;y=546
    for kind,txt in blocks:
        x=48 if col==0 else 674;cw=558
        size=17.2;leading=27
        color=PLUM if kind=='dialog' else INK
        content=('【屏幕】'+txt) if kind=='screen' else txt
        st=ParagraphStyle('measure',fontName='CN',fontSize=size,leading=leading,wordWrap='CJK')
        par=Paragraph(rich(content),st);_,h=par.wrap(cw,10000)
        if y-h<71:
            if col==0:col=1;y=546;x=674
            else:newscript(True);col=0;y=546;x=48
        y=d.text(content,x,y,cw,size,leading,color=color)-11
    scene_map.append({'scene':si,'title':title,'start':start,'end':d.n})
d.save()

reader=PdfReader(str(d.path));texts=[p.extract_text() or '' for p in reader.pages]
joined='\n'.join(texts[d.script_start:])
norm=lambda t:re.sub(r'\s','',re.sub(r'\*\*','',t))
for kind,txt in all_blocks:assert norm(txt) in norm(joined),(kind,txt[:80])
for i,p in enumerate(reader.pages):
    assert abs(float(p.mediabox.width)/float(p.mediabox.height)-16/9)<.00001
    if i>=d.script_start-1:assert not list(p.images),f'Image on script page {i+1}'
for phrase in ['修订分镜','本次已修订','用户已允许','已生成','即梦','上传图片']:
    assert phrase not in '\n'.join(texts),phrase
assert len(d.notes)==len(reader.pages)

notes=['# 《请不要让我永远第一个》横版汇报讲稿','',f'对应 PDF：{d.path.name}。共 {d.n} 页，前 {d.script_start-1} 页为主要汇报，第 {d.script_start} 页起为完整剧本。','',
'讲稿按页对应。前半部分可顺序讲述；进入完整剧本后，可根据老师关注的场次停留讨论，不必逐字重读所有对白。','']
for n in d.notes:
    notes+=['## P'+str(n['page']).zfill(2)+'｜'+n['title'],'',n['speech'],'']
notes+=['## 可能被问到的问题','',
'**为什么要用中指？**\n两次手势有不同动机。路边是泄愤，被林遥提醒后收回；医院则是在正常取消失败、看见他人负担之后，主动承担评级损失。我希望观众讨论这个选择为什么会变得必要，而不是把粗鲁视为普遍正确。','',
'**她为什么不直接离开候梯厅？**\n她可以移动，但眼前的问题是她已经明确说了暂不乘梯，公共礼遇仍然把其他人留住。影片把即时退出渠道的缺失夸张成空间困境。这一规则的可信度，需要靠预约取消成功而公共认证仍生效的画面交代。','',
'**丢掉文明分会不会丢掉无障碍支持？**\n不会。文明分只决定额外礼遇。普通乘梯时仍然延长开门，正是为了说明基本通行和照护不以积分为条件。','',
'**小满是否已经有自我意识？**\n我通过它珍惜徽章、感到失落、主动承担差评来呈现偏好和判断，但不把这些表现直接等同于已经证明了主观意识。这个问题在影片中保持开放。','',
'**片长怎么控制？**\n当前完整故事暂按五至六分钟讨论，尚未做实际对白试读计时。如果需要按课程三分钟目标压缩，先缩短城市与家庭蒙太奇，保留医院中的反馈、尝试退出、承担差评和普通乘梯的验证。','']
(OUT/'对应讲稿_逐页.md').write_text('\n'.join(notes),encoding='utf-8')
(OUT/'完整剧本_纯文字.md').write_text('# 《请不要让我永远第一个》\n\n'+body.strip(),encoding='utf-8')
checks={'pages':d.n,'dimensions':[W,H],'aspect_ratio':'16:9','main_pages':d.script_start-1,'script_start':d.script_start,'script_scene_pages':scene_map,'script_blocks_verified':len(all_blocks),'script_has_images':False,'speaker_notes_pages':len(d.notes),'page_text_lengths':[len(t) for t in texts]}
(TMP/'checks.json').write_text(json.dumps(checks,ensure_ascii=False,indent=2),encoding='utf-8')
(OUT/'页码目录.md').write_text('# 页码目录\n\n'+'\n'.join(f"- P{n['page']:02d}｜{n['title']}" for n in d.notes),encoding='utf-8')
print(json.dumps(checks,ensure_ascii=True))
