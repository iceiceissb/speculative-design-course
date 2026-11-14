(()=>{'use strict';
const $=id=>document.getElementById(id),clips=window.VIDEO_CLIPS||[],timeline=window.VIDEO_TIMELINE||[],key='xiuxiu-video-clips-v1';
let done={};try{done=JSON.parse(localStorage.getItem(key)||'{}')}catch{}
const safe=s=>String(s).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));
function frameHTML(frame,type){return `<figure><img src="${encodeURI(frame.file)}" alt="${safe(frame.number+' '+type)}" data-file="${safe(frame.file)}"><figcaption>${safe(frame.number)} ${type}</figcaption></figure>`}
function copy(value,button){const old=button.textContent;function ok(){button.textContent='已复制';setTimeout(()=>button.textContent=old,1300)}function fallback(){const el=document.createElement('textarea');el.value=value;document.body.append(el);el.select();try{document.execCommand('copy');ok()}finally{el.remove()}}if(navigator.clipboard&&window.isSecureContext)navigator.clipboard.writeText(value).then(ok).catch(fallback);else fallback()}
function renderTimeline(){const target=$('timeline');target.innerHTML=timeline.map(s=>`<a class="timeline-shot${s.pov?' pov':''}" href="#clip-${safe(s.task)}" title="${safe(s.scene+' · '+s.title)}"><img loading="lazy" src="${encodeURI(s.file)}" alt="${safe(s.number+' '+s.title)}"><span>${safe(s.start)}–${safe(s.end)}</span><b>${safe(s.number)} ${safe(s.title)}</b>${s.pov?'<em>主观视角</em>':''}</a>`).join('');target.addEventListener('click',e=>{const link=e.target.closest('a[href^="#clip-"]');if(!link)return;e.preventDefault();$('scene-filter').value='';$('status-filter').value='';$('search').value='';render();document.querySelector(link.getAttribute('href'))?.scrollIntoView({behavior:'smooth',block:'start'})})}
function render(){
  const scene=$('scene-filter').value,status=$('status-filter').value,q=$('search').value.trim().toLowerCase(),target=$('clips');target.replaceChildren();let count=0;
  clips.forEach((c,i)=>{
    if(scene&&c.scene!==scene)return;if(status==='todo'&&done[c.id])return;if(status==='done'&&!done[c.id])return;if(q&&!`${c.id} ${c.title} ${c.prompt} ${c.dialogue.join(' ')} ${c.bridge||''}`.toLowerCase().includes(q))return;count++;
    const card=document.createElement('article');card.className='clip'+(done[c.id]?' completed':'');card.id='clip-'+c.id;
    const frames=c.frames.map((f,j)=>frameHTML(f,c.frames.length===2?(j===0?'首帧':'尾帧'):'参考帧')).join('');
    const lines=c.dialogue.length?c.dialogue.map(x=>`<p>${safe(x)}</p>`).join(''):'<p class="silent">这一段不加对白，保留环境与动作声。</p>';
    const overlays=c.overlays.length?c.overlays.map(x=>`<p>画面文字：${safe(x)}</p>`).join(''):'';
    card.innerHTML=`<div><div class="clip-head"><span class="serial">${String(i+1).padStart(2,'0')} / ${clips.length}</span><span class="pill ${c.kind==='首尾帧'?'paired':''}">${safe(c.kind)}</span><span class="pill">${safe(c.scene)}</span><span class="pill">生成约 ${c.duration} 秒</span></div><h2>${safe(c.title)}</h2><p class="timecodes">剪映位置：${safe(c.timecodes.join('，'))}</p><div class="frames" style="--frames:${c.frames.length}">${frames}</div><p class="edit">${safe(c.edit)}${c.insert?' · 中插：'+safe(c.insert):''}</p>${c.bridge?`<p class="bridge"><b>镜头接力：</b>${safe(c.bridge)}</p>`:''}</div><div class="clip-right"><p class="label">即梦｜复制整段提示词，音效已包含</p><div class="prompt">${safe(c.prompt)}</div><div class="post"><p class="sub">剪映｜后配台词与画面文字</p>${lines}${overlays}</div><div class="actions"><button type="button" data-action="prompt">复制即梦提示词</button><button type="button" data-action="dialogue">复制剪映内容</button><button type="button" data-action="done" class="${done[c.id]?'done':''}">${done[c.id]?'✓ 已生成':'标记已生成'}</button></div></div>`;
    card.querySelectorAll('[data-file]').forEach(img=>img.addEventListener('click',()=>{const d=$('lightbox');$('large-image').src=img.src;$('large-image').alt=img.alt;$('large-caption').textContent=img.alt;d.showModal()}));
    card.querySelector('[data-action=prompt]').onclick=e=>copy(c.prompt,e.currentTarget);
    card.querySelector('[data-action=dialogue]').onclick=e=>copy([...c.dialogue,...c.overlays].join('\n')||'本段无台词，保留环境与动作音。',e.currentTarget);
    card.querySelector('[data-action=done]').onclick=()=>{done[c.id]=!done[c.id];localStorage.setItem(key,JSON.stringify(done));render()};target.append(card)
  });
  $('empty').hidden=count>0;const n=clips.filter(c=>done[c.id]).length;$('progress-text').textContent=n+' / '+clips.length;$('progress-fill').style.width=(n/clips.length*100)+'%'
}
['scene-filter','status-filter','search'].forEach(id=>$(id).addEventListener(id==='search'?'input':'change',render));$('close').onclick=()=>$('lightbox').close();$('lightbox').onclick=e=>{if(e.target===$('lightbox'))$('lightbox').close()};renderTimeline();render();
})();
