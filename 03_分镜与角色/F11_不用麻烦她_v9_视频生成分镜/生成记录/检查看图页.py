from pathlib import Path
import json, re, subprocess, hashlib
from urllib.parse import unquote

root=Path(__file__).resolve().parent.parent
page=(root/'看图.html').read_text(encoding='utf-8')
data=json.loads(re.search(r'<script id="frames-data" type="application/json">(.*?)</script>',page,re.S).group(1))
assert len(data)==72 and len({s['id'] for s in data})==72
for s in data:
    assert (root/s['image']).is_file()
    assert (root/'总览/缩略图'/f"{s['id']}.jpg").is_file()
js=re.findall(r'<script>(.*?)</script>',page,re.S)[0]
syntax=subprocess.run(['node','--check','-'],input=js,text=True,encoding='utf-8',capture_output=True)
assert syntax.returncode==0, syntax.stderr
links=[]
errors=[]
for doc in root.glob('*.md'):
    for target in re.findall(r'!?\[[^\]]*\]\(([^)]+)\)',doc.read_text(encoding='utf-8-sig')):
        target=target.strip('<> ').split('#')[0]
        if not target or re.match(r'^\w+://',target):
            continue
        resolved=(doc.parent/unquote(target)).resolve()
        links.append(str(resolved))
        if not resolved.exists():
            errors.append({'file':doc.name,'link':target})
assert not errors, errors
plan=json.loads((root/'generation_plan.json').read_text(encoding='utf-8-sig'))
assert len(plan['jobs'])==61 and not plan['ready_for_generation']
for job in plan['jobs']:
    assert (root/job['storyboard_image']).is_file()
    assert job['first_frame_placeholder']==job['storyboard_image']
    assert not job['media_ready'] and job['submission_status']=='not_submitted'
story=json.loads((root/'storyboard.json').read_text(encoding='utf-8-sig'))
digest=hashlib.sha256((root/story['source_script']).read_bytes()).hexdigest().upper()
assert digest==story['source_sha256'].upper()
result={'selected_images':72,'gallery_images':72,'thumbnails':72,'javascript_syntax_valid':True,'local_markdown_links_checked':len(links),'broken_links':errors,'video_jobs_submitted':0,'source_script_unchanged':True,'visual_review_status':'draft_with_documented_scene_and_mechanism_issues'}
(root/'生成记录/看图页检查.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(result,ensure_ascii=True))
