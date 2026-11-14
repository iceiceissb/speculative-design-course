from pathlib import Path
import requests, json, concurrent.futures
OUT=Path(__file__).resolve().parent/'sources'
OUT.mkdir(exist_ok=True)
sources={
 'luci_current.pdf':'https://www.luci.com/hubfs/Luci_April2026/pdf/613-00003_F_LUCI-User-Guide_Color-1.pdf',
 'sralab.jpg':'https://www.sralab.org/sites/default/files/styles/header_1280x410_/public/2017-03/wheelchair_0.jpg?h=3fcaf87b&itok=grn5zliC',
 'whill.png':'https://whill.inc/_next/static/media/autonomousdriveSection2.1v5ho7qv2_omo.png',
 'luci_guide.pdf':'https://luci.com/wp-content/uploads/2023/11/613-00003_Rev-C_LUCI-User-Guide.pdf',
 'luci_safety.pdf':'https://luci.com/wp-content/uploads/2021/07/LUCI-Safety-Report.pdf',
 'conav.pdf':'https://arxiv.org/pdf/2507.11716',
 'navchair.pdf':'https://cdn.aaai.org/AAAI/1996/AAAI96-222.pdf',
 'huggiebot.pdf':'https://files.ait.ethz.ch/projects/huggiebot2.0/Block21-HRI-Commandments.pdf',
 'sralab.html':'https://www.sralab.org/research/projects/smart-wheelchair',
 'whill.html':'https://whill.inc/au/mobility-service/how-it-works/autonomous-drive',
 'clara.html':'https://clararobot.github.io/',
 'armar.html':'https://www.frontiersin.org/journals/robotics-and-ai/articles/10.3389/frobt.2024.1455375/full',
 'corrective.html':'https://pmc.ncbi.nlm.nih.gov/articles/PMC8050957/',
}
def fetch(item):
 name,url=item
 if (OUT/name).exists():return {'file':name,'url':url,'status':'previously downloaded'}
 try:
  r=requests.get(url,timeout=50);r.raise_for_status();(OUT/name).write_bytes(r.content)
  return {'file':name,'url':url,'status':r.status_code,'bytes':len(r.content)}
 except Exception as e:return {'file':name,'url':url,'error':str(e)}
with concurrent.futures.ThreadPoolExecutor(max_workers=5) as ex:results=list(ex.map(fetch,sources.items()))
(OUT/'download_log.json').write_text(json.dumps(results,ensure_ascii=False,indent=2),encoding='utf-8')
for r in results:print(r)
