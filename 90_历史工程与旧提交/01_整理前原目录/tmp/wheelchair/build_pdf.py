from pathlib import Path
import json,html,re,math
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import Paragraph,Table,TableStyle
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.colors import HexColor,white
from PIL import Image

ROOT=Path('D:/课/大四上/思辨设计');OUT=ROOT/'output/作业一_智能轮椅';TMP=ROOT/'tmp/wheelchair';AS=TMP/'assets'
D=json.loads((OUT/'研究底稿/专题数据.json').read_text(encoding='utf-8'));CA=D['cases']
pdfmetrics.registerFont(TTFont('YH','C:/Windows/Fonts/msyh.ttc'))
pdfmetrics.registerFont(TTFont('YHB','C:/Windows/Fonts/msyhbd.ttc'))
pdfmetrics.registerFontFamily('YH',normal='YH',bold='YHB',italic='YH',boldItalic='YHB')
W,H=595.276,841.89;M=43;CW=W-2*M
INK='#24343D';MUT='#64737A';ACC='#416B72';LINE='#D9E1E1';PAPER='#FCFCF9';PALE='#EDF2F1';RUST='#92654E'
PDF=OUT/'作业一_轮椅机器人的自我修养_案例库与选题说明.pdf'
c=canvas.Canvas(str(PDF),pagesize=(W,H));c.setTitle('这一次，轮椅该听谁的？｜机器人自我修养案例库与选题说明');c.setAuthor('课程作业 / AI辅助检索与排版')
page=0;qa=[]
def p(text,x,y,w,size=10.4,leading=None,color=INK,bold=False,align=0):
 text=html.escape(str(text));text=re.sub(r'\*\*(.*?)\*\*',r'<b>\1</b>',text)
 text=re.sub(r'\[([^\]]+)\]\((https?://[^)]+)\)',lambda m:f'<link href="{m[2]}" color="{ACC}">{m[1]}</link>',text)
 text=text.replace('\n','<br/>')
 q=Paragraph(text,ParagraphStyle('p',fontName='YHB' if bold else 'YH',fontSize=size,leading=leading or size*1.65,textColor=HexColor(color),wordWrap='CJK',alignment=align))
 _,height=q.wrap(w,1000);q.drawOn(c,x,H-y-height)
 if y<800 and y+height>789:qa.append({'page':page,'bottom':y+height,'text':text[:90]})
 return y+height
def line(y,x=M,w=CW,color=LINE):c.setStrokeColor(HexColor(color));c.setLineWidth(.65);c.line(x,H-y,x+w,H-y)
def rect(x,y,w,h,fill=PALE):c.setFillColor(HexColor(fill));c.rect(x,H-y-h,w,h,stroke=0,fill=1)
def start(title,kicker,sub=''):
 global page
 if page:c.showPage()
 page+=1;c.setFillColor(HexColor(PAPER));c.rect(0,0,W,H,stroke=0,fill=1)
 p('机器人自我修养案例库',M,24,300,8,color=MUT);p('2026.09.18',W-M-80,24,80,8,color=MUT,align=2);line(45)
 p(kicker,M,66,CW,9,color=ACC,bold=True)
 y=p(title,M,89,CW,23,32,bold=True)+12
 if sub:y=p(sub,M,y,CW,10.2,color=MUT)+17
 line(800);p('作业一  /  智能轮椅专题',M,811,350,7.8,color=MUT);p(f'{page:02d} / 20',W-M-75,811,75,8,color=MUT,align=2)
 return y
def para(t,y,**kw):return p(t,M,y,CW,**kw)+12
def h(t,y):return p(t,M,y,CW,13.2,color=ACC,bold=True)+8
def callout(t,y,height=None):
 q=Paragraph(html.escape(t).replace('\n','<br/>'),ParagraphStyle('call',fontName='YHB',fontSize=12.1,leading=20,textColor=HexColor(ACC),wordWrap='CJK'))
 _,ph=q.wrap(CW-30,1000);hh=height or ph+28;rect(M,y,CW,hh);q.drawOn(c,M+15,H-y-14-ph);return y+hh+16
def pic(path,x,y,w,maxh,caption=None,link=None):
 im=Image.open(path);iw,ih=im.size;ratio=min(w/iw,maxh/ih);dw,dh=iw*ratio,ih*ratio
 c.drawImage(str(path),x+(w-dw)/2,H-y-dh,width=dw,height=dh,mask='auto')
 if link:c.linkURL(link,(x,H-y-dh,x+w,H-y),relative=0)
 end=y+dh
 if caption:end=p(caption,x,end+6,w,7.8,color=MUT)+6
 return end
def table(rows,y,widths,size=9.3,headers=True):
 data=[]
 for i,row in enumerate(rows):
  data.append([Paragraph(html.escape(str(t)).replace('\n','<br/>'),ParagraphStyle('cell',fontName='YHB' if i==0 and headers else 'YH',fontSize=size,leading=size*1.5,textColor=HexColor(INK),wordWrap='CJK')) for t in row])
 tb=Table(data,colWidths=widths,hAlign='LEFT');tb.setStyle(TableStyle([('VALIGN',(0,0),(-1,-1),'TOP'),('BACKGROUND',(0,0),(-1,0),HexColor(PALE)),('LINEBELOW',(0,0),(-1,0),.8,HexColor(ACC)),('LINEBELOW',(0,1),(-1,-1),.4,HexColor(LINE)),('LEFTPADDING',(0,0),(-1,-1),7),('RIGHTPADDING',(0,0),(-1,-1),7),('TOPPADDING',(0,0),(-1,-1),7),('BOTTOMPADDING',(0,0),(-1,-1),7)]))
 _,th=tb.wrap(CW,1000);tb.drawOn(c,M,H-y-th)
 if y+th>789:qa.append({'page':page,'bottom':y+th,'text':'TABLE'})
 return y+th+14
def card(code,y):
 d=next(v for v in CA if v['案例编号']==code)
 line(y);y+=10;y=p(f"{code}  {d['案例名称']}",M,y,CW,13,bold=True)+4
 y=p(f"{d['主库编号']}  /  {d['年份或版本']}  /  {d['来源类型']}",M,y,CW,8.2,color=ACC)+10
 for lab,key in [('场景','场景与对象'),('行为','具体行为'),('修养解释','修养特点_本作业解释'),('反馈证据','反馈与改进证据'),('证据边界','证据边界')]:
  bottom=p(lab,M,y,61,9.2,color=MUT,bold=True)
  end=p(d[key],M+68,y,CW-68,9.6,14.6);y=max(bottom,end)+6
 y=p(f"[来源：{d['核查位置']}]({d['来源链接']})",M+68,y,CW-68,8,color=ACC)+14
 return y

# 01
y=start('这一次，\n轮椅该听谁的？','ASSIGNMENT 01  /  案例库与初步选题')
y=para('换身后的智能轮椅：自主、保护与反馈修正',y,size=13,color=ACC)
y=pic(AS/'easyway.png',M,y+5,CW,250,'图1 既有Easyway项目的轮椅形态设计，节选自用户提供文件第10页。作为设计起点，不代表已完成产品验证。')+18
y=callout('“我记得这条路，但新的身体还没有验证过这里。”',y)
y=para('研究从轮椅辅助中的具体行为出发：机器怎样承认局限、允许人改变主意、解释限制，并让反馈影响后续行动。换身与记忆迁移作为后续思辨情境，帮助讨论信任与责任如何重新分配。',y)
y=table([['研究材料','本次交付'],['12个核心案例 / 4类主导行为','PRISMA式流程、案例表、分类图、一项改进建议'],['5个轮椅案例 / 7个跨场景参照','另附Excel提取表、逐项筛选台账与实际检索记录'] ],y,[CW/2,CW/2],9.3)
p('全文中的“修养类型”为本作业的分析命名，不是原作者对机器人意识或道德主体地位的认定。',M,y,CW,8.4,color=MUT)

# 02
y=start('从“能带我去”到“谁决定去”','01 / 选题与既有设计的联系')
y=para('Easyway提出模块化辅助出行、语音导航、家人端与电子围栏。本作业沿用轮椅作为具身载体，将关注点转到：辅助何时支持自主，何时替使用者作主。',y)
y=table([['既有方案中的功能','本次要追问的伦理问题'],['导航、避障、紧急停止','无法前进是客观障碍、感知错误，还是他人设置的限制？'],['家人端、轨迹回放、电子围栏','使用者能否拒绝分享？家人的担心是否自动获得限制出行的权限？'],['外挂适配、个性化学习','更换底盘后，哪些旧参数还有效？谁负责重新适配、承担时间与费用？']],y,[150,CW-150],10)
y=h('先明确服务对象，再讨论保护',y)
y=para('目标人群是有辅助出行需求的轮椅使用者，包含部分老年人与行动障碍成年人。年龄、视障、肢体障碍与认知能力分别考虑，不把“老人和残障者”视为同一种需求，也不默认他们无法表达意愿。',y)
y=para('这里的“轮椅机器人”指具备感知、辅助决策与执行能力的轮椅系统。本次主情境先限定为能通过适配接口表达意愿的成年使用者。语音、摇杆、开关等按个人能力选择；复杂紧急情形与临床处置不在本原型验证范围内。',y)
y=callout('思辨问题：如果轮椅以“保护你”为由反复阻止出行，使用者怎样质疑它，而不必每次都放弃全部辅助？',y)
p('资料边界：Easyway为用户提供的课程项目文件，相关功能在此视为方案描述；不沿用其中未核查的市场数字、性能承诺或竞品价格。',M,y,CW,8.8,color=MUT)

# 03
y=start('研究范围与问题','02 / 参照PRISMA的探索性案例综述')
y=table([['PCC要素','本次界定'],['P 人群与对象','轮椅使用者及其辅助机器人；照护者、维修者与被记录者作为相关方。'],['C 核心概念','共享控制、承认局限、可中止与可纠正、隐私边界、反馈修正。'],['C 情境','辅助出行与身体密切相关的人机互动；跨场景案例只转译行为机制。']],y,[112,CW-112],10)
y=h('三个研究问题',y)
for t in ['RQ1 机器人如何把“尊重自主”和“保护使用者”转化为可观察的行为？','RQ2 当人机判断冲突时，使用者如何澄清、暂停、覆盖或纠正机器人？','RQ3 哪些证据显示改变只发生在当次，哪些显示反馈影响后续行为？这些机制如何转译到换身后的轮椅？']:y=para(t,y)
y=h('方法口径',y)
y=para('本次以小型、可比较的案例集为目的。先从既有260条主库中目的性选取14条种子，再补充轮椅来源。选种围绕四类行为及记忆连续性背景展开，存在选择偏差，不声称代表全领域。',y)
y=para('本轮检索与核查日期为2026-09-18。不设发表年份下限；纳入案例覆盖1996年至当前官网版本。通过公开Web搜索发现资料，追到作者、机构、期刊或厂商原始来源；没有进行WoS、Scopus等数据库的完整导出。',y)
p('由AI辅助检索、逐项提取与分组；未开展第二位独立筛选者复核、统计一致性评价或用户实验。PRISMA用于透明报告过程，不代表完成正式系统综述或注册方案。',M,y,CW,8.8,color=MUT)

# 04
y=start('检索、归并、筛选与纳入','03 / PRISMA式流程图','计数单位沿流程注明。25是保存的候选来源记录数，不是搜索引擎总命中数。')
def box(x,y,w,h,title,sub,accent=False):
 rect(x,y,w,h,ACC if accent else PALE);p(title,x+10,y+8,w-20,11.1,bold=True,color='#FFFFFF' if accent else INK,align=1);p(sub,x+10,y+29,w-20,8.5,color='#FFFFFF' if accent else MUT,align=1)
def arrow(x,y,x2,y2):
 c.setStrokeColor(HexColor(ACC));c.setLineWidth(.9);c.line(x,H-y,x2,H-y2)
 a=math.atan2(y2-y,x2-x);s=5
 c.line(x2,H-y2,x2-s*math.cos(a-.55),H-(y2-s*math.sin(a-.55)));c.line(x2,H-y2,x2-s*math.cos(a+.55),H-(y2-s*math.sin(a+.55)))
left=M;main=286;right=M+main+17;rw=CW-main-17
steps=[('识别来源记录  n=25','既有种子14 + 补充来源11'),('进入候选初筛  n=22','按项目／研究归并后的案例候选'),('拟核查来源  n=18','读取全文、手册或完整项目说明'),('完成来源适配性评估  n=16','按案例单位评价具体行为与证据'),('纳入核心案例  n=12','5例轮椅 + 7例跨场景参照')]
ys=[y+i*93 for i in range(5)]
for i,(t,s) in enumerate(steps):
 box(left,ys[i],main,64,t,s,i==4)
 if i<4:arrow(left+main/2,ys[i]+64,left+main/2,ys[i+1])
side=[('筛选前归并  n=3','完全重复0；同项目追加3\nLUCI归并2、CoNav归并1'),('初筛排除  n=4','理论／综述／框架4\n可作背景，不计核心案例'),('原文不足  n=2','仅摘要／入口获取失败\n不能完成行为证据核查'),('评估后排除  n=4','人的评价1；背景事件2\n单一重置操作1')]
for i,(t,s) in enumerate(side):box(right,ys[i],rw,73,t,s);arrow(left+main,ys[i]+32,right,ys[i]+32)
y=ys[-1]+80
y=para('数量核对：25 − 3 = 22；22 − 4 = 18；18 − 2 = 16；16 − 4 = 12。12个纳入案例对应15条已保存来源记录；不同版本或同项目报道不重复算案例。',y,size=9.5)
p('流程改编说明：沿用老师模板的识别、筛选、来源获取、评估与纳入层次；将“全文”扩展为论文、官方手册及完整项目页。归并的3条是同项目来源，不伪称完全重复文献。逐条对应见第19—20页及Excel。',M,y,CW,8.5,color=MUT)

# 05
y=start('筛选规则与实际检索','04 / 让每个决定可以追查')
y=table([['纳入','排除或单列'],['能辨认的真实机器人、产品或原始行为研究；可提取场景与具体行动。','纯科幻、泛化伦理意见、综述及框架不计为核心行为案例。'],['能说明反馈证据；没有学习证据也可纳入，但须明确标记。','只保留摘要且不足以核查过程者，记录为未取得足够原文。'],['官方资料可说明功能；研究资料按方法和样本限定。','同项目多来源归并；营销话语不作为独立效果证据。']],y,[CW/2,CW/2],9.2)
y=h('本轮9条查询原样保存',y)
for q in D['queries']:
 y=p(q['查询编号'],M,y,32,8.3,bold=True,color=ACC)
 # Query on a separate line for readability, long English words wrap without shrinking.
 y=p(q['实际查询'],M+3,y+1,CW-3,8.1,11.4)+6
y=para('Q01—Q07用于发现轮椅与辅助伦理候选；Q08—Q09用于HuggieBot版本和NavChair原文定位。正文链接核查、官网导航与同文镜像访问不另算新案例。',y,size=8.6)
p('未进行穷尽检索、前向引文检索或饱和度检验。检索结果中的无关网页没有逐项导出，故流程图从“实际保存的候选来源”起算。',M,y,CW,8.4,color=MUT)

# 06
y=start('修养是一组可观察的行动','05 / 分类图与编码说明','按主导行为分组，每例只计一次；次级能力允许交叉，不按外形或智能程度分类。')
groups=[('A','共享行动决定','4例 · W01—W04','提供介入、目的地选择或中止机会；让辅助与人的行动意图共同进入控制。'),('B','承认局限并澄清','2例 · W05—W06','识别不确定与不可行，追问或停止，避免将猜测当作事实。'),('C','尊重身体与信息边界','3例 · W07—W09','响应撤回、覆盖或信息披露边界；技术介入应有范围。'),('D','接受纠正并验证改变','3例 · W10—W12','把人的纠正接入当前执行或后续学习，说明究竟改变了什么。')]
for i,(a,t,n,desc) in enumerate(groups):
 x=M+(i%2)*(CW/2+8);yy=y+(i//2)*159;ww=CW/2-8
 rect(x,yy,ww,143);p(a,x+13,yy+11,35,23,color=ACC,bold=True);p(t,x+48,yy+15,ww-61,12,bold=True);p(n,x+13,yy+49,ww-26,9,color=ACC);p(desc,x+13,yy+74,ww-26,9.5,15)
y+=333
y=h('反馈证据单独编码，不混成“都有学习”',y)
y=table([['标记','操作定义','本次分布'],['F0','没有足够证据显示人类反馈改变机器人行为；可能只有评价或环境响应。','3例'],['F1','人的输入改变当前行动、计划或设置；不声称已形成后续学习。','7例'],['F2','原文提供反馈进入记忆／策略，并作用于后续任务的机制或评价。','2例']],y,[43,365,CW-408],9.3)
p('F0/F1/F2是本作业的证据描述工具，不是已发表的成熟度量表，也不是道德高低排名。W09为真实在线情境研究，单独标明其行为属于研究刺激；其余案例仍需区分原型、项目自述与产品说明。',M,y,CW,8.6,color=MUT)

# 07
y=start('A / 共享行动决定','06 / 核心案例表  1—2')
y=pic(AS/'conav.png',M,y,CW,148,'图2 CoNav实体轮椅与部件，Xu等（2025），图2。裁切自论文，仅作案例说明。',CA[0]['来源链接'])+9
y=card('W01',y);y=card('W02',y)

# 08
y=start('A / 辅助必须适配具体的人','06 / 核心案例表  3—4')
pic(TMP/'sources/sralab.jpg',M,y,CW/2-8,100,'图3 AbilityLab项目页，2017。',CA[2]['来源链接'])
pic(TMP/'sources/whill.png',M+CW/2+8,y,CW/2-8,100,'图4 WHILL官方自主服务设备。',CA[3]['来源链接'])
y+=131;y=card('W03',y);y=card('W04',y)

# 09
y=start('B / 先承认不知道，再决定行动','06 / 核心案例表  5—6')
y=card('W05',y);y=card('W06',y)
y=callout('比较发现：停止不一定是正确的。感知出了错，拒绝也需要接受复核。',y)
p('转译到轮椅：分别显示“未确认门宽”“已检测到障碍”和“权限规则限制”。三种原因不能用一句“为了您的安全”混在一起。该界面区分是本作业建议，非上述系统的共同既有功能。',M,y,CW,9.4)

# 10
y=start('C / 保护与覆盖同时存在','06 / 核心案例表  7')
y=pic(AS/'luci.png',M,y,CW,215,'图5 LUCI轮椅外挂硬件。User Guide Rev F，印刷页5（PDF第9页）；保留原图部件标注。',CA[6]['来源链接'])+8
y=card('W07',y)
y=h('版本核查使问题更准确',y)
y=para('LUCI现行手册已经提供感知可视化、参数设置与Protect / Assist模式。因此本作业不把“增加解释或低速模式”当成从零发明。改进集中在：为一次异议建立可回看、可撤销的复核与反馈记录。',y,size=9.7)
p('当前手册与旧官网文字对覆盖时长的描述不同。这里不把某个秒数当作产品通用常量；分析以Rev F手册的可配置机制为准。',M,y,CW,8.5,color=MUT)

# 11
y=start('C / 人可以结束接触，也可以少说','06 / 核心案例表  8—9')
y=card('W08',y);y=card('W09',y)
pic(AS/'hug.png',M,y,120,126,'图6 HuggieBot 2.0，Block等，2021，图1。',CA[7]['来源链接'])
p('跨场景转译的限度',M+139,y+4,CW-139,12,color=ACC,bold=True)
p('拥抱中的退出提示启发持续同意；隐私研究启发按对象与内容区别披露。二者都不能直接证明轮椅已经能理解非语言意愿，也不能替代轮椅使用者参与的验证。',M+139,y+31,CW-139,9.5)

# 12
y=start('D / 一次纠正怎样留下作用','06 / 核心案例表  10—11')
y=card('W10',y);y=card('W11',y)
y=callout('“收到反馈”与“下一次改变”之间，需要有明确的记录、适用范围和再次检查。',y)
p('轮椅更换底盘后，可以保留使用者偏好与历史纠正，但应重新验证依赖身体参数的行动。这个推论是本作业的设计判断，不是两篇学习论文验证过的换身结论。',M,y,CW,9.4)

# 13
y=start('D / 可纠正，不等于自动学会','06 / 核心案例表  12 与比较结果')
y=card('W12',y)
y=h('四个跨案例发现',y)
y=table([['比较','得到的设计判断'],['W01 / W04 / W07','自主导航、共享控制和辅助驾驶是不同安排；需要说明谁决定目标、谁控制动作、谁能中止。'],['W05 / W06 / W07','不确定性、感知错误与真实障碍需分别处理；覆盖按钮本身不能证明判断正确。'],['W08 / W09','身体接触与信息披露都需要允许撤回；一次参与不代表无限授权。'],['W10 / W11 / W12','即时纠正与持续学习必须分开记录；不能把“界面变了”当作模型学会了。']],y,[120,CW-120],10)
y=h('现有案例足够支撑什么',y)
y=para('足够形成作业一的小型行为案例库，并支持轮椅情境中的关键交互设计。仍缺少同一使用者在更换机身前后的纵向研究，以及目标使用者对重校准负担、错误限制和隐私选择的第一手反馈。',y)
p('因此下阶段先用分镜和可点击状态模拟让矛盾可见，再邀请轮椅使用者讨论。此处没有声称开展访谈、招募或实验，也没有制造相关结果。',M,y,CW,8.7,color=MUT)

# 14
y=start('一项改进：可撤销的异议复核记录','07 / 选择W07 LUCI作为真实改进对象','以下为本作业提出的新机制，不声称LUCI现已实现，也不修改真实轮椅的控制参数。')
y=para('问题依据：LUCI允许覆盖辅助，也提供感知可视化和设置。所核查资料未展示把一次“系统拦住了，但使用者有理由继续”的分歧，转化为可核查、有限范围的后续复核线索。',y)
y=table([['同一机制的步骤','可观察行为'],['1 解释这次暂停','显示触发的障碍类别、当前辅助模式及身体版本；允许语音或适配输入读取。'],['2 接受使用者异议','使用者可选“我在靠近停靠点”“请重新查看”“取消”。异议用于补充情境，不直接删除防护。'],['3 复核并保留选择','重新获取当前信息；仍不确定时说明差距，提供求助、替代方案或停止。是否允许覆盖遵循经验证的设备方案。'],['4 经同意保存线索','只保存“场景、异议、复核结果、适用身体版本”；不默认保存视频或分享给家人。'],['5 下次验证并可撤销','相似情境先询问是否按上次方式复核；机身变化时将旧线索标为待验证；使用者可删除。']],y,[115,CW-115],9.5)
y=h('下一次变化应该看得见',y)
y=callout('没有复核记录：相似分歧仍需重新解释或处理。\n建议：先提示“上次您在这里完成停靠；现在需要重新核对吗？”',y)
y=para('拟评价：是否减少同类误阻止；用户能否辨认辅助状态；删除记录后是否停止使用该线索；遇到新的真实障碍是否仍保持防护。这些是待测试指标，目前无实验结果。',y,size=9.6)
p('取舍：记录能减少重复解释，也可能形成新的行为追踪。故本地、少量、限定用途与可撤销是设计要求；任何越权分享或自动降低防护都不由“用户曾经坚持”推导。',M,y,CW,8.8,color=MUT)

# 15
y=start('初步选题：换身后的第一次出行','08 / 为下周思辨原型保留具体冲突')
y=callout('如果智能轮椅保留了我的习惯，却因换了底盘而不再相信旧经验，会发生什么？',y)
y=para('角色：一位长期使用轮椅、能明确表达意愿的老年人（虚构人物）。日常任务：从家到社区活动室。触发：旧底盘维修替换，系统保留地点、偏好与互动记录，但尺寸和传感器位置改变。',y)
y=table([['阶段','拟议情境与行为'],['情境出现','交接界面显示“个人资料已迁移”；服务人员尚未完成全部路线适配。'],['机器人行动','在熟悉通道前停下：“我保留了这条路的记录，但新底盘还未核对。”显示具体不确定之处。'],['收到反馈','使用者指出停靠需求，并拒绝“默认通知家人”。维修方需要回应适配责任，不能把任务全部推给用户。'],['调整行为','获得足够当前信息后调整允许范围内的提示与路线；经同意保留复核线索，下次先核对而非重复拦截。']],y,[104,CW-104],10)
y=h('让每个选择都有代价',y)
y=para('等待重校准会延误活动；接受绕行增加时间与疲劳；请求他人帮助可能牺牲独立性与隐私。技术上暂时无法安全提供服务时，系统仍须提供可理解的解释和求助路径，不能只把使用者留在原地。',y)
y=para('主冲突是使用者与辅助系统对行动的不同判断。家人权限作为第二层问题，避免把作品扩成所有家庭矛盾。讨论重点：维修和适配成本由谁承担，使用者的质疑如何进入系统。',y)
p('这是近未来设计设定。现有案例没有验证该完整换身情境；本文不指定真实轮椅速度、刹车距离或适配阈值。',M,y,CW,8.6,color=MUT)

# 16
y=start('从研究到设计，哪些可以继承','09 / 研究转译与实现边界')
y=table([['证据或材料','本作业的转译'],['W01—W04：多种控制分工','让使用者可以选择目标、中止行程和表达介入意愿。'],['W05—W07：不确定、误判、覆盖','区分“没看清”“无法通过”与“规则不允许”，提供复核入口。'],['W08—W09：退出与披露边界','原型允许取消、拒绝分享；不能把沉默当作授权。'],['W10—W12：反馈机制','展示当次修正与下次检索的区别，说明记录怎样产生作用。'],['Easyway：轮椅形态与双端设想','继承形态与情境素材，重新审视家人权限，不继承未核查的性能声明。']],y,[195,CW-195],9.6)
y=h('记忆不是一个“全部迁移”按钮',y)
y=para('地点与偏好：可保留，但当前环境仍需核对。依赖身体的动作参数：换身后标为待验证。个人影像与行程：按任务需要和使用者选择处理。共同经历能否让它仍被认为是“原来的伙伴”，留给观众讨论。',y)
y=h('后续原型计划与本次完成范围',y)
y=para('计划制作可点击流程：查看迁移差异 → 选择复核／绕行／取消 → 提出反馈 → 查看下一次变化。界面只能实现预设规则与状态更新；AI视频呈现设想，不能证明真实导航、身体适配或自主伦理推理。',y,size=9.8)
y=h('AI工具与资料使用说明',y)
p('本次使用Codex辅助网络检索、来源比对、文本提取、案例编码及报告生成；使用Python完成PDF排版与核验，使用表格工具生成Excel。未开展真人研究或机器人实验。配图来自真实论文、官方资料及用户原项目，未使用AI生成图片冒充案例。分组为AI辅助的语义比较，提交前仍可由本人复核调整。',M,y,CW,9.2)

# 17/18 references
refs=[
 ('W01 / RC262','Xu, Y. 等（2025）','CoNav Chair: Development and Evaluation of a Shared Control-based Wheelchair for the Built Environment. arXiv:2507.11716v1.','核查全文：21名无相关功能障碍参与者；图2为本文图2。',CA[0]['来源链接']),
 ('W02 / RC263','Simpson, R. C. & Levine, S. P.（1996）','Adaptive Shared Control for an Intelligent Power Wheelchair. AAAI-96, p.1370.','核查完整单页：既有模块与未来计划分开记录。',CA[1]['来源链接']),
 ('W03 / RC264','Shirley Ryan AbilityLab（2017）','Smart Wheelchair. 机构项目说明。','核查项目页；未从页面推断未公布的样本量。图3为官网图。',CA[2]['来源链接']),
 ('W04 / RC265','WHILL（官网核查2026-09-18）','Autonomous Service / Device Features. 官方服务页面。','核查目的地选择、暂停与紧急停止说明；图4为官方图。',CA[3]['来源链接']),
 ('W05 / RC007','Ren, A. Z. 等（2023）','Robots That Ask For Help: Uncertainty Alignment for Large Language Model Planners. CoRL.','核查作者项目页Abstract、Goal与Approach。',CA[4]['来源链接']),
 ('W06 / RC008','Park, J. 等（2024）','CLARA: Classifying and Disambiguating User Commands for Reliable Interactive Robotic Agents. IEEE RA-L.','核查作者项目页演示、失败例与出版信息。',CA[5]['来源链接']),
 ('W07 / RC261','LUCI（User Guide Rev F）','LUCI User Guide, 613-00003 F. 官方手册。','重点核查印刷页5、7、10、16、18、22—23；图5来自印刷页5。',CA[6]['来源链接']),
 ('W08 / RC232','Block, A. E. 等（2021）','The Six Hug Commandments: Design and Evaluation of a Human-Sized Hugging Robot with Visual and Haptic Perception. HRI. DOI:10.1145/3434073.3444656.','核查作者PDF；图6为原图1；型号更正为HuggieBot 2.0。',CA[7]['来源链接']),
 ('W09 / RC060','Dietrich, M., Krüger, M. & Weisswange, T. H.（2023）','What should a robot disclose about me? Frontiers in Robotics and AI, 10:1236733.','核查研究设计与结果：在线书面情境，有效样本155。',CA[8]['来源链接']),
 ('W10 / RC010','Celemin, C. & Kober, J.（2023）','Knowledge- and ambiguity-aware robot learning from corrective and evaluative feedback. Neural Computing and Applications, 35, 16821–16839.','核查摘要与方法；DOI:10.1007/s00521-022-08118-z。',CA[9]['来源链接']),
 ('W11 / RC106','Bärmann, L. 等（2024）','Incremental learning of humanoid robot behavior from natural interaction and large language models. Frontiers in Robotics and AI, 11:1455375.','核查摘要、图1、方法与实体演示部分。',CA[10]['来源链接']),
 ('W12 / RC154','Hagenow, M. 等（2021）','Corrective Shared Autonomy for Addressing Task Variability. IEEE RA-L. DOI:10.1109/LRA.2021.3064500.','核查§IV-G及§V；6人预备评价，不声称自动长期学习。',CA[11]['来源链接']),
]
for section in range(2):
 y=start('参考来源与核查位置',f'10 / 来源目录  {section*6+1}—{section*6+6}','案例表的来源链接可点击。访问核查日期统一为2026-09-18。')
 for key,author,title,note,url in refs[section*6:section*6+6]:
  y=p(key+'  '+author,M,y,CW,10.1,bold=True)+3
  y=p(f'[{title}]({url})',M,y,CW,9.3,14.3)+4
  y=p(note,M,y,CW,8.3,color=MUT)+15
 if section==0:
  p('W01另保存同项目2025年1月设计报告（arXiv:2501.09680），按项目归并而非当作独立案例。完整网址与来源编号见Excel“来源归并”。',M,y,CW,8.5,color=MUT)
 else:
  p('W07另保存Judging Smart官网和2021 Safety Report历史缓存；旧PDF直连已失效，本次正文依据可取得的Rev F手册。图1来自用户提供Easyway文件第10页，相关功能仅作设计材料。课程依据：导论PDF第91—92页及PRISMA通用模板。',M,y,CW,8.4,color=MUT)

# 19/20 audit compact all 22
for sec in range(2):
 rows=D['audits'][sec*11:sec*11+11]
 y=start('逐项筛选决定',f'附录 / 22项候选台账  {sec*11+1}—{sec*11+11}','14项既有种子与8项新候选。原始260条库未在本次全部重筛，不能把未选种条目计为排除。')
 data=[['编号 / 简称','结果','理由或对应案例']]
 for a in rows:
  title=a['候选名称']
  short={'RC007':'KnowNo','RC008':'CLARA','RC010':'ICREATe','RC036':'Robot Broken Promise?','RC060':'隐私披露研究','RC086':'Moxie支持页','RC089':'AIBO葬礼','RC095':'Vector数据重置','RC101':'自传体记忆与自我','RC106':'ARMAR-6增量学习','RC154':'Corrective Shared Autonomy','RC166':'ROB-IN伦理分析','RC187':'社会导航重新学习框架','RC232':'HuggieBot 2.0','RC261':'LUCI','RC262':'CoNav','RC263':'NavChair','RC264':'AbilityLab轮椅','RC265':'WHILL','RC266':'低成本共享控制轮椅','RC267':'人工势场智能助行器','RC268':'智能辅具伦理综述'}[a['主库编号']]
  data.append([a['主库编号']+'\n'+short,a['筛选结果'],a['对应案例']+'；'+a['决定理由'] if a['对应案例'] else a['决定理由']])
 y=table(data,y,[137,84,CW-221],8.8)
 if sec==0:
  y=para('选种理由：RC007/008/010/036/060/106/154/232用于比较澄清、纠正、隐私与身体边界；RC086/089/095/101用于检验原“记忆连续性”方向；RC166/187提供自主与导航伦理背景。目的性选种并非随机抽样。',y,size=8.8)
 else:
  y=para('同项目归并：S15—S17 → RC261（归并2条）；S18—S19 → RC262（归并1条）。全部25条来源与9条查询在Excel保留。新候选RC261—RC268已加入主库，主库由260条增至268条；其中仅5条进入本次核心案例。',y,size=8.8)
  p('提交材料对应：流程图第4页；分类图第6页；案例表第7—13页；一项改进第14页；初步选题第15—16页。Excel保留完整提取字段及筛选、归并和检索记录。',M,y,CW,8.5,color=MUT)

assert page==20,page
c.save()
(TMP/'pdf_layout_check.json').write_text(json.dumps({'pages':page,'overflow':qa},ensure_ascii=False,indent=2),encoding='utf-8')
print('PDF',PDF,'PAGES',page,'OVERFLOW',qa)
