(() => {
 'use strict';
 const $=id=>document.getElementById(id),story=window.HOSPITAL_STORY;
 const state={chapter:0,phase:'choice',history:{},preference:null,nextConsent:null,muted:true};
 let stage;
 class Soundtrack{
  constructor(){this.enabled=false;this.ctx=null;this.gain=null;this.voices=[];}
  async enable(v){this.enabled=v;if(v){if(!this.ctx){this.ctx=new (window.AudioContext||window.webkitAudioContext)();this.gain=this.ctx.createGain();this.gain.gain.value=.17;this.gain.connect(this.ctx.destination);}await this.ctx.resume();this.note(440,.1);}else{if(this.gain)this.gain.gain.cancelScheduledValues(this.ctx.currentTime);window.speechSynthesis?.cancel();}if(this.gain)this.gain.gain.value=v?.17:0;}
  note(freq,duration=.3,offset=0){if(!this.enabled||!this.ctx)return;const t=this.ctx.currentTime+offset,o=this.ctx.createOscillator(),g=this.ctx.createGain();o.type='sine';o.frequency.value=freq;g.gain.setValueAtTime(0,t);g.gain.linearRampToValueAtTime(.24,t+.03);g.gain.exponentialRampToValueAtTime(.001,t+duration);o.connect(g);g.connect(this.gain);o.start(t);o.stop(t+duration+.03);}
  speak(who,line,index){if(!this.enabled)return;this.note([330,392,440,523.25][index%4],.23);if(state.chapter===2&&state.history[2]==='music')[0,4,7,12].forEach((n,i)=>this.note(261.63*Math.pow(2,n/12),.42,i*.14));if('speechSynthesis'in window){window.speechSynthesis.cancel();const u=new SpeechSynthesisUtterance(line);u.lang='zh-CN';u.rate=who==='A 梯'?1.14:who==='B 梯'?.86:1;u.pitch=who==='小椅'?1.2:who==='林岚'?.92:1;u.volume=.7;const voice=window.speechSynthesis.getVoices().find(v=>v.localService&&/^zh[-_]/i.test(v.lang));if(voice){u.voice=voice;window.speechSynthesis.speak(u);};}}
  cancel(){window.speechSynthesis?.cancel();}
 }
 const sound=new Soundtrack();
 function button(label,fn,primary=true,id=''){const b=document.createElement('button');b.className=primary?'primary':'secondary';b.textContent=label;if(id)b.dataset.action=id;b.addEventListener('click',fn);$('actions').append(b);return b;}
 function nav(){[...$('chapters').children].forEach((b,i)=>{b.classList.toggle('active',i===state.chapter);b.classList.toggle('done',state.history[i]!==undefined);if(i===state.chapter)b.setAttribute('aria-current','step');else b.removeAttribute('aria-current');});}
 function motionUI(active){$('pause').disabled=!active;$('pause').querySelector('span').textContent='暂停';$('pause').setAttribute('aria-label','暂停动画');$('skip').hidden=!active;$('motion-label').textContent=active?'拖动查看 · 动画播放中':'拖动旋转 · 滚轮缩放';}
 function scene(i){sound.cancel();state.chapter=i;state.phase='choice';state.nextConsent=null;stage.reset(i);$('camera').querySelector('span').textContent='全景视角';if(i!==5)state.preference=null;const c=story[i];$('heading').textContent=c.title;$('description').textContent=c.description;$('dialogue').textContent=c.dialogue;$('chapter-count').textContent=String(i+1).padStart(2,'0')+' / 06';$('scene-caption').textContent=c.caption;$('reflection').hidden=true;$('replay').hidden=true;$('actions').replaceChildren();$('speaker-bubble').classList.remove('active');motionUI(false);c.choices.forEach((v,n)=>button(v.label,()=>choose(v),n===0,v.id));nav();}
 function beat(lines,index){$('dialogue').textContent=lines[0]+'：'+lines[1];$('speaker-bubble').textContent=lines[0]+'：'+lines[1];$('speaker-bubble').classList.add('active');sound.speak(lines[0],lines[1],index);}
 function choose(choice){if(state.phase!=='choice')return;state.phase='playing';state.history[state.chapter]=choice.id;if(state.chapter===5)state.preference=choice.id;nav();$('actions').replaceChildren();const b=button('正在发生…',()=>{},true);b.disabled=true;$('replay').hidden=true;motionUI(true);stage.play(choice.id,choice.beats,beat,()=>result(choice),{projection:state.history[2]!=='quiet'});}
 function result(c){state.phase='result';motionUI(false);$('speaker-bubble').classList.remove('active');$('heading').textContent=c.result;$('description').textContent=c.body;$('dialogue').textContent=c.quote;$('reflection').textContent=c.question;$('reflection').hidden=false;$('actions').replaceChildren();$('replay').hidden=false;
  if(state.chapter<5){button('下一幕',()=>scene(state.chapter+1),true,'next');}
  else if(c.id==='ask'){button('今天不想开投影',()=>respond(false),true,'refuse');button('今天可以开一次',()=>respond(true),false,'once');}
  else{if(state.history[2]==='quiet'){$('heading').textContent='下一次，它自动保持安静';$('description').textContent='小椅记住了今天关闭投影的选择。下一次仍然安静，但今天也许想和大家玩一下。';$('dialogue').textContent='林岚：今天可以换一种吗？';}button('叫停，改为每次先问',revoke,true,'revoke');button('这次继续用这个设置',()=>finish('保留设置，仍可随时撤回','小椅会沿用已保存的投影偏好。你仍然可以叫停，改为重新询问。'),false,'keep');}
 }
 function respond(yes){state.nextConsent=yes;state.preference='ask';if(yes){stage.river.visible=true;stage.musicAmount=1;stage.notes.forEach(n=>n.material.opacity=.8);stage.padAmount=1;stage.pads[0].visible=true;sound.note(523,.4);}else stage.revoke();finish(yes?'只答应这一次':'这一次，安静经过',yes?'林岚打开了今天的投影。下次仍然需要重新询问。':'投影保持关闭，轮椅留在原位。没有把上一次的选择当作这一次的答案。');}
 function revoke(){state.preference='ask';state.nextConsent=false;stage.revoke();sound.cancel();finish('安排撤回了','投影和自动安排已停止。下一次重新询问，今天的选择没有变成长期义务。');}
 function finish(title,body){state.phase='complete';$('heading').textContent=title;$('description').textContent=body;$('dialogue').textContent='林岚：别存。下次先问我。';$('reflection').textContent='她想要的帮助，可以由她重新决定。';$('actions').replaceChildren();button('重新体验这一天',restart,true,'restart');if(state.preference==='remember')button('撤回偏好',revoke,false,'revoke');else button('回到最后的选择',()=>scene(5),false,'last');$('replay').hidden=true;}
 function restart(){state.history={};state.preference=null;state.nextConsent=null;scene(0);}
 story.forEach((c,i)=>{let b=document.createElement('button');b.innerHTML='<span class="num">'+String(i+1).padStart(2,'0')+'</span><span>'+c.title+'</span>';b.addEventListener('click',()=>scene(i));b.dataset.chapter=i;$('chapters').append(b);});
 $('sound').addEventListener('click',async()=>{state.muted=!state.muted;try{await sound.enable(!state.muted);}catch(e){state.muted=true;}const b=$('sound');b.setAttribute('aria-pressed',String(!state.muted));b.querySelector('span').textContent=state.muted?'声音关闭':'声音开启';});
 $('camera').addEventListener('click',()=>{if(!stage)return;stage.setView((stage.view+1)%3);$('camera').querySelector('span').textContent=['全景视角','乘坐视角','俯视视角'][stage.view];});
 $('restart').addEventListener('click',()=>{if(stage)restart();});$('replay').addEventListener('click',()=>scene(state.chapter));
 $('pause').addEventListener('click',()=>{if(!stage.running)return;stage.paused=!stage.paused;$('pause').querySelector('span').textContent=stage.paused?'继续':'暂停';$('pause').setAttribute('aria-label',stage.paused?'继续动画':'暂停动画');$('motion-label').textContent=stage.paused?'已暂停 · 可以旋转查看':'拖动查看 · 动画播放中';if(stage.paused)window.speechSynthesis?.pause();else window.speechSynthesis?.resume();});
 $('skip').addEventListener('click',()=>{sound.cancel();stage.skip();});
 document.addEventListener('visibilitychange',()=>{if(document.hidden&&stage?.running&&!stage.paused)$('pause').click();});
 try{stage=new HospitalStage($('world'));scene(0);window.hospitalDemo={state,stage,scene,restart,choose,sound,story};}catch(e){$('webgl-error').hidden=false;console.error(e);}
})();
