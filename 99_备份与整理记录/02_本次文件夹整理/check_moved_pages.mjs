import {chromium} from '../../90_历史工程与旧提交/01_整理前原目录/output/最终作业_不用麻烦她_3D交互原型/.ppt_build/node_modules/playwright/index.mjs';
import fs from 'node:fs';
import path from 'node:path';
import {pathToFileURL} from 'node:url';
import {spawn} from 'node:child_process';
import net from 'node:net';
const root=process.cwd();
const record=path.join(root,'99_备份与整理记录/02_本次文件夹整理');
const catalog=JSON.parse(fs.readFileSync(path.join(record,'版本总表_新路径.json'),'utf8'));
const browser=await chromium.launch({executablePath:'C:/Program Files/Google/Chrome/Application/chrome.exe',headless:true,args:['--enable-unsafe-swiftshader']});
const report={pages:[],tools:[]};
const children=[];
async function freePort(){return new Promise((resolve,reject)=>{const s=net.createServer();s.once('error',reject);s.listen(0,'127.0.0.1',()=>{const p=s.address().port;s.close(()=>resolve(p))})})}
async function waitHttp(url,child){for(let i=0;i<60;i++){if(child.exitCode!==null)throw new Error('Local tool exited before HTTP was ready');try{const r=await fetch(url);if(r.ok)return}catch{}await new Promise(r=>setTimeout(r,200))}throw new Error('Local tool did not start')}
try{
 for(const v of catalog.filter(v=>v.category==='Demo'||v.id==='F07')){
  const p=await browser.newPage({viewport:{width:1366,height:900}}),errors=[],failed=[];
  p.on('pageerror',e=>errors.push(e.message));p.on('requestfailed',r=>failed.push(r.url()));
  await p.goto(pathToFileURL(path.join(root,v.target)).href);await p.waitForTimeout(500);
  const state=await p.evaluate(()=>({title:document.title,text_length:document.body.innerText.length,canvas_count:document.querySelectorAll('canvas').length,demo_ready:!!window.xiuxiuDemo}));
  if(v.id==='D07'&&!state.demo_ready)errors.push('Demo 初始化失败');
  report.pages.push({id:v.id,path:v.target,...state,errors,failed_requests:failed});
  console.log(v.id,'errors',errors.length,'failed',failed.length);await p.close();
 }
 for(const spec of [{id:'T01',folder:'06_制作工具/T01_AI视频工作流',args:['workflow.py','serve']},{id:'T02',folder:'06_制作工具/T02_Bodystorming_Agent',args:['server.py','--no-browser','--data-dir',path.join(record,'验收临时数据/bodystorm')]}]){
  const port=await freePort();
  const child=spawn('python',['-X','utf8',...spec.args,'--port',String(port)],{cwd:path.join(root,spec.folder),windowsHide:true,env:{...process.env,PYTHONIOENCODING:'utf-8'},stdio:['ignore','pipe','pipe']});
  children.push(child);let stderr='';child.stderr.on('data',b=>{stderr+=String(b)});child.stdout.on('data',()=>{});
  const url=`http://127.0.0.1:${port}/`;await waitHttp(url,child);
  const p=await browser.newPage(),errors=[],failed=[];
  p.on('pageerror',e=>errors.push(e.message));p.on('requestfailed',r=>failed.push(r.url()));
  await p.goto(url);await p.waitForTimeout(700);
  const state=await p.evaluate(()=>({title:document.title,text_length:document.body.innerText.length}));
  if(state.text_length<50)errors.push('正文过少');
  report.tools.push({id:spec.id,path:spec.folder,...state,errors,failed_requests:failed,real_model_called:false});
  console.log(spec.id,'HTTP loaded','errors',errors.length,'failed',failed.length);await p.close();child.kill();
 }
}finally{
 for(const child of children)if(child.exitCode===null)child.kill();
 await browser.close();fs.writeFileSync(path.join(record,'移动后浏览器检查.json'),JSON.stringify(report,null,2));
}
if([...report.pages,...report.tools].some(p=>p.errors.length||p.failed_requests.length))process.exitCode=1;
