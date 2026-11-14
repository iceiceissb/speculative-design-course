const fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict');
const sleep=ms=>new Promise(r=>setTimeout(r,ms));
(async()=>{
  let targets;
  for(let i=0;i<20;i++){try{targets=await fetch('http://127.0.0.1:9226/json').then(r=>r.json());break}catch{await sleep(300)}}
  const ws=new WebSocket(targets.find(x=>x.type==='page').webSocketDebuggerUrl);
  await new Promise(r=>ws.addEventListener('open',r,{once:true}));let id=0;const pending=new Map();
  ws.addEventListener('message',e=>{const d=JSON.parse(e.data);if(d.id){const p=pending.get(d.id);pending.delete(d.id);d.error?p.reject(d.error):p.resolve(d.result)}});
  const call=(method,params={})=>new Promise((resolve,reject)=>{const n=++id;pending.set(n,{resolve,reject});ws.send(JSON.stringify({id:n,method,params}))});
  const evaluate=async expression=>(await call('Runtime.evaluate',{expression,awaitPromise:true,returnByValue:true})).result.value;
  const wait=async expression=>{for(let i=0;i<30;i++){if(await evaluate(expression))return;await sleep(200)}throw Error('Timeout '+expression)};
  await call('Page.enable');await call('Emulation.setDeviceMetricsOverride',{width:1440,height:1080,deviceScaleFactor:1,mobile:false});
  await call('Page.navigate',{url:'http://127.0.0.1:8765'});await wait("document.querySelectorAll('.job').length===4");
  await evaluate("document.querySelector('[data-view=timeline]').click()");
  await evaluate("document.querySelector('tr[data-timeline=\"21\"] input.start').value='6';document.querySelector('button.save-time[data-id=\"21\"]').click()");
  await wait("state.project.timeline[0].source_start===6");
  await evaluate("document.querySelector('#assemble').click()");await wait("document.querySelector('#status').textContent.includes('短于')");
  await sleep(3500);assert.equal(await evaluate("document.querySelector('#status').textContent.includes('短于')"),true);
  await evaluate("document.querySelector('tr[data-timeline=\"21\"] input.start').value='0';document.querySelector('button.save-time[data-id=\"21\"]').click()");
  await wait("state.project.timeline[0].source_start===0");
  const checked={passed:true,invalid_trim_blocked:true,error_visible_after_poll:true,original_timing_restored:true};
  const out=path.resolve(__dirname,'../../output/AI视频工作流/reports');
  fs.writeFileSync(path.join(out,'browser-final-smoke.json'),JSON.stringify(checked,null,2));
  await evaluate("document.querySelector('[data-view=shots]').click()");
  const screenshot=await call('Page.captureScreenshot',{format:'png'});fs.writeFileSync(path.join(out,'选片台_桌面.png'),Buffer.from(screenshot.data,'base64'));
  console.log(JSON.stringify(checked));await call('Browser.close');ws.close();
})().catch(e=>{console.error(e);process.exit(1)});
