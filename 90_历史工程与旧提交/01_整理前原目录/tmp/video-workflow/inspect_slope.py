from pathlib import Path
import json
import subprocess
from PIL import Image, ImageDraw, ImageFont

root = Path(__file__).resolve().parents[2] / 'output' / 'AI视频工作流'
state = json.loads((root / 'state.json').read_text(encoding='utf-8-sig'))
selected = state['selection']
items = {item['id']: item for item in state['candidates']}
out = root / 'reports' / 'finecut-inspection'
out.mkdir(exist_ok=True)
rows = [('E', [0.3, 1.2, 2.2, 3.2, 4.2]), ('E', [5.2, 6.1, 7.1, 8.1, 9.2]),
        ('22', [.2, .8, 1.5, 2.4, 3.5]), ('35', [.2, .8, 1.5, 2.4, 3.5]),
        ('24', [.2, .8, 1.5, 2.4, 3.5])]
font = ImageFont.truetype('C:/Windows/Fonts/msyh.ttc', 18)
canvas = Image.new('RGB', (1280, 880), '#eeeeee')
draw = ImageDraw.Draw(canvas)
for row, (job, times) in enumerate(rows):
    source = root / items[selected[job]]['file']
    for col, at in enumerate(times):
        frame = out / f'{row}_{col}.jpg'
        subprocess.run(['ffmpeg', '-hide_banner', '-loglevel', 'error', '-ss', str(at),
                        '-i', str(source), '-frames:v', '1', '-vf', 'scale=256:144',
                        '-y', str(frame)], check=True)
        canvas.paste(Image.open(frame), (col * 256, row * 176 + 30))
        draw.text((col * 256 + 8, row * 176 + 4), f'{job} / {at:.1f}s', font=font, fill='#222222')
canvas.save(out / 'sources-contact.jpg')
print(out / 'sources-contact.jpg')
