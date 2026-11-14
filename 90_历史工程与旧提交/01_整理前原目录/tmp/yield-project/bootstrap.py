from pathlib import Path
import requests,json,shutil,re,fitz
root=Path('作业二/提交_请别替我让路');build=Path('tmp/yield-project')
for p in [root/'3D交互原型/assets',root/'研究与讲稿',build/'slides',build/'qa',build/'sources']:p.mkdir(parents=True,exist_ok=True)
shutil.copyfile('D:/清华/SRT/人本AI智能体SRT/laban-workflow-app/js/lib/three.min.js',root/'3D交互原型/three.min.js')
for name in ['luci','conav']:
 shutil.copyfile(f'tmp/wheelchair/assets/{name}.png',root/f'3D交互原型/assets/{name}.png')
urls={
 'dawn':'https://dawn2021.orylab.com/assets/images/common/c-area-pic.jpg',
 'guests':'https://ardentservices.co.uk/wp-content/uploads/2016/11/guests.jpg',
 'proxemics':'https://www.frontiersin.org/files/Articles/57423/xml-images/fpsyg-04-00859-g002.webp'
}
log=[]
for name,url in urls.items():
 try:
  r=requests.get(url,timeout=35);r.raise_for_status()
  suffix='.webp' if '.webp' in url else '.jpg';p=root/f'3D交互原型/assets/{name}{suffix}';p.write_bytes(r.content)
  log.append({'name':name,'url':url,'path':str(p),'bytes':len(r.content)});print(name,len(r.content))
 except Exception as e:log.append({'name':name,'url':url,'error':str(e)});print(name,str(e)[:180])
p=fitz.open('tmp/wheelchair/sources/huggiebot.pdf')
for i in range(min(3,len(p))):
 for j,im in enumerate(p[i].get_images(full=True)):
  x=p.extract_image(im[0]);f=build/f'sources/hug-{i}-{j}.{x["ext"]}';f.write_bytes(x['image']);print('hug',f.name,x['width'],x['height'])
(build/'sources/assets-log.json').write_text(json.dumps(log,ensure_ascii=False,indent=2),encoding='utf-8')
