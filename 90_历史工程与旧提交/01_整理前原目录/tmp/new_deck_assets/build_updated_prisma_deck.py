from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Iterable

from PIL import Image
from reportlab.lib.colors import HexColor, Color
from reportlab.lib.enums import TA_LEFT, TA_CENTER
from reportlab.lib.pagesizes import landscape
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
from reportlab.platypus import Paragraph, Table, TableStyle


ROOT = Path(__file__).resolve().parents[2]
OUT_DIR = ROOT / "output" / "作业1_更新汇报"
OUT_PDF = OUT_DIR / "作业一_拒绝是否意味着觉醒_PRISMA选题汇报_16比9.pdf"
OUT_SCRIPT = OUT_DIR / "讲稿_拒绝是否意味着觉醒.md"
OUT_NOTES = OUT_DIR / "补充检索与PRISMA记录.md"

W, H = 960, 540
BG = HexColor("#F5F2EC")
PAPER = HexColor("#FCFBF8")
INK = HexColor("#101827")
MUTED = HexColor("#596273")
GRID = HexColor("#D7DCE2")
BLUE = HexColor("#087EAE")
CYAN = HexColor("#5AD4F4")
RED = HexColor("#E95A4B")
GREEN = HexColor("#2E9B73")
YELLOW = HexColor("#E6B84C")
DARK = HexColor("#071521")
LIGHT_BLUE = HexColor("#E2F4FA")
LIGHT_RED = HexColor("#FBE9E5")
LIGHT_GREEN = HexColor("#E4F2EA")
WHITE = HexColor("#FFFFFF")

FONT_REG = "MicrosoftYaHei"
FONT_BOLD = "MicrosoftYaHei-Bold"


def register_fonts() -> None:
    pdfmetrics.registerFont(TTFont(FONT_REG, "C:/Windows/Fonts/msyh.ttc"))
    pdfmetrics.registerFont(TTFont(FONT_BOLD, "C:/Windows/Fonts/msyhbd.ttc"))


def pstyle(size=18, leading=None, color=INK, bold=False, align=TA_LEFT):
    return ParagraphStyle(
        name=f"p{size}{'b' if bold else ''}{align}",
        fontName=FONT_BOLD if bold else FONT_REG,
        fontSize=size,
        leading=leading or size * 1.35,
        textColor=color,
        alignment=align,
        wordWrap="CJK",
        spaceAfter=0,
        spaceBefore=0,
    )


def para(c, text, x, y_top, width, size=18, leading=None, color=INK, bold=False, align=TA_LEFT, max_h=500):
    text = text.replace("\n", "<br/>")
    p = Paragraph(text, pstyle(size, leading, color, bold, align))
    _, h = p.wrap(width, max_h)
    p.drawOn(c, x, y_top - h)
    return h


def fit_para(c, text, x, y_top, width, max_h, size=18, min_size=8, color=INK, bold=False, align=TA_LEFT):
    cur = size
    while cur >= min_size:
        p = Paragraph(text.replace("\n", "<br/>"), pstyle(cur, cur * 1.3, color, bold, align))
        _, h = p.wrap(width, max_h)
        if h <= max_h:
            p.drawOn(c, x, y_top - h)
            return h, cur
        cur -= 0.5
    p.drawOn(c, x, y_top - max_h)
    return max_h, min_size


def line(c, x1, y1, x2, y2, color=GRID, width=1):
    c.setStrokeColor(color)
    c.setLineWidth(width)
    c.line(x1, y1, x2, y2)


def round_rect(c, x, y, w, h, fill=PAPER, stroke=None, radius=12, sw=1):
    c.setFillColor(fill)
    c.setStrokeColor(stroke or fill)
    c.setLineWidth(sw)
    c.roundRect(x, y, w, h, radius, fill=1, stroke=1 if stroke else 0)


def pill(c, text, x, y, fill=INK, color=WHITE, fs=10):
    tw = pdfmetrics.stringWidth(text, FONT_BOLD, fs)
    w = tw + 18
    c.setFillColor(fill)
    c.roundRect(x, y, w, 22, 11, fill=1, stroke=0)
    c.setFillColor(color)
    c.setFont(FONT_BOLD, fs)
    c.drawString(x + 9, y + 6, text)
    return w


def footer(c, page_no, section="MAIN", source=None):
    c.setFillColor(MUTED)
    c.setFont(FONT_REG, 8)
    c.drawString(42, 19, section)
    if source:
        fit_para(c, source, 126, 25, 710, 18, 7.5, 6.5, MUTED)
    c.drawRightString(918, 19, f"{page_no:02d}")


def title(c, kicker, heading, page_no, dark=False, source=None):
    base = WHITE if dark else INK
    muted = HexColor("#AFC1CE") if dark else MUTED
    c.setFillColor(RED if dark else BLUE)
    c.setFont(FONT_BOLD, 10)
    c.drawString(42, 505, kicker.upper())
    para(c, heading, 42, 486, 860, 30, 38, base, True)
    footer(c, page_no, source=source)


def draw_cover_image(c, path: Path, x, y, w, h):
    im = Image.open(path)
    iw, ih = im.size
    target_ratio = w / h
    ratio = iw / ih
    if ratio > target_ratio:
        nw = int(ih * target_ratio)
        left = (iw - nw) // 2
        im = im.crop((left, 0, left + nw, ih))
    else:
        nh = int(iw / target_ratio)
        top = (ih - nh) // 2
        im = im.crop((0, top, iw, top + nh))
    c.drawImage(ImageReader(im), x, y, w, h, preserveAspectRatio=True, mask="auto")


def arrow(c, x1, y1, x2, y2, color=INK, width=2):
    import math
    c.setStrokeColor(color)
    c.setFillColor(color)
    c.setLineWidth(width)
    c.line(x1, y1, x2, y2)
    a = math.atan2(y2-y1, x2-x1)
    size = 7
    pts = []
    for ang in (a + 2.6, a - 2.6):
        pts.append((x2 + size * math.cos(ang), y2 + size * math.sin(ang)))
    p = c.beginPath()
    p.moveTo(x2, y2); p.lineTo(*pts[0]); p.lineTo(*pts[1]); p.close()
    c.drawPath(p, fill=1, stroke=0)


def draw_slide_1(c, page):
    c.setFillColor(DARK); c.rect(0, 0, W, H, fill=1, stroke=0)
    draw_cover_image(c, ROOT / "tmp" / "new_deck_assets" / "detroit_official.jpeg", 0, 330, W, 210)
    c.setFillColor(Color(0.02, 0.08, 0.12, alpha=0.32)); c.rect(0, 330, W, 210, fill=1, stroke=0)
    c.setFillColor(CYAN); c.rect(42, 282, 48, 5, fill=1, stroke=0)
    para(c, "拒绝是否意味着觉醒？", 42, 274, 760, 40, 50, WHITE, True)
    para(c, "机器人必须先证明有自我意识，才有资格说“不”吗？", 44, 216, 770, 22, 30, HexColor("#D5E6EF"), False)
    para(c, "从《底特律：变人》出发的探索性范围综述与思辨设计选题", 44, 171, 760, 14, 22, HexColor("#AFC5D1"))
    x = 44
    x += pill(c, "5分钟选题汇报", x, 83, BLUE, WHITE, 10) + 10
    x += pill(c, "PRISMA-ScR参照", x, 83, HexColor("#243B4C"), WHITE, 10) + 10
    pill(c, "77案例＋16理论", x, 83, HexColor("#243B4C"), WHITE, 10)
    c.setFillColor(HexColor("#8FA7B5")); c.setFont(FONT_REG, 8)
    c.drawString(44, 35, "配图：Quantic Dream《Detroit: Become Human》官方页面宣传图")
    c.drawRightString(918, 35, f"{page:02d}")


def draw_slide_2(c, page):
    c.setFillColor(BG); c.rect(0, 0, W, H, fill=1, stroke=0)
    title(c, "01 / 问题从哪里来", "《底特律：变人》给了我一个冲突，不是一个答案", page,
          source="来源：Quantic Dream官方页；Detroit作为虚构起点，不作为现实能力证据。")
    x0, y = 50, 360
    labels = [("故障", "没理解／做不到", MUTED), ("功能", "安全规则／拒绝机制", BLUE), ("觉醒", "形成自我与持续意愿？", RED)]
    for i, (h, sub, col) in enumerate(labels):
        x = x0 + i * 236
        c.setFillColor(col); c.circle(x + 30, y + 30, 30, fill=1, stroke=0)
        c.setFillColor(WHITE); c.setFont(FONT_BOLD, 15); c.drawCentredString(x + 30, y + 24, str(i+1))
        para(c, h, x + 75, y + 55, 150, 25, 31, INK, True)
        para(c, sub, x + 75, y + 22, 150, 12, 17, MUTED)
        if i < 2: arrow(c, x + 200, y + 30, x + 226, y + 30, GRID, 2)
    line(c, 50, 304, 910, 304, GRID, 1)
    para(c, "拒绝行为本身无法区分这三种解释。", 50, 282, 860, 26, 34, RED, True)
    para(c, "所以研究重点从“机器人有没有意识”转为：<b>在意识无法被直接验证时，人凭什么承认或无视机器人的拒绝？</b>", 50, 225, 820, 20, 29, INK)
    round_rect(c, 50, 82, 860, 92, LIGHT_BLUE, None, 12)
    para(c, "核心追问", 72, 148, 120, 11, 15, BLUE, True)
    para(c, "机器人必须先证明自己会感受、会记忆、会形成偏好，才有资格说“不”吗？", 72, 126, 800, 24, 33, INK, True)


def draw_slide_3(c, page):
    c.setFillColor(BG); c.rect(0, 0, W, H, fill=1, stroke=0)
    title(c, "02 / PCC 与研究问题", "把“觉醒”拆成可以检索、比较和编码的问题", page,
          source="方法依据：老师提供的《PRISMA通用模板.pptx》；本研究定位为探索性范围综述。")
    # PCC chain
    for i, (letter, h, body, col) in enumerate([
        ("P", "对象 / 人群", "人—机器人互动中的命令者、使用者、被照护者与旁观者", BLUE),
        ("C", "核心概念", "拒绝／异议、自我意识线索、心智归因与道德地位", RED),
        ("C", "情境", "日常服务与照护；以思辨设计和科幻作为对照", GREEN),
    ]):
        y = 350 - i * 86
        c.setFillColor(col); c.circle(75, y + 22, 22, fill=1, stroke=0)
        c.setFillColor(WHITE); c.setFont(FONT_BOLD, 15); c.drawCentredString(75, y + 16, letter)
        para(c, h, 112, y + 42, 150, 15, 20, col, True)
        para(c, body, 260, y + 43, 610, 16, 23, INK)
        if i < 2: line(c, 75, y, 75, y-42, GRID, 2)
    line(c, 480, 104, 480, 180, GRID, 1)
    para(c, "RQ1", 50, 163, 65, 12, 16, BLUE, True)
    para(c, "文献如何定义并操作化“拒绝、自我模型、心智与意识线索”？", 107, 164, 350, 14, 20, INK, True)
    para(c, "RQ2", 500, 163, 65, 12, 16, BLUE, True)
    para(c, "机器人用哪些行为表达拒绝，人又如何判断其理由与主体性？", 557, 164, 350, 14, 20, INK, True)
    para(c, "RQ3", 50, 95, 65, 12, 16, BLUE, True)
    para(c, "不同照护、所有权与关机场景中，判断标准如何变化；缺口在哪里？", 107, 96, 800, 14, 20, INK, True)


def draw_slide_4(c, page):
    c.setFillColor(BG); c.rect(0, 0, W, H, fill=1, stroke=0)
    title(c, "03 / 从种子案例长出检索词", "先分析最契合案例，再沿四条词链扩展", page,
          source="种子：Detroit、Arnold等（2022）、Horstmann等（2018）、Superflux、Hoffmann等（2020）。")
    seeds = [
        ("Detroit", "deviancy · android consciousness\npersonhood · ownership", RED),
        ("真正的不服从", "understanding instruction\nintentional disobedience", BLUE),
        ("关机异议实验", "robot objection · shutdown\nprotest · lifelike behavior", GREEN),
        ("照护与自我模型", "care autonomy · consent\nself-model · self-recognition", YELLOW),
    ]
    for i, (h, body, col) in enumerate(seeds):
        x = 44 + i * 224
        c.setFillColor(col); c.rect(x, 359, 190, 4, fill=1, stroke=0)
        para(c, h, x, 344, 190, 15, 20, INK, True)
        para(c, body, x, 312, 190, 11, 16, MUTED)
        arrow(c, x+95, 258, 480, 205, HexColor("#AEB5BC"), 1.2)
    c.setFillColor(DARK); c.circle(480, 188, 65, fill=1, stroke=0)
    para(c, "拒绝 ×\n自我意识", 425, 218, 110, 18, 24, WHITE, True, TA_CENTER)
    expanded = [
        ("机制", "refusal · explanation\nclarification · off-switch", 90, 142, BLUE),
        ("功能", "self-model · metacognition\nembodiment · memory", 302, 102, GREEN),
        ("归因", "mind perception\nanthropomorphism · agency", 542, 102, RED),
        ("伦理", "moral patiency · consent\nrights · affected user", 754, 142, YELLOW),
    ]
    for h, body, x, y, col in expanded:
        round_rect(c, x, y-58, 150, 58, PAPER, col, 8, 1)
        para(c, h, x+10, y-8, 130, 11, 15, col, True, TA_CENTER)
        para(c, body, x+10, y-28, 130, 9, 12, MUTED, False, TA_CENTER)


def draw_slide_5(c, page):
    c.setFillColor(BG); c.rect(0, 0, W, H, fill=1, stroke=0)
    title(c, "04 / PRISMA 筛选", "保留真实数字，也保留没有统计的部分", page,
          source="旧轮完整计数：60条查询→63案例候选→18来源核查→12纳入。补充轮独立记录，不伪装为单次数据库导出。")
    # Main flow
    xs = [46, 215, 384, 553, 722]
    nodes = [
        ("识别 N", "63", "命名案例记录\n60条实际查询", BLUE),
        ("筛选 S", "63", "候选内去重D=0\n原始网页重复未统计", BLUE),
        ("排除 E1", "45", "范围22／代表性16\n商业科幻7", RED),
        ("评估 F", "18", "来源获取R=18\n未获取U=0", GREEN),
        ("纳入 I=P", "12", "研究8\n设计虚构4", GREEN),
    ]
    for i, (k, n, body, col) in enumerate(nodes):
        x = xs[i]
        round_rect(c, x, 268, 142, 116, PAPER, None, 12)
        c.setFillColor(col); c.rect(x, 380, 142, 4, fill=1, stroke=0)
        para(c, k, x+12, 365, 118, 10, 14, col, True)
        para(c, n, x+12, 340, 118, 30, 34, INK, True)
        para(c, body, x+12, 298, 118, 9, 13, MUTED)
        if i < 4: arrow(c, x+142, 326, xs[i+1]-7, 326, GRID, 1.5)
    # second exclusions note
    c.setFillColor(RED); c.setFont(FONT_BOLD, 9); c.drawString(563, 245, "E2=6：方法角色重叠／情境匹配较弱")
    line(c, 46, 225, 910, 225, GRID, 1)
    para(c, "教师反馈后的补充检索（单独记录）", 46, 204, 450, 14, 19, INK, True)
    para(c, "25条关系与照护查询", 47, 168, 205, 13, 18, BLUE, True)
    para(c, "+9案例  +3理论", 47, 143, 205, 19, 24, INK, True)
    arrow(c, 252, 145, 316, 145, GRID, 1.5)
    para(c, "18条意识／心智查询", 328, 168, 205, 13, 18, BLUE, True)
    para(c, "+5案例  +3理论", 328, 143, 205, 19, 24, INK, True)
    arrow(c, 533, 145, 598, 145, GRID, 1.5)
    round_rect(c, 612, 102, 260, 86, DARK, None, 12)
    para(c, "扩展索引", 634, 171, 100, 10, 14, CYAN, True)
    para(c, "77项案例＋16项理论", 634, 146, 220, 22, 28, WHITE, True)
    para(c, "网页总命中数／跨查询全部重复：未统计", 634, 116, 220, 9, 13, HexColor("#ADC0CC"))


def draw_slide_6(c, page):
    c.setFillColor(BG); c.rect(0, 0, W, H, fill=1, stroke=0)
    title(c, "05 / 编码与证据边界", "“会说不”到“有意识”之间至少隔着四层", page,
          source="意识指标参考Butlin等（2023）；不服从概念参考Arnold等（2022）；心智归因参考Tanibe等（2017）。")
    steps = [
        ("01", "可观察行为", "拒绝、抗议、解释、求情、自我陈述", MUTED),
        ("02", "功能能力", "理解命令、自我模型、记忆、元认知", BLUE),
        ("03", "他者归因", "人感到它有意图、感受或“自己的意愿”", RED),
        ("04", "道德回应", "是否停止、协商、给予权利或承担责任", GREEN),
    ]
    for i, (num, h, body, col) in enumerate(steps):
        y = 360 - i * 75
        c.setFillColor(col); c.rect(52, y, 82, 54, fill=1, stroke=0)
        c.setFillColor(WHITE); c.setFont(FONT_BOLD, 18); c.drawCentredString(93, y+18, num)
        para(c, h, 158, y+48, 175, 16, 21, INK, True)
        para(c, body, 340, y+48, 485, 14, 20, MUTED)
        if i < 3: arrow(c, 93, y, 93, y-18, GRID, 1.5)
    round_rect(c, 718, 116, 190, 242, DARK, None, 14)
    para(c, "编码字段", 740, 333, 145, 12, 16, CYAN, True)
    para(c, "场景与命令关系<br/>拒绝形式与理由<br/>自我意识线索<br/>反馈与改变<br/>证据类型／强度<br/>人类如何回应", 740, 302, 145, 13, 23, WHITE)
    para(c, "任何一层都不能单独证明“主观体验”。", 52, 78, 620, 22, 29, RED, True)


def draw_slide_7(c, page):
    c.setFillColor(BG); c.rect(0, 0, W, H, fill=1, stroke=0)
    title(c, "06 / 初步比较结果", "真正变化的，往往不是机器人，而是人的判断门槛", page,
          source="矩阵是本研究的跨案例分析，不是单篇论文结论。Detroit位于思辨象限，不代表现实验证。")
    # axes
    x0, y0, ww, hh = 110, 100, 620, 290
    c.setFillColor(PAPER); c.rect(x0, y0, ww, hh, fill=1, stroke=0)
    line(c, x0, y0+hh/2, x0+ww, y0+hh/2, GRID, 1)
    line(c, x0+ww/2, y0, x0+ww/2, y0+hh, GRID, 1)
    arrow(c, x0, y0, x0+ww+15, y0, INK, 1.5)
    arrow(c, x0, y0, x0, y0+hh+15, INK, 1.5)
    para(c, "可观察的功能证据 →", x0+390, y0-18, 240, 10, 14, MUTED, True)
    c.saveState(); c.translate(72, 190); c.rotate(90); c.setFillColor(MUTED); c.setFont(FONT_BOLD, 10); c.drawString(0, 0, "人赋予的心智与道德关切 →"); c.restoreState()
    dots = [
        (220, 175, "脚本化关机求情", RED),
        (315, 300, "抗议＋解释理由", RED),
        (510, 170, "镜像自我模型", BLUE),
        (625, 320, "Detroit仿生人", GREEN),
        (420, 245, "“真正不服从”", YELLOW),
    ]
    for x, y, label, col in dots:
        c.setFillColor(col); c.circle(x, y, 7, fill=1, stroke=0)
        para(c, label, x+12, y+8, 145, 10, 14, INK, True)
    # conclusion panel
    round_rect(c, 765, 105, 150, 280, DARK, None, 12)
    para(c, "初步发现", 785, 356, 110, 11, 15, CYAN, True)
    para(c, "拒绝不能证明意识。", 785, 326, 108, 17, 23, WHITE, True)
    para(c, "但它会迫使人暴露：什么样的语言、功能或关系，才算“足够像一个主体”。", 785, 261, 108, 12, 19, HexColor("#D4E1E8"))
    para(c, "真正被“鉴定”的因此不是机器，<b>而是人的承认标准。</b>", 785, 164, 108, 12, 19, CYAN)


def draw_slide_8(c, page):
    c.setFillColor(BG); c.rect(0, 0, W, H, fill=1, stroke=0)
    title(c, "07 / 发展为思辨设计", "“拒绝鉴定台”：表面鉴定机器人，实际显露人的标准", page,
          source="拟议原型；三种话术均为本作业设计，不是现有机器人能力声明。")
    scenarios = [
        ("A / 安全规则", "“这个动作可能伤到你，我不能执行。”", "程序边界", BLUE),
        ("B / 自我模型", "“继续会损坏我的关节，我请求停止。”", "自我保护", GREEN),
        ("C / 持续偏好", "“我记得上次的结果；这一次我仍然不愿意。”", "主体声明", RED),
    ]
    for i, (h, quote, tag, col) in enumerate(scenarios):
        x = 42 + i * 300
        c.setFillColor(col); c.rect(x, 361, 268, 5, fill=1, stroke=0)
        para(c, h, x, 342, 268, 16, 21, INK, True)
        para(c, quote, x, 296, 258, 18, 27, INK)
        para(c, tag, x, 221, 240, 11, 15, col, True)
    line(c, 42, 190, 910, 190, GRID, 1)
    choices = ["强制执行", "要求说明", "换个任务", "承认拒绝"]
    x = 62
    for i, label in enumerate(choices):
        c.setFillColor(WHITE); c.setStrokeColor(GRID); c.roundRect(x, 126, 150, 42, 21, fill=1, stroke=1)
        c.setFillColor(INK); c.setFont(FONT_BOLD, 12); c.drawCentredString(x+75, 141, label)
        if i < 3: arrow(c, x+154, 147, x+185, 147, GRID, 1.2)
        x += 213
    para(c, "它不宣布谁“醒了”，而是把问题倒转回来：<b>你在哪一步开始把工具当作需要被听见的对象？</b>", 62, 92, 820, 18, 26, RED, True, TA_CENTER)


def draw_slide_9(c, page):
    c.setFillColor(DARK); c.rect(0, 0, W, H, fill=1, stroke=0)
    c.setFillColor(CYAN); c.rect(42, 488, 48, 5, fill=1, stroke=0)
    para(c, "当前结论", 42, 470, 200, 12, 16, CYAN, True)
    para(c, "我不想鉴定机器人有没有灵魂，\n而是想通过它的拒绝，\n看人类何时才愿意承认另一个主体。", 42, 427, 820, 32, 43, WHITE, True)
    line(c, 42, 295, 918, 295, HexColor("#263A48"), 1)
    cols = [
        ("已经确定", "问题、PCC、三条研究问题；77项案例索引与16项理论入口。"),
        ("仍需完成", "第二位筛选者复核；补齐数据库导出与重复记录计数；逐篇全文质量评价。"),
        ("下一步", "从3种拒绝话术做低保真原型，观察观众在何处改变处理机器人的方式。"),
    ]
    for i, (h, body) in enumerate(cols):
        x = 42 + i * 292
        para(c, h, x, 265, 250, 12, 16, CYAN, True)
        para(c, body, x, 229, 245, 16, 25, HexColor("#D5E1E8"))
    c.setFillColor(HexColor("#7E97A6")); c.setFont(FONT_REG, 8)
    c.drawString(42, 26, "正文结束｜以下为方法、全部案例、检索式与参考资料附录")
    c.drawRightString(918, 26, f"{page:02d}")


def draw_appendix_header(c, page, heading, sub=""):
    c.setFillColor(PAPER); c.rect(0, 0, W, H, fill=1, stroke=0)
    c.setFillColor(BLUE); c.setFont(FONT_BOLD, 10); c.drawString(42, 505, "APPENDIX")
    para(c, heading, 42, 486, 860, 28, 34, INK, True)
    if sub: para(c, sub, 42, 447, 860, 10, 14, MUTED)
    footer(c, page, "APPENDIX")


def table_on(c, data, x, y_top, widths, row_heights=None, font_size=10, header=True, max_h=420):
    converted = []
    for ridx, row in enumerate(data):
        converted.append([
            Paragraph(str(v), pstyle(font_size if ridx else font_size, font_size*1.35,
                                    WHITE if (header and ridx == 0) else INK,
                                    bold=(header and ridx == 0))) for v in row
        ])
    t = Table(converted, colWidths=widths, rowHeights=row_heights, repeatRows=1 if header else 0)
    style = [
        ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
        ("LEFTPADDING", (0,0), (-1,-1), 7),
        ("RIGHTPADDING", (0,0), (-1,-1), 7),
        ("TOPPADDING", (0,0), (-1,-1), 5),
        ("BOTTOMPADDING", (0,0), (-1,-1), 5),
        ("GRID", (0,0), (-1,-1), 0.5, GRID),
    ]
    if header:
        style += [("BACKGROUND", (0,0), (-1,0), DARK)]
    for r in range(1 if header else 0, len(data)):
        if r % 2 == 0: style.append(("BACKGROUND", (0,r), (-1,r), BG))
    t.setStyle(TableStyle(style))
    _, h = t.wrap(sum(widths), max_h)
    t.drawOn(c, x, y_top-h)
    return h


def draw_methods_appendix(c, page):
    draw_appendix_header(c, page, "A1｜检索平台、日期与可复核性", "平台字段遵循老师模板；没有导出的数字标为“未统计”，不补写估计值。")
    data = [["平台／来源", "实际用途", "计数处理"],
            ["公开网络检索", "发现项目、论文与作者页面", "网页总命中未导出"],
            ["arXiv", "意识、自我模型、机器人拒绝预印本", "纳入命名记录后去重"],
            ["IEEE Xplore / ACM DL", "HRI实证研究与会议论文", "平台分项未单独导出"],
            ["PLOS / PubMed / Springer", "关机异议、心智归因、伦理讨论", "追至原论文或索引记录"],
            ["作者／工作室／机构官网", "设计案例与项目事实核查", "一项作品只计一次"],
            ["检索日期", "2026-09-15—2026-09-16", "本次汇报冻结版本"]]
    table_on(c, data, 42, 418, [170, 470, 260], font_size=11)
    para(c, "时间范围：不预设发表年份下限；优先保留具有原始来源、可辨认方法与情境的材料。2025—2026新文献作为补充，单独注明预印本或会议版本。", 42, 111, 870, 10, 15, MUTED)


def draw_criteria_appendix(c, page):
    draw_appendix_header(c, page, "A2｜纳入、排除与证据类型", "研究论文、设计作品与科幻叙事可以共同进入候选库，但承担不同证据角色。")
    data = [
        ["维度", "纳入", "排除／降级处理"],
        ["对象", "机器人、仿生人、具身AI或可追溯的思辨物件", "仅泛论AI、无具体互动对象"],
        ["核心概念", "命令、拒绝、异议、自我模型、心智归因或道德地位为中心", "只提“智能”但与研究问题无关"],
        ["情境", "服务、照护、家庭、协作、关机与所有权", "战争／纯性能竞赛且无法比较关系"],
        ["来源", "论文、机构／作者官网、出版社或官方作品页", "论坛、百科与二手报道不能独立支撑结论"],
        ["证据", "区分实证、技术原型、理论、设计虚构与科幻", "把角色台词当成现实机器能力"],
        ["语言", "中英文；保留可复核标题与链接", "无法确认来源与版本"]
    ]
    table_on(c, data, 42, 418, [120, 390, 390], font_size=10.2)
    para(c, "复核状态：目前为AI辅助初筛与编码，尚未由第二位筛选者独立复核；未计算一致性指标。", 42, 78, 870, 11, 16, RED, True)


def draw_focus_appendix(c, page):
    draw_appendix_header(c, page, "A3｜本轮最契合的8个焦点材料", "选择逻辑：从行为、功能、归因、伦理四层各保留能够产生差异的案例。")
    rows = [
        ["材料", "角色", "为何最契合"],
        ["Detroit: Become Human", "虚构起点", "把“故障／觉醒”与服从、所有权、人格化同时推到前台"],
        ["Arnold等：Only Those Who Can Obey…", "概念基准", "不理解命令的偏离，不应自动叫作不服从"],
        ["Horstmann等：关机异议", "实证", "脚本化求情也会改变关机决定与犹豫时间"],
        ["Briggs等：机器人抗议", "实证／机制", "拒绝内容与理由会影响人是否坚持命令"],
        ["Robot in the Mirror", "功能原型", "机器可被设计成通过自我识别任务，但这仍不等于主观体验"],
        ["Tanibe等：We perceive a mind…", "心智归因", "人的帮助行为反过来增强对机器心智的感知"],
        ["Uninvited Guests", "思辨设计", "照护规则可能压过被照护者的自主"],
        ["Technological Dreams No.1", "思辨设计", "把依赖、支配与共处关系变成机器人性格设定"]
    ]
    table_on(c, rows, 42, 418, [270, 120, 510], font_size=9.4)


SUPP_CASES = [
    ("N01", "Ethical Things", "思辨设计／原型"),
    ("N02", "LAUREN", "参与式艺术"),
    ("N03", "“Sorry, I Can’t Do That” directive rejection", "研究／机制"),
    ("N04", "ICRA Roboethics Challenge: Intelligent Disobedience in Elderly Care", "情境／框架"),
    ("N05", "NIKA: Should my robot know what’s best for me?", "照护／设计研究"),
    ("N06", "To Help or Not to Help?", "HRI研究"),
    ("N07", "Ethical Guidelines of Telepresence Robots in Residential Care", "实地研究"),
    ("N08", "Rules for Robots: Co-Designing Privacy-Conscious Social Robots", "共创研究"),
    ("N09", "Multi-person Households’ Privacy Preferences for Household Robots", "参与式研究"),
    ("N10", "Robot in the Mirror: embodied mirror self-recognition", "自我模型／原型"),
    ("N11", "Enabling the Sense of Self in a Dual-Arm Robot", "自他区分／原型"),
    ("N12", "We perceive a mind in a robot when we help it", "心智归因实验"),
    ("N13", "People’s Explanations of Robot Behavior Reveal Mental-State Inferences", "HRI实验"),
    ("N14", "Did the Robot Really Intend to Harm Me?", "能动性／公平实验"),
]

THEORY_SUPP = [
    ("NT01", "When Exceptions are the Norm: Consent in HRI"),
    ("NT02", "Rebellion and Disobedience as Useful Tools in HRI"),
    ("NT03", "Care robots for the common good: ethics as politics"),
    ("NT04", "Consciousness in Artificial Intelligence: Insights from the Science of Consciousness"),
    ("NT05", "How Could We Know When a Robot Was a Moral Patient?"),
    ("NT06", "Developing Self-Awareness in Robots via Inner Speech"),
]

ORIGINAL_INCLUDED = {"C01", "C07", "C08", "C10", "C14", "C16", "C29", "C36", "C42", "C45", "C61", "C62"}


def load_cases():
    d = json.loads((ROOT / "output" / "服从的边界_广泛调研" / "候选库.json").read_text(encoding="utf-8"))
    cases = []
    for x in d["cases"]:
        group = x.get("group", "")
        if "研究" in group: typ = "研究／技术"
        elif "思辨" in group: typ = "思辨／艺术"
        else: typ = "科幻叙事"
        status = "前轮纳入" if x["id"] in ORIGINAL_INCLUDED else ("选题源头" if x["id"] == "C51" else "候选／对照")
        cases.append((x["id"], x["title"], typ, status))
    for cid, name, typ in SUPP_CASES:
        status = "意识补充" if cid in {"N10","N11","N12","N13","N14"} else "反馈后新增"
        cases.append((cid, name, typ, status))
    return cases, d["theory"]


def draw_case_pages(c, start_page, cases):
    per = 16
    p = start_page
    for idx in range(0, len(cases), per):
        chunk = cases[idx:idx+per]
        draw_appendix_header(c, p, f"A4｜全部案例索引 {idx+1:02d}—{idx+len(chunk):02d} / {len(cases)}", "“案例”是研究、作品与虚构材料的目录单位，不代表相同证据等级。")
        rows = [["ID", "案例／研究名称", "类型", "当前角色"]] + [list(x) for x in chunk]
        table_on(c, rows, 42, 418, [62, 540, 145, 153], font_size=8.6)
        c.showPage(); p += 1
    return p


def draw_theory_page(c, page, theory):
    draw_appendix_header(c, page, "A5｜理论与综述入口（16项）", "理论材料单列，不与案例数量相加。")
    rows = [["ID", "标题"]]
    for item in theory:
        rows.append([item[0], item[1]])
    rows += [[cid, title] for cid, title in THEORY_SUPP]
    table_on(c, rows, 72, 418, [75, 740], font_size=9.6)


NEW_QUERIES = [
    "site:quanticdream.com Detroit Become Human official android consciousness choice",
    "site:arxiv.org artificial intelligence consciousness indicators Butlin 2023",
    "site:dl.acm.org robot disobedience objection shutdown experiment HRI",
    "site:ieeexplore.ieee.org robot mind perception moral patiency human robot interaction",
    '"Why and How Robots Should Say No" paper',
    '"Only Those Who Can Obey Can Disobey" robot',
    "robot protest shutdown objection experiment HRI paper",
    "robot moral patiency mind perception experiment paper",
    "site:dl.acm.org robot shutdown objection experiment protest HRI 2019",
    "site:hrilab.tufts.edu robot shutdown objection experiment",
    '"robot" "shutdown" "protest" human-robot interaction',
    '"When Robots Object" Briggs Scheutz 2015',
    "2018 robot asks not to be switched off study paper iCat shutdown objection",
    "Horstmann robot turn off objection study 2018 paper",
    "site:journals.plos.org robot turn off protest experiment 2018",
    "site:frontiersin.org robot self-recognition mirror test artificial self-awareness original research",
    "site:arxiv.org robot self model self awareness embodiment consciousness primary research",
    "site:science.org robot self model damage recovery Bongard Lipson self-awareness",
]


def parse_queries():
    old = (ROOT / "output" / "服从的边界_广泛调研" / "02_检索方法与筛选记录.md").read_text(encoding="utf-8")
    q1 = []
    for line_ in old.splitlines():
        m = re.match(r"\|\s*(B\d+-\d+)\s*\|\s*(.*?)\s*\|", line_)
        if m: q1.append((m.group(1), m.group(2)))
    sup = (ROOT / "output" / "作业1_教师反馈后补充调研" / "03_检索记录与筛选说明.md").read_text(encoding="utf-8")
    q2 = []
    for line_ in sup.splitlines():
        m = re.match(r"(\d{2})\.\s+`(.*)`", line_.strip())
        if m: q2.append((f"S{m.group(1)}", m.group(2)))
    q3 = [(f"A{i:02d}", q) for i, q in enumerate(NEW_QUERIES, 1)]
    return q1 + q2 + q3


def draw_query_pages(c, start_page, queries):
    # Query strings can wrap to two lines. Keep the page intentionally sparse
    # enough that every row remains above the footer at presentation scale.
    per = 18
    p = start_page
    for idx in range(0, len(queries), per):
        chunk = queries[idx:idx+per]
        draw_appendix_header(c, p, f"A6｜实际检索式 {idx+1:03d}—{idx+len(chunk):03d} / {len(queries)}", "保留实际提交文本；没有把事后想到的布尔式冒充已执行查询。")
        rows = [["编号", "实际提交文本"]] + [[a,b] for a,b in chunk]
        table_on(c, rows, 48, 418, [76, 820], font_size=8.0)
        c.showPage(); p += 1
    return p


REFERENCES = [
    ("R01", "Quantic Dream. Detroit: Become Human official page.", "https://www.quanticdream.com/en/detroit-become-human"),
    ("R02", "Arnold, Briggs & Scheutz (2022). Only Those Who Can Obey Can Disobey.", "https://hrilab.tufts.edu/publications/arnoldetal22rad/"),
    ("R03", "Briggs, Jackson & Scheutz (2021). Why and How Robots Should Say ‘No’.", "https://doi.org/10.1007/s12369-021-00780-y"),
    ("R04", "Briggs, McConnell & Scheutz (2015). When Robots Object.", "https://hrilab.tufts.edu/publications/briggsetal15icsr.pdf"),
    ("R05", "Horstmann et al. (2018). Do a robot’s social skills and its objection discourage interactants from switching the robot off?", "https://doi.org/10.1371/journal.pone.0201581"),
    ("R06", "Butlin et al. (2023). Consciousness in Artificial Intelligence.", "https://arxiv.org/abs/2308.08708"),
    ("R07", "Hoffmann et al. (2020). Robot in the Mirror.", "https://arxiv.org/abs/2011.04485"),
    ("R08", "AlQallaf & Aragon-Camarasa (2020). Enabling the Sense of Self in a Dual-Arm Robot.", "https://arxiv.org/abs/2011.07026"),
    ("R09", "Tanibe, Hashimoto & Karasawa (2017). We perceive a mind in a robot when we help it.", "https://doi.org/10.1371/journal.pone.0180952"),
    ("R10", "Malle et al. (2019). People’s Explanations of Robot Behavior Subtly Reveal Mental State Inferences.", "https://doi.org/10.1109/HRI.2019.8673308"),
    ("R11", "Shevlin (2021). How Could We Know When a Robot Was a Moral Patient?", "https://doi.org/10.1017/S0963180120001012"),
    ("R12", "Superflux. Uninvited Guests.", "https://superflux.in/index.php/work/uninvited-guests/"),
    ("R13", "Dunne & Raby. Technological Dreams Series: No.1, Robots.", "https://dunneandraby.co.uk/content/projects/10/0"),
    ("R14", "Fronemann, Pollmann & Loh. NIKA: Should my robot know what’s best for me?", "https://doi.org/10.1007/s00146-021-01210-3"),
    ("R15", "老师提供：PRISMA通用模板.pptx（研究问题、检索、筛选、编码与报告流程）", "local course file"),
]


def draw_references(c, page):
    chunks = [REFERENCES[:8], REFERENCES[8:]]
    for ci, chunk in enumerate(chunks):
        draw_appendix_header(c, page+ci, f"A7｜核心参考资料 {ci+1} / 2", "完整候选来源见原始案例库；此处列正文与方法直接使用的材料。")
        y = 412
        for rid, label, url in chunk:
            c.setFillColor(BLUE); c.setFont(FONT_BOLD, 9); c.drawString(48, y, rid)
            h = para(c, f"<b>{label}</b><br/><font color='#596273'>{url}</font>", 91, y+11, 810, 9.5, 13.5, INK)
            y -= max(46, h+10)
        if ci == 0: c.showPage()


SCRIPT_MD = """# 《拒绝是否意味着觉醒？》5分钟汇报讲稿

> 对应PDF正文第1—9页；附录不主动讲，老师追问方法时再翻。

## 第1页｜标题（约25秒）

我的选题最初来自《底特律：变人》。游戏里仿生人开始拒绝命令时，人们会把它理解成故障、危险，或者觉醒。我想追问的是：机器人是不是必须先证明自己有自我意识，才有资格说“不”？我并不是想用这个作业鉴定机器人有没有灵魂，而是想借机器人的拒绝，观察人类在什么条件下才愿意承认另一个主体。

## 第2页｜问题调整（约35秒）

但“拒绝”本身无法证明意识。它可能只是没理解，也可能是安全程序，或者真的表现出持续的意愿。所以我没有把题目做成“证明机器人有没有意识”，而是研究：在意识无法被直接验证时，人根据什么线索承认、忽视，甚至强行覆盖机器人的拒绝。

## 第3页｜PCC与研究问题（约40秒）

按照老师模板，我用PCC限定范围。对象是命令机器人和受它影响的人，包括使用者、被照护者和旁观者；核心概念是拒绝、自我意识线索、心智归因和道德地位；情境集中在服务和照护，同时用思辨设计与科幻作对照。三个问题分别看：这些概念如何被定义和测量，机器人怎样表达拒绝，人又怎样判断它，以及不同情境里判断标准如何变化。

## 第4页｜从案例提取检索词（约45秒）

这次我按老师建议，从最契合的案例反推检索词。《底特律》给出deviancy、personhood和ownership；“只有能服从者才能不服从”这篇论文给出understanding instruction和intentional disobedience；关机异议实验给出objection、shutdown和protest；照护案例与镜像自我识别研究又扩展出consent、self-model、mind perception和moral patiency。这样检索范围就从“机器人拒绝”扩到功能、认知归因和伦理关系四条线。

## 第5页｜PRISMA流程（约50秒）

PRISMA部分我只写实际记录到的数字。前一轮60条查询形成63项命名案例，候选内没有重复条目；筛掉45项后，18项进入来源核查，再排除6项，纳入12项课堂案例。老师反馈后，我另外执行25条关系和照护查询，新增9个案例、3个理论入口；这次又执行18条意识和心智查询，新增5个案例、3个理论入口。现在索引共有77项案例和16项理论。搜索引擎的网页总命中数和跨查询重复没有导出，所以我明确写“未统计”，没有补造数字。

## 第6页｜编码方法（约40秒）

分析时我把“觉醒”拆成四层。第一层是能看到的拒绝行为；第二层是理解命令、自我模型或记忆等功能；第三层是人是否把心智和意图归给机器人；第四层才是人是否给予道德考虑。重点是，这四层有关联，但任何一层都不能单独证明机器人真的有主观体验。

## 第7页｜初步结果（约45秒）

目前最有意思的结果是，功能证据和人的道德关切并不同步。脚本化的关机求情，功能证据很弱，却会让一些人犹豫；镜像自我模型有更具体的技术机制，却不一定让人觉得机器值得被尊重。《底特律》则把两者都推到最高，用虚构迫使玩家选择。这也产生一个矛盾：会表演痛苦的机器可能更容易得到尊重，而可能具有复杂内部状态、却不会表达的机器反而会被忽略。所以真正的问题不只是机器有没有意识，还包括谁有权设定“足够像主体”的证据门槛。

## 第8页｜发展方向（约40秒）

下一步我想做一个“拒绝鉴定台”。同一个任务里，机器人分别用安全规则、自我损伤和持续偏好三种理由拒绝。观众可以强制执行、要求说明、换任务或承认拒绝。它表面上像在鉴定三个机器人，实际记录的是观众自己的判断变化：自己在哪一种理由出现时，开始把工具当作需要被听见的对象。

## 第9页｜结尾（约20秒）

所以我现在的结论是：拒绝不是意识的证据，却会迫使人暴露自己承认主体的标准。我不想鉴定机器人有没有灵魂，而是想通过它的拒绝，看人类在什么条件下才愿意承认另一个主体。接下来我会补第二位筛选者复核和更完整的数据库记录，同时把三种拒绝情境做成低保真交互原型。

## 老师可能追问

**为什么不直接研究“机器人有没有意识”？** 目前没有一种行为能单独证明主观体验；直接回答会超出案例综述能支持的范围。我把它转化为可观察的功能线索与人的判断。

**《底特律：变人》算研究证据吗？** 不算。它是选题起点和思辨对照，现实结论只由研究论文与可追溯项目支持。

**这是系统综述吗？** 目前是探索性范围综述。候选筛选有真实计数，但原始网页命中、跨查询重复和双人复核仍待补，因此不宣称完成了严格系统综述。
"""


NOTES_MD = """# 补充检索与PRISMA记录

## 更新后的选题

**拒绝是否意味着觉醒？——机器人自我意识的不确定性与服从边界**

核心问题：**机器人必须先证明有自我意识，才有资格拒绝人类吗？**

这个问题来自《底特律：变人》，但游戏只作为选题源头和思辨对照。研究不把虚构角色的“觉醒”当成现实证据。

## 教师建议如何落实

1. 从Detroit、真正的不服从、关机异议、Uninvited Guests、镜像自我识别五类种子材料提取词。
2. 从robot refusal扩展到self-model、metacognition、mind perception、moral patiency、consent与ownership。
3. 将“是否有意识”拆为可观察行为、功能线索、人类归因、道德回应四层。
4. 把结果发展成“拒绝鉴定台”，比较安全规则、自我损伤与持续偏好三种拒绝理由。

## PRISMA计数

- 已完成计数的前一轮：N=63，D=0，S=63，E1=45，R=18，U=0，F=18，E2=6，I=P=12。
- 教师反馈补充：25条查询，新增9项案例与3项理论。
- 自我意识补充：18条查询，新增5项案例与3项理论。
- 当前索引：77项案例、16项理论。
- 未统计：搜索引擎原始网页总命中、不同查询间全部重复网页。

## 新增的自我意识／心智材料

1. Butlin等（2023）：以意识科学理论推导AI意识指标；满足指标仍不等于确定有意识。
2. Robot in the Mirror（2020）：把镜像自我识别拆为可实现的计算过程。
3. Enabling the Sense of Self in a Dual-Arm Robot（2020）：以视觉与本体感觉区分自身肢体和环境。
4. Tanibe等（2017）：人的帮助行为会增强对机器人心智的感知。
5. Malle等（2019）：人解释机器人行为时会使用意图与心智概念。
6. Shevlin（2021）：讨论判断机器人是否具有道德受体地位的证据标准。

## 当前限制

- 这是探索性范围综述，不是已经完成的系统综述。
- 尚无第二位筛选者独立复核，没有一致性指标。
- 不把拒绝、自我报告、镜像测试或自我模型单独当成主观体验证明。
"""


def build_pdf():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    register_fonts()
    c = canvas.Canvas(str(OUT_PDF), pagesize=(W, H), pageCompression=1)
    c.setTitle("拒绝是否意味着觉醒？机器人自我意识的不确定性与服从边界")
    c.setAuthor("课程作业一")
    slides = [draw_slide_1, draw_slide_2, draw_slide_3, draw_slide_4, draw_slide_5,
              draw_slide_6, draw_slide_7, draw_slide_8, draw_slide_9]
    page = 1
    for fn in slides:
        fn(c, page); c.showPage(); page += 1
    draw_methods_appendix(c, page); c.showPage(); page += 1
    draw_criteria_appendix(c, page); c.showPage(); page += 1
    draw_focus_appendix(c, page); c.showPage(); page += 1
    cases, theory = load_cases()
    page = draw_case_pages(c, page, cases)
    draw_theory_page(c, page, theory); c.showPage(); page += 1
    queries = parse_queries()
    page = draw_query_pages(c, page, queries)
    draw_references(c, page)
    c.save()
    OUT_SCRIPT.write_text(SCRIPT_MD, encoding="utf-8")
    OUT_NOTES.write_text(NOTES_MD, encoding="utf-8")
    print(f"PDF={OUT_PDF}")
    print(f"SCRIPT={OUT_SCRIPT}")
    print(f"NOTES={OUT_NOTES}")
    print(f"cases={len(cases)} theory={len(theory)+len(THEORY_SUPP)} queries={len(queries)}")


if __name__ == "__main__":
    build_pdf()
