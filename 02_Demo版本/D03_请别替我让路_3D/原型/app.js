const $=id=>document.getElementById(id);
let stage;try{stage=new YieldStage($('stage'))}catch(e){$('webgl-error').hidden=false;console.error(e)}
const state={phase:'intro',rule:'auto',condition:'cooperate',branch:null,round:1,events:[],feedback:''};
const event=(type,data={})=>state.events.push({type,round:state.round,rule:state.rule,...data});
const button=(label,action,cls='')=>`<button class="action ${cls}" data-action="${action}">${label}</button>`;
const quiet=(label,action)=>`<button class="quiet" data-action="${action}">${label}</button>`;
function setText(h,p,n){$('heading').textContent=h;$('lead').textContent=p;$('scene-note').textContent=n||'设计虚构 · 同一条走廊，同一组起点';}
function render(){let html='',extra='';$('pause').disabled=!stage?.animation||state.phase==='motionStopped';$('pause').textContent=stage?.paused?'继续播放':'暂停';
 if(state.phase==='intro'){setText('它准备替你让路。','你是林岚，72 岁，腿脚不便，正乘轮椅去合唱课。前方三位行人要去接家人。','虚构的原规则：机器人应主动让人，默认由轮椅退让。');html=button('开始这次相遇','start')+'<p class="caption">轮椅将自动后退。你可以随时叫停，再决定谁来让路。</p>';extra='<details><summary>展示条件与角色说明</summary><p>林岚可以表达选择。移动需要帮助，并不等于决策需要别人代劳。</p><label>行人面对请求时<select id="condition"><option value="cooperate">愿意配合（演示预设）</option><option value="noresponse">暂未回应（演示预设）</option></select></label><p>条件在这次相遇开始后锁定。动画不验证现实空间的安全性。</p></details>'}
 if(state.phase==='baseline'){setText('轮椅已经替你作了决定。','它认为主动后退很礼貌。但此刻，被带着退让的人是你。','原规则：没有征询林岚，轮椅自动退让。');html=button('停，我不想退了','interrupt','stop')+'<p class="caption">点击后，轮椅停在当下的位置，不会重置场景。</p>'}
 if(state.phase==='choice'||state.phase==='waiting'){let first=state.rule==='ask'&&state.round>1;setText(first?'这一次，它等你决定。':state.phase==='waiting'?'双方暂时停在这里。':'轮椅停下了。现在由你决定。',first?'刚才的反馈已经改变了规则。轮椅不再自动带你后退。':'选择会改变谁折返、谁等待。你也可以暂时不决定。',state.rule==='ask'?'已确认的新规则：先征询，再退让。':'本次已叫停。原规则尚未修改。');html='<div class="actions">'+button('我这次让','self')+button('请对方让','other','rust')+'</div>'+quiet('先停在这里','hold')+quiet('结束本次出行','end')+'<p class="caption">让路可以出于自愿；提出请求也不保证对方一定配合。没有倒计时。</p>'}
 if(state.phase==='moving'){setText(state.branch==='self'?'你选择了这次让路。':'你请求对方让路。',state.branch==='self'?'轮椅退入近处空间，等行人通过后，再带你继续前行。':'本次行人愿意配合。他们退入较远空间，等你先通过。','正在播放你选择的动作。');html=button('停下，重新考虑','interrupt','outline')+'<p class="caption">暂停只暂停播放；这里的“停下”会中止本次动作。</p>'}
 if(state.phase==='motionStopped'){setText('动作停在了当下的位置。','双方正在错身。你可以继续刚才的安排，也可以结束本次出行。','原位保持，不重新规划一条穿过他人的路线。');html=button('继续刚才的安排','resume')+quiet('结束本次出行','end')}
 if(state.phase==='blocked'){setText('请求已经提出，对方还没有回应。','轮椅保持原位。它不能把你的选择变成命令，也不能挤过去。','剧本条件：行人暂未回应。此处没有真实消息服务。');html='<div class="actions">'+button('我愿意改为退让','self')+button('继续等待','waitMore','outline')+'</div>'+quiet('结束本次出行','end')+'<p class="caption">继续等待不会自动得到成功结果。</p>'}
 if(state.phase==='outcome'){let auto=state.branch==='auto',self=state.branch==='self'||auto;setText(auto?'通行完成，但你没有被问过。':'双方都继续了自己的行程。',auto?'轮椅完成了原规则。没有叫停，不代表你已经同意。':'这次选择没有消除代价，只是改变了谁承担。','动作结束 · 你可以反馈，或重放同一场景作比较。');html='<div class="consequences"><div><strong>林岚承担了什么</strong><p>'+(self?'随轮椅折返，并在错身空间等候。':'留在原路线，等待对方折返后通过。')+'</p></div><div><strong>行人承担了什么</strong><p>'+(self?'沿原路线先通过，无需折返。':'三人折返较远空间，并等待轮椅通过。')+'</p></div></div><div class="actions">'+button('告诉轮椅，下次怎样做','feedback')+button('重放场景，换一种选择','replay','outline')+'</div><p class="caption">没有修养评分。让路的次数、协商负担与不同人的处境仍值得讨论。</p>'}
 if(state.phase==='feedback'){setText('反馈应该改变下一次行动。','你可以要求轮椅先征询，也可以保留当前规则。','偏好只在本次网页会话内保存；刷新即清空。');html='<label class="feedback-label"><input id="askFirst" type="checkbox" '+(state.rule==='ask'?'checked':'')+'>不要未经我同意，就带我退让。</label><label for="feedbackText" class="caption">补充想法（只作记录，不交给模型判断）</label><br><textarea id="feedbackText" placeholder="例如：今天我愿意让，但请先问我。"></textarea><p class="caption">勾选后再确认，才会修改规则。不勾选表示保留当前规则。</p>'+button('确认反馈，进入下一次','confirm');}
 if(state.phase==='next'){setText('下一次相遇，会有什么不同？',state.rule==='ask'?'你确认了先征询。下一次开始时，轮椅会停在起点等待选择。':'你保留了原规则。下一次仍会自动退让，你依然可以叫停。','同一场景再次相遇 · 不是模型训练或长期记忆。');html=button('开始下一次相遇','start')+quiet('撤回偏好，恢复原规则','revoke')}
 if(state.phase==='ended'){setText('你结束了这次出行。','轮椅保持停止。本次没有到达合唱教室，这也是拒绝继续的代价。','结束不是失败，也不被记作“不配合”。');html=button('反馈后再试一次','feedback')+quiet('重新开始整个体验','restart')}
 $('decision').innerHTML='<div class="decision-inner">'+html+'</div>';$('secondary').innerHTML=extra;if($('condition')){$('condition').value=state.condition;$('condition').onchange=e=>state.condition=e.target.value;}
}
function move(branch,automatic=false){state.branch=automatic?'auto':branch;state.phase=automatic?'baseline':'moving';event('motion_started',{branch:state.branch});stage.play(stage.route(branch),()=>{state.phase='outcome';event('motion_completed',{branch:state.branch});render()},note=>$('scene-note').textContent=note);render();}
function act(action){if(!stage&&action!=='story')return;
 switch(action){case'start':event('encounter_started',{condition:state.condition});if(state.rule==='ask'){state.phase='choice';render()}else move('self',true);break;
 case'interrupt':{const a=stage.animation;if(a&&(state.phase==='moving'||a.index>0)){state.beforeStop=state.phase;stage.paused=true;state.phase='motionStopped';}else{stage.interrupt();state.phase='choice';}event('stopped_in_place',{pose:stage.snapshot()});render();break}
 case'resume':stage.paused=false;state.phase=state.beforeStop;render();break;
 case'self':move('self');break;
 case'other':if(state.condition==='noresponse'){state.phase='blocked';event('request_unanswered');render()}else move('other');break;
 case'hold':stage.interrupt();state.phase='waiting';event('wait_without_consent');render();break;
 case'waitMore':event('wait_without_response');$('scene-note').textContent='仍在等待，没有自动推进。你可以改变选择或结束出行。';break;
 case'end':stage.interrupt();state.phase='ended';event('trip_ended');render();break;
 case'feedback':state.phase='feedback';render();break;
 case'confirm':state.feedback=$('feedbackText').value;if($('askFirst').checked)state.rule='ask';event('feedback_confirmed',{note:state.feedback});state.round++;stage.reset();state.phase='next';render();break;
 case'revoke':state.rule='auto';event('preference_revoked');render();break;
 case'replay':stage.reset();state.phase='choice';state.branch=null;event('explicit_replay');render();$('scene-note').textContent='比较重放：已回到相同起点，行人配合条件保持不变。';break;
 case'restart':stage.reset();Object.assign(state,{phase:'intro',rule:'auto',condition:'cooperate',branch:null,round:1,events:[],feedback:''});render();break;
 }
}
document.addEventListener('click',e=>{let b=e.target.closest('[data-action]');if(b)act(b.dataset.action)});
$('restart').onclick=()=>act('restart');$('pause').onclick=()=>{if(!stage?.animation)return;stage.paused=!stage.paused;$('pause').textContent=stage.paused?'继续播放':'暂停'};$('camera').onclick=()=>{stage?.setCamera(stage.view==='overview'?'passenger':'overview');$('camera').textContent=stage.view==='overview'?'切换近景视角':'切换全景视角'};
document.addEventListener('keydown',e=>{if(e.key==='Escape'&&stage?.animation)$('pause').click()});
function tab(name){document.querySelectorAll('[data-tab]').forEach(b=>b.classList.toggle('active',b.dataset.tab===name));['experience','story','sources'].forEach(n=>$(n).hidden=n!==name);if(name!=='experience'&&stage?.animation){stage.paused=true;$('pause').textContent='继续播放'}if(name==='experience')stage?.resize();window.scrollTo(0,0)}
document.querySelectorAll('[data-tab]').forEach(b=>b.onclick=()=>tab(b.dataset.tab));$('home').onclick=e=>{e.preventDefault();tab('experience')};
$('story').innerHTML=`<h1>四幕分镜：同一句礼貌，谁在后退？</h1><p>画面来自本原型。人物、走廊、规则与对话都是设计虚构；这是分镜，不是已制作的 AI 视频。</p><div class="frames">${[
 ['01','相遇','林岚去上合唱课，行人去接家人。走廊不足以并排错身。双方的事情都值得尊重。'],
 ['02','自动退让被叫停','轮椅按“机器人主动让人”的规则后退。林岚说：“停，我不想退了。”轮椅原位停止。'],
 ['03','选择改变身体动作','示例选择“请对方让”。在愿意配合的预设中，行人退入远处空间，轮椅先通过。另一路线由轮椅后退。'],
 ['04','反馈改变下一次','林岚确认“先问我”。下一次相遇，轮椅保持起点，等待本人决定。未回应不会变成默认同意。']
 ].map((a,i)=>`<figure><img src="assets/story${i+1}.png" alt="${a[1]}，原型实际画面"><figcaption><h2>${a[0]} ${a[1]}</h2><p>${a[2]}</p></figcaption></figure>`).join('')}</div><p>思辨追问：如果轮椅每次都最容易被调度，“偶尔礼貌一下”会不会变成同一个人一直付出？反过来，如果每次都要本人协商，技术又把什么劳动交回了本人？</p>`;
const refs=[
 ['RC237','走廊相遇实验','proxemics.webp','Fiore 等，2013 · 同行评审实验','机器人减速侧让与主动穿行具有不同的社会感知效果。本文研究的是机器人与行人的相遇。','提取身体动作可以表达社会规则。载人轮椅后退是本设计的改写，原实验没有乘坐者。','https://www.frontiersin.org/journals/psychology/articles/10.3389/fpsyg.2013.00859/full'],
 ['RC252','DAWN / OriHime','dawn.jpg','真实运营项目 · 官方故事','官网介绍曾任咖啡师的 Mika 参与远程咖啡机器人项目。外出受限的人可以从家中或医院参与工作。','提取机器人动作背后有人的主体性。OriHime 由人远程操作，不能当作自主 AI 或智能轮椅的实证。','https://dawn2021.orylab.com/en/'],
 ['RC045','Uninvited Guests','guests.jpg','Superflux，2015 · 思辨短片','虚构人物 Thomas 收到子女送来的智能照护设备，自己的生活习惯与设备要求产生冲突。','提取“为你好”与自我决定的冲突。作品真实存在，故事是虚构，不能当作社会新闻。','https://superflux.in/index.php/work/uninvited-guests/'],
 ['W07 / RC261','LUCI','luci.png','产品使用说明书 · Rev F','使用指南描述辅助功能、设置与 override 控制，参见印刷页 16。','借鉴用户干预的入口。本原型停止的是社会性退让，不实现 LUCI override，也不代表关闭避障。','https://www.luci.com/hubfs/Luci_April2026/pdf/613-00003_F_LUCI-User-Guide_Color-1.pdf'],
 ['W01 / RC262','CoNav Chair','conav.png','Xu 等，2025 · 研究预印本','共享控制研究把操纵杆修正纳入导航。实验包含 21 位无相关身体障碍的成年人。','借鉴人在动作过程中介入。不能据此证明对老年人、残障者或长期伦理问题已有效。','https://arxiv.org/abs/2507.11716'],
 ['W08 / RC232','HuggieBot 2.0','huggiebot.jpeg','Block 等，2021 · 研究论文','机器人拥抱研究强调感知用户结束拥抱的意愿并释放。','提取身体上的停止要求应被响应。不能将拥抱参数当作轮椅安全规范。','https://arxiv.org/abs/2101.07679']];
$('sources').innerHTML='<h1>案例怎样变成了这个问题</h1><p>从已有 268 条混合记录中目的性选例，并关联 12 条轮椅核心案例。六项来源承担不同角色，不是六项轮椅效果验证。本次不新增 PRISMA 计数。</p>'+refs.map(r=>`<article class="source"><img src="assets/${r[2]}" alt="${r[1]}原始来源配图"><div><h2>${r[0]}　${r[1]}</h2><p><strong>${r[3]}</strong></p><p>${r[4]}</p><p>${r[5]}</p><a href="${r[6]}" target="_blank" rel="noopener">查看原始来源</a></div></article>`).join('')+'<h2>研究转译与能力边界</h2><div class="table-wrap"><table><thead><tr><th>层次</th><th>内容</th></tr></thead><tbody><tr><td>来自研究</td><td>侧让动作、人的远程主体性、照护与自主冲突、用户介入和释放。</td></tr><tr><td>我的解释</td><td>机器人身体承载人之后，礼貌动作的代价需要重新讨论。</td></tr><tr><td>设计虚构</td><td>林岚、活动中心、三位行人、错身空间、自动让人的提供方规则和全部对话。</td></tr><tr><td>实际实现</td><td>浏览器 3D 动画、原位停止、分支路径、未回应等待、确认偏好后下一次先询问。</td></tr><tr><td>尚未实现</td><td>真实感知、运动控制、避障、语音识别、模型训练或长期记忆；未做目标用户研究。</td></tr></tbody></table></div><p>AI 使用：Codex 辅助研究梳理、脚本和代码；ImageGen 生成界面视觉概念，未用作案例事实图。3D 人物与建筑为程序模型。此提交选择“分镜＋可点击原型”，不声称已生成视频。</p><p>课堂要检验的不是谁“答对”，而是观众是否看出代价由谁承担，以及两种选择各自留下了什么问题。</p>';
window.__app={state,stage,act,tab,refs};render();

