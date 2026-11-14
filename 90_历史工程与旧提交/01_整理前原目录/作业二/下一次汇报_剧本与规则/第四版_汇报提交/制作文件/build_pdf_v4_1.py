from pathlib import Path
import json, re, html
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.colors import HexColor
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import Paragraph
from reportlab.lib.utils import ImageReader
from PIL import Image

ROOT=Path(__file__).resolve().parent.parent
DATA=json.loads((ROOT/'制作文件/content_v4_1.json').read_text(encoding='utf-8'))
OUT=ROOT/'请等下一班_v4.1_作品剧本与故事板_横版汇报.pdf'
W,H=1280,720
M=64
BG='#F4F1EA'; INK='#172D31'; MUTED='#596A6C'; ACC='#A56A32'
DARK='#111E22'; LIGHT='#F4F0E8'; DM='#B6C5C7'
pdfmetrics.registerFont(TTFont('CN','C:/Windows/Fonts/msyh.ttc',subfontIndex=0))
pdfmetrics.registerFont(TTFont('CNB','C:/Windows/Fonts/msyhbd.ttc',subfontIndex=0))
C=canvas.Canvas(str(OUT),pagesize=(W,H),pageCompression=1)
C.setTitle('请等下一班 | 第四版作品剧本与故事板')
C.setAuthor('思辨设计课程作品')
C.setSubject('医院智能轮椅、让行协商、单次同意与长期偏好')
PAGE=0; OVER=[]; BOXES=[]
SOURCES={s[0]:s for s in DATA['sources']}
imgs=[ROOT/'分镜原图/01_等候与理由.png',ROOT/'分镜原图/02_协调与反转.png',ROOT/'分镜原图/03_选择与尾声.png']
READERS=[ImageReader(str(p)) for p in imgs]

def txt(s,x,y,w,fs=24,color=INK,bold=False,maxh=None,leading=None):
    st=ParagraphStyle('p',fontName='CNB' if bold else 'CN',fontSize=fs,leading=leading or fs*1.42,textColor=HexColor(color),wordWrap='CJK',spaceAfter=0,splitLongWords=True)
    p=Paragraph(html.escape(s).replace('\n','<br/>'),st)
    aw,ah=p.wrap(w,10000)
    if maxh is not None and ah>maxh+.5: OVER.append({'page':PAGE,'text':s[:50],'height':ah,'max':maxh})
    if x<0 or x+w>W+.5 or y<0 or y+ah>H+.5: OVER.append({'page':PAGE,'bounds':(x,y,w,ah),'text':s[:35]})
    p.drawOn(C,x,H-y-ah)
    BOXES.append({'page':PAGE,'rect':[x,y,x+w,y+ah],'text':s[:45]})
    return ah

def rule(y,x=M,w=W-2*M,color='#D8DDD8'):
    C.setStrokeColor(HexColor(color));C.setLineWidth(.8);C.line(x,H-y,x+w,H-y)

def new(title=None,label=None,dark=False):
    global PAGE
    if PAGE:C.showPage()
    PAGE+=1
    C.setFillColor(HexColor(DARK if dark else BG));C.rect(0,0,W,H,fill=1,stroke=0)
    col=LIGHT if dark else INK
    if label:txt(label,M,34,1100,15,DM if dark else MUTED)
    if title:txt(title,M,66,1152,36,col,True,maxh=67)
    txt(f'{PAGE:02d}',1180,677,40,14,DM if dark else MUTED)

def foot(s,dark=False):txt(s,M,679,1090,13,DM if dark else MUTED,maxh=20)

def refs(ids,y=646):
    x=M
    for sid in ids:
        s=SOURCES[sid];label='['+sid+'] '+s[1].split('：')[0]
        if len(label)>33:label=label[:31]+'…'
        fs=12;ww=pdfmetrics.stringWidth(label,'CN',fs)+23
        if x+ww>W-M:x=M;y+=20
        txt(label,x,y,ww,fs,MUTED,maxh=20)
        C.linkURL(s[2],(x,H-y-18,x+ww,H-y),relative=0,thickness=0)
        x+=ww+12

def panel(index,x,y,w,h):
    sheet=index//4;q=index%4
    im=READERS[sheet];iw,ih=im.getSize()
    # Clip a grid panel natively in the PDF, leaving original images untouched.
    col=q%2;row=q//2;pad=3
    sx=col*iw/2+pad;sy=row*ih/2+pad;sw=iw/2-2*pad;sh=ih/2-2*pad
    scale=max(w/sw,h/sh)
    extra_x=(sw*scale-w)/2;extra_y=(sh*scale-h)/2
    C.saveState();p=C.beginPath();p.rect(x,H-y-h,w,h);C.clipPath(p,stroke=0,fill=0)
    dx=x-sx*scale-extra_x;top=y-sy*scale-extra_y
    C.drawImage(im,dx,H-top-ih*scale,width=iw*scale,height=ih*scale,mask='auto')
    C.restoreState()

# 01
new(dark=True)
txt('思辨设计 / 作品剧本与故事板 / 第四版',M,56,1000,18,DM)
txt('请等\n下一班',M,137,1000,104,LIGHT,True,leading=129,maxh=268)
txt('医院里的两把智能轮椅',M,431,1000,30,LIGHT)
rule(500,color='#415252')
txt('它终于替主人争取到位置。\n另一个人，却要重新等待。',M,530,1100,28,'D2DADB' if False else '#D2DADB',maxh=86)
foot('五段故事 + 一次偏好询问　　影片设想约5分钟　　五国法规与院内使用调研',True)

# 02
new('谁在等电梯','人物与场景')
txt('综合医院门诊楼 · 普通公共客梯',M,148,1100,24,ACC,True)
txt('大家都要看病，林岚的预约快到了。',M,192,1100,28,INK,maxh=45)
rule(263)
for x,title,body in [(64,'林岚，72岁','腿部活动受限，需要轮椅。\n说话客气，不爱当众争执。\n她想准时复诊，也会犹豫。'),(468,'小椅','嘴快、护短，想把主人送到。\n它能代言、导航、请求协商。\n它需要确认每个人的意愿。'),(872,'另一位乘坐者','也要看病，带纸质就诊单。\n以前同意过等候。\n这次，他仍有权拒绝。')]:
    txt(title,x,302,344,27,INK,True,maxh=46)
    txt(body,x,371,344,23,MUTED,maxh=191)
txt('片中没有急救任务，也不靠揭露谁病得更重来决定谁值得先行。',M,588,1140,22,INK,maxh=65)
foot('人物、医院及轮椅协商机制为设计虚构。')

# 03
new('从真实研究，走到这个设想','选例与研究转译')
rows=[('R01','轮椅能够学习通行习惯','Johnson 与 Kuipers，2018','把“人们经常怎样走”学成可泛化的导航规范。'),('R02','模仿也可能继承偏差','Hurtado 等，2021','导航看起来顺畅，仍需检查负担是否反复落在同一群人身上。'),('R03','问题也藏在组织流程里','NIST，2022','把数据、人的判断与制度放在一起检查，不能只修一条模型输出。')]
for i,(sid,head,meta,body) in enumerate(rows):
    y=155+i*139
    txt(sid,M,y,83,20,ACC,True)
    txt(head,168,y,1030,27,INK,True,maxh=45)
    txt(meta,168,y+42,1030,17,MUTED)
    txt(body,168,y+74,1010,21,INK,maxh=61)
    if i<2:rule(y+125,x=168,w=1048)
txt('创作追问：预测“谁会让”，什么时候变成了决定“谁该让”？',M,588,1152,26,INK,True,maxh=49)
refs(['R01','R02','R03'])
foot('研究支持问题方向；没有证明本片的医院制度已经部署。')

# 04-09
for i,s in enumerate(DATA['scenes']):
    new(s['title'],f'故事 {i+1}/6　　影片 {s["time"]}',dark=True)
    for k,ix in enumerate(s['panels']):
        x=64+k*588
        panel(ix,x,150,564,317)
        txt(f'{ix+1:02d}  '+s['cap'][k],x,482,564,20,DM,maxh=75)
    txt(s['quote'],M,570,1152,31,LIGHT,True,maxh=49)
    txt(s['meaning'],M,628,1152,18,DM,maxh=29)
    foot('AI生成关键帧 / 非现场照片　　画面顺序与对白以第四版剧本为准。',True)

# 10
new('为什么总是找同一个人？','剧本背后的虚构制度')
for i,r in enumerate(DATA['rules']):
    y=148+i*79
    txt(r[0],64,y,72,19,ACC,True)
    txt(r[1],150,y,330,24,INK,True,maxh=70)
    txt(r[2],503,y,700,21,MUTED,maxh=62)
    if i<5:rule(y+66,x=150,w=1066)
foot('以上为本作品设定；不是现实医院规章，也不是某款轮椅的已部署功能。')

# 11
new('轮椅机器人的修养体现在哪里','角色行为与设计要求')
items=[('安全地争取','她先到，可以替她说。\n有人进入路径，仍要停下。'),('确认当前意愿','设备回复不替代本人同意。\n历史偏好不能压过当前拒绝。'),('说明影响并撤回','撤回安排，不另找更好说话的人。\n向实际有权限的人继续求助。'),('不默认保存偏好','尊重“不保存”。\n不把体谅训练成长期义务。')]
for i,(head,body) in enumerate(items):
    x=64+(i%2)*588;y=159+(i//2)*218
    txt(head,x,y,540,29,INK,True,maxh=48)
    txt(body,x,y+65,540,24,MUTED,maxh=117)
    rule(y+176,x=x,w=540)
txt('林岚可能迟到，对方可以拒绝。修养并不保证主人每次都赢。',64,609,1152,23,INK,maxh=41)
foot('机构仍需修改请求入口、连续漏乘记录、授权范围和考核方式。')

# 12: direct answer, with evidence strength visible
new('自主轮椅能在医院里运行吗？','五国调研结论 · 核查日期 2026.09.23')
txt('已有医院投入使用或开展试点；不能据此认定全国、全院、全模式开放。',64,132,1152,23,INK,True,maxh=40)
for x,t,w in [(64,'地区',100),(190,'可确认的结论',260),(490,'院内证据与限制',720)]:txt(t,x,190,w,17,MUTED,True)
rule(221)
rows=[
 ('中国','有院内启用报道','广西医大二附院2026年启用报道包含自主辅行轮椅。\n这是机构发布的部署信息，不能替代具体产品与运行模式核验。[D04]'),
 ('美国','有获机构批准的载人试点','2025.10—2026.01门诊试点，在预设路线运行；\n2026年原始研究已发表，不代表任意自主模式均获准。[D02]'),
 ('日本','部分医院已正式导入','横滨市民医院公告2024年4月起导入WHILL院内自主移动。\n可确认特定医院提供服务，不等于全国通用许可。[D01]'),
 ('英格兰','自主载人准入尚待核实','已核实产品监管与医院物流试验，未取得自主载人通行文件。\n目前不能下“普遍允许”或“普遍禁止”的结论。[L05/L10]'),
 ('新加坡','确认有历史院内测试','SMART记录2016年在樟宜综合医院测试自主轮椅。\n尚不能据此确认2026年常规服务或所有医院开放。[D03]')]
for i,(country,status,evidence) in enumerate(rows):
    y=237+i*77
    txt(country,64,y,110,23,ACC,True,maxh=36)
    txt(status,190,y,280,21,INK,True,maxh=60)
    txt(evidence,490,y,726,18,INK,maxh=61,leading=25)
    if i<4:rule(y+65)
refs(['D01','D02','D03','D04'],641)
foot('结论限定于公开证据；院内部署、产品上市条件与全国通行许可分别判断。')

# 13: statutes, not robot anecdotes
new('现行法规：具体管什么？','法规依据 1/2 · 中国 / 美国')
txt('中国',64,145,160,27,ACC,True)
txt('《医疗器械监督管理条例》',226,143,960,26,INK,True)
txt('第13条：分类注册或备案；第48条：按说明书和操作规范使用。\n第50、55条：维护设备，不得使用未依法注册/备案等不合规器械。',226,188,976,22,INK,maxh=76)
txt('《无障碍环境建设法》第44条：医疗机构应为残障者、老年人就医提供便利。',226,274,976,21,INK,maxh=65)
txt('结论：支持就医便利，但自动运行仍须符合具体产品条件；两部法规均非自主导航通行证。',226,347,976,20,MUTED,maxh=64)
rule(421)
txt('美国',64,447,160,27,ACC,True)
txt('ADA实施规则：28 CFR 36.311；FDA：21 CFR 890.3860',226,445,976,23,INK,True,maxh=68)
txt('ADA要求公众开放区域允许符合定义的轮椅通行；其他动力设备另作安全评估。\nFDA将电动轮椅列为Class II，具体产品及功能的监管状态需另核实。',226,518,976,21,INK,maxh=70)
txt('结论：保障轮椅使用者进入，不等于批准所有自主驾驶功能或任意路线。',226,591,976,20,MUTED,maxh=37)
refs(['L01','L02','L13','L09'],642)
foot('美国本页引用Title III公共服务场所条款；中国条例采用总局公布的含2024修改文本。')

# 14
new('现行法规与技术标准不能混用','法规依据 2/2 · 日本 / 英格兰 / 新加坡')
rows=[
 ('日本','《障害者差別解消法》；2024年4月修法生效',
 '提供合理便利的义务扩展至私营经营者，医疗服务也在范围内。\n结论：保障获得服务的机会，不是对任何自主轮椅自动发放运行许可。[L12]'),
 ('英格兰','UK Medical Devices Regulations 2002（经修订）',
 'MHRA按制造商预期用途判断医疗器械属性，适用者须满足相应合规条件。\n结论：必须核实具体产品和院内使用方案；送药机器人试验不能证明载人获准。[L10]'),
 ('新加坡','Health Products Act / Medical Devices Regulations 2010',
 'HSA：Class A免产品注册但需通知；B/C/D按适用路径注册。\nTR 108:2022、SS 713:2025是部署/互联技术标准，不是医院通行许可。[L11/L14/L07/L08]')]
for i,(country,law,body) in enumerate(rows):
    y=145+i*142
    txt(country,64,y,156,26,ACC,True)
    txt(law,248,y,968,23,INK,True,maxh=68)
    txt(body,248,y+49,968,20,INK,maxh=76,leading=28)
    if i<2:rule(y+128)
txt('本片设定：设备和路线已经获准使用；旧偏好替代本次同意，是虚构的制度问题。',64,590,1152,23,INK,True,maxh=69)
refs(['L10','L11','L12','L14'],644)
foot('英格兰页所引器械框架适用于大不列颠；新加坡标准仅核读官方公开范围，未引用付费正文。')

# 14
new('作品展示方式','故事板与交互设计')
txt('故事板展示',64,161,520,30,INK,True)
txt('按五段与尾声讲述12幅分镜。\n第五段暂停：接受安排，还是撤回？\n两种选择都有等待的代价。',64,228,535,25,INK,maxh=178)
txt('研究与创作边界',676,161,540,30,INK,True)
txt('人物与设备协商制度为虚构。\n研究和法规分别列出来源。\n故事板为AI生成的视觉设想。',676,228,540,24,INK,maxh=146)
rule(447)
txt('后续设想',64,486,230,23,ACC,True)
txt('同一个3D电梯厅，让观众选择一次同意、拒绝或撤回偏好，查看双方等待。',300,486,916,24,INK,maxh=112)
txt('尚未实现动画、可点击Demo、模型训练、医院接入或安全验证。',64,613,1152,21,MUTED,maxh=39)
foot('真实法规与研究、虚构制度、AI合成画面分别标注，互不替代。')

# 15
new(dark=True)
txt('请等下一班',64,71,1100,23,DM)
txt('“别存。\n下次先问我。”',64,183,1152,69,LIGHT,True,leading=94,maxh=205)
rule(460,color='#415252')
txt('以前愿意让行的人，\n今天还能不能方便地拒绝？',64,505,1120,32,LIGHT,maxh=109)
foot('轮椅具身智能 / 让行、同意与医院调度',True)

# 16-17 sources
for part in range((len(DATA['sources'])+5)//6):
    new(f'参考来源 {part+1}/{(len(DATA["sources"])+5)//6}','法规 / 研究 / 院内应用')
    for j,s in enumerate(DATA['sources'][part*6:(part+1)*6]):
        y=145+j*82
        txt(s[0],64,y,70,17,ACC,True,maxh=29)
        txt(s[1],155,y,1055,20,INK,True,maxh=31)
        txt(s[3],155,y+34,1055,16,MUTED,maxh=46)
        C.linkURL(s[2],(155,H-y-30,1216,H-y),relative=0,thickness=0)
        if j<5:rule(y+71,x=155,w=1061)
    foot('来源编号与第四版MD一致。法规、试验、技术研究与创作参考的效力和范围不同。')

# 18-20 full screenplay, 2 acts per page
for part in range(3):
    new(f'完整剧本 {part+1}/3','作品剧本 / 医院门诊楼')
    for k,s in enumerate(DATA['scenes'][part*2:(part+1)*2]):
        x=64+k*588
        txt(s['n']+'  '+s['title'],x,143,552,24,INK,True,maxh=73)
        txt('影片 '+s['time'],x,198,552,14,MUTED,maxh=25)
        text=s['text'].replace('\n\n','\n')
        txt(text,x,237,552,16.5,INK,maxh=416,leading=24)
    foot('时间为叙事预算。记忆、回放与切镜不等于电梯持续开门；实际门时序需后续预演核定。')

C.save()
(ROOT/'制作文件/layout_checks_v4_1.json').write_text(json.dumps({'pages':PAGE,'overflow':OVER,'text_boxes':BOXES},ensure_ascii=False,indent=2),encoding='utf-8')
if OVER:
    print(json.dumps(OVER,ensure_ascii=False,indent=2))
    raise SystemExit('Layout overflow detected')
print(json.dumps({'pdf':str(OUT),'pages':PAGE,'bytes':OUT.stat().st_size,'overflow':len(OVER)},ensure_ascii=False))
