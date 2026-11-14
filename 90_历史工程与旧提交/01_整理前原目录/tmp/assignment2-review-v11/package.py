from pathlib import Path
import fitz, hashlib, json, re, zipfile
root=Path('作业二/提交_这一次轮椅该听谁的')
tmp=Path('tmp/assignment2-review-v11')
receipt=json.loads((tmp/'deck-validation-v11-final.json').read_text(encoding='utf-8'))
ppt=root/'说明PPT_这一次轮椅该听谁的_v1.1_修订.pptx'
assert hashlib.sha256(ppt.read_bytes()).hexdigest()==receipt['finalSha256']
assert receipt['packageIntegrity']['status']=='pass'
assert receipt['firstPartyImport']['passed']
assert receipt['presentationLayout']['finding_count']==0
assert receipt['nativeTableArithmetic']['native_table_count']==4
with zipfile.ZipFile(ppt) as p:
    assert p.testzip() is None
    assert len([s for s in p.namelist() if re.fullmatch(r'ppt/slides/slide\d+\.xml',s)])==16
    assert len([s for s in p.namelist() if re.fullmatch(r'ppt/notesSlides/notesSlide\d+\.xml',s)])==16
pdf=root/'演示备份_这一次轮椅该听谁的_v1.1.pdf'
with fitz.open(pdf) as p:
    assert len(p)==16
    assert len(p[15].get_links())==4
web=root/'交互原型v1'
html=(web/'index.html').read_text(encoding='utf-8')
for name in re.findall(r'(?:src|href)="([^"]+)"',html):
    if not name.startswith(('http','#')):assert (web/name).is_file(),name
assert 'app.js' not in html
assert (web/'assets/scene.png').is_file() and (web/'assets/storyboard.png').is_file()
for name in re.findall(r'\]\(([^)]+)\)',(root/'先读我_提交与演示.md').read_text(encoding='utf-8')):
    assert (root/name).is_file(),name
checks=json.loads((tmp/'checks.json').read_text(encoding='utf-8'))
assert len(checks['checks'])==36 and not checks['errors'] and not checks['external']
archive=Path('作业二/作业二_轮椅机器人_完整提交包_v1.1.zip')
assert not archive.exists(), 'Preserve any existing submission archive'
files=sorted(p for p in root.rglob('*') if p.is_file())
with zipfile.ZipFile(archive,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=6) as z:
    for p in files:z.write(p,arcname=str(p.relative_to(root.parent)))
with zipfile.ZipFile(archive) as z:
    assert z.testzip() is None
    assert len(z.namelist())==len(files)
    for p in files:assert hashlib.sha256(z.read(str(p.relative_to(root.parent)).replace('\\','/'))).digest()==hashlib.sha256(p.read_bytes()).digest()
report={'version':'v1.1','file_count':len(files),'zip_bytes':archive.stat().st_size,'ppt_sha256':receipt['finalSha256'],'slides':16,'notes':16,'pdf_pages':16,'pdf_source_links':4,'prototype_checks':36,'zip_integrity':'pass','local_assets':'pass','README_links':'pass','old_v1_zip_preserved':Path('作业二/作业二_轮椅机器人_完整提交包_v1.zip').stat().st_size==18981699}
(tmp/'package-checks.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(report,ensure_ascii=True))
