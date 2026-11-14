from pathlib import Path
import json,re
import fitz
from PIL import Image, ImageDraw
root=Path(__file__).resolve().parent.parent
pdf=root/'请等下一班_v4.1_作品剧本与故事板_横版汇报.pdf'
doc=fitz.open(pdf)
out=root/'校对预览_v4.1'
out.mkdir(exist_ok=True)
text='\n'.join(p.get_text() for p in doc)
for bad in ['总有人会让','这次就是这次','有一张嘴','逐页朗读','现场不逐句','8分钟']:
 assert bad not in text,bad
assert '请等' in doc[0].get_text()
assert '现行法规' in doc[12].get_text()
for i,p in enumerate(doc):
 p.get_pixmap(matrix=fitz.Matrix(1,1),alpha=False).save(out/f'page_{i+1:02}.png')
for start in range(0,len(doc),8):
 sheet=Image.new('RGB',(1280,1560),'#deded9')
 draw=ImageDraw.Draw(sheet)
 for k in range(min(8,len(doc)-start)):
  im=Image.open(out/f'page_{start+k+1:02}.png');im.thumbnail((620,349))
  x=10+(k%2)*640;y=10+(k//2)*390
  sheet.paste(im,(x,y));draw.text((x,y+352),f'PAGE {start+k+1}',fill='#111111')
 sheet.save(out/f'contact_{start//8+1}.png')
links=sum(len(p.get_links()) for p in doc)
result={'pages':len(doc),'links':links,'replacement_chars':text.count('\ufffd'),'layout_overflow':json.loads((root/'制作文件/layout_checks_v4_1.json').read_text(encoding='utf-8'))['overflow'],'bytes':pdf.stat().st_size}
(root/'制作文件/pdf_validation_v4_1.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(result))
