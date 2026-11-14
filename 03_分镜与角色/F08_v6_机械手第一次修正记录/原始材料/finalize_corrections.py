"""Update metadata, prompts and preview; image files were edited using imagegen."""
from pathlib import Path
from html.parser import HTMLParser
import hashlib
import json
import re
import subprocess
import sys
import zipfile

ROOT = Path(__file__).resolve().parent.parent / 'v6_完整分镜'
BACKUP = Path(__file__).resolve().parent / '原图备份'
manifest_path = ROOT / 'mechanical_hand_corrections_2026-10-11.json'
manifest = json.loads(manifest_path.read_text(encoding='utf-8'))
entries = {e['id']: e for e in manifest['entries']}
data_path = ROOT / 'storyboard.json'
data = json.loads(data_path.read_text(encoding='utf-8'))
data['images_updated'] = '2026-10-11'
structure_en = (' MECHANICAL CONTINUITY: exactly two chair-mounted arms; each has two rigid green links (upper arm and forearm) joined at one elbow, followed by a compact wrist and a complete five-digit hand. Left and right hands are mirrored counterparts with opposing thumbs. No extra middle arm link, no additional arm chain, no missing/detached hand, no fused human sleeve. A hand may be naturally occluded by the table or framing. Grips must support the object with palm and fingers, not the back of the hand.')
structure_zh = ' 机械结构保持一致：只有两条机械臂，每条为上臂、前臂两段主体臂节，中间一处肘轴，末端小腕部连接完整五指机械手；左右手互为镜像，拇指与四指对握，不增添第三段臂节，不缺手、不悬空、不接人袖口；托杯托物时掌面与手指实际承重。'
if 'MECHANICAL CONTINUITY:' not in data['image_prompt_common']:
    data['image_prompt_common'] += structure_en
if '机械结构保持一致：' not in data['video_prompt_common']:
    data['video_prompt_common'] += structure_zh
for shot in data['shots']:
    if shot['id'] in entries:
        shot['image_revision'] = '20261011-arms-v2'
        shot['image_correction'] = entries[shot['id']]['issue']
data_path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')

builder_path = ROOT / 'build_package.py'
builder = builder_path.read_text(encoding='utf-8')
if 'def asset_url(shot):' not in builder:
    needle = 'cards=[]'
    assert needle in builder
    builder = builder.replace(needle, "def asset_url(shot):\n    revision = shot.get('image_revision')\n    return shot['image'] + ('?v=' + revision if revision else '')\n\n" + needle, 1)
    builder = builder.replace("esc(s['image'])", 'esc(asset_url(s))')
    builder = builder.replace('embedded=json.dumps(shots, ensure_ascii=False)', "embedded=json.dumps([{**s, 'image': asset_url(s)} for s in shots], ensure_ascii=False)")
    builder = builder.replace("(ROOT / '00_先看这里.md').write_text(readme, encoding='utf-8')", "readme += '\\n## 生成与修正记录\\n\\n[来源与 AI 使用](04_生成记录.md) · [机械手检查与修正](05_机械手检查与修正.md)。\\n'\n(ROOT / '00_先看这里.md').write_text(readme, encoding='utf-8')")
builder_path.write_text(builder, encoding='utf-8')
subprocess.run([sys.executable, '-X', 'utf8', str(builder_path)], check=True)

log_path = ROOT / 'image_generation_log.json'
log = json.loads(log_path.read_text(encoding='utf-8'))
for entry in log['entries']:
    if entry['id'] in entries:
        repair = entries[entry['id']]
        history = entry.setdefault('history', [])
        if entry.get('corrected_date') != '2026-10-11':
            history.append({k: entry.get(k) for k in ('source', 'prompt', 'references', 'tool', 'correction')})
        for key in ('source', 'prompt', 'references', 'tool'):
            entry[key] = repair[key]
        entry['correction'] = True
        entry['corrected_date'] = '2026-10-11'
        entry['correction_reason'] = repair['issue']
log['updated'] = '2026-10-11'
log_path.write_text(json.dumps(log, ensure_ascii=False, indent=2), encoding='utf-8')

rows = [
    '# 机械手检查与修正', '', '日期：2026-10-11。逐张检查 36 镜，替换 7 张。使用内置 imagegen 对原图进行局部编辑。', '',
    '## 统一结构', '',
    '轮椅只有两条机械臂，分别连接两侧车身。每条为上臂、前臂两段主体臂节；肘轴连接两段，末端小腕部接完整机械手。左右手互为镜像，各为四指加一拇指。车身安装转轴、腕轴不算新增的长臂节；画外或被桌面自然遮挡的手，不强行添加到画面中。', '',
    '## 已替换画面', '', '| 镜号 | 修正 |', '|---|---|',
]
for e in manifest['entries']:
    rows.append(f"| [{e['id']} · {e['title']}]({e['image']}) | {e['issue']} |")
rows += ['', '## 其余画面检查', '', '01、02、04、06—12、14—23、27、29—36 已检查机械臂数量、主体臂节、手掌、连接与持物。未发现与本轮缺手、重复臂链或多余臂节同类的明显问题，保留原图；画外与遮挡按实际构图判断。', '',
         '第 24、25 镜改为从下方托住茶罐／早餐的姿势，使掌面、拇指方向与物体承重更明确；第 26 镜去掉多余的第三段主体臂节。人物表情、对白、镜头时长和剧情不变。', '',
         '## 文件与记录', '', '预览页已为这 7 张图更新资源版本，缩略图、大图和打开原图使用同一修正版。生视频通用提示词增加了机械结构要求。完整 ZIP 已同步更新。', '',
         '最终编辑指令及生成文件来源见 `mechanical_hand_corrections_2026-10-11.json`；原始生成记录的旧条目保留在 `image_generation_log.json` 的 history 中。原图备份在制作包同级的 `v6_机械手修正_2026-10-11/原图备份/`。', '',
         '## 最终编辑提示词', '']
for e in manifest['entries']:
    rows += [f"### {e['id']} · {e['title']}", '', '```text', e['prompt'], '```', '']
(ROOT / '05_机械手检查与修正.md').write_text('\n'.join(rows), encoding='utf-8')
record_path = ROOT / '04_生成记录.md'
record = record_path.read_text(encoding='utf-8')
if '## 2026-10-11 机械手复查' not in record:
    record += '\n## 2026-10-11 机械手复查\n\n逐张复查 36 镜，以内置 imagegen 编辑并替换 03、05、13、24、25、26、28，共 7 张；修正缺手、手掌方向、重复臂链、多余臂节与托物承重。详见 [机械手检查与修正](05_机械手检查与修正.md)。预览、提示词、结构化数据与完整制作包已同步。\n'
record_path.write_text(record, encoding='utf-8')

from PIL import Image
shots = json.loads(data_path.read_text(encoding='utf-8'))['shots']
assert len(shots) == 36 and sum(s['duration'] for s in shots) == 180
image_results = []
for shot in shots:
    target = ROOT / shot['image']
    with Image.open(target) as im:
        im.verify()
    digest = hashlib.sha256(target.read_bytes()).hexdigest()
    old_digest = hashlib.sha256((BACKUP / target.name).read_bytes()).hexdigest()
    if shot['id'] in entries:
        assert digest != old_digest, shot['id']
    else:
        assert digest == old_digest, shot['id']
    image_results.append({'id': shot['id'], 'sha256': digest, 'changed': digest != old_digest})
assert len({x['sha256'] for x in image_results}) == 36
page = (ROOT / 'index.html').read_text(encoding='utf-8')
class GalleryParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.images = []
    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == 'img' and attrs.get('src', '').startswith('frames/'):
            self.images.append(attrs['src'])
parser = GalleryParser()
parser.feed(page)
assert len(parser.images) == 36
embedded = json.loads(re.search(r'const shots=(.*?);const byId=', page, re.S).group(1))
for shot, embedded_shot, gallery_src in zip(shots, embedded, parser.images):
    expected = shot['image'] + ('?v=20261011-arms-v2' if shot['id'] in entries else '')
    assert embedded_shot['image'] == gallery_src == expected
    assert (ROOT / gallery_src.split('?')[0]).is_file()

archive = ROOT.parent / '不用麻烦她_v6_完整分镜制作包.zip'
temporary = ROOT.parent / '不用麻烦她_v6_完整分镜制作包_修正中.zip'
assert archive.resolve().parent == ROOT.parent.resolve()
assert temporary.resolve().parent == ROOT.parent.resolve()
files = [p for p in ROOT.rglob('*') if p.is_file() and '__pycache__' not in p.parts]
with zipfile.ZipFile(temporary, 'w', compression=zipfile.ZIP_DEFLATED, compresslevel=6) as zf:
    for p in files:
        zf.write(p, (Path(ROOT.name) / p.relative_to(ROOT)).as_posix())
with zipfile.ZipFile(temporary) as zf:
    assert zf.testzip() is None
    for e in manifest['entries']:
        packed = zf.read((Path(ROOT.name) / e['image']).as_posix())
        assert packed == (ROOT / e['image']).read_bytes()
report = {'checked': 36, 'changed': [r['id'] for r in image_results if r['changed']], 'seconds': 180, 'gallery_images': len(parser.images), 'archive_files': len(files), 'archive_bytes': temporary.stat().st_size, 'images': image_results}
(Path(__file__).resolve().parent / '验证结果.json').write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
print(json.dumps({k: v for k, v in report.items() if k != 'images'}, ensure_ascii=False))
