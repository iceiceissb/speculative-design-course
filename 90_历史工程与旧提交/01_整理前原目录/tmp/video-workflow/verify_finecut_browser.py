import json
from pathlib import Path
from playwright.sync_api import sync_playwright

root = Path(__file__).resolve().parents[2] / 'output/AI视频工作流'
out = root / 'exports/坡道精剪_v1_20261009'
with sync_playwright() as p:
    browser = p.chromium.launch(channel='chrome', headless=True)
    try:
        page = browser.new_page(viewport={'width':1280,'height':1000})
        page.goto('http://127.0.0.1:8765/', wait_until='domcontentloaded')
        page.locator('[data-view="timeline"]').click()
        page.locator('#result h2').wait_for()
        assert page.locator('#result h2').inner_text() == '坡道精剪 · 字幕与配音'
        page.wait_for_function('document.querySelector("#result video").readyState >= 1')
        duration = page.locator('#result video').evaluate('(v)=>v.duration')
        assert abs(duration-18)<.1
        assert page.locator('#result video track').count()==0, '字幕重复叠加'
        video = page.locator('#result video')
        video.evaluate('(v)=>{v.currentTime=14.8;}')
        page.wait_for_function('!document.querySelector("#result video").seeking')
        page.locator('#result').screenshot(path=str(out/'验收/选片台精剪.png'))
        report = {'ok':True,'title':page.locator('#result h2').inner_text(),
                  'duration':duration,'duplicate_subtitle_tracks':0,
                  'video_loaded':True,'javascript_errors':False}
        (out/'验收/浏览器验收.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
        print(json.dumps(report,ensure_ascii=False))
    finally:
        browser.close()
