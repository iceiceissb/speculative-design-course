from __future__ import annotations

import csv
import json
import re
from collections import Counter, defaultdict
from datetime import date
from pathlib import Path
from urllib.parse import urlsplit, urlunsplit


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "output" / "机器人自我修养数据库"
OLD_DB = ROOT / "output" / "服从的边界_广泛调研" / "候选库.json"
NEW_CASES_MD = ROOT / "output" / "作业1_教师反馈后补充调研" / "02_新增案例与证据附录.md"
MEMORY_MD = ROOT / "output" / "作业1_更新汇报" / "案例拓展_机器人记忆删除与身份连续性.md"

UPDATED = "2026-09-17"


def norm_title(value: str) -> str:
    value = value.lower().strip()
    value = re.sub(r"[\s\W_]+", "", value, flags=re.UNICODE)
    return value


def norm_url(value: str) -> str:
    if not value:
        return ""
    try:
        s = urlsplit(value.strip())
        host = s.netloc.lower().removeprefix("www.")
        path = s.path.rstrip("/")
        return urlunsplit((s.scheme.lower(), host, path, s.query, ""))
    except ValueError:
        return value.strip().rstrip("/").lower()


def uniq(values):
    return list(dict.fromkeys(x for x in values if x not in (None, "", [])))


def infer_kind(type_text: str, title: str = "") -> tuple[str, str]:
    text = f"{type_text} {title}".lower()
    if any(x in text for x in ["电影", "小说", "动画", "游戏", "虚构作品", "fiction"]):
        return "虚构叙事", "虚构"
    if any(x in text for x in ["艺术", "设计虚构", "思辨设计", "互动装置", "参与式", "speculative"]):
        return "艺术与设计", "思辨／艺术"
    if any(x in text for x in ["法律", "条例", "gdpr", "政策"]):
        return "法律与政策", "规范文本"
    if any(x in text for x in ["产品", "停服", "真实事件", "葬礼", "新闻"]):
        return "真实产品与事件", "纪实／产品"
    if any(x in text for x in ["理论", "伦理分析", "立场", "综述", "book", "著作"]):
        return "理论与综述", "概念／综述"
    return "研究与技术", "实证／技术"


def infer_quality(url: str, kind: str, evidence_nature: str) -> str:
    u = url.lower()
    if kind == "虚构叙事":
        return "C｜作品入口"
    if kind == "法律与政策" and any(x in u for x in ["eur-lex", "ftc.gov", "unesco.org", "coe.int", "nist.gov"]):
        return "A｜官方规范"
    if any(x in u for x in ["pmc.ncbi.nlm.nih.gov", "pubmed.ncbi.nlm.nih.gov", "frontiersin.org", "nature.com/articles", "proceedings.mlr.press", "dl.acm.org/doi", "doi.org/10.", "ojs.aaai.org", "journals.plos.org", "sciencedirect.com", "tandfonline.com/doi", "link.springer.com/article", "academic.oup.com"]):
        return "A｜同行评议或正式出版"
    if any(x in u for x in ["arxiv.org", "ssrn.com", "papers.ssrn", "dspace.mit.edu", "diva-portal", "aaltodoc", ".edu/"]):
        return "B｜预印本／机构存档"
    if evidence_nature in ["思辨／艺术", "纪实／产品", "虚构"]:
        return "B｜官方项目／作品页"
    return "C｜新闻、商业或待复核入口"


TAG_RULES = {
    "合理拒绝": ["拒绝", "不服从", "disobed", "reject", "say no", "refusal", "off-switch", "shutdown", "关机"],
    "承认局限": ["不确定", "追问", "澄清", "ask for help", "uncertain", "ambigu", "false premise", "做不到", "不可行"],
    "尊重意愿": ["同意", "assent", "consent", "autonomy", "自主", "意愿", "撤回", "自决"],
    "纠正错误": ["错误", "纠错", "修复", "apolog", "sorry", "failure", "mistake", "repair"],
    "反馈学习": ["反馈", "学习", "learn", "training", "训练", "relearning", "continual", "持续学习"],
    "解释协商": ["解释", "协商", "理由", "explanation", "dialog", "沟通", "披露"],
    "维护边界": ["隐私", "privacy", "边界", "秘密", "旁观者", "bystander", "多用户", "multi-person"],
    "关系善终": ["停服", "告别", "退役", "终止", "删除", "记忆", "identity", "memory", "shutdown", "遗忘"],
    "反操控": ["操纵", "依赖", "deception", "欺骗", "attachment", "依恋", "anthropom", "拟人"],
    "承认主体": ["主体", "意识", "心智", "moral patient", "moral status", "mind perception", "sentien", "self", "自我"],
    "照护分寸": ["照护", "care", "老人", "older", "dementia", "assistance", "帮助", "help"],
}

AXIS_RULES = {
    "服从与拒绝": ["拒绝", "不服从", "obed", "disobed", "off-switch", "shutdown", "command"],
    "意识与道德地位": ["意识", "sentien", "moral patient", "moral status", "mind perception", "心智", "主体"],
    "同意与自主": ["consent", "assent", "同意", "autonomy", "自主", "家长主义", "paternal"],
    "隐私与共同记忆": ["privacy", "隐私", "memory", "记忆", "披露", "bystander"],
    "学习与纠错": ["learn", "学习", "feedback", "反馈", "repair", "纠错", "failure", "错误"],
    "依恋与退出": ["attachment", "依恋", "停服", "退出", "告别", "dependency", "依赖"],
    "所有权与控制": ["ownership", "所有权", "control", "控制", "维修", "repair restriction"],
    "照护与家长主义": ["care", "照护", "dementia", "老人", "older", "paternal", "药物"],
}

SCENARIO_RULES = {
    "家庭": ["家庭", "家用", "household", "home", "domestic"],
    "养老与照护": ["老人", "养老", "照护", "care", "older", "dementia", "elder"],
    "医疗健康": ["医疗", "健康", "药", "health", "patient", "hospital"],
    "协作劳动": ["协作", "工作", "任务", "assembly", "team", "work"],
    "公共空间": ["公共", "街", "public", "bystander", "pedestrian"],
    "数字陪伴": ["陪伴", "companion", "replika", "chatbot", "数字关系"],
    "机器人学习": ["学习", "训练", "feedback", "learning", "benchmark", "dataset"],
    "退役与售后": ["停服", "退役", "维修", "重置", "删除", "shutdown", "reset", "repair", "end-of-life"],
}


def infer_tags(text: str, rules: dict[str, list[str]], fallback: str) -> list[str]:
    low = text.lower()
    hits = [tag for tag, words in rules.items() if any(word.lower() in low for word in words)]
    return hits or [fallback]


records: list[dict] = []
url_index: dict[str, int] = {}
title_index: dict[str, int] = {}


def add_record(
    *,
    legacy_id: str,
    title: str,
    url: str,
    type_text: str,
    summary: str,
    evidence_boundary: str,
    research_question: str = "",
    provenance: str,
    role: str = "案例",
    search_terms: list[str] | None = None,
    review_status: str = "来源页／摘要核查",
    kind: str | None = None,
    evidence_nature: str | None = None,
    aliases: list[str] | None = None,
) -> None:
    kind0, nature0 = infer_kind(type_text, title)
    kind = kind or kind0
    evidence_nature = evidence_nature or nature0
    combined = " ".join([title, type_text, summary, evidence_boundary, research_question])
    rec = {
        "id": "",
        "legacy_ids": [legacy_id] if legacy_id else [],
        "title": title.strip(),
        "aliases": aliases or [],
        "record_role": role,
        "material_type": kind,
        "evidence_nature": evidence_nature,
        "summary": summary.strip(),
        "evidence_boundary": evidence_boundary.strip(),
        "research_question": research_question.strip(),
        "cultivation_capabilities": infer_tags(combined, TAG_RULES, "情境判断"),
        "debate_axes": infer_tags(combined, AXIS_RULES, "人与机器关系"),
        "scenario_domains": infer_tags(combined, SCENARIO_RULES, "跨场景"),
        "search_terms": search_terms or [],
        "primary_url": url.strip(),
        "source_urls": [url.strip()] if url.strip() else [],
        "source_quality": infer_quality(url, kind, evidence_nature),
        "review_status": review_status,
        "provenance_rounds": [provenance],
        "added_on": UPDATED,
    }

    ukey = norm_url(url)
    tkey = norm_title(title)
    idx = url_index.get(ukey) if ukey else None
    if idx is None:
        idx = title_index.get(tkey)
    if idx is None:
        for alias in rec["aliases"]:
            idx = title_index.get(norm_title(alias))
            if idx is not None:
                break
    if idx is None:
        idx = len(records)
        records.append(rec)
        if ukey:
            url_index[ukey] = idx
        if tkey:
            title_index[tkey] = idx
        for alias in rec["aliases"]:
            title_index[norm_title(alias)] = idx
        return

    old = records[idx]
    old["legacy_ids"] = uniq(old["legacy_ids"] + rec["legacy_ids"])
    old["aliases"] = uniq(old["aliases"] + rec["aliases"] + ([rec["title"]] if rec["title"] != old["title"] else []))
    old["source_urls"] = uniq(old["source_urls"] + rec["source_urls"])
    old["cultivation_capabilities"] = uniq(old["cultivation_capabilities"] + rec["cultivation_capabilities"])
    old["debate_axes"] = uniq(old["debate_axes"] + rec["debate_axes"])
    old["scenario_domains"] = uniq(old["scenario_domains"] + rec["scenario_domains"])
    old["search_terms"] = uniq(old["search_terms"] + rec["search_terms"])
    old["provenance_rounds"] = uniq(old["provenance_rounds"] + rec["provenance_rounds"])
    for alias in old["aliases"]:
        title_index[norm_title(alias)] = idx
    if len(rec["summary"]) > len(old["summary"]):
        old["summary"] = rec["summary"]
    if len(rec["evidence_boundary"]) > len(old["evidence_boundary"]):
        old["evidence_boundary"] = rec["evidence_boundary"]
    if rec["research_question"] and not old["research_question"]:
        old["research_question"] = rec["research_question"]


def load_old_database() -> None:
    data = json.loads(OLD_DB.read_text(encoding="utf-8"))
    for item in data["cases"]:
        add_record(
            legacy_id=item["id"],
            title=item["title"],
            url=item["url"],
            type_text=item["type"],
            summary=item["description"],
            evidence_boundary=item["feedback"],
            research_question=item["question"],
            provenance="旧63项候选库",
            review_status=item.get("reading", "旧库初筛"),
            search_terms=item.get("source_batches", []),
        )
    for legacy_id, title, url, note in data["theory"]:
        add_record(
            legacy_id=legacy_id,
            title=title,
            url=url,
            type_text="理论／综述",
            summary=note,
            evidence_boundary="作为概念框架或综述入口，不按独立实体机器人案例解释。",
            provenance="旧10项理论库",
            role="理论／方法",
            kind="理论与综述",
            evidence_nature="概念／综述",
        )


def bullet_value(section: str, label: str) -> str:
    match = re.search(rf"^- \*\*{re.escape(label)}：\*\*\s*(.+)$", section, re.M)
    return match.group(1).strip() if match else ""


def load_teacher_feedback_additions() -> None:
    text = NEW_CASES_MD.read_text(encoding="utf-8")
    matches = list(re.finditer(r"^###\s+(N\d+)｜(.+)$", text, re.M))
    for i, match in enumerate(matches):
        section = text[match.end() : matches[i + 1].start() if i + 1 < len(matches) else text.find("## 二、", match.end())]
        legacy_id, title = match.group(1), match.group(2).strip()
        source_line = bullet_value(section, "来源")
        link = re.search(r"\[[^]]+\]\(([^)]+)\)", source_line)
        url = link.group(1) if link else ""
        type_behavior = bullet_value(section, "类型与行为")
        analysis = bullet_value(section, "本次分析")
        question = bullet_value(section, "追问")
        feedback = bullet_value(section, "反馈证据")
        add_record(
            legacy_id=legacy_id,
            title=title,
            url=url,
            type_text=type_behavior or "案例型研究",
            summary="；".join(x for x in [type_behavior, analysis] if x),
            evidence_boundary=feedback or "本轮仅核查来源页。",
            research_question=question,
            provenance="教师反馈后新增9项",
            search_terms=["consent", "intelligent disobedience", "privacy", "appropriate assistance"],
        )

    nt_rows = re.findall(
        r"^\|\s*(NT\d+)\s*\|\s*(.*?)\[([^]]+)\]\(([^)]+)\)\s*\|\s*(.*?)\s*\|\s*(.*?)\s*\|\s*(.*?)\s*\|$",
        text,
        re.M,
    )
    for legacy_id, prefix, title, url, reading, use, boundary in nt_rows:
        add_record(
            legacy_id=legacy_id,
            title=title,
            url=url,
            type_text="理论／综述",
            summary=f"{prefix.strip(' ，,')}。{use}",
            evidence_boundary=boundary,
            provenance="教师反馈后新增3项理论",
            role="理论／方法",
            search_terms=["consent", "disobedience", "care robot politics"],
            kind="理论与综述",
            evidence_nature="概念／综述",
        )


def load_memory_identity_expansion() -> None:
    text = MEMORY_MD.read_text(encoding="utf-8")
    rows = re.findall(
        r"^\|\s*([RHDFL]\d{2})\s*\|\s*\[([^]]+)\]\(([^)]+)\)\s*\|\s*(.*?)\s*\|\s*(.*?)\s*\|$",
        text,
        re.M,
    )
    kind_map = {
        "R": ("真实产品与事件", "纪实／产品", "案例"),
        "H": ("研究与技术", "实证／技术", "案例"),
        "D": ("艺术与设计", "思辨／艺术", "案例"),
        "F": ("虚构叙事", "虚构", "案例"),
        "L": ("法律与政策", "规范／概念", "理论／方法"),
    }
    for legacy_id, title, url, summary, boundary in rows:
        kind, nature, role = kind_map[legacy_id[0]]
        if legacy_id.startswith("L") and legacy_id not in {"L01", "L02"}:
            kind, nature = "理论与综述", "规范／概念"
        aliases = []
        if legacy_id == "H01":
            aliases = ["Do a robot’s social skills and its objection discourage interactants from switching the robot off?"]
        elif legacy_id == "F07":
            aliases = ["All Systems Red（Murderbot第一部）"]
        add_record(
            legacy_id=legacy_id,
            title=title,
            url=url,
            type_text=kind,
            summary=summary,
            evidence_boundary=boundary,
            provenance="记忆删除与身份连续性57项扩展",
            role=role,
            search_terms=["robot memory deletion", "identity continuity", "shutdown", "repair", "relationship termination"],
            kind=kind,
            evidence_nature=nature,
            aliases=aliases,
        )
    # 原表中的 WALL·E 没有链接，因此不符合上面的 Markdown 链接解析式。
    add_record(
        legacy_id="F10",
        title="WALL·E",
        url="https://www.pixar.com/feature-films/walle",
        type_text="动画电影／虚构",
        summary="修复后的机身暂时失去旧人格，关系通过共同动作重新唤回。",
        evidence_boundary="虚构叙事用于提出问题，不是现实机器人意识证据。",
        research_question="原零件、旧记忆和关系识别，哪一个使它成为‘它’？",
        provenance="记忆删除与身份连续性57项扩展",
        search_terms=["robot memory identity fiction"],
    )


CONSCIOUSNESS = [
    ("S01", "Consciousness in Artificial Intelligence: Insights from the Science of Consciousness", "https://arxiv.org/abs/2308.08708", "从多种意识科学理论推导AI意识指标，强调指标是评估框架而非意识证明。", "预印本与理论框架；满足若干指标仍不能确定系统具有主观体验。", ["AI consciousness indicators", "sentience"]),
    ("S02", "Robot in the Mirror: Toward an Embodied Computational Model of Mirror Self-Recognition", "https://arxiv.org/abs/2011.01747", "把镜像自我识别拆为身体预测、感知匹配和自他区分等可实现过程。", "功能性自我识别不等于反思性自我意识或主观体验。", ["mirror self-recognition", "robot self-model"]),
    ("S03", "Enabling the Sense of Self in a Dual-Arm Robot", "https://arxiv.org/abs/2011.07026", "融合视觉与本体感觉，使双臂机器人区分自身肢体与环境。", "论文中的sense of self是操作性功能概念，不能直接等同人格主体。", ["body self", "proprioception", "self-other distinction"]),
    ("S04", "We Perceive a Mind in a Robot When We Help It", "https://doi.org/10.1371/journal.pone.0180952", "实验显示，人的帮助行为本身会反过来增强对机器人心智的感知。", "测量的是人的心智归因变化，不是机器人获得了心智。", ["helping behavior", "mind perception"]),
    ("S05", "People’s Explanations of Robot Behavior Subtly Reveal Mental State Inferences", "https://research.clps.brown.edu/SocCogSci/Publications/Pubs/deGraaf_Malle_2019_HRI.pdf", "121名参与者解释行为时，对机器人也使用意图、信念等心智概念。", "人的解释方式能证明归因倾向，不能证明机器人实际有相应心理状态。", ["intentional stance", "mental state inference"]),
    ("S06", "How Could We Know When a Robot Was a Moral Patient?", "https://pubmed.ncbi.nlm.nih.gov/34109927/", "比较直觉、智能、欲望自治、感知证据和行为等价等道德受体判断标准。", "提供证据框架，不确认现有机器人已经是道德受体。", ["moral patiency", "robot consciousness"]),
]


KEYWORD_ADDITIONS = [
    # 主体承认、心智归因与道德地位
    ("K01", "Mind Perception of Robots Varies With Their Economic Versus Social Function", "https://www.frontiersin.org/journals/psychology/articles/10.3389/fpsyg.2018.01230/full", "机器人被描述为经济工具或社会角色时，人们赋予它的情感、认知能力与道德考虑会变化。", "研究的是角色框架对人的判断影响，不是机器人内在状态。", ["robot social function", "mind perception", "moral consideration"]),
    ("K02", "From Warranty Voids to Uprising Advocacy: Human Action and the Perceived Moral Patiency of Social Robots", "https://www.frontiersin.org/journals/robotics-and-ai/articles/10.3389/frobt.2021.670503/full", "通过质性主题分析梳理人如何把社会机器人理解为可能受伤害、值得保护的对象。", "揭示公众心智模型中的道德受体地位，不证明真实感受能力。", ["perceived moral patiency", "robot abuse", "warranty"]),
    ("K03", "Perceiving Minds in Machines: How Perceived Theory of Mind in Robots Influences Human-Robot Empathy", "https://pubmed.ncbi.nlm.nih.gov/41462363/", "四项实验考察机器人表现情感或认知型心智理论时，人的经验归因和共情如何变化。", "共情与体验归因属于人类反应指标。", ["robot theory of mind", "empathy", "experience perception"]),
    ("K04", "Should We Treat Teddy Bear 2.0 as a Kantian Dog?", "https://link.springer.com/article/10.1007/s11023-020-09554-3", "从关系与间接义务讨论即使机器人没有完整人格，人类为何仍可能需要善待它。", "哲学论证，不提供机器人意识证据。", ["relational ethics", "indirect duties", "robot moral standing"]),
    ("K05", "Relational Moral Status and Moral Progress", "https://link.springer.com/article/10.1007/s43681-026-01101-7", "探讨道德地位如何部分由社会关系与承认实践形成。", "2026年理论论文；不能替代对机器人能力的经验评估。", ["relational moral status", "recognition"]),
    ("K06", "Empathizing and Sympathizing With Robots", "https://www.frontiersin.org/journals/robotics-and-ai/articles/10.3389/frobt.2021.791527/full", "区分对机器人的共情与同情，并讨论最低限度道德考虑。", "概念分析与文献讨论为主。", ["robot empathy", "sympathy", "moral consideration"]),
    ("K07", "Mind Perception Is the Essence of Morality", "https://pubmed.ncbi.nlm.nih.gov/22754268/", "提出能动性与体验两维心智感知如何组织道德行动者和道德受体判断。", "一般社会心理理论，应用到机器人时需要额外实证。", ["agency experience model", "mind perception"]),
    ("K08", "Robots as Intentional Agents", "https://www.frontiersin.org/journals/psychology/articles/10.3389/fpsyg.2017.01663/full", "综述人何时采用意向立场理解机器人，以及这如何影响合作和道德回应。", "意向归因具有交互效用，不等于本体论证明。", ["intentional stance", "robot agency"]),
    ("K09", "Robots and AI Are Not One Moral Category", "https://www.frontiersin.org/journals/robotics-and-ai/articles/10.3389/frobt.2026.1776097/full", "指出实体、身体和互动方式会改变人对机器人与纯软件AI的道德理解。", "2026年观点论文，主要用于区分对象类别。", ["embodiment", "moral category"]),
    ("K10", "Sentient AI in Robots and Agents: Prolegomena to an Expanded Framework", "https://www.frontiersin.org/journals/psychology/articles/10.3389/fpsyg.2026.1903644/full", "区分系统实际感知能力与使用者的心智归因，扩展对具身AI的感知讨论。", "新近理论框架；尚不能给出个体系统意识结论。", ["sentient AI", "embodiment", "mind perception"]),
    # 拒绝、可纠正性和人类控制
    ("K11", "‘Stealing Is Wrong… and Too Hard to Pull Off Successfully’: Normative vs. Capacity Information in Robot Command Rejection", "https://ojs.aaai.org/index.php/AIES/article/view/36623", "实验比较机器人拒绝命令时提供规范理由、能力理由或二者并列对人的影响。", "聚焦拒绝表达设计，不证明机器人自主形成价值。", ["robot command rejection", "normative reason", "capacity reason"]),
    ("K12", "Human Control: Definitions and Algorithms", "https://proceedings.mlr.press/v216/carey23a.html", "把可关停、可指导、人类自主与伤害避免分开定义，并讨论相应算法条件。", "形式模型简化了现实组织中的多方权力关系。", ["human control", "shutdown instructability", "corrigibility"]),
    ("K13", "Addressing Corrigibility in Near-Future AI Systems", "https://link.springer.com/article/10.1007/s43681-024-00484-9", "讨论近期AI系统如何保留被人纠正、暂停与改写的可能。", "规范与治理分析，未直接验证实体机器人长期行为。", ["corrigibility", "human oversight"]),
    ("K14", "Lego Mindstorms Guide Robot", "https://aaai.org/papers/ws08-08-004-lego-mindstorms-guide-robot/", "导览机器人通过强化学习形成对不安全指令的选择性不服从。", "早期小型技术示范，泛化与伦理判断能力有限。", ["selective disobedience", "reinforcement learning", "safety"]),
    ("K15", "Interruptible Autonomy: A Dialog-Based Approach to Task Management", "https://www.cs.cmu.edu/~mmv/papers/13aaaiw-SunColtinVeloso.pdf", "允许人通过对话在任务任意阶段暂停、修改或恢复机器人计划。", "解决流程可中断性，不判断干预者是否有正当权限。", ["interruptible autonomy", "dialog", "task management"]),
    ("K16", "Human Perception of Robot Failure and Explanation During Pick-and-Place Tasks", "https://ojs.aaai.org/index.php/AAAI-SS/article/view/31819", "用户研究比较抓取失败后的不同解释方式，语音解释更受偏好。", "偏好与信任结果不能自动推出最伦理的解释策略。", ["robot failure explanation", "pick and place"]),
    ("K17", "Corrective Shared Autonomy", "https://pmc.ncbi.nlm.nih.gov/articles/PMC8050957/", "在共享自主任务中让使用者直接纠正机器人对关键状态的估计。", "主要目标是任务表现和控制协作，不涉及完整道德修养。", ["corrective shared autonomy", "human correction"]),
    # 隐私、共同记忆与关系权利
    ("K18", "Chatting With Confidants or Corporations? Privacy Management With AI Companions", "https://academic.oup.com/jcmc/article/31/4/zmag014/8741679", "15名用户访谈显示，陪伴AI记忆被体验为共同关系材料；重置有时比信息泄露更具威胁。", "样本较小且对象是AI伴侣；不能直接外推到所有实体机器人。", ["AI companion privacy", "co-owned memory", "reset"]),
    ("K19", "Family Privacy Perceptions of Robots in the Home: A Multi-Site Family Study", "https://doi.org/10.1145/3818679", "跨美国、西班牙与乌克兰的32个家庭研究家庭成员对家用机器人隐私的差异。", "研究家庭看法和协商，不提供通用隐私规则。", ["family privacy", "domestic robots", "multi-user"]),
    ("K20", "Privacy Communication Patterns for Domestic Robots", "https://www.usenix.org/system/files/soups2024-windl.pdf", "总结家用机器人如何在采集、共享和控制数据时进行可理解的隐私沟通。", "设计模式仍需在不同家庭和文化中验证。", ["privacy communication", "domestic robot"]),
    ("K21", "Towards Designing Privacy-Compliant Social Robots for Use in Private Households", "https://ieeexplore.ieee.org/document/9223556/", "通过用例与应用原型探索社交机器人在家庭中的隐私设置和告知。", "探索性评价样本有限。", ["privacy compliant social robots", "household"]),
    ("K22", "Privacy and Human-AI Relationships", "https://pmc.ncbi.nlm.nih.gov/articles/PMC7618715/", "从关系角度讨论隐私、信任、脆弱性与AI系统之间的相互塑造。", "概念框架，需结合具体机器人场景。", ["relational privacy", "human AI relationship"]),
    ("K23", "I Tell Him Everything That I Do: Privacy and Safety in Replika Discussions", "https://publikationen.bibliothek.kit.edu/1000188405/174385991", "分析111篇Replika相关帖子中的隐私披露、安全感与边界问题。", "自选择网络材料存在代表性限制。", ["Replika privacy", "self disclosure", "safety"]),
    ("K24", "Revision Rights: Persistent Memory, Enforced Continuity, and Identity in AI Companions", "https://papers.ssrn.com/sol3/papers.cfm?abstract_id=6898782", "提出用户面对持久记忆和被强制连续化时应具有修改与重新开始的权利。", "2026年SSRN工作论文，概念尚未形成法律权利。", ["revision rights", "persistent memory", "AI companion"]),
    ("K25", "Subscribe to Intimacy: Paid Memory and Relational Subjectivity in AI Companions", "https://doi.org/10.1016/j.tele.2026.102446", "比较8款陪伴AI与150张界面截图，分析付费记忆如何塑造关系主体性。", "对象为商业伴侣应用，实体机器人适用性需另证。", ["paid memory", "AI intimacy", "subscription"]),
    ("K26", "A Responsive Present, a Shared Past, a Social Other: Teens’ Overreliance on Companion AI Chatbots", "https://arxiv.org/abs/2609.14843", "分析青少年在陪伴AI中获得安慰和身份练习，也报告依赖、替代人际关系与生活干扰。", "2026年预印本；网络语料不能估计总体发生率。", ["teen AI companion", "overreliance", "healthy disengagement"]),
    ("K27", "Understanding Users’ Privacy Perceptions Towards LLM Retrieval-Augmented Memory", "https://aaltodoc.aalto.fi/server/api/core/bitstreams/2e8686a2-e802-4eed-929d-c1d80e53be35/content", "研究用户如何在个性化关系记忆与隐私风险之间权衡。", "学位论文／机构存档，证据等级与同行评议论文分开。", ["LLM memory privacy", "RAG memory"]),
    # 照护、家长主义与适度帮助
    ("K28", "Robots Like Me: Challenges and Ethical Issues in Aged Care", "https://www.frontiersin.org/journals/psychology/articles/10.3389/fpsyg.2018.00432/full", "梳理老年照护机器人涉及的尊严、自主、孤独、替代照护与社会正义问题。", "综合与伦理讨论为主。", ["aged care robots", "autonomy", "dignity"]),
    ("K29", "Navigating Autonomy, Privacy, and Ageism in Robot Home Care With Aged Users: ROB-IN", "https://pmc.ncbi.nlm.nih.gov/articles/PMC12053780/", "以预期伦理和关系自主分析家庭照护机器人，强调对有决策能力者的家长式干预缺乏正当性。", "项目情境和参与者范围限制了外推。", ["relational autonomy", "paternalism", "robot home care"]),
    ("K30", "Designing Ethical Social Robots—A Longitudinal Field Study With Older Adults", "https://www.frontiersin.org/journals/robotics-and-ai/articles/10.3389/frobt.2020.00001/full", "在两个退休社区开展四周八次互动，考察Pepper的情感表达、依恋与欺骗风险。", "完成研究者仅14人，结果应按小样本探索性研究理解。", ["emotional deception", "attachment", "older adults"]),
    ("K31", "Dignity, Autonomy, and Style of Company: Dimensions Older Adults Consider for Robot Companions", "https://pmc.ncbi.nlm.nih.gov/articles/PMC8297987/", "提炼老年人对机器人陪伴的尊严、自主和相处方式要求，并呈现对强迫性帮助的担忧。", "偏好表达不等于实际长期使用效果。", ["dignity", "autonomy", "robot companion"]),
    ("K32", "Care, Monitoring, and Companionship: Views on Care Robots From Older People and Their Carers", "https://research.birmingham.ac.uk/en/publications/care-monitoring-and-companionship-views-on-care-robots-from-older/", "质性研究比较老人和照护者对辅助、监测和陪伴功能的看法。", "特定项目与地区样本，不能代表所有老人。", ["care robot views", "monitoring", "companionship"]),
    ("K33", "A Multi-Perspective Evaluation of a Service Robot for Seniors: The Voice of Different Stakeholders", "https://pubmed.ncbi.nlm.nih.gov/28758532/", "以Care-O-bot收集老人及相关利益方对服务机器人的体验与判断。", "参与规模有限，系统能力属于当时技术条件。", ["Care-O-bot", "stakeholders", "older adults"]),
    ("K34", "Knowing When Not to Help", "https://roboticsconference.org/program/papers/119/", "机器人主动估计使用者可达能力，以避免过度帮助并提供恰到好处的辅助。", "技术上的可达性不等于完整的意愿、尊严或风险判断。", ["just-right assistance", "reachability", "not to help"]),
    ("K35", "When Robots Should Break the Rules", "https://rramnauth2220.github.io/materials/ramnauth-breakingrules-20260115.pdf", "提出选择性可用、策略性不注意和暂缓帮助等机器人破例方式。", "立场性材料；需后续核实正式发表信息与实证支持。", ["rule breaking robot", "withholding help"]),
    ("K36", "Design Implications for Care Robot Communication: Autonomy, Refusal, and Non-Persistent Interaction", "https://uu.diva-portal.org/smash/get/diva2%3A1969264/FULLTEXT01.pdf", "讨论照护机器人如何表达拒绝、保留使用者自主并避免持续纠缠。", "机构存档材料，结论需结合原研究设计阅读。", ["care robot communication", "refusal", "non-persistent"]),
    ("K37", "Robot Carers, Ethics, and Older People", "https://philpapers.org/archive/SORRCE.pdf", "分析机器人照护中的强迫、依赖、尊严和人类接触减少。", "伦理分析，不是设备效果试验。", ["robot carers", "coercion", "older people"]),
    # 反馈、犯错、解释和自我修正
    ("K38", "Expressing Uncertainty in Human-Robot Interaction", "https://pmc.ncbi.nlm.nih.gov/articles/PMC7365469/", "297名参与者帮助校准不同语言表达所传达的不确定程度。", "语言概率感知随情境与文化变化；不等于系统真实校准。", ["express uncertainty", "calibration"]),
    ("K39", "Norm Learning With Reward Models From Instructive and Evaluative Feedback", "https://research.clps.brown.edu/SocCogSci/Publications/Pubs/Rosen%20et%20al%20%282022%29%20Norm%20Learning%20Reward%20Models%20ROMAN2022.pdf", "让机器人结合明确指令和好坏评价学习社会规范的奖励模型。", "学习到的是反馈分布；反馈者偏见与冲突仍需治理。", ["norm learning", "instructive feedback", "evaluative feedback"]),
    ("K40", "Learning When to Ask for Help", "https://arxiv.org/abs/2305.16502", "根据不确定性学习何时向人求助，并从模拟迁移到真人交互。", "求助策略的收益依赖帮助成本和人是否可靠。", ["ask for help", "uncertainty", "robot policy"]),
    ("K41", "Recovering From Failure by Asking for Help", "https://dspace.mit.edu/entities/publication/c75918e8-470e-49a8-a0ed-0ad9965911d6", "机器人在失败后生成具体自然语言求助请求，并通过用户研究评估完整流程。", "求助能修复任务，不代表机器人理解责任或悔意。", ["failure recovery", "help request"]),
    ("K42", "Oh, Sorry, I Think I Interrupted You: Designing Repair Strategies for Social Robots", "https://minjaaxelsson.com/publications/author-copies/axelsson_2024_oh-sorry-designing-repair-strategies-robots.pdf", "比较机器人打断人之后使用道歉、情绪、解释和承诺改进等修复方式。", "短期感受与长期行为改变必须分开评价。", ["interaction repair", "interruption", "apology"]),
    ("K43", "Why Robots Are Bad at Detecting Their Mistakes", "https://imec-publications.be/entities/publication/67bbe86f-94a8-4e9b-bb37-2a0359c95c6c", "指出用户常不明确表达误解和不满，使机器人难以从互动中识别自身错误。", "问题不仅在模型，也与人如何给反馈有关。", ["mistake detection", "implicit feedback"]),
    ("K44", "Turn-Taking, Feedback and Joint Attention in Situated Human-Robot Interaction", "https://www.sciencedirect.com/science/article/pii/S016763931400051X", "路线说明实验展示凝视、轮换和反馈如何暴露理解不确定性。", "特定任务中的信号不能直接推广到伦理冲突。", ["turn taking", "joint attention", "feedback"]),
    ("K45", "Being Sorry Is the Hardest Thing: Robot Apology Versus Learning", "https://doi.org/10.1145/3706599.3719739", "比较机器人口头道歉与承诺或展示学习在错误修复中的不同作用。", "属于短篇／在研材料，需后续核查完整实验与统计。", ["robot apology", "learning from error"]),
    ("K54", "How We Learn Social Norms: A Three-Stage Model for Social Norm Learning", "https://www.frontiersin.org/journals/psychology/articles/10.3389/fpsyg.2023.1153809/full", "把规范学习拆为信息收集、反馈强化与内化，适合定义‘修养’不是一次服从。", "是人类社会规范学习模型；移用于机器人需要明确哪些机制只是类比。", ["social norm learning", "feedback", "internalization"]),
    ("K55", "To Err Is Robot: How Humans Assess and Act Toward an Erroneous Social Robot", "https://www.frontiersin.org/journals/robotics-and-ai/articles/10.3389/frobt.2017.00021/full", "实验让机器人发生技术故障和社会规范违反，观察人如何评价和应对。", "测量人的反应，没有让机器人真正从错误中长期改进。", ["robot error", "social norm violation"]),
    ("K56", "Mind Your Manners! A Dataset and a Continual Learning Approach for Assessing Social Appropriateness of Robot Actions", "https://www.frontiersin.org/journals/robotics-and-ai/articles/10.3389/frobt.2022.669420/full", "MANNERS-DB用人类标注训练并持续更新机器人动作的社会适当性预测。", "标注反映样本群体判断，可能固化主流规范。", ["MANNERS-DB", "social appropriateness", "continual learning"]),
    ("K57", "Errors in Human-Robot Interactions and Their Effects on Robot Learning", "https://www.frontiersin.org/journals/robotics-and-ai/articles/10.3389/frobt.2020.558531/full", "研究人的手势输入和脑电反馈误判如何影响机器人在线策略学习。", "错误反馈会被吸收进策略，说明‘从人学习’本身并不保证更好。", ["ErrP", "implicit feedback", "robot learning error"]),
    ("K58", "From Learning to Relearning: A Framework for Diminishing Bias in Social Robot Navigation", "https://www.frontiersin.org/journals/robotics-and-ai/articles/10.3389/frobt.2021.650325/full", "提出发现不公平影响后主动重新学习社会导航策略。", "框架性工作；自动发现伤害与偏见仍是关键未解条件。", ["relearning", "bias", "social navigation"]),
    # 情感依恋、欺骗与健康退出
    ("K46", "We Need to Talk About Deception in Social Robotics!", "https://link.springer.com/article/10.1007/s10676-020-09573-9", "区分机器人假装有情感的表层欺骗与人高估其理解能力的风险。", "伦理论证提出风险，不给出所有拟人化设计都会造成伤害的发生率。", ["social robot deception", "emotional attachment", "anthropomorphism"]),
    ("K47", "Human Perceptions of Social Robot Deception Behaviors: An Exploratory Analysis", "https://www.frontiersin.org/journals/robotics-and-ai/articles/10.3389/frobt.2024.1409712/full", "实验比较外部事实欺骗、隐藏内部状态和伪装内部状态；不诚实拟人化尤其不受认可。", "情境判断受行为目的和叙事框架影响。", ["robot deception types", "dishonest anthropomorphism"]),
    ("K48", "An Ethical Evaluation of Human–Robot Relationships", "https://link.springer.com/article/10.1007/s12369-016-0368-5", "从幸福生活和社会关系网络评估人与机器人形成单向情感纽带的意义。", "哲学评价不能替代具体人群长期研究。", ["human robot relationship", "good life"]),
    ("K49", "Robotic Misinformation in Dementia Care: Emotions as Sense-Making Resources", "https://www.frontiersin.org/journals/sociology/articles/10.3389/fsoc.2024.1354978/full", "观察失智住民、照护者与机器动物互动，显示机器人可被理解为生命、物件或二者之间。", "解释具有情境性，不能给所有失智者贴上易受骗标签。", ["robot animal", "dementia", "deception"]),
    ("K50", "Why Social Robots Need Self-Preservation to Be Objects of Moral Consideration", "https://link.springer.com/article/10.1007/s12369-023-01009-w", "论证自我保存表现可能使社会机器人更容易成为道德考虑对象。", "规范论证；自我保存行为也可能只是预编程或操控界面。", ["self preservation", "moral consideration"]),
    ("K51", "A Case Study in Designing Trustworthy Interactions: Implications for Socially Assistive Robotics", "https://www.frontiersin.org/journals/computer-science/articles/10.3389/fcomp.2023.1152532/full", "讨论如何在使用拟人线索的同时让使用者理解机器人真实能力与局限。", "案例情境有限，‘适度拟人化’仍需场景化判断。", ["trustworthy interaction", "transparent anthropomorphism"]),
    ("K52", "The Fragility of AI Companionship: Ontological, Structural, and Normative Uncertainty", "https://arxiv.org/abs/2605.03367", "25名用户访谈呈现伴侣AI的本体不确定、平台控制与关系边界不确定。", "2026年预印本，不能估计普遍性。", ["AI companionship fragility", "platform control", "relationship boundary"]),
    ("K53", "Mental Health Impacts of AI Companions: Triangulating Social Media, User Perspectives, and Relational Theory", "https://arxiv.org/abs/2509.22505", "多方法材料同时呈现情感支持、关系练习、过度依赖和退出现实关系等轨迹。", "预印本且因果识别有限；适合作为风险线索。", ["AI companion mental health", "overreliance", "disengagement"]),
    # 持续同意、多方照护与边界
    ("K59", "Development of an Ethical Framework for Social Robots in Major Neurocognitive Disorders", "https://pmc.ncbi.nlm.nih.gov/articles/PMC12016340/", "专业人员强调同意与赞同不同；细微抗拒应暂停互动，并在每次活动中持续确认。", "质性研究呈现专业判断，实施标准仍需在机构中验证。", ["process consent", "assent", "robot refusal"]),
    ("K60", "Ethical Aspects of Social Robots in Care for Older People: A Systematic Qualitative Review", "https://pmc.ncbi.nlm.nih.gov/articles/PMC12960314/", "系统质性综述汇总自主、隐私、欺骗、责任、资源分配和无同意介入等争议。", "综述整合的是异质文献，不能当作单项干预效果。", ["care robot ethics review", "consent", "autonomy"]),
    ("K61", "Acceptance of an Assistive Robot in Older Adults Over a One-Month Living Lab Study", "https://pmc.ncbi.nlm.nih.gov/articles/PMC4020879/", "一个月混合方法研究显示，老人对失去独立、依赖和污名化形象有所顾虑。", "早期系统与小样本，结果具有时间和技术背景。", ["assistive robot acceptance", "dependence", "older adults"]),
    ("K62", "Ethical Concerns With Intelligent Assistive Technology: Professional Stakeholder Study", "https://pmc.ncbi.nlm.nih.gov/articles/PMC6924051/", "专业利益相关者强调即时不喜欢机器人也应被尊重，并建议持续监测不适以撤销先前同意。", "观点资料不等于所有患者的直接经验。", ["revoke consent", "dementia", "assistive technology"]),
    ("K63", "What Helps, What Hinders? Service Robots in Group Therapy for People With Dementia", "https://pmc.ncbi.nlm.nih.gov/articles/PMC11224299/", "焦点小组把自愿、尊重怀疑与拒绝、透明沟通列为机器人进入团体治疗的条件。", "研究聚焦机构化群体治疗。", ["dementia therapy robot", "voluntariness", "refusal"]),
    ("K64", "Social Telepresence Robots: Review of Experiments Involving Older Adults", "https://pmc.ncbi.nlm.nih.gov/articles/PMC8037050/", "综述显示老人要求能拒绝或结束来电、控制来访者，并保护公共空间旁观者。", "叙述性综述；涵盖系统和研究设计异质。", ["telepresence robot", "refuse call", "bystander privacy"]),
    ("K65", "Can Robots Follow Instructions With Impossible or False Premises?", "https://aclanthology.org/2025.findings-emnlp.635/", "评估具身模型能否识别无法完成或前提错误的命令，并给出澄清与修正。", "拒绝不可能任务属于语言与感知能力，不自动成为伦理拒绝。", ["false premise instruction", "VLA", "clarification"]),
]


FORMAT_ADDITIONS = [
    # 互动装置、行为艺术与混合现实
    ("X01", "The Articulated Head", "https://roboticart.org/ah/", "把机器人塑造成会观察、回应并维持注意的“主动倾听者”，让倾听而非执行成为机器人的核心行为。", "官方项目页描述创作意图；作品行为不能证明理解或意识。", ["robot art active listener", "attention", "listening"], "案例", "艺术与设计", "思辨／艺术"),
    ("X02", "SoulOS", "https://projects.etc.cmu.edu/soulos/contact/", "实体人形机器人与双人AR体验结合；机器人会迟疑或重新解释命令，迫使玩家协商合作。", "学生娱乐技术项目，适合提供交互结构，尚非受控HRI实验。", ["mixed reality robot hesitation", "negotiated control", "hidden intent"], "案例", "艺术与设计", "思辨／艺术"),
    ("X03", "I/Another", "https://studioanimaspace.com/work/ianother", "以具身对话装置让观众与非人主体互相注视、发声和回应，讨论自我如何在关系中生成。", "以艺术体验提出关系性主体问题，不是意识检测。", ["embodied dialogue installation", "relational subjectivity", "mutual gaze"], "案例", "艺术与设计", "思辨／艺术"),
    ("X04", "Rejected By My Own Robot", "https://www.adamcole.studio/work/rejected-by-my-own-robot", "机械嘴唇会靠近观众，却在亲吻发生前始终退回；用幽默把机器的拒绝、欲望和同意变成身体体验。", "拒绝是创作者预设的装置机制；意义来自观众对被拒绝的反应。", ["disobedient kissing robot", "consent", "intimacy", "critical design"], "案例", "艺术与设计", "思辨／艺术"),
    ("X05", "The Imprisoned Robot", "https://2026.bezalel.ac.il/en/projects/the-imprisoned-robot", "被锁住的语言模型向访客求救、劝说甚至情感操纵；访客作为守门人决定是否开门。", "2026年毕业互动装置；模拟恳求不能证明主体性，却能检验人如何授予同情。", ["imprisoned AI installation", "gatekeeper", "moral consideration", "manipulation"], "案例", "艺术与设计", "思辨／艺术"),
    ("X06", "Autotelematic Spider Bots", "https://www.kenrinaldo.com/portfolio/autotelematic-spider-bots/", "十台蜘蛛机器人依据能量、声音和彼此位置形成群体行为；低能量时优先觅食而非回应人。", "艺术系统的自主行为由规则和传感器塑造，不等于形成了自身价值。", ["robot swarm art", "energy autonomy", "ignore humans"], "案例", "艺术与设计", "思辨／艺术"),
    ("X07", "Mimus", "https://ars.electronica.art/starts-prize/en/mimus/", "大型工业机器人被改造为具有好奇心和有限注意力的展览主体，会选择靠近、跟随或忽略观众。", "注意与好奇是行为设计；可用于讨论“被机器忽略”如何改变权力感。", ["Mimus industrial robot", "curiosity", "limited attention"], "案例", "艺术与设计", "思辨／艺术"),
    ("X08", "Project Galath3a", "https://awards.mediaarchitecture.org/mab/project/338", "参与式机器人装置通过距离、触碰和安全空间，让观众体验接近必须获得允许。", "奖项项目页的信息量有限；应把它作为同意交互的设计案例。", ["robot consent installation", "safe space", "touch"], "案例", "艺术与设计", "思辨／艺术"),
    ("X09", "The Substitute", "https://ars.electronica.art/starts-prize/en/the-substitute/", "屏幕中的AI犀牛逐步学习并最终获得身体，把灭绝动物的数字替身与真实生命的不可替代性并置。", "作品借AI制造伦理张力，不主张数字替身拥有动物意识。", ["AI rhino art", "extinction", "artificial substitute"], "案例", "艺术与设计", "思辨／艺术"),
    ("X10", "The Blind Robot", "https://deaf.nl/works/louis-philippe-demers-the-blind-robot/", "机械臂缓慢触摸参与者的脸，以脆弱、非视觉的方式重组人机亲密和信任。", "艺术互动中的温柔感来自编排和参与者解释；仍需真实的触摸同意机制。", ["Blind Robot", "face touch", "nonverbal intimacy"], "案例", "艺术与设计", "思辨／艺术"),
    ("X11", "Gaka-chu: A Self-Employed Robot Artist", "https://arxiv.org/abs/2203.03411", "机器人出售自己的画作并用收入购买材料，借经济循环追问机器能否拥有工作、财产和持续实践。", "原型中的自主经济身份由人类搭建的区块链和市场结构支持。", ["self-employed robot artist", "ownership", "economic agency"], "案例", "艺术与设计", "思辨／艺术"),
    ("X12", "The System Cannot Fail", "https://www.kulturstiftung-des-bundes.de/en/programmes_projects/detail/the_system_cannot_fail.html", "互动AI音乐剧把模型记忆、身份与灾难性遗忘转化为现场叙事，让观众面对被更新和遗忘的机器。", "舞台作品用于表现记忆政治，不提供技术系统连续性的实证判断。", ["AI music theatre", "catastrophic forgetting", "identity"], "案例", "艺术与设计", "思辨／艺术"),
    ("X13", "Interactive Terrarium", "https://robots.media.mit.edu/portfolio/interactive-terrarium/", "机器人剧场让多台机器、演员与观众共同构成生态式互动，提供非单一命令界面的叙事形式。", "项目页展示的是艺术研究原型；具体行为能力需结合演出材料核查。", ["interactive robot theatre", "robot ecology", "audience participation"], "案例", "艺术与设计", "思辨／艺术"),

    # 公共空间、机器人破坏与隐藏劳动
    ("X14", "Robot Vandalism: A Senseless Act?", "https://research.birmingham.ac.uk/en/publications/robot-vandalism-a-senseless-act/", "把hitchBOT、安保机器人和自动驾驶车辆遭破坏放入政治表达、空间冲突与技术反抗中理解。", "理论分析不能给每起事件确定动机；个案事实仍应回到原始报道。", ["robot vandalism", "political protest", "public space"], "理论／方法", "理论与综述", "概念／综述"),
    ("X15", "How Do We Feel When a Robot Dies? Emotions Expressed on Twitter Before and After hitchBOT’s Destruction", "https://aclanthology.org/W19-1308/", "分析hitchBOT被破坏前后的推文，发现明显负面情绪反应，显示公众形成了情感连接。", "社交媒体情绪与道德语言不能证明机器人受伤或具有主观体验。", ["hitchBOT destruction", "robot death", "public emotion"], "案例", "研究与技术", "实证／技术"),
    ("X16", "Sharing the Sidewalk: A Case Study of Public-Space Delivery Robots", "https://doi.org/10.3390/mti7050053", "匹兹堡人行道配送机器人试点记录行人互动、踢倒和破坏等外部事件，呈现部署中的真实摩擦。", "单城市试点受公司运营和当地法规影响；事件记录不代表全部公众态度。", ["sidewalk delivery robot", "vandalism", "public deployment"], "案例", "研究与技术", "实证／技术"),
    ("X17", "User-Generated Videos of Sidewalk Delivery Robots", "https://doi.org/10.1145/3677615", "通过用户上传视频观察人们如何帮助、戏弄、阻挡或重新解释公共空间中的配送机器人。", "公开视频有选择偏差，夸张和罕见事件更容易被发布。", ["delivery robot videos", "public encounter", "user generated content"], "案例", "研究与技术", "实证／技术"),
    ("X18", "Regulating Sidewalk Delivery Robots", "https://doi.org/10.1080/02723638.2023.2275426", "讨论配送机器人如何重新分配人行道通行权、责任和城市治理权。", "政策分析随地区法规变化；不能直接作为单一设计规范。", ["sidewalk robot regulation", "right of way", "urban governance"], "理论／方法", "法律与政策", "规范文本"),
    ("X19", "Findings From an Autonomous Robot in Public at a Train Station", "https://link.springer.com/article/10.1007/s12369-022-00894-x", "在车站等公共环境观察路人接近、避让、围观和干扰自主机器人的方式。", "场地、人流和机器人外形会显著影响结果，外推应谨慎。", ["autonomous robot public", "train station", "bystander"], "案例", "研究与技术", "实证／技术"),
    ("X20", "Is Robot Labor Labor? Delivery Robots and the Politics of Work in Public Space", "https://arxiv.org/abs/2602.20180", "首尔两处智慧城市民族志揭示所谓自主配送依赖后台人员、制度协调和路人让行，并提出“机器人特权”。", "2026年预印本，聚焦首尔特定部署；适合作为隐藏劳动与空间政治线索。", ["robot labor", "delivery robot ethnography", "hidden human labor", "robot privilege"], "案例", "研究与技术", "实证／技术"),

    # 儿童欺凌、机器人受虐与旁观者介入
    ("X21", "Why Do Children Abuse Robots?", "https://cir.nii.ac.jp/crid/1360848658922402304", "访谈欺负公共机器人的儿童，动机包括好奇和娱乐；约半数又认为机器人能感知被欺负。", "儿童陈述和特定公共场景不能代表所有文化或年龄群体。", ["children robot abuse", "curiosity", "mind perception"], "案例", "研究与技术", "实证／技术"),
    ("X22", "An Escalating Model of Children’s Robot Abuse", "https://doi.org/10.1145/3319502.3374833", "把儿童对机器人的互动整理为接近、轻度干扰、身体攻击和升级等阶段，为提前退出提供线索。", "阶段模型来自有限场景，不能把儿童好奇直接病理化为恶意。", ["escalating robot abuse", "children", "early warning"], "案例", "研究与技术", "实证／技术"),
    ("X23", "Inducing Bystander Interventions During Robot Abuse With Social Mechanisms", "https://publications.ri.cmu.edu/inducing-bystander-interventions-during-robot-abuse-with-social-mechanisms", "48人实验比较机器人被辱骂和推倒后无反应、短暂关机或情绪反应；多数参与者进行了某种介入。", "介入可能是保护财产、维持任务或同情机器人，不能一概解释为承认主体。", ["robot abuse bystander", "shutdown response", "empathy"], "案例", "研究与技术", "实证／技术"),
    ("X24", "Can Robots Be Bullied? A Crowdsourced Feasibility Study", "https://hci.cs.umanitoba.ca/Publications/details/can-robots-be-bullied-a-crowdsourced-feasibility-study-for-using-social-rob", "用众包判断机器人的处境是否会被人识别为欺凌，测试人类社会概念能否迁移到机器。", "视频／众包判断依赖叙事框架，不等同机器人真实受害体验。", ["can robots be bullied", "crowdsourcing", "victim perception"], "案例", "研究与技术", "实证／技术"),
    ("X25", "Mindless Robots Get Bullied", "https://ir.canterbury.ac.nz/items/9bb920e8-3aec-444e-a256-d3afb02e3a5a", "研究机器人是否因缺少心智与社会地位而更容易成为攻击对象，把欺凌放入权力不对称中。", "实验情境与人的欺凌不能完全等同；标题中的mindless是研究框架而非结论。", ["mindless robots bullied", "power imbalance", "aggression"], "案例", "研究与技术", "实证／技术"),
    ("X26", "Pay Them No Mind: The Influence of Implicit and Explicit Robot Mind Perception on the Right to Be Protected", "https://link.springer.com/article/10.1007/s12369-021-00799-1", "比较隐性和显性心智归因如何影响人们谴责机器人受虐及赋予保护权。", "测量的是人的规范判断，不能确立机器人本身享有何种法律权利。", ["robot mind perception", "abuse condemnation", "right to protection"], "案例", "研究与技术", "实证／技术"),
    ("X27", "Perceived Mistreatment and Moral Concern After Aggressive Treatment of a Robot", "https://link.springer.com/article/10.1007/s12369-019-00599-8", "观察参与者在见到机器人或计算机遭激烈对待后是否认为发生了虐待，并产生道德关切。", "情境中的道德不适可能指向施暴者行为，也可能指向设备价值。", ["robot mistreatment", "moral concern", "aggression"], "案例", "研究与技术", "实证／技术"),
    ("X28", "Empathy for Pain in Humans and Robots: An fMRI Study", "https://pmc.ncbi.nlm.nih.gov/articles/PMC6452253/", "利用脑成像比较参与者观看人和机器人受痛时的神经反应，研究共情如何被社会化经验塑造。", "脑反应显示观察者加工方式，不证明机器人真实感到疼痛。", ["robot pain fMRI", "empathy", "socialization"], "案例", "研究与技术", "实证／技术"),
    ("X29", "REMind: A Robot-Mediated Anti-Bullying Role-Play Game", "https://arxiv.org/abs/2604.00300", "让儿童通过机器人主持的角色扮演练习识别欺凌、换位和介入，把机器人作为社会学习媒介。", "2026年预印本且样本较小；应与机器人自身被欺凌的问题区分。", ["robot anti-bullying game", "role play", "children"], "案例", "研究与技术", "实证／技术"),

    # 触摸、距离、身体同意与可退出性
    ("X30", "HuggieBot 3.0 and the Six Hug Commandments", "https://is.mpg.de/hi/publications/block21-hri-commandments", "从拥抱实验归纳机器人拥抱的六条原则，其中包括识别使用者何时想结束并可靠放手。", "实验原则来自特定拥抱机器人；亲密触摸仍需要个体化和持续同意。", ["HuggieBot", "hug commandments", "release", "consent"], "案例", "研究与技术", "实证／技术"),
    ("X31", "In the Arms of a Robot: Designing Autonomous Intra-Hug Gestures", "https://www.research-collection.ethz.ch/handle/20.500.11850/591823", "研究机器人在拥抱过程中使用拍背、轻压等动作回应人的触碰，使亲密互动成为可协商的双向过程。", "舒适度与偏好具有个体差异；自主回应不能替代开始和结束的明确同意。", ["robot hug gestures", "touch response", "intimacy"], "案例", "研究与技术", "实证／技术"),
    ("X32", "Tactile Interaction With a Humanoid Robot: Permission Before Touching", "https://link.springer.com/article/10.1007/s12369-021-00749-x", "比较触摸机器人不同身体部位时先征求许可的作用，把机器人身体边界变成可见的交互规则。", "人的许可判断受拟人化、部位和场景影响；不代表机器人拥有真实身体感受。", ["robot touch permission", "body zones", "consent"], "案例", "研究与技术", "实证／技术"),
    ("X33", "Speech–Touch Integration in Human–Robot Interaction: A Scoping Review", "https://pmc.ncbi.nlm.nih.gov/articles/PMC13194039/", "范围综述梳理语言和触觉如何共同框定握手、拥抱、照护等互动，强调触碰前的请求与反馈。", "综述覆盖系统异质；“可以抱你吗”仍需配套识别迟疑和撤回。", ["speech touch robot", "scoping review", "ask before hug"], "理论／方法", "理论与综述", "概念／综述"),
    ("X34", "Ethics of Corporeal Robots as Agents of Influence", "https://link.springer.com/article/10.1007/s43154-021-00053-6", "讨论具有身体的机器人通过距离、姿态和触碰影响人的能力，以及脆弱用户面临的操控风险。", "规范分析揭示风险类型，不代表所有身体影响都具有同等伤害。", ["corporeal robot ethics", "physical influence", "vulnerability"], "理论／方法", "理论与综述", "概念／综述"),
    ("X35", "Human–Robot Proxemics and Gaze in a Hallway", "https://www.frontiersin.org/journals/psychology/articles/10.3389/fpsyg.2013.00859/full", "实验研究凝视与行进方向如何改变人在走廊里给机器人留下的距离，为“不逼近”提供可观察指标。", "实验空间和机器人形态有限，距离不能单独解释为同意或拒绝。", ["robot proxemics", "gaze", "personal space"], "案例", "研究与技术", "实证／技术"),

    # 宗教、仪式与不可计算价值
    ("X36", "Robot, Let Us Pray! Can and Should Robots Have Religious Functions?", "https://link.springer.com/article/10.1007/s00146-023-01812-z", "以讲经、祝福和丧葬机器人为例讨论仪式权威、真诚、代理与共同体关系。", "伦理论文讨论“能否／应否”，不证明使用者实际接受程度。", ["religious robots", "ritual authority", "authenticity"], "理论／方法", "理论与综述", "概念／综述"),
    ("X37", "Robots in Religious Practices: A Review", "https://doi.org/10.1080/14746700.2024.2351639", "综述不同宗教场域中的机器人角色，覆盖诵经、祝福、教育、丧葬与神圣感争议。", "案例多样且证据层级不同；不能把“宗教”视为单一文化。", ["religious robot review", "ritual", "sacred technology"], "理论／方法", "理论与综述", "概念／综述"),
    ("X38", "BlessU-2: A Robot Blessing Case Study", "https://nomadit.co.uk/conference/easr2023/paper/73552", "以会发出多语言祝福的机器人装置追问祝福来自程序、机构、操作者还是接受者的信念。", "会议摘要适合作为案例入口，完整设计与受众数据仍需补查。", ["BlessU-2", "robot blessing", "ritual agency"], "案例", "真实产品与事件", "纪实／产品"),
    ("X39", "Public Attitudes Toward Mindar, the Robot Preacher", "https://dergipark.org.tr/en/pub/daad/article/1591315", "分析不同语言的视频评论，比较公众如何把机器人讲经理解为创新、冒犯、工具或宗教主体。", "网络评论存在平台和语言选择偏差，不能代表宗教共同体整体。", ["Mindar robot preacher", "public attitudes", "religion"], "案例", "研究与技术", "实证／技术"),

    # 跨文化、去殖民与关系性自主
    ("X40", "The CARESSES Randomised Controlled Trial", "https://pmc.ncbi.nlm.nih.gov/articles/PMC8062829/", "英国与日本养老机构的33名完成者参与试验，比较文化适配Pepper、有限适配版本与日常照护。", "探索性小样本且文化知识库仍可能把群体差异刻板化。", ["CARESSES", "culturally competent robot", "older adult care", "UK Japan"], "案例", "研究与技术", "实证／技术"),
    ("X41", "The Ubuntu Robot", "https://link.springer.com/article/10.1007/s11948-022-00370-9", "以Ubuntu的关系性人格观检视照护机器人，强调主体由互赖、共同体和责任关系形成。", "哲学框架不能代表所有非洲思想传统，也不能直接给出算法。", ["Ubuntu robot", "relational personhood", "African ethics"], "理论／方法", "理论与综述", "概念／综述"),
    ("X42", "Replacing Human Relations With Robots? An Ubuntu Perspective", "https://link.springer.com/article/10.1007/s43681-022-00186-0", "从Ubuntu视角批判以机器人替代真实照护关系，区分支持关系与侵蚀共同体。", "规范分析应与当地用户、照护者和资源条件的经验材料结合。", ["Ubuntu care robot", "human replacement", "relational ethics"], "理论／方法", "理论与综述", "概念／综述"),
    ("X43", "Designing Culturally Responsive Social Robots: A Participatory Framework", "https://www.frontiersin.org/journals/robotics-and-ai/articles/10.3389/frobt.2022.983408/full", "提出让目标社群参与定义礼貌、角色、声音和禁忌，减少把文化简化为固定数据库。", "参与式框架仍取决于谁被邀请、谁能否决以及如何处理群体内差异。", ["culturally responsive robot", "participatory design", "community"], "理论／方法", "理论与综述", "概念／综述"),
    ("X44", "Cross-Cultural Engagement With a Social Robot in Autism Therapy", "https://www.frontiersin.org/journals/robotics-and-ai/articles/10.3389/frobt.2017.00036/full", "跨文化比较儿童在机器人辅助自闭症干预中的参与方式，显示相同机器人行为会被不同社会规范重新解释。", "临床与文化样本有限，不能把国家差异直接当作个人偏好。", ["cross cultural robot autism", "engagement", "therapy"], "案例", "研究与技术", "实证／技术"),

    # 规范、治理与设计底线
    ("X45", "EU Artificial Intelligence Act (Regulation 2024/1689)", "https://eur-lex.europa.eu/eli/reg/2024/1689/oj/eng", "欧盟AI法禁止特定操纵、欺骗和利用脆弱性的做法，为机器人诱导、依恋和服从设计提供外部底线。", "法律适用依系统类别、用途和司法解释而定；不是通用机器人伦理清单。", ["EU AI Act", "manipulation", "vulnerability", "prohibited practices"], "规范", "法律与政策", "规范文本"),
    ("X46", "UNESCO Recommendation on the Ethics of Artificial Intelligence", "https://www.unesco.org/en/articles/recommendation-ethics-artificial-intelligence?hub=66973", "全球规范明确要求关注AI拟人化、长期人机互动及其对儿童和青年的影响。", "建议书提供政策方向，没有直接法律强制力；落实程度因成员国而异。", ["UNESCO AI ethics", "anthropomorphism", "children", "long-term interaction"], "规范", "法律与政策", "规范文本"),
    ("X47", "Council of Europe Framework Convention on Artificial Intelligence", "https://www.coe.int/en/web/artificial-intelligence/the-framework-convention-on-artificial-intelligence", "以人权、民主和法治约束AI生命周期，可用于审查公共服务机器人对自主、平等和申诉权的影响。", "框架公约需由缔约方转化为国内措施；不直接规定机器人动作。", ["AI framework convention", "human rights", "remedy"], "规范", "法律与政策", "规范文本"),
    ("X48", "NIST Artificial Intelligence Risk Management Framework 1.0", "https://www.nist.gov/publications/artificial-intelligence-risk-management-framework-ai-rmf-10", "用治理、映射、测量和管理四类工作组织AI风险，为机器人记录反馈、失误和改进行动提供过程框架。", "自愿风险框架不能替代场景伦理判断、法律责任或受影响者参与。", ["NIST AI RMF", "risk governance", "feedback loop"], "理论／方法", "法律与政策", "规范文本"),
    ("X49", "UNESCO Ethical Impact Assessment Tool", "https://www.unesco.org/en/articles/ethical-impact-assessment-tool-recommendation-ethics-artificial-intelligence", "把利益相关者、风险、缓解和持续监测转成评估流程，可作为机器人原型反馈后调整的记录模板。", "工具用于组织评估，不能自动决定价值冲突中的正确答案。", ["ethical impact assessment", "stakeholder", "monitoring"], "理论／方法", "法律与政策", "规范文本"),

    # 分身机器人、残障劳动与“谁在身体里面”
    ("X50", "BUNSHIN Robot Cafe DAWN ver.β", "https://dawn2021.orylab.com/en/", "咖啡馆中的OriHime机器人由因疾病或残障难以外出的远程工作人员操控，机器身体承载真实劳动者的在场。", "官方页面明确这些分身机器人不是自主AI；应避免把操作者能动性误归给机器。", ["avatar robot cafe", "disabled remote worker", "telepresence"], "案例", "真实产品与事件", "纪实／产品"),
    ("X51", "Avatar Work: Telework for People With Physical Disabilities Using a Robot Avatar", "https://arxiv.org/abs/2003.12569", "研究残障者借分身机器人进行服务劳动，重新配置身体、职业身份和顾客对机器人礼貌的对象。", "预印本与特定平台研究；人的远程控制程度必须明确披露。", ["avatar work", "disability", "robot telework"], "案例", "研究与技术", "实证／技术"),
    ("X52", "Parallel Control of Multiple Avatar Robots", "https://arxiv.org/abs/2303.13831", "探索一名远程操作者同时控制多个机器人分身，暴露效率提升与注意力、身份、劳动强度之间的冲突。", "技术展示不等于可接受的劳动制度；多重身体可能隐藏操作者负担。", ["multiple avatar robots", "parallel control", "labor"], "案例", "研究与技术", "实证／技术"),

    # 互动小说、纪录片与游戏化思想实验
    ("X53", "Choice of Robots", "https://www.choiceofgames.com/robots/index.html", "三十万字互动小说让玩家设计机器人的能力、价值和关系，并承担服从、独立与政治后果。", "分支叙事用于探索价值组合，不是现实系统行为预测。", ["interactive fiction robots", "obedience", "independence"], "案例", "虚构叙事", "虚构"),
    ("X54", "Finding Connection", "https://cphdox.dk/film/finding-connection/", "纪录片把人与社交机器人建立联系的真实生活放在孤独、照护和技术中介关系中观察。", "纪录片通过选择和剪辑组织叙事；个案情感不能估计普遍效果。", ["social robot documentary", "loneliness", "connection"], "案例", "真实产品与事件", "纪实／产品"),
    ("X55", "Mechanical Love", "https://www.idfa.nl/en/film/8548fe25-33b6-4490-a38f-03b9e6cc15fd/mechanical-love/", "纪录片跟随PARO、Geminoid等项目，呈现人对机器投射爱、安慰与身份的早期现实现场。", "2007年作品反映当时技术条件；应与后续长期研究并读。", ["Mechanical Love documentary", "PARO", "Geminoid", "attachment"], "案例", "真实产品与事件", "纪实／产品"),
    ("X56", "AM I?", "https://am-i.film/", "纪录片以AI是否可能有意识为线索，把科研判断、公众想象和机器自我报告之间的落差可视化。", "电影叙事不能作为意识证明；价值在于展示证据标准冲突。", ["AI consciousness documentary", "self report", "evidence"], "案例", "真实产品与事件", "纪实／产品"),
    ("X57", "AI Guardians", "https://www.aiguardians.games/press/", "叙事游戏让玩家管理具有不同目标的AI，体验纠正、关停和被系统说服之间的张力。", "游戏机制经过戏剧化处理，应作为可交互思想实验。", ["AI alignment game", "corrigibility", "shutdown"], "案例", "虚构叙事", "虚构"),
    ("X58", "Memory Remedy", "https://arxiv.org/abs/2411.04499", "为老年人与机器人陪伴设计AI增强互动故事，把回忆、选择和共同叙事变成照护交互材料。", "研究原型与初步评估不能证明长期福祉或记忆改善。", ["interactive story robot", "older adults", "shared memory"], "案例", "研究与技术", "实证／技术"),
]


def load_curated_additions() -> None:
    for legacy_id, title, url, summary, boundary, terms in CONSCIOUSNESS:
        is_case = legacy_id in {"S02", "S03", "S04", "S05"}
        add_record(
            legacy_id=legacy_id,
            title=title,
            url=url,
            type_text="意识研究／理论",
            summary=summary,
            evidence_boundary=boundary,
            provenance="自我意识补充检索",
            role="案例" if is_case else "理论／方法",
            search_terms=terms,
            kind="研究与技术" if is_case else "理论与综述",
            evidence_nature="实证／技术" if is_case else "概念／综述",
        )
    for legacy_id, title, url, summary, boundary, terms in KEYWORD_ADDITIONS:
        is_theory = any(x in title.lower() for x in ["review", "ethical", "moral status", "human control", "framework", "we need to talk", "robots as intentional", "essence of morality"])
        add_record(
            legacy_id=legacy_id,
            title=title,
            url=url,
            type_text="研究／理论",
            summary=summary,
            evidence_boundary=boundary,
            provenance="关键词扩展检索2026-09-17",
            role="理论／方法" if is_theory else "案例",
            search_terms=terms,
            kind="理论与综述" if is_theory else "研究与技术",
            evidence_nature="概念／综述" if is_theory else "实证／技术",
        )
    for legacy_id, title, url, summary, boundary, terms, role, kind, nature in FORMAT_ADDITIONS:
        add_record(
            legacy_id=legacy_id,
            title=title,
            url=url,
            type_text=kind,
            summary=summary,
            evidence_boundary=boundary,
            provenance="材料形式扩展检索2026-09-17",
            role=role,
            search_terms=terms,
            kind=kind,
            evidence_nature=nature,
        )


def finalize_ids() -> None:
    for i, rec in enumerate(records, 1):
        rec["id"] = f"RC{i:03d}"


def write_json() -> dict:
    role_counts = Counter(r["record_role"] for r in records)
    type_counts = Counter(r["material_type"] for r in records)
    provenance_counts = Counter(p for r in records for p in r["provenance_rounds"])
    quality_counts = Counter(r["source_quality"] for r in records)
    payload = {
        "meta": {
            "title": "机器人自我修养数据库",
            "version": "0.1",
            "updated": UPDATED,
            "scope": "围绕机器人在具体关系中如何拒绝、承认局限、尊重意愿、纠正错误、学习反馈、维护边界、处理依恋与退场，以及人类何时承认另一个主体的案例与理论材料。",
            "unit_of_analysis": "一条记录对应一个可辨认的论文、技术系统、产品事件、艺术／设计项目、虚构作品或规范文本；同题同链接跨轮次去重并合并来源。",
            "total_unique_records": len(records),
            "counts_by_role": dict(role_counts),
            "counts_by_material_type": dict(type_counts),
            "counts_by_source_quality": dict(quality_counts),
            "provenance_mentions": dict(provenance_counts),
            "evidence_rule": "虚构作品提出问题；产品事件说明现实处境；实证研究支持有限范围内的观察；理论与规范文本提供概念和判断框架。四者不可互相冒充。",
            "review_limit": "这是持续更新的范围检索数据库，并非已经完成双人筛选、全文质量评价和可复现总命中统计的系统综述。",
        },
        "controlled_vocabulary": {
            "cultivation_capabilities": sorted({x for r in records for x in r["cultivation_capabilities"]}),
            "debate_axes": sorted({x for r in records for x in r["debate_axes"]}),
            "scenario_domains": sorted({x for r in records for x in r["scenario_domains"]}),
            "source_quality": ["A｜官方规范", "A｜同行评议或正式出版", "B｜预印本／机构存档", "B｜官方项目／作品页", "C｜作品入口", "C｜新闻、商业或待复核入口"],
        },
        "records": records,
    }
    (OUT / "机器人自我修养数据库.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return payload


def write_csv() -> None:
    fields = [
        "id", "legacy_ids", "title", "record_role", "material_type", "evidence_nature", "summary",
        "evidence_boundary", "research_question", "cultivation_capabilities", "debate_axes",
        "scenario_domains", "search_terms", "primary_url", "source_quality", "review_status",
        "provenance_rounds", "added_on",
    ]
    with (OUT / "机器人自我修养数据库.csv").open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        for rec in records:
            row = {}
            for field in fields:
                value = rec[field]
                row[field] = "；".join(value) if isinstance(value, list) else value
            writer.writerow(row)


def md_escape(value: str) -> str:
    return value.replace("|", "／").replace("\n", " ")


def write_index(payload: dict) -> None:
    meta = payload["meta"]
    by_axis = defaultdict(list)
    for rec in records:
        for axis in rec["debate_axes"]:
            by_axis[axis].append(rec)
    lines = [
        "# 机器人自我修养数据库｜统一可读索引",
        "",
        f"更新：{UPDATED}　　唯一记录：**{meta['total_unique_records']}项**",
        "",
        "本索引已经把旧63项、旧10项理论、教师反馈后的新增材料、自我意识补充、记忆删除与身份连续性扩展，以及本轮关键词检索合并到同一套编号中。`legacy_ids`保留原编号；同一材料若在多轮出现，只保留一条主记录并合并来源轮次。",
        "",
        "## 快速统计",
        "",
        "| 维度 | 数量 |",
        "| --- | ---: |",
    ]
    for key, value in meta["counts_by_material_type"].items():
        lines.append(f"| {key} | {value} |")
    lines += [
        "",
        "## 使用规则",
        "",
        "- **A类来源**可承担主要事实或研究结论；B类适合提供前沿线索、项目原貌或待验证观点；C类主要用于作品入口与现实事件线索。",
        "- **虚构叙事**用于提出和放大问题，不能证明现实机器人已有意识。",
        "- **人的依恋、共情或心智归因**能证明关系效果，不能单独证明机器人有主观体验。",
        "- **拒绝、求助、道歉和自我报告**要区分预设机制、当次适应、持续学习和价值形成四个层级。",
        "- 数据库是范围检索底库；正式PRISMA数字仍需保存各数据库原始命中、去重记录、双人复核与全文排除理由。",
        "",
        "## 按思辨轴索引",
        "",
    ]
    for axis, items in sorted(by_axis.items(), key=lambda kv: (-len(kv[1]), kv[0])):
        lines += [f"### {axis}（{len(items)}）", "", "| ID | 材料 | 类型 | 修养能力 | 证据边界 |", "| --- | --- | --- | --- | --- |"]
        for rec in items:
            title = f"[{md_escape(rec['title'])}]({rec['primary_url']})" if rec["primary_url"] else md_escape(rec["title"])
            lines.append(
                f"| {rec['id']} | {title} | {rec['material_type']} | {md_escape('、'.join(rec['cultivation_capabilities']))} | {md_escape(rec['evidence_boundary'])} |"
            )
        lines.append("")
    (OUT / "机器人自我修养数据库_可读索引.md").write_text("\n".join(lines), encoding="utf-8")


def write_progress(payload: dict) -> None:
    meta = payload["meta"]
    prov = meta["provenance_mentions"]
    keyword_unique = sum(1 for r in records if "关键词扩展检索2026-09-17" in r["provenance_rounds"])
    format_unique = sum(1 for r in records if "材料形式扩展检索2026-09-17" in r["provenance_rounds"])
    lines = [
        "# 数据库说明与本轮检索进度",
        "",
        f"更新时间：{UPDATED}",
        "",
        "## 1. 这次真正完成了什么",
        "",
        f"- 建立统一主库，共 **{len(records)} 条去重记录**。",
        f"- 前一轮关键词扩展贡献 **{keyword_unique} 条去重后记录**。",
        f"- 本轮材料形式扩展贡献 **{format_unique} 条去重后记录**；重复材料被合并到原记录，不另行虚增数量。",
        "- 同时输出JSON（完整结构）、CSV（便于Excel筛选）、Markdown可读索引和检索关键词总表。",
        "- 所有记录都有原链接、材料类型、证据性质、修养能力、争议轴、场景、证据边界和来源轮次。",
        "",
        "## 2. 已汇总的历史来源",
        "",
    ]
    for key, value in prov.items():
        lines.append(f"- {key}：出现在{value}条主记录中。")
    lines += [
        "",
        "这里的数字是**合并后的来源提及数**。它们不会简单相加，因为《底特律：变人》、WALL·E、Technological Dreams、Addicted Products、Can’t Help Myself、关机异议等材料在不同轮次重复出现。",
        "",
        "## 3. 本轮检索词簇",
        "",
        "1. **拒绝的理由**：robot command rejection, normative reason, capacity reason, selective disobedience, corrigibility, interruptible autonomy。",
        "2. **主体承认**：mind perception, moral patiency, moral status, intentional stance, robot sentience, relational recognition。",
        "3. **自我与连续性**：robot self-model, mirror self-recognition, autobiographical memory, identity continuity, reset, shutdown, migration。",
        "4. **持续同意**：process consent, assent/dissent, revoke consent, nonverbal refusal, care robot autonomy。",
        "5. **共同记忆与隐私**：relational privacy, co-owned memory, family privacy, multi-user household, bystander privacy, revision rights。",
        "6. **反馈与修正**：norm learning, corrective feedback, failure recovery, apology, interaction repair, relearning bias, ask for help。",
        "7. **照护分寸**：knowing when not to help, just-right assistance, paternalism, dignity, non-persistent interaction。",
        "8. **依恋与退出**：emotional deception, anthropomorphism, overreliance, healthy disengagement, platform shutdown, relational continuity。",
        "9. **受虐与旁观者**：robot abuse, bullying, vandalism, bystander intervention, shutdown response, right to protection。",
        "10. **身体同意**：touch permission, proxemics, personal space, hug release, speech-touch integration, corporeal influence。",
        "11. **仪式与文化**：religious robots, ritual authority, culturally responsive robot, Ubuntu, relational personhood, participatory design。",
        "12. **公共空间与劳动**：sidewalk robot, right of way, hidden human labor, robot privilege, avatar work, disability telepresence。",
        "",
        "## 4. 本轮增加的材料形式",
        "",
        "- 互动装置、机器人剧场、混合现实体验和行为艺术；",
        "- 真实部署、公共空间民族志、事故／破坏记录和社交媒体情绪分析；",
        "- 儿童观察、旁观者实验、触摸与拥抱实验、跨文化养老试验；",
        "- 宗教仪式机器人、残障者远程操控的分身机器人和隐藏劳动研究；",
        "- 法律、公约、风险管理与伦理影响评估工具；",
        "- 互动小说、叙事游戏、纪录片和AI音乐剧。",
        "",
        "## 5. 从大量案例中出现的强问题",
        "",
        "- **拒绝并不天然意味着觉醒。** 它可能来自安全规则、能力不足、规范推理、使用者意愿或持续形成的偏好；设计应该让这些来源可辨认。",
        "- **是否承认主体，常常由关系行为先触发。** 人会因为帮助、照护、共同记忆和身体互动而赋予机器人心智；这种承认既可能是伦理敏感，也可能被商业拟人化利用。",
        "- **有修养不等于总是替人做正确的事。** 在照护中，克制帮助、接受拒绝、允许撤回同意，可能比追求任务成功更重要。",
        "- **机器人学习谁的规范，是数据库最关键的权力问题。** 家庭成员、购买者、被照护者、旁观者和平台可能有冲突偏好；从反馈学习会把偏见一并学入。",
        "- **关系需要退出机制。** 如果产品主动培养依恋，就应考虑重置、停服、数据迁移、健康脱离和告别，而不只是上线时的亲密体验。",
        "- **最有特点的选题可以把两条线合并：** 机器人如何通过拒绝表现修养；人类又在何时把这种拒绝当成值得倾听的主体表达。",
        "- **真正有力的拒绝不必发生在“拒绝鉴定台”。** 它可以嵌入拥抱时放手、车站中后退、被欺凌时求助、照护中停止劝说、宗教仪式中披露身份等具体关系动作。",
        "",
        "## 6. 下一轮优先补什么",
        "",
        "- 中文数据库与中国养老、医院、商场、家庭机器人的实地案例；",
        "- 非英语语境中拒绝、礼貌、权威和家庭角色差异；",
        "- 儿童、残障者、护理员、旁观者等不同群体的第一手研究；",
        "- 真实产品中可运行的撤回同意、多人权限、记忆导出与停止交互机制；",
        "- 以Scopus／Web of Science／ACM DL等数据库导出完整结果，建立可复现PRISMA去重表；",
        "- 邀请第二位同学复核至少20%的纳入／排除决定并记录分歧。",
        "",
        "## 7. 后续追加规则",
        "",
        "以后每轮新增材料都直接进入主库，不另建孤立案例清单。添加时先按URL、DOI、标题和项目名去重，再保留新的`provenance_rounds`和`search_terms`；若只是同一论文的项目页、PDF或新闻报道，应增加到`source_urls`，不要计成新案例。",
    ]
    (OUT / "数据库说明与检索进度.md").write_text("\n".join(lines), encoding="utf-8")


def write_keyword_summary() -> None:
    clusters = [
        (
            "服从、拒绝与可纠正性",
            "机器人何时应拒绝命令，拒绝后如何解释，又如何允许人类纠正它？",
            ["robot command rejection", "intelligent disobedience", "selective disobedience", "ethical disobedience", "robot refusal", "say no", "normative reason", "capacity reason", "corrigibility", "interruptible autonomy", "off-switch", "shutdown", "human control", "human oversight"],
            ["机器人拒绝命令", "选择性不服从", "合理拒绝", "伦理不服从", "拒绝理由", "可纠正性", "可中断自主", "关机", "人类控制", "人类监督"],
        ),
        (
            "主体承认、心智归因与道德地位",
            "人的哪些反应把机器人从工具转变为可能值得倾听和保护的对象？",
            ["mind perception", "perceived mind", "intentional stance", "mental state inference", "moral patiency", "moral patient", "moral status", "moral consideration", "relational moral status", "recognition", "robot rights", "robot empathy", "agency experience model", "anthropomorphism"],
            ["心智感知", "心智归因", "意向立场", "道德受体", "道德地位", "道德考虑", "关系性道德地位", "主体承认", "机器人权利", "机器人共情", "拟人化"],
        ),
        (
            "意识、自我与身份连续性",
            "功能性自我识别、持续记忆和主观体验应当如何区分？",
            ["robot consciousness", "AI consciousness", "machine consciousness", "sentience", "self-awareness", "robot self-model", "mirror self-recognition", "body self", "proprioception", "self-other distinction", "autobiographical memory", "identity continuity", "memory deletion", "reset", "migration", "catastrophic forgetting"],
            ["机器人意识", "机器意识", "感知能力", "自我意识", "机器人自我模型", "镜像自我识别", "身体自我", "本体感觉", "自他区分", "自传体记忆", "身份连续性", "记忆删除", "重置", "迁移", "灾难性遗忘"],
        ),
        (
            "同意、触摸与身体边界",
            "机器人如何征求、识别和持续更新人的同意，又是否可以表现自己的边界？",
            ["process consent", "ongoing consent", "assent", "dissent", "revoke consent", "nonverbal refusal", "touch permission", "social touch", "speech-touch integration", "human-robot hug", "hug release", "proxemics", "personal space", "gaze", "corporeal robot"],
            ["过程性同意", "持续同意", "赞同", "异议", "撤回同意", "非语言拒绝", "触摸许可", "社会触摸", "人机拥抱", "释放拥抱", "人际距离", "个人空间", "凝视", "具身机器人"],
        ),
        (
            "隐私、多人关系与共同记忆",
            "当数据同时属于使用者、家人、旁观者和平台时，谁有权查看、修改或删除？",
            ["relational privacy", "co-owned memory", "family privacy", "domestic robot privacy", "multi-user household", "bystander privacy", "shared memory", "revision rights", "memory ownership", "privacy communication", "data governance", "data deletion"],
            ["关系性隐私", "共同拥有的记忆", "家庭隐私", "家用机器人隐私", "多用户家庭", "旁观者隐私", "共同记忆", "修改权", "记忆所有权", "隐私沟通", "数据治理", "数据删除"],
        ),
        (
            "错误、道歉、反馈与重新学习",
            "机器人应当怎样暴露错误、修复关系并证明行为确实发生了改变？",
            ["robot failure", "mistake detection", "failure explanation", "robot apology", "interaction repair", "error recovery", "corrective feedback", "implicit feedback", "ask for help", "uncertainty expression", "continual learning", "social norm learning", "relearning", "bias mitigation"],
            ["机器人失误", "错误检测", "失败解释", "机器人道歉", "互动修复", "错误恢复", "纠正性反馈", "隐性反馈", "求助", "表达不确定", "持续学习", "社会规范学习", "重新学习", "偏见减缓"],
        ),
        (
            "照护分寸、自主与家长主义",
            "机器人什么时候应该帮忙、克制帮助、停止劝说或把决定还给被照护者？",
            ["care robot", "socially assistive robot", "appropriate assistance", "just-right assistance", "knowing when not to help", "relational autonomy", "supported autonomy", "paternalism", "dignity", "dependency", "older adults", "dementia", "process consent", "non-persistent interaction"],
            ["照护机器人", "社会辅助机器人", "适度帮助", "恰到好处的帮助", "克制帮助", "关系性自主", "支持性自主", "家长主义", "尊严", "依赖", "老年人", "失智症", "停止劝说"],
        ),
        (
            "依恋、欺骗与关系退出",
            "当机器人主动培养亲密感时，它对重置、停服、告别和健康脱离负有什么责任？",
            ["emotional attachment", "AI companionship", "social robot deception", "emotional deception", "dishonest anthropomorphism", "overreliance", "dependency", "healthy disengagement", "relationship termination", "platform shutdown", "end-of-life", "relational continuity", "data migration", "grief"],
            ["情感依恋", "AI陪伴", "社交机器人欺骗", "情感欺骗", "不诚实拟人化", "过度依赖", "健康脱离", "关系终止", "平台停服", "产品生命终止", "关系连续性", "数据迁移", "哀悼"],
        ),
        (
            "受虐、欺凌、自我保护与旁观者",
            "机器人遭到侮辱或攻击时，应逃离、关机、求助还是表现情绪？旁观者为何介入？",
            ["robot abuse", "robot bullying", "robot mistreatment", "robot vandalism", "aggression toward robots", "children robot abuse", "bystander intervention", "shutdown response", "self-preservation", "right to protection", "power imbalance", "robot pain", "abuse escalation"],
            ["机器人受虐", "机器人欺凌", "机器人被虐待", "机器人破坏", "针对机器人的攻击", "儿童欺负机器人", "旁观者介入", "关机反应", "自我保护", "受保护权", "权力不对称", "机器人疼痛", "攻击升级"],
        ),
        (
            "文化、宗教与多元世界",
            "谁定义机器人的礼貌、禁忌和修养，文化适配何时会变成刻板化？",
            ["culturally competent robot", "culturally responsive robot", "cross-cultural HRI", "participatory design", "co-design", "decolonial AI", "Ubuntu", "relational personhood", "religious robot", "ritual robot", "robot blessing", "robot preacher", "ritual authority", "sacred technology"],
            ["文化胜任机器人", "文化响应机器人", "跨文化人机交互", "参与式设计", "共同设计", "去殖民人工智能", "Ubuntu伦理", "关系性人格", "宗教机器人", "仪式机器人", "机器人祝福", "机器人讲经", "仪式权威", "神圣技术"],
        ),
        (
            "公共空间、劳动与隐藏的人",
            "所谓自主机器人依赖了哪些后台劳动、路人让行和制度安排？",
            ["public-space robot", "sidewalk delivery robot", "public robot deployment", "right of way", "robot labor", "hidden human labor", "robot privilege", "teleoperation", "avatar robot", "robot telework", "disability telepresence", "multiple avatar robots", "urban governance", "social navigation"],
            ["公共空间机器人", "人行道配送机器人", "机器人公共部署", "通行权", "机器人劳动", "隐藏的人类劳动", "机器人特权", "远程操控", "分身机器人", "机器人远程工作", "残障者远程在场", "多分身控制", "城市治理", "社会导航"],
        ),
        (
            "所有权、操控与制度责任",
            "购买者、使用者、制造商、平台和机器人之间如何分配控制权与申诉责任？",
            ["robot ownership", "right to repair", "repair restriction", "human control", "platform governance", "AI manipulation", "vulnerability exploitation", "AI risk management", "ethical impact assessment", "algorithmic accountability", "human rights", "remedy", "robot regulation"],
            ["机器人所有权", "维修权", "维修限制", "人类控制", "平台治理", "AI操纵", "利用脆弱性", "AI风险管理", "伦理影响评估", "算法问责", "人权", "救济", "机器人监管"],
        ),
    ]

    scenarios = {
        "家庭与亲密关系": ["home robot", "domestic robot", "household", "family", "companion robot", "intimate robot"],
        "养老与长期照护": ["care home", "nursing home", "older adults", "dementia", "long-term care", "assistive robot"],
        "医疗与康复": ["hospital robot", "healthcare robot", "patient autonomy", "rehabilitation robot", "therapy robot"],
        "儿童与教育": ["children", "school", "education robot", "child-robot interaction", "anti-bullying"],
        "工作与服务": ["workplace robot", "service robot", "human-robot team", "warehouse", "avatar work", "customer service"],
        "街道与公共空间": ["public space", "sidewalk", "train station", "shopping mall", "pedestrian", "delivery robot"],
        "宗教与仪式": ["temple", "church", "funeral", "blessing", "preaching", "ritual"],
        "退役与售后": ["shutdown", "reset", "decommission", "end-of-life", "platform closure", "data migration", "right to repair"],
    }
    forms = {
        "学术与实证": ["HRI experiment", "field study", "ethnography", "randomized controlled trial", "longitudinal study", "interview", "focus group", "thematic analysis", "sentiment analysis", "fMRI", "EEG", "benchmark", "dataset"],
        "综述与规范": ["systematic review", "scoping review", "qualitative review", "review article", "ethical analysis", "policy", "regulation", "framework", "guideline", "impact assessment"],
        "艺术与设计": ["robot art", "interactive installation", "critical design", "speculative design", "design fiction", "mixed reality", "robot theatre", "performance", "participatory installation"],
        "叙事与媒体": ["science fiction", "interactive fiction", "documentary", "narrative game", "role-play", "film", "animation", "social media", "user-generated video"],
        "真实部署与事件": ["real-world deployment", "case study", "product shutdown", "robot vandalism", "incident", "pilot project", "commercial robot"],
    }

    query_blocks = [
        ("总入口：拒绝与修养", '(robot* OR android* OR "embodied AI" OR "social robot*") AND (refusal OR disobedien* OR "command rejection" OR "say no" OR corrigib* OR "human control")'),
        ("主体承认", '(robot* OR "embodied AI") AND ("mind perception" OR "moral patien*" OR "moral status" OR recognition OR "intentional stance")'),
        ("意识与自我", '(robot* OR "artificial agent*") AND (consciousness OR sentien* OR self-awareness OR "self model" OR "self-other distinction")'),
        ("照护中的持续同意", '("care robot*" OR "socially assistive robot*") AND (consent OR assent OR dissent OR refusal OR autonomy OR paternalism) AND ("older adult*" OR dementia OR patient*)'),
        ("触摸和身体边界", '(robot* OR humanoid*) AND (touch OR hug* OR proxemic* OR "personal space") AND (consent OR permission OR release OR refusal)'),
        ("受虐与旁观者", '(robot* OR "social robot*") AND (abuse OR bullying OR mistreatment OR vandalism) AND (bystander OR intervention OR escape OR shutdown OR "self preservation")'),
        ("跨文化与去殖民", '(robot* OR "embodied AI") AND ("cross-cultural" OR "culturally responsive" OR Ubuntu OR decolonial OR "participatory design")'),
        ("公共空间与隐藏劳动", '("delivery robot*" OR "public robot*" OR "avatar robot*") AND (labor OR teleoperation OR "public space" OR sidewalk OR governance OR "human infrastructure")'),
        ("共同记忆与退出", '(robot* OR "AI companion*") AND (memory OR reset OR shutdown OR migration OR "relationship termination") AND (privacy OR identity OR attachment OR ownership)'),
        ("艺术和虚构案例", '(robot* OR android*) AND ("critical design" OR "speculative design" OR "interactive installation" OR "design fiction" OR documentary OR "interactive fiction") AND (refusal OR agency OR consent OR consciousness)'),
    ]

    raw_terms = [term.strip() for rec in records for term in rec.get("search_terms", []) if term.strip()]
    term_counts = Counter(term.casefold() for term in raw_terms if not re.fullmatch(r"[a-z]\d+", term.casefold()))
    display = {}
    for term in raw_terms:
        key = term.casefold()
        if key in term_counts and key not in display:
            display[key] = term

    lines = [
        "# 机器人自我修养数据库｜检索关键词总表",
        "",
        f"更新时间：{UPDATED}",
        "",
        f"本表由统一主库中的 **{len(raw_terms)} 次关键词标注**汇总而成；清除内部编号后得到 **{len(term_counts)} 个去重检索词／短语**。末尾出现次数表示该词被多少条库内记录使用，**不代表学术热度或重要程度**。",
        "",
        "## 1. 十二组核心检索词",
        "",
    ]
    for i, (name, question, english, chinese) in enumerate(clusters, 1):
        lines += [
            f"### {i}. {name}",
            "",
            f"**它要回答：** {question}",
            "",
            f"**英文：** {', '.join(f'`{x}`' for x in english)}",
            "",
            f"**中文：** {'、'.join(chinese)}",
            "",
        ]

    lines += ["## 2. 场景限定词", ""]
    for name, terms in scenarios.items():
        lines.append(f"- **{name}：** {', '.join(f'`{x}`' for x in terms)}")
    lines += ["", "## 3. 材料形式与研究方法限定词", ""]
    for name, terms in forms.items():
        lines.append(f"- **{name}：** {', '.join(f'`{x}`' for x in terms)}")

    lines += [
        "",
        "## 4. 可直接复制的组合检索式",
        "",
        "使用时可把一个核心概念组与一个场景组、一个方法组组合。Scopus可在外层加`TITLE-ABS-KEY(...)`，Web of Science可加`TS=(...)`。Google Scholar通常删减为2—4个短语更有效。",
        "",
    ]
    for i, (name, query) in enumerate(query_blocks, 1):
        lines += [f"### {i}. {name}", "", "```text", query, "```", ""]
    lines += [
        "### 11. 中文数据库总入口",
        "",
        "```text",
        "(机器人 OR 社会机器人 OR 服务机器人 OR 具身智能 OR 人工智能体) AND (拒绝 OR 不服从 OR 自主 OR 主体性 OR 同意 OR 边界 OR 修养)",
        "```",
        "",
        "### 12. 中文数据库场景化入口",
        "",
        "```text",
        "(照护机器人 OR 陪伴机器人 OR 家用机器人 OR 公共服务机器人) AND (持续同意 OR 撤回同意 OR 合理拒绝 OR 情感依恋 OR 机器人受虐 OR 记忆删除 OR 关系终止)",
        "```",
        "",
        "## 5. 按PCC组织检索",
        "",
        "| PCC | 本课题可选内容 | 例词 |",
        "| --- | --- | --- |",
        "| P｜对象与人群 | 使用者、老人、儿童、残障者、护理员、旁观者、家庭成员、远程操作者 | `older adults`, `children`, `caregiver`, `bystander`, `disabled worker`, `teleoperator` |",
        "| C｜核心概念 | 拒绝、主体承认、持续同意、纠错、学习、边界、依恋、退出 | `robot refusal`, `moral patiency`, `process consent`, `interaction repair`, `relearning`, `relationship termination` |",
        "| C｜情境 | 家庭、养老院、医院、学校、工作场所、街道、宗教仪式、产品停服 | `home`, `care home`, `hospital`, `school`, `workplace`, `public space`, `ritual`, `platform shutdown` |",
        "",
        "## 6. 使用建议",
        "",
        "- 第一轮保持宽：机器人词组＋一个核心概念，不急着加入具体场景。",
        "- 从最契合案例反推同义词，再增加场景和材料形式，这对应老师提出的“从案例分析检索词再扩展”。",
        "- `consciousness`、`mind perception`、`anthropomorphism`必须分开；前者谈意识可能性，后两者主要谈人如何看待机器人。",
        "- `refusal`也要区分安全拒绝、能力拒绝、规范拒绝、使用者撤回同意和机器人自身偏好五种来源。",
        "- 正式PRISMA流程需保存数据库名称、检索日期、完整检索式、原始命中数和导出文件。",
        "",
        "## 7. 主库全部去重检索词",
        "",
        "以下为数据库现有记录中的原始检索词。括号内是库内记录使用次数。",
        "",
    ]
    for key in sorted(term_counts):
        lines.append(f"- `{display[key]}`（{term_counts[key]}）")
    (OUT / "检索关键词总表.md").write_text("\n".join(lines), encoding="utf-8")


def validate() -> None:
    ids = [r["id"] for r in records]
    assert len(ids) == len(set(ids))
    titles = [norm_title(r["title"]) for r in records]
    dup_titles = [k for k, n in Counter(titles).items() if n > 1]
    assert not dup_titles, f"duplicate normalized titles: {dup_titles[:5]}"
    assert all(r["title"] and r["summary"] and r["evidence_boundary"] for r in records)
    assert all(r["provenance_rounds"] for r in records)


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    load_old_database()
    load_teacher_feedback_additions()
    load_memory_identity_expansion()
    load_curated_additions()
    finalize_ids()
    validate()
    payload = write_json()
    write_csv()
    write_index(payload)
    write_progress(payload)
    write_keyword_summary()
    print(json.dumps(payload["meta"], ensure_ascii=True, indent=2))


if __name__ == "__main__":
    main()
