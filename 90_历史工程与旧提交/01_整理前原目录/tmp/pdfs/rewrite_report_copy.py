from pathlib import Path
p=Path(r'D:/课/大四上/思辨设计/tmp/pdfs/build_landscape_report.py')
s=p.read_text(encoding='utf-8')
a=s.index('shots=[\n')
b=s.index("\nd.page('05 /",a)
s=s[:a]+"shots=json.loads((ROOT/'tmp/pdfs/storyboard_report_copy.json').read_text(encoding='utf-8'))\nfor i,(title,img,place,story,line,note) in enumerate(shots,1):d.shot(i,title,img,place,story,line,note)\n"+s[b:]
s=s.replace("'剧本阅读页。'+('承接上一页，继续本场动作与对白。' if cont else '本场重点：'+shots[[0,1,2,3,4,8,9,10][si-1]][4])", "scene_speeches[si-1][1 if cont else 0]")
p.write_text(s,encoding='utf-8')
