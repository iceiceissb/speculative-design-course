from pathlib import Path
import fitz, zipfile, json, hashlib
from PIL import Image,ImageDraw
root=Path('作业二/提交_这一次轮椅该听谁的')
images=sorted(Path('tmp/assignment2/slides').glob('*.png'))
assert len(images)==16
pdf=fitz.open()
for im in images:
    page=pdf.new_page(width=960,height=540)
    page.insert_image(page.rect,filename=str(im))
urls=['https://www.luci.com/hubfs/Luci_April2026/pdf/613-00003_F_LUCI-User-Guide_Color-1.pdf','https://arxiv.org/abs/2507.11716','https://clararobot.github.io/','https://www.frontiersin.org/journals/robotics-and-ai/articles/10.3389/frobt.2024.1455375/full']
for i,url in enumerate(urls):
    y=(175+i*109+70)*.75
    pdf[15].insert_link({'kind':fitz.LINK_URI,'from':fitz.Rect(48,y,905,y+21),'uri':url})
pdf.set_metadata({'title':'这一次，轮椅该听谁的？｜原型v1演示备份','subject':'固定版式备份；可编辑文字和表格见同目录PPTX；情境为设计虚构','creator':'Codex + Artifact Tool / PyMuPDF'})
out=root/'演示备份_这一次轮椅该听谁的_v1.pdf'
pdf.save(out,garbage=4,deflate=True)
pdf.close()
check=fitz.open(out)
assert len(check)==16 and len(check[15].get_links())==4
print(json.dumps({'pdf':str(out),'pages':len(check),'source_links':4,'bytes':out.stat().st_size},ensure_ascii=False))
sheet=Image.new('RGB',(1600,980),'#f4f2ec');d=ImageDraw.Draw(sheet)
for i,p in enumerate(images):
    im=Image.open(p);im.thumbnail((388,218))
    x=(i%4)*400;y=(i//4)*245
    sheet.paste(im,(x,y));d.text((x+8,y+223),str(i+1).zfill(2),fill='#285c52')
sheet.save('tmp/assignment2/deck-contact.png')
