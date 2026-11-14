from pathlib import Path
import json, shutil, zipfile
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
root=Path.cwd(); build=root/'tmp/yield-project'; out=root/'作业二/提交_请别替我让路'; docs=out/'研究与讲稿'
pages=json.loads((build/'narrative.json').read_text(encoding='utf-8'))
refs=json.loads((build/'refs.json').read_text(encoding='utf-8'))
notes=['# PPT 叙事与来源备注\n\n对应正式 13 页 PPT，2026-09-20。讲述用语见《课堂讲稿与答问.md》。\n']
for p in pages: notes.append(f"## 第 {p['page']} 页｜{p['title'] or '请别替我让路'}\n\n{p['notes']}\n")
(docs/'PPT叙事与来源备注.md').write_text('\n'.join(notes),encoding='utf-8')
source=['# 案例与图片来源\n\n核对日期：2026-09-20。沿用已有总库编号，六项目的性选例不改变作业一 PRISMA 数量。268 条是包含实验、产品、设计作品等类型的记录，不是 268 项现实部署效果证据。\n\n本地总库：`D:/课/大四上/思辨设计/output/机器人自我修养数据库/机器人自我修养数据库.csv`。轮椅专题：`D:/课/大四上/思辨设计/output/作业一_智能轮椅/01_核心案例提取表.csv`。\n']
details=[
 '定位：论文实验设计中的 proxemic behavior 与 Discussion，图片为 Figure 2。提取减速侧让/主动穿行作为社会信号。原实验未载人，本原型的后退由设计者改写。部分社会感知结果不等于普遍礼让规则；未采用数据库对测量指标的过度简写。',
 '定位：Concept 及 The birth of the Tele-Barista。Mika 曾任咖啡师，参与远程咖啡机器人项目。图像为项目配图，不是 Mika 肖像。官网明确由人遥操作，不能当作自主 AI 或轮椅研究的实证。',
 '定位：官方故事简介与 Project Background。项目真实存在，Thomas 与情节属于虚构。提取照护规则与本人意愿的冲突，不当社会新闻。原库 evidence_boundary 中与记忆有关的表述不作为本题依据。',
 '定位：LUCI User Guide Rev F，印刷页 16（PDF 第 20 页）等用户控制说明。图片摘自官方使用指南。停止本原型的社会性退让不等于 LUCI override，也不意味着关掉现实避障。',
 '定位：CoNav Chair，摘要、III-D、IV-C 与系统图。2025 年研究预印本；21 位无相关身体障碍的成人样本，不能推断老年/残障使用者长期效果。提取在控制过程中接受人类修正。',
 '定位：The Six Hug Commandments: Design and Evaluation of a Human-Sized Hugging Robot with Visual and Haptic Perception，感知与释放的设计要求；图片为 PDF 首页参与者与机器人照片。提取响应结束意愿，不能迁移成轮椅安全参数。'
]
for r,d in zip(refs,details):
 source.append(f"## {r['id']}｜{r['name']}\n\n类型：{r['type']}。\n\n[原始来源]({r['url']})\n\n{d}\n\n配图文件：`3D交互原型/assets/{r['image']}`。图源：{r['imageURL']}。\n")
source.append('## 课程与自有画面\n\n课程《思辨设计-Week1-案例RTD.pdf》，用户提供，重点参照页 24、51、52、58：区分事实与解释、追问规则服务谁与谁承担代价、用选择显示不同后果、反思设计者预设。\n\n四幕分镜和 3D 场景截图均来自本原型，人物、建筑、提供方规则和对话为设计虚构。图像用作课程分析，案例照片版权归原作者或项目；Three.js 的 MIT 许可单独保留。\n')
(docs/'案例与图片来源.md').write_text('\n'.join(source),encoding='utf-8')
old=(root/'作业二/请别替我让路_内容稿/04_故事案例补充与选用理由.md').read_text(encoding='utf-8')
old=old.replace('仅补充 Markdown 内容稿，没有制作 PPT 或原型。','故事补充现已落实为正式 PPT 第 4、5 页，研究转译在第 10 页。')
old=old.replace('它们先在第 5 页被介绍','它们先在第 4、5 页被分别介绍').replace('第十页分别标注','第 10 页分别标注')
(docs/'故事案例补充与选用理由.md').write_text(old,encoding='utf-8')
pdf=canvas.Canvas(str(out/'说明PPT_放映备份.pdf'),pagesize=(960,540));pdf.setTitle('请别替我让路：说明PPT放映备份')
for i in range(1,14):
 pdf.drawImage(ImageReader(str(build/'slides'/f'{i:02}.png')),0,0,width=960,height=540)
 if i==13:
  for j,r in enumerate(refs):
   x=(64+(j%3)*400)*.75;y=(180+(j//3)*235+130)*.75
   pdf.linkURL(r['url'],(x,540-y-30,x+270,540-y),relative=0,thickness=0)
 pdf.showPage()
pdf.save()
# Archive our own earlier render revisions, leaving one unambiguous deck in submission.
for n in ['说明PPT_请别替我让路_v1.pptx','说明PPT_请别替我让路_课堂版.pptx']:
 if (out/n).exists(): shutil.move(str(out/n),str(build/n))
print('DOCUMENTS_AND_PDF_READY')
