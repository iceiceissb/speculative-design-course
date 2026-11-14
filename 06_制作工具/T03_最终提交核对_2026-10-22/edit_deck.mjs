import fs from 'node:fs/promises';
import path from 'node:path';
import {pathToFileURL,fileURLToPath} from 'node:url';
const {FileBlob,PresentationFile}=await import(pathToFileURL('C:/Users/22602/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/@oai/artifact-tool/dist/artifact_tool.mjs'));
const root='D:/课/大四上/思辨设计';
const work=path.dirname(fileURLToPath(import.meta.url));
const source=path.join(root,'05_汇报与成片/04_最终提交作业/不用麻烦她_最终结课汇报.pptx');
const p=await PresentationFile.importPptx(await FileBlob.load(source));
const all=await p.inspect({kind:'textbox',maxChars:100000});
const changes=[];
const replacements=[
 ['4分32秒','4分37秒'],['V01成片','V02成片'],
 ['以 S35 v9 的可见动作作为判断依据','按当前V02影片中的可见动作核对'],
 ['下一步：使用者参与测试，\n把“错标—纠正—复测”\n补成可操作的交互分支。','下一步：邀请真实使用者试玩，\n检验拒绝与反馈是否清楚，\n再扩展错标和复测交互。']
];
for(const r of all.records){
 for(const [before,after] of replacements){
  if(r.text?.includes(before)){p.resolve(r.id).text.replace(before,after);changes.push({slide:r.slideIndex+1,before,after});}
 }
}
const tables=await p.inspect({kind:'table',maxChars:12000});
function cell(slide,row,col,text){
 const rec=tables.records.find(x=>x.slideIndex===slide-1);if(!rec)throw Error('Missing table on slide '+slide);
 p.resolve(rec.id).cells.set(row,col,text);changes.push({slide,row,col,text});
}
cell(12,1,1,'共享记录时点按允许；\n报修前问“要报吗？”');
cell(12,1,2,'涉及新的提交，先取得确认。');
cell(17,0,2,'实际实现');
cell(17,0,3,'脚本模拟与边界');
cell(17,1,3,'障碍由场景预设；\n没有实物感知验证。');
cell(17,2,2,'确认后进入待处理；\n拒绝后继续行程。');
cell(17,2,3,'办完任务后触发修复；\n没有真实政务接口。');
cell(17,3,0,'反馈后的变化');
cell(17,3,2,'返程看道路变化；\n保存照片与地点状态。');
cell(17,3,3,'固定规则更新状态；\n没有模型自主学习。');
cell(18,2,1,'ImageGen；Seedance 2.5 API\n生成参考图及逐镜视频。');
cell(18,3,1,'剪映Skill；FFmpeg\nReal-ESRGAN；本地语音识别。');
cell(18,3,2,'提出节奏、声音与片尾要求；\n审阅后决定重生成和剪辑调整。');
const output=path.join(work,'不用麻烦她_最终结课汇报_修订.pptx');
const blob=await PresentationFile.exportPptx(p);
await blob.save(output);
const render=path.join(work,'PPT修改后');await fs.mkdir(render,{recursive:true});
for(let i=0;i<p.slides.items.length;i++){
 const img=await p.export({slide:p.slides.items[i],format:'png',scale:.7});
 await fs.writeFile(path.join(render,`slide-${i+1}.png`),new Uint8Array(await img.arrayBuffer()));
}
await fs.writeFile(path.join(work,'PPT改动记录.json'),JSON.stringify({engine:'@oai/artifact-tool file workflow; live module import rejected node:process',slides:p.slides.items.length,output,changes},null,2));
console.log(JSON.stringify({output,slides:p.slides.items.length,changedSlides:[...new Set(changes.map(c=>c.slide))],changes:changes.length}));
