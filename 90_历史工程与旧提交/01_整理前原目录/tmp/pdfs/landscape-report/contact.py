from pathlib import Path
from PIL import Image,ImageDraw
p=Path(__file__).parent
files=sorted(p.glob('page-*.png'))
for start in range(0,len(files),6):
    group=files[start:start+6]
    sheet=Image.new('RGB',(1440,3*432),'#d5d2c9')
    for j,f in enumerate(group):
        im=Image.open(f).convert('RGB');im.thumbnail((704,396))
        x=(j%2)*720+8;y=(j//2)*432+27
        sheet.paste(im,(x,y));ImageDraw.Draw(sheet).text((x,y-20),f.stem,fill='black')
    sheet.save(p/f'contact-{start//6+1}.jpg',quality=92)
print(len(files))
