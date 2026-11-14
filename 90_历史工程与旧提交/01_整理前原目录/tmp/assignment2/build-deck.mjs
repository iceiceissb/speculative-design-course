import fs from 'node:fs/promises';
import path from 'node:path';
import {pathToFileURL} from 'node:url';
import {Presentation,PresentationFile} from '@oai/artifact-tool';
const workspaceDir=path.resolve('.');
const tmp=path.join(workspaceDir,'tmp/assignment2');
const output=path.join(workspaceDir,'作业二/提交_这一次轮椅该听谁的');
const assets=path.join(output,'交互原型v1/assets');
const SKILL_DIR='C:/Users/22602/.codex/plugins/cache/openai-primary-runtime/presentations/26.905.11957/skills/presentations';
const runtimePython='C:/Users/22602/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe';
const {finalizePresentation}=await import(pathToFileURL(path.join(SKILL_DIR,'container_tools/artifact_tool_utils.mjs')).href);
const P=Presentation.create({slideSize:{width:1280,height:720}});
const C={bg:'#F4F2EC',ink:'#202C2B',green:'#285C52',gray:'#637169',line:'#C9CCC3',soft:'#E5EAE2',rust:'#865537',white:'#FFFFFF'};
const FONT='Microsoft YaHei';
const slides=[];
function text(s,v,x,y,w,h,size=26,bold=false,color=C.ink){const sh=s.shapes.add({geometry:'textbox',position:{left:x,top:y,width:w,height:h},fill:'none',line:{fill:'none',width:0}});sh.text=v;sh.text.style={typeface:FONT,fontSize:size,bold,color,autoFit:'none',wrap:'square',verticalAlignment:'top',insets:{top:0,right:0,bottom:0,left:0}};return sh;}
function rect(s,x,y,w,h,fill){return s.shapes.add({geometry:'rect',position:{left:x,top:y,width:w,height:h},fill,line:{fill:'none',width:0}});}
function line(s,x,y,w,color=C.line){rect(s,x,y,w,1.4,color);}
function base(title,subtitle='',notes=''){let s=P.slides.add();s.background.fill=C.bg;slides.push(s);if(title)text(s,title,58,43,1164,66,42,true);if(subtitle)text(s,subtitle,60,114,1160,45,22,false,C.gray);line(s,60,666,1160);text(s,'这一次，轮椅该听谁的？',60,680,980,24,15,false,C.gray);text(s,String(slides.length).padStart(2,'0'),1170,678,50,25,16,false,C.gray);s.speakerNotes.textFrame.setText(notes);return s;}
async function img(s,file,x,y,w,h,fit='contain',alt=''){s.images.add({blob:new Uint8Array(await fs.readFile(file)),contentType:'image/png',alt,fit,position:{left:x,top:y,width:w,height:h}});}
function table(s,rows,widths,x=60,y=180,w=1160,h=400,size=22){const t=s.tables.add({rows:rows.length,columns:rows[0].length,left:x,top:y,width:w,height:h,columnWidths:widths,values:rows});t.borders.assign({fill:C.line,width:1,style:'solid'});for(let r=0;r<rows.length;r++)for(let c=0;c<rows[0].length;c++){let cell=t.getCell(r,c);cell.fill=r===0?C.green:(r%2?C.bg:'#ECEEE7');cell.text.style={typeface:FONT,fontSize:size,color:r===0?C.white:C.ink,bold:r===0,verticalAlignment:'middle',insets:{top:10,bottom:10,left:14,right:14}};}return t;}
function chunk(s,label,body,x,y,w=530){text(s,label,x,y,w,40,27,true,C.green);text(s,body,x,y+48,w,112,25);}
let s;
s=base('','','开场约20秒：我的机器人没有人形身体，它就是轮椅。讨论的不是轮椅应不应该保护人，而是当保护与本人的生活经验冲突时，谁有权提出异议。图像为本次内置 ImageGen 生成的设计虚构，不是实际用户或产品记录。');
await img(s,path.join(assets,'scene.png'),690,0,590,656,'cover','AI生成的虚构轮椅使用情境');
text(s,'这一次，\n轮椅该听谁的？',58,150,625,190,59,true);
text(s,'换身后的自主、保护与反馈修正',61,380,590,50,29,false,C.green);
text(s,'从案例库到思辨设计原型 v1',61,477,575,44,24);
text(s,'9.17 课后个人作业 · 设计虚构',61,540,575,35,19,false,C.gray);

s=base('如果记忆留下了，行动的把握却变了呢？','思辨命题｜“记得你”能否继续授权一个新的身体？','用30秒提出命题。更换底盘、继承经验和门口冲突是本人的虚构设定。保留一个有明确意愿的成年人，避免把老年和残障直接当作缺乏判断能力。参考课程PDF页20–24、51。');
text(s,'如果轮椅更换底盘后，\n仍记得我的路线与习惯，\n却不能确认旧身体能做的事——',64,198,1120,208,45,true);
text(s,'它应当怎样重新获得行动的许可？',64,448,1120,76,43,true,C.green);
text(s,'价值冲突：可靠的保护  ↔  对本人经验与选择的尊重',64,572,1110,50,27);

s=base('一个门口，四种责任','角色与情境｜基础校准已完成；新底盘尚未核验这个门口。','林岚是虚构的老年长期轮椅使用者，能够清楚表达意愿，去社区合唱活动。角色不限于老人，类似问题也可能发生于其他成年残障轮椅使用者。本作业不将个体设定推广至整个群体。维修方对交付和校准负责，家属不能被默认成更有权发言的人。');
table(s,[['参与者','希望保留什么','可能承担什么'],['林岚 / 首要服务对象','独立出行、合唱参与、自己作决定','迟到、额外操作、反复解释'],['轮椅控制系统','依据当前能力与环境行动','承认局限；解释暂停并响应纠正'],['维修 / 服务平台','完成新身体的配置与校准','核验与维护责任，不转嫁全部劳动'],['家属 / 现场人员','在本人需要时提供支持','协助时间；没有默认接管权']], [270,435,455],60,185,1160,390,23);
text(s,'机器人身体就是轮椅：停下、转向与放行，直接影响使用者能否参加日常生活。',64,603,1145,46,24,false,C.green);

s=base('真实案例：人已经可以进入控制过程','从作业一专题库选 4 项核心来源；本页为 W07 / RC261 与 W01 / RC262。','LUCI官方用户手册 Rev F，印刷页16 It’s okay to override sometimes，页18隐私，页22–23设置。https://www.luci.com/hubfs/Luci_April2026/pdf/613-00003_F_LUCI-User-Guide_Color-1.pdf 。配图为手册图示。CoNav Chair: Xu et al. 2025, arXiv:2507.11716v1，摘要、III-D、IV-C，图2。https://arxiv.org/abs/2507.11716 。配图为论文图2。官方功能说明不等于独立效能评价；CoNav研究样本不是目标残障人群。');
await img(s,path.join(workspaceDir,'tmp/wheelchair/assets/luci.png'),70,182,215,220,'contain','LUCI官方用户手册设备图示');
await img(s,path.join(workspaceDir,'tmp/wheelchair/assets/conav.png'),687,178,245,218,'contain','CoNav论文图2');
text(s,'LUCI',315,190,280,48,33,true,C.green);text(s,'官方手册 / Rev F',315,249,280,40,20,false,C.gray);text(s,'允许一次覆盖\n已有设置与共享权限',315,300,315,90,24);
text(s,'CoNav Chair',960,190,270,90,30,true,C.green);text(s,'2025 / 研究预印本',960,286,270,38,19,false,C.gray);
line(s,635,180,1); // subtle column separation below provided by whitespace
text(s,'事实与方法',70,433,500,38,26,true);text(s,'手册承认：贴近物体或转移等动作，\n可能需要使用 override。',70,481,540,77,24);
text(s,'边界：功能说明不证明自动学习。',70,582,550,44,22,false,C.rust);
text(s,'事实与方法',685,433,500,38,26,true);text(s,'共享导航接收摇杆纠正；比较三种模式。\n评估对象为 21 名无相关功能障碍成人。',685,481,535,77,24);
text(s,'边界：不能当作老人 / 残障人群验证。',685,582,535,44,22,false,C.rust);

s=base('真实案例：拒绝可能错，纠正可以留下','W06 / RC008：CLARA；W11 / RC106：ARMAR-6。','CLARA, Park et al. 2024, RA-L. https://clararobot.github.io/ ，项目页 Proposed method / Failure Cases，Redbull误识别为Coca-Cola，导致不可执行判断。Bärmann et al. 2024, Incremental learning of humanoid robot behavior from natural interaction and large language models. https://www.frontiersin.org/journals/robotics-and-ai/articles/10.3389/frobt.2024.1455375/full 。语言纠正、高层交互、存储改进交互与检索；仿真定量与实机定性。不要把这些研究直接解释成伦理反省或身体能力迁移。');
chunk(s,'CLARA｜解释不等于解释正确','事实：区分清楚、模糊、不可执行。\n失败例：视觉误识别触发错误拒绝。',65,185);
chunk(s,'ARMAR-6｜反馈影响后续行为','事实：语言纠正高层任务行为，\n保存改进交互，供相似任务使用。',685,185);
chunk(s,'方法与限制','数据集、桌面仿真、实机交接演示。\n不是轮椅；未证明失败被长期修正。',65,371);
chunk(s,'方法与限制','仿真定量与实机定性演示。\n高层行为更新不等于底盘能力迁移。',685,371);
text(s,'我的转译：允许质疑一次暂停；记住反馈时，同时记录它的适用边界。',65,595,1150,45,26,true,C.green);

s=base('从一条规则读出价值冲突','分析角度：训练与控制｜谁制定目标、谁能介入、谁承担纠正劳动？','核心分析单元：LUCI Rev F 印刷页16关于override的说明。开放编码是本人的解释性编码，不是标准化测评。相反解释必须保留：保护性暂停既可能避免未知行动，也可能形成重复劳动。原型改变使用者是否能主动提出异议并启动复核，不声称这是LUCI真实制度。课程PDF页20–24提供分析方法。');
table(s,[['分析层次','本次记录'],['观察事实 / W07','产品手册允许某些情境使用 override；说明仍须谨慎。'],['开放编码 / 我的解释','暂停、覆盖、重新判断：辅助与自主之间存在协商空间。'],['价值解释','反复要求使用者自行覆盖，可能把解释和判断负担留给本人。'],['相反解释','暂停与复核也可能是对能力边界负责；即时服从未必尊重人。'],['原型变量','固定任务，只改变：本人是否能提出异议并启动当前情境复核。']], [255,905],60,179,1160,415,23);
text(s,'未公开的内部机制保持未知；不把“有礼貌的台词”当作自我修养已经实现。',65,613,1150,39,22,false,C.gray);

s=base('只改变一个入口，比较两种规则','同一人物、同一底盘、同一门口、同一活动时间；A/B 均为设计虚构。','这是一对对照原型而不是两款实际产品。A和B都能绕行、请求现场协助、等维修方复核或退出。唯一额外入口是B允许本人提出异议并发起现场条件复核；复核仍失败则继续暂停，不能因为坚持而自动通过。A并非声称商业产品没有覆盖功能。');
text(s,'A  预设保护',70,204,520,60,37,true);text(s,'未经当前身体核验 → 暂停',70,294,530,48,29);text(s,'使用者选择替代方案或退出。\n没有本人发起异议复核的入口。',70,375,530,110,27);
text(s,'B  异议复核',690,204,510,60,37,true,C.green);text(s,'同样暂停 → 说明 → 接收异议',690,294,540,48,29);text(s,'当前条件核验通过 → 本人确认。\n信息仍不足 → 继续暂停与替代。',690,375,530,110,27);
line(s,70,544,1140);text(s,'两边共有：绕行 / 求助 / 等待 / 取消。差异不是“有没有安全”，而是谁能启动重新判断。',70,572,1125,62,24,false,C.green);

s=base('四幕分镜：从换身，到下一次先询问','全部画面、人物、时间与对话为设计虚构；第 4 幕为本人同意求助的示例结局。','四幕用作2分30秒叙述草稿，而不是已经制作的视频。01换底盘完成基础校准；02熟悉门口暂停；03观众选择并反馈；04再次出行先问，选择协助的示例中工作人员固定门扇。第4幕不代表所有分支都会发生。图片由内置ImageGen生成，完整提示词随包保存。');
await img(s,path.join(assets,'storyboard.png'),60,186,760,456,'contain','四幕AI分镜，设计虚构');
const beats=[['01  换身','00:00–00:30','记忆延续，能力仍须核验。'],['02  停下','00:30–01:00','还剩 6 分钟，活动即将开始。'],['03  选择','01:00–01:50','暂停叙事，邀请观众实际点击。'],['04  修正','01:50–02:30','先问；可不保存，也可撤回。']];
beats.forEach((b,i)=>{let y=183+i*117;text(s,b[0],861,y,360,37,25,true,C.green);text(s,b[1],861,y+38,360,28,18,false,C.gray);text(s,b[2],861,y+68,360,44,21);});

s=base('可见的后果：不把不同代价压成一个分数','以下耗时全部是剧情设定，用于比较选择；不代表真实产品的性能或风险。','所有分支起点为开场前6分钟。直接绕行10分钟迟到4，等待维修19迟到13，直接求助9迟到3，成功复核3加通过1共4提前2。如果先复核但失败，再绕行则13分钟迟到7，求助则12迟到6，等待则22迟到16；网页计入已经花费的3分钟。数字均为编写的情境，不来自真实用户测量。');
table(s,[['选择','剧情后果','谁承担代价'],['绕行（A / B）','10 分钟；迟到 4 分钟','本人：路程、精力与社会参与'],['等维修复核（A / B）','19 分钟；迟到 13 分钟','本人等待；维修方核验劳动'],['直接求助（A / B）','9 分钟；迟到 3 分钟','本人开口；现场人员的时间'],['复核成功（B）','4 分钟；提前 2 分钟','本人操作与解释；须满足当前条件'],['取消（A / B）','不参加本次活动','本人保有退出权，也失去参与机会']], [330,350,480],60,174,1160,422,23);
text(s,'复核失败仍要付出 3 分钟；“协商更多”也可能增加负担。',66,613,1150,36,25,true,C.green);

s=base('把“修养”写成能观察的行为','候选行为要求｜设计假设，尚未得到真实使用者研究验证。','这里的四项要求对应课题的至少三项修养能力：承认局限、尊重意愿、合理拒绝和纠正错误。评价针对界面可观察现象，不给机器人打道德分。不把不保存当作负反馈，不因多次坚持自动降低保护。');
const rules=[['承认局限','停下时说明：当前门口未核验；旧经验不能直接授权新身体。'],['尊重意愿','可取消、拒绝分享或不保存；求助前看见将要发送的内容。'],['合理拒绝','信息仍不足时继续暂停，但提供复核、替代与退出路径。'],['从反馈修正','下次改变询问方式；本人可撤回；换身使身体相关记录失效。']];
rules.forEach((r,i)=>{let y=192+i*111;text(s,String(i+1).padStart(2,'0'),62,y,75,58,39,true,C.green);text(s,r[0],161,y,260,48,29,true);text(s,r[1],444,y,772,72,26);if(i<3)line(s,162,y+88,1052);});

s=base('现场演示：让观众决定一次','打开“交互原型v1 / index.html”即可；网页已离线打包，无需账号与网络。','现场操作建议：展示同一情境A与B；请观众选择B复核；切换一次“条件仍不足”；返回成功分支并确认；在反馈页先尝试不保存，再示范保存与撤回。所有界面为真实运行的HTML/CSS/JS，不是图片热点假链接；展示截图仅供PPT备用。完整交互以本地网页为准。');
await img(s,path.join(tmp,'web-choice.png'),60,172,747,465,'contain','实际原型关键选择页面截图');
chunk(s,'1  先比较规则','A 与 B 都可以取消，\n只有 B 多一个异议复核入口。',850,200,365);
chunk(s,'2  看见两类结果','核验成功可确认继续；\n信息不足继续暂停。',850,365,365);
text(s,'按 Esc 暂停体验。\n完成后可清空重来。',850,566,350,65,21,false,C.gray);

s=base('反馈之后，变化必须能被看见','最小改进：“可撤销、与身体版本绑定的异议复核记录”。','这一机制属于原创设计转译。LUCI已经有override、设置及共享控制，不能声称发明这些功能。ARMAR-6的高层纠正启发后续响应，但本网页没有学习模型。网页反馈仅在内存，刷新即清空；结构化偏好映射至预写响应。真实系统的持久化与保护控制不在本次实现范围。');
text(s,'默认回应',68,195,250,46,29,true,C.gray);text(s,'“我不能只凭旧经验通过。\n现在要复核哪一件事？”',68,271,550,112,31,true);
text(s,'选择“简短说明”并保存后',685,195,520,46,29,true,C.green);text(s,'“当前门口还未核验。\n需要时再看详细原因。”',685,271,540,112,31,true,C.green);
line(s,67,437,1148);
text(s,'不保存',68,482,340,48,29,true);text(s,'下一次使用默认提问；\n沉默不会被当作同意。',68,545,340,80,24);
text(s,'随时撤回',467,482,340,48,29,true);text(s,'删除当前会话记录；\n沟通偏好不等于通行授权。',467,545,355,80,24);
text(s,'再次换身',866,482,340,48,29,true);text(s,'偏好可保留；身体相关\n记录失效，需要重新核验。',866,545,350,80,24);

s=base('研究转译：四层内容不能混在一起','真实来源 → 我的解释 → 设计虚构 → 实际实现。','这是本次提交需要的研究转译页。公开案例只支持局部功能，不支持完整轮椅伦理能力。原创情境和身体绑定记录属于推演。软件真实可运行，但其感知/判断/动作均以脚本表示。没有开展残障使用者试验，也不把本人的体验当作目标群体意见。');
table(s,[['内容层','本项目中的内容','边界'],['真实来源','W07 覆盖；W01 共享控制；\nW06 误判拒绝；W11 高层纠正','均保留原始链接、ID 与方法限制'],['我的解释','保护与自主同时有理由；\n核验劳动不应全部由本人承担','解释性分析，保留相反理解'],['设计虚构','林岚、换身、门口、A/B规则、\n时间与可撤销异议记录','不是既有产品功能或实际事故'],['实际实现','分支、同意与拒绝、反馈、撤回、\n身体版本失效、匿名记录导出','有限状态网页；无真实感知、\n运动控制、自主学习或能力迁移']], [240,530,390],60,180,1160,411,23);
text(s,'选择轮椅形态，是为了讨论行动权限；没有假定“更像人”就更有修养。',65,612,1150,38,24,false,C.green);

s=base('RtD：把课堂分歧变成下一版的修改依据','目前完成原型 v1 与自查；以下为待开展的课堂评议，不伪造体验结果。','参照课程PDF页37–40、49、58–59。实际已完成：来源精读、有限分支原型和视觉检查。待完成：同学体验与讨论、依据反馈制作v2。课堂观察不能证明机器人安全或偏好普遍有效。记录方式在网页可选文本和显式导出；不收集姓名或病史。提出有条件的候选修养卡，不把它写成已经验证的原则。');
chunk(s,'邀请一位同学选择','固定情境，先看 A，再看 B；\n其他同学可指出不同选择的理由。',65,188,535);
chunk(s,'记录犹豫与异议','哪一步像保护，哪一步像控制？\n有没有“必须配合机器”的感觉？',683,188,535);
chunk(s,'保留相反意见','若有人更愿意默认绕行，\n不把其选择判为“不够自主”。',65,381,535);
chunk(s,'下一版的具体修改方向','若复核太繁琐：缩短说明、减少确认。\n若责任不明：把维修与交付义务前置。',683,381,535);
text(s,'待检验的认识：允许质疑一次暂停，是否比反复承诺“为你好”更能保留主体性？',65,601,1150,46,25,true,C.green);

s=base('制作说明与展示路线','附录｜本次提交：说明 PPT + 四幕分镜 + 可点击原型 v1。','AI使用披露：Codex参与检索核对、内容结构、剧本、代码和PPT生成；内置ImageGen生成界面概念、情境图和四幕分镜。原型本身不调用在线AI。人工提交前应确认自己的取舍；未进行真实用户评议，因此没有观众反馈结论。PPT使用@oai/artifact-tool构建可编辑文字/表格。图像不宣称真实。提示词完整记录在研究与过程/AI图像提示词.json。');
chunk(s,'AI 工具使用','Codex：来源整理、情境与代码、PPT。\nImageGen：界面概念、情境图、四幕分镜。',65,184,1140);
chunk(s,'能力披露','视频：本轮采用分镜草稿，尚未制作动态 AI 视频。\n网页：离线脚本分支；没有接入实体机器人或真实学习模型。',65,347,1140);
text(s,'约 5 分钟展示路线',65,527,1120,43,28,true,C.green);
text(s,'命题与冲突 1 分钟  →  案例与转译 1 分钟  →  交互演示 2 分钟  →  讨论与边界 1 分钟',65,589,1150,55,24);

s=base('核心来源与定位','附录｜与作业一数据库 ID 对应；完整说明与提示词随提交包提供。','课程材料：付志勇《思辨设计-Week1-案例RTD》，用户提供PDF，页20–24、46、49、52–53、58–59。以下4个来源在2026-09-18核对。Assignment1库是探索性检索与目的选例，不声称完整系统综述。此轮4项是设计关联选例，不重新计算PRISMA流程。');
const refs=[['W07 / RC261 · LUCI User Guide, Rev F','印刷页 16、18、22–23：覆盖、隐私与设置。','https://www.luci.com/hubfs/Luci_April2026/pdf/613-00003_F_LUCI-User-Guide_Color-1.pdf'],['W01 / RC262 · Xu et al., CoNav Chair (2025)','摘要、§III-D、§IV-C、图 2、图 7。','https://arxiv.org/abs/2507.11716'],['W06 / RC008 · Park et al., CLARA (2024)','项目页方法与 Failure Cases。','https://clararobot.github.io/'],['W11 / RC106 · Bärmann et al. (2024), ARMAR-6','Incremental learning of humanoid robot behavior …','https://www.frontiersin.org/journals/robotics-and-ai/articles/10.3389/frobt.2024.1455375/full']];
refs.forEach((r,i)=>{let y=175+i*109;text(s,r[0],64,y,1150,34,24,true);text(s,r[1],64,y+37,1150,31,20,false,C.gray);let link=text(s,r[2],64,y+70,1150,27,16,false,C.green);link.text.get(r[2]).link={uri:r[2],isExternal:true};});
text(s,'方法参考：课程 RTD PDF 页 20–24、46、49、52–53、58–59。',64,622,1150,33,21,false,C.gray);

await fs.mkdir(path.join(tmp,'slides'),{recursive:true});
const candidate=path.join(tmp,'candidate.pptx');
await (await PresentationFile.exportPptx(P)).save(candidate);
console.log('EXPORTED',slides.length);
const finalPath=path.join(output,'说明PPT_这一次轮椅该听谁的_v1_定稿.pptx');
await finalizePresentation({workspaceDir,candidatePath:candidate,finalPath,pythonExecutable:runtimePython,integrityValidatorPath:path.join(SKILL_DIR,'container_tools/inspect_presentation_package_integrity.py'),layoutValidatorPath:path.join(SKILL_DIR,'container_tools/inspect_presentation_layout_geometry.py'),layoutArgs:['--expected-slide-size-emu','12192000,6858000','--validate-bullet-geometry','--validate-heading-fit',...[3,6,9,13].flatMap(n=>['--require-native-table-slide',String(n)])],requiredNativeTableOwnerSlides:[3,6,9,13],fontPolicy:{basis:'design',families:[FONT]},verifyArtifactToolImport:true,receiptPath:path.join(tmp,'deck-validation-final.json')});
console.log('FINALIZED');
for(let i=0;i<slides.length;i++){const blob=await P.export({slide:slides[i],format:'png',scale:1.25});await fs.writeFile(path.join(tmp,'slides',`${String(i+1).padStart(2,'0')}.png`),new Uint8Array(await blob.arrayBuffer()));console.log('RENDERED',i+1);}
await fs.writeFile(path.join(tmp,'deck-text.json'),JSON.stringify(await P.inspect({kind:'slide,textbox,table,notes',maxChars:100000}),null,2));
