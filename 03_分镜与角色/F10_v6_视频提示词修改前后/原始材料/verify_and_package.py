from pathlib import Path
from html.parser import HTMLParser
import csv
import hashlib
import json
import re
import subprocess
import zipfile

WORK = Path(__file__).resolve().parent
ROOT = WORK.parent / 'v6_完整分镜'
backup = json.loads((WORK / '修改前/storyboard.json').read_text(encoding='utf-8'))
data = json.loads((ROOT / 'storyboard.json').read_text(encoding='utf-8'))
shots = data['shots']
assert len(shots) == 36
assert sum(s['duration'] for s in shots) == 180
by_id = {s['id']: s for s in shots}
assert len({s['video_prompt'] for s in shots}) == 36
for old, new in zip(backup['shots'], shots):
    assert old['video_prompt'] != new['video_prompt']
    assert {k: v for k, v in old.items() if not k.startswith('video_')} == {
        k: v for k, v in new.items() if not k.startswith('video_')}
assert not any(n in data['video_prompt_common'] for n in ('邱', '徐', '秀秀', '轮椅', '眼镜', '开衫'))
for sid in ['01', '02', '03', '04', '05', '06', '07']:
    assert not any(n in by_id[sid]['video_prompt'] for n in ('徐月禾', '徐家', '赭黄', '低发髻', '蓝条纹'))
for sid in ['01', '02', '03', '04']:
    assert '米白' in by_id[sid]['video_prompt']
    assert '砖红' not in by_id[sid]['video_prompt']
assert '空轮椅' in by_id['01']['video_prompt']
assert not any(n in by_id['08']['video_prompt'] for n in ('邱懿贞', '轮椅', '机械', '机器人', '秀秀'))
assert '仅徐月禾一人' in by_id['08']['video_prompt']
assert '侧脸与肩部' in by_id['11']['video_prompt']
assert '人物脸部留在画外' in by_id['17']['video_prompt']
assert not any(n in by_id['17']['video_prompt'] for n in ('银发髻', '眼镜', '蓝条纹', '邱懿贞', '徐月禾'))
assert all('虚焦' in by_id[sid]['video_prompt'] for sid in ['20', '21'])
assert '仅保留原图的赭黄衣袖与一小段躯干' in by_id['28']['video_prompt']
assert '邱懿贞没有接走' in by_id['28']['video_prompt']
assert '双人构图' in by_id['30']['video_prompt']
assert '两人的脸和手同框' in by_id['33']['video_prompt']

md = (ROOT / '02_即梦逐镜提示词.md').read_text(encoding='utf-8')
blocks = re.findall(r'```text\n(.*?)\n```', md, flags=re.S)
assert blocks == [s['video_prompt'] for s in shots]
with (ROOT / '分镜制作表.csv').open(encoding='utf-8-sig', newline='') as f:
    rows = list(csv.DictReader(f))
assert len(rows) == 36
assert all(row['镜号'] == s['id'] and row['即梦提示词'] == s['video_prompt']
           for row, s in zip(rows, shots))

class GalleryParser(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.in_textarea = False
        self.current = []
        self.prompts = []
        self.copy_ids = []
        self.scope_labels = 0
    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == 'textarea':
            self.in_textarea = True
            self.current = []
        if 'data-copy' in attrs:
            self.copy_ids.append(attrs['data-copy'])
    def handle_data(self, text):
        if self.in_textarea:
            self.current.append(text)
        if text == '本镜入画':
            self.scope_labels += 1
    def handle_endtag(self, tag):
        if tag == 'textarea' and self.in_textarea:
            self.prompts.append(''.join(self.current))
            self.in_textarea = False

html = (ROOT / 'index.html').read_text(encoding='utf-8')
parser = GalleryParser()
parser.feed(html)
assert parser.prompts == [s['video_prompt'] for s in shots]
assert parser.copy_ids == [s['id'] for s in shots]
assert parser.scope_labels == 36
embedded_start = html.index('const shots=') + len('const shots=')
embedded, _ = json.JSONDecoder().raw_decode(html[embedded_start:])
assert [s['video_prompt'] for s in embedded] == [s['video_prompt'] for s in shots]
assert 'const t=byId[b.dataset.copy].video_prompt' in html
for actual, source in zip(embedded, shots):
    expected = source['image'] + ('?v=' + source['image_revision'] if source.get('image_revision') else '')
    assert actual['image'] == expected
inline_js = re.search(r'<script>\s*(.*?)\s*</script>', html, re.S).group(1)
check_js = WORK / 'gallery_script_check.js'
check_js.write_text(inline_js, encoding='utf-8')
subprocess.run(['node', '--check', str(check_js)], check=True)

original_zip = WORK.parent / '不用麻烦她_v6_完整分镜制作包.zip'
untouched = []
with zipfile.ZipFile(original_zip) as old_zip:
    for path in ROOT.rglob('*'):
        if not path.is_file():
            continue
        rel = path.relative_to(ROOT).as_posix()
        if rel.startswith(('frames/', 'references/')) or rel in {
            '03_分镜画面提示词.md', '05_机械手检查与修正.md', '剧本_v6.md',
            'image_generation_log.json', 'mechanical_hand_corrections_2026-10-11.json',
            'bathroom_mechanical_hand_corrections_2026-10-11.json',
        }:
            assert hashlib.sha256(path.read_bytes()).digest() == hashlib.sha256(
                old_zip.read(ROOT.name + '/' + rel)).digest(), rel
            untouched.append(rel)

staged_zip = WORK.parent / '不用麻烦她_v6_完整分镜制作包_提示词更新中.zip'
files = sorted(p for p in ROOT.rglob('*') if p.is_file())
with zipfile.ZipFile(staged_zip, 'w', compression=zipfile.ZIP_DEFLATED, compresslevel=6) as package:
    for path in files:
        package.write(path, ROOT.name + '/' + path.relative_to(ROOT).as_posix())
with zipfile.ZipFile(staged_zip) as package:
    assert package.testzip() is None
    assert len(package.namelist()) == len(files) == 53
    for rel in ['storyboard.json', 'index.html', '02_即梦逐镜提示词.md', '分镜制作表.csv', 'build_package.py']:
        assert package.read(ROOT.name + '/' + rel) == (ROOT / rel).read_bytes()
report = {
    'prompts_updated': 36,
    'timeline_seconds': 180,
    'single_character_and_partial_frame_checks': 'passed',
    'markdown_csv_gallery_textareas_copy_data': 'all 36 prompts match canonical JSON',
    'gallery_javascript_syntax': 'passed',
    'unchanged_art_and_source_files': len(untouched),
    'unchanged_storyboard_images': sum(p.startswith('frames/') for p in untouched),
    'zip_crc_and_content': 'passed',
    'zip_files': len(files),
    'staged_zip': str(staged_zip),
    'videos_generated_or_tested': False,
}
(WORK / '检查结果.json').write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
print(json.dumps(report, ensure_ascii=False, indent=2))
