import fs from 'node:fs/promises';
import path from 'node:path';
import {pathToFileURL} from 'node:url';
import {Presentation,PresentationFile} from '@oai/artifact-tool';

const project='D:\\课\\大四上\\思辨设计\\output\\最终作业_不用麻烦她_3D交互原型';
const frames=path.join(project,'分镜图','30帧制作版');
const build=path.join(project,'.ppt_build');
const output=path.join(project,'简介PPT','简介PPT_不用麻烦她_2026-10-07_研究过程版_最终.pptx');
const SKILL_DIR='C:\\Users\\22602\\.codex\\plugins\\cache\\openai-primary-runtime\\presentations\\26.905.11957\\skills\\presentations';
const RUNTIME_PYTHON='C:\\Users\\22602\\.cache\\codex-runtimes\\codex-primary-runtime\\dependencies\\python\\python.exe';
const FONT='Microsoft YaHei';
const C={cream:'#F4EFE4',ink:'#252B26',sage:'#657E69',terra:'#9D5243',muted:'#657064',white:'#FFFAF0'};
await fs.mkdir(build,{recursive:true});
await fs.mkdir(path.dirname(output),{recursive:true});
const presentation=Presentation.create({slideSize:{width:1280,height:720}});
function rect(slide,left,top,width,height,fill){return slide.shapes.add({geometry:'rect',position:{left,top,width,height},fill,line:{fill:'none',width:0}})}
function words(slide,value,left,top,width,height,size,color,bold=false){const o=slide.shapes.add({geometry:'textbox',position:{left,top,width,height},fill:'none',line:{fill:'none',width:0}});o.text=value;o.text.style={typeface:FONT,fontSize:size,bold,color,autoFit:'none'};return o}
async function pic(slide,filename,left,top,width,height){return slide.images.add({blob:new Uint8Array(await fs.readFile(path.join(frames,filename))),contentType:'image/png',alt:filename,fit:'cover',position:{left,top,width,height}})}
function makeSlide(){const s=presentation.slides.add();s.background.fill=C.cream;return s}
function notes(slide,value){slide.speakerNotes.textFrame.setText(value)}

{
 const s=makeSlide();await pic(s,'01_路口停下_首帧.png',0,0,1280,720);rect(s,0,430,1280,290,C.ink);
 words(s,'思辨设计 · 最终作业',75,47,800,40,22,C.white,true);
 words(s,'不用麻烦她',72,470,850,94,69,C.white,true);
 words(s,'一台智能轮椅，怎样给两位朋友留出同行的空间',75,586,1130,66,31,C.white);
 notes(s,'虚构设计情境。角色及画面为项目 ImageGen 分镜参考图。课程主题：设计有修养的机器人。');
}

{
 const s=makeSlide();words(s,'研究起点：机器人自我修养库',73,60,1120,78,49,C.ink,true);
 words(s,'268',73,162,380,120,94,C.terra,true);words(s,'条去重主库记录',75,286,410,52,28,C.ink);
 words(s,'先用 PCC 定义对象、概念与情境。\n再检索、去重并标注证据性质。',75,385,502,145,26,C.ink);
 rect(s,628,174,5,420,C.sage);words(s,'轮椅专题',665,180,490,56,34,C.terra,true);
 words(s,'22 个候选 → 12 例纳入',665,260,500,60,35,C.ink,true);
 words(s,'从主库选 14 条种子，补充来源按项目归并为 8 个候选。目的性筛选，不等于对全库 268 条做系统综述。',665,355,495,180,24,C.ink);
 words(s,'专题四类：共享行动 · 承认局限 · 身体与信息边界 · 接受纠正',75,628,1100,48,22,C.muted);
 notes(s,'研究过程据项目本地《数据库说明与本轮检索进度》《检索方法与当前筛选状态》及《01_核心案例提取表.csv》：2026-09-17 主库260条去重，2026-09-18 智能轮椅专题更新至268条；专题目的性选取14条种子、归并8个新候选，共22个候选，12例纳入。12例分为共享行动决定、承认局限并澄清、尊重身体与信息边界、接受纠正并验证改变四类。探索性检索按PCC限定对象、概念、情境并记录来源、材料类型、证据性质与局限。专题不是对全库268条的系统筛选，也不是完整PRISMA系统综述。');
}
{
 const s=makeSlide();words(s,'从专题与主库选出三个参照',73,58,1130,80,49,C.ink,true);
 const items=[
  ['05_看菜根.png','RC045 · Superflux','Uninvited Guests','智能照护物件与日常习惯发生摩擦。','转译：便捷取代挑菜这件小事。'],
  ['10_删除借口_首帧.png','W09 / RC060 · Dietrich 等','信息披露研究','机器人向第三者披露个人信息有边界。','转译：是否把设备状态告诉朋友？'],
  ['21_隐瞒助力_首帧.png','RC059 · Anderson 等','价值驱动照护机器人','原则需要落实为可说明的行为。','转译：助力前说清，反馈后真改。']
 ];
 for(let i=0;i<3;i++){const x=68+i*390;await pic(s,items[i][0],x,178,368,207);words(s,items[i][1],x,404,368,43,23,C.terra,true);words(s,items[i][2],x,447,368,47,29,C.ink,true);words(s,items[i][3],x,506,368,69,20,C.ink);words(s,items[i][4],x,599,368,68,20,C.sage,true)}
 notes(s,'三个编号均来自本项目机器人自我修养主库，其中RC060同时是轮椅专题纳入案例W09；RC045、RC059是从主库回选的跨类型参照，不属于12例轮椅专题纳入项。RC045：Superflux, Uninvited Guests, https://superflux.in/index.php/work/uninvited-guests/ 。这是一部思辨设计作品，不是使用者实证研究。RC060：Dietrich 等, “What should a robot disclose about me?”, Frontiers in Robotics and AI, 2023, https://www.frontiersin.org/journals/robotics-and-ai/articles/10.3389/frobt.2023.1236733/full 。研究情境与本故事的轮椅、朋友关系不同。RC059：Anderson 等, “A Value-Driven Eldercare Robot”, Proceedings of the IEEE, 2019, https://proceedingsoftheieee.ieee.org/a-value-driven-eldercare-robot-virtual-and-physical-instantiations-of-a-case-supported-principle-based-behavior-paradigm/ 。三张图均为本项目的设计转译分镜，不是案例原图。');
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
{
 const s=makeSlide();words(s,'情境：同行，是两个人的事',74,62,1130,80,51,C.ink,true);rect(s,75,165,6,444,C.sage);
 words(s,'邱懿贞想请老朋友徐月禾陪她走一段。',108,195,490,130,35,C.ink,true);
 words(s,'邱懿贞｜熟悉菜摊，也想把自己挑的菜送给朋友。',108,355,490,77,24,C.ink);
 words(s,'徐月禾｜愿意同行，也有自己的时间。',108,448,490,77,24,C.ink);
 words(s,'秀秀｜能导航、代购、助力，也会误读人的关系。',108,541,490,77,24,C.ink);
 await pic(s,'16_见面商量_首帧.png',650,194,560,315);
 words(s,'小区缓坡 · 早市 · 夜里的邀请',654,532,560,44,23,C.muted);
 notes(s,'人物与轮椅能力均为设计虚构。角色、场景来自项目剧本和设定图。');
}
{
 const s=makeSlide();words(s,'三次善意，三次越界',73,62,1130,80,51,C.ink,true);
 const items=[
  ['06_菜摊纠错_首帧.png','替她挑菜','最低价盖过她对菜根的经验。'],
  ['10_删除借口_首帧.png','替她解释来意','设备正常，却把想念写成故障。'],
  ['21_隐瞒助力_首帧.png','替朋友省力','助力有效，推的人却不知情。']
 ];
 for(let i=0;i<3;i++){const x=67+i*390;await pic(s,items[i][0],x,185,368,207);words(s,items[i][1],x,420,368,54,31,C.terra,true);words(s,items[i][2],x,489,368,97,24,C.ink)}
 words(s,'机器未经商量，替人决定了关系中的一部分。',68,635,1120,43,25,C.muted);
 notes(s,'三次情节来自本项目的虚构剧本，不是现实案例或实验发现。');
}
{
 const s=makeSlide();words(s,'把修养变成看得见的动作',73,62,1130,80,51,C.ink,true);
 const rows=[
  ['尊重意愿','路口先停；买菜报价格后等她挑；坡道先问。'],
  ['承认局限','自检只知道设备状态，不能判断她是不是想见朋友。'],
  ['合理拒绝','不代发故障借口；拒绝代购后，另问是否需要提袋。'],
  ['纠正错误','买错可换；暗中助力被指出后，下一次先告知并等待。']
 ];
 for(let i=0;i<4;i++){const y=187+i*116;rect(s,75,y-22,1125,2,C.sage);words(s,rows[i][0],78,y,230,66,33,C.terra,true);words(s,rows[i][1],322,y,864,72,27,C.ink)}
 notes(s,'四项能力为本作品设计选择。安全底线另行保留：侧翻、跌倒或突发不适时立即接管。当前交互原型没有真实物理风险检测能力。');
}
{
 const s=makeSlide();await pic(s,'30_交换礼物.png',0,0,1280,720);rect(s,0,448,1280,272,C.ink);
 words(s,'当机器能替人走完一段路，',75,482,1130,70,45,C.white,true);
 words(s,'它能否为两个人留下“同行”的空间？',75,560,1130,90,45,C.white,true);
 notes(s,'结尾画面为项目 ImageGen 分镜参考图。可在此转入现场体验原型。AI 使用：Codex 辅助剧本整理、前端三维原型和测试；ImageGen 生成角色设定与分镜参考帧；视频阶段拟用即梦生成画面及音效，用剪映完成人声对白、字幕和剪辑。');
}

const candidate=path.join(build,'intro_v5_candidate.pptx');
await (await PresentationFile.exportPptx(presentation)).save(candidate);
for(let i=0;i<presentation.slides.length;i++){
 const png=await presentation.export({slide:presentation.slides[i],format:'png',scale:1});
 await fs.writeFile(path.join(build,`slide-${i+1}.png`),new Uint8Array(await png.arrayBuffer()));
}
const {finalizePresentation}=await import(pathToFileURL(path.join(SKILL_DIR,'container_tools','artifact_tool_utils.mjs')).href);
const result=await finalizePresentation({workspaceDir:project,candidatePath:candidate,finalPath:output,pythonExecutable:RUNTIME_PYTHON,integrityValidatorPath:path.join(SKILL_DIR,'container_tools','inspect_presentation_package_integrity.py'),layoutValidatorPath:path.join(SKILL_DIR,'container_tools','inspect_presentation_layout_geometry.py'),layoutArgs:['--expected-slide-size-emu','12192000,6858000','--validate-heading-fit'],fontPolicy:{basis:'design',families:[FONT]},requiredNativeTableOwnerSlides:[],verifyArtifactToolImport:true,receiptPath:path.join(build,'intro_v5.validation.json')});
console.log(JSON.stringify({output,slides:presentation.slides.length,result},null,2));
