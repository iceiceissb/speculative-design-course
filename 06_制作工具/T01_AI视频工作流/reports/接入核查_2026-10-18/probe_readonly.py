"""GET-only public-page and Ark transport checks; never submits a video job."""
from pathlib import Path
import concurrent.futures
import html
import json
import re
import urllib.error
import urllib.parse
import urllib.request

ROOT = Path(__file__).resolve().parent

def check(label, url):
    req = urllib.request.Request(url, method='GET', headers={'User-Agent':'Mozilla/5.0'})
    try:
        response=urllib.request.urlopen(req, timeout=30)
    except urllib.error.HTTPError as error:
        response=error
    except (urllib.error.URLError, TimeoutError, OSError) as error:
        return {'label':label,'url':url,'error':str(error),'job_submitted':False}
    with response:
        raw=response.read(3*1024*1024).decode('utf-8','replace')
        final=urllib.parse.urlsplit(response.geturl())
        public_url=urllib.parse.urlunsplit((final.scheme,final.netloc,final.path,'',''))
        result={'label':label,'url':public_url,'http_status':response.code,'bytes_read':len(raw),'job_submitted':False}
        if label=='ark_transport':
            try:
                err=json.loads(raw).get('error',{})
                result['error_code']=err.get('code')
                result['error_type']=err.get('type')
            except (ValueError,AttributeError):
                pass
            result['authorization_sent']=False
            result['meaning']='Transport only. A 401/403 does not verify account/model access.'
        else:
            (ROOT/'xiaohongshu_public_page.html').write_text(raw,encoding='utf-8')
            result['title']=[html.unescape(x) for x in re.findall(r'<title[^>]*>(.*?)</title>',raw,re.S)]
            text=re.sub(r'<(script|style)\b[^>]*>.*?</\1>',' ',raw,flags=re.S|re.I)
            text=html.unescape(re.sub(r'<[^>]+>',' ',text))
            result['visible_text']=re.sub(r'\s+',' ',text).strip()[:14000]
            match=re.search(r'window\.__INITIAL_STATE__\s*=\s*(.*?)</script>',raw,re.S)
            if match:
                try:
                    value=re.sub(r'\bundefined\b','null',match.group(1).strip().rstrip(';'))
                    state=json.loads(value)
                    notes=state.get('note',{}).get('noteDetailMap',{})
                    result['notes']=[{'title':v.get('note',{}).get('title'),'desc':v.get('note',{}).get('desc'),'type':v.get('note',{}).get('type')} for v in notes.values()]
                except (ValueError,AttributeError):
                    result['structured_note_parse']=False
        return result

targets=[('ark_transport','https://ark.cn-beijing.volces.com/api/v3/contents/generations/tasks?page_num=1&page_size=1'),('xiaohongshu','https://xhslink.cn/o/6TuAazFLLHq')]
with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
    results=list(executor.map(lambda pair:check(*pair),targets))
report={'mode':'read_only_no_authentication','generated_jobs':0,'results':results}
(ROOT/'只读联网核查.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(report,ensure_ascii=False,indent=2))
