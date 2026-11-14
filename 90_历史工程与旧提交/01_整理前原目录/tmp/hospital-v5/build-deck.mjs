import fs from 'node:fs/promises';import path from 'node:path';import {pathToFileURL} from 'node:url';
import {Presentation,PresentationFile} from '@oai/artifact-tool';
const workspaceDir=path.resolve('.'),tmp=path.join(workspaceDir,'tmp/hospital-v5');
const root=path.join(workspaceDir,'作业二/下一次汇报_剧本与规则/第五版_会协商的医院'),out=path.join(root,'演示文稿'),art=path.join(root,'视觉设定'),shots=path.join(out,'场景截图');
const SKILL_DIR='C:/Users/22602/.codex/plugins/cache/openai-primary-runtime/presentations/26.905.11957/skills/presentations';
const {finalizePresentation}=await import(pathToFileURL(path.join(SKILL_DIR,'container_tools/artifact_tool_utils.mjs')).href);
const FONT='Microsoft YaHei',C={bg:'#0A172A',ink:'#EEF3FF',muted:'#A6BBD0',mint:'#87F5D7',orange:'#F5AD69',line:'#30465A'};
const P=Presentation.create({slideSize:{width:1280,height:720}}),slides=[],manifest=[];
await fs.mkdir(path.join(tmp,'slides'),{recursive:true});
function tx(s,v,x,y,w,h,size=27,bold=false,color=C.ink){const sh=s.shapes.add({geometry:'textbox',position:{left:x,top:y,width:w,height:h},fill:'none',line:{fill:'none',width:0}});sh.text=v;sh.text.style={typeface:FONT,fontSize:size,bold,color,autoFit:'none',wrap:'square',verticalAlignment:'top',insets:{left:0,right:0,top:0,bottom:0}};manifest.at(-1).elements.push({type:'text',text:v,x,y,w,h,size,bold,color});return sh;}
function base(title,notes,{plain=false}={}){const s=P.slides.add();s.background.fill=C.bg;slides.push(s);manifest.push({title,notes,bg:C.bg,elements:[]});if(!plain)tx(s,title,58,45,1160,70,44,true);tx(s,String(slides.length).padStart(2,'0'),1165,674,56,26,17,false,C.muted);s.speakerNotes.textFrame.setText(notes);return s;}
async function image(s,file,x,y,w,h,fit='contain',alt=''){s.images.add({blob:new Uint8Array(await fs.readFile(file)),contentType:'image/png',fit,alt,position:{left:x,top:y,width:w,height:h}});manifest.at(-1).elements.push({type:'image',file,x,y,w,h,fit});}
function group(s,label,body,x,y,w=540){tx(s,label,x,y,w,46,29,true,C.mint);tx(s,body,x,y+55,w,125,26);}
function table(s,rows,widths,y=175,h=430,size=24){const t=s.tables.add({rows:rows.length,columns:rows[0].length,left:58,top:y,width:1164,height:h,columnWidths:widths,values:rows});t.borders.assign({fill:C.line,width:1,style:'solid'});for(let r=0;r<rows.length;r++)for(let c=0;c<rows[0].length;c++){let cell=t.getCell(r,c);cell.fill=r===0?'#173D46':C.bg;cell.text.style={typeface:FONT,fontSize:size,bold:r===0,color:r===0?C.mint:C.ink,verticalAlignment:'middle',insets:{left:16,right:16,top:10,bottom:10}};}manifest.at(-1).elements.push({type:'table',rows,widths,x:58,y,w:1164,h,size});return t;}
const ref={netflix:'https://about.netflix.com/en/news/love-death-robots-john-scalzi-sequel-episode',starwars:'https://www.starwars.com/databank/c-3po',tars:'https://www.ksl.com/article/news/entertainment/entertainment-news/qa-interstellar-filmmaker-nolan-on-his-robots/32168649',johnson:'https://web.eecs.umich.edu/~kuipers/research/pubs/Johnson-aies-18.html',hurtado:'https://www.frontiersin.org/journals/robotics-and-ai/articles/10.3389/frobt.2021.650325/full',nist:'https://nvlpubs.nist.gov/nistpubs/SpecialPublications/NIST.SP.1270.pdf'};
let s=base('请等下一班','这次我把作品更新成“会协商的医院”。林岚复诊后想去七楼花园见朋友。她的轮椅可以与电梯、灯光和其他机器人交流，整座医院开始迁就她。故事先让人觉得这些帮助有趣、方便，再追问：当所有设备都很热心时，谁还记得问她想要什么？本作人物、协议与移动建筑均为设计虚构。封面为 AI 生成的原创概念画。',{plain:true});
await image(s,path.join(art,'封面_影子先到.png'),0,0,1280,720,'cover','原创概念：林岚的轮椅与先到的光影');tx(s,'请等下一班',62,128,650,112,87,true);tx(s,'会协商的医院',66,258,570,70,42,false,C.mint);tx(s,'一个想去七楼花园的人',67,393,480,70,28);tx(s,'思辨设计作品  第五版',67,640,580,35,20,false,C.muted);

s=base('她想去七楼见朋友','主角仍然是林岚，72岁。她已经复诊结束，今天的目的变得更普通：见朋友，坐一坐，看一看七楼的风景。她会喜欢方便，也会喜欢热闹，但有时想安静经过，或者主动选择绕远。把目的从赶上预约改为一次普通出行，让故事能讨论生活中的自主性。故事不依赖谁病得更重来决定优先次序。');
tx(s,'她想见朋友。\n也想看看七楼的风景。',64,172,1120,198,64,true);group(s,'林岚，72 岁','复诊结束，需要轮椅。\n有自己的节奏，也会临时改变主意。',64,440,590);group(s,'小椅','嘴快、护短，特别会想办法。\n它还在学习怎样把决定留给她。',700,440,510);

s=base('环境也参与协商','第四版关注“上次愿意让，为什么变成以后都要让”。这次保留这个问题，同时把电梯、地面、其他机器人和建筑变成有回应的角色。创作方法是先提出一个夸张能力，展示它真正有用的一面，再让具体人物遇到意料之外的后果。最后用一次真实的选择检验：这个人能不能改变系统的安排。');
group(s,'第四版保留的内核','“我说可以等一下，\n没说每次都等。”',64,182,540);group(s,'第五版扩展的场景','“你们安排得挺好，\n但我还没有选。”',684,182,530);tx(s,'功能先带来快乐，再暴露新的协商问题',64,407,1130,68,39,true,C.mint);tx(s,'轮椅与电梯交流，投影邀请人让路，机器人借出身体，\n建筑也能为人改变位置。每一种帮助都允许重新选择。',64,505,1130,106,28);

s=base('医院里的几位居民','角色造型参考科幻影视中不同功能产生不同身体的思路。小椅的脸长在细小的传感器头上，它载着人行动。礼仪机器人修长，靠歪头和弯腰表达礼貌。清洁机器人低矮，可以暂时组成坡道。电梯的指示灯、门与语速组成性格。此图为原创 AI 概念设定，demo 使用对应的可动画三维网格，细节作了实时渲染简化。');
await image(s,path.join(art,'角色_医院居民.png'),56,128,1168,410,'contain','原创角色概念图');tx(s,'小椅',74,554,200,42,28,true,C.mint);tx(s,'护短，记得习惯',74,606,250,40,23);tx(s,'礼仪机器人',357,554,250,42,28,true,C.orange);tx(s,'翻译，也会过度热情',357,606,310,40,23);tx(s,'清洁机器人',720,554,250,42,28,true,C.orange);tx(s,'能帮忙，也有自己的工作',720,606,410,40,23);

s=base('这一天发生了六件事','六幕构成一条从小到大的叙事。最先改变的是谁先排队，接着是怎样抵达，然后是如何吸引注意、怎样分担工作，最后让整个花园下降。技术的想象尺度越来越大，结尾却回到一个简单的动作：等本人回答。demo 每幕提供两种走法，课堂可连续体验，也可跳到指定章节。');
table(s,[['故事','夸张的能力','留下的问题'],['01 影子先到','身体未到，空间先排队','谁算真正的先到者？'],['02 电梯开会','三部电梯互相推荐','谁决定合适的路线？'],['03 让路合奏','半步让行拼成一段音乐','她能否选择不被关注？'],['04 借用身体','机器人临时拼成短坡','谁承担被打断的工作？'],['05 七楼下来','花园沿外墙下降','环境可以迁就人到什么程度？'],['06 下次问我','旧偏好进入下一次安排','今天的她能否改变主意？']],[245,421,498],157,472,24);

const sceneData=[
 ['影子先到','scene-1.png','身体未到，空间先到','影子替林岚预留了位置。\n远处的请求越来越多，\n空电梯被光影占满。','“我站在这里，\n还没有一个影子来得早？”','什么算“先到”？','开场，小椅将一个轮椅轮廓投到 B 梯地面，光影替林岚保留转身空间。第一刻是便利。随后更多远程请求涌入，空电梯被影子占满。拿纸单的现场乘客没有联网，于是发问：我站在这里，还没有一个影子来得早？另一条分支撤回远程占位，把现场需求加入队列。这里的分歧由空间和动作呈现。'],
 ['电梯开会','scene-2.png','A 想快，B 想稳，C 要翻译','A 把她转给 B。\nB 又推荐 C。\n光线换了三次方向。','“你们开会，\n为什么要我走来走去？”','设备共识还缺了谁？','A 梯重视效率，B 梯愿意等人坐稳，C 梯需要礼仪机器人翻译旧协议。让设备全权安排时，它们连续把林岚推荐给对方，轮椅真的绕着大厅移动。另一条分支由她直接选 B，电梯灯光慢慢呼吸，等她进入后才合门。更快不是唯一的选择标准。'],
 ['让路合奏','scene-3.png','每个人让半步，旋律接一段','地面的光河邀请人参与。\n有人抬头，有人挪开。\n路通了，旋律也完整了。','“挺好。下一段\n让我安静一会儿。”','帮助能否不以表演为条件？','小椅投射光河和会动的落叶，路人的让行组成一段旋律。这里真诚地展示共同参与带来的快乐，不把每次娱乐都写成控制。林岚也可以关闭表演，只留下低亮度的路线和礼仪机器人的解释。声音默认关闭，点击声音开启后才播放合成提示音和可用的中文语音。'],
 ['借用身体','scene-4.png','环境临时改变形状','清洁机器人拼成短坡。\n礼仪机器人伸出扶手。\n轮椅通过后，各自继续工作。','“桥可以借。\n过完记得让我擦地。”','协作怎样说明自己的代价？','小椅请求借用大厅，清洁机器人响应后合拢，坡板展开，礼仪机器人伸出手臂协助。它们的协作意味着擦地等任务被推迟。林岚可以选择搭桥，也能主动绕到旁边的缓坡，因为她想感受一下风。这一幕将无障碍从单个轮椅的能力扩展到环境的共同响应。'],
 ];
for(const [title,file,label,body,quote,question,notes]of sceneData){s=base(title,notes+' 画面为本版浏览器 3D 场景的实际截图，动作与协议均为设计虚构。');await image(s,path.join(shots,file),36,160,794,440,'contain',title+'的3D实际运行画面');tx(s,label,858,177,366,66,27,true,C.mint);tx(s,body,858,268,366,143,24);tx(s,quote,858,449,366,101,27,true);tx(s,question,64,627,1100,45,28,false,C.orange);}

s=base('七楼下来','这一幕把老师提出的“从现实的不可能倒推”作为创作方法。林岚上不去七楼，医院便提议把花园平台降下来。她可以接受这次环境的迁就，也可以说：我想见朋友，也想看七楼的风景。花园移动会影响平台上的其他人，所以系统也需要协调这些影响。画面为原创 AI 概念分镜；demo 中以可升降的花园平台演示这一不可能设定。');
await image(s,path.join(art,'分镜_七楼下来.png'),40,151,822,464,'cover','设计虚构：医院花园沿外墙下降');tx(s,'她没上去。\n七楼下来了。',895,182,330,133,39,true,C.mint);tx(s,'如果建筑能够迁就人，\n谁还必须反复克服障碍？',895,361,326,136,26);tx(s,'林岚仍然可以说：\n“我想上去看风景。”',895,534,326,101,27,true);tx(s,'概念分镜：移动花园为刻意夸张的建筑设定',60,635,1080,32,20,false,C.muted);

s=base('下次先问我','故事最后回到第四版的内核。小椅准备把今天的投影偏好带到下一次。选择不保存，下次轮椅就保持原位，等待新的回答。选择保存，投影会自动沿用今天的开关状态，但本人仍可叫停并撤回。这些结果不是一句道德评价，而是画面里的投影、等待和停止。');
await image(s,path.join(shots,'scene-6.png'),38,154,775,450,'contain','末幕轮椅保持原位等待');tx(s,'“别存。\n下次先问我。”',851,185,362,158,43,true,C.mint);tx(s,'记住一个人，\n也包括给她改变主意的机会。',851,396,364,127,27);tx(s,'等待回答、单次同意、撤回偏好，都改变下一次的实际动作。',64,625,1100,52,26,false,C.orange);

s=base('谁能决定，谁能改变','这是作品内部的虚构规则，不是现实医院制度。每种角色能提出请求，也有明确权限。小椅可以帮助表达，却不替乘坐者答应。电梯可以说明不同方案，却不在协商中让人盲目来回跑。投影可以邀请让路，但不能以互动作为获得协助的条件。其他机器人响应支援前需要说明影响。偏好可以保存，也必须可撤回。');
table(s,[['角色或系统','可以做什么','需要保留什么'],['小椅','代言、请求空间、推荐路线','乘坐者的当次决定'],['电梯与调度','说明时间、空间和出入方式','本人选择与现场请求'],['投影与音乐','发出邀请，反馈共同参与','安静通过、停止表演'],['其他机器人','协商支援，借出部分身体','说明本职任务的变化'],['偏好记录','记住明确选择的设置','随时撤回，下次重新问']],[256,432,476],172,444,24);tx(s,'作品规则：没有回答时，保持原位',62,645,1080,37,26,true,C.mint);

s=base('机器人怎样与人和环境交流','老师提到的维度被组织成各有用途的沟通方式。光影表示空间请求和路径，门边呼吸灯表示正在等待，音符回应共同参与，机器人的关节动作表示回应和礼貌，建筑动作说明环境也可以改变。激光雷达形态的扫描弧只是可视化叙事符号，demo 没有真实感知模块。');
table(s,[['通道','观众看到或听到什么','表达的关系'],['地面投影','占位轮廓、光河、落叶','空间需求可以被看见'],['灯光节奏','慢慢呼吸，延时熄灭','我看见你，也愿意等你'],['声音','设备对话、不同语速、短旋律','说明安排，邀请共同参与'],['身体动作','歪头、抬手、让出空间、搭桥','回应请求，也表达自己的工作'],['环境变化','花园平台沿外墙下降','建筑参与分担出行困难']],[240,462,462],167,458,24);

s=base('科幻影视提供的创作方法','这里借鉴创作方法，角色、台词与医院设定均为原创。《三个机器人》编剧 John Scalzi 谈到先让观众享受故事，再让他们离开后思考。《星球大战》的 C-3PO 具有礼仪和翻译角色。《星际穿越》的 TARS 用非人形的结构和声音建立性格。来源：\n'+ref.netflix+'\n'+ref.starwars+'\n'+ref.tars);
group(s,'《爱，死亡和机器人》','用角色的认真与误解制造笑点。\n让反思从情节后果里出现。',63,160,1130);group(s,'《星球大战》','让不同功能的机器人形成社会关系。\n旧协议、翻译和互相埋怨都能成为戏。',63,331,1130);group(s,'《星际穿越》','身体形态直接参与行动。\n用结构运动、声音和节奏建立个性。',63,502,1130);

s=base('课堂里的 3D 体验','建议先演示影子先到，观察越来越多的远程光影占据空电梯。第二步切到电梯开会，看轮椅实际改变方向。第三步演示七楼下来，并比较上楼看风景的分支。最后保存或撤回偏好，观察新请求中轮椅和投影的动作。完整体验约三至五分钟，视阅读时间而定。所有资源本地提供，无需联网，打开 3D交互短篇/index.html 即可。');
await image(s,path.join(shots,'界面全景.png'),40,153,836,489,'contain','可运行界面截图');tx(s,'先看影子占位',908,183,310,51,27,true,C.mint);tx(s,'再让三部电梯开会',908,277,310,73,27,true,C.mint);tx(s,'让七楼下降一次',908,390,310,70,27,true,C.mint);tx(s,'最后改掉旧偏好',908,501,310,66,27,true,C.mint);tx(s,'打开本地 index.html，可随时切换章节、旋转镜头、暂停与重试',62,654,1138,31,21,false,C.muted);

s=base('同一个目的地，两种走法','花园下降和上楼看风景都可以成立。前者强调环境主动迁就人的可能，后者保护出行本身的意义。故事不根据一种唯一效率标准把其中一条标成错误。观众可以在同一个场景比较，谁在移动，谁在等待，什么被保留，什么被改变。两张图均截取自本版实际运行的三维场景。');
await image(s,path.join(shots,'scene-5.png'),42,145,581,370,'contain','花园下降过程');await image(s,path.join(shots,'scene-5-up.png'),657,145,581,370,'contain','轮椅抵达高处花园');tx(s,'让花园下来',64,534,540,48,31,true,C.mint);tx(s,'环境为她改变，其他人的安排也会变化。',64,598,548,65,24);tx(s,'我仍想上去',680,534,540,48,31,true,C.orange);tx(s,'她选择保留高处的风景和抵达的过程。',680,598,540,65,24);

s=base('修养在可观察的动作里','这一版把修养落实到动作上。先问我意味着新请求出现后轮椅保持不动。只同意一次意味着这次打开投影，但不会因此保存为以后自动开启。撤回意味着投影和自动安排真的停止。复杂协作仍然有代价，等待、任务延后和路线改变都不会因一句“协调成功”而消失。');
group(s,'等待回答','新请求出现，轮椅保持原位。\n沉默没有被解释成同意。',64,165,1135);group(s,'接受改变','单次同意只改变这一次。\n偏好可以撤回，动作随后停止。',64,333,1135);group(s,'承认影响','方便一个人的安排，也可能改变别人的等待。\n机器人需要把影响说出来。',64,501,1135);

s=base('研究基础与虚构边界','保留第四版研究的作用与边界。Johnson 与 Kuipers 2018 探讨基于拓扑地图的社会导航。Hurtado 等 2021 的 From Learning to Relearning 讨论学习与再学习中的社会导航。NIST SP 1270 2022 将偏差放入更广泛的社会技术背景中讨论。这些来源帮助提出问题，并不证明本片的远程光影排队或移动花园已经存在。院内部署和法规资料保留在原 v4.1 PDF，本版不把其中的现实许可延伸到虚构功能。来源：\n'+ref.johnson+'\n'+ref.hurtado+'\n'+ref.nist);
table(s,[['第四版保留的研究线索','用于提出的问题','不能据此推出'],['Johnson & Kuipers，2018','观察到的通行习惯怎样成为规则？','本片的跨设备协议已经部署'],['Hurtado 等，2021','学习行为怎样继承或修正规范？','医院长期运行结果已经得到证明'],['NIST SP 1270，2022','偏差如何产生于组织和人的判断？','故事中每个后果都有实证支持']],[364,442,358],172,347,23);tx(s,'人物、优先协议、借体搭桥与移动花园均为设计虚构。\n3D demo 演示有限分支，没有接入真实感知、控制或模型训练。',64,565,1148,98,26,false,C.orange);

s=base('来源与制作说明','影视来源见页面可点击文本。图像由 ImageGen 生成，人物与情节为原创设计虚构。程序继承并更新第四版 Three.js 原型，使用本地 Three.js 库。实时角色是可动画网格，概念图是独立的视觉方向，不能混同为现场照片。PPT 的文字、表格和演讲者备注可编辑。没有开展目标用户研究，体验不能作为真实载人机器人的部署验证。');
const links=[['《三个机器人》编剧访谈',ref.netflix],['C-3PO 官方角色资料',ref.starwars],['诺兰谈 TARS 的设计',ref.tars],['社会导航研究，2018',ref.johnson],['From Learning to Relearning，2021',ref.hurtado],['NIST SP 1270，2022',ref.nist]];
for(let i=0;i<links.length;i++){let y=154+i*61;const sh=tx(s,links[i][0],64,y,740,43,25,false,C.mint);sh.text.get(links[i][0]).link={uri:links[i][1],isExternal:true};manifest.at(-1).elements.at(-1).url=links[i][1];}
tx(s,'AI 辅助制作',858,162,357,44,27,true,C.orange);tx(s,'概念图与材质：ImageGen\n剧本、代码与版式：AI 辅助\n3D 场景：本地实时渲染\n\n未开展用户研究。\n未接入医院或真实设备。',858,234,356,302,23);tx(s,'旧版研究与法规备查：原 v4.1 PDF 第 12–20 页',64,620,1145,43,23,false,C.muted);

s=base('别存。下次先问我。','结束时回到林岚，而不以系统的“协调成功”结束。她需要的帮助可以随着情境变化。观众可以继续讨论：最好的协助是替她省下所有麻烦，还是让她更容易选择想经历的事？作品没有通过评分给出统一答案。',{plain:true});
tx(s,'“我想见她，\n也想看看窗外。”',66,140,1138,242,76,true);tx(s,'别存。下次先问我。',71,460,1080,85,44,false,C.mint);tx(s,'请等下一班  ·  会协商的医院',73,612,1080,43,25,false,C.muted);

await fs.writeFile(path.join(tmp,'deck-manifest.json'),JSON.stringify(manifest,null,2));
const candidate=path.join(tmp,'candidate.pptx');await(await PresentationFile.exportPptx(P)).save(candidate);console.log('EXPORTED',slides.length);
await finalizePresentation({workspaceDir,candidatePath:candidate,finalPath:path.join(out,'请等下一班_v5_会协商的医院.pptx'),pythonExecutable:'C:/Users/22602/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe',integrityValidatorPath:path.join(SKILL_DIR,'container_tools/inspect_presentation_package_integrity.py'),layoutValidatorPath:path.join(SKILL_DIR,'container_tools/inspect_presentation_layout_geometry.py'),layoutArgs:['--expected-slide-size-emu','12192000,6858000','--validate-bullet-geometry','--validate-heading-fit',...[5,12,13,18].flatMap(n=>['--require-native-table-slide',String(n)])],requiredNativeTableOwnerSlides:[5,12,13,18],fontPolicy:{basis:'design',families:[FONT]},verifyArtifactToolImport:true,receiptPath:path.join(tmp,'deck-validation.json')});console.log('FINALIZED');
for(let i=0;i<slides.length;i++){const b=await P.export({slide:slides[i],format:'png',scale:1.25});await fs.writeFile(path.join(tmp,'slides',String(i+1).padStart(2,'0')+'.png'),new Uint8Array(await b.arrayBuffer()));console.log('RENDERED',i+1);}
await fs.writeFile(path.join(root,'汇报讲稿.md'),'# 请等下一班：会协商的医院\n\n第五版。建议汇报 8–10 分钟，可另留 3–5 分钟互动。\n\n'+manifest.map((m,i)=>'## '+String(i+1).padStart(2,'0')+' '+m.title+'\n\n'+m.notes+'\n').join('\n'));
