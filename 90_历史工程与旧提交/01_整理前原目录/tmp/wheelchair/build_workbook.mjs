import fs from 'node:fs/promises';
import path from 'node:path';
import {Workbook,SpreadsheetFile} from '@oai/artifact-tool';
const root='D:/课/大四上/思辨设计';
const out=path.join(root,'output/作业一_智能轮椅');
const data=JSON.parse(await fs.readFile(path.join(out,'研究底稿/专题数据.json'),'utf8'));
const wb=Workbook.create();
const cols=n=>{let s='';for(;n;n=Math.floor((n-1)/26))s=String.fromCharCode(65+(n-1)%26)+s;return s;};
const tables=[
 ['核心案例',data.cases,[11,12,37,24,20,23,43,54,47,57,54,42,68,16]],
 ['筛选台账',data.audits,[13,58,27,24,24,70,15,75]],
 ['来源归并',data.sources,[13,13,65,25,44,80]],
 ['检索记录',data.queries,[13,18,25,95,32,65]],
];
for(const [name,rows,widths] of tables){
 const sh=wb.worksheets.add(name);sh.showGridLines=false;
 const headers=Object.keys(rows[0]);const values=[headers,...rows.map(r=>headers.map(k=>['核查日期','执行日期'].includes(k)?new Date(`${r[k]}T00:00:00Z`):r[k]))];
 const area=sh.getRange(`A1:${cols(headers.length)}${values.length}`);area.values=values;
 area.format.font={name:'Microsoft YaHei',size:11,color:'#24343D'};area.format.wrapText=true;area.format.verticalAlignment='top';
 const head=sh.getRange(`A1:${cols(headers.length)}1`);head.format.fill='#416B72';head.format.font={name:'Microsoft YaHei',size:11,bold:true,color:'#FFFFFF'};head.format.rowHeight=34;
 for(let j=0;j<headers.length;j++)sh.getRange(`${cols(j+1)}1:${cols(j+1)}${values.length}`).format.columnWidth=widths[j]??35;
 for(let i=2;i<=values.length;i++){
  const r=sh.getRange(`A${i}:${cols(headers.length)}${i}`);r.format.rowHeight=name==='核心案例'?86:name==='筛选台账'?72:62;
  if(i%2===0)r.format.fill='#F0F4F3';
 }
 sh.freezePanes.freezeRows(1);
 for(let j=0;j<headers.length;j++)if(['核查日期','执行日期'].includes(headers[j]))sh.getRange(`${cols(j+1)}2:${cols(j+1)}${values.length}`).setNumberFormat('yyyy-mm-dd');
 const tbl=sh.tables.add(`A1:${cols(headers.length)}${values.length}`,true,`Evidence${tables.findIndex(x=>x[0]===name)+1}`);tbl.showFilterButton=true;
}
const sh=wb.worksheets.add('方法与计数');sh.showGridLines=false;
const rows=[['口径','数量／说明'],['既有目的性种子来源',14],['补充来源记录',11],['保存的来源总数',null],['完全重复',0],['同项目来源归并',3],['进入候选初筛',null],['初筛排除：理论、综述或框架',4],['拟核查来源的候选',null],['未取得足够原文',2],['完成来源适配性评估',null],['评估后排除',4],['纳入核心案例',null],['纳入案例对应来源记录',15],['主库更新','260条＋8项新候选＝268条；不是268项都已重筛。'],['种子选择','从260条既有库目的性选取14条；不声称全库系统筛选。'],['反馈编码','F0：无足够行为改变证据；F1：当次调整或设置改变；F2：反馈进入后续记忆或策略。'],['分组','A共享行动决定4例；B承认局限并澄清2例；C尊重身体与信息边界3例；D接受纠正并验证改变3例。'],['来源类型','产品手册说明功能；研究按方法与样本限定。W09为在线书面情境，不能写成部署效果。'],['方法限制','9条实际Web查询；不统计搜索引擎总命中，无数据库全量导出、双人独立复核或用户实验。'],['AI使用','Codex辅助检索、核查、编码与排版；未用AI生成图片冒充真实案例。'],['原始资料','核查日期2026-09-18。来源链接在核心案例、筛选台账与来源归并对应行。'],['PRISMA说明','本作业参照PRISMA流程报告探索性案例综述；同项目归并不冒称完全重复文献。']];
sh.getRange(`A1:B${rows.length}`).values=rows;
sh.getRange(`A1:B${rows.length}`).format.font={name:'Microsoft YaHei',size:11,color:'#24343D'};
sh.getRange(`A1:B${rows.length}`).format.wrapText=true;sh.getRange(`A1:B${rows.length}`).format.verticalAlignment='top';
sh.getRange('A1:A23').format.columnWidth=36;sh.getRange('B1:B23').format.columnWidth=100;
sh.getRange('A1:B1').format.fill='#416B72';sh.getRange('A1:B1').format.font={bold:true,color:'#FFFFFF',name:'Microsoft YaHei',size:11};
sh.getRange('A1:B14').format.rowHeight=29;sh.getRange('A15:B23').format.rowHeight=52;
for(const [cell,f] of [['B4','=B2+B3'],['B7','=B4-B5-B6'],['B9','=B7-B8'],['B11','=B9-B10'],['B13','=B11-B12']])sh.getRange(cell).formulas=[[f]];
wb.recalculate();
const inspect=await wb.inspect({kind:'table',range:'方法与计数!A1:B14',include:'values,formulas',tableMaxRows:14,tableMaxCols:2});
await fs.writeFile(path.join(root,'tmp/wheelchair/workbook_check.json'),JSON.stringify(inspect,null,2));
const xlsx=await SpreadsheetFile.exportXlsx(wb);await xlsx.save(path.join(out,'作业一_智能轮椅案例与PRISMA记录.xlsx'));
for(const [name] of [...tables,['方法与计数']]){
 try{const preview=await wb.render({sheetName:name,range:name==='核心案例'?'A1:G4':name==='方法与计数'?'A1:B14':'A1:D5',scale:1,format:'png'});await fs.writeFile(path.join(root,`tmp/wheelchair/sheet_${name}.png`),new Uint8Array(await preview.arrayBuffer()));}
 catch(e){console.log('render',name,String(e));}
}
console.log('Saved workbook with 12 cases, 22 candidate decisions, 25 source records and 9 queries.');
for(const [range,name] of [['H1:N5','证据字段'],['H7:N10','证据字段下半']]){
 const preview=await wb.render({sheetName:'核心案例',range,scale:1,format:'png'});
 await fs.writeFile(path.join(root,`tmp/wheelchair/sheet_${name}.png`),new Uint8Array(await preview.arrayBuffer()));
}
