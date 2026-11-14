from pathlib import Path

build = Path(__file__).resolve().parent
source = (build / 'create_intro.mjs').read_text(encoding='utf-8')
source = source.replace('简介PPT_不用麻烦她_2026-10-07_修订版.pptx', '简介PPT_不用麻烦她_2026-10-07_研究过程版.pptx')
source = source.replace('intro_candidate.pptx', 'intro_v3_candidate.pptx').replace('intro_v2.validation.json', 'intro_v3.validation.json')
new_slides = r'''
{
 const s=makeSlide();words(s,'研究起点：机器人自我修养库',73,60,1120,78,49,C.ink,true);
 words(s,'268',73,162,380,120,94,C.terra,true);words(s,'条去重主库记录',75,286,410,52,28,C.ink);
 words(s,'先按 PCC 确定对象、概念与情境，再做探索性检索、来源去重和证据性质标注。',75,385,502,145,26,C.ink);
 rect(s,628,174,5,420,C.sage);words(s,'轮椅专题',665,180,490,56,34,C.terra,true);
 words(s,'22 个候选 → 12 例纳入',665,260,500,60,35,C.ink,true);
 words(s,'从主库选 14 条种子，补充来源按项目归并为 8 个候选。目的性筛选，不等于对全库 268 条做系统综述。',665,355,495,180,24,C.ink);
 words(s,'方法记录：PCC 范围 · 检索与去重 · 来源/虚构/证据边界 · 轮椅专题选例',75,628,1100,48,22,C.muted);
 notes(s,'研究过程据项目本地《数据库说明与本轮检索进度》及《检索方法与当前筛选状态》：2026-09-17 主库260条去重，2026-09-18 智能轮椅专题更新至268条；专题目的性选取14条种子、归并8个新候选，共22个候选，12例纳入。探索性检索曾按PCC限定对象、概念、情境并记录来源、材料类型、证据性质与局限。专题不是对全库268条的系统筛选，也不是完整PRISMA系统综述。');
}
{
 const s=makeSlide();words(s,'从库里选出三项关键案例',73,58,1130,80,49,C.ink,true);
 const items=[
  ['05_看菜根.png','RC045 · Superflux','Uninvited Guests','智能照护物件与日常习惯发生摩擦。','转译：便捷取代挑菜这件小事。'],
  ['10_删除借口_首帧.png','RC060 · Dietrich 等','信息披露研究','机器人向第三者披露个人信息有边界。','转译：是否把设备状态告诉朋友？'],
  ['21_隐瞒助力_首帧.png','RC059 · Anderson 等','价值驱动照护机器人','原则需要落实为可说明的行为。','转译：助力前说清，反馈后真改。']
 ];
 for(let i=0;i<3;i++){const x=68+i*390;await pic(s,items[i][0],x,178,368,207);words(s,items[i][1],x,404,368,43,23,C.terra,true);words(s,items[i][2],x,447,368,47,29,C.ink,true);words(s,items[i][3],x,506,368,69,20,C.ink);words(s,items[i][4],x,599,368,68,20,C.sage,true)}
 notes(s,'三个编号均来自本项目机器人自我修养主库。RC045：Superflux, Uninvited Guests, https://superflux.in/index.php/work/uninvited-guests/ 。这是一部思辨设计作品，不是使用者实证研究。RC060：Dietrich 等, “What should a robot disclose about me?”, Frontiers in Robotics and AI, 2023, https://www.frontiersin.org/journals/robotics-and-ai/articles/10.3389/frobt.2023.1236733/full 。研究情境与本故事的轮椅、朋友关系不同。RC059：Anderson 等, “A Value-Driven Eldercare Robot”, Proceedings of the IEEE, 2019, https://proceedingsoftheieee.ieee.org/a-value-driven-eldercare-robot-virtual-and-physical-instantiations-of-a-case-supported-principle-based-behavior-paradigm/ 。三张图均为本项目的设计转译分镜，不是案例原图。');
}
{
 const s=makeSlide();words(s,'推理方法：让案例变成可体验的冲突',73,56,1120,80,47,C.ink,true);
 words(s,'01  先区分事实与解释',75,169,510,55,32,C.terra,true);
 words(s,'案例说明技术或作品提出过什么；不把作品情节当成轮椅实证。',75,231,520,105,25,C.ink);
 words(s,'02  把价值冲突放入具体关系',75,352,515,55,32,C.terra,true);
 words(s,'效率对上挑菜的经验；诚实对上私人邀请；省力对上同行者的知情。',75,417,515,130,25,C.ink);
 await pic(s,'24_坡顶追问.png',648,176,554,312);
 words(s,'03  用“行动 → 反馈 → 下一次行动”检验修养',651,514,540,78,29,C.sage,true);
 words(s,'原型记录行为与关系后果，不给人物打道德分。',651,602,535,48,21,C.muted);
 notes(s,'研究转译方法：案例来源事实、设计者价值解释、具体情境动作分别记录；用三类关系冲突构造分镜；在交互原型中采用先行动、观察反馈、再回应、下一次执行的闭环。方法依据本项目研究底稿与课程《思辨设计-Week1-案例RTD》提出的案例研究、Research through Design 思路。原型为脚本模拟，没有目标用户验证或真实机器人学习。');
}
'''
marker = "{\n const s=makeSlide();words(s,'情境：同行，是两个人的事'"
assert source.count(marker) == 1
source = source.replace(marker, new_slides + marker)
start = source.index("{\n const s=makeSlide();words(s,'设计依据与取舍'")
end = source.index("{\n const s=makeSlide();await pic(s,'30_交换礼物.png'", start)
source = source[:start] + source[end:]
(build / 'create_intro_v3.mjs').write_text(source, encoding='utf-8')
print('created v3 source')
