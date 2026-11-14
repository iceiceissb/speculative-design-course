from pathlib import Path
import json, subprocess, sys
from PIL import Image, ImageDraw
ROOT=Path(__file__).resolve().parents[2]
a=json.loads((ROOT/'tmp/video-workflow/contact/index.json').read_text(encoding='utf-8'))
indices=[3,8,11,12,16,21,24,25,26,31,40]
sheet=Image.new('RGB',(1280,len(indices)*205),'#f7f5ef');draw=ImageDraw.Draw(sheet)
for row,index in enumerate(indices):
    e=a[index]
    for col,t in enumerate([0,1,2,3]):
        p=ROOT/f'tmp/video-workflow/contact/slope_{index}_{col}.jpg'
        subprocess.run(['ffmpeg','-hide_banner','-loglevel','error','-ss',str(t),'-i',e['path'],'-frames:v','1','-vf','scale=320:-1','-y',str(p)],check=True)
        sheet.paste(Image.open(p),(col*320,row*205));draw.text((col*320+8,row*205+181),f'{index:02} / {t}s',fill='#23382b')
sheet.save(ROOT/'tmp/video-workflow/contact/slope_sequences.jpg')
print('done')
