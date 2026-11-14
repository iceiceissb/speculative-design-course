"""Local video production workflow. No API request happens unless generate is invoked."""
from __future__ import annotations

import argparse
import base64
from contextlib import contextmanager
from datetime import datetime
import getpass
import hashlib
import json
import mimetypes
import os
from pathlib import Path
import re
import secrets
import shutil
import subprocess
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
import uuid

ROOT = Path(__file__).resolve().parent
TERMINAL = {'succeeded', 'failed', 'expired', 'cancelled'}


def stamp():
    return datetime.now().astimezone().isoformat(timespec='seconds')


def read_json(path, default=None):
    return json.loads(path.read_text(encoding='utf-8-sig')) if path.exists() else default


def write_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name + '.' + uuid.uuid4().hex + '.tmp')
    tmp.write_text(json.dumps(value, ensure_ascii=False, indent=2), encoding='utf-8')
    os.replace(tmp, path)


def load_key(root=ROOT):
    if os.environ.get('ARK_API_KEY', '').strip():
        return os.environ['ARK_API_KEY'].strip()
    path = root / '.env'
    if path.exists():
        for line in path.read_text(encoding='utf-8-sig').splitlines():
            if line.strip().startswith('ARK_API_KEY='):
                return line.split('=', 1)[1].strip().strip('"').strip("'")
    return ''


def run_tool(args):
    flags = {'creationflags': subprocess.CREATE_NO_WINDOW} if os.name == 'nt' else {}
    result = subprocess.run(args, capture_output=True, text=True, encoding='utf-8', errors='replace', **flags)
    if result.returncode:
        raise RuntimeError(result.stderr[-2500:] or '工具运行失败')
    return result.stdout


def probe(path):
    result = json.loads(run_tool(['ffprobe', '-v', 'error', '-show_streams', '-show_format', '-of', 'json', str(path)]))
    video = next((s for s in result.get('streams', []) if s['codec_type'] == 'video'), None)
    if not video:
        raise ValueError('没有视频轨道')
    duration = float(result['format'].get('duration') or video.get('duration') or 0)
    if duration <= 0:
        raise ValueError('视频时长无效')
    return {'duration': duration, 'width': video['width'], 'height': video['height'],
            'has_audio': any(s['codec_type'] == 'audio' for s in result.get('streams', []))}


@contextmanager
def exclusive(root):
    """OS-managed lock releases even if a process is interrupted."""
    root.mkdir(parents=True, exist_ok=True)
    with (root / '.operation.lock').open('a+b') as handle:
        handle.seek(0)
        if not handle.read(1):
            handle.write(b'0'); handle.flush()
        handle.seek(0)
        try:
            if os.name == 'nt':
                import msvcrt
                msvcrt.locking(handle.fileno(), msvcrt.LK_NBLCK, 1)
            else:
                import fcntl
                fcntl.flock(handle, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except OSError:
            raise RuntimeError('另一个生成或剪辑操作正在运行，请稍后再试。') from None
        try:
            yield
        finally:
            handle.seek(0)
            if os.name == 'nt':
                msvcrt.locking(handle.fileno(), msvcrt.LK_UNLCK, 1)
            else:
                fcntl.flock(handle, fcntl.LOCK_UN)


class SeedanceClient:
    def __init__(self, base_url, key, *, allow_test_http=False):
        self.base = base_url.rstrip('/')
        parsed = urllib.parse.urlparse(self.base)
        valid = parsed.scheme == 'https' and parsed.hostname in {'ark.cn-beijing.volces.com', 'ark.cn-shanghai.volces.com'}
        test = allow_test_http and parsed.scheme == 'http' and parsed.hostname in {'127.0.0.1', 'localhost'}
        if not (valid or test):
            raise ValueError('API 地址必须是官方火山方舟 HTTPS 地址。')
        self.key, self.test = key, test
        # Honor local proxies for real network calls. Test server bypasses proxies.
        self.opener = urllib.request.build_opener(urllib.request.ProxyHandler({})) if test else urllib.request.build_opener()

    def request(self, method, suffix, payload=None):
        data = json.dumps(payload).encode('utf-8') if payload is not None else None
        request = urllib.request.Request(self.base + suffix, data=data, method=method,
                  headers={'Authorization': 'Bearer ' + self.key, 'Content-Type': 'application/json'})
        # A POST is never retried: the remote side may already have created a paid task.
        for attempt in range(3 if method == 'GET' else 1):
            try:
                with self.opener.open(request, timeout=45) as response:
                    return json.load(response)
            except urllib.error.HTTPError as error:
                body = error.read(16384).decode('utf-8', errors='replace')
                if method == 'GET' and error.code in {429, 500, 502, 503, 504} and attempt < 2:
                    time.sleep(2 ** attempt); continue
                # Only explicit 4xx rejections conclusively mean the task was not accepted.
                exc = RuntimeError(f'方舟 HTTP {error.code}: {body[:1000].replace(self.key, "[REDACTED]")}')
                exc.definite_rejection = 400 <= error.code < 500
                raise exc from None
            except (urllib.error.URLError, TimeoutError, OSError) as error:
                if method == 'GET' and attempt < 2:
                    time.sleep(2 ** attempt); continue
                raise RuntimeError('方舟网络请求未完成；请检查网络或代理。') from None

    def create(self, payload):
        result = self.request('POST', '/contents/generations/tasks', payload)
        task_id = result.get('id')
        if not task_id or not re.fullmatch(r'[A-Za-z0-9_-]{1,160}', task_id):
            raise RuntimeError('方舟没有返回有效任务 ID；请到控制台核对，避免重复计费。')
        return task_id

    def get(self, task_id):
        if not re.fullmatch(r'[A-Za-z0-9_-]{1,160}', task_id):
            raise ValueError('任务 ID 无效')
        return self.request('GET', '/contents/generations/tasks/' + task_id)

    def download(self, url, destination):
        parsed = urllib.parse.urlparse(url)
        test = self.test and parsed.scheme == 'http' and parsed.hostname in {'127.0.0.1', 'localhost'}
        if not (parsed.scheme == 'https' or test):
            raise ValueError('结果视频必须使用 HTTPS 下载。')
        destination.parent.mkdir(parents=True, exist_ok=True)
        partial = destination.with_suffix('.part')
        # CDN download is a separate unauthenticated request. Never forward the API key.
        with self.opener.open(urllib.request.Request(url), timeout=60) as response, partial.open('wb') as target:
            shutil.copyfileobj(response, target)
        info = probe(partial)
        os.replace(partial, destination)
        return info


class Workflow:
    def __init__(self, root=ROOT):
        self.root = Path(root).resolve()
        self.project = read_json(self.root / 'project.json')
        if not self.project:
            raise ValueError('缺少 project.json')
        ids = [job['id'] for job in self.project['jobs']]
        if len(ids) != len(set(ids)) or any(not re.fullmatch(r'[A-Za-z0-9_-]+', x) for x in ids):
            raise ValueError('镜头任务编号必须唯一，且只含字母、数字、下划线或连字符。')
        self.jobs = {job['id']: job for job in self.project['jobs']}
        for item in self.project['timeline']:
            if item['job_id'] not in self.jobs or item['duration'] <= 0 or item['source_start'] < 0:
                raise ValueError('时间线配置无效')
        self.state_path = self.root / 'state.json'

    def state(self):
        return read_json(self.state_path, {'candidates': [], 'selection': {}, 'created_at': stamp()})

    def save(self, state):
        state['updated_at'] = stamp()
        write_json(self.state_path, state)

    def local(self, relative):
        p = (self.root / relative).resolve()
        if not p.is_relative_to(self.root):
            raise ValueError('路径超出工作流目录')
        return p

    def key_ready(self):
        return bool(load_key(self.root))

    def doctor(self):
        missing = [frame['file'] for job in self.jobs.values() for frame in job['frames']
                   if not self.local('assets/' + frame['file']).is_file()]
        return {'python': sys.version.split()[0], 'ffmpeg': bool(shutil.which('ffmpeg')),
                'ffprobe': bool(shutil.which('ffprobe')), 'api_key_configured': self.key_ready(),
                'missing_images': missing, 'jobs': len(self.jobs),
                'timeline_seconds': sum(x['duration'] for x in self.project['timeline']),
                'api_model': self.project['api']['model']}

    def payload(self, job, seed):
        api = self.project['api']
        if not 4 <= job['duration'] <= 30:
            raise ValueError('Seedance 2.5 的视频时长须为4至30秒。')
        content = [{'type': 'text', 'text': job['prompt']}]
        frames = job['frames']
        if [f['role'] for f in frames] not in [['first_frame'], ['first_frame', 'last_frame']]:
            raise ValueError('当前流程只支持首帧或首尾帧输入。')
        for frame in frames:
            path = self.local('assets/' + frame['file'])
            if not path.is_relative_to(self.root / 'assets'):
                raise ValueError('参考图片必须位于 assets 目录。')
            mime = mimetypes.guess_type(path.name)[0] or 'image/png'
            blob = path.read_bytes()
            if len(blob) >= 30 * 1024 * 1024:
                raise ValueError('参考图片超过30MB，需先压缩。')
            content.append({'type': 'image_url', 'role': frame['role'],
                            'image_url': {'url': 'data:' + mime + ';base64,' + base64.b64encode(blob).decode('ascii')}})
        payload = {'model': api['model'], 'content': content, 'duration': job['duration'],
                'ratio': api['ratio'], 'resolution': api['resolution'], 'seed': seed,
                'generate_audio': api['generate_audio'], 'watermark': api.get('watermark', True)}
        if len(json.dumps(payload).encode('utf-8')) > 64 * 1024 * 1024:
            raise ValueError('请求体超过64MB，请压缩参考图片。')
        return payload

    def signature(self, job):
        payload = self.payload(job, 0)
        return hashlib.sha256(json.dumps(payload, sort_keys=True, ensure_ascii=False).encode()).hexdigest()

    def plan(self, only=None, variants=1, max_new_tasks=4):
        if not 1 <= variants <= 8 or not 1 <= max_new_tasks <= 8:
            raise ValueError('候选数与本轮新增任务数须为1至8。')
        chosen = list(self.jobs) if not only else only
        if not chosen or any(x not in self.jobs for x in chosen) or len(chosen) != len(set(chosen)):
            raise ValueError('任务编号不存在或重复。')
        state = self.state(); pending = []
        for job_id in chosen:
            job = self.jobs[job_id]; sig = self.signature(job)
            api_candidates = [c for c in state['candidates'] if c['job_id'] == job_id and c.get('signature') == sig and c['source'] == 'seedance']
            # Failed/rejected candidates remain counted. Increase variants explicitly to request another.
            for index in range(len(api_candidates), variants):
                pending.append({'job_id': job_id, 'signature': sig, 'variant': index+1, 'duration': job['duration']})
        if len(pending) > max_new_tasks:
            raise ValueError(f'本轮需新增{len(pending)}个任务，超过本轮上限{max_new_tasks}。')
        booked = [c for c in state['candidates'] if c['source'] == 'seedance' and c['status'] != 'rejected']
        total_seconds = sum(c['requested_duration'] for c in booked)
        limits = self.project['limits']
        if len(booked) + len(pending) > limits['max_total_api_tasks']:
            raise ValueError('超过项目累计API任务上限，请先核对已生成候选和预算。')
        if total_seconds + sum(x['duration'] for x in pending) > limits['max_total_generated_seconds']:
            raise ValueError('超过项目累计生成秒数上限，请先核对预算。')
        return {'new_tasks': pending, 'new_generated_seconds': sum(x['duration'] for x in pending),
                'booked_tasks': len(booked), 'booked_seconds': total_seconds,
                'resolution': self.project['api']['resolution'], 'model': self.project['api']['model'],
                'note': '费用以方舟结算为准；任务数和秒数上限不等同于人民币费用上限。'}

    def thumbnail(self, candidate):
        video = self.local(candidate['file']); image = video.with_suffix('.jpg')
        run_tool(['ffmpeg', '-hide_banner', '-loglevel', 'error', '-i', str(video), '-frames:v', '1',
                  '-vf', 'scale=480:-1', '-y', str(image)])
        candidate['thumbnail'] = image.relative_to(self.root).as_posix()

    def generate(self, only=None, variants=1, max_new_tasks=4, client=None):
        with exclusive(self.root):
            plan = self.plan(only, variants, max_new_tasks)
            key = load_key(self.root)
            if not client and not key:
                raise RuntimeError('尚未配置 API Key。请运行“配置API.cmd”，或设置 ARK_API_KEY。')
            client = client or SeedanceClient(self.project['api']['base_url'], key)
            state = self.state()
            # Any interrupted submission is ambiguous and is never automatically recreated.
            for candidate in state['candidates']:
                if candidate['status'] == 'submitting':
                    candidate['status'] = 'uncertain'
                    candidate['error'] = '提交时被中断，请在方舟控制台核对任务ID后关联。'
            self.save(state)
            for task in plan['new_tasks']:
                job = self.jobs[task['job_id']]; seed = secrets.randbelow(2**31)
                candidate = {'id': uuid.uuid4().hex[:16], 'job_id': job['id'], 'source': 'seedance',
                    'status': 'submitting', 'signature': task['signature'], 'variant': task['variant'],
                    'seed': seed, 'requested_duration': job['duration'], 'created_at': stamp(),
                    'snapshot': {'job': job, 'api': self.project['api']}}
                state['candidates'].append(candidate); self.save(state)
                try:
                    candidate['task_id'] = client.create(self.payload(job, seed))
                    candidate['status'] = 'queued'; self.save(state)
                except Exception as error:
                    candidate['status'] = 'rejected' if getattr(error, 'definite_rejection', False) else 'uncertain'
                    candidate['error'] = str(error).replace(key, '[REDACTED]') if key else str(error)
                    self.save(state)
                    raise RuntimeError('提交未完成，已保存现场。' + candidate['error']) from None
            targets = [c for c in state['candidates'] if c['source'] == 'seedance' and c.get('task_id')
                       and (not only or c['job_id'] in only)
                       and c['status'] not in {'failed', 'expired', 'cancelled', 'rejected'}
                       and not (c['status'] == 'succeeded' and c.get('file') and self.local(c['file']).is_file())]
            deadline = time.monotonic() + self.project['api'].get('wait_seconds', 1200)
            while targets and time.monotonic() < deadline:
                for candidate in targets[:]:
                    result = client.get(candidate['task_id'])
                    candidate['status'] = result.get('status', 'running')
                    candidate['usage'] = result.get('usage', {})
                    self.save(state)
                    if candidate['status'] == 'succeeded':
                        url = result.get('content', {}).get('video_url')
                        if not url:
                            raise RuntimeError('生成成功但缺少视频URL；下次继续查询此任务，不重新提交。')
                        relative = 'candidates/' + candidate['job_id'] + '/' + candidate['id'] + '.mp4'
                        candidate['media'] = client.download(url, self.local(relative))
                        candidate['file'] = relative
                        self.thumbnail(candidate); self.save(state); targets.remove(candidate)
                    elif candidate['status'] in TERMINAL:
                        candidate['error'] = json.dumps(result.get('error', {}), ensure_ascii=False)
                        self.save(state); targets.remove(candidate)
                if targets:
                    time.sleep(self.project['api'].get('poll_seconds', 8))
            unresolved = sum(c['status'] in {'uncertain', 'submitting'} for c in state['candidates'] if c['source'] == 'seedance')
            failed = sum(c['status'] in {'failed', 'expired', 'cancelled', 'rejected'} for c in state['candidates'] if c['source'] == 'seedance')
            message = ('有提交结果不确定的任务，请核对并关联方舟任务ID。' if unresolved else
                       '已有任务失败，成功候选已保存；需要新候选时请显式请求。' if failed else
                       '任务与视频已保存。' if not targets else
                       '等待时间结束，任务仍在运行。再次生成会继续查询已有任务。')
            return {'completed': not targets and not unresolved and not failed, 'pending': len(targets),
                    'uncertain': unresolved, 'failed': failed, 'new_tasks': len(plan['new_tasks']), 'message': message}

    def attach_task(self, candidate_id, task_id):
        if not re.fullmatch(r'[A-Za-z0-9_-]{1,160}', task_id):
            raise ValueError('任务 ID 无效')
        with exclusive(self.root):
            state = self.state(); c = next(c for c in state['candidates'] if c['id'] == candidate_id)
            if c['status'] not in {'uncertain', 'submitting'}:
                raise ValueError('仅可关联提交结果不确定的候选')
            c['task_id'] = task_id; c['status'] = 'queued'; c.pop('error', None); self.save(state)

    def import_video(self, job_id, source):
        if job_id not in self.jobs:
            raise ValueError('镜头任务不存在')
        source = Path(source).resolve(); info = probe(source)
        with exclusive(self.root):
            state = self.state(); digest = hashlib.sha256(source.read_bytes()).hexdigest()
            existing = next((c for c in state['candidates'] if c['job_id'] == job_id and c.get('sha256') == digest), None)
            if existing:
                return existing
            candidate_id = uuid.uuid4().hex[:16]
            target = self.local('candidates/' + job_id + '/' + candidate_id + source.suffix.lower())
            target.parent.mkdir(parents=True, exist_ok=True); shutil.copy2(source, target)
            c = {'id': candidate_id, 'job_id': job_id, 'source': 'imported', 'status': 'succeeded',
                 'file': target.relative_to(self.root).as_posix(), 'original_name': source.name,
                 'sha256': digest, 'media': info, 'created_at': stamp()}
            self.thumbnail(c); state['candidates'].append(c); self.save(state); return c

    def select(self, job_id, candidate_id):
        with exclusive(self.root):
            state = self.state()
            candidate = next((c for c in state['candidates'] if c['id'] == candidate_id and c['job_id'] == job_id), None)
            if not candidate or candidate['status'] != 'succeeded' or not candidate.get('file'):
                raise ValueError('候选尚未生成完成')
            if not self.local(candidate['file']).is_file():
                raise ValueError('候选文件已丢失')
            state['selection'][job_id] = candidate_id; self.save(state)

    def resolved_timeline(self):
        state = self.state(); rows = []; position = 0
        for item in self.project['timeline']:
            candidate_id = state['selection'].get(item['job_id'])
            c = next((c for c in state['candidates'] if c['id'] == candidate_id), None)
            if not c or c['status'] != 'succeeded' or not c.get('file'):
                raise ValueError('请先为任务 ' + item['job_id'] + ' 选片。')
            file = self.local(c['file']); media = probe(file)
            if item['source_start'] + item['duration'] > media['duration'] + .025:
                raise ValueError(f"任务{item['job_id']}的片段短于所需截取范围，请换片或调整时间线。")
            rows.append(dict(item, candidate_id=c['id'], file=str(file), media=media, target_start=position))
            position += item['duration']
        return rows

    def update_timing(self, timeline_id, source_start, duration):
        start, length = float(source_start), float(duration)
        if not (0 <= start <= 600 and 0 < length <= 120):
            raise ValueError('截取时间无效')
        with exclusive(self.root):
            item = next(x for x in self.project['timeline'] if x['id'] == timeline_id)
            item['source_start'], item['duration'] = start, length
            write_json(self.root / 'project.json', self.project)

    def assemble(self, kind='mp4', **kwargs):
        from editing import assemble
        with exclusive(self.root):
            return assemble(self, kind=kind, **kwargs)

    def public_state(self):
        state = self.state()
        signatures = {key: self.signature(job) for key, job in self.jobs.items()}
        candidates = [dict({k: v for k, v in c.items() if k not in {'snapshot', 'signature', 'sha256'}},
                          current_version=c.get('signature') == signatures[c['job_id']]) for c in state['candidates']]
        exports = read_json(self.root / 'exports/latest.json', {})
        return {'project': self.project, 'candidates': candidates, 'selection': state['selection'],
                'doctor': self.doctor(), 'exports': exports}


def main():
    parser = argparse.ArgumentParser(description='AI视频工作流：生成、选片、粗剪')
    sub = parser.add_subparsers(dest='command', required=True)
    sub.add_parser('doctor'); sub.add_parser('configure-key')
    p = sub.add_parser('stop'); p.add_argument('--port', type=int, default=8765)
    for command in ['plan', 'generate']:
        p = sub.add_parser(command)
        p.add_argument('--only', help='任务编号，逗号分隔，例如 E,35')
        p.add_argument('--variants', type=int, default=1, help='每任务累计目标候选数')
        p.add_argument('--max-new-tasks', type=int, default=4)
    p = sub.add_parser('import'); p.add_argument('--job', required=True); p.add_argument('--file', required=True)
    p = sub.add_parser('select'); p.add_argument('--job', required=True); p.add_argument('--candidate', required=True)
    p = sub.add_parser('attach-task'); p.add_argument('--candidate', required=True); p.add_argument('--task-id', required=True)
    p = sub.add_parser('assemble'); p.add_argument('--kind', choices=['mp4', 'draft', 'both'], default='both')
    p = sub.add_parser('serve'); p.add_argument('--port', type=int, default=8765); p.add_argument('--open', action='store_true')
    args = parser.parse_args(); workflow = Workflow()
    if args.command == 'serve':
        from server import serve
        return serve(workflow, args.port, args.open)
    if args.command == 'stop':
        opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
        base = f'http://127.0.0.1:{args.port}'
        with opener.open(base + '/api/state', timeout=3) as response:
            current = json.load(response)
        request = urllib.request.Request(base + '/api/stop', data=b'{}', method='POST',
                  headers={'Content-Type': 'application/json', 'X-Workflow-Token': current['token']})
        with opener.open(request, timeout=3) as response:
            print(json.load(response)['message'])
        return
    if args.command == 'configure-key':
        key = getpass.getpass('请输入方舟 API Key（输入不显示，不会发送到聊天）：').strip()
        if not key or any(c.isspace() for c in key):
            raise ValueError('API Key为空或包含空白字符')
        (ROOT / '.env').write_text('ARK_API_KEY=' + key + '\n', encoding='utf-8')
        result = {'message': '已写入本地 .env；尚未发起生成请求。'}
    elif args.command == 'doctor':
        result = workflow.doctor()
    elif args.command in {'plan', 'generate'}:
        result = getattr(workflow, args.command)(args.only.split(',') if args.only else None, args.variants, args.max_new_tasks)
    elif args.command == 'import':
        result = workflow.import_video(args.job, args.file)
    elif args.command == 'select':
        workflow.select(args.job, args.candidate); result = {'selected': args.candidate}
    elif args.command == 'attach-task':
        workflow.attach_task(args.candidate, args.task_id); result = {'associated': args.task_id}
    else:
        result = workflow.assemble(args.kind)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    try:
        main()
    except (ValueError, RuntimeError, OSError, StopIteration) as error:
        message = str(error) or '没有找到指定候选或任务'
        key = load_key()
        if key:
            message = message.replace(key, '[REDACTED]')
        print('未完成：' + message, file=sys.stderr)
        sys.exit(1)
