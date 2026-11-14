"""Four-page screenshot-led introduction for the final coursework Demo folder."""
from pathlib import Path
import json
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.colors import HexColor, Color
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.utils import ImageReader
from pypdf import PdfReader

BASE=Path(__file__).resolve().parents[1]
WORKSPACE=BASE.parents[1]
QA=BASE/'QA'
OUT=WORKSPACE/'05_汇报与成片/04_最终提交作业/Demo/把路走通_游戏介绍.pdf'
CHECKS=QA/'PDF_介绍检查'
pdfmetrics.registerFont(TTFont('YaHei',r'C:\Windows\Fonts\msyh.ttc',subfontIndex=0))
pdfmetrics.registerFont(TTFont('YaHeiBold',r'C:\Windows\Fonts\msyhbd.ttc',subfontIndex=0))
W,H=landscape(A4);M=46;CW=W-M*2
INK=HexColor('#23465C');TEAL=HexColor('#178F91');MUTED=HexColor('#637D78')
PAPER=HexColor('#FBF8EE');GREEN=HexColor('#E3EEDB');CORAL=HexColor('#EF805E')
SAND=HexColor('#EFE7D3');WHITE=HexColor('#FFFFFF')
c=canvas.Canvas(str(OUT),pagesize=(W,H),pageCompression=1)
c.setTitle('把路走通 · 晴溪两岸 | 游戏 Demo 介绍')
c.setAuthor('思辨设计项目')
c.setSubject('轮椅出行、障碍反馈与持续改善的城市地图')
used=[]

def text(value,x,y,size=11,color=INK,bold=False):
    c.setFillColor(color);c.setFont('YaHeiBold' if bold else 'YaHei',size);c.drawString(x,y,value)

def wrap(value,width,size=11,bold=False):
    font='YaHeiBold' if bold else 'YaHei';lines=[]
    for paragraph in value.split('\n'):
        line=''
        for ch in paragraph:
            if line and pdfmetrics.stringWidth(line+ch,font,size)>width:lines.append(line);line=ch
            else:line+=ch
        lines.append(line)
    return lines

def body(value,x,y,width,size=11,leading=17,color=INK,bold=False):
    lines=wrap(value,width,size,bold)
    for i,line in enumerate(lines):text(line,x,y-i*leading,size,color,bold)
    return y-len(lines)*leading

def panel(x,y,w,h,color=GREEN,r=7):
    c.setFillColor(color);c.roundRect(x,y,w,h,r,stroke=0,fill=1)

def image(name,x,y,w,h=None):
    p=QA/name
    if not p.exists():raise FileNotFoundError(p)
    if h is None:h=w*9/16
    c.saveState();path=c.beginPath();path.roundRect(x,y,w,h,6);c.clipPath(path,stroke=0,fill=0)
    c.drawImage(ImageReader(str(p)),x,y,width=w,height=h,preserveAspectRatio=True,anchor='c',mask='auto')
    c.restoreState();c.setStrokeColor(HexColor('#DBDFD1'));c.setLineWidth(.6);c.roundRect(x,y,w,h,6,stroke=1,fill=0)
    used.append(name)
    return h

def page(n,title,subtitle,kicker='把路走通 / 晴溪两岸'):
    c.setFillColor(PAPER);c.rect(0,0,W,H,fill=1,stroke=0)
    c.setFillColor(TEAL);c.rect(M,H-24,31,3,fill=1,stroke=0)
    text(kicker,M+42,H-25,8.5,MUTED)
    text(title,M,H-60,30 if n==1 else 25,INK,True)
    text(subtitle,M,H-84,11.5,MUTED)
    c.setStrokeColor(HexColor('#DDE4D5'));c.setLineWidth(.6);c.line(M,30,W-M,30)
    text('思辨设计 · 3D 游戏交互原型',M,16,8,MUTED)
    c.setFillColor(MUTED);c.setFont('YaHei',8);c.drawRightString(W-M,16,f'{n:02d} / 04')

# 01: The playable idea, led by the actual sunny neighbourhood.
page(1,'把路走通','从一次普通的出门开始，让回家的路更好走。','SUNNY PATH / DEMO v3 / WINDOWS')
image('native_theme_2_scene.png',M,82,CW)
text('扮演坐轮椅出行的小女孩，去买菜、借书或种薄荷。',M,62,11,INK,True)
text('遇到障碍时留下反馈，办完生活任务，再沿着改善后的道路回家。',M,44,10.5,MUTED)
c.showPage()

# 02: Report, finish the errand, and test the repaired street on the way home.
page(2,'一次出行，留下看得见的改变','核心玩法：自己的生活任务，和城市通行问题的反馈，一起发生。')
steps=['出门办事','遇到障碍','定位上报','完成任务','沿路回家']
gap=15;stepw=(CW-gap*4)/5
for i,label in enumerate(steps):
    x=M+i*(stepw+gap);panel(x,450,stepw,40,TEAL if i==4 else GREEN)
    text(f'{i+1:02d}',x+11,464,9,WHITE if i==4 else TEAL,True)
    text(label,x+35,463,12,WHITE if i==4 else INK,True)
    if i<4:text('>',x+stepw+4,463,10,MUTED)
colw=(CW-28)/3
cards=[('native_first_person_0.png','看见不便','货箱、台阶或过窄的柱口，\n会直接影响轮椅的通行。'),
       ('fp_full_report.png','留下反馈','按 E 查看现场图片与位置，\n确认提交后继续自己的行程。'),
       ('fp_full_return.png','回程验证','完成生活任务后沿原路回家，\n亲自通过已经改善的路段。')]
for i,(name,title,note) in enumerate(cards):
    x=M+i*(colw+14);image(name,x,284,colw)
    text(title,x,263,15,TEAL,True);body(note,x,242,colw,10.5,16,MUTED)
text('修复的是原来的路，也改变下一次出发的条件。',M,177,17,INK,True)
body('去程仍然需要观察和绕行。办完自己的事后，已提交的问题在游戏中得到处理；返程时，障碍物和可通行空间会一起改变。',M,151,CW,11,18,MUTED)
issues=['货箱占道','缺少坡道','柱口过窄','地砖翘起','车辆占道','坡道过陡']
iw=(CW-10*5)/6
for i,issue in enumerate(issues):
    x=M+i*(iw+10);panel(x,73,iw,31,SAND,5);text(issue,x+12,83,10,INK)
text('Demo 将受理与维修压缩到生活任务之后，呈现“提交反馈、得到处理、再次走过”的闭环。',M,45,9,MUTED)
c.showPage()

# 03: The view switch has a different purpose and a different driving scheme.
page(3,'同一条路，两种观看方式','按 V 随时切换；位置、任务与沿途反馈保持连续。')
colw=(CW-18)/2
image('native_theme_0_scene.png',M,289,colw)
image('native_first_person_0.png',M+colw+18,289,colw)
text('河对岸观察',M,268,17,TEAL,True)
text('看清轮椅、街景与绕行空间。',M,247,10.5,MUTED)
text('轮椅第一人称',M+colw+18,268,17,TEAL,True)
text('以坐姿眼高感受路面、障碍和距离。',M+colw+18,247,10.5,MUTED)
panel(M,175,colw,57,GREEN);panel(M+colw+18,175,colw,57,GREEN)
text('A / D 沿街移动    W / S 纵深绕行',M+13,211,10.5,INK,True)
text('滚轮拉近 / 拉远；Shift 稍快行驶。',M+13,191,10,MUTED)
text('W / S 前进后退    A / D 左右转向',M+colw+31,211,10.5,INK,True)
text('按住鼠标右键环顾；R 看回正前方。',M+colw+31,191,10,MUTED)
text('通用操作：E 互动与上报    M 城市地图    J 反馈记录    Esc 暂停 / 返回',M,151,10.5,INK)
taskw=(CW-28)/3
tasks=[('晴日市集','挑选三样食材，买好后回家。'),('梧桐图书馆','归还旧书，再借走预约的书。'),('共享花园','领取薄荷苗，种植并浇水。')]
for i,(title,note) in enumerate(tasks):
    x=M+i*(taskw+14);panel(x,52,taskw,78,SAND)
    text(title,x+14,105,13,INK,True);body(note,x+14,83,taskw-28,10,15,MUTED)
c.showPage()

# 04: Persistent progress, photos, and a practical hand-in launch instruction.
page(4,'一张会留下变化的城市地图','每完成一次行程，就为下一次出发多打开一点空间。')
leftw=470;rightx=M+leftw+18;rightw=CW-leftw-18
image('world_v3.png',M,220,leftw)
image('theme0_journal.png',rightx,337,rightw)
text('反馈记录 J',rightx,316,15,TEAL,True)
body('现场照片、地点与处理状态留在记录页。\n回来再看一次，确认道路发生了什么变化。',rightx,294,rightw,10.5,17,MUTED)
text('25 个街区 / 75 个通行地点',M,193,17,TEAL,True)
body('改善结果保存在本机。完成行程后，相邻街区逐步开放；\n每次出门积累的改变，会成为下一次探索的起点。',M,171,leftw,10.5,17,MUTED)
panel(M,58,CW,83,GREEN)
text('开始试玩',M+16,120,13,INK,True)
text('双击 Demo 文件夹中的「开始游戏.cmd」；也可打开「游戏文件 / SunnyPath.exe」。',M+16,99,10.5,INK)
text('在标题页选择市集、图书馆或花园，按 Enter 开始。无需安装 Unity 或 Blender，无需联网。',M+16,79,10,MUTED)
text('当前为本地单人演示，受理与维修均为游戏内模拟；联网共建的更大地图属于后续设想。',M,42,8.5,MUTED)
c.showPage();c.save()

reader=PdfReader(str(OUT));content='\n'.join(p.extract_text() or '' for p in reader.pages)
required=['把路走通','核心玩法','第一人称','75 个通行地点','开始游戏.cmd','游戏内模拟']
missing=[s for s in required if s not in content]
if len(reader.pages)!=4 or missing:raise RuntimeError({'pages':len(reader.pages),'missing':missing})
CHECKS.mkdir(parents=True,exist_ok=True)
(CHECKS/'extracted_text.txt').write_text(content,encoding='utf-8')
(CHECKS/'pdf_content_check.json').write_text(json.dumps({'pdf':str(OUT),'pages':4,'screenshots':used,'requiredTextPresent':not missing,'bytes':OUT.stat().st_size},ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'pdf':str(OUT),'pages':4,'screenshots':len(used),'bytes':OUT.stat().st_size},ensure_ascii=True))
