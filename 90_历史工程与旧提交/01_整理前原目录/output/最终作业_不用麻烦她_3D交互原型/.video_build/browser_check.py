import base64
import json
import subprocess
import tempfile
import time
import urllib.request
from pathlib import Path
from websocket import create_connection

root = Path(__file__).resolve().parents[1]
chrome = r'C:\Program Files\Google\Chrome\Application\chrome.exe'
port = 9237

def wait_until(test, seconds=25):
    end = time.time() + seconds
    while time.time() < end:
        try:
            value = test()
            if value:
                return value
        except Exception:
            pass
        time.sleep(.2)
    raise AssertionError('browser wait timed out')

class Tab:
    def __init__(self, ws):
        self.ws = create_connection(ws, timeout=8)
        self.count = 0
    def call(self, method, params=None):
        self.count += 1
        ident = self.count
        self.ws.send(json.dumps(dict(id=ident, method=method, params=params or {})))
        while True:
            data = json.loads(self.ws.recv())
            if data.get('id') == ident:
                if 'error' in data:
                    raise RuntimeError(data['error'])
                return data.get('result', {})
    def eval(self, expr):
        r = self.call('Runtime.evaluate', dict(expression=expr, returnByValue=True, awaitPromise=True))
        if 'exceptionDetails' in r:
            raise RuntimeError(r['exceptionDetails'])
        return r.get('result', {}).get('value')
    def close(self):
        self.ws.close()

with tempfile.TemporaryDirectory(prefix='xiuxiu-chrome-') as profile:
    proc = subprocess.Popen([chrome, '--headless=new', '--disable-gpu', '--enable-unsafe-swiftshader', '--remote-allow-origins=*', f'--remote-debugging-port={port}', f'--user-data-dir={profile}', (root/'index.html').as_uri()], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, creationflags=subprocess.CREATE_NO_WINDOW)
    try:
        def get_tabs():
            with urllib.request.urlopen(f'http://127.0.0.1:{port}/json', timeout=1) as response:
                return json.load(response)
        tabs = wait_until(get_tabs)
        tab = Tab(next(x['webSocketDebuggerUrl'] for x in tabs if x.get('type') == 'page'))
        tab.call('Emulation.setDeviceMetricsOverride', dict(width=1366,height=768,deviceScaleFactor=1,mobile=False))
        tab.call('Page.reload', dict(ignoreCache=True))
        wait_until(lambda: tab.eval('Boolean(window.xiuxiuDemo && window.xiuxiuDemo.world)'))
        assert tab.eval('xiuxiuDemo.state.phase === "briefing" && document.getElementById("decision-timer").hidden')
        tab.eval('document.getElementById("begin-timed").click()')
        first = tab.eval('({phase:xiuxiuDemo.state.phase,timer:!document.getElementById("decision-timer").hidden,hidden:document.hidden})')
        assert first['phase'] == 'choice' and first['timer'] and not first['hidden'], first
        time.sleep(.4)
        image = tab.call('Page.captureScreenshot', dict(format='png'))['data']
        (root/'.video_build'/'demo_timer_qa.png').write_bytes(base64.b64decode(image))
        wait_until(lambda: tab.eval('xiuxiuDemo.state.timeouts[0] === "choice" && xiuxiuDemo.state.phase === "reaction"'), 25)
        auto = tab.eval('({id:xiuxiuDemo.state.history[0],title:document.getElementById("result-title").textContent})')
        assert auto['id'] == 'road_auto' and '时间到了' in auto['title'], auto
        tab.eval('xiuxiuDemo.state.maxVisited=4;xiuxiuDemo.go(4)')
        tab.eval('document.getElementById("begin-timed").click()')
        tab.eval('xiuxiuDemo.choose(STORY[4].choices.find(x=>x.id==="slope_tell"));xiuxiuDemo.world.skip()')
        wait_until(lambda: tab.eval('xiuxiuDemo.state.phase === "reactionBriefing"'))
        tab.eval('document.getElementById("begin-timed").click()')
        assert tab.eval('!document.getElementById("decision-timer").hidden')
        wait_until(lambda: tab.eval('xiuxiuDemo.state.timeouts[4] === "reaction" && xiuxiuDemo.state.phase === "result"'), 20)
        follow = tab.eval('({id:xiuxiuDemo.state.followups[4],title:document.getElementById("result-title").textContent})')
        assert follow['id'] == 'slope_limit' and '回应超时' in follow['title'], follow
        print('Demo timer:', json.dumps([first, auto, follow], ensure_ascii=True))
        tab.close()
        tab = Tab(next(x['webSocketDebuggerUrl'] for x in get_tabs() if x.get('type') == 'page'))
        tab.call('Page.navigate', dict(url=(root/'分镜图'/'30帧制作版'/'即梦制作台.html').as_uri()))
        wait_until(lambda: tab.eval('document.querySelectorAll(".clip").length === 30'))
        video = tab.eval('({clips:VIDEO_CLIPS.length,pairs:VIDEO_CLIPS.filter(x=>x.kind==="首尾帧").length,frames:VIDEO_CLIPS.reduce((n,x)=>n+x.frames.length,0),images:[...document.querySelectorAll(".frames img")].filter(x=>x.complete&&x.naturalWidth>0).length,timeline:VIDEO_TIMELINE.length,pov:VIDEO_TIMELINE.filter(x=>x.pov).length,minutes:VIDEO_CLIPS.reduce((n,x)=>n+x.duration,0)})')
        assert video == dict(clips=30,pairs=6,frames=36,images=36,timeline=36,pov=5,minutes=180), video
        image = tab.call('Page.captureScreenshot', dict(format='png'))['data']
        (root/'.video_build'/'video_page_qa.png').write_bytes(base64.b64decode(image))
        tab.eval('document.getElementById("timeline").scrollIntoView()')
        time.sleep(.2)
        image = tab.call('Page.captureScreenshot', dict(format='png'))['data']
        (root/'.video_build'/'timeline_qa.png').write_bytes(base64.b64decode(image))
        tab.eval('document.getElementById("clip-31").scrollIntoView()')
        time.sleep(.2)
        image = tab.call('Page.captureScreenshot', dict(format='png'))['data']
        (root/'.video_build'/'pov_card_qa.png').write_bytes(base64.b64decode(image))
        print('Video page:', video)
        tab.call('Page.navigate', dict(url=(root/'分镜图'/'30帧制作版'/'index.html').as_uri()))
        wait_until(lambda: tab.eval('document.querySelectorAll(".card").length === 36'))
        assert tab.eval('document.querySelectorAll(".card.pov").length === 5')
        print('Storyboard gallery: 36 frames, 5 subjective shots')
        tab.close()
    finally:
        proc.terminate()
        try:
            proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            proc.kill()
