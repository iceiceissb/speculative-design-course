import {chromium} from '../output/最终作业_不用麻烦她_3D交互原型/.ppt_build/node_modules/playwright/index.mjs';
import path from 'node:path';
import {pathToFileURL} from 'node:url';

const root=path.resolve('output/最终作业_不用麻烦她_3D交互原型');
const browser=await chromium.launch({executablePath:'C:/Program Files/Google/Chrome/Application/chrome.exe',headless:true,args:['--enable-unsafe-swiftshader']});
const page=await browser.newPage({viewport:{width:1500,height:950}});
const errors=[];page.on('pageerror',e=>errors.push(e.message));
await page.goto(pathToFileURL(path.join(root,'index.html')).href);
await page.waitForFunction(()=>Boolean(window.xiuxiuDemo));
async function act(label){await page.locator('#choices button', {hasText:label}).first().click();await page.evaluate(()=>xiuxiuDemo.world.skip());}
async function react(label){await page.locator('#result-actions button', {hasText:label}).first().click();await page.evaluate(()=>xiuxiuDemo.world.skip());}
async function next(){await page.getByRole('button',{name:'进入下一幕'}).click();}
async function begin(){if(await page.locator('#begin-timed').isVisible())await page.locator('#begin-timed').click();}
function check(ok,message){if(!ok)throw new Error(message);}

await begin();await act('停一下');await react('轻声问');await next();
await begin();await act('报出价格');await react('等她选完');await next();
await act('如实说明');await react('只发送她亲口');await next();
await act('不代答');await react('等双方说完');await next();
await begin();await act('暗中补');await begin();await react('承认助力');
check(await page.evaluate(()=>xiuxiuDemo.deriveMemory(4).pushRule==='tell'),'坡道反馈没有写入规则');
await page.screenshot({path:path.resolve('tmp/final_demo_feedback.png'),fullPage:true});
await next();
check((await page.locator('#choices').innerText()).includes('先说明，等她求助'),'下一次选项没有采用已记录的规则');
await begin();await act('应用反馈');
check(!(await page.evaluate(()=>xiuxiuDemo.world.snapshot().assist)),'人未求助前助力灯应关闭');
const waitingPose=await page.evaluate(()=>xiuxiuDemo.world.snapshot());
await react('持续等待');
check(await page.evaluate(()=>xiuxiuDemo.world.snapshot().assist),'明确求助后助力灯应亮起');
check(await page.evaluate(z=>xiuxiuDemo.world.snapshot().chair[2]>z,waitingPose.chair[2]),'求助后轮椅应继续上坡');
check(await page.evaluate(()=>xiuxiuDemo.world.audit().pusherBehind),'推行者应位于轮椅后方');
check(await page.locator('#final-summary').isVisible(),'最后一幕结束后应自动显示规则总结');
check((await page.locator('#final-status').innerText())==='反馈已落实','采纳分支的总结状态不正确');
check((await page.locator('#final-loop-steps').innerText()).includes('助力灯才亮'),'结尾没有说明反馈怎样改变动作');
check((await page.locator('#final-rule-items .final-rule').count())===4,'结尾应总结前四幕的行动原则');
check((await page.locator('#final-trace-items li').count())===6,'选择记录应覆盖六幕');
await page.screenshot({path:path.resolve('tmp/final_demo_adjusted.png'),fullPage:true});
await page.setViewportSize({width:390,height:844});
check(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth),'手机视口出现横向溢出');
await page.screenshot({path:path.resolve('tmp/final_demo_mobile.png'),fullPage:true});
await page.setViewportSize({width:1500,height:950});
await page.getByRole('button',{name:'重选下一次，比较另一种结果'}).click();
await begin();await act('仍沿用原来的省力策略');await react('坚持原策略');
check((await page.locator('#final-status').innerText())==='反馈仍未落实','忽略反馈分支的总结状态不正确');
check((await page.locator('#final-loop-steps').innerText()).includes('继续自动驶完'),'忽略反馈分支没有显示实际动作');
await page.screenshot({path:path.resolve('tmp/final_demo_missed.png'),fullPage:true});
await page.getByRole('button',{name:'重选下一次，比较另一种结果'}).click();
await begin();await act('仍沿用原来的省力策略');await react('承认没有采纳');
check((await page.locator('#final-status').innerText())==='今天才补救','迟到纠错分支的总结状态不正确');
check((await page.locator('#final-loop-steps').innerText()).includes('停下承认错误'),'迟到纠错分支没有说明实际动作');
await page.evaluate(()=>{xiuxiuDemo.state.history[4]='slope_auto';xiuxiuDemo.state.followups[4]='slope_stop';xiuxiuDemo.state.history[5]='tomorrow_update';xiuxiuDemo.state.followups[5]='tomorrow_wait';xiuxiuDemo.finish()});
check((await page.locator('#final-verdict').innerText()).includes('下次先问我'),'坡道不同反馈应形成不同的总结标题');
check(errors.length===0,'浏览器运行错误：'+errors.join('；'));
console.log(JSON.stringify({passed:true,checks:['反馈写入规则','下一次选项改变','求助前灯关闭','求助后灯亮起并继续上坡','结尾自动生成四项行动原则与六幕记录','重选后显示反馈未落实','迟到纠错分支可见','不同反馈生成对应标题','手机无横向溢出','无脚本错误']},null,2));
await browser.close();
