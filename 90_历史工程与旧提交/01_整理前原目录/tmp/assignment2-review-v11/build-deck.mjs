import fs from 'node:fs/promises';
import path from 'node:path';
import {pathToFileURL} from 'node:url';
import {Presentation,PresentationFile} from '@oai/artifact-tool';
const workspaceDir=path.resolve('.');
const tmp=path.join(workspaceDir,'tmp/assignment2-review-v11');
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
s=base('','','开场约20秒：我的机器人没有人形身体，它就是轮椅。讨论的不是轮椅应不应该保护人，而是当保护与本人的生活经验冲突时，谁有权提出异议。图像为上一版内置 ImageGen 生成的设计虚构，不是实际用户或产品记录。');
await img(s,path.join(assets,'scene.png'),690,0,590,656,'cover','AI生成的虚构轮椅使用情境');
text(s,'这一次，\n轮椅该听谁的？',58,150,625,190,59,true);
text(s,'谁承担重新确认的劳动？',61,380,590,50,29,false,C.green);
text(s,'从案例库到思辨设计原型 v1.1',61,477,575,44,24);
text(s,'9.17 课后个人作业 · 设计虚构',61,540,575,35,19,false,C.gray);

s=base('换了身体，我要重新证明自己吗？','思辨命题｜自主不只是“有权点确认”，还包括不被迫反复解释。','本版不是改变产品外观，而是改变研究问题：如果保护性暂停要求本人反复确认，机器人怎样减少这份劳动？制度反馈不能被降格为措辞调整。依据课件PDF页22–24、45、51、58。');
text(s,'如果换身使旧经验失去效力，\n轮椅应当反复请求本人确认，\n还是减少本人重新证明的劳动？',64,203,1130,206,43,true);
text(s,'谁有权修改这条规则？',64,458,1130,76,44,true,C.green);
text(s,'保护与解释的义务  ↔  不被打断、拒绝留档与参与生活的权利',64,575,1130,55,26);

s=base('一个门口，四种责任','角色与情境｜基础校准已完成；门口出现旧记录与当前感知的局部冲突。','林岚是虚构的老年长期轮椅使用者，能够清楚表达意愿，去社区合唱活动。角色不限于老人，类似问题也可能发生于其他成年残障轮椅使用者。本作业不将个体设定推广至整个群体。维修方对交付和校准负责，家属不能被默认成更有权发言的人。');
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

s=base('从一条规则读出价值冲突','分析角度：训练与控制｜谁制定目标、谁能介入、谁承担纠正劳动？','核心分析单元：LUCI Rev F 印刷页16关于override的说明。开放编码是本人的解释性编码，不是标准化测评。相反解释必须保留：保护性暂停既可能避免未知行动，也可能形成重复劳动。原型只改变由谁发起处置对话，其他行动和环境条件相同，不声称这是LUCI真实制度。课程PDF页20–24提供分析方法。');
table(s,[['分析层次','本次记录'],['观察事实 / W07','产品手册允许某些情境使用 override；说明仍须谨慎。'],['开放编码 / 我的解释','暂停、覆盖、重新判断：辅助与自主之间存在协商空间。'],['价值解释','反复要求使用者自行覆盖，可能把解释和判断负担留给本人。'],['相反解释','暂停与复核也可能是对能力边界负责；即时服从未必尊重人。'],['原型变量','固定任务，只改变：由轮椅主动发起对话，还是由本人按需打开。']], [255,905],60,179,1160,415,23);
text(s,'未公开的内部机制保持未知；不把“有礼貌的台词”当作自我修养已经实现。',65,613,1150,39,22,false,C.gray);

s=base('两种合理规则，都有可能让人疲惫','固定人物、身体、门口、记录状态与环境条件，只改变谁先发起对话。','A和B均能复核、绕行、协助、等待或退出，同条件同动作耗时相同。区别是主动解释与避免打断之间的取舍。环境由讲述者在开始前锁定，途中不能选择感知成功。两条规则均为虚构，不是产品能力比较。');
text(s,'每次主动问',70,201,520,65,39,true,C.green);text(s,'“现在愿意看原因和选项吗？”',70,298,540,68,28);text(s,'帮助：原因与选择更容易被发现。\n代价：每次停顿都开启确认对话。',70,398,535,110,27);
text(s,'由我发起',690,201,510,65,39,true,C.green);text(s,'“已暂停。” 等待本人打开。',690,298,535,68,28);text(s,'帮助：保留何时处理的主动权。\n代价：需要本人主动寻找入口。',690,398,535,110,27);
line(s,70,553,1140);text(s,'不预选、不评分；没有把成功、更快或更多权限只给其中一条规则。',70,585,1130,55,26);

s=base('四幕分镜：从换身，到质疑确认的劳动','全部画面、人物、时间与对话为设计虚构；第 4 幕为本人同意求助的示例结局。','四幕用作2分30秒叙述草稿，而不是已经制作的视频。01换底盘完成基础校准；02熟悉门口暂停；03观众选择并反馈；04再次出行先问，选择协助的示例中工作人员固定门扇。第4幕不代表所有分支都会发生。沿用上一版内置ImageGen图像，本次未生成新画面，完整提示词随包保存。');
await img(s,path.join(assets,'storyboard.png'),60,186,760,456,'contain','四幕AI分镜，设计虚构');
const beats=[['01  换身','00:00–00:30','旧记录与当前感知出现冲突。'],['02  停下','00:30–01:00','还剩 6 分钟，活动即将开始。'],['03  选择','01:00–01:50','行动、留档与规则都可被质疑。'],['04  修正','01:50–02:30','规则与记录分别改变下一次。']];
beats.forEach((b,i)=>{let y=183+i*117;text(s,b[0],861,y,360,37,25,true,C.green);text(s,b[1],861,y+38,360,28,18,false,C.gray);text(s,b[2],861,y+68,360,44,21);});

s=base('物理结果相同，沟通代价仍然不同','所有时间是叙事设定；两种提问规则共用本表，不当作性能数据。','起点均为开场前6分钟。复核3分钟，通过1，绕行10，协助9，维修复核19。先复核失败再绕行13分钟、迟到7；规则A与B相同。主动询问与主动打开次数来自网页事件，但也不是用户研究。记录复用的后续演示与同条件对照分开。');
table(s,[['共同路径','剧情耗时','没有被时间概括的代价'],['复核仍不足，再绕行','3 + 10 = 13 分钟','本人已解释，仍需额外路程'],['复核可确认，本人继续','3 + 1 = 4 分钟','本人操作；一次确认不是永久授权'],['直接求助 / 等维修方','9 / 19 分钟','他人的劳动、等待与开口求助'],['暂时不处理 / 取消','等待 2 分钟 / 不进入活动','注意力得到保留，也可能失去参与'],['“每次主动问” / “由我发起”','同条件同动作耗时相同','对话打断 / 主动寻找入口']], [350,300,510],60,180,1160,418,23);
text(s,'拒绝用一个“修养分”抵消时间、注意力、隐私和他人的劳动。',65,614,1150,36,25,true,C.green);

s=base('修养不仅是会问，也要允许少问与不留档','可观察要求｜作为设计假设，不宣称机器人已经具备伦理理解。','承认局限、尊重拒绝、限定记录、接受制度异议。UI真实实现规则切换和记录复用/失效，物理状态仍是脚本。平台反馈显示已记录未处理，不伪装实施。');
const rules=[['说明局限','说明本次局部证据冲突；重复点击不能使遮挡变成可通行。'],['尊重拒绝','允许暂不处理、取消、拒绝共享与留档；不标记为“不配合”。'],['限定记忆','偏好与现场记录分别授权；身体或门口变化使旧记录不能放行。'],['承认权限边界','制度异议保留待处理状态；不以礼貌回复代替平台履责。']];
rules.forEach((r,i)=>{let y=193+i*111;text(s,String(i+1).padStart(2,'0'),62,y,75,58,39,true,C.green);text(s,r[0],161,y,263,48,28,true);text(s,r[1],444,y,768,80,25);if(i<3)line(s,162,y+89,1052);});

s=base('现场演示：体验以后再判断','原入口已更新为 v1.1；双击“交互原型v1 / index.html”，无需网络。','先保持默认遮挡条件走一轮，体验另一个规则也用同样条件，比较不同开口方式。第二轮可重新设定clear演示保存记录/换身失效；不要把这两组当作同条件性能比较。截图是实际本地页面。');
await img(s,path.join(tmp,'web-setup.png'),60,179,760,457,'contain','修订后真实界面：对照前锁定环境，两条规则同级');
chunk(s,'先锁定条件','同组环境与记录状态固定。\n复核结果不能在途中改选。',850,205,365);
chunk(s,'再比较经历','相同结果可能带来不同感受。\n邀请同学说出偏好与相反理由。',850,386,365);
text(s,'Esc 原位暂停与恢复。\n到“反思与修订”查看自我批评。',850,571,365,68,21,false,C.gray);

s=base('反馈改变步骤，也暴露记忆的代价','两份授权：提问偏好与现场核验记录，分别决定下一次发生什么。','网页实装：保存rule改变下一次由谁发起；保存proof在当前身体和门口条件一致时可减少一次核验。换底盘或门口变化则不复用。用户可只存偏好、只存现场记录、分别撤回或不存。无真实持久数据库，无训练模型。');
chunk(s,'保存提问偏好','下一次从“轮椅主动问”，\n变为“安静停止，等待本人发起”。',65,184,535);
chunk(s,'保存现场记录','身体与门口当前条件一致：\n减少一次核验，仍由本人确认继续。',683,184,535);
chunk(s,'不保存或撤回','下次重新选择方式或现场核验。\n保护档案边界，也可能多一次操作。',65,374,535);
chunk(s,'再次换身 / 门口变化','旧记录无法继续放行。\n沟通偏好可以保留，能力依据需更新。',683,374,535);
text(s,'少一点重复证明，是否值得留下地点经验？这个取舍由使用者决定。',65,597,1145,50,27,true,C.green);

s=base('研究转译：哪些来自案例，哪些由我设定','保留四项来源；本轮没有新增检索，也不重写作业一 PRISMA 数量。','真实案例见末页来源和4–5页。新情境、提问制度、全部耗时、地点记录与预检提案都属于设计虚构。实际实现范围是有限状态网页；没有真实学习、感知、运动或平台申诉服务。');
table(s,[['层次','本项目内容','边界'],['真实来源','覆盖、共享控制、错误拒绝、\n高层行为纠正','局部功能，不证明伦理意识'],['我的解释','确认也需要劳动；不回应与\n接受帮助都不等于失去自主','保留相反解释，仍有设计者预设'],['设计虚构','林岚、局部冲突、提问制度、\n所有时间、地点记录与预检提案','不是产品已有能力或真实事件'],['实际实现','锁定对照、分支、分别授权、\n复用 / 失效、异议记录、撤回','真实物理判断与服务通知未接入；\n制度异议不会自动落实']], [230,545,385],60,180,1160,414,23);
text(s,'平台异议停在“已记录，未处理”，让权限边界和未完成的责任保持可见。',65,614,1150,38,24,false,C.green);

s=base('自我批评：上一版把答案放进了按钮','依据课件页 22–24、45、49、51–53、58–59、61–62；这是制作自查，非课堂反馈。','原版有四个核心缺陷：B默认且更有利、用户自行选择成功、改措辞但流程变化少、平台责任只是旁白。本次修改后仍有局限：单一角色、点击代替身体体验、脚本预定后果、没有真实平台申诉和目标群体研究。课堂应观察误解与分歧而非给机器人打分。');
chunk(s,'把 B 写成了优选答案','修订：同级规则、相同行动与耗时。\n不预选，不用成功奖励“配合”。',65,184,535);
chunk(s,'由观众挑选感知是否正确','修订：出行前锁定环境。\n同条件的物理结果对两条规则一致。',683,184,535);
chunk(s,'反馈主要是更换措辞','修订：实际改变发问与核验步骤。\n让留档、拒绝与撤回都有后果。',65,379,535);
chunk(s,'责任只在说明文字里','修订：允许质疑规则、记录异议。\n待处理状态保留，不能假装已解决。',683,379,535);
text(s,'仍待课堂检验：什么样的“少问”让人轻松，什么样的“少问”又让人被遗弃？',65,605,1150,45,25,true,C.green);

s=base('制作与课堂展示说明','附录｜v1.1：说明 PPT + 修订分镜脚本 + 可点击原型；旧版完整包保留。','Codex参与自查、内容、网页逻辑与PPT更新。沿用2026-09-18内置ImageGen生成的图片，本轮未生成新图像或视频。未开展正式用户研究。独立读取范围与学术来源保持原记录。');
chunk(s,'这次由什么推动修改','课件走查 + 原型自查 + 实际点击检查。\n没有把这些检查冒写成真实参与者反馈。',65,182,1140);
chunk(s,'AI 与实现范围','Codex：结构、反思、脚本与代码；图像沿用上一版 ImageGen。\n无动态视频、实体机器人、学习模型或平台通知接入。',65,352,1140);
text(s,'约 5 分钟展示',65,524,1120,44,28,true,C.green);
text(s,'命题与不足 1 分钟 → 来源与规则 1 分钟 → 同学体验 2 分钟 → 分歧与边界 1 分钟',65,586,1150,58,24);

s=base('核心来源与定位','附录｜与作业一数据库 ID 对应；完整说明与提示词随提交包提供。','课程材料：付志勇《思辨设计-Week1-案例RTD》，用户提供PDF，页20–24、46、49、52–53、58–59。以下4个来源在2026-09-18核对。Assignment1库是探索性检索与目的选例，不声称完整系统综述。此轮4项是设计关联选例，不重新计算PRISMA流程。');
const refs=[['W07 / RC261 · LUCI User Guide, Rev F','印刷页 16、18、22–23：覆盖、隐私与设置。','https://www.luci.com/hubfs/Luci_April2026/pdf/613-00003_F_LUCI-User-Guide_Color-1.pdf'],['W01 / RC262 · Xu et al., CoNav Chair (2025)','摘要、§III-D、§IV-C、图 2、图 7。','https://arxiv.org/abs/2507.11716'],['W06 / RC008 · Park et al., CLARA (2024)','项目页方法与 Failure Cases。','https://clararobot.github.io/'],['W11 / RC106 · Bärmann et al. (2024), ARMAR-6','Incremental learning of humanoid robot behavior …','https://www.frontiersin.org/journals/robotics-and-ai/articles/10.3389/frobt.2024.1455375/full']];
refs.forEach((r,i)=>{let y=175+i*109;text(s,r[0],64,y,1150,34,24,true);text(s,r[1],64,y+37,1150,31,20,false,C.gray);let link=text(s,r[2],64,y+70,1150,27,16,false,C.green);link.text.get(r[2]).link={uri:r[2],isExternal:true};});
text(s,'方法参考：课程 RTD PDF 页 20–24、46、49、52–53、58–59。',64,622,1150,33,21,false,C.gray);

await fs.mkdir(path.join(tmp,'slides'),{recursive:true});
const candidate=path.join(tmp,'candidate.pptx');
await (await PresentationFile.exportPptx(P)).save(candidate);
console.log('EXPORTED',slides.length);
const finalPath=path.join(output,'说明PPT_这一次轮椅该听谁的_v1.1_修订.pptx');
await finalizePresentation({workspaceDir,candidatePath:candidate,finalPath,pythonExecutable:runtimePython,integrityValidatorPath:path.join(SKILL_DIR,'container_tools/inspect_presentation_package_integrity.py'),layoutValidatorPath:path.join(SKILL_DIR,'container_tools/inspect_presentation_layout_geometry.py'),layoutArgs:['--expected-slide-size-emu','12192000,6858000','--validate-bullet-geometry','--validate-heading-fit',...[3,6,9,13].flatMap(n=>['--require-native-table-slide',String(n)])],requiredNativeTableOwnerSlides:[3,6,9,13],fontPolicy:{basis:'design',families:[FONT]},verifyArtifactToolImport:true,receiptPath:path.join(tmp,'deck-validation-v11-final.json')});
console.log('FINALIZED');
for(let i=0;i<slides.length;i++){const blob=await P.export({slide:slides[i],format:'png',scale:1.25});await fs.writeFile(path.join(tmp,'slides',`${String(i+1).padStart(2,'0')}.png`),new Uint8Array(await blob.arrayBuffer()));console.log('RENDERED',i+1);}
await fs.writeFile(path.join(tmp,'deck-text.json'),JSON.stringify(await P.inspect({kind:'slide,textbox,table,notes',maxChars:100000}),null,2));
