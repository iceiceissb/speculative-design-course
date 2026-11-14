from pathlib import Path
from PIL import Image,ImageOps,ImageDraw
root=Path(__file__).parent
paths=sorted(root.glob('final-*.png'))
for start in range(0,len(paths),6):
    group=paths[start:start+6]
    sheet=Image.new('RGB',(1100,3*805),'#d8d5cf')
    for j,path in enumerate(group):
        im=Image.open(path).convert('RGB');im.thumbnail((535,765))
        x=(j%2)*550+8;y=(j//2)*805+27
        sheet.paste(im,(x,y));ImageDraw.Draw(sheet).text((x,y-20),path.stem,fill='black')
    sheet.save(root/f'final-contact-{start//6+1}.jpg',quality=90)
print(len(paths))
