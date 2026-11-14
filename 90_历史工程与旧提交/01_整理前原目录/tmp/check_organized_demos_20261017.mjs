import {chromium} from '../output/最终作业_不用麻烦她_3D交互原型/.ppt_build/node_modules/playwright/index.mjs';
import fs from 'node:fs';
import path from 'node:path';
import {pathToFileURL} from 'node:url';

const root=process.cwd();
const records=path.join(root,'创作工作区/99_整理记录');
const versions=JSON.parse(fs.readFileSync(path.join(records,'版本总表.json'),'utf8'));
const browser=await chromium.launch({executablePath:'C:/Program Files/Google/Chrome/Application/chrome.exe',headless:true,args:['--enable-unsafe-swiftshader']});
const result={date:'2026-10-17',scope:'复制后的入口加载与本地依赖检查，不重做旧版本全部分支测试',pages:[]};
try{
  const main=await browser.newPage({viewport:{width:1440,height:1000}});
  const errs=[];main.on('pageerror',e=>errs.push(e.message));
  await main.goto(pathToFileURL(path.join(root,'00_打开工作区.html')).href);
  if(await main.locator('article').count()!==51)throw new Error('导航档案数量不对');
  await main.getByRole('button',{name:'Demo',exact:true}).click();
  if(await main.locator('article:visible').count()!==7)throw new Error('Demo 筛选不对');
  await main.locator('#search').fill('不用麻烦她');
  if(await main.locator('article:visible').count()!==2)throw new Error('组合搜索不对');
  await main.locator('#search').fill('');
  await main.getByRole('button',{name:'全部',exact:true}).click();
  await main.screenshot({path:path.join(records,'工作区导航_桌面.png'),fullPage:true});
  await main.setViewportSize({width:390,height:844});
  if(!await main.evaluate(()=>document.documentElement.scrollWidth<=innerWidth))throw new Error('导航移动端溢出');
  await main.screenshot({path:path.join(records,'工作区导航_手机.png'),fullPage:true});
  result.navigation={entries:51,demo_filter:7,combined_search:2,mobile_overflow:false,page_errors:errs};
  await main.close();
  for(const v of versions.filter(v=>v.category==='Demo'||v.id==='F07')){
    const page=await browser.newPage({viewport:{width:1440,height:950}});
    const errors=[],failed=[];
    page.on('pageerror',e=>errors.push(e.message));
    page.on('requestfailed',r=>failed.push({url:r.url(),failure:r.failure()?.errorText}));
    await page.goto(pathToFileURL(path.join(root,v.target)).href);
    await page.waitForTimeout(900);
    const info=await page.evaluate(()=>({title:document.title,body_text:document.body.innerText.trim().length,canvases:[...document.querySelectorAll('canvas')].map(c=>({width:c.width,height:c.height})),demo_ready:Boolean(window.xiuxiuDemo)}));
    if(info.body_text<50)errors.push('页面正文过少');
    if(v.id==='D07'&&!info.demo_ready)errors.push('xiuxiuDemo 没有初始化');
    if(v.id==='D07')await page.screenshot({path:path.join(records,'D07_归档入口.png'),fullPage:true});
    result.pages.push({id:v.id,path:v.target,...info,errors,failed_requests:failed});
    console.log(v.id,info.title,'errors',errors.length,'requests_failed',failed.length);
    await page.close();
  }
}finally{
  await browser.close();
  fs.writeFileSync(path.join(records,'浏览器入口检查.json'),JSON.stringify(result,null,2));
}
if(result.pages.some(p=>p.errors.length)||result.navigation.page_errors.length)process.exitCode=1;
