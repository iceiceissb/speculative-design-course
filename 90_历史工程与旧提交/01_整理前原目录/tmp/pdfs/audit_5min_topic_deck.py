from pathlib import Path
import re
import pdfplumber
from pypdf import PdfReader

pdf = Path(r"D:/课/大四上/思辨设计/output/pdf/作业一_机器人该听谁的话_5分钟选题汇报_16比9.pdf")
reader = PdfReader(str(pdf))
sizes = [(float(p.mediabox.width), float(p.mediabox.height)) for p in reader.pages]
print("pages", len(reader.pages))
print("sizes", [(round(w, 2), round(h, 2)) for w, h in sizes])
print("all_16_9", all(abs(w / h - 16 / 9) < 1e-6 for w, h in sizes))

bad = []
replacement = 0
with pdfplumber.open(pdf) as doc:
    for number, page in enumerate(doc.pages, 1):
        replacement += (page.extract_text() or "").count("\ufffd")
        for char in page.chars:
            if (
                char["x0"] < -0.5
                or char["x1"] > page.width + 0.5
                or char["top"] < -0.5
                or char["bottom"] > page.height + 0.5
            ):
                bad.append((number, char.get("text"), char["x0"], char["x1"], char["top"], char["bottom"]))
print("out_of_bounds", len(bad))
print("replacement_chars", replacement)

script = Path(r"D:/课/大四上/思辨设计/output/作业1_5分钟汇报/讲稿_机器人该听谁的话.md").read_text(encoding="utf-8")
main = script.split("## 老师可能追问")[0]
print("script_cjk_chars", len(re.findall(r"[\u4e00-\u9fff]", main)))
print("pdf_bytes", pdf.stat().st_size)
