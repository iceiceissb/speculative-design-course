from pathlib import Path
root=Path('作业二/提交_这一次轮椅该听谁的/交互原型v1')
p=root/'view.js'
s=p.read_text(encoding='utf-8')
s=s.replace("${btn('同一情境，体验另一条规则','counterpart','secondary')}","${r.origin==='pair'?btn('同一情境，体验另一条规则','counterpart','secondary'):btn('另开一组同条件对照','setup','secondary')}")
s=s.replace("${s.trip&&s.result?btn('同组体验另一规则','counterpart','secondary'):''}","${s.trip?.origin==='pair'&&s.result?btn('同组体验另一规则','counterpart','secondary'):''}")
p.write_text(s,encoding='utf-8')
p=root/'model.js'
s=p.read_text(encoding='utf-8').replace("if(!state.pair||!state.trip)throw Error('没有可对照的情境');", "if(!state.pair||state.trip?.origin!=='pair')throw Error('边界演示不能冒充同条件对照');")
p.write_text(s,encoding='utf-8')
p=Path('tmp/assignment2-review-v11/verify.mjs')
s=p.read_text(encoding='utf-8')
pos=s.index('const browser=')
extra="""check('撤回偏好与地点记录互不捆绑',()=>{for(const scope of ['rule','proof']){let s=M.create();s.fixture='clear';M.beginPair(s,'A');M.review(s);M.finish(s,'pass');M.feedback(s);s.draft={rule:'B',keepRule:true,keepProof:true};M.save(s);M.revoke(s,scope);assert.equal(s.memory[scope],null);assert(s.memory[scope==='rule'?'proof':'rule']);}});
check('后续换身场景不能重新标为原组对照',()=>{let s=M.create();M.beginPair(s,'A');M.finish(s,'cancel');M.feedback(s);M.save(s,true);s.nextDraft={kind:'body',rule:'B'};M.beginNext(s);assert.throws(()=>M.counterpart(s));});
"""
s=s[:pos]+extra+s[pos:]
s=s.replace("await click('pass');await see('1 分钟','复用记录真实减少核验步骤');", "await click('pass');await see('1 分钟','复用记录真实减少核验步骤');assert.equal(await page.locator('[data-action=\"counterpart\"]').count(),0);checks.push('后续边界结果不显示虚假的同组对照入口');")
p.write_text(s,encoding='utf-8')
p=Path('tmp/assignment2-review-v11/build-deck.mjs')
s=p.read_text(encoding='utf-8')
s=s.replace('可以暂时不处理、取消、不共享、不留档；不把这些选择记成不配合。','允许暂不处理、取消、拒绝共享与留档；不标记为“不配合”。')
s=s.replace('制度异议保留待处理状态；不能把平台责任改写成一句更礼貌的回复。','制度异议保留待处理状态；不以礼貌回复代替平台履责。')
s=s.replace('同一组内，环境与记录状态不变。\\n观众不能途中选择“复核成功”。','同组环境与记录状态固定。\\n复核结果不能在途中改选。')
s=s.replace('deck-validation-v11.json','deck-validation-v11-final.json')
p.write_text(s,encoding='utf-8')
final=Path('作业二/提交_这一次轮椅该听谁的/说明PPT_这一次轮椅该听谁的_v1.1_修订.pptx')
target=Path('tmp/assignment2-review-v11/pre-visual-fix.pptx')
assert final.exists() and not target.exists()
final.rename(target)
