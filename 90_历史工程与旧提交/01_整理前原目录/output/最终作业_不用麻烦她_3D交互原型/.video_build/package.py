from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED
import os

project = Path(__file__).resolve().parents[1]
target = project.parent / (project.name + '.zip')
temporary = project.parent / (project.name + '.tmp.zip')
latest_ppt = '简介PPT_不用麻烦她_2026-10-07_研究过程版_最终.pptx'
files = []
for file in project.rglob('*'):
    if not file.is_file():
        continue
    relative = file.relative_to(project)
    if any(part.startswith('.') for part in relative.parts):
        continue
    if relative.parts[0] == '简介PPT' and file.suffix.lower() == '.pptx' and file.name != latest_ppt:
        continue
    files.append((file, relative))
with ZipFile(temporary, 'w', compression=ZIP_DEFLATED, compresslevel=6) as archive:
    for file, relative in files:
        archive.write(file, (Path(project.name) / relative).as_posix())
os.replace(temporary, target)
print(f'{len(files)} files | {target.stat().st_size} bytes')
