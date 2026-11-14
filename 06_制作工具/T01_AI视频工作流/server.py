"""Loopback-only review UI; serves only declared media, never credentials."""
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import mimetypes
import re
import secrets
import threading
import urllib.parse
import urllib.request
import webbrowser

from workflow import Workflow, load_key, stamp


def serve(workflow, port=8765, open_browser=False):
    token = secrets.token_urlsafe(32)
    operation = {'running': False, 'message': '', 'error': '', 'finished_at': ''}
    mutex = threading.Lock()

    def start_action(function):
        with mutex:
            if operation['running']:
                raise ValueError('已有操作正在运行')
            operation.update(running=True, message='正在处理…', error='')
        def worker():
            try:
                result = function()
                operation['message'] = result.get('message', '已完成，请查看结果。')
            except Exception as error:
                text = str(error); key = load_key(workflow.root)
                operation['error'] = text.replace(key, '[REDACTED]') if key else text
                operation['message'] = '操作未完成，已保存已有结果。'
            finally:
                operation['running'] = False; operation['finished_at'] = stamp()
        threading.Thread(target=worker, daemon=True).start()

    class Handler(BaseHTTPRequestHandler):
        def log_message(self, fmt, *args):
            pass

        def valid_host(self):
            return self.headers.get('Host') in {f'127.0.0.1:{port}', f'localhost:{port}'}

        def json_response(self, payload, status=200):
            body = json.dumps(payload, ensure_ascii=False).encode('utf-8')
            self.send_response(status)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.send_header('Cache-Control', 'no-store')
            self.send_header('Content-Length', str(len(body))); self.end_headers(); self.wfile.write(body)

        def send_file(self, path, head=False):
            size = path.stat().st_size; start, end = 0, size-1
            byte_range = self.headers.get('Range', '')
            if byte_range:
                match = re.fullmatch(r'bytes=(\d*)-(\d*)', byte_range)
                if not match or not any(match.groups()):
                    self.send_error(416); return
                if match[1]:
                    start = int(match[1]); end = min(int(match[2]), size-1) if match[2] else size-1
                else:
                    start = max(0, size-int(match[2]))
                if start >= size or end < start:
                    self.send_error(416); return
            self.send_response(206 if byte_range else 200)
            self.send_header('Content-Type', mimetypes.guess_type(path.name)[0] or 'application/octet-stream')
            self.send_header('Accept-Ranges', 'bytes')
            self.send_header('X-Content-Type-Options', 'nosniff')
            self.send_header('Content-Length', str(end-start+1))
            if byte_range:
                self.send_header('Content-Range', f'bytes {start}-{end}/{size}')
            self.end_headers()
            if head:
                return
            try:
                with path.open('rb') as file:
                    file.seek(start); remaining = end-start+1
                    while remaining:
                        data = file.read(min(65536, remaining))
                        if not data: break
                        self.wfile.write(data); remaining -= len(data)
            except (ConnectionResetError, ConnectionAbortedError, BrokenPipeError):
                pass

        def do_HEAD(self):
            self.do_GET(head=True)

        def do_GET(self, head=False):
            if not self.valid_host():
                return self.json_response({'error': 'Host不允许'}, 403)
            path = urllib.parse.unquote(urllib.parse.urlparse(self.path).path)
            try:
                w = Workflow(workflow.root)
                if path == '/api/state':
                    value = w.public_state(); value.update(token=token, operation=operation.copy())
                    return self.json_response(value)
                if path == '/':
                    return self.send_file(w.root / 'web/index.html', head)
                if path in {'/app.js', '/style.css'}:
                    return self.send_file(w.root / 'web' / path[1:], head)
                allowed = set()
                for c in w.state()['candidates']:
                    allowed.update(c[k] for k in ['file', 'thumbnail'] if c.get(k))
                for job in w.jobs.values():
                    allowed.update('assets/' + f['file'] for f in job['frames'])
                exports = w.public_state()['exports']
                allowed.update(exports[k] for k in ['mp4', 'vtt', 'srt'] if exports.get(k))
                if path[1:] in allowed:
                    return self.send_file(w.local(path[1:]), head)
                self.send_error(404)
            except (ValueError, OSError) as error:
                self.json_response({'error': str(error)}, 400)

        def do_POST(self):
            origin = self.headers.get('Origin')
            if not self.valid_host() or self.headers.get('X-Workflow-Token') != token or (origin and origin not in {f'http://127.0.0.1:{port}', f'http://localhost:{port}'}):
                return self.json_response({'error': '请求来源无效'}, 403)
            try:
                length = int(self.headers.get('Content-Length', '0'))
                if length > 65536:
                    raise ValueError('请求过大')
                data = json.loads(self.rfile.read(length) or b'{}'); w = Workflow(workflow.root)
                path = urllib.parse.urlparse(self.path).path
                if path == '/api/plan':
                    result = w.plan(data.get('only'), int(data.get('variants', 1)), 4)
                elif path == '/api/generate':
                    w.plan(data.get('only'), int(data.get('variants', 1)), 4)
                    if not w.key_ready():
                        raise ValueError('尚未配置API Key，请运行配置API.cmd。')
                    start_action(lambda: w.generate(data.get('only'), int(data.get('variants', 1)), 4)); result = {'started': True}
                elif path == '/api/select':
                    w.select(data['job_id'], data['candidate_id']); result = {'saved': True}
                elif path == '/api/timing':
                    w.update_timing(data['id'], data['source_start'], data['duration']); result = {'saved': True}
                elif path == '/api/import-inbox':
                    results = []
                    for job_id in w.jobs:
                        inbox = w.root / 'inbox' / job_id
                        if inbox.is_dir():
                            for file in sorted(inbox.iterdir()):
                                if file.suffix.lower() in {'.mp4', '.mov', '.mkv', '.webm'}:
                                    results.append(w.import_video(job_id, file)['id'])
                    result = {'imported': len(results), 'message': f'已扫描导入目录，共识别{len(results)}段素材。'}
                elif path == '/api/assemble':
                    w.resolved_timeline(); start_action(lambda: w.assemble('both')); result = {'started': True}
                elif path == '/api/stop':
                    if operation['running']:
                        raise ValueError('生成或粗剪仍在处理，请完成后再停止本地服务。')
                    result = {'message': '本地选片台已停止。'}
                    threading.Thread(target=server.shutdown, daemon=True).start()
                else:
                    return self.json_response({'error': '接口不存在'}, 404)
                self.json_response(result)
            except (ValueError, RuntimeError, TypeError, KeyError, OSError, StopIteration) as error:
                self.json_response({'error': str(error) or '未找到项目'}, 400)

    try:
        server = ThreadingHTTPServer(('127.0.0.1', port), Handler)
    except OSError:
        if open_browser:
            try:
                opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
                with opener.open(f'http://127.0.0.1:{port}/api/state', timeout=3) as response:
                    other = json.load(response)
                if other.get('project', {}).get('title') == workflow.project['title']:
                    webbrowser.open(f'http://127.0.0.1:{port}')
                    print('已打开正在运行的本地选片台。', flush=True)
                    return
            except (OSError, ValueError):
                pass
        raise RuntimeError(f'本地端口{port}正在使用，请换一个端口，例如 serve --port 8766。') from None
    print(f'选片台已启动：http://127.0.0.1:{port} （关闭此窗口即停止）', flush=True)
    if open_browser:
        webbrowser.open(f'http://127.0.0.1:{port}')
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
