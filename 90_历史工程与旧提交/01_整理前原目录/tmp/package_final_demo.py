from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED

workspace = Path(r"D:\课\大四上\思辨设计")
source = workspace / "output" / "最终作业_不用麻烦她_3D交互原型"
target = workspace / "output" / "最终作业_不用麻烦她_3D交互原型_2026-10-08_修订.zip"
deck = "简介PPT_不用麻烦她_2026-10-08_最终作业修订版_v3.pptx"

with ZipFile(target, "w", compression=ZIP_DEFLATED, compresslevel=6) as archive:
    for file in sorted(source.rglob("*")):
        if not file.is_file():
            continue
        relative = file.relative_to(source)
        if relative.parts[0] in {".ppt_build", ".video_build"}:
            continue
        if relative.parts[0] == "简介PPT" and relative.name != deck:
            continue
        archive.write(file, str(Path(source.name) / relative))

with ZipFile(target) as archive:
    names = archive.namelist()
    assert any(name.endswith("/index.html") for name in names)
    assert any(name.endswith("/app.js") for name in names)
    assert any(name.endswith("/" + deck) for name in names)
    print(f"{len(names)} files, {target.stat().st_size} bytes")
