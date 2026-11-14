from pathlib import Path
import json, shutil, subprocess, sys
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'output' / 'AI视频工作流'
SOURCE = ROOT / 'output/最终作业_不用麻烦她_3D交互原型/分镜图/30帧制作版'
OUT.mkdir(parents=True, exist_ok=True)
for name in ['assets', 'candidates', 'exports', 'vendor', 'web', 'reports', 'inbox']:
    (OUT / name).mkdir(exist_ok=True)
s = (SOURCE / 'clips.js').read_text(encoding='utf-8-sig')
clips, _ = json.JSONDecoder().raw_decode(s[s.index('['):])
jobs = []
for clip_id in ['E', '22', '35', '24']:
    c = next(x for x in clips if x['id'] == clip_id)
    frames = []
    for index, f in enumerate(c['frames']):
        shutil.copy2(SOURCE / f['file'], OUT / 'assets' / f['file'])
        frames.append({'file': f['file'], 'role': 'first_frame' if index == 0 else 'last_frame'})
    # Each request contains only its own action; cross-shot rules belong in the review checklist.
    shared = c['prompt'].split(' 固定')[0] if clip_id == 'E' else ''
    prompt = c['prompt']
    prompt = prompt.replace('助力灯在前次第22镜亮、次日第28镜经人求助后才亮。', '')
    prompt = prompt.replace('中间插入 22 号灯亮特写。', '')
    prompt = prompt.replace('接22号灯亮镜头。', '')
    prompt = prompt.replace('构图与36号下次同视角相似，但此时灯亮且无人被告知。', '此时灯亮且无人被告知。')
    checks = {
        'E': ['轮椅朝右，推行者始终在后方，车轮贴地', '前半段灯灭；后半段发现灯亮并停下'],
        '22': ['只亮同一枚琥珀灯，不生成文字', '电机声先于人物察觉'],
        '35': ['严格第一视角，双手仍握后推把', '灯已亮，呼吸停顿，人物不换位'],
        '24': ['轮椅已停，人物不换边', '追问有停顿，嘴部和手指不变形'],
    }
    jobs.append({'id': clip_id, 'title': c['title'], 'duration': c['duration'], 'frames': frames,
                 'prompt': prompt, 'dialogue': c['dialogue'], 'checks': checks[clip_id]})
project = {
    'schema_version': 1, 'title': '不用麻烦她 · 坡道 20 秒试片',
    'api': {'base_url': 'https://ark.cn-beijing.volces.com/api/v3',
            'model': 'doubao-seedance-2-5-260628', 'resolution': '720p', 'ratio': '16:9',
            'generate_audio': True, 'watermark': True, 'poll_seconds': 8, 'wait_seconds': 1200},
    'limits': {'max_total_api_tasks': 8, 'max_total_generated_seconds': 50},
    'jobs': jobs,
    'timeline': [
        {'id': '21', 'job_id': 'E', 'title': '人推上坡', 'source_start': 0, 'duration': 5},
        {'id': '22', 'job_id': '22', 'title': '助力灯亮', 'source_start': 0, 'duration': 3},
        {'id': '35', 'job_id': '35', 'title': '她察觉了', 'source_start': 0, 'duration': 4},
        {'id': '23', 'job_id': 'E', 'title': '停下', 'source_start': 5, 'duration': 5},
        {'id': '24', 'job_id': '24', 'title': '坡顶追问', 'source_start': 0, 'duration': 3},
    ],
    'subtitles': [
        {'start': 9, 'duration': 2.5, 'text': '灯怎么亮了？'},
        {'start': 17, 'duration': 3, 'text': '刚才这一路，你也在推？'},
    ],
    'audio_tracks': [],
    'notes': '20秒版仅验证生成、选片、剪辑交接，不是完整坡道场景。对白仅作为字幕占位，没有自动配音。完整对白保留在jobs中。',
}
(OUT / 'project.json').write_text(json.dumps(project, ensure_ascii=False, indent=2), encoding='utf-8')
vendor = ROOT / 'tmp/video-workflow/jianying-editor-skill/scripts/vendor/pyJianYingDraft'
dest = OUT / 'vendor/pyJianYingDraft'
if not dest.exists():
    shutil.copytree(vendor, dest, ignore=shutil.ignore_patterns('__pycache__'))
    p = dest / '__init__.py'
    body = p.read_text(encoding='utf-8')
    body = body.replace('if ISWIN:\n    from .jianying_controller import JianyingController, ExportResolution, ExportFramerate',
                        'if ISWIN:\n    try:\n        from .jianying_controller import JianyingController, ExportResolution, ExportFramerate\n    except ImportError:\n        pass  # Local workflow uses draft generation without UI automation dependencies.')
    p.write_text(body, encoding='utf-8')
license_file = ROOT / 'tmp/video-workflow/jianying-editor-skill/LICENSE'
if license_file.exists():
    shutil.copy2(license_file, OUT / 'vendor/JIAN YING SKILL LICENSE.txt')
thumbdir = ROOT / 'tmp/video-workflow/contact'
thumbdir.mkdir(exist_ok=True)
files = sorted((ROOT / '最终作业/视频片段').glob('*.mp4'))
entries = []
for i, video in enumerate(files):
    thumb = thumbdir / f'{i:02}.jpg'
    if not thumb.exists():
        subprocess.run(['ffmpeg', '-hide_banner', '-loglevel', 'error', '-ss', '0.4', '-i', str(video),
                        '-frames:v', '1', '-vf', 'scale=320:-1', '-y', str(thumb)], check=True)
    entries.append({'index': i, 'name': video.name, 'path': str(video), 'thumb': str(thumb)})
sheet = Image.new('RGB', (5*320, ((len(entries)+4)//5)*208), '#f4f1e9')
draw = ImageDraw.Draw(sheet)
for entry in entries:
    i = entry['index']; x = i % 5 * 320; y = i // 5 * 208
    im = Image.open(entry['thumb']); sheet.paste(im, (x, y))
    draw.text((x+8, y+182), f"{i:02}  {entry['name'].split('-')[3]}", fill='#1d2a26')
sheet.save(thumbdir / 'all_clips.jpg')
(thumbdir / 'index.json').write_text(json.dumps(entries, ensure_ascii=False, indent=2), encoding='utf-8')
print(json.dumps({'workflow': str(OUT), 'jobs': len(jobs), 'timeline_seconds': 20,
                  'contact_sheet': str(thumbdir/'all_clips.jpg')}, ensure_ascii=False))
