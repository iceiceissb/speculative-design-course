import {chromium} from 'playwright';import path from 'node:path';import {pathToFileURL} from 'node:url';
const root=path.resolve('作业二/提交_请别替我让路/3D交互原型');
const b=await chromium.launch({executablePath:'C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe',headless:true,args:['--enable-unsafe-swiftshader']});
const p=await b.newPage({viewport:{width:1505,height:1045}});await p.goto(pathToFileURL(path.join(root,'index.html')).href);await p.waitForTimeout(400);
await p.evaluate(()=>{const el=document.querySelector('.stage-wrap');el.style.width='680px';el.style.height='700px';document.getElementById('labels').style.display='none';document.getElementById('scene-note').style.display='none';});await p.waitForTimeout(200);
await p.evaluate(()=>{const s=__app.stage;const c=s.camera;c.left=-3.8;c.right=3.8;c.top=3.91;c.bottom=-3.91;c.position.set(1,6,11);c.lookAt(1.1,.6,0);c.updateProjectionMatrix();s.render();});await p.locator('.stage-wrap').screenshot({path:path.join(root,'assets/cover-hero.png')});
await p.reload();await p.setViewportSize({width:390,height:844});await p.waitForTimeout(300);await p.locator('[data-action=start]').click();await p.locator('[data-action=interrupt]').click();await p.screenshot({path:'tmp/yield-project/qa/mobile-choice-final.png',fullPage:true});console.log('CAPTURED');await b.close();
