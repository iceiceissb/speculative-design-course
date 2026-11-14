import base64, json, subprocess, tempfile, time, urllib.request
from pathlib import Path
from websocket import create_connection

root=Path(__file__).resolve().parents[1]
chrome=r'C:\Program Files\Google\Chrome\Application\chrome.exe'
port=9238
with tempfile.TemporaryDirectory(prefix='xiuxiu-world-') as profile:
    proc=subprocess.Popen([chrome,'--headless=new','--disable-gpu','--enable-unsafe-swiftshader','--remote-allow-origins=*',f'--remote-debugging-port={port}',f'--user-data-dir={profile}',(root/'index.html').as_uri()],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,creationflags=subprocess.CREATE_NO_WINDOW)
    ws=None
    try:
        for _ in range(100):
            try:
                with urllib.request.urlopen(f'http://127.0.0.1:{port}/json',timeout=1) as r: tabs=json.load(r)
                break
            except Exception: time.sleep(.1)
        ws=create_connection(next(t['webSocketDebuggerUrl'] for t in tabs if t.get('type')=='page'),timeout=8)
        ident=0
        def call(method,params=None):
            global ident
            ident+=1;now=ident;ws.send(json.dumps(dict(id=now,method=method,params=params or {})))
            while True:
                result=json.loads(ws.recv())
                if result.get('id')==now:return result.get('result',{})
        def ev(expr):
            result=call('Runtime.evaluate',dict(expression=expr,returnByValue=True))
            if result.get('exceptionDetails'):raise RuntimeError(result['exceptionDetails'])
            return result.get('result',{}).get('value')
        call('Emulation.setDeviceMetricsOverride',dict(width=1600,height=900,deviceScaleFactor=1,mobile=False));call('Page.reload',dict(ignoreCache=True))
        for _ in range(100):
            if ev('Boolean(window.xiuxiuDemo && window.xiuxiuDemo.world)'):break
            time.sleep(.1)
        w='xiuxiuDemo.world'
        idle1=ev(f'({{{"q"}:{w}.chair.userData.qHead.rotation.y,"xu":{w}.xu.userData.head.rotation.y,"foot":{w}.xu.userData.legs[0].rotation.x}})')
        time.sleep(1.2)
        idle2=ev(f'({{{"q"}:{w}.chair.userData.qHead.rotation.y,"xu":{w}.xu.userData.head.rotation.y,"foot":{w}.xu.userData.legs[0].rotation.x}})')
        assert all(abs(idle2[k]-idle1[k])>.001 for k in idle1),(idle1,idle2)
        chapter_idle=[]
        for chapter in range(6):
            ev(f'{w}.setScene({chapter},{{gift:true}})')
            first=ev(f'({{q:{w}.chair.userData.qHead.rotation.y,xu:{w}.xu.userData.head.rotation.y,visible:{w}.xu.visible}})')
            ev(f'{w}.tick(.85)')
            last=ev(f'({{q:{w}.chair.userData.qHead.rotation.y,xu:{w}.xu.userData.head.rotation.y,visible:{w}.xu.visible}})')
            assert abs(last['q']-first['q'])>.001,(chapter,first,last)
            if last['visible']:assert abs(last['xu']-first['xu'])>.001,(chapter,first,last)
            chapter_idle.append(chapter)
        ev('xiuxiuDemo.state.maxVisited=1;xiuxiuDemo.go(1);document.getElementById("begin-timed").click();xiuxiuDemo.choose(STORY[1].choices.find(x=>x.id==="market_pause"));xiuxiuDemo.world.skip()')
        ev('xiuxiuDemo.respond(FOLLOWUPS.market_pause.find(x=>x.id==="market_carry_take"));xiuxiuDemo.world.skip()')
        bag=ev(f'({{carried:{w}.carriedBag.visible,ground:{w}.marketBag.visible,lap:{w}.lapBag.visible,position:{w}.carriedBag.getWorldPosition(new THREE.Vector3()).toArray()}})')
        assert bag['carried'] and not bag['ground'] and not bag['lap'] and bag['position'][0]<-1.1 and bag['position'][1]>.85,bag
        time.sleep(.3)
        png=call('Page.captureScreenshot',dict(format='png'))['data']
        (root/'.video_build'/'carry_qa.png').write_bytes(base64.b64decode(png))
        ev('xiuxiuDemo.state.maxVisited=3;xiuxiuDemo.go(3)')
        assert ev(f'{w}.carriedBag.visible && !{w}.marketBag.visible')
        ev('xiuxiuDemo.state.maxVisited=1;xiuxiuDemo.go(1);document.getElementById("begin-timed").click();xiuxiuDemo.choose(STORY[1].choices.find(x=>x.id==="market_refuse"));xiuxiuDemo.world.skip()')
        ev('xiuxiuDemo.respond(FOLLOWUPS.market_refuse.find(x=>x.id==="market_refuse_all"));xiuxiuDemo.world.skip()')
        assert ev(f'{w}.lapBag.visible && !{w}.carriedBag.visible')
        print(json.dumps(dict(idle1=idle1,idle2=idle2,chapter_idle=chapter_idle,carry=bag,lap=True),ensure_ascii=True))
    finally:
        if ws:ws.close()
        proc.terminate()
        try:proc.wait(timeout=5)
        except subprocess.TimeoutExpired:proc.kill()
