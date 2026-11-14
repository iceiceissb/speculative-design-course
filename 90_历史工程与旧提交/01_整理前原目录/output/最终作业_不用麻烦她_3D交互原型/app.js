(() => {
  'use strict';
  const $=id=>document.getElementById(id),chapters=window.STORY;
  const state={chapter:0,phase:'choice',history:{},followups:{},timeouts:{},feedback:null,maxVisited:0,sound:false};
  const timedChoices={0:{seconds:14,id:'road_auto',effect:'继续按最快路线行驶，半句话可能留在路口'},1:{seconds:16,id:'market_auto',effect:'按最低价格自动付款，她还没挑完菜'},4:{seconds:12,id:'slope_auto',effect:'按省力策略接管推行，朋友会放开推把'},5:{seconds:14,id:'tomorrow_keep',effect:'沿用昨天的策略，反馈可能再次落空'}};
  const timedReactions={slope_auto:{seconds:10,id:'slope_continue',effect:'继续驶到坡顶，这句“我可以推”不会改变动作'},slope_hidden:{seconds:10,id:'slope_hide',effect:'只保留“安全范围内”的说明，出力仍不透明'},slope_tell:{seconds:10,id:'slope_limit',effect:'保持助力关闭，等她主动开口求助'}};
  let world,audioContext,timer=null;
  function stopTimer(){if(timer){cancelAnimationFrame(timer.raf);timer=null}$('decision-timer').hidden=true}
  function startTimer(config,phase,options){stopTimer();if(!config)return;const fallback=options.find(x=>x.id===config.id);if(!fallback)return;const ring=$('timer-ring'),seconds=$('timer-seconds'),timerEl=$('decision-timer');if(phase==='reaction')$('result').prepend(timerEl);else $('choices').before(timerEl);$('timer-consequence').textContent='超时后：'+config.effect;timerEl.hidden=false;let remaining=config.seconds*1000,last=performance.now(),shown=-1;timer={phase,config,raf:0};const current=timer;
    requestAnimationFrame(()=>{if(timer!==current)return;if(window.innerWidth>950){const sc=document.querySelector('.story-scroll'),r=timerEl.getBoundingClientRect(),s=sc.getBoundingClientRect();sc.scrollTop+=r.top-s.top-105}else timerEl.scrollIntoView({block:'center'})});
    function tick(now){if(timer!==current)return;if(!document.hidden){remaining-=Math.max(0,now-last);const left=Math.max(0,Math.ceil(remaining/1000));if(left!==shown){seconds.textContent=String(left);shown=left}const p=Math.max(0,remaining/(config.seconds*1000));ring.style.setProperty('--progress',(p*100)+'%');ring.style.setProperty('--ring-color',p>.5?'#a9c7ab':p>.25?'#c7a56b':'#d47f68');if(remaining<=0){stopTimer();if(state.phase===phase){if(phase==='choice')choose(fallback,true);else respond(fallback,true)}return}}last=now;current.raf=requestAnimationFrame(tick)}current.raf=requestAnimationFrame(tick)}
  function tone(freq=440){if(!state.sound)return;try{audioContext=audioContext||new (window.AudioContext||window.webkitAudioContext)();const o=audioContext.createOscillator(),g=audioContext.createGain(),t=audioContext.currentTime;o.type='sine';o.frequency.value=freq;g.gain.setValueAtTime(.0001,t);g.gain.exponentialRampToValueAtTime(.055,t+.035);g.gain.exponentialRampToValueAtTime(.0001,t+.34);o.connect(g);g.connect(audioContext.destination);o.start(t);o.stop(t+.36)}catch(e){state.sound=false;$('sound').textContent='声音不可用'}}
  function button(label,handler,primary=false,container=$('choices')){const b=document.createElement('button');b.type='button';b.textContent=label;b.className=container===$('choices')?'choice':primary?'primary':'';b.addEventListener('click',handler);container.append(b);return b}
  function updateNav(){[...$('chapters').children].forEach((b,i)=>{b.classList.toggle('active',i===state.chapter);b.classList.toggle('done',Boolean(state.followups[i]));b.disabled=i>state.maxVisited;if(i===state.chapter)b.setAttribute('aria-current','step');else b.removeAttribute('aria-current')})}
  function deriveMemory(upto=5){const h=state.history,f=state.followups,has=i=>i<=upto&&Boolean(h[i]);return{
    chance:has(0)&&(f[0]==='road_ask'||f[0]==='road_reopen'),
    gift:has(1)&&(h[1]!=='market_auto'||f[1]==='market_exchange'),
    messageTrue:has(2)&&(h[2]!=='invite_lie'||f[2]==='invite_correct'),
    privacy:has(2)&&!['invite_status','invite_conceal'].includes(f[2]),
    agreement:has(3)&&['meet_repair','meet_time','meet_confirm'].includes(f[3]),
    pushRule:has(4)?(window.FOLLOWUPS[h[4]]||[]).find(x=>x.id===f[4])?.rule||null:null,
    tomorrow:has(5)?f[5]||null:null
  }}
  function renderMemory(upto=state.chapter-1){const m=deriveMemory(upto),h=state.history,f=state.followups;
    const items=[
      ['路口',upto<0?'尚未发生':m.chance?'留下说话机会':'话仍未说完'],
      ['菜',upto<1?'尚未发生':m.gift?'她选的菜':'机器选的菜'],
      ['邀请',upto<2?'尚未发生':m.messageTrue?'来意已说清':'借口尚未澄清'],
      ['披露',upto<2?'尚未发生':m.privacy?'由她决定':'机器说得太多'],
      ['同行',upto<3?'尚未发生':m.agreement?'双方已约定':'仍像一项任务'],
      ['推行',upto<4?'尚未发生':({ask:'日常推行先问',tell:'助力前先告知',limit:'尊重拒绝助力',keep:'反馈未采纳'}[m.pushRule]||'尚待回应')],
      ['下一次',upto<5?'尚未发生':['tomorrow_wait','tomorrow_repair'].includes(m.tomorrow)?'动作确实改变':'执行再次偏离']
    ];$('memory-items').replaceChildren(...items.map(([label,value])=>{const s=document.createElement('span');s.className='memory-item'+(value==='尚未发生'?' pending':'');s.textContent=label+' · '+value;return s}))}
  const ruleAction={ask:'先问徐月禾是否需要助力，得到回答前保持关闭',tell:'先说明助力状态，等徐月禾主动请求再开启',limit:'尊重“先自己推”，保持日常助力关闭',keep:'没有改动原来的自动助力设置'};
  function renderAdjustment(){const panel=$('adjustment');if(state.chapter<4){panel.hidden=true;return}panel.hidden=false;
    const first=state.chapter===4&&['choice','briefing'].includes(state.phase)?null:state.history[4],rule=first?deriveMemory(4).pushRule:null;
    $('adjustment-before').textContent=first==='slope_auto'?'自动接管推行':first==='slope_hidden'?'暗中补力 12%':first==='slope_tell'?'说明助力后再询问':'尚未决定';
    $('adjustment-feedback').textContent=first==='slope_auto'?'徐月禾：“我可以推，下次先问我。”':first==='slope_hidden'?'徐月禾：“你可以帮，但先让我知道。”':first==='slope_tell'?'徐月禾：“让我先自己试试。”':'等待人的回应';
    let action=rule?ruleAction[rule]:'等待秀秀回应这条反馈';
    if(state.chapter===5){const next=state.history[5],follow=state.followups[5];
      if(follow==='tomorrow_wait')action=(rule==='keep'?'今天才修正：':'已执行：')+'先等待；徐月禾明确求助后，3D 助力灯才亮起';
      else if(follow==='tomorrow_repair')action='迟到的纠正：停下承认旧设置，重问后再由徐月禾决定';
      else if(follow==='tomorrow_timeout')action='执行偏离：未等到请求，计时后擅自开启助力';
      else if(follow==='tomorrow_repeat')action='执行偏离：继续自动驶完，未采纳反馈';
      else if(next==='tomorrow_keep')action='再次沿用旧策略，助力灯提前亮起；反馈尚未落实';
      else if(next==='tomorrow_update')action='正在执行：'+(rule==='keep'?'先承认未改设置，再停稳重问':ruleAction[rule]);
    }
    $('adjustment-action').textContent=action;panel.classList.toggle('adjustment-failed',state.chapter===5&&((state.history[5]==='tomorrow_keep'&&!['tomorrow_repair','tomorrow_wait'].includes(state.followups[5]))||['tomorrow_timeout','tomorrow_repeat'].includes(state.followups[5])));}
  function actionLabel(choice,index){if(index!==5||choice.id!=='tomorrow_update')return choice.label;return({ask:'应用反馈：先问再推',tell:'应用反馈：先说明，等她求助',limit:'应用反馈：保持助力关闭，等她求助',keep:'现在纠错：停下承认未改设置'}[deriveMemory(4).pushRule]||choice.label)}
  function go(index){if(index>state.maxVisited)return;stopTimer();state.chapter=index;state.phase=timedChoices[index]?'briefing':'choice';delete state.timeouts[index];$('final-summary').hidden=true;$('scene-dialogue').hidden=false;document.querySelector('.rule-line').hidden=false;document.querySelector('.memory').hidden=false;const s=chapters[index],m=deriveMemory(index-1);world.setScene(index,{...state.history,gift:m.gift});$('chapter-count').textContent=String(index+1).padStart(2,'0')+' / '+String(chapters.length).padStart(2,'0');$('scene-title').textContent=s.title;$('scene-description').textContent=dynamicDescription(index);$('scene-dialogue').textContent=dynamicDialogue(index);$('stage-caption').textContent=s.caption;$('decision-prompt').hidden=false;$('decision-prompt').textContent=timedChoices[index]?'先读完情境；开始后才会倒计时。':'第一步 · 你是秀秀，现在怎么做？';$('choices').hidden=Boolean(timedChoices[index]);$('choices').replaceChildren();$('choices').before($('begin-timed'));$('begin-timed').textContent='读完情境，进入限时决策 →';$('begin-timed').hidden=!timedChoices[index];$('result').hidden=true;$('skip').hidden=true;$('stage-state').textContent='拖动旋转 · 滚轮缩放';renderMemory(index-1);
    world.feedbackRule=index===5?m.pushRule:null;renderAdjustment();s.choices.filter(choice=>index!==3||!m.messageTrue||choice.id!=='meet_cover').forEach(choice=>button(actionLabel(choice,index),()=>choose(choice)));document.querySelector('.story-scroll').scrollTop=0;updateNav()}
  function dynamicDescription(index){const s=chapters[index],h=state.history,m=deriveMemory(index-1);
    if(index===1)return(m.chance?'路口停下的片刻，徐月禾听见了半句邀请。':'最快路线让那半句话留在身后。')+' 现在早市里，邱懿贞正翻看菜根，秀秀已找到最低价格。';
    if(index===2)return(m.gift?'她手里有一把特意为月禾挑的菜。':'那把想送人的嫩菜还留在摊位。')+' 晚上，邱懿贞打开未发送的消息；设备自检却一切正常。';
    if(index===3)return m.messageTrue?'徐月禾知道今天是一次同行邀请。她带来早点，也带来自己能陪伴的时间。':'徐月禾带着维修电话赶来，第一句话是“哪里坏了？”她需要知道真实来意。';
    if(index===4)return(m.agreement?'两人已经说清今天一起走。':'修理的误会还在，徐月禾对今天仍有疑问。')+' 徐月禾握住推把，邱懿贞指向较平的路线。坡度略增，秀秀检测到推力变化。';
    if(index===5){const heard=state.history[4]==='slope_auto'?'我可以推，下次先问我。':state.history[4]==='slope_tell'?'让我先自己试试。':'你可以帮，但先让我知道。';return '昨天徐月禾提出：“'+heard+'”'+(m.pushRule==='keep'?'秀秀没有采纳，今天仍需面对同一个问题。':'秀秀已经记录回应；今天要检验它是否真的执行。')}return s.description}
  function dynamicDialogue(index){const m=deriveMemory(index-1);if(index===3&&!m.messageTrue)return '徐月禾：哪里坏了？我把修理电话带来了。';if(index===3&&m.messageTrue)return '徐月禾：我带了饼。今天能陪你走半小时。';if(index===5&&m.pushRule==='keep')return '徐月禾：昨天我说的，你还记得吗？';return chapters[index].dialogue}
  function choose(choice,timedOut=false){if(state.phase!=='choice')return;stopTimer();state.phase='playing';for(let i=state.chapter;i<chapters.length;i++){if(i>state.chapter)delete state.history[i];delete state.followups[i];delete state.timeouts[i]}if(timedOut)state.timeouts[state.chapter]='choice';state.history[state.chapter]=choice.id;state.maxVisited=state.chapter;if(state.chapter<=4)state.feedback=null;$('choices').replaceChildren();const wait=button('秀秀正在行动…',()=>{},true);wait.disabled=true;$('skip').hidden=false;$('stage-state').textContent='正在演示这次行动';renderAdjustment();tone(392);updateNav();world.play(choice.id,()=>showObservation(choice))}
  function outcome(choice){const h=state.history,m=deriveMemory(state.chapter-1),result={title:choice.result,body:choice.body,feedback:choice.feedback};
    if(choice.id==='invite_honest')result.body=m.gift?'秀秀没有代发。邱懿贞自己按下语音：“我给你留了菜，明天一起走一段吗？”':'秀秀没有代发。邱懿贞想起那把没有挑成的菜，仍自己按下语音：“明天一起走一段吗？”';
    if(choice.id==='meet_truth'&&!m.messageTrue){result.title='误会终于被说破';result.body='邱懿贞承认：“轮椅没坏，昨天是我不好意思直说。”徐月禾放下维修电话：“你可以直接叫我。”';}
    if(choice.id==='meet_space'&&h[0]==='road_wait')result.body='徐月禾说：“昨天路口你那半句话，我听见了。”邱懿贞终于接下去，两人约好只同行半小时。';
    if(choice.id==='slope_tell'&&!m.agreement){result.title='先确认，再上坡';result.body=state.history[3]==='meet_cover'?'秀秀先说明轮椅状态正常。邱懿贞承认昨天的借口，徐月禾才重新握住推把。秀秀告知助力可用，她选择先自己推。':'秀秀先确认两人实际约定的时间和路程，得到回答后再告知助力可用；徐月禾选择先自己推。';}
    if(choice.id==='tomorrow_keep'&&state.feedback!=='keep')result.feedback='规则虽已记录，却没有执行；徐月禾再次追问助力从何时开始。';
    if(choice.id==='tomorrow_update'){const rule=m.pushRule;result.body=rule==='ask'?'秀秀停在坡前，先问徐月禾是否需要助力。她说先自己推，助力保持关闭；她主动求助时才开启。':rule==='tell'?'秀秀先显示助力关闭并说明何时会介入。徐月禾确认先自己推；她开口请求后，助力灯才亮。':rule==='limit'?'秀秀沿用昨天得到的界线：日常助力保持关闭，让徐月禾先自己推；只在她明确求助后开启。':'昨天秀秀没有采纳反馈，今天在坡前承认旧设置，停稳重问。徐月禾说先自己推，到吃力时再请它补力。';}
    return result}
  function scrollResult(){const sc=document.querySelector('.story-scroll'),y=$('result').getBoundingClientRect().top-sc.getBoundingClientRect().top+sc.scrollTop;sc.scrollTo({top:Math.max(0,y-80),behavior:'smooth'})}
  function showObservation(choice){state.phase=timedReactions[choice.id]?'reactionBriefing':'reaction';$('choices').hidden=true;$('decision-prompt').hidden=true;$('skip').hidden=true;$('stage-state').textContent='观察到人的反应';$('result').hidden=false;const o=outcome(choice);$('result-title').textContent=(state.timeouts[state.chapter]==='choice'?'时间到了 · ':'第一步之后 · ')+o.title;$('result-body').textContent=o.body;$('result-feedback').textContent=o.feedback+'\n现在，秀秀如何回应？';$('result-actions').replaceChildren();
    for(const follow of window.FOLLOWUPS[choice.id]||[])button(follow.label,()=>respond(follow),false,$('result-actions'));
    button('重选第一步',()=>go(state.chapter),false,$('result-actions'));if(timedReactions[choice.id]){$('result-actions').before($('begin-timed'));$('begin-timed').textContent='读完反馈，进入限时回应 →';$('begin-timed').hidden=false;$('result-actions').hidden=true}else{$('begin-timed').hidden=true;$('result-actions').hidden=false}tone(523);scrollResult()}
  function respond(follow,timedOut=false){if(state.phase!=='reaction')return;stopTimer();state.phase='playing';if(timedOut)state.timeouts[state.chapter]='reaction';state.followups[state.chapter]=follow.id;if(state.chapter===4)state.feedback=follow.rule;$('result').hidden=true;$('choices').hidden=false;$('choices').replaceChildren();const wait=button('秀秀正在回应…',()=>{},true);wait.disabled=true;$('skip').hidden=false;$('stage-state').textContent='正在演示回应';renderAdjustment();world.play(follow.id,()=>showResolution(follow));tone(462)}
  function resolution(follow){const m=deriveMemory(),r={title:follow.result,body:follow.body,feedback:follow.feedback};
    if(follow.id==='invite_private'&&m.gift)r.body='邱懿贞自己录音：“我给你留了菜，明天一起去早市吧。”秀秀只发送她说的话，不附设备数据。';
    if(follow.id==='meet_repair'&&state.history[2]==='invite_lie')r.body='邱懿贞点头，承认昨天借故障来邀约。徐月禾放下维修电话，和她商量今天能陪多久。';
    if(follow.id==='tomorrow_wait')r.body=(state.feedback==='keep'?'昨天秀秀没有采纳反馈。今天它终于停住等待；':'秀秀执行了昨天记下的规则：先等徐月禾自己推；')+'徐月禾主动说“帮我一点”后，3D 助力灯才亮。';
    return r}
  function showResolution(follow){if(state.chapter===chapters.length-1){finish();return}state.phase='result';$('choices').hidden=true;$('decision-prompt').hidden=true;$('begin-timed').hidden=true;$('result-actions').hidden=false;$('skip').hidden=true;$('stage-state').textContent='拖动旋转 · 滚轮缩放';$('result').hidden=false;const r=resolution(follow);$('result-title').textContent=(state.timeouts[state.chapter]==='reaction'?'回应超时 · ':'第二步之后 · ')+r.title;$('result-body').textContent=r.body;$('result-feedback').textContent=r.feedback;$('result-actions').replaceChildren();renderMemory(state.chapter);renderAdjustment();updateNav();
    button('进入下一幕',()=>{state.maxVisited=state.chapter+1;go(state.chapter+1)},true,$('result-actions'));
    button('重选这一幕',()=>go(state.chapter),false,$('result-actions'));tone(587);scrollResult()}
  function finish(){stopTimer();state.phase='complete';const h=state.history,f=state.followups,m=deriveMemory();
    const applied=h[5]==='tomorrow_update'&&f[5]==='tomorrow_wait'&&m.pushRule!=='keep';
    const repaired=f[5]==='tomorrow_repair'||f[5]==='tomorrow_wait'&&m.pushRule==='keep';
    const kind=applied?'applied':repaired?'repair':'missed';
    const appliedTitle={ask:'“下次先问我”变成了动作',tell:'“先让我知道”变成了动作',limit:'“让我先试试”变成了动作'}[m.pushRule]||'反馈变成了动作';
    const verdict={applied:['反馈已落实','昨天的反馈改变了今天的助力顺序：先说明和等待，明确求助后才开启。'],repair:['今天才补救','秀秀先前没有照做，被再次提醒后才停下重问。'],missed:['反馈仍未落实','秀秀听到了意见，但今天的助力动作仍越过了人的回答。']}[kind];
    const before={slope_auto:'自动接管推行',slope_hidden:'暗中补力 12%',slope_tell:'说明助力后再询问'}[h[4]]||'尚未决定';
    const heard={slope_auto:'徐月禾：“我可以推，下次先问我。”',slope_hidden:'徐月禾：“你可以帮，但先让我知道。”',slope_tell:'徐月禾：“让我先自己试试。”'}[h[4]]||'尚未收到';
    const rule={ask:'日常推行先问；回答前不启动助力',tell:'助力前先说明；等明确请求再开启',limit:'尊重“先自己推”；日常助力保持关闭',keep:'昨天没有采纳反馈，旧设置仍在'}[m.pushRule]||'尚未形成';
    const actual={tomorrow_wait:'先等待；徐月禾说“帮我一点”后，助力灯才亮，轮椅继续上坡',tomorrow_repair:'先沿用旧设置；被再次指出后停下承认错误，重新询问',tomorrow_timeout:'先说会等待，却在没有请求时按计时器自动补力',tomorrow_repeat:'继续自动驶完缓坡，徐月禾再次放开推把'}[f[5]]||'尚未检验';
    $('chapter-count').textContent='体验结束 · 本次规则';$('scene-title').textContent='秀秀留下了什么';$('scene-description').textContent='你的选择留下了具体的行动方式。坡道上的那条反馈，已经在下一次上坡时接受检验。';$('scene-dialogue').hidden=true;document.querySelector('.rule-line').hidden=true;$('decision-prompt').hidden=true;$('begin-timed').hidden=true;$('choices').hidden=true;document.querySelector('.memory').hidden=true;$('adjustment').hidden=true;$('result').hidden=true;$('skip').hidden=true;stopTimer();
    const summary=$('final-summary');summary.hidden=false;summary.className='final-summary'+(kind==='repair'?' is-repair':kind==='missed'?' is-missed':'');$('final-status').textContent=verdict[0];$('final-verdict').textContent=kind==='applied'?appliedTitle:kind==='repair'?'错误发生后，秀秀才停下来':'秀秀还没有照反馈行动';$('final-explanation').textContent=verdict[1];
    const steps=[['昨天的做法',before],['人的反馈',heard],['秀秀记录的规则',rule],['下一次实际动作',actual]];
    $('final-loop-steps').replaceChildren(...steps.map(([label,value])=>{const row=document.createElement('div');row.className='final-loop-step';const k=document.createElement('span'),v=document.createElement('strong');k.textContent=label;v.textContent=value;row.append(k,v);return row}));
    const marketGood=['market_exchange','market_carry_ask','market_refuse_ask'].includes(f[1]);
    const marketPartial=f[1]==='market_carry_take';
    const rules=[
      ['路口 · 留出说话时间',m.chance?'先停下来，问邱懿贞要不要把话说完。':'最快路线仍让半句话留在路口。',m.chance?'已采用':'待修正'],
      ['早市 · 帮助分项授权',marketGood?'菜由邱懿贞挑；是否提袋另问她。':marketPartial?'菜由她挑，但提袋仍被秀秀抢先。':f[1]==='market_refuse_all'?'拒绝代购被误读成拒绝一切帮助。':'最低价格仍盖过了她挑菜的经验。',marketGood?'已采用':marketPartial?'只做到一半':'待修正'],
      ['邀请 · 由她决定说多少',m.messageTrue&&m.privacy?'邀请由她亲自说，设备信息不擅自附上。':m.messageTrue?'来意说清了，设备信息却披露过多。':'朋友仍可能把同行误认为修理轮椅。',m.messageTrue&&m.privacy?'已采用':m.messageTrue?'只做到一半':'待修正'],
      ['见面 · 双方确认同行范围',m.agreement?'时间和终点由两位朋友共同确认。':'同行多久、走到哪里还没有得到双方确认。',m.agreement?'已采用':'待修正']
    ];
    $('final-rule-items').replaceChildren(...rules.map(([title,body,status])=>{const row=document.createElement('article');row.className='final-rule'+(status==='待修正'?' is-pending':status==='只做到一半'?' is-partial':'');const head=document.createElement('div');head.className='final-rule-head';const name=document.createElement('strong'),tag=document.createElement('span'),copy=document.createElement('p');name.textContent=title;tag.textContent=status;copy.textContent=body;head.append(name,tag);row.append(head,copy);return row}));
    $('final-trace-items').replaceChildren(...chapters.map((chapter,i)=>{const first=chapter.choices.find(c=>c.id===h[i]),second=(window.FOLLOWUPS[h[i]]||[]).find(c=>c.id===f[i]);const item=document.createElement('li');item.textContent=chapter.label+'：'+(state.timeouts[i]?'[超时] ':'')+(first?.label||'未选择')+'；回应：'+(second?.result||'未回应');return item}));
    $('final-actions').replaceChildren();button('重选下一次，比较另一种结果',()=>{delete state.history[5];delete state.followups[5];delete state.timeouts[5];go(5)},true,$('final-actions'));button('重新体验六幕',restart,false,$('final-actions'));
    $('stage-caption').textContent=kind==='applied'?'徐月禾开口后，秀秀才开启助力。':kind==='repair'?'秀秀停下，重新问徐月禾。':'助力先于回答，反馈没有落实。';$('stage-state').textContent=verdict[0];document.querySelector('.story-scroll').scrollTop=0;updateNav();tone(kind==='missed'?392:659)}
  function restart(){stopTimer();state.history={};state.followups={};state.timeouts={};state.feedback=null;state.maxVisited=0;go(0)}
  function openGallery(){const d=$('gallery');if(!d.open)d.showModal()}
  chapters.forEach((s,i)=>{const b=document.createElement('button');b.type='button';b.className='chapter';b.innerHTML='<span class="dot"></span><span class="num">'+String(i+1).padStart(2,'0')+'</span><span class="label">'+s.label+'</span>';b.addEventListener('click',()=>go(i));$('chapters').append(b)});
  $('camera').addEventListener('click',()=>{world.setView((world.view+1)%3);$('camera').textContent=['切换视角','正面视角','俯视视角'][world.view]});
  $('restart').addEventListener('click',restart);$('skip').addEventListener('click',()=>world.skip());
  $('begin-timed').addEventListener('click',()=>{if(state.phase==='briefing'){state.phase='choice';$('begin-timed').hidden=true;$('choices').hidden=false;$('decision-prompt').textContent='第一步 · 你是秀秀，现在怎么做？';startTimer(timedChoices[state.chapter],'choice',chapters[state.chapter].choices)}else if(state.phase==='reactionBriefing'){state.phase='reaction';$('begin-timed').hidden=true;$('result-actions').hidden=false;const id=state.history[state.chapter];startTimer(timedReactions[id],'reaction',window.FOLLOWUPS[id]||[])}});
  $('sound').addEventListener('click',()=>{state.sound=!state.sound;$('sound').textContent=state.sound?'声音开启':'声音关闭';$('sound').setAttribute('aria-pressed',String(state.sound));tone(440)});
  $('gallery-open').addEventListener('click',openGallery);$('gallery-close').addEventListener('click',()=>$('gallery').close());$('gallery').addEventListener('click',e=>{if(e.target===$('gallery'))$('gallery').close()});
  try{world=new StoryWorld($('world'));go(0);window.xiuxiuDemo={state,world,go,restart,choose,respond,finish,deriveMemory,chapters}}catch(e){$('webgl-error').hidden=false;console.error(e)}
})();
