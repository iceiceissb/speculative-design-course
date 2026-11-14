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
DATA=json.loads((ROOT/'制作文件/content.json').read_text(encoding='utf-8'))
OUT=ROOT/'总有人会让_v4_作品剧本与故事板_横版汇报.pdf'
W,H=1280,720
M=64
BG='#F4F1EA'; INK='#172D31'; MUTED='#596A6C'; ACC='#A56A32'
DARK='#111E22'; LIGHT='#F4F0E8'; DM='#B6C5C7'
pdfmetrics.registerFont(TTFont('CN','C:/Windows/Fonts/msyh.ttc',subfontIndex=0))
pdfmetrics.registerFont(TTFont('CNB','C:/Windows/Fonts/msyhbd.ttc',subfontIndex=0))
C=canvas.Canvas(str(OUT),pagesize=(W,H),pageCompression=1)
C.setTitle('总有人会让 | 第四版作品剧本与故事板')
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
txt('总有人\n会让',M,137,860,104,LIGHT,True,leading=129,maxh=268)
txt('医院里的两把智能轮椅',M,431,1000,30,LIGHT)
rule(500,color='#415252')
txt('它终于替主人争取到位置。\n另一个人，却要重新等待。',M,530,1100,28,'D2DADB' if False else '#D2DADB',maxh=86)
foot('五段故事 + 一次偏好询问　　影片设想约5分钟　　汇报约8分钟',True)

# 02
new('谁在等电梯','人物与场景')
txt('综合医院门诊楼 · 普通公共客梯',M,148,1100,24,ACC,True)
txt('大家都要看病，林岚的预约快到了。',M,192,1100,28,INK,maxh=45)
rule(263)
for x,title,body in [(64,'林岚，72岁','腿部活动受限，需要轮椅。\n说话客气，不爱当众争执。\n她想准时复诊，也会犹豫。'),(468,'小椅','嘴快、护短，想把主人送到。\n它能代言、导航、请求协商。\n它不能替别人答应。'),(872,'另一位乘坐者','也要看病，带纸质就诊单。\n以前同意过等候。\n这次，他仍有权拒绝。')]:
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
new('小椅要学会的修养','通过行动表现，而不是给它打“礼貌分”')
items=[('安全地争取','她先到，可以替她说。\n有人进入路径，仍要停下。'),('重新问这一次','设备回复不替代本人同意。\n历史偏好不能压过当前拒绝。'),('承认代价来自谁','撤回安排，不另找更好说话的人。\n向实际有权限的人继续求助。'),('让一次保持为一次','尊重“不保存”。\n不把体谅训练成长期义务。')]
for i,(head,body) in enumerate(items):
    x=64+(i%2)*588;y=159+(i//2)*218
    txt(head,x,y,540,29,INK,True,maxh=48)
    txt(body,x,y+65,540,24,MUTED,maxh=117)
    rule(y+176,x=x,w=540)
txt('林岚可能迟到，对方可以拒绝。修养并不保证主人每次都赢。',64,609,1152,23,INK,maxh=41)
foot('机构仍需修改请求入口、连续漏乘记录、授权范围和考核方式。')

# 12
new('医院能不能用自动设备？','多国调研 1/2')
txt('通行权、产品条件和自动模式，需要分别核对。',64,140,1152,24,INK,True,maxh=43)
countries=[('中国','法规要求分类管理、相应注册/备案与规范使用。\n无障碍法要求保障设施并提供就医便利。','还需核实医院允许的区域、模式及接管流程。'),('美国','ADA区分轮椅与其他动力移动设备，\n保障相应公众开放区域的通行。','通行要求不等于批准某种自主驾驶功能。'),('日本','庆应大学医院2020年公告\n院内自主载人移动技术试验。','具体试验存在，不代表所有医院普遍开放。')]
for i,(name,fact,limit) in enumerate(countries):
    y=219+i*130
    txt(name,64,y,120,27,ACC,True,maxh=45)
    txt(fact,215,y,576,22,INK,maxh=101)
    txt(limit,850,y,366,22,MUTED,maxh=101)
    if i<2:rule(y+109,x=215,w=1001)
refs(['L01','L02','L03','L04'],640)
foot('定向核查至2026-09-23。历史试验不作为2026年实时运营证明。')

# 13
new('设备能通信，谁有权答应？','多国调研 2/2')
txt('英格兰',64,167,150,27,ACC,True)
txt('医院有送药机器人限定路线试验。\nCQC的同意要求适用于相应受监管照护/治疗。',248,165,956,23,INK,maxh=107)
txt('物流试验不能直接证明载人获准。',248,260,956,22,MUTED)
rule(319)
txt('新加坡',64,358,150,27,ACC,True)
txt('TR 108:2022涉及医疗场所机器人系统部署。\nSS 713:2025涉及机器人与电梯、自动门集成。',248,356,956,23,INK,maxh=107)
txt('互联标准不授予替乘坐者同意移动的权力。',248,451,956,22,MUTED)
txt('本片设定：设备与路线已获准，争议发生在协商和授权之中。',64,548,1152,26,INK,True,maxh=80)
refs(['L05','L06','L07','L08'],640)
foot('新加坡仅核读官方目录公开范围。SS 713:2025替代TR 93:2021，未查付费全文。')

# 14
new('把选择留给观众','汇报方式与能力边界')
txt('现场怎样展示',64,161,520,30,INK,True)
txt('按五段与尾声讲述12幅分镜。\n第五段暂停：接受安排，还是撤回？\n两种选择都有等待的代价。',64,228,535,25,INK,maxh=178)
txt('本次已经完成',676,161,540,30,INK,True)
txt('第四版剧本、AI关键帧、横版PDF、讲稿。\n图像由内置图像生成工具制作。',676,228,540,24,INK,maxh=146)
rule(447)
txt('后续设想',64,486,230,23,ACC,True)
txt('同一个3D电梯厅，让观众选择一次同意、拒绝或撤回偏好，查看双方等待。',300,486,916,24,INK,maxh=112)
txt('尚未实现动画、可点击Demo、模型训练、医院接入或安全验证。',64,613,1152,21,MUTED,maxh=39)
foot('真实法规与研究、虚构制度、AI合成画面分别标注，互不替代。')

# 15
new(dark=True)
txt('总有人会让',64,71,1100,23,DM)
txt('“不。\n这次就是这次。”',64,183,1152,69,LIGHT,True,leading=94,maxh=205)
rule(460,color='#415252')
txt('机器人能不能记住我们的需要，\n又不把一次体谅记成一种义务？',64,505,1120,32,LIGHT,maxh=109)
foot('以下为来源备查与完整剧本，不需在8分钟汇报中逐页朗读。',True)

# 16-17 sources
for part in range(2):
    new(f'来源备查 {part+1}/2','点击条目可打开原始页面')
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
    new(f'完整剧本 {part+1}/3','备查附录 / 现场不逐句朗读')
    for k,s in enumerate(DATA['scenes'][part*2:(part+1)*2]):
        x=64+k*588
        txt(s['n']+'  '+s['title'],x,143,552,24,INK,True,maxh=73)
        txt('影片 '+s['time'],x,198,552,14,MUTED,maxh=25)
        text=s['text'].replace('\n\n','\n')
        txt(text,x,237,552,16.5,INK,maxh=416,leading=24)
    foot('时间为叙事预算。记忆、回放与切镜不等于电梯持续开门；实际门时序需后续预演核定。')

C.save()
(ROOT/'制作文件/layout_checks.json').write_text(json.dumps({'pages':PAGE,'overflow':OVER,'text_boxes':BOXES},ensure_ascii=False,indent=2),encoding='utf-8')
if OVER:
    print(json.dumps(OVER,ensure_ascii=False,indent=2))
    raise SystemExit('Layout overflow detected')
print(json.dumps({'pdf':str(OUT),'pages':PAGE,'bytes':OUT.stat().st_size,'overflow':len(OVER)},ensure_ascii=False))
