import fs from 'node:fs/promises';
import {PresentationFile,FileBlob} from 'file:///C:/Users/22602/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/@oai/artifact-tool/dist/artifact_tool.mjs';
const p=await PresentationFile.importPptx(await FileBlob.load('D:/课/大四上/思辨设计/PRISMA通用模板.pptx'));
console.log((await p.inspect({kind:'slide',maxChars:1500})).ndjson);
for(const n of [5,12]) {const b=await p.export({slide:p.slides.items[n],format:'png',scale:1}); await fs.writeFile(`D:/课/大四上/思辨设计/tmp/assignment1/template-${n+1}.png`,new Uint8Array(await b.arrayBuffer()));}
