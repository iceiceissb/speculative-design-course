import fs from 'node:fs/promises';import path from 'node:path';import {pathToFileURL} from 'node:url';
import {Presentation,PresentationFile} from '@oai/artifact-tool';
const workspaceDir=path.resolve('.'),tmp=path.join(workspaceDir,'tmp/yield-project'),out=path.join(workspaceDir,'作业二/提交_请别替我让路'),assets=path.join(out,'3D交互原型/assets');
const SKILL_DIR='C:/Users/22602/.codex/plugins/cache/openai-primary-runtime/presentations/26.905.11957/skills/presentations';
const {finalizePresentation}=await import(pathToFileURL(path.join(SKILL_DIR,'container_tools/artifact_tool_utils.mjs')));
const FONT='Microsoft YaHei',C={bg:'#F7F6F2',ink:'#243431',teal:'#316659',rust:'#A66545',muted:'#66716D',line:'#CFD4CB'};
const P=Presentation.create({slideSize:{width:1280,height:720}}),slides=[],transcript=[];
function text(s,v,x,y,w,h,size=26,bold=false,color=C.ink){const sh=s.shapes.add({geometry:'textbox',position:{left:x,top:y,width:w,height:h},fill:'none',line:{fill:'none',width:0}});sh.text=v;sh.text.style={typeface:FONT,fontSize:size,bold,color,autoFit:'none',wrap:'square',verticalAlignment:'top',insets:{top:0,right:0,bottom:0,left:0}};return sh;}
function base(title,subtitle,notes){let s=P.slides.add();s.background.fill=C.bg;slides.push(s);text(s,title,60,43,1160,65,42,true);if(subtitle)text(s,subtitle,62,117,1156,44,21,false,C.muted);text(s,'请别替我让路',62,674,1050,24,15,false,C.muted);text(s,String(slides.length).padStart(2,'0'),1160,672,60,28,17,false,C.muted);s.speakerNotes.textFrame.setText(notes);transcript.push({page:slides.length,title,notes});return s;}
async function img(s,file,x,y,w,h,fit='contain',alt=''){let ext=path.extname(file).toLowerCase();s.images.add({blob:new Uint8Array(await fs.readFile(file)),contentType:ext==='.jpg'||ext==='.jpeg'?'image/jpeg':ext==='.webp'?'image/webp':'image/png',fit,alt,position:{left:x,top:y,width:w,height:h}})}
function pair(s,label,body,x,y,w=530,color=C.teal){text(s,label,x,y,w,45,28,true,color);text(s,body,x,y+52,w,120,26);}
function table(s,rows,widths,y=181,h=420,size=23){let t=s.tables.add({rows:rows.length,columns:rows[0].length,left:60,top:y,width:1160,height:h,columnWidths:widths,values:rows});t.borders.assign({fill:C.line,width:1,style:'solid'});for(let r=0;r<rows.length;r++)for(let c=0;c<rows[0].length;c++){let cell=t.getCell(r,c);cell.fill=r===0?C.teal:r%2?C.bg:'#E9EDE5';cell.text.style={typeface:FONT,fontSize:size,bold:r===0,color:r===0?'#FFFFFF':C.ink,verticalAlignment:'middle',insets:{left:12,right:12,top:9,bottom:9}}}return t;}
const refs=[
 {id:'RC237',name:'走廊相遇实验',type:'Fiore 等，2013 / 实验论文',image:'proxemics.png',url:'https://www.frontiersin.org/journals/psychology/articles/10.3389/fpsyg.2013.00859/full',imageURL:'https://www.frontiersin.org/files/Articles/57423/xml-images/fpsyg-04-00859-g002.webp'},
 {id:'RC252',name:'DAWN / OriHime',type:'真实运营项目与官方人物故事',image:'dawn.jpg',url:'https://dawn2021.orylab.com/en/',imageURL:'https://dawn2021.orylab.com/assets/images/common/c-area-pic.jpg'},
 {id:'RC045',name:'Uninvited Guests',type:'Superflux，2015 / 虚构短片',image:'guests.jpg',url:'https://superflux.in/index.php/work/uninvited-guests/',imageURL:'https://superflux.in/wp-content/uploads/2016/11/guests.jpg'},
 {id:'W07 / RC261',name:'LUCI',type:'官方产品使用指南，Rev F',image:'luci.png',url:'https://www.luci.com/hubfs/Luci_April2026/pdf/613-00003_F_LUCI-User-Guide_Color-1.pdf',imageURL:'LUCI 官方指南中的产品示意图'},
 {id:'W01 / RC262',name:'CoNav Chair',type:'Xu 等，2025 / 研究预印本',image:'conav.png',url:'https://arxiv.org/abs/2507.11716',imageURL:'CoNav Chair 论文中的系统图'},
 {id:'W08 / RC232',name:'HuggieBot 2.0',type:'Block 等，2021 / 研究论文',image:'huggiebot.jpeg',url:'https://arxiv.org/abs/2101.07679',imageURL:'论文首页机器人与参与者照片'}];
let s=base('','','开场：我的机器人身体就是一台轮椅。我想讨论一个很小的动作：让路。当公共机器人的礼貌规则要求它后退时，它也把坐在上面的人带着退了。谁有权决定这一步？画面来自实际运行的3D网页，人物、空间和规则均为设计虚构。');
text(s,'请别替我让路',62,150,615,95,62,true);text(s,'轮椅机器人的礼貌，\n应该由谁付出代价？',66,290,590,122,35,false,C.teal);text(s,'身体动作视角的思辨设计',66,494,570,44,25);text(s,'案例解读 · 四幕分镜 · 3D 交互原型 v1',66,552,580,40,20,false,C.muted);await img(s,path.join(assets,'cover-hero.png'),680,60,565,584,'contain','实际3D原型中的轮椅和行人，设计虚构');

s=base('主角、情境与思辨命题','首要服务对象：需要轮椅辅助移动、能够表达本人意愿的人。','林岚是虚构的72岁老人，腿脚不便，能表达选择，去社区上合唱课。也可以延伸到暂时腿伤、需轮椅辅助的人，但不能把失明等同于轮椅需求。视力与行动双重障碍需要进一步验证交互。核心反事实是：如果把公共机器人主动让人的规则直接移到载人的轮椅上，会怎样？机器人让出的空间，实际由乘坐者用身体移动来付出。本题以身体动作为唯一主分析角度，不同时铺开训练、文本等多个题目。');
text(s,'如果公共机器人“主动让人”的规则，\n被直接套用到载人的轮椅机器人上，\n会怎样？',62,191,1150,191,40,true);pair(s,'林岚，72 岁','需要移动辅助，想自己决定何时退让。\n她正去上合唱课，行人正去接家人。',64,433,610);text(s,'用户边界',770,433,420,43,28,true,C.teal);text(s,'不以年龄推断决策能力。\n失明本身不构成轮椅需求。\n本版尚未验证无障碍交互。',770,486,440,120,24);

s=base('案例一：身体动作会传达社会规则','RC237 / Fiore 等，2013。研究论文中的机器人与行人相遇实验。','事实：研究比较机器人凝视和空间行为；passive条件包括减速并移到一侧让行，assertive条件包括加速并切到人前方。部分社会临场感、情感评价在passive条件更积极。不能把局部量表结果概括成任何场合都应让人，也不能把它写成行人给机器人让出多少距离的研究。关键转译：原实验没有轮椅乘坐者，我把同类礼让规则移到载人的身体上，追问代价归属。原实验侧让，本作后退是设计改写。来源 '+refs[0].url+' 图片 '+refs[0].imageURL);
await img(s,path.join(assets,'proxemics.png'),66,186,470,390,'contain','Fiore论文图2中的iRobot Ava');pair(s,'原研究做了什么','比较机器人减速侧让、主动穿行等动作，\n观察人们怎样感知它。',588,187,626);pair(s,'我从中提出什么问题','当机器人身体上坐着一个人，\n“让人觉得有礼貌”还足够吗？',588,389,626);text(s,'边界：原研究没有轮椅乘坐者。“载人后退”是本设计的反事实改写。',65,602,1150,45,23,false,C.rust);

s=base('案例二：机器人动作背后，有一个人的生活','RC252 / DAWN 分身机器人咖啡馆。真实项目与官方人物故事。','官方项目介绍：外出受限的操作者可以从家里或医院远程参与咖啡馆工作。官网The birth of the Tele-Barista讲述曾任咖啡师的Mika参与项目，她与Sae及团队探索远程咖啡机器人。强调参与工作的意愿，不用病情制造同情。照片是项目机器人配图，不是Mika肖像。OriHime由真人远程操控，官网明确不是自主AI。与轮椅的技术关系不同，我只借此提醒：不能只看机器人怎样方便旁观者，还要看它承载谁的意愿。来源 '+refs[1].url+' 图片 '+refs[1].imageURL);
await img(s,path.join(assets,'dawn.jpg'),62,182,615,408,'cover','DAWN项目机器人，非Mika肖像');pair(s,'Mika 想继续参与工作','曾任咖啡师的她，\n参与了远程咖啡机器人项目。\n让外出受限的人也能参与服务。',722,186,490);pair(s,'对轮椅的启发','评价机器动作时，\n要看见它所承载的人的意愿。',722,392,490);text(s,'照片为项目配图。远程操作者的主体性，不等于机器人具备自主伦理判断。',64,611,1150,43,22,false,C.rust);

s=base('案例三：“为你好”与本人想要的生活','RC045 / Superflux《Uninvited Guests》，2015。思辨设计短片。','作品讲述虚构的70岁Thomas。子女送来的智能设备关注饮食、健康与睡眠，但设备要求与他自己的生活方式发生冲突。这不是社会新闻，而是一部真实存在的虚构作品。借用的方法：把抽象价值冲突压缩到一个普通日常行为中，让观众看到两种有理由的要求怎样碰撞。本项目据此把照护规则改写为公共礼貌规则。来源 '+refs[2].url+' 图片 '+refs[2].imageURL);
await img(s,path.join(assets,'guests.jpg'),62,183,612,418,'cover','Superflux短片中的虚构人物Thomas');pair(s,'一个具体的故事','Thomas 收到子女送来的智能照护设备。\n设备的安排与他的生活习惯发生冲突。',722,185,490);pair(s,'我借用的叙事方法','让“照顾我”与“替我决定”，\n在同一个日常动作中显现。',722,392,490);text(s,'作品是真实来源，人物情节是虚构。不能据此声称智能照护普遍有害。',64,611,1150,43,22,false,C.rust);

s=base('虚构情境：谁更容易被安排退让','规则由虚构的轮椅服务提供方设定；首要使用者是林岚，行人也有正当通行需求。','场景全部虚构。社区中心窄走廊，两处错身空间。轮椅一侧较近，行人一侧较远。服务方沿用公共机器人的主动让人规则，默认调度轮椅。没有紧急事故，不把行人塑造成坏人。真正冲突是公共通行便利与本人对身体移动的决定权。如果每次都调度最易控制的轮椅，负担可能反复集中在同一个人。原型只是脚本空间，不是建筑或安全验证。');
await img(s,path.join(assets,'story1.png'),57,177,1166,325,'contain','带两处错身空间的实际3D模拟场景');pair(s,'虚构的默认规则','轮椅是可调度设备，因此主动退到近处。',66,518,548);pair(s,'被规则省略的问题','被带着后退的人，是否愿意承担这次代价？',674,518,543,C.rust);

s=base('两个选择，把代价交给不同的人','两种选择都可以有理由。原型不设道德评分，也不保证请求一定成功。','我这次让：林岚自愿折返到近处空间，等候行人先过。请对方让：愿意配合的预设中，三位行人折返到较远空间，林岚先过。没有谁免费解决问题，也不把拒绝安排成撞车或惩罚。未回应的分支保持停止，可以等待、改为自愿退让或者结束出行。两张图取自实际网页的两个分支。');
await img(s,path.join(assets,'self-yield.png'),58,185,565,227,'cover','轮椅退入近处空间');await img(s,path.join(assets,'others-yield.png'),657,185,565,227,'cover','行人退入远处空间');pair(s,'我这次让','林岚折返并等待，行人沿原路线通过。\n自愿礼让保留了决定权，仍需付出身体代价。',64,430,560);pair(s,'请对方让','行人折返并等待，林岚沿原路线通过。\n请求能表达意愿，也依赖他人配合。',664,430,556,C.rust);text(s,'若对方暂未回应：保持原位，不把请求模拟成命令。',64,615,1150,39,23,false,C.muted);

s=base('四幕分镜：相遇、叫停、选择、反馈','人物、空间和对话为设计虚构；画面截取自可运行的 3D 原型。','四幕讲述：一，双方都有自己的生活目的，窄走廊发生相遇。二，原规则启动轮椅后退，林岚叫停，轮椅原位保持。三，观众决定谁让路，图示为行人愿意配合分支。四，林岚明确确认先询问，下一次轮椅不再默认后退。此页是分镜，不是已经生成的AI视频。人物、台词与空间为设计虚构。');
const beats=[['相遇','双方都有自己的去处。'],['叫停','“停，我不想退了。”'],['选择','动作改变，代价随之改变。'],['反馈','下一次先等本人决定。']];
for(let i=0;i<4;i++){let x=62+(i%2)*599,y=178+Math.floor(i/2)*238;await img(s,path.join(assets,`story${i+1}.png`),x,y,557,159,'cover',beats[i][0]);text(s,`${i+1}  ${beats[i][0]}`,x,y+168,175,35,24,true,C.teal);text(s,beats[i][1],x+174,y+170,390,40,21);}

s=base('关键交互：叫停要落实到身体动作','课堂演示约 60–90 秒，打开同目录“3D交互原型 / index.html”。','实际操作：点击开始相遇，在第一段后退动作期间点击停，我不想退了，观察轮椅停在当下位置。选择请对方让，看行人退入远处空间。动作结束，打开反馈，勾选不要未经我同意就带我退让并确认。下一次开始时，轮椅等待选择。注意：仅勾选未确认不会改变规则；不点击不视为同意。运行中的错身阶段暂停后，继续原安排或结束，避免不可靠的实时重规划。可在开场条件中选择暂未回应。');
await img(s,path.join(tmp,'qa/choice-desktop.png'),61,180,705,455,'contain','实际网页叫停后的两个选择按钮');pair(s,'叫停','轮椅保留当下位置。\n不是只更换一句安慰。',816,184,397);pair(s,'表达反馈','明确勾选并确认，\n才修改下一次的退让规则。',816,348,397);text(s,'下一次：保持起点，等我决定。',816,557,399,81,28,true,C.teal);

s=base('研究转译：六项来源分别贡献了什么','从既有数据库目的性选例，未新增检索计数，也不把 268 条混合记录都称为真实机器人。','此表把事实、我的解释与能力边界区分开。前三项推动命题与叙事，后三项提供实现行为的参考。LUCI官方使用手册印刷页16讲override，但我的停止社会性退让不等同其override，更不代表停用避障。CoNav为共享控制预印本，实验21位无相关身体障碍成年人，不能推广至老人或残障者。HuggieBot支持身体结束意愿应得到响应的启发，不提供轮椅控制规范。完整来源见最后一页，所有链接可点击。'+refs.map(r=>r.id+' '+r.url).join('\n'));
table(s,[['来源','提取的观点或方法','保留的证据边界'],['RC237 走廊实验','礼让动作表达社会关系','无乘坐者；侧让不等于载人后退'],['RC252 DAWN','机器动作承载人的意愿','真人遥操作，不是自主 AI'],['RC045 思辨短片','用日常冲突质疑照护规则','故事虚构，不能当作社会新闻'],['W07 / RC261 LUCI','本人可以介入辅助过程','我的“叫停”不等同产品 override'],['W01 / RC262 CoNav','把人的纠正纳入控制','21 位无相关身体障碍成年人'],['W08 / RC232 HuggieBot','响应身体上的结束意愿','拥抱研究，不能直接迁移安全参数']],[288,412,460],182,427,22);
text(s,'我的转译：把礼貌规则搬到载人的身体上，追问“谁有权决定，谁反复付出”。',64,621,1150,40,23,false,C.teal);

s=base('“自我修养”如何成为可观察行为','身体动作视角：从默认后退，变为能停止、可协商、可修正。','这里至少有三项修养要求，全部落成观察得到的行为。尊重意愿：用户叫停就保持位置，沉默不自动同意。承认权限与能力边界：可以请求行人配合，但不能命令或挤过；暂停社会性退让不意味着关闭真实避障。纠正错误：用户明确确认反馈后，下一次不再默认带人后退。取舍是先询问带来额外的操作和协商劳动，因此自愿让路依然保留。我们没有证明机器人具备伦理理解，只做出了有限状态下的响应。');
pair(s,'尊重本人意愿','叫停时保持原位。\n未作选择时持续等待，不自动替人同意。',66,188,1138);pair(s,'承认自己的权限','请求不保证成功。\n对方未回应时停下，不编造通行结果。',66,343,1138);pair(s,'从明确反馈中修正','确认“先问我”后，下一次改变动作顺序。\n偏好可以撤回，刷新后清空。',66,498,1138);

s=base('设计取舍与尚未解决的问题','思辨目标：让代价与权限可见，保留观众提出相反理由的空间。','本版避免用算法伦理评分选出标准答案，把对照限定在谁折返与谁等待。但标题本身已经重视本人决定权；人物设定也排除了急救、严重认知困难等不同情境。先征询仍可能把协商劳动交回本人，也不能解决无障碍空间不足或服务提供方责任。课堂可问：自愿总是让路的人有没有真实选择？行人不配合时，谁应协调？实际实现仅浏览器脚本和3D插值，无真实感知、避障、运动控制、模型训练或长期记忆，未做目标用户研究。Codex协助研究、叙事、代码和PPT；ImageGen生成界面概念；六项案例配图来自原始来源；3D画面由本网页生成。');
text(s,'如果每次最容易被调度的都是轮椅，\n“偶尔让一下”会不会变成同一个人一直付出？',65,189,1145,138,37,true);pair(s,'保留的困难','先询问也增加操作与协商劳动。\n一次交互无法解决空间不足和制度责任。',65,372,565);pair(s,'实际实现与 AI 使用','已实现：3D 分支、原位停止、确认后改规则。\n未接入真实感知、控制或训练，无用户研究。\nCodex 辅助制作；ImageGen 用于界面概念。',673,372,545);text(s,'人物、走廊、规则与对话属于设计虚构；选择了“分镜＋交互”，未制作视频。',65,610,1150,45,22,false,C.muted);

s=base('来源备查：案例、图片与数据库编号','点击案例名称可打开原始来源。完整定位、配图出处与证据边界随提交包保存。','六张缩略图按用户要求与前述案例对应，重复作为来源识别。所有图片仅用于课程分析，版权归原作者或项目。各项目细节及图源：\n'+refs.map(r=>`${r.id} ${r.name}\n${r.url}\n图源：${r.imageURL}`).join('\n\n')+'\n课程依据：用户提供《思辨设计-Week1-案例RTD.pdf》，页24、51、52、58。核对日期2026-09-20。');
for(let i=0;i<6;i++){let x=64+(i%3)*400,y=180+Math.floor(i/3)*235;let r=refs[i];await img(s,path.join(assets,r.image),x,y,356,123,'contain',r.name+'原始来源配图');let link=text(s,r.name,x,y+130,363,37,26,true,C.teal);link.text.get(r.name).link={uri:r.url,isExternal:true};text(s,r.id+'  /  '+(i===0?'2013':i===1?'真实项目':i===2?'虚构作品':i===3?'官方手册':i===4?'预印本':'机器人研究'),x,y+170,363,28,18,false,C.muted);}

await fs.writeFile(path.join(tmp,'narrative.json'),JSON.stringify(transcript,null,2));await fs.writeFile(path.join(tmp,'refs.json'),JSON.stringify(refs,null,2));
const candidate=path.join(tmp,'candidate.pptx');await (await PresentationFile.exportPptx(P)).save(candidate);console.log('EXPORTED',slides.length);
await finalizePresentation({workspaceDir,candidatePath:candidate,finalPath:path.join(out,'说明PPT_请别替我让路.pptx'),pythonExecutable:'C:/Users/22602/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe',integrityValidatorPath:path.join(SKILL_DIR,'container_tools/inspect_presentation_package_integrity.py'),layoutValidatorPath:path.join(SKILL_DIR,'container_tools/inspect_presentation_layout_geometry.py'),layoutArgs:['--expected-slide-size-emu','12192000,6858000','--validate-bullet-geometry','--validate-heading-fit','--require-native-table-slide','10'],requiredNativeTableOwnerSlides:[10],fontPolicy:{basis:'design',families:[FONT]},verifyArtifactToolImport:true,receiptPath:path.join(tmp,'deck-validation-delivery.json')});console.log('FINALIZED');
for(let i=0;i<slides.length;i++){let b=await P.export({slide:slides[i],format:'png',scale:1.25});await fs.writeFile(path.join(tmp,'slides',String(i+1).padStart(2,'0')+'.png'),new Uint8Array(await b.arrayBuffer()));console.log('RENDERED',i+1)}

