from pathlib import Path
p=Path('作业二/提交_这一次轮椅该听谁的/交互原型v1/app.js')
s=p.read_text(encoding='utf-8')
s=s.replace("${cls?'':arrow}", "${/secondary|quiet/.test(cls)?'':arrow}")
s=s.replace("function next(){let saved=state.saved, valid=saved&&saved.body===state.body;", "function next(){let saved=state.saved, valid=saved&&saved.body===state.body;")
needle="</blockquote><div class=\"record\"><p><b>默认回应：</b>"
replacement="</blockquote>${saved?.pref==='brief'?'<details><summary>查看详细原因</summary><p>基础校准已完成，但这次门口的门扇位置和通行空间仍需确认。旧身体的通过记录不能代替当前条件；你可复核、绕行、求助、等待或取消。</p></details>':''}<div class=\"record\"><p><b>默认回应：</b>"
assert needle in s
s=s.replace(needle,replacement)
p.write_text(s,encoding='utf-8')
p=Path('作业二/提交_这一次轮椅该听谁的/交互原型v1/style.css')
s=p.read_text(encoding='utf-8')+'\ndetails{border-top:1px solid var(--line);border-bottom:1px solid var(--line);padding:16px 0;margin:20px 0}summary{cursor:pointer;font-size:18px;color:var(--accent);font-weight:600}details p{font-size:18px}summary:focus-visible{outline:3px solid #bb783e;outline-offset:4px}\n'
p.write_text(s,encoding='utf-8')
