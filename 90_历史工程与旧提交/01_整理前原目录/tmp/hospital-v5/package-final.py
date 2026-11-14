from pathlib import Path
import json
import hashlib
import zipfile
import re

root = Path(r'D:\课\大四上\思辨设计\作业二\下一次汇报_剧本与规则\第五版_会协商的医院')
qa = Path(r'D:\课\大四上\思辨设计\tmp\hospital-v5')
pptx = root / '演示文稿/请等下一班_v5_会协商的医院.pptx'
pdf = root / '演示文稿/请等下一班_v5_会协商的医院.pdf'
demo = root / '3D交互短篇/index.html'
receipt = json.loads((qa / 'deck-validation.json').read_text(encoding='utf-8'))
checks = json.loads((qa / 'qa/checks.json').read_text(encoding='utf-8'))
assert hashlib.sha256(pptx.read_bytes()).hexdigest() == receipt['finalSha256']
assert len(checks['checks']) == 39 and all(c['ok'] for c in checks['checks'])
assert not checks['errors']
assert pdf.read_bytes().startswith(b'%PDF-') and demo.is_file()
with zipfile.ZipFile(pptx) as z:
    assert z.testzip() is None
    slides = [p for p in z.namelist() if re.fullmatch(r'ppt/slides/slide\d+\.xml', p)]
    notes = [p for p in z.namelist() if re.fullmatch(r'ppt/notesSlides/notesSlide\d+\.xml', p)]
    assert len(slides) == len(notes) == 20
files = sorted(p for p in root.rglob('*') if p.is_file())
for required in ['开始3D体验.cmd', '先看这里.md', '汇报讲稿.md', '作品剧本与交互分支.md',
                 '3D交互短篇/three.min.js', '3D交互短篇/texture.js', '视觉设定/3D实际界面.png']:
    assert (root / required).is_file(), required
archive = root.with_name(root.name + '_完整提交.zip')
with zipfile.ZipFile(archive, 'w', zipfile.ZIP_DEFLATED, compresslevel=6) as z:
    for p in files:
        z.write(p, str(Path(root.name) / p.relative_to(root)))
with zipfile.ZipFile(archive) as z:
    assert z.testzip() is None
    assert len(z.namelist()) == len(files)
result = {'archive': str(archive), 'files': len(files), 'bytes': archive.stat().st_size,
          'pptx_slides': len(slides), 'pptx_notes': len(notes), 'checks_passed': 39,
          'pptx_sha256_matches_validated_file': True, 'zip_integrity': 'pass'}
(qa / 'package-receipt.json').write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding='utf-8')
print(json.dumps(result, ensure_ascii=False, indent=2))
