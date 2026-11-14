import fs from 'node:fs/promises';import vm from 'node:vm';
const root='作业二/提交_这一次轮椅该听谁的/交互原型v1';
const box={window:{}};vm.runInNewContext(await fs.readFile('tmp/assignment2-review-v11/data-v1.js','utf8'),box);
const sources=box.window.STUDY.sources;
sources[0].translation='已有覆盖功能说明控制存在选择空间；本次比较谁发起确认，并允许对服务规则提出异议。';
sources[1].translation='人的操作可以介入控制；进一步追问是否默认使用者始终愿意、能够主动解释。';
sources[3].translation='让反馈改变后续提问规则，同时给现场记录设置身体与地点边界；这不是在网页内实现学习模型。';
await fs.writeFile(root+'/data.js','window.STUDY = '+JSON.stringify({sources},null,2)+';\n');
const css=`
/* v1.1: retain the existing off-white / teal visual system. */
.rule-pair{display:grid;grid-template-columns:1fr 1fr;gap:42px;margin:34px 0}.rule-pair article{padding:0 20px 18px 0}.rule-pair article+article{border-left:1px solid var(--line);padding-left:40px}.rule-pair h2{color:var(--accent);margin-top:0}.tradeoff{min-height:90px;color:var(--warn)}.trip-bar{display:flex;justify-content:space-between;gap:20px;flex-wrap:wrap;padding:16px 0;margin:10px 0 26px;border-top:1px solid var(--line);border-bottom:1px solid var(--line);font-size:17px}.outcome-status{font-size:20px;color:var(--accent);padding:12px 0}.memory-visible{border-left:3px solid var(--accent);padding-left:20px;color:var(--accent)}select{display:block;width:100%;background:#faf9f5;border:1px solid var(--line);color:var(--ink);border-radius:4px;font-size:18px;padding:12px;margin:12px 0 20px;min-height:50px}label{line-height:1.7}button:disabled,input:disabled{cursor:not-allowed;opacity:.6}.check-row:has(input:disabled){color:var(--muted)}.rule-pair .btn{min-width:190px}nav{gap:24px}small{font-size:15px;line-height:1.65}.caption{font-size:15px}textarea{min-height:135px}
@media(max-width:1100px){header{gap:20px}.brand{font-size:22px}nav{gap:17px}nav button{font-size:16px}.intro h1{font-size:36px}}
@media(max-width:760px){nav{gap:20px;flex-wrap:wrap}nav button{font-size:15px}.rule-pair{grid-template-columns:1fr;gap:24px}.rule-pair article{padding:0 0 24px}.rule-pair article+article{border-left:0;border-top:1px solid var(--line);padding:24px 0 0}.tradeoff{min-height:0}.trip-bar{font-size:15px;gap:10px}.intro h1{font-size:30px}.caption{font-size:14px}select{font-size:16px}small{font-size:14px}}
`;
const original=await fs.readFile('tmp/assignment2-review-v11/style-v1.css','utf8');await fs.writeFile(root+'/style.css',original+css);
