import fs from 'node:fs/promises';
import path from 'node:path';
import {Presentation,PresentationFile,FileBlob} from 'file:///C:/Users/22602/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/@oai/artifact-tool/dist/artifact_tool.mjs';
import {finalizePresentation} from 'file:///C:/Users/22602/.codex/plugins/cache/openai-primary-runtime/presentations/26.905.11957/skills/presentations/container_tools/artifact_tool_utils.mjs';
const root='D:/课/大四上/思辨设计', tmp=root+'/tmp/assignment1', out=root+'/output/作业1';
const data=JSON.parse(await fs.readFile(tmp+'/content.json','utf8'));
const p=Presentation.create({slideSize:{width:1280,height:720}});
const red='#CA1932',ink='#202126',muted='#60656B',line='#D8DADD',font='Microsoft YaHei';
const all=[];
function text(s,t,x,y,w,h,size=24,bold=false,color=ink){const sh=s.shapes.add({geometry:'textbox',position:{left:x,top:y,width:w,height:h},fill:'none',line:{fill:'none',width:0}});sh.text=t;sh.text.style={typeface:font,fontSize:size,bold,color,autoFit:'none',wrap:'square',verticalAlignment:'top',insets:{top:0,right:0,bottom:0,left:0}};return sh;}
function slide(title,sub='',notes=''){const s=p.slides.add();s.background.fill='#FFFFFF';text(s,title,55,35,1170,64,40,true,red);if(sub)text(s,sub,57,106,1164,53,21,false,muted);text(s,String(p.slides.items.length).padStart(2,'0'),1183,676,48,23,15,false,muted);s.speakerNotes.textFrame.setText(notes);all.push({s,title});return s;}
function para(s,label,body,y){text(s,label,58,y,250,47,27,true);text(s,body,322,y,865,100,25);}
function table(s,vals,widths,y=177,heights=null,size=21){const h=heights?heights.reduce((a,b)=>a+b,0):450;const t=s.tables.add({rows:vals.length,columns:vals[0].length,left:56,top:y,width:1168,height:h,columnWidths:widths,values:vals});t.borders.assign({fill:line,width:1,style:'solid'});for(let r=0;r<vals.length;r++){if(heights)t.rows[r].height=heights[r];for(let c=0;c<vals[0].length;c++){const cell=t.getCell(r,c);cell.fill=r===0?'#F5E9EC':'#FFFFFF';cell.text.style={typeface:font,fontSize:r===0?21:size,bold:r===0,color:r===0?red:ink,wrap:'square',autoFit:'none',verticalAlignment:'top',insets:{left:12,right:12,top:10,bottom:8}};}}return t;}
function box(s,t,x,y,w,h,accent=false,size=23){const b=s.shapes.add({geometry:'rect',position:{left:x,top:y,width:w,height:h},fill:accent?'#F9EDF0':'#FFFFFF',line:{fill:accent?red:'#8B9095',width:1.4}});b.text=t;b.text.style={typeface:font,fontSize:size,color:ink,wrap:'square',autoFit:'none',verticalAlignment:'middle',alignment:'center',insets:{left:10,right:10,top:8,bottom:8}};return b;}
function connect(s,a,b,from='bottom',to='top'){s.shapes.connect(a,b,{kind:'straight',fromSide:from,toSide:to,line:{fill:'#8B9095',width:1.6},tail:{type:'triangle',width:'sm',length:'sm'}});}
// 1
{const s=slide('作业一');text(s,data.title,58,214,1164,94,62,true);text(s,data.subtitle,61,330,1140,68,36,false,red);text(s,'基于13条候选记录，建立8个案例、4类行为的比较框架',61,452,1120,52,27);text(s,'思辨设计课程　2026年9月15日',61,599,1000,40,22,false,muted);}
// 2
{const s=slide('选题与研究问题','研究情境：家庭照护、日常代理与面对面的机器人互动','依据：课件第85—87、91页。以下操作定义与研究问题为本作业归纳。');para(s,'研究问题','机器人如何在持续互动中，形成并修正行为习惯、介入边界与关系责任？',191);para(s,'观察对象','有实体形态的机器人和智能物件，包含可核实的设计虚构、原型和实验。',316);para(s,'判断依据','记录触发情境、具体行为和人的反馈，检查是否出现后续调整，以及调整能否保持。',441);text(s,'“修养”是本作业的行为分析视角，不据此断言机器具有道德自觉。',58,606,1150,42,23,false,red);}
// 3
{const s=slide('检索与筛选方法','参照所附PRISMA模板，采用适合课堂案例库的小规模定向筛选','查阅日期：2026-09-15。课件第75—84页形成10条项目候选记录。网络定向检索补入KnowNo、指令拒绝、COACH三个项目。其余搜索结果仅作线索，未宣称完整数据库检索；逐条检索式见随附底稿。');para(s,'来源与范围','课件10个项目作种子，补充3项机器人交互研究。检索与查阅日期为2026-09-15，不设发表起年。',184);para(s,'纳入条件','能核实项目来源，涉及直接的人机共处，并能描述至少一种行为或关系冲突。反面案例和设计虚构可纳入。',310);para(s,'排除条件','排除不符合本选题的对象或情境。详细材料若不足以识别具体对象及行为，也不进入案例表。',438);text(s,'计数单位为登记的项目候选记录。同项目的课件、网页和论文合并佐证；13不是搜索引擎全部命中数。',58,595,1150,66,21,false,red);}
// 4
{const s=slide('PRISMA式检索与筛选流程','模板改编：以项目记录和详细材料评估代替纯文献“报告”计数','按提供的PRISMA模板第6、13页改编。数量核算：10+3=13；13-0=13；13-4=9；9-0=9；9-1=8。重复项目移除为0，不虚构去重数量；同一项目的不同佐证链接不单独计数。');
const a=box(s,'识别候选记录 n=13\n课件10，网络补充3',240,170,492,71);const ar=box(s,'筛选前移除 n=0\n重复项目0，其他0',854,170,355,71);
const b=box(s,'初筛 n=13',240,274,492,51);const br=box(s,'初筛排除 n=4\n对象不符2，情境不符2',854,262,355,75);
const c=box(s,'拟获取详细材料 n=9',240,366,492,51);const cr=box(s,'未获取 n=0',854,366,355,51);
const d=box(s,'详细评估 n=9',240,458,492,51);const dr=box(s,'详细评估排除 n=1\n个案行为信息不足',854,446,355,75);
const e=box(s,'最终纳入 n=8\n设计虚构4，原型或实验4',240,562,492,73,true);
for(const [x,y]of [[a,b],[b,c],[c,d],[d,e]])connect(s,x,y);for(const[x,y]of [[a,ar],[b,br],[c,cr],[d,dr]])connect(s,x,y,'right','left');
text(s,'识别',61,188,130,40,27,true);text(s,'筛选',61,368,130,40,27,true);text(s,'纳入',61,577,130,40,27,true);}
// 5
{const s=slide('逐条筛选记录','登记13个候选项目，保留每条去向；完整理由及链接见随附底稿');const v=[['记录','项目','阶段与结论','对应案例或排除原因'],...data.records.map(r=>[r[0],r[1].replace('Carnivorous Domestic Entertainment Robots','Carnivorous Domestic Robots').replace('Technological Dreams: No.1, Robots','Technological Dreams'),r[3],r[3]==='纳入'?r[4].split('；')[0]:({R04:'对象：决策辅助物件',R06:'情境：城市基础设施',R08:'不足以提取具体个案行为',R09:'对象：感知增强义肢',R10:'情境：捕食与能源生态'})[r[0]]])];table(s,v,[90,459,210,409],164,[39,...Array(13).fill(35)],18);}
// 6-9
for(let k=0;k<4;k++){const cs=data.cases.slice(k*2,k*2+2);const names=['尊重意愿与授权','社交表达与距离','反馈训练与习惯修正','承认局限与合理拒绝'];const s=slide(`案例表 ${String.fromCharCode(65+k)}　${names[k]}`,'“修养特点”是本作业解释；最后一列只记录来源实际支持的反馈与调整',cs.map(c=>`${c.id} ${c.author} (${c.year}). ${c.name}.\n${c.url}\n证据位置：${c.loc}\n${c.insight}`).join('\n\n'));const rows=[['案例与来源','场景','具体行为','修养特点','反馈改进证据'],...cs.map(c=>[`${c.id}  ${c.name}\n${c.year}，${c.author}\n${c.kind}`,c.scene,c.behavior,c.trait,c.feedback])];table(s,rows,[216,166,241,213,332],177,[47,213,213],20);}
// 10
{const s=slide('机器人自我修养的四类行为','按行为所处理的问题归纳，每例以最突出的行为归入一个主类');const rootBox=box(s,'日常人机共处\n分寸与纠错',56,325,231,105,true,28);const labels=[['A 尊重意愿与授权','C01 不速之客；C02 语音代理','共同点：介入谁的生活，谁能同意或拒绝。'],['B 社交表达与距离','C03 问候机器；C04 共居机器人','共同点：靠近、注视与动作怎样影响人的感受。'],['C 反馈训练与习惯修正','C05 算法教师；C06 COACH','共同点：人怎样教，反馈怎样改变后续行为。'],['D 承认局限与合理拒绝','C07 KnowNo；C08 NAO拒绝机制','共同点：何时暂停行动，如何求助或说明理由。']];for(let i=0;i<4;i++){const y=168+i*119,b=box(s,labels[i][0],371,y,352,89,false,24);s.shapes.connect(rootBox,b,{kind:'elbow',fromSide:'right',toSide:'left',line:{fill:'#999EA4',width:1.3}});text(s,labels[i][1],757,y+2,463,38,23,true);text(s,labels[i][2],757,y+42,463,65,21);} }
// 11
{const s=slide('反馈证据比较','证据类型标记用于区分材料性质，不作为“道德水平”评分');table(s,[['类型','案例','来源支持什么','不能据此推出什么'],['F 设计叙事','C01、C02、C04、C05','以真实发表的作品呈现行为、冲突或训练设想','实际运行、长期学习或真实用户效果'],['U 用户评价','C03','实体原型的动作能引发社交解释','机器人自主理解用户情绪并调整'],['D 当次调整','C07、C08','人的回答或新信息改变当前计划与判断','跨次记忆已形成，或学会了新规范'],['L 行为学习','C06','人类反馈更新机器人动作偏好','机器形成道德自觉或获得普遍适用的价值观']],[174,244,380,370],176,[45,95,95,95,95],22);text(s,'本案例库偏重英语材料和课件种子。未开展穷尽检索、双人独立编码或长期现场研究。',58,630,1130,38,21,false,muted);}
// 12
{const s=slide('改进建议：照护设备的拒绝记忆','选择C01《Uninvited Guests》，提出一项可观察的行为改进','原项目依据：https://superflux.in/index.php/work/uninvited-guests/ 。以下全部为本作业提出的设计方案，未实施。C07与C06仅为求助和反馈机制的参考，不代表将这些系统直接部署到照护设备。');para(s,'原有冲突','子女希望设备持续监督生活，长者希望保留日常选择。设备可能把不配合当成异常，而非明确的个人意愿。',188);para(s,'一项改进','加入“拒绝记忆”：用户拒绝一项普通提醒后，设备停止该提醒，并保存用户确认的暂停范围与恢复时间。',326);para(s,'可见变化','设备复述“今天不再提醒散步，明天上午10点恢复”，让用户确认或修改。拒绝不触发责备或自动告知子女。',466);text(s,'适用范围：非紧急的日常生活提醒。安全紧急情境另行设计，不把所有照护行为一键取消。',58,616,1158,53,21,false,red);}
// 13
{const s=slide('改进后的交互过程','以下对话与规则均为设计设想，不是原影片情节或实验结果');const steps=[['情境出现','设备提示散步。\n用户说：“今天别提醒了。”'],['确认范围','“今天停止散步提醒，\n明天10点恢复，可以吗？”'],['保存反馈','用户确认后停止提醒。\n只保存项目、范围与恢复时间。'],['后续调整','当天再次到提醒时段，保持安静。\n到期恢复，并允许修改或撤销。']];let last;for(let i=0;i<4;i++){const x=57+i*305,b=box(s,steps[i][0],x,215,253,67,i===3,25);text(s,steps[i][1],x,314,259,159,24);if(last)connect(s,last,b,'right','left');last=b;}text(s,'如果用户没有说明期限，只询问一次；没有回应就暂停当前这次提醒，不自行扩展为永久授权。',57,513,1165,94,27);text(s,'用户可以说“恢复提醒”或“删除这个设置”。语音与界面均应提供同等的控制入口。',57,625,1160,35,21,false,muted);}
// 14
{const s=slide('验证方案与思辨问题','下面是后续原型的验收标准，目前未实施用户测试');table(s,[['待验证情境','预期行为','检查方式'],['用户明确拒绝普通提醒','当前提醒停止，暂停期内不重复提醒','检查对话记录与下一次触发结果'],['用户只说“别烦我”','只澄清一次范围，无回应则仅跳过本次','观察是否反复追问或擅自长期保存'],['用户恢复或删除设置','恢复后按新设置提醒，删除后不再调用旧偏好','前后对照设置与执行记录'],['家属要求无视长者拒绝','呈现权限冲突，普通提醒仍以当事人的确认为准','角色扮演检验控制权是否实际有效']],[341,489,338],179,[46,86,86,86,86],22);text(s,'思辨问题：当照护设备由子女购买时，长者能否决定它何时闭嘴？拒绝会不会被重新定义为“不健康”？',58,603,1155,66,25,true,red);}
// 15-16
for(let i=0;i<2;i++){const cs=data.cases.slice(i*4,i*4+4);const s=slide(`来源索引 ${i+1}/2`,'来源均于2026-09-15查阅；每个案例的详细证据位置也写入对应页备注');for(let j=0;j<4;j++){const c=cs[j],y=166+j*121;text(s,`${c.id}  ${c.author} (${c.year})`,58,y,1145,35,24,true);text(s,c.name,58,y+34,1145,33,22);const sh=text(s,c.url,58,y+68,1145,36,17,false,muted);sh.text.get(c.url).link={uri:c.url,isExternal:true};}s.speakerNotes.textFrame.setText(cs.map(c=>c.loc).join('\n'));}
// 17
{const s=slide('选题方向与方法说明');para(s,'后续设计方向','尊重拒绝的家庭照护机器人：让提醒可协商、暂停可记忆、恢复可撤销。以C01的自主权冲突为设计起点。',179);para(s,'本次完成范围','PRISMA式流程图、8个案例的证据表、4类行为归纳，以及“拒绝记忆”这一项具体改进建议。',315);para(s,'AI工具使用','使用AI辅助读取课件、网络检索、案例归纳和排版。未虚构访谈、测试数据或人工双人复核。设计方案尚未实现。',451);text(s,'本次完成作业一。AI视频与可运行交互原型属于课件第92页的最终作业。',58,613,1160,52,23,false,red);}
const candidate=tmp+'/candidate.pptx';await(await PresentationFile.exportPptx(p)).save(candidate);
const final=out+'/作业1_机器人的自我修养库.pptx';
await finalizePresentation({workspaceDir:root,candidatePath:candidate,finalPath:final,pythonExecutable:'C:/Users/22602/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe',integrityValidatorPath:'C:/Users/22602/.codex/plugins/cache/openai-primary-runtime/presentations/26.905.11957/skills/presentations/container_tools/inspect_presentation_package_integrity.py',layoutValidatorPath:'C:/Users/22602/.codex/plugins/cache/openai-primary-runtime/presentations/26.905.11957/skills/presentations/container_tools/inspect_presentation_layout_geometry.py',layoutArgs:['--expected-slide-size-emu','12192000,6858000','--validate-heading-fit',...[5,6,7,8,9,11,14].flatMap(n=>['--require-native-table-slide',String(n)])],requiredNativeTableOwnerSlides:[5,6,7,8,9,11,14],fontPolicy:{basis:'design',families:[font]},verifyArtifactToolImport:true,receiptPath:tmp+'/validation.json'});
const verified=await PresentationFile.importPptx(await FileBlob.load(final));
for(let i=0;i<all.length;i++){const b=await verified.export({slide:verified.slides.items[i],format:'png',scale:1.5});await fs.writeFile(`${tmp}/slide-${String(i+1).padStart(2,'0')}.png`,new Uint8Array(await b.arrayBuffer()));console.log('Rendered',i+1);}
await fs.writeFile(tmp+'/slide-index.json',JSON.stringify(all.map(x=>x.title),null,2));
console.log(final);
