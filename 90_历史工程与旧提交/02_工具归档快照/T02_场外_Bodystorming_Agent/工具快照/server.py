"""Run with Python 3.10+: python server.py. No backend dependencies."""
import argparse
import json
import mimetypes
import os
import re
import threading
import urllib.parse
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from agent.engine import Engine, NODES, export_markdown, prompt
from agent.model import AgentError, ModelClient
from agent.storage import Store

ROOT = Path(__file__).resolve().parent


def make_server(port=8765, data_dir=None, model=None):
    store = Store(Path(data_dir or ROOT / 'data') / 'workbench.sqlite3')
    client = model or ModelClient()
    engine = Engine(store, client)

    class Handler(BaseHTTPRequestHandler):
        def log_message(self, fmt, *args):
            pass

        def send(self, data, status=200, content_type='application/json; charset=utf-8'):
            body = json.dumps(data, ensure_ascii=False).encode() if isinstance(data, (dict, list)) else (data.encode() if isinstance(data, str) else data)
            self.send_response(status)
            self.send_header('Content-Type', content_type)
            self.send_header('Content-Length', str(len(body)))
            self.send_header('Cache-Control', 'no-store')
            self.send_header('X-Content-Type-Options', 'nosniff')
            self.send_header('X-Frame-Options', 'DENY')
            self.end_headers()
            self.wfile.write(body)

        def do_GET(self):
            try:
                path = urllib.parse.urlsplit(self.path).path
                if path == '/api/health':
                    return self.send({'ok': True, 'model': client.public()})
                if path == '/api/config':
                    return self.send(client.public())
                if path == '/api/sessions':
                    return self.send(store.listing())
                if path == '/api/knowledge':
                    return self.send(store.documents())
                if path == '/api/workflow':
                    return self.send([n | {'prompt_text': prompt(n['prompt']) if n['prompt'] else ''} for n in NODES])
                match = re.fullmatch(r'/api/sessions/([a-f0-9]+)(?:/(export))?', path)
                if match:
                    doc = store.get(match[1])
                    if match[2]:
                        query = urllib.parse.parse_qs(urllib.parse.urlsplit(self.path).query)
                        return self.send(export_markdown(doc), content_type='text/markdown; charset=utf-8') if query.get('format') == ['md'] else self.send(doc)
                    return self.send(doc)
                if path.startswith('/api/'):
                    return self.send({'error': '没有此接口。'}, 404)
                root = ROOT / 'dist'
                candidate = (root / urllib.parse.unquote(path).lstrip('/')).resolve()
                if not candidate.is_relative_to(root.resolve()):
                    return self.send({'error': '无效路径。'}, 403)
                if not candidate.is_file():
                    if Path(path).suffix:
                        return self.send({'error': '资源不存在。'}, 404)
                    candidate = root / 'index.html'
                if not candidate.exists():
                    return self.send('尚未构建前端，请在项目中执行 npm install 和 npm run build。', 503, 'text/plain; charset=utf-8')
                mime = mimetypes.guess_type(candidate.name)[0] or 'application/octet-stream'
                if candidate.suffix == '.js':
                    mime = 'text/javascript'
                return self.send(candidate.read_bytes(), content_type=mime)
            except KeyError:
                self.send({'error': '演练不存在。'}, 404)

        def do_POST(self):
            try:
                origin = self.headers.get('Origin')
                allowed = {f'http://127.0.0.1:{self.server.server_port}', f'http://localhost:{self.server.server_port}'}
                if origin and origin not in allowed:
                    return self.send({'error': '仅接受本地工作台的请求。'}, 403)
                if not self.headers.get('Content-Type', '').startswith('application/json'):
                    return self.send({'error': '请求必须为 JSON。'}, 415)
                length = int(self.headers.get('Content-Length', '0'))
                if length <= 0 or length > 10_000_000:
                    return self.send({'error': '请求为空或超过 10MB。'}, 413)
                data = json.loads(self.rfile.read(length))
                if not isinstance(data, dict):
                    raise AgentError('请求格式不正确。')
                path = urllib.parse.urlsplit(self.path).path
                if path == '/api/config':
                    return self.send(client.configure(data))
                if path == '/api/config/test':
                    answer = client.complete('仅返回JSON对象：{"ok":true}', {'task': 'connection test'})
                    if answer.get('ok') is not True:
                        raise AgentError('模型有响应，但没有通过 JSON 格式测试。')
                    return self.send({'ok': True, 'message': '已完成一次真实模型请求。'})
                if path == '/api/sessions':
                    for key in ('story', 'constraints', 'title', 'participants', 'remaining'):
                        if key in data and not isinstance(data[key], str):
                            raise AgentError('演练字段必须是文本。')
                    if data.get('mode', 'demo') not in ('demo', 'live'):
                        raise AgentError('请选择演示或真实模型模式。')
                    return self.send(store.create(data), 201)
                if path == '/api/knowledge':
                    title, text, source = (str(data.get(k, '')).strip() for k in ('title', 'text', 'source'))
                    if not title or not text or len(text) > 300_000:
                        raise AgentError('请填写资料标题和正文，正文最多 30 万字符。')
                    return self.send(store.add_document(title[:180], source[:1000], text), 201)
                if path == '/api/observe':
                    image = data.get('image', '')
                    if not isinstance(image, str) or not re.fullmatch(r'data:image/(?:png|jpeg|webp);base64,[A-Za-z0-9+/=\r\n]+', image):
                        raise AgentError('请上传 PNG、JPEG 或 WebP 照片。')
                    answer = client.complete(prompt('observe.md'), {'note': str(data.get('note', ''))}, image=image)
                    if not all(isinstance(answer.get(k), str) for k in ('observation', 'uncertainty')):
                        raise AgentError('照片描述节点的返回格式不正确。')
                    return self.send(answer)
                match = re.fullmatch(r'/api/sessions/([a-f0-9]+)/(generate|select|guide|feedback)', path)
                if match:
                    sid, action = match.groups()
                    if action == 'generate':
                        return self.send(engine.generate(sid))
                    if action == 'select':
                        return self.send(engine.select(sid, data.get('event_id')))
                    if action == 'guide':
                        return self.send(engine.guide(sid, str(data.get('observation', '')), data.get('state')))
                    return self.send(engine.feedback(sid, data.get('hint_id'), data.get('feedback')))
                self.send({'error': '没有此接口。'}, 404)
            except AgentError as exc:
                self.send({'error': str(exc)}, 400)
            except KeyError:
                self.send({'error': '演练不存在。'}, 404)
            except (ValueError, TypeError):
                self.send({'error': '输入格式不正确。'}, 400)
            except Exception:
                self.send({'error': '本地处理失败，请检查服务窗口及运行记录。'}, 500)

    server = ThreadingHTTPServer(('127.0.0.1', port), Handler)
    server.daemon_threads = True
    server.store, server.engine, server.model = store, engine, client
    return server


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--port', type=int, default=8765)
    parser.add_argument('--no-browser', action='store_true')
    parser.add_argument('--data-dir', type=Path, default=None)
    args = parser.parse_args()
    server = None
    for candidate in range(args.port, args.port+20):
        try:
            server = make_server(candidate, args.data_dir)
            break
        except OSError:
            continue
    if not server:
        raise SystemExit('没有可用的本地端口，请关闭旧服务后重试。')
    url = f'http://127.0.0.1:{server.server_port}'
    print(f'Out-Actor workbench: {url}', flush=True)
    print('Keep this window open. Ctrl+C stops the workbench.', flush=True)
    if not args.no_browser:
        threading.Timer(0.7, lambda: webbrowser.open(url)).start()
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
