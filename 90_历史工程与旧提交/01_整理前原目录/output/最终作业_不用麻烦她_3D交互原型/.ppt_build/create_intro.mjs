import fs from 'node:fs/promises';
import path from 'node:path';
import {pathToFileURL} from 'node:url';
import {Presentation,PresentationFile} from '@oai/artifact-tool';

const project='D:\\课\\大四上\\思辨设计\\output\\最终作业_不用麻烦她_3D交互原型';
const frames=path.join(project,'分镜图','30帧制作版');
const build=path.join(project,'.ppt_build');
const output=path.join(project,'简介PPT','简介PPT_不用麻烦她_2026-10-07_修订版.pptx');
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
 const s=makeSlide();words(s,'设计依据与取舍',73,58,1130,80,51,C.ink,true);
 words(s,'Superflux《Uninvited Guests》',75,180,592,45,28,C.terra,true);
 words(s,'借用智能照护物件会改写日常节奏的提问方式。',75,229,580,79,24,C.ink);
 words(s,'机器人信息披露研究 · Dietrich 等，2023',75,331,594,47,27,C.terra,true);
 words(s,'把“向朋友说多少设备信息”变成可选择的动作。',75,382,580,79,24,C.ink);
 words(s,'价值驱动照护机器人 · Anderson 等，2019',75,491,594,45,27,C.terra,true);
 words(s,'让原则落在可说明、可纠正的下一次行动。',75,541,580,74,24,C.ink);
 await pic(s,'26_下一次先问_首帧.png',716,199,490,276);
 words(s,'设计取舍：保留应急安全接管；日常帮助分项授权。',717,506,490,107,24,C.muted);
 notes(s,'来源：Superflux, Uninvited Guests, https://superflux.in/index.php/work/uninvited-guests/ （原项目提出智能照护物件与独立生活习惯的张力）；Dietrich et al., “What should a robot disclose about me?”, Frontiers in Robotics and AI, 2023, https://www.frontiersin.org/journals/robotics-and-ai/articles/10.3389/frobt.2023.1236733/full （研究机器人向具体第三者披露个人信息的适当程度）；Anderson, Anderson and Berenz, “A Value-Driven Eldercare Robot”, Proceedings of the IEEE, 2019, https://proceedingsoftheieee.ieee.org/a-value-driven-eldercare-robot-virtual-and-physical-instantiations-of-a-case-supported-principle-based-behavior-paradigm/ （提出原则与案例支持的照护机器人行为范式）。本作品是设计虚构，不声称这些来源验证了剧本结论。');
}
{
 const s=makeSlide();await pic(s,'30_交换礼物.png',0,0,1280,720);rect(s,0,448,1280,272,C.ink);
 words(s,'当机器能替人走完一段路，',75,482,1130,70,45,C.white,true);
 words(s,'它能否为两个人留下“同行”的空间？',75,560,1130,90,45,C.white,true);
 notes(s,'结尾画面为项目 ImageGen 分镜参考图。可在此转入现场体验原型。AI 使用：Codex 辅助剧本整理、前端三维原型和测试；ImageGen 生成角色设定与分镜参考帧；视频阶段拟用即梦生成画面及音效，用剪映完成人声对白、字幕和剪辑。');
}

const candidate=path.join(build,'intro_candidate.pptx');
await (await PresentationFile.exportPptx(presentation)).save(candidate);
for(let i=0;i<presentation.slides.length;i++){
 const png=await presentation.export({slide:presentation.slides[i],format:'png',scale:1});
 await fs.writeFile(path.join(build,`slide-${i+1}.png`),new Uint8Array(await png.arrayBuffer()));
}
const {finalizePresentation}=await import(pathToFileURL(path.join(SKILL_DIR,'container_tools','artifact_tool_utils.mjs')).href);
const result=await finalizePresentation({workspaceDir:project,candidatePath:candidate,finalPath:output,pythonExecutable:RUNTIME_PYTHON,integrityValidatorPath:path.join(SKILL_DIR,'container_tools','inspect_presentation_package_integrity.py'),layoutValidatorPath:path.join(SKILL_DIR,'container_tools','inspect_presentation_layout_geometry.py'),layoutArgs:['--expected-slide-size-emu','12192000,6858000','--validate-heading-fit'],fontPolicy:{basis:'design',families:[FONT]},requiredNativeTableOwnerSlides:[],verifyArtifactToolImport:true,receiptPath:path.join(build,'intro_v2.validation.json')});
console.log(JSON.stringify({output,slides:presentation.slides.length,result},null,2));
