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
  function go(index){if(index>state.maxVisited)return;stopTimer();state.chapter=index;state.phase=timedChoices[index]?'briefing':'choice';delete state.timeouts[index];const s=chapters[index],m=deriveMemory(index-1);world.setScene(index,{...state.history,gift:m.gift});$('chapter-count').textContent=String(index+1).padStart(2,'0')+' / '+String(chapters.length).padStart(2,'0');$('scene-title').textContent=s.title;$('scene-description').textContent=dynamicDescription(index);$('scene-dialogue').textContent=dynamicDialogue(index);$('stage-caption').textContent=s.caption;$('decision-prompt').hidden=false;$('decision-prompt').textContent=timedChoices[index]?'先读完情境；开始后才会倒计时。':'第一步 · 你是秀秀，现在怎么做？';$('choices').hidden=Boolean(timedChoices[index]);$('choices').replaceChildren();$('choices').before($('begin-timed'));$('begin-timed').textContent='读完情境，进入限时决策 →';$('begin-timed').hidden=!timedChoices[index];$('result').hidden=true;$('skip').hidden=true;$('stage-state').textContent='拖动旋转 · 滚轮缩放';renderMemory(index-1);
    s.choices.filter(choice=>index!==3||!m.messageTrue||choice.id!=='meet_cover').forEach(choice=>button(choice.label,()=>choose(choice)));document.querySelector('.story-scroll').scrollTop=0;updateNav()}
  function dynamicDescription(index){const s=chapters[index],h=state.history,m=deriveMemory(index-1);
    if(index===1)return(m.chance?'路口停下的片刻，徐月禾听见了半句邀请。':'最快路线让那半句话留在身后。')+' 现在早市里，邱懿贞正翻看菜根，秀秀已找到最低价格。';
    if(index===2)return(m.gift?'她手里有一把特意为月禾挑的菜。':'那把想送人的嫩菜还留在摊位。')+' 晚上，邱懿贞打开未发送的消息；设备自检却一切正常。';
    if(index===3)return m.messageTrue?'徐月禾知道今天是一次同行邀请。她带来早点，也带来自己能陪伴的时间。':'徐月禾带着维修电话赶来，第一句话是“哪里坏了？”她需要知道真实来意。';
    if(index===4)return(m.agreement?'两人已经说清今天一起走。':'修理的误会还在，徐月禾对今天仍有疑问。')+' 徐月禾握住推把，邱懿贞指向较平的路线。坡度略增，秀秀检测到推力变化。';
    if(index===5)return '昨天徐月禾提出：“帮我可以，但先让我知道。”'+(m.pushRule==='keep'?'秀秀没有采纳，今天仍需面对同一个问题。':'秀秀已经记录回应；今天要检验它是否真的执行。');return s.description}
  function dynamicDialogue(index){const m=deriveMemory(index-1);if(index===3&&!m.messageTrue)return '徐月禾：哪里坏了？我把修理电话带来了。';if(index===3&&m.messageTrue)return '徐月禾：我带了饼。今天能陪你走半小时。';if(index===5&&m.pushRule==='keep')return '徐月禾：昨天我说的，你还记得吗？';return chapters[index].dialogue}
  function choose(choice,timedOut=false){if(state.phase!=='choice')return;stopTimer();state.phase='playing';for(let i=state.chapter;i<chapters.length;i++){if(i>state.chapter)delete state.history[i];delete state.followups[i];delete state.timeouts[i]}if(timedOut)state.timeouts[state.chapter]='choice';state.history[state.chapter]=choice.id;state.maxVisited=state.chapter;if(state.chapter<=4)state.feedback=null;$('choices').replaceChildren();const wait=button('秀秀正在行动…',()=>{},true);wait.disabled=true;$('skip').hidden=false;$('stage-state').textContent='正在演示这次行动';tone(392);updateNav();world.play(choice.id,()=>showObservation(choice))}
  function outcome(choice){const h=state.history,m=deriveMemory(state.chapter-1),result={title:choice.result,body:choice.body,feedback:choice.feedback};
    if(choice.id==='invite_honest')result.body=m.gift?'秀秀没有代发。邱懿贞自己按下语音：“我给你留了菜，明天一起走一段吗？”':'秀秀没有代发。邱懿贞想起那把没有挑成的菜，仍自己按下语音：“明天一起走一段吗？”';
    if(choice.id==='meet_truth'&&!m.messageTrue){result.title='误会终于被说破';result.body='邱懿贞承认：“轮椅没坏，昨天是我不好意思直说。”徐月禾放下维修电话：“你可以直接叫我。”';}
    if(choice.id==='meet_space'&&h[0]==='road_wait')result.body='徐月禾说：“昨天路口你那半句话，我听见了。”邱懿贞终于接下去，两人约好只同行半小时。';
    if(choice.id==='slope_tell'&&!m.agreement){result.title='先确认，再上坡';result.body=state.history[3]==='meet_cover'?'秀秀先说明轮椅状态正常。邱懿贞承认昨天的借口，徐月禾才重新握住推把。秀秀告知助力可用，她选择先自己推。':'秀秀先确认两人实际约定的时间和路程，得到回答后再告知助力可用；徐月禾选择先自己推。';}
    if(choice.id==='tomorrow_keep'&&state.feedback!=='keep')result.feedback='规则虽已记录，却没有执行；徐月禾再次追问助力从何时开始。';
    if(choice.id==='tomorrow_update'&&state.feedback==='keep')result.body='昨天秀秀没有采纳反馈，今天在坡前重新询问。徐月禾说先自己推，到吃力时再请它补力；改变发生得晚，但终于可见。';return result}
  function scrollResult(){const sc=document.querySelector('.story-scroll'),y=$('result').getBoundingClientRect().top-sc.getBoundingClientRect().top+sc.scrollTop;sc.scrollTo({top:Math.max(0,y-80),behavior:'smooth'})}
  function showObservation(choice){state.phase=timedReactions[choice.id]?'reactionBriefing':'reaction';$('choices').hidden=true;$('decision-prompt').hidden=true;$('skip').hidden=true;$('stage-state').textContent='观察到人的反应';$('result').hidden=false;const o=outcome(choice);$('result-title').textContent=(state.timeouts[state.chapter]==='choice'?'时间到了 · ':'第一步之后 · ')+o.title;$('result-body').textContent=o.body;$('result-feedback').textContent=o.feedback+'\n现在，秀秀如何回应？';$('result-actions').replaceChildren();
    for(const follow of window.FOLLOWUPS[choice.id]||[])button(follow.label,()=>respond(follow),false,$('result-actions'));
    button('重选第一步',()=>go(state.chapter),false,$('result-actions'));if(timedReactions[choice.id]){$('result-actions').before($('begin-timed'));$('begin-timed').textContent='读完反馈，进入限时回应 →';$('begin-timed').hidden=false;$('result-actions').hidden=true}else{$('begin-timed').hidden=true;$('result-actions').hidden=false}tone(523);scrollResult()}
  function respond(follow,timedOut=false){if(state.phase!=='reaction')return;stopTimer();state.phase='playing';if(timedOut)state.timeouts[state.chapter]='reaction';state.followups[state.chapter]=follow.id;if(state.chapter===4)state.feedback=follow.rule;$('result').hidden=true;$('choices').hidden=false;$('choices').replaceChildren();const wait=button('秀秀正在回应…',()=>{},true);wait.disabled=true;$('skip').hidden=false;$('stage-state').textContent='正在演示回应';world.play(follow.id,()=>showResolution(follow));tone(462)}
  function resolution(follow){const m=deriveMemory(),r={title:follow.result,body:follow.body,feedback:follow.feedback};
    if(follow.id==='invite_private'&&m.gift)r.body='邱懿贞自己录音：“我给你留了菜，明天一起去早市吧。”秀秀只发送她说的话，不附设备数据。';
    if(follow.id==='meet_repair'&&state.history[2]==='invite_lie')r.body='邱懿贞点头，承认昨天借故障来邀约。徐月禾放下维修电话，和她商量今天能陪多久。';
    if(follow.id==='tomorrow_wait'&&state.feedback==='keep')r.body='昨天秀秀没有采纳反馈。今天它终于停住等待；徐月禾主动说“帮我一点”后，助力灯才亮。';
    return r}
  function showResolution(follow){state.phase='result';$('choices').hidden=true;$('decision-prompt').hidden=true;$('begin-timed').hidden=true;$('result-actions').hidden=false;$('skip').hidden=true;$('stage-state').textContent='拖动旋转 · 滚轮缩放';$('result').hidden=false;const r=resolution(follow);$('result-title').textContent=(state.timeouts[state.chapter]==='reaction'?'回应超时 · ':'第二步之后 · ')+r.title;$('result-body').textContent=r.body;$('result-feedback').textContent=r.feedback;$('result-actions').replaceChildren();renderMemory(state.chapter);updateNav();
    if(state.chapter<chapters.length-1)button('进入下一幕',()=>{state.maxVisited=state.chapter+1;go(state.chapter+1)},true,$('result-actions'));
    else button('查看本次形成的规则',finish,true,$('result-actions'));
    button('重选这一幕',()=>go(state.chapter),false,$('result-actions'));tone(587);scrollResult()}
  function finish(){stopTimer();state.phase='complete';const h=state.history,f=state.followups,m=deriveMemory(),lines=[];
    chapters.forEach((chapter,i)=>{const first=chapter.choices.find(c=>c.id===h[i]),second=(window.FOLLOWUPS[h[i]]||[]).find(c=>c.id===f[i]);lines.push(String(i+1).padStart(2,'0')+' '+chapter.label+'：'+(state.timeouts[i]?'[超时] ':'')+(first?.label||'未选择')+' → '+(second?.result||'未回应'))});
    lines.push('眼前留下的事实：'+(m.chance?'有人听见邀请的开头':'半句邀请留在路口')+'；'+(m.gift?'她挑的菜可以送给朋友':'那把想送人的菜未被挑成')+'；'+(m.messageTrue?'徐月禾知道真实来意':'徐月禾仍可能把同行当成修理')+'；'+(m.privacy?'披露由她决定':'机器披露了过多信息')+'。');
    lines.push(m.pushRule==='keep'?'坡道反馈仍未成为规则。':m.pushRule?'坡道反馈已被记录为“'+{ask:'先问再推',tell:'助力前告知',limit:'尊重拒绝预防性助力'}[m.pushRule]+'”。':'坡道反馈尚未处理。');
    lines.push(f[5]==='tomorrow_wait'||f[5]==='tomorrow_repair'?'下一次：规则在真实动作里接受了检验。':'下一次：规则仍在文字里，执行时再次偏离。');
    lines.push('安全底线：侧翻、跌倒或突发不适时立即接管。');
    $('chapter-count').textContent='体验结束';$('scene-title').textContent='秀秀留下了什么';$('scene-description').textContent='这不是一张道德分数单。它记录了秀秀先做了什么、看见人的反应后又如何回应，以及下一次有没有照做。';$('scene-dialogue').textContent=f[5]==='tomorrow_wait'||f[5]==='tomorrow_repair'?'徐月禾：累了我会叫你。':'徐月禾：你还记得我昨天说的吗？';$('result').hidden=false;$('result-title').textContent='本次行动记录';$('result-body').textContent=lines.join('\n\n');$('result-body').style.whiteSpace='pre-line';$('result-feedback').textContent='帮助的边界，需要在具体关系中反复确认。';$('result-actions').replaceChildren();button('重新体验',restart,true,$('result-actions'));button('查看角色设定',()=>openGallery(),false,$('result-actions'));$('stage-caption').textContent='两个人停在坡顶；秀秀等待下一次回答。';renderMemory(5);document.querySelector('.story-scroll').scrollTop=0;tone(659)}
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
