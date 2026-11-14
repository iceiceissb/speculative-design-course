import fs from 'node:fs/promises';import path from 'node:path';import vm from 'node:vm';import {pathToFileURL} from 'node:url';
import {chromium} from '../yield-project/node_modules/playwright/index.mjs';
const root=path.resolve('作业二/下一次汇报_剧本与规则/第五版_会协商的医院'),demo=path.join(root,'3D交互短篇'),qa=path.resolve('tmp/hospital-v5/qa');
const ctx={window:{}};vm.runInNewContext(await fs.readFile(path.join(demo,'story.js'),'utf8'),ctx);const story=ctx.window.HOSPITAL_STORY;
let script='# 请等下一班：会协商的医院\n\n第五版完整分支剧本。人物、医院、协议、移动花园均为设计虚构。\n\n林岚，72 岁，复诊结束。她想去七楼花园见朋友，也想看看高处的风景。小椅陪她出发，医院里的设备逐渐加入这次出行。\n\n';
for(let i=0;i<story.length;i++){const c=story[i];script+=`## 第 ${i+1} 幕：${c.title}\n\n${c.caption}\n\n${c.description}\n\n${c.dialogue}\n\n`;for(const v of c.choices){script+=`### 选择：${v.label}\n\n`;for(const [who,line]of v.beats)script+=`${who}：“${line}”\n\n`;script+=`结果：${v.body}\n\n${v.quote}\n\n留给观众的问题：${v.question}\n\n`;}}
script+='## 末幕的实际分支\n\n选择“别存，下次先问我”：新请求出现后保持原位。可以拒绝投影，也可以只开启这一次。\n\n选择保存：沿用第三幕的投影开关状态。没有体验第三幕时，以开启投影作为示例设置。可以立即叫停，也可以本次继续，之后仍能撤回。\n\n重启或刷新清除本次体验的选择。本作品不将这些选择保存为实际个人档案。\n';await fs.writeFile(path.join(root,'作品剧本与交互分支.md'),script);
const browser=await chromium.launch({executablePath:'C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe',headless:true,args:['--enable-unsafe-swiftshader']});
const page=await browser.newPage({viewport:{width:1586,height:992},deviceScaleFactor:1});await page.goto(pathToFileURL(path.join(demo,'index.html')).href);await page.waitForFunction(()=>!!window.hospitalDemo);await page.waitForTimeout(250);
await page.screenshot({path:path.join(qa,'native-concept-size.png')});await page.screenshot({path:path.join(root,'视觉设定/3D实际界面.png')});
await page.evaluate(()=>{hospitalDemo.scene(2);hospitalDemo.choose(hospitalDemo.story[2].choices[1]);hospitalDemo.stage.skip();});const before=await page.evaluate(()=>hospitalDemo.stage.river.visible);await page.evaluate(()=>hospitalDemo.stage.tick(8.1));const after=await page.evaluate(()=>hospitalDemo.stage.river.visible);if(!before||after)throw Error('delayed light extinction failed');
await browser.close();console.log('Story and native viewport exported; delayed light extinction passed.');
