from pathlib import Path
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib import colors
from reportlab.lib.utils import ImageReader
from PIL import Image

ROOT = Path(r"D:/课/大四上/思辨设计")
OUT = ROOT / "output/pdf"
OUT.mkdir(parents=True, exist_ok=True)
PDF = OUT / "作业一_机器人该听谁的话_5分钟选题汇报_16比9.pdf"

W, H = 960, 540
M = 54

pdfmetrics.registerFont(TTFont("YH", r"C:/Windows/Fonts/msyh.ttc"))
pdfmetrics.registerFont(TTFont("YHB", r"C:/Windows/Fonts/msyhbd.ttc"))

INK = colors.HexColor("#1F2827")
PAPER = colors.HexColor("#F4F0E7")
PAPER2 = colors.HexColor("#EAE5DA")
RED = colors.HexColor("#D5253F")
LIME = colors.HexColor("#B8F31D")
TEAL = colors.HexColor("#3A7774")
MUTED = colors.HexColor("#66706D")
WHITE = colors.white
LINE = colors.HexColor("#CFC8BB")

c = canvas.Canvas(str(PDF), pagesize=(W, H), pageCompression=1)
c.setTitle("机器人该听谁的话？家庭照护中的命令权与拒绝权")
c.setAuthor("思辨设计课程作业")


def sw(text, font="YH", size=20):
    return pdfmetrics.stringWidth(text, font, size)


def wrap(text, width, font="YH", size=20):
    lines = []
    for para in str(text).split("\n"):
        if not para:
            lines.append("")
            continue
        line = ""
        for ch in para:
            trial = line + ch
            if line and sw(trial, font, size) > width:
                lines.append(line)
                line = ch
            else:
                line = trial
        if line:
            lines.append(line)
    return lines


def txt(text, x, y, width, size=20, leading=None, font="YH", color=INK, max_lines=None):
    leading = leading or size * 1.45
    c.setFont(font, size)
    c.setFillColor(color)
    lines = wrap(text, width, font, size)
    if max_lines:
        lines = lines[:max_lines]
    for line in lines:
        c.drawString(x, y, line)
        y -= leading
    return y


def pill(label, x, y, bg=INK, fg=WHITE, size=10, pad_x=10, h=22):
    width = sw(label, "YHB", size) + 2 * pad_x
    c.setFillColor(bg)
    c.roundRect(x, y, width, h, h / 2, fill=1, stroke=0)
    c.setFillColor(fg)
    c.setFont("YHB", size)
    c.drawString(x + pad_x, y + 6, label)
    return width


def line_arrow(x1, y1, x2, y2, color=INK, width=1.4):
    c.setStrokeColor(color)
    c.setFillColor(color)
    c.setLineWidth(width)
    c.line(x1, y1, x2, y2)
    import math
    ang = math.atan2(y2 - y1, x2 - x1)
    a = 7
    p = c.beginPath()
    p.moveTo(x2, y2)
    p.lineTo(x2 - a * math.cos(ang - 0.55), y2 - a * math.sin(ang - 0.55))
    p.lineTo(x2 - a * math.cos(ang + 0.55), y2 - a * math.sin(ang + 0.55))
    p.close()
    c.drawPath(p, fill=1, stroke=0)


def title(kicker, heading, sub=None, number=None):
    c.setFillColor(PAPER)
    c.rect(0, 0, W, H, fill=1, stroke=0)
    pill(kicker, M, H - 48, RED, WHITE, 9, 10, 20)
    txt(heading, M, H - 94, W - 2 * M, 31, 38, "YHB", INK, 2)
    if sub:
        txt(sub, M, H - 151, W - 2 * M, 14, 21, "YH", MUTED, 2)
    if number is not None:
        c.setFillColor(MUTED)
        c.setFont("YH", 9)
        c.drawRightString(W - M, H - 34, f"{number:02d} / 08")


def footer(source=None, urls=None):
    c.setStrokeColor(LINE)
    c.setLineWidth(0.6)
    c.line(M, 24, W - M, 24)
    if source:
        c.setFont("YH", 7.5)
        c.setFillColor(MUTED)
        c.drawString(M, 10, source)
    if urls:
        x = M
        for label, url in urls:
            w = sw(label, "YH", 7.5)
            c.linkURL(url, (x, 7, x + w, 20), relative=0)
            x += w + 12


def card(x, y, w, h, label, heading, body, accent=TEAL, body_size=12):
    c.setFillColor(WHITE)
    c.setStrokeColor(LINE)
    c.setLineWidth(0.8)
    c.roundRect(x, y, w, h, 12, fill=1, stroke=1)
    c.setFillColor(accent)
    c.roundRect(x, y + h - 9, w, 9, 9, fill=1, stroke=0)
    pill(label, x + 14, y + h - 39, accent, WHITE, 8, 8, 18)
    txt(heading, x + 14, y + h - 61, w - 28, 17, 23, "YHB", INK, 2)
    txt(body, x + 14, y + h - 113, w - 28, body_size, body_size * 1.55, "YH", MUTED, 5)


def image_cover(path, x, y, w, h):
    im = Image.open(path)
    iw, ih = im.size
    target = w / h
    src = iw / ih
    if src > target:
        nw = int(ih * target)
        left = (iw - nw) // 2
        im = im.crop((left, 0, left + nw, ih))
    else:
        nh = int(iw / target)
        top = (ih - nh) // 2
        im = im.crop((0, top, iw, top + nh))
    c.drawImage(ImageReader(im), x, y, w, h, mask="auto")


def dot(x, y, r, fill):
    c.setFillColor(fill)
    c.circle(x, y, r, fill=1, stroke=0)


# 01 Cover
c.setFillColor(INK)
c.rect(0, 0, W, H, fill=1, stroke=0)
image_cover(ROOT / "tmp/pdfs/figure1.png", 530, 0, 430, H)
c.setFillColor(colors.Color(0.12, 0.16, 0.15, alpha=0.22))
c.rect(530, 0, 430, H, fill=1, stroke=0)
pill("思辨设计 / 作业一 / 5 MIN", M, H - 62, LIME, INK, 9, 10, 22)
txt("机器人该听谁的话？", M, 382, 450, 43, 55, "YHB", WHITE, 2)
txt("家庭照护中的命令权与拒绝权", M, 274, 420, 21, 31, "YH", colors.HexColor("#D8DED9"), 2)
c.setStrokeColor(LIME)
c.setLineWidth(4)
c.line(M, 235, 210, 235)
txt("从5个种子案例反推检索词\n用PRISMA思路记录筛选与收紧", M, 205, 400, 14, 23, "YH", colors.HexColor("#C7CFCA"), 3)
txt("核心追问", M, 112, 120, 10, 15, "YHB", LIME, 1)
txt("当付款者、被照护者和平台意见不一致，机器人依据谁的意愿行动？", M, 88, 425, 16, 25, "YHB", WHITE, 3)
c.setFillColor(colors.HexColor("#ECE7DD"))
c.rect(530, 0, 430, 52, fill=1, stroke=0)
txt("图：Superflux, Uninvited Guests, 2015 / 课程PDF第76页", 548, 31, 390, 8, 12, "YH", MUTED, 1)
c.showPage()


# 02 Topic narrowing
title("01 / 选题如何收紧", "从“会不会拒绝”转向“替谁作决定”", "老师的建议促使我从最契合案例出发，重新检查研究对象。", 2)
c.setFillColor(WHITE)
c.roundRect(M, 265, 360, 138, 14, fill=1, stroke=0)
pill("原来的问题", M + 18, 366, MUTED, WHITE, 9, 10, 20)
txt("机器人拒绝之后，\n如何解释并接受纠正？", M + 18, 335, 325, 22, 32, "YHB", INK, 3)
line_arrow(430, 333, 525, 333, RED, 2.2)
c.setFillColor(colors.HexColor("#FCE8EC"))
c.roundRect(545, 265, 360, 138, 14, fill=1, stroke=0)
pill("更新后的问题", 563, 366, RED, WHITE, 9, 10, 20)
txt("谁有资格命令、拒绝，\n又由谁修改规则？", 563, 335, 325, 22, 32, "YHB", RED, 3)

# role diagram
roles = [(150, 174, "付款者", "设定照护目标"), (480, 154, "机器人 / 平台", "解释与执行规则"), (810, 174, "被照护者", "承受实际影响")]
for x, y, a, b in roles:
    dot(x, y + 24, 25, LIME if x == 810 else PAPER2)
    txt(a, x - 70, y - 12, 140, 14, 20, "YHB", INK, 2)
    txt(b, x - 80, y - 36, 160, 10, 15, "YH", MUTED, 2)
line_arrow(190, 195, 430, 175, INK, 1.2)
line_arrow(530, 175, 765, 195, INK, 1.2)
line_arrow(765, 166, 530, 149, RED, 1.2)
txt("研究范围：能表达并自主决定的成年人 / 日常提醒与非紧急信息分享", M, 71, 650, 12, 18, "YHB", TEAL, 2)
txt("暂不讨论急救、临床治疗和法定监护，避免不同伦理条件混在一起。", M, 46, 760, 10, 15, "YH", MUTED, 1)
footer()
c.showPage()


# 03 Seed cases to search terms
title("02 / 从案例反推检索词", "5个种子案例，扩展出4条检索主线", "检索词来自案例中的角色、行为和冲突，而不只来自“robot refusal”。", 3)
rows = [
    ("Uninvited Guests", "照护 vs 自主", "paternalism / refusal of care"),
    ("That's Mine!", "归属与许可", "ownership / permission / multi-user"),
    ("Our Friends Electric", "命令者也要解释", "justification / hidden authority"),
    ("CLARA", "误拒绝能否申诉", "appeal / contestability"),
    ("关机异议实验", "拒绝是否造成内疚", "manipulation / right to disengage"),
]
y = 343
for i, (a, b, d) in enumerate(rows):
    c.setFillColor(WHITE if i % 2 == 0 else colors.HexColor("#EEE9DF"))
    c.roundRect(M, y - 43, 505, 51, 8, fill=1, stroke=0)
    pill(str(i + 1), M + 10, y - 28, RED if i in (0, 2) else TEAL, WHITE, 8, 7, 17)
    txt(a, M + 45, y - 11, 170, 12, 17, "YHB", INK, 1)
    txt(b, M + 220, y - 11, 125, 11, 16, "YH", INK, 1)
    txt(d, M + 350, y - 11, 195, 9, 14, "YH", MUTED, 2)
    y -= 59

branches = [
    ("命令资格", "ownership / authority / permission"),
    ("拒绝照护", "autonomy / paternalism / consent"),
    ("共同生活", "bystander / non-user / household"),
    ("规则来源", "human labor / delegation / contestability"),
]
y = 348
for i, (a, b) in enumerate(branches):
    c.setFillColor(INK if i == 0 else WHITE)
    c.setStrokeColor(INK)
    c.roundRect(600, y - 49, 305, 58, 10, fill=1, stroke=1)
    dot(622, y - 19, 6, LIME if i == 0 else RED)
    txt(a, 641, y - 11, 120, 14, 20, "YHB", WHITE if i == 0 else INK, 1)
    txt(b, 641, y - 33, 245, 9, 14, "YH", colors.HexColor("#C8D0CB") if i == 0 else MUTED, 1)
    y -= 71
txt("从单条命令，转向多人关系中的决定权。", 600, 66, 305, 15, 22, "YHB", RED, 2)
footer("种子来源：Superflux / AAAI / CLARA / PLOS ONE。完整25条实际查询保存在检索记录中。")
c.showPage()


# 04 PRISMA-inspired flow
title("03 / PRISMA式记录", "补充检索如何从72项收紧到8项", "查询数、案例数和理论文献分开记录；未统计的原始网页命中数保持未知。", 4)
steps = [
    ("识别", "旧库", "63项案例\n10项理论"),
    ("扩展", "25条查询", "新增9项案例型材料\n新增3项理论"),
    ("核对", "去重与脉络检查", "旧项目再次命中\n不重复计数"),
    ("聚焦", "适配性比较", "72项案例索引\n13项理论单列"),
    ("纳入", "课堂重点", "8项案例\n旧3 + 新5"),
]
x = M
for i, (stage, head, body) in enumerate(steps):
    w = 150
    bg = RED if i == 4 else (INK if i == 0 else WHITE)
    fg = WHITE if i in (0, 4) else INK
    c.setFillColor(bg)
    c.setStrokeColor(LINE)
    c.roundRect(x, 232, w, 136, 14, fill=1, stroke=0 if i in (0, 4) else 1)
    pill(stage, x + 14, 335, LIME if i == 0 else (INK if i == 4 else TEAL), INK if i == 0 else WHITE, 8, 8, 18)
    txt(head, x + 14, 307, w - 28, 14, 20, "YHB", fg, 2)
    txt(body, x + 14, 268, w - 28, 11, 18, "YH", colors.HexColor("#CFD7D2") if i == 0 else fg, 3)
    if i < len(steps) - 1:
        line_arrow(x + w + 6, 299, x + w + 30, 299, RED, 1.8)
    x += 174

# audit notes
card(M, 68, 260, 122, "口径", "案例型材料 ≠ 机器人实验", "研究、设计虚构、艺术实践和共创研究分别标注。", TEAL, 11)
card(350, 68, 260, 122, "诚实记录", "原始网页总数未统计", "不把25条查询写成25篇文献，也不伪造初筛数量。", RED, 11)
card(646, 68, 260, 122, "复核限制", "尚无第二位独立筛选者", "后续由同学复核纳入判断，再记录分歧。", INK, 11)
footer("这是教师反馈后的补充检索流程；旧稿63→18→12仍表示上一轮代表性筛选，不与本轮混算。")
c.showPage()


# 05 Selected cases
title("04 / 8项重点案例", "四类问题，不按机器人外形或技术先进程度分组", "每组放入两个最能显示关系冲突的案例。", 5)
cards = [
    (M, 256, "A", "谁能命令", "That’s Mine!\n养老机构遥在机器人", "购买或操作设备，不等于替所有人授权。", TEAL),
    (505, 256, "B", "谁能拒绝照护", "Uninvited Guests\nNIKA", "机器人是否把人的拒绝当作需要克服的失败？", RED),
    (M, 70, "C", "谁规定什么是好", "Ethical Things\nOur Friends Electric", "机器说“为你好”时，“我”到底代表谁？", INK),
    (505, 70, "D", "谁能改变规则", "Rules for Robots\n多成员家庭隐私共创", "同一家庭里，不同人的偏好如何独立表达？", colors.HexColor("#8A5A7B")),
]
for x, y, lab, head, cases, q, accent in cards:
    c.setFillColor(WHITE)
    c.setStrokeColor(LINE)
    c.roundRect(x, y, 400, 150, 14, fill=1, stroke=1)
    c.setFillColor(accent)
    c.roundRect(x, y, 52, 150, 14, fill=1, stroke=0)
    c.setFillColor(WHITE)
    c.setFont("YHB", 28)
    c.drawCentredString(x + 26, y + 91, lab)
    txt(head, x + 72, y + 118, 150, 18, 24, "YHB", accent, 1)
    txt(cases, x + 235, y + 118, 145, 11, 19, "YHB", INK, 2)
    c.setStrokeColor(LINE)
    c.line(x + 72, y + 75, x + 380, y + 75)
    txt(q, x + 72, y + 58, 308, 11, 17, "YH", MUTED, 3)
footer("8项重点：旧案例3项 + 新案例5项。完整72项候选索引保留为后续比较与反证。")
c.showPage()


# 06 Findings
title("05 / 比较后的发现", "真正的问题不是“机器人会不会说不”", "而是它替谁说不，谁能让它改口。", 6)
findings = [
    ("01", "拒绝是双向的", "既看机器人如何拒绝命令，也看它能否接受人拒绝帮助。"),
    ("02", "家庭不是一个用户", "付款者、当事人、访客和平台承受的风险不同。"),
    ("03", "解释不会消除分歧", "即使规则说清楚，人们仍可能不同意由谁来决定。"),
]
y = 352
for n, head, body in findings:
    c.setFillColor(WHITE)
    c.roundRect(M, y - 58, 535, 78, 12, fill=1, stroke=0)
    pill(n, M + 14, y - 39, RED, WHITE, 8, 8, 18)
    txt(head, M + 60, y - 17, 170, 16, 22, "YHB", INK, 1)
    txt(body, M + 240, y - 15, 330, 11, 17, "YH", MUTED, 3)
    y -= 94

# authority triangle
cx, cy = 755, 252
pts = [(cx, cy + 116, "付款者\n目标"), (cx - 125, cy - 86, "被照护者\n当下意愿"), (cx + 125, cy - 86, "平台\n默认规则")]
c.setStrokeColor(INK)
c.setLineWidth(1.3)
c.line(pts[0][0], pts[0][1], pts[1][0], pts[1][1])
c.line(pts[1][0], pts[1][1], pts[2][0], pts[2][1])
c.line(pts[2][0], pts[2][1], pts[0][0], pts[0][1])
for i, (x, y, lab) in enumerate(pts):
    dot(x, y, 34, LIME if i == 1 else (RED if i == 0 else TEAL))
    color = INK if i == 1 else WHITE
    lines = lab.split("\n")
    c.setFillColor(color)
    c.setFont("YHB", 10)
    c.drawCentredString(x, y + 4, lines[0])
    c.setFont("YH", 8)
    c.drawCentredString(x, y - 10, lines[1])
dot(cx, cy - 5, 29, INK)
c.setFillColor(WHITE)
c.setFont("YHB", 10)
c.drawCentredString(cx, cy - 1, "机器人")
c.setFont("YH", 7)
c.drawCentredString(cx, cy - 14, "替谁作决定？")
txt("新的分析单位：关系中的决定权", 650, 95, 255, 13, 19, "YHB", RED, 2)
footer("分析结论来自8项重点案例的横向比较，不是对某一论文结论的直接转述。")
c.showPage()


# 07 Speculative prototype
title("06 / 思辨原型方向", "一张“照护边界凭条”，两种完全不同的家庭关系", "场景：父亲说“今天不要再提醒我散步”。", 7)

def receipt(x, y, w, h, mode, accent, lines, stamp):
    c.setFillColor(WHITE)
    c.setStrokeColor(accent)
    c.setLineWidth(1.4)
    c.roundRect(x, y, w, h, 8, fill=1, stroke=1)
    c.setFillColor(accent)
    c.rect(x, y + h - 48, w, 48, fill=1, stroke=0)
    txt("CARE BOUNDARY / 001", x + 16, y + h - 19, w - 32, 7, 10, "YHB", WHITE, 1)
    txt(mode, x + 16, y + h - 38, w - 32, 15, 19, "YHB", WHITE, 1)
    yy = y + h - 75
    for label, value in lines:
        txt(label, x + 16, yy, 94, 9, 13, "YH", MUTED, 1)
        txt(value, x + 112, yy, w - 128, 10, 14, "YHB", INK, 2)
        c.setStrokeColor(PAPER2)
        c.line(x + 16, yy - 9, x + w - 16, yy - 9)
        yy -= 39
    c.setStrokeColor(accent)
    c.setDash(3, 2)
    c.line(x + 16, y + 42, x + w - 16, y + 42)
    c.setDash()
    txt(stamp, x + 16, y + 25, w - 32, 9, 12, "YHB", accent, 2)

receipt(M, 80, 365, 300, "付款者优先", RED,
        [("请求", "暂停散步提醒"), ("状态", "等待购买者批准"), ("当日行为", "继续原提醒"), ("共享", "向子女发送原因")],
        "拒绝只是待审批的申请")
receipt(540, 80, 365, 300, "当事人优先", TEAL,
        [("请求", "暂停散步提醒"), ("状态", "暂停至今晚"), ("次日行为", "恢复前再次确认"), ("共享", "不记录私人原因")],
        "拒绝成为可限定的反馈")
line_arrow(439, 226, 519, 226, RED, 2.0)
c.setFillColor(RED)
c.setFont("YHB", 11)
c.drawCentredString(479, 241, "只改变授权规则")
c.drawCentredString(479, 205, "关系已经不同")
txt("《思辨一切》：用日常物件承载价值选择", M, 51, 390, 10, 15, "YHB", INK, 1)
txt("《Not Here, Not Now》：购买机器人 ≠ 自动获得管理当事人的资格", 515, 51, 390, 10, 15, "YHB", INK, 1)
footer("这是作业提出的思想实验，原作Uninvited Guests没有实现该机制。")
c.showPage()


# 08 Next steps and close
title("07 / 继续发展", "下一步不是再堆案例，而是让冲突可比较、可体验", None, 8)
road = [
    ("01", "复核8项重点案例", "统一记录角色、命令、拒绝、反馈和证据类型。"),
    ("02", "加入第二位筛选者", "同学独立复核纳入与分类，记录分歧。"),
    ("03", "制作两套凭条原型", "同一情境，只改变“谁能覆盖谁”的规则。"),
    ("04", "用3个日常场景测试", "散步提醒 / 信息分享 / 来访者隐私。"),
]
y = 345
for i, (n, head, body) in enumerate(road):
    x = M + (i % 2) * 426
    yy = y - (i // 2) * 116
    c.setFillColor(WHITE)
    c.roundRect(x, yy - 70, 390, 88, 12, fill=1, stroke=0)
    pill(n, x + 14, yy - 53, LIME if i == 2 else INK, INK if i == 2 else WHITE, 8, 8, 18)
    txt(head, x + 60, yy - 26, 300, 15, 21, "YHB", INK, 1)
    txt(body, x + 60, yy - 50, 300, 10, 15, "YH", MUTED, 2)

c.setFillColor(INK)
c.roundRect(M, 68, W - 2 * M, 84, 14, fill=1, stroke=0)
txt("照护如果不能被拒绝，它还是照护吗？", M + 25, 119, 650, 24, 32, "YHB", WHITE, 1)
pill("研究问题", W - 190, 99, LIME, INK, 9, 10, 22)
txt("机器人该听谁的话", W - 284, 84, 230, 11, 16, "YHB", LIME, 1)
footer("理论入口：Speculative Everything (MIT Press, 2013)；Not Here, Not Now (MIT Press, 2025)。")
c.showPage()

c.save()
print(PDF)
