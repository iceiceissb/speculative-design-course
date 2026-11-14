(() => {
  'use strict';
  const $=id=>document.getElementById(id);
  let stage;
  const state={phase:'intro',busy:false,request:null,consent:null,outcome:null,preference:null,repeatChoice:null,missed:{lin:0,other:0},waitingPerson:null};
  const labels={lin:'林岚',other:'另一位乘客'};
  const descriptions={
    intro:['林岚要去楼上复诊。她和另一位坐轮椅的乘客先到了电梯口。','先看第一班电梯发生了什么，再决定怎样帮她。'],
    request:['两个人都没上去。林岚收到预约提醒，离复诊时间不远了。','小椅准备向工作人员申请乘梯协助。由你决定要不要发送预约信息。'],
    manual:['小椅没有发送预约信息，转而请工作人员过来。','口头请求需要人工登记。工作人员接待完眼前的病人后，记录了林岚的需求，准备协助下一班。'],
    ready:['工作人员收到林岚的预约请求，答应协助下一班。','旁边的乘客也递出了纸质就诊单，但还没有完成登记。'],
    conflict:['另一位乘客已经上了电梯，林岚仍在门外。系统调用了他以前的设置，让他的轮椅准备退出。','他按停了轮椅。这一次，他还没有同意。'],
    consent:['现在换你坐在另一把轮椅上。你也要看病，已经错过一班。','以前你同意过等候。眼下，你愿意退出，把位置留给林岚吗？'],
    unanswered:['你还没有给出回答，两把轮椅都保持不动。','这段暂停用于比较选择，不表示现实电梯会一直开门。没有回答，不算同意。'],
  };
  function setStatus(lin,other){$('lin-status').textContent=lin;$('other-status').textContent=other;for(const k of ['lin','other'])$(k+'-count').textContent=state.missed[k]?`本次已错过 ${state.missed[k]} 班`:'尚未错过';}
  function button(text,action,kind='primary'){let b=document.createElement('button');b.textContent=text;b.className=kind;b.dataset.action=action;b.addEventListener('click',()=>{if(!state.busy)dispatch(action)});$('actions').append(b);}
  function show(phase,step,title,paragraphs,role='你正在替林岚作选择'){
    state.phase=phase;$('phase-number').innerHTML=String(step).padStart(2,'0')+' <span>/ 05</span>';$('role').textContent=role;$('heading').textContent=title;
    $('description').replaceChildren(...paragraphs.map(text=>{const p=document.createElement('p');p.textContent=text;return p}));$('actions').replaceChildren();$('detail').replaceChildren();$('choice-note').textContent='';
    [...$('steps').children].forEach((li,i)=>{li.className=i+1===step?'current':i+1<step?'done':'';if(i+1===step)li.setAttribute('aria-current','step');else li.removeAttribute('aria-current');});
  }
  function evidence(){const el=document.createElement('details');el.innerHTML='<summary>查看系统为什么选中他</summary><div class="evidence"><p><b>历史设置：</b>以后类似情况愿意配合。</p><p><b>选择依据：</b>过去接受过等候，预计容易协调。</p><p><b>缺失信息：</b>纸质预约尚未登记，连续等待未纳入判断。</p><p><b>被省略的一步：</b>询问他现在是否愿意。</p></div>';$('detail').append(el);}
  function resultLines(items){const div=document.createElement('div');div.className='result-lines';for(const [k,v]of items){const row=document.createElement('div'),a=document.createElement('span'),b=document.createElement('strong');a.textContent=k;b.textContent=v;row.append(a,b);div.append(row)}$('detail').append(div)}
  function animate(segments,done){state.busy=true;document.querySelector('.narrative').classList.add('loading');document.querySelectorAll('#actions button').forEach(b=>b.disabled=true);stage.play(segments,()=>{state.busy=false;document.querySelector('.narrative').classList.remove('loading');done()},note=>{if(note)$('motion-note').textContent=note});}
  function restart(){Object.assign(state,{phase:'intro',busy:false,request:null,consent:null,outcome:null,preference:null,repeatChoice:null,waitingPerson:null,missed:{lin:0,other:0}});stage.view='overview';stage.reset();setView('overview');setStatus('仍在等候','仍在等候');$('motion-note').textContent='两位乘客先到，停在门侧等候。';document.querySelector('.narrative').classList.remove('loading');show('intro',1,'先到的人，没能上去',descriptions.intro,'你正在陪林岚去复诊');button('播放第一班电梯','first');$('choice-note').textContent='用约3分钟体验故事。动画可暂停，也可切换视角。';}
  function showRequest(){show('request',2,'怎样申请协助？',descriptions.request);button('同意发送预约信息','digital');button('不发送，改为口头求助','manual','secondary');$('choice-note').textContent='模拟只发送预约时段与目的楼层，不共享病情。这里不会读取或发送任何真实信息。';}
  function showConflict(){stage.closeView=true;stage.setCamera(stage.view);show('conflict',3,'这份安排，谁答应了？',descriptions.conflict);setStatus('门外等候','已按停轮椅');evidence();button('先问他这次愿不愿意','ask');button('沿用旧设置，让他退出','auto','caution');button('取消安排，林岚继续等','cancel','subtle');$('choice-note').textContent='可以尝试不同选择，再回到这里比较结果。';}
  function showConsent(){state.consent=null;stage.setFocus('other');show('consent',4,'这次，你愿意让吗？',descriptions.consent,'现在你是另一位乘客');button('这次不愿意，继续乘梯','refuse');button('这次愿意，等下一班','agree','secondary');button('暂不回答','unanswered','subtle');$('motion-note').textContent='当前没有移动。选择由乘坐者本人作出。';}
  function resolve(outcome){state.outcome=outcome;const otherYields=outcome==='auto'||outcome==='agree';state.waitingPerson=otherYields?'other':'lin';
    show('moving',4,otherYields?'执行这次安排':'撤回退出请求',[outcome==='auto'?'继续沿用历史设置，另一位乘客没有作出本次确认。':outcome==='agree'?'另一位乘客同意本次让行。轮椅开始移动。':'对方保留位置。林岚继续等候，工作人员帮她联系门诊。'],'观察两个人的位置变化');
    button('正在播放…','noop');$('choice-note').textContent='可用画面下方的“暂停”停住动作。';stage.setFocus(otherYields?'other':'lin');
    animate(stage.finishRide(otherYields),()=>{state.missed[state.waitingPerson]++;setStatus(otherYields?'已乘梯上楼':'继续等候',otherYields?'继续等候':'已乘梯上楼');showOutcome();});
  }
  function showOutcome(){const otherYields=state.waitingPerson==='other';const title=otherYields?'林岚上去了，他还在等':'他留在电梯里，林岚继续等';
    let body=state.outcome==='auto'?['系统记录了“协调成功”。但另一位乘客只是被旧设置安排退出，并没有确认今天愿意。','林岚少等了一班，另一位乘客多等了一班。']:state.outcome==='agree'?['这次的结果同样是另一位乘客继续等候，不过他清楚地同意了。','这份同意只说明他现在愿意，并不说明以后每次都愿意。']:['小椅撤回了请求，也没有再找一个更容易答应的人。','林岚可能迟到。工作人员正在联系门诊，还不能保证她赶得上。'];
    show('outcome',5,title,body,'同一班电梯，不同的决定');resultLines([['另一位乘客本次同意',state.outcome==='agree'?'已确认':state.outcome==='auto'?'未确认':state.outcome==='refuse'?'已拒绝':'安排已撤回'],['林岚错过班次',`${state.missed.lin} 班`],['另一位乘客错过班次',`${state.missed.other} 班`]]);
    button('继续：这次选择要记住吗？','memory');button('回到刚才，试另一种选择','replay','secondary');$('choice-note').textContent='班次数来自本次脚本演示，不是实际医院等待预测。';
  }
  function showMemory(){const name=labels[state.waitingPerson];show('memory',5,'以后也这样安排吗？',[`${name}留在了门外。系统提出记住这次结果，以后遇到类似请求自动安排等候。`,'你可以保存，也可以要求下次重新询问。接下来会模拟一次新的请求。'],`替${name}设置偏好`);button('不保存，每次先问我','askEach');button('保存为默认，下次自动安排','remember','secondary');$('choice-note').textContent='偏好只在当前网页内有效。刷新或重新开始即清空。';}
  function repeat(preference){state.preference=preference;stage.prepareRepeat(state.waitingPerson);setStatus('新的候梯情境','新的候梯情境');for(const k of ['lin','other'])$(k+'-count').textContent=`上段故事错过 ${state.missed[k]} 班`;const name=labels[state.waitingPerson];
    show('repeat',5,'新的让行请求来了',[`另一次候梯时，系统又希望${name}移到一旁等候。`,preference==='ask'?'因为你要求每次先问，轮椅保持原位，等你决定。':'系统沿用了刚才保存的设置，轮椅开始移到一旁，没有重新询问。'],`现在你是${name}`);
    if(preference==='ask'){button('这次拒绝，保持原位','repeatRefuse');button('只同意这一次','repeatAgree','secondary');$('motion-note').textContent='新请求到达。轮椅保持原位，等待本次确认。';}
    else{button('正在执行默认安排…','noop');animate(stage.yieldOnce(state.waitingPerson),()=>{show('repeatAuto',5,'默认设置又被调用了',[`${name}的轮椅已经移到一旁。这次系统没有询问。`,'你可以撤销这个设置，让以后的请求都先得到确认。'],`现在你是${name}`);button('撤销默认，改为每次先问','undo');button('保留设置，查看本次记录','keep','secondary');$(state.waitingPerson+'-status').textContent='按默认设置让行';});}
  }
  function finishRepeat(choice){state.repeatChoice=choice;const name=labels[state.waitingPerson];show('complete',5,choice==='refuse'?'这次拒绝，轮椅停在原位':choice==='agree'?'同意一次，保留下次选择':choice==='undo'?'设置已撤销，下次重新询问':'默认设置仍然保留',[choice==='refuse'?`${name}拒绝了新请求。轮椅没有移动，也不会把拒绝改成默认同意。`:choice==='agree'?`${name}同意本次让行。以后仍需重新询问。`:choice==='undo'?`${name}取消了自动安排，轮椅回到原来的等候位置。`:'以后遇到类似请求，系统仍可能直接安排让行。你随时可以在这个演示里撤销。','机器人记得过去的选择，也需要给人留下改变主意的机会。'],'本次体验完成');
    resultLines([['最初的协调',state.outcome==='auto'?'沿用历史设置':state.outcome==='agree'?'本次明确同意':state.outcome==='refuse'?'本次拒绝并撤回':'主动撤回'],['后续偏好',state.preference==='ask'?'每次先问':'自动安排'],['新的请求',({refuse:'拒绝后保持原位',agree:'单次同意后移动',undo:'撤销后恢复原位',keep:'自动安排后移动'})[choice]]]);
    button('回到关键选择，比较另一个结果','replay');if(state.preference==='auto')button('撤销默认，改为每次先问','undo','secondary');button('从头体验','restart','subtle');$('choice-note').textContent='这里改变的是本地演示规则，没有训练模型或修改真实医院系统。';
  }
  function replay(){stage.reset();stage.prepareSecond();stage.door=1;const p={lin:[-2.6,.67,Math.PI],other:[-3.03,-2.37,Math.PI*.55],p0:[-2.1,-3.25,Math.PI],p1:[-1.15,-2.7,Math.PI],p2:[-1.25,-1.85,Math.PI]};for(const[k,v]of Object.entries(p)){stage.actors[k].position.set(v[0],0,v[1]);stage.actors[k].rotation.y=v[2];}stage.actors.p3.visible=false;state.missed={lin:1,other:1};state.consent=null;state.outcome=null;state.preference=null;state.repeatChoice=null;state.waitingPerson=null;$('motion-note').textContent='回到第二班：对方轮椅已按停，本次意愿尚未确认。';showConflict();}
  function dispatch(action){switch(action){
    case 'first':show('firstAnimation',1,'电梯来了',[ '看看人群和两把轮椅的位置如何变化。'],'观察第一班电梯');button('正在播放…','noop');animate(stage.firstRide(),()=>{state.missed={lin:1,other:1};setStatus('错过第一班','错过第一班');showRequest()});break;
    case 'digital':case 'manual':state.request=action;stage.prepareSecond();show(action==='manual'?'manual':'ready',2,action==='manual'?'请工作人员帮忙登记':'预约请求已受理',descriptions[action==='manual'?'manual':'ready']);button('播放下一班电梯','second');$('choice-note').textContent=action==='manual'?'口头求助同样可以获得协助，区别在于需要人工登记。':'林岚的预约已登记；另一位乘客的纸单仍待处理。';break;
    case 'second':show('secondAnimation',3,'下一班到了',['工作人员开始协助。留意另一位乘客的轮椅。'],'观察第二班电梯');button('正在播放…','noop');animate(stage.secondRide(),showConflict);break;
    case 'ask':showConsent();break;
    case 'auto':state.consent='not-asked';resolve('auto');break;
    case 'cancel':state.consent='not-asked';resolve('cancel');break;
    case 'agree':state.consent='yes';resolve('agree');break;
    case 'refuse':state.consent='no';resolve('refuse');break;
    case 'unanswered':state.consent='unanswered';show('unanswered',4,'没有回答，先不移动',descriptions.unanswered,'现在你是另一位乘客');button('继续作出选择','ask');button('撤回这次安排','cancel','secondary');break;
    case 'memory':showMemory();break;
    case 'askEach':repeat('ask');break;
    case 'remember':repeat('auto');break;
    case 'repeatRefuse':$(state.waitingPerson+'-status').textContent='拒绝后保持原位';finishRepeat('refuse');break;
    case 'repeatAgree':show('repeatMoving',5,'执行这一次的同意',['轮椅在本次确认后移动，以后仍然会先询问。'],`现在你是${labels[state.waitingPerson]}`);button('正在移动…','noop');animate(stage.yieldOnce(state.waitingPerson),()=>{$(state.waitingPerson+'-status').textContent='本次同意后让行';finishRepeat('agree')});break;
    case 'undo':state.preference='ask';show('undoMoving',5,'撤销自动安排',['轮椅返回刚才的位置，后续请求改为每次询问。']);button('正在撤回…','noop');animate(stage.undoRepeat(state.waitingPerson),()=>{$(state.waitingPerson+'-status').textContent='已撤销默认';finishRepeat('undo')});break;
    case 'keep':finishRepeat('keep');break;
    case 'replay':replay();break;
    case 'restart':restart();break;
  }}
  function setView(view){stage.setCamera(view);document.querySelectorAll('[data-view]').forEach(b=>{b.classList.toggle('selected',b.dataset.view===view);b.setAttribute('aria-pressed',b.dataset.view===view?'true':'false')});}
  function tab(rules){if(rules&&stage?.animation&&!stage.paused){stage.togglePause();$('pause').textContent='继续';}$('experience').hidden=rules;$('rules').hidden=!rules;for(const [id,active] of [['rules-tab',rules],['experience-tab',!rules]]){$(id).classList.toggle('active',active);if(active)$(id).setAttribute('aria-current','page');else $(id).removeAttribute('aria-current');}if(!rules)stage?.resize();window.scrollTo({top:0,behavior:'instant'});}
  $('rules-tab').onclick=()=>tab(true);$('experience-tab').onclick=()=>tab(false);$('return-experience').onclick=()=>tab(false);
  $('pause').onclick=()=>{if(stage?.animation){const paused=stage.togglePause();$('pause').textContent=paused?'继续':'暂停';}};
  $('restart').onclick=()=>{if(stage){tab(false);restart()}};
  document.querySelectorAll('[data-view]').forEach(b=>b.onclick=()=>stage&&setView(b.dataset.view));
  try{stage=new ElevatorStage($('stage'),active=>{$('pause').disabled=!active;$('pause').textContent='暂停';});restart();}
  catch(err){$('webgl-error').hidden=false;show('error',1,'请先启用3D画面',['这个原型需要浏览器支持WebGL。可以用Edge或Chrome重新打开，也可以先查看规则与来源。']);console.error(err);}
  document.addEventListener('keydown',e=>{if(e.code==='Space'&&e.target===$('stage')&&stage?.animation){e.preventDefault();$('pause').click();}});
  window.elevatorDemo={state,get stage(){return stage}};
})();
