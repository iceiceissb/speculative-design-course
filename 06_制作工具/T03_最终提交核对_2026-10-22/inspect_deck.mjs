import fs from 'node:fs/promises';
import {pathToFileURL} from 'node:url';
const runtime='C:/Users/22602/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/@oai/artifact-tool/dist/artifact_tool.mjs';
const {FileBlob,PresentationFile}=await import(pathToFileURL(runtime));
const source='D:/课/大四上/思辨设计/05_汇报与成片/04_最终提交作业/不用麻烦她_最终结课汇报.pptx';
const p=await PresentationFile.importPptx(await FileBlob.load(source));
const r=await p.inspect({kind:'table',maxChars:100000});
await fs.writeFile(new URL('./PPT文字索引.json',import.meta.url),JSON.stringify(r,null,2)); console.log(JSON.stringify(r.records.filter(x=>[11,13,16,17].includes(x.slideIndex)).map(x=>x)))
console.log('prototype',Object.getOwnPropertyNames(Object.getPrototypeOf(p)).filter(x=>/export|save|proto/.test(x)));
console.log('exportPptx',typeof PresentationFile.exportPptx);
