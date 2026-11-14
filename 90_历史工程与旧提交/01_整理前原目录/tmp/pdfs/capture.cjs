const {chromium}=require('C:/Users/22602/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
const fs=require('fs');
(async()=>{const dir='D:/课/大四上/思辨设计/tmp/pdfs';fs.mkdirSync(dir,{recursive:true});const browser=await chromium.launch({channel:'msedge',headless:true});const page=await browser.newPage({viewport:{width:1200,height:800},deviceScaleFactor:1.5});
for(const [name,url,label] of [['clara','https://clararobot.github.io/','Failure Cases'],['teacher','https://www.simonerebaudengo.com/teacher','IN A NUTSHELL']]){try{await page.goto(url,{waitUntil:'domcontentloaded',timeout:25000});await page.waitForTimeout(1800);const h=page.getByRole('heading',{name:label,exact:true});if(await h.count())await h.scrollIntoViewIfNeeded();await page.screenshot({path:dir+'/'+name+'.png'});console.log(name+' captured');}catch(e){console.log(name+': '+e.message.slice(0,180));}}
await browser.close();})();
