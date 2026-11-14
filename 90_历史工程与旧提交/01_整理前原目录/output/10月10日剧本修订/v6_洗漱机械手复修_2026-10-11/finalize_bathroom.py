"""Install two imagegen edits, update production records and verify packaging."""
from pathlib import Path
import hashlib
import json
import re
import shutil
import subprocess
import sys
import zipfile
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent / 'v6_完整分镜'
manifest = json.loads((ROOT / 'bathroom_mechanical_hand_corrections_2026-10-11.json').read_text(encoding='utf-8'))
entries = {e['id']: e for e in manifest['entries']}
data_path = ROOT / 'storyboard.json'
data = json.loads(data_path.read_text(encoding='utf-8'))
def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()
before = {s['id']: digest(ROOT / s['image']) for s in data['shots']}
for e in entries.values():
    source = Path(e['source'])
    target = ROOT / e['image']
    assert target.resolve().parent == (ROOT / 'frames').resolve()
    assert source.is_file()
    with Image.open(source) as im:
        im.verify()
    shutil.copy2(source, target)

for s in data['shots']:
    if s['id'] in entries:
        s['image_revision'] = '20261011-bathroom-v3'
        s['image_correction'] = entries[s['id']]['issue']
    if s['id'] == '03':
        s['keyframe'] = ('Same warm miniature bathroom and Qiu in ivory blouse. Near/screen-left chair-mounted robot RIGHT arm bends outward into clear space left of her torso, with its upper arm, elbow, forearm, wrist and entire five-digit hand visibly connected. It supports the rinse cup from below; Qiu reaches with her HUMAN right hand to receive the handle. Far/screen-right robot LEFT arm holds toothbrush to her lips. Qiu HUMAN left hand remains on lap. Exactly two arm chains, each of two main rigid links, no floating cup hand or sleeve-obscured forearm.')
        if '递杯臂的前臂' not in s['motion']:
            s['motion'] += ' 左侧递杯臂的前臂、手腕与手掌保持完整连接并清楚露出，邱用人手接杯柄。'
    if s['id'] == '04':
        s['keyframe'] += (' The near/screen-left idle robot arm folds outside her lap, with its entire forearm, wrist and complete five-digit hand inside frame; slightly wider lower-left framing includes the hand and a small near-wheel edge. Do not crop or hide this idle hand.')
        if '待机机械手完整入画' not in s['motion']:
            s['motion'] += ' 左侧待机机械手完整入画，前臂和手腕连接清楚，五指放松。'
data_path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')
subprocess.run([sys.executable, '-X', 'utf8', str(ROOT / 'build_package.py')], check=True)

log_path = ROOT / 'image_generation_log.json'
log = json.loads(log_path.read_text(encoding='utf-8'))
for item in log['entries']:
    if item['id'] not in entries:
        continue
    e = entries[item['id']]
    item.setdefault('history', []).append({k: item.get(k) for k in ('source','prompt','references','tool','correction','corrected_date','correction_reason')})
    item.update({k: e[k] for k in ('source','prompt','references','tool')})
    item.update(correction=True, corrected_date='2026-10-11', correction_reason=e['issue'], correction_round=e['round'])
log_path.write_text(json.dumps(log, ensure_ascii=False, indent=2), encoding='utf-8')

registry_path = ROOT / 'mechanical_hand_corrections_2026-10-11.json'
registry = json.loads(registry_path.read_text(encoding='utf-8'))
existing = {e['id']: e for e in registry['entries']}
for key, e in entries.items():
    new_entry = dict(e)
    if key in existing:
        new_entry['history'] = [existing[key]]
    existing[key] = new_entry
registry['entries'] = [existing[k] for k in sorted(existing)]
registry['corrected_shots'] = sorted(existing)
registry['latest_round'] = 'bathroom-visible-arms-v3'
registry_path.write_text(json.dumps(registry, ensure_ascii=False, indent=2), encoding='utf-8')

record_path = ROOT / '05_机械手检查与修正.md'
record = record_path.read_text(encoding='utf-8')
record = record.replace('逐张检查 36 镜，替换 7 张。', '逐张检查 36 镜，累计替换 8 张；03 镜在本轮再次修正，04 镜新增修正。')
record = re.sub(r'(?m)^\| \[03 ·.*$', f"| [03 · 刷牙的默契](frames/03_刷牙的默契.png) | {entries['03']['issue']} |", record)
table_row = f"| [04 · 她说停的方式](frames/04_她说停的方式.png) | {entries['04']['issue']} |"
record = record.replace('| [05 ·', table_row + '\n| [05 ·', 1)
record = record.replace('01、02、04、06—12、14—23、27、29—36', '01、02、06—12、14—23、27、29—36')
new_prompts = '\n'.join('### '+e['id']+' · '+e['title']+'\n\n```text\n'+e['prompt']+'\n```\n' for e in entries.values())
record = re.sub(r'### 03 · 刷牙的默契\n.*?(?=### 05 ·)', lambda m: new_prompts+'\n', record, flags=re.S)
record += '\n## 洗漱镜头复修：2026-10-11\n\n03 镜上一版的前臂仍被袖口遮挡，连接不清；04 镜上一轮保留原图，实际未交代完整左侧机械手。本轮改为完整可见的结构：03 递杯移到身体左侧空处；04 调整收拢手姿势，完整前臂、腕部与手指均入画。两张新图逐张检查后替换。最终指令另存于 `bathroom_mechanical_hand_corrections_2026-10-11.json`；修正版资源版本为 `20261011-bathroom-v3`。\n'
record_path.write_text(record, encoding='utf-8')
generation_record_path = ROOT / '04_生成记录.md'
generation_record = generation_record_path.read_text(encoding='utf-8')
generation_record += '\n## 2026-10-11 洗漱镜头复修\n\n03 再次编辑：把递杯移到身体左侧空处，使整条机械臂连接露出。04 新增编辑：调整待机机械臂姿势，补齐并完整显示前臂、手腕与五指机械手。使用内置 imagegen。累计替换 8 个镜头，03 有两轮修正。预览页、逐镜提示词、来源记录与 ZIP 同步更新。\n'
generation_record_path.write_text(generation_record, encoding='utf-8')

data = json.loads(data_path.read_text(encoding='utf-8'))
assert len(data['shots']) == 36 and sum(s['duration'] for s in data['shots']) == 180
changed = []
for s in data['shots']:
    target = ROOT / s['image']
    with Image.open(target) as im:
        im.verify()
    current = digest(target)
    if s['id'] in entries:
        assert current != before[s['id']]
        assert current == digest(Path(entries[s['id']]['source']))
        changed.append(s['id'])
    else:
        assert current == before[s['id']]
page = (ROOT / 'index.html').read_text(encoding='utf-8')
embedded = json.loads(re.search(r'const shots=(.*?);const byId=', page, re.S).group(1))
for s in embedded:
    if s['id'] in entries:
        expected = entries[s['id']]['image'] + '?v=20261011-bathroom-v3'
        assert s['image'] == expected
        assert f'src="{expected}"' in page
        assert f'href="{expected}"' in page

archive = ROOT.parent / '不用麻烦她_v6_完整分镜制作包.zip'
temporary = ROOT.parent / '不用麻烦她_v6_完整分镜制作包_洗漱复修中.zip'
assert temporary.resolve().parent == ROOT.parent.resolve()
files = [p for p in ROOT.rglob('*') if p.is_file() and '__pycache__' not in p.parts]
with zipfile.ZipFile(temporary, 'w', compression=zipfile.ZIP_DEFLATED, compresslevel=6) as zf:
    for p in files:
        zf.write(p, (Path(ROOT.name) / p.relative_to(ROOT)).as_posix())
with zipfile.ZipFile(temporary) as zf:
    assert zf.testzip() is None
    for e in entries.values():
        assert zf.read((Path(ROOT.name) / e['image']).as_posix()) == (ROOT / e['image']).read_bytes()
report = {'changed_this_round':changed, 'total_images':36, 'timeline_seconds':180, 'total_corrected_shots':registry['corrected_shots'], 'zip_files':len(files), 'zip_bytes':temporary.stat().st_size}
(Path(__file__).resolve().parent / '验证结果.json').write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
print(json.dumps(report, ensure_ascii=False))
