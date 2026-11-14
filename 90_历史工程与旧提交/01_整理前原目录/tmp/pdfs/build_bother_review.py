from pathlib import Path
import re,json,io
from xml.sax.saxutils import escape
from PIL import Image
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.colors import HexColor
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import Paragraph
from reportlab.lib.utils import ImageReader
from pypdf import PdfReader

ROOT=Path(r'D:/课/大四上/思辨设计')
ASSETS=ROOT/'output/故事板_定格版/完整分镜'
OUT=ROOT/'output/pdf/不用麻烦她_完整分镜审阅版'
OUT.mkdir(parents=True,exist_ok=True)
W,H=1280,720
pdfmetrics.registerFont(TTFont('CN',r'C:/Windows/Fonts/msyh.ttc',subfontIndex=0))
pdfmetrics.registerFont(TTFont('CNB',r'C:/Windows/Fonts/msyhbd.ttc',subfontIndex=0))
pdfmetrics.registerFontFamily('CN',normal='CN',bold='CNB')
PAPER='#F8F5EE'; INK='#293A33'; MUTED='#777B70'; ACCENT='#92744E'
source=(ROOT/'output/故事板_定格版/01_完整故事板提示词_待确认.md').read_text(encoding='utf-8')
chunks=re.findall(r'### (\d{2})｜([^\n]+)\n(.*?)(?=\n### |\n## 四|\Z)',source,re.S)
stories='''以前，每次去河边，邱懿贞都会约徐月禾。徐月禾推着普通轮椅，经过帽子店却停下看橱窗。邱懿贞回头催她，两个人一路拌嘴。
到了常去的钓位，徐月禾扣好轮椅刹车，支起折叠凳。两杯茶放好，抄网搁在手边。她们在这儿坐过很多个下午。
鱼咬钩了。邱懿贞侧身控竿，轮子下的碎石轻轻错动。徐月禾一手稳住推把，另一手伸抄网；长柄压在一只手上，网口歪了。
邱懿贞想腾手接网，竿尖却垂了下去，只好重新握紧。鱼一翻身，脱钩了。徐月禾拉回空网，两人还保持着刚才别扭的姿势。
徐月禾放下网，揉了揉手腕。邱懿贞把茶递过去。徐月禾提起一种能自己走、停下还能撑稳的轮椅。两人约好一起去试。
几天后，两人来到辅具体验室。邱懿贞换坐秀秀，起初握紧扶手，只让它走一小段。徐月禾跟在旁边，陪她来回试。
秀秀停在模拟河岸的泥土地面。支撑脚从底盘展开，宽脚垫贴地，短锚钉压进泥土。邱懿贞侧身伸手，椅子没有晃。
秀秀的机械臂托住抄网后段，徐月禾握住前段试方向。她夸了一句，秀秀便举起另一只手。她愣了愣，笑着拍了一掌。
邱懿贞试过后决定换椅子。秀秀送到家那天，徐月禾帮她把旧杯架、钓具袋移过去。普通轮椅留在旁边，东西还是她们用惯的。
出门时，徐月禾习惯性握住推把，秀秀已经自行越过门槛。她松了手。两人看着新椅子，确实觉得日子方便了。
清晨，秀秀帮邱懿贞擦脸、整理衣服。出门前备好钓具，走到不平处会减速。许多原先需要请人帮忙的事，现在自己就能完成。
晚上，邱懿贞写好邀约，还没发送，秀秀已经备齐明天的钓具。她看看消息，觉得既然轮椅能送自己，就不用再叫朋友了。
第二天，秀秀独自载她经过同一家帽子店。她看见那顶奇怪的帽子，下意识转头说话。说了一半，才发现身旁没有人。
到了河边，秀秀停稳。邱懿贞拿出两只杯子，照旧把一只递向旁边。手停了一会儿，那只杯子又被放回包里。
秀秀真的能帮她把鱼抄上来。它举起手等击掌，邱懿贞却忙着拍鱼。她只给徐月禾发了一张照片。那只机械手等了片刻，收了回去。
徐月禾买了两份吃的，出门才想起今天没有约邱懿贞。她看看手机，又放下。她以为有秀秀照顾，朋友已经不需要自己来回跑。
后来，第二只杯子不再带出门，折叠凳也留在家里。秀秀发现邱懿贞越来越安静，便报天气、讲鱼情、放音乐。她叫它安静一会儿。
一个下午，邱懿贞从柜旁拿出折叠凳，擦了擦，又放下。她看着这件许久没带出门的东西，坐了一会儿。
邱懿贞把秀秀切到普通推行模式。自动行驶暂停了。她打开与徐月禾的聊天框，开始找一个能请朋友过来的理由。
她写了一条消息，说轮椅不太方便，想请徐月禾来。手指停在发送键前。这句话还只是草稿，徐月禾并没有收到。
秀秀检查供电与驱动，没有发现故障，准备恢复自动行驶。邱懿贞按住扶手，叫它先别修。屋里静下来，她也说不出究竟坏了哪里。
邱懿贞删掉借口，改发语音。第一遍说了半句又取消，第二遍终于把话说完。这次没有再加“你要是忙就算了”。
秀秀收起自动行驶提示。邱懿贞等到徐月禾的回复，又听了一遍，打开收纳格。那只留下的杯子，也要重新带上。
第二天下午，徐月禾来到家里，又把手放上推把。秀秀正要接过来，邱懿贞拍拍扶手，让朋友推一段。制动和稳定辅助仍然保留。
两人再经过帽子店。徐月禾在后面讲检查时的趣事，邱懿贞几次转头没听清，便叫她到身旁来。秀秀恢复自动行驶，跟着她们的步调。
到河边，秀秀先展开支撑脚。徐月禾习惯性握住推把，邱懿贞朝底盘指了指。她低头看见椅子已经撑稳，松开手，把凳子搬到旁边。
浮漂突然沉下去。邱懿贞提竿收线，徐月禾起身。轮椅停得稳稳的，这次她不必先去抓推把。
徐月禾的衣角带歪了饵盒。秀秀接住盒子，又伸手想扶竿；邱懿贞已握稳。人、竿、盒子同时在动，它短短半拍没跟上。
秀秀放好饵盒，抽出抄网。徐月禾双手掌握前段的方向，机械手托住后段的重量。邱懿贞控竿，把鱼慢慢带到网口。
鱼靠近了，尾巴一甩。徐月禾忍住没有抢着抬网，等邱懿贞喊出那一声。她定住方向，秀秀托起网柄，鱼整个落进网兜。
网收回岸上，鱼在里面扑腾。两人笑着看鱼，没注意秀秀又举起了手。那只手悄悄往她们中间挪了一点。
徐月禾拍完，秀秀没有立刻收手，又转向邱懿贞。邱懿贞也伸手碰了一下。等两个人都拍过，它才把手收回。
鱼放进桶里，两人重新坐下。秀秀把伞偏向中间，罩住她们。两只旧杯子放在手边。鱼线再落进水里，她们继续聊那顶帽子。'''.splitlines()
dialogues=[
'邱懿贞：到底是陪我钓鱼，还是拿我当购物车？',
'水声。杯子轻轻碰在一起。',
'邱懿贞：再往左一点。\n徐月禾：我知道，手腾不开！',
'徐月禾：又差一只手。',
'邱懿贞：下回换个地方吧。\n徐月禾：换个地方，鱼也得抄上来呀。\n邱懿贞：嫌我沉了？\n徐月禾：我这手还得留着钓鱼呢。',
'邱懿贞：先走一点。好，停。',
'电机轻响，泥土被缓缓压实。',
'徐月禾：这个好。\n一声轻轻的击掌。',
'钓具袋的扣子合上。',
'秀秀：我来就好。\n徐月禾：这下可用不着我了。\n邱懿贞：可算不用使唤你了。',
'水滴声、布料摩擦声。',
'草稿：明天有没有空，推我去河边？你要是忙就算了。\n秀秀：路线安排好了，我可以送您过去。\n邱懿贞：也是。那就不麻烦她了。\n她删掉草稿。',
'邱懿贞：月禾，你看那个——\n声音停在半句。',
'水声。无人接过那只杯子。',
'手机拍照声。她没有看见举起的手。',
'纸袋沙沙作响。没有拨出的电话。',
'邱懿贞：安静会儿。\n音乐停下，只剩水声。',
'擦拭凳面的声音。',
'控制屏：自动行驶已暂停。',
'未发送的草稿：轮椅不太方便了，明天能不能来一趟？',
'秀秀：可以恢复自动行驶。\n邱懿贞：先别修。\n停顿。\n秀秀：要我告诉她，哪里坏了吗？\n邱懿贞：也没哪儿坏。',
'邱懿贞：月禾，明天陪我出去坐坐吧。',
'徐月禾（语音）：明早我要去检查。下午两点吧，你把茶带上。\n邱懿贞：那只杯子也拿来。',
'秀秀：我来——\n邱懿贞：让她推一段。',
'邱懿贞：到这边来。你在后面说话，我还得扭着脖子。',
'电机声停下。徐月禾松开推把。',
'鱼线绷紧，衣料窸窣。',
'秀秀：我先——\n邱懿贞：抄网！这还用问！',
'邱懿贞：别追它，等我带过来。',
'邱懿贞：现在！\n水花、笑声。',
'徐月禾：看见了，有你的份。',
'邱懿贞：一个都不能少是吧。\n另一声击掌。',
'闲聊声与河水声。\n画面渐暗。']
assert len(chunks)==len(stories)==len(dialogues)==33
def chapter(i):
 return '一 · 以前那段路' if i<5 else '二 · 秀秀来了' if i<11 else '三 · 不用麻烦她' if i<17 else '四 · 先别修' if i<23 else '五 · 到这边来' if i<26 else '六 · 抄网'
def img(n):
 fs=sorted(ASSETS.glob(n+'_*.png'))
 assert fs,f'Missing {n}'
 return fs[-1]
for n,_,_ in chunks:img(n)
c=canvas.Canvas(str(OUT/'不用麻烦她_完整分镜与剧本_16比9.pdf'),pagesize=(W,H),pageCompression=1)
c.setTitle('不用麻烦她｜完整分镜与剧本');c.setAuthor('思辨设计课程作品')
page=0;bounds=[]
def text(s,x,y,w,sz=20,bold=False,color=INK,leading=None):
 st=ParagraphStyle('p',fontName='CNB' if bold else 'CN',fontSize=sz,leading=leading or sz*1.6,wordWrap='CJK',textColor=HexColor(color))
 p=Paragraph(escape(s).replace('\n','<br/>'),st);_,h=p.wrap(w,9999)
 assert y-h>=38,(page,s[:20],y,h)
 p.drawOn(c,x,y-h);bounds.append([page,x,y-h,w,h]);return y-h
def new(section,title):
 global page
 if page:c.showPage()
 page+=1;c.setFillColor(HexColor(PAPER));c.rect(0,0,W,H,fill=1,stroke=0)
 c.setFillColor(HexColor(MUTED));c.setFont('CN',11);c.drawString(22,692,section)
 c.drawRightString(1258,692,'不用麻烦她 · 剧本审阅')
 text(title,22,674,1200,25,True)
 c.setStrokeColor(HexColor('#DDD9CF'));c.line(22,36,1258,36)
 c.setFont('CN',10);c.setFillColor(HexColor(MUTED));c.drawString(22,18,'思辨设计 / 机器人自我修养');c.drawRightString(1258,18,f'{page:02d}')
 c.bookmarkPage('p'+str(page));c.addOutlineEntry(title,'p'+str(page),0)
def picture(path,x,y,w,h):
 im=Image.open(path).convert('RGB');iw,ih=im.size;s=min(w/iw,h/ih);dw,dh=iw*s,ih*s
 buf=io.BytesIO();im.save(buf,'JPEG',quality=92,subsampling=0);buf.seek(0)
 c.drawImage(ImageReader(buf),x+(w-dw)/2,y+(h-dh)/2,dw,dh)
new('故事概览','不用麻烦她')
picture(img('33'),22,155,830,467)
y=text('当帮助不再必要，\n我们还会主动邀请彼此吗？',887,607,348,27,True)
y=text('邱懿贞换上智能轮椅秀秀，终于不用每次都请徐月禾推自己去钓鱼。秀秀越能干，两位老朋友见面的理由却越少。',887,y-25,348,19)
y=text('直到邱懿贞想把一台没有坏的轮椅说成坏了，秀秀第一次不知道该把什么修好。',887,y-18,348,19)
text('秀秀认定的修养：不让主人麻烦别人。\n故事追问：它能否分辨“替人做事”与“让人一起做事”？',22,132,810,19)
text('微缩定格动画质感\n完整故事板 / 33个关键帧\n附完整文字剧本',887,150,348,15,color=MUTED)
new('人物设定','两位老朋友，一张新轮椅')
cast=[('邱懿贞 · 72岁','人物设定_定格版/邱懿贞_角色设定.png','爱钓鱼，说话利落，不愿欠人情。她需要帮忙，也怕别人觉得麻烦。换椅子之后，她要学会直接说出想见朋友。'),('徐月禾 · 74岁','人物设定_定格版/徐月禾_角色设定.png','有自己的生活和安排。陪朋友出门时顺手推车、拿东西，路上也爱逛商店。她来钓鱼，是因为自己也想来。'),('秀秀 · 智能轮椅','秀秀_定格造型三选/C_轻巧折面.png','能行驶、护理、固定底盘、帮忙抄网。没有脸，喜欢举手等击掌。它很能干，也会忙乱；它把少麻烦别人当成一件好事。')]
for i,(title,path,desc) in enumerate(cast):
 x=22+i*420;picture(ROOT/'output'/path,x,341,395,260);text(title,x,310,395,24,True);text(desc,x,261,380,20)
new('世界与场景','未来已经住进普通人的日常')
picture(img('01'),22,334,597,290);picture(img('21'),646,334,612,290)
text('社区街道与河岸',22,310,580,25,True)
text('帽子店、旧铺地、两个人熟悉的钓位。出门的路线没有变，同行的人与彼此的位置却变了。河边用同一个空间，呈现“手不够用”“独自钓鱼”和“三人配合”。',22,258,570,20)
text('家与辅具体验室',646,310,580,25,True)
text('家里留着旧杯子、帆布凳和钓具袋。智能轮椅是一件新添的生活用品。冲突来自秀秀的照护逻辑，以及两个人不好意思直说的心事。试用轮椅的过程，则让这份便利变得具体。',646,258,580,20)
for i,(n,title,body) in enumerate(chunks):
 new(chapter(i),n+'  '+title)
 picture(img(n),0,74,990,557)
 x=1010;w=247;y=626
 y=text('剧情',x,y,w,12,True,ACCENT)-12
 y=text(stories[i],x,y,w,18,leading=28)-25
 y=text('对白 / 声音',x,y,w,12,True,ACCENT)-11
 # Text stays comfortably readable even on dialogue-heavy pages.
 text(dialogues[i],x,y,w,16,leading=25)

# Full prose script: one balanced two-column page per scene chapter.
script=(ROOT/'output/10月8日汇报_剧本重构/05_不用麻烦她_剧本梗概.md').read_text(encoding='utf-8')
script=script.split('## 故事',1)[1].strip()
chapters=re.split(r'(?m)^### ',script)
for section in chapters:
 if not section.strip():continue
 title,body=section.split('\n',1)
 paras=[p.strip() for p in body.split('\n\n') if p.strip()]
 size=18
 while True:
  leading=size*1.5;heights=[]
  st=ParagraphStyle('measure',fontName='CN',fontSize=size,leading=leading,wordWrap='CJK')
  for b in paras:
   p=Paragraph(escape(b).replace('\n','<br/>'),st);_,h=p.wrap(550,9999);heights.append(h+9)
  split=min(range(1,len(paras)),key=lambda k:abs(sum(heights[:k])-sum(heights[k:])))
  if max(sum(heights[:split]),sum(heights[split:]))<=553:break
  size-=.5
  assert size>=14
 new('完整文字剧本',title)
 for x,items in [(62,paras[:split]),(668,paras[split:])]:
  y=617
  for b in items:y=text(b,x,y,550,size,leading=leading)-9
c.save()
pdf=OUT/'不用麻烦她_完整分镜与剧本_16比9.pdf'
reader=PdfReader(pdf)
assert all(abs(float(p.mediabox.width)/float(p.mediabox.height)-16/9)<1e-6 for p in reader.pages)
plain='\n'.join(p.extract_text() or '' for p in reader.pages)
for n,title,_ in chunks:assert title in plain
for word in ['邱懿贞','徐月禾','抄网！这还用问！','也没哪儿坏']:assert word in plain
(OUT/'排版检查.json').write_text(json.dumps({'pages':len(reader.pages),'shots':33,'ratio':'16:9','size_bytes':pdf.stat().st_size,'bounds':bounds},ensure_ascii=False,indent=2),encoding='utf-8')
teacher='# 《不用麻烦她》分镜剧本\n\n'+ '\n\n'.join(f'## {n} {title}\n\n{stories[i]}\n\n{dialogues[i]}' for i,(n,title,_) in enumerate(chunks))
(OUT/'分镜剧本文字.md').write_text(teacher,encoding='utf-8')
print(json.dumps({'pages':len(reader.pages),'bytes':pdf.stat().st_size,'pdf':str(pdf)},ensure_ascii=True))
