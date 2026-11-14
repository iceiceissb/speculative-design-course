"""Build a clean shareable ZIP and verify its extracted copy using stdlib only."""
import argparse
import hashlib
import json
import re
import shutil
import subprocess
import sys
import uuid
import zipfile
from pathlib import Path
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1]
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
PACKAGE_NAME = '场外_Bodystorming_工作台'
FORBIDDEN = {'node_modules', 'data', 'qa', '__pycache__', '.git', '.browser-cache', '.npm-cache', '.env'}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def dist_files():
    base = ROOT / 'dist'
    pending = [base / 'index.html']
    found = set()
    while pending:
        path = pending.pop().resolve()
        if not path.is_relative_to(base.resolve()) or not path.is_file():
            raise RuntimeError(f'Missing or invalid built asset: {path.name}')
        if path in found:
            continue
        found.add(path)
        refs = []
        if path.suffix == '.html':
            refs = re.findall(r'(?:src|href)=["\']([^"\']+)', path.read_text(encoding='utf-8'))
        elif path.suffix == '.css':
            refs = re.findall(r'url\(["\']?([^\)"\']+)', path.read_text(encoding='utf-8'))
        for ref in refs:
            url = urlsplit(ref)
            if url.scheme or url.netloc or ref.startswith('#'):
                continue
            local = unquote(url.path)
            pending.append(base / local.lstrip('/') if local.startswith('/') else path.parent / local)
    found.update((base / 'fonts').glob('*'))  # Keep the bundled font's OFL license.
    return sorted(found)


OFFLINE_CHECK = r'''
import json
from pathlib import Path
from agent.engine import Engine, classroom_view, export_markdown
from agent.storage import Store
import server
root = Path.cwd().resolve()
assert Path(server.__file__).resolve().parent == root
assert (root / 'dist/index.html').is_file()
store = Store(root / '_offline_check' / 'workbench.sqlite3')
assert store.listing() == [] and store.documents() == [] and store.plans() == []
class NoNetworkModel:
    def complete(self, *args, **kwargs):
        raise AssertionError('Demo must not call a model')
engine = Engine(store, NoNetworkModel())
fields = dict(title='打包验证', story='三个人用纸板协作搭建临时空间。', participants='3', remaining='5', mode='demo',
              activity_config=dict(materials=['纸板', '绳子'], space='fixed', focus='即兴与协作'))
plan = store.add_plan(fields)
assert store.plans()[0]['id'] == plan['id']
d = store.create(fields)
sid = d['id']
assert '纸板、绳子' in d['constraints']
d = engine.generate(sid)
assert len(d['events']) == 5
engine.select(sid, 'E1')
d = engine.guide(sid, '有人明确请求帮助', 'help')
assert d['hints'][-1]['feedback'] == 'not_shown'
assert classroom_view(d)['presentation'] is None
d = engine.present(sid, 'hint', d['hints'][-1]['id'])
assert classroom_view(d)['presentation']['kind'] == 'hint'
assert 'logs' not in classroom_view(d)
assert '手写演示，非模型生成' in export_markdown(d)
assert engine.present(sid, 'blank')['presentation']['kind'] == 'blank'
assert engine.select(sid, 'E2')['presentation'] is None
print(json.dumps(dict(ok=True, check='extracted offline demo', events=5, no_model_requests=True)))
'''

HTTP_CHECK = r'''
import json, re, threading, urllib.request
from pathlib import Path
from server import make_server
root = Path.cwd().resolve()
s = make_server(0, root / '_http_check')
t = threading.Thread(target=s.serve_forever, daemon=True)
t.start()
base = 'http://127.0.0.1:' + str(s.server_port)
opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
def request(path, data=None, raw=False):
    req = urllib.request.Request(base + path, data=None if data is None else json.dumps(data).encode(),
                                 headers={'Content-Type':'application/json'})
    with opener.open(req, timeout=8) as response:
        body = response.read()
        return body if raw else json.loads(body)
try:
    assert request('/api/health')['ok']
    assert request('/api/sessions') == [] and request('/api/knowledge') == [] and request('/api/plans') == []
    html = request('/', raw=True).decode()
    for asset in re.findall(r'(?:src|href)=["\'](/[^"\']+)', html):
        assert len(request(asset, raw=True)) > 0
    fields = dict(story='三人协作搭建临时休息点', mode='demo', activity_config=dict(materials=['纸板']))
    d = request('/api/sessions', fields)
    sid = d['id']
    assert len(request('/api/sessions/' + sid + '/generate', {})['events']) == 5
    request('/api/sessions/' + sid + '/select', dict(event_id='E1'))
    d = request('/api/sessions/' + sid + '/guide', dict(observation='有人明确求助', state='help'))
    assert request('/api/classroom/' + sid)['presentation'] is None
    request('/api/sessions/' + sid + '/present', dict(kind='hint', hint_id=d['hints'][-1]['id']))
    assert request('/api/classroom/' + sid)['presentation']['kind'] == 'hint'
    assert '手写演示'.encode() in request('/api/sessions/' + sid + '/export?format=md', raw=True)
    print(json.dumps(dict(ok=True, check='extracted HTTP demo and built assets', actual_port=s.server_port)))
finally:
    s.shutdown(); s.server_close(); t.join()
'''


def run_check(code, folder):
    result = subprocess.run([sys.executable, '-B', '-c', code], cwd=folder, capture_output=True, text=True, encoding='utf-8')
    if result.returncode:
        raise RuntimeError('Extracted package check failed:\n' + result.stderr[-3000:])
    return json.loads(result.stdout.strip().splitlines()[-1])


def build(date):
    release = ROOT / 'releases' / date
    release.mkdir(parents=True, exist_ok=True)
    target = release / f'场外_Bodystorming_分享包_{date}.zip'
    n = 2
    while target.exists():
        target = release / f'场外_Bodystorming_分享包_{date}_{n:02}.zip'
        n += 1
    work = ROOT / 'qa' / ('打包验收_' + uuid.uuid4().hex[:10])
    stage = work / '待打包' / PACKAGE_NAME
    stage.mkdir(parents=True)
    files = [ROOT / name for name in ('server.py', 'start.ps1', '启动场外.cmd', 'README.md', 'package.json', 'package-lock.json', 'vite.config.js', 'index.html', '.gitignore')]
    for folder in ('agent', 'prompts', 'src', 'public', 'tests', '交付说明', 'tools'):
        files.extend(p for p in (ROOT / folder).rglob('*') if p.is_file() and not any(part in FORBIDDEN for part in p.relative_to(ROOT).parts))
    files += [ROOT / 'design' / '课堂角色与交互改进.md']
    files += list((ROOT / 'design').glob('classroom-*.png'))
    files += dist_files()
    for source in sorted(set(files)):
        relative = source.relative_to(ROOT)
        if any(part in FORBIDDEN for part in relative.parts):
            raise RuntimeError('Excluded path reached allowlist')
        destination = stage / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, destination)
    shutil.copy2(stage / '交付说明' / '00_先看这里.txt', stage / '00_先看这里.txt')
    payload = sorted(p for p in stage.rglob('*') if p.is_file())
    manifest = '\n'.join(f'{sha(p)}  {p.relative_to(stage).as_posix()}' for p in payload) + '\n'
    (stage / 'MANIFEST.sha256').write_text(manifest, encoding='utf-8')
    with zipfile.ZipFile(target, 'x', compression=zipfile.ZIP_DEFLATED, compresslevel=6) as archive:
        for p in sorted(stage.rglob('*')):
            if p.is_file():
                archive.write(p, PACKAGE_NAME + '/' + p.relative_to(stage).as_posix())
    extracted = work / '解压验收 含空格路径'
    with zipfile.ZipFile(target) as archive:
        if archive.testzip() is not None:
            raise RuntimeError('ZIP CRC validation failed')
        for name in archive.namelist():
            parts = Path(name).parts
            if any(p in FORBIDDEN or p == '..' for p in parts) or Path(name).is_absolute():
                raise RuntimeError('Unexpected archive path')
        archive.extractall(extracted)
    app = extracted / PACKAGE_NAME
    for line in manifest.splitlines():
        digest, relative = line.split('  ', 1)
        if sha(app / relative) != digest:
            raise RuntimeError('Extracted file hash mismatch')
    offline = run_check(OFFLINE_CHECK, app)
    info = dict(zip=str(target), size_bytes=target.stat().st_size, sha256=sha(target), payload_files=len(payload) + 1,
                extracted_app=str(app), crc_verified=True, file_hashes_verified=True, offline=offline,
                excluded=sorted(FORBIDDEN), python_required='3.10+')
    report = target.with_suffix('.校验.json')
    report.write_text(json.dumps(info, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps(info, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--date', default='2026-10-21')
    parser.add_argument('--verify-http', type=Path, help='An existing build verification JSON')
    args = parser.parse_args()
    if args.verify_http:
        report = args.verify_http.resolve()
        if not report.is_relative_to((ROOT / 'releases').resolve()):
            raise SystemExit('Report must belong to this project releases directory')
        info = json.loads(report.read_text(encoding='utf-8'))
        app = Path(info['extracted_app']).resolve()
        if not app.is_relative_to((ROOT / 'qa').resolve()):
            raise SystemExit('Extraction must stay inside this project QA directory')
        info['http'] = run_check(HTTP_CHECK, app)
        report.write_text(json.dumps(info, ensure_ascii=False, indent=2), encoding='utf-8')
        print(json.dumps(info['http'], ensure_ascii=False, indent=2))
    else:
        build(args.date)
