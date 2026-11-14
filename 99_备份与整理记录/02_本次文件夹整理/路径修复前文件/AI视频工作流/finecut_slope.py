"""Build a reviewed slope edit, offline dialogue, subtitles and a full-skill draft."""
from datetime import datetime, timedelta, timezone
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import time
import uuid
import wave

import numpy as np

ROOT = Path(__file__).resolve().parent
OUT = ROOT / 'exports' / '坡道精剪_v1_20261009'
FPS = 24


def read(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))


def write(path, obj):
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2), encoding='utf-8')


def run(args):
    result = subprocess.run(args, capture_output=True, text=True, encoding='utf-8',
                            errors='replace', timeout=120)
    if result.returncode:
        raise RuntimeError(result.stderr[-4000:])
    return result


def probe(path):
    return json.loads(run(['ffprobe', '-v', 'error', '-show_format', '-show_streams',
                          '-of', 'json', str(path)]).stdout)


def wav(path, samples, rate=48000):
    samples = np.asarray(samples)
    with wave.open(str(path), 'wb') as file:
        file.setnchannels(1 if samples.ndim == 1 else samples.shape[1])
        file.setsampwidth(2)
        file.setframerate(rate)
        file.writeframes((np.clip(samples, -1, 1) * 32767).astype('<i2').tobytes())


def sounds(total):
    folder = OUT / 'sound'
    folder.mkdir(exist_ok=True)
    rate = 48000
    count = round(total * rate)
    rng = np.random.default_rng(20261009)
    noise = rng.normal(size=count)
    freq = np.fft.rfftfreq(count, 1 / rate)
    shaping = np.where((freq > 120) & (freq < 1700), 1 / np.sqrt(np.maximum(freq, 1)), 0)
    wind = np.fft.irfft(np.fft.rfft(noise) * shaping, n=count)
    wind *= .0045 / max(np.sqrt(np.mean(wind ** 2)), 1e-9)
    t = np.arange(count) / rate
    wind *= np.minimum(t / .3, 1) * np.minimum((total - t) / .8, 1)
    wav(folder / '坡道环境底声.wav', wind)
    length = 6.7
    t = np.arange(round(length * rate)) / rate
    envelope = np.minimum(t / 1.1, 1) * np.minimum((length - t) / .7, 1)
    motor = .022 * (np.sin(2 * np.pi * 88 * t) + .22 * np.sin(2 * np.pi * 176 * t))
    wav(folder / '轻电机声.wav', motor * envelope)
    t = np.arange(round(.12 * rate)) / rate
    cue = .013 * np.sin(2 * np.pi * (760 * t + 280 * t ** 2)) * np.sin(np.pi * t / .12) ** 2
    wav(folder / '灯亮轻提示.wav', cue)
    return [
        {'id': 'wind', 'file': str(folder / '坡道环境底声.wav'), 'start': 0, 'duration': total, 'volume': 1},
        {'id': 'motor', 'file': str(folder / '轻电机声.wav'), 'start': 3.0, 'duration': length, 'volume': 1},
        {'id': 'light', 'file': str(folder / '灯亮轻提示.wav'), 'start': 3.09, 'duration': .12, 'volume': 1},
    ]


def clips():
    state = read(ROOT / 'state.json')
    selected = state['selection']
    candidates = {item['id']: item for item in state['candidates']}
    source = {job: str(ROOT / candidates[candidate]['file']) for job, candidate in selected.items()}
    index = read(ROOT.parents[1] / 'tmp/video-workflow/contact/index.json')
    # Bounds inspected against actual camera cuts; avoid replaying the same action.
    specs = [
        {'title': '推行建立', 'source': source['E'], 'source_start': .025, 'source_duration': 1.6, 'frames': 48},
        {'title': '车轮与推力', 'source': index[8]['path'], 'source_start': .85, 'source_duration': .8, 'frames': 24},
        {'title': '助力灯亮', 'source': source['22'], 'source_start': 1.35, 'source_duration': .933333, 'frames': 28},
        {'title': '主观发现', 'source': source['35'], 'source_start': 0, 'source_duration': 2.4, 'frames': 72},
        {'title': '停下留白', 'source': index[21]['path'], 'source_start': .5, 'source_duration': 2.2, 'frames': 66},
        {'title': '指灯追问', 'source': source['24'], 'source_start': .1, 'source_duration': 1.6, 'frames': 48},
        {'title': '助力灯切回', 'source': source['35'], 'source_start': 2.4, 'source_duration': 1.5, 'frames': 45},
        {'title': '告知边界与反应', 'source': source['24'], 'source_start': 1.7, 'source_duration': 2.3,
         'frames': 101, 'motion_frames': 69, 'crop': [720, 405, 100, 45]},
    ]
    folder = OUT / '镜头素材'
    folder.mkdir(exist_ok=True)
    at = 0
    for number, spec in enumerate(specs, 1):
        target = folder / f'{number:02}_{spec["title"]}.mp4'
        duration = spec['frames'] / FPS
        motion = spec.get('motion_frames', spec['frames']) / FPS
        speed = spec['source_duration'] / motion
        vf = []
        if spec.get('crop'):
            w, h, x, y = spec['crop']
            vf += [f'crop={w}:{h}:{x}:{y}', 'scale=1280:720:flags=lanczos']
        else:
            vf += ['scale=1280:720:flags=lanczos']
        vf += [f'setpts=(PTS-STARTPTS)/{speed}', 'fps=24',
               'eq=contrast=1.025:brightness=0.003:saturation=0.97',
               f'tpad=stop_mode=clone:stop_duration={duration-motion+.15}',
               f'trim=end_frame={spec["frames"]}', 'setpts=PTS-STARTPTS', 'setsar=1']
        has_audio = any(s['codec_type'] == 'audio' for s in probe(Path(spec['source']))['streams'])
        video_only = folder / f'{number:02}_video.mp4'
        audio_only = folder / f'{number:02}_audio.m4a'
        args = ['ffmpeg', '-hide_banner', '-loglevel', 'error', '-nostdin', '-filter_threads', '1',
                '-ss', str(spec['source_start']), '-t', str(spec['source_duration']), '-i', spec['source'],
                '-an', '-vf', ','.join(vf), '-frames:v', str(spec['frames']), '-c:v', 'libx264',
                '-threads', '2', '-preset', 'fast', '-crf', '16', '-pix_fmt', 'yuv420p',
                '-movflags', '+faststart', '-y', str(video_only)]
        run(args)
        if has_audio:
            af = (f'atempo={speed},highpass=f=80,lowpass=f=7000,loudnorm=I=-32:TP=-9:LRA=7,'
                  f'apad=whole_dur={duration},atrim=duration={duration},afade=t=in:d=0.045,'
                  f'afade=t=out:st={max(0,duration-.12)}:d=0.12')
            audio_args = ['ffmpeg', '-hide_banner', '-loglevel', 'error', '-nostdin',
                          '-ss', str(spec['source_start']), '-t', str(spec['source_duration']),
                          '-i', spec['source'], '-vn', '-af', af]
        else:
            audio_args = ['ffmpeg', '-hide_banner', '-loglevel', 'error', '-nostdin',
                          '-f', 'lavfi', '-i', 'anullsrc=r=48000:cl=stereo']
        audio_args += ['-t', str(duration), '-c:a', 'aac', '-ar', '48000', '-ac', '2',
                       '-y', str(audio_only)]
        run(audio_args)
        run(['ffmpeg', '-hide_banner', '-loglevel', 'error', '-nostdin',
             '-i', str(video_only), '-i', str(audio_only), '-map', '0:v:0', '-map', '1:a:0',
             '-c', 'copy', '-t', str(duration), '-movflags', '+faststart', '-y', str(target)])
        info = probe(target)
        video_duration = float(next(s for s in info['streams'] if s['codec_type'] == 'video')['duration'])
        if abs(video_duration - duration) > .043:
            raise RuntimeError(f'镜头时长不正确：{spec["title"]}, {video_duration}')
        spec.update(file=str(target), start=at, duration=duration, speed=speed)
        at += duration
        print(f'镜头 {number}/8：{spec["title"]} {duration:.3f}s', flush=True)
    return specs, at


def timecode(seconds, separator=','):
    ms = round(seconds * 1000)
    hours, ms = divmod(ms, 3600000)
    minutes, ms = divmod(ms, 60000)
    secs, ms = divmod(ms, 1000)
    return f'{hours:02}:{minutes:02}:{secs:02}{separator}{ms:03}'


def subtitles(voices):
    items = []
    for voice in voices:
        items.append({'text': voice['text'], 'start': voice['start'] + max(0, voice['speech_start']-.07),
                      'end': voice['start'] + voice['speech_end'] + .35})
    srt = '\n'.join(f'{i}\n{timecode(s["start"])} --> {timecode(s["end"])}\n{s["text"]}\n'
                    for i, s in enumerate(items, 1))
    (OUT / '对白字幕.srt').write_text(srt, encoding='utf-8-sig')
    (OUT / '对白字幕.vtt').write_text('WEBVTT\n\n' + '\n'.join(
        f'{timecode(s["start"], ".")} --> {timecode(s["end"], ".")}\n{s["text"]}\n' for s in items), encoding='utf-8')
    header = '''[Script Info]
ScriptType: v4.00+
PlayResX: 1280
PlayResY: 720
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Default,Microsoft YaHei,34,&H00FFFFFF,&H00FFFFFF,&H80181818,&H90000000,0,0,0,0,100,100,1,0,1,1.5,0.7,2,80,80,54,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
'''
    def ass_time(seconds):
        cs = round(seconds * 100)
        h, cs = divmod(cs, 360000)
        m, cs = divmod(cs, 6000)
        s, cs = divmod(cs, 100)
        return f'{h}:{m:02}:{s:02}.{cs:02}'
    events = ''.join(f'Dialogue: 0,{ass_time(s["start"])},{ass_time(s["end"])},Default,,0,0,0,,{{\\fad(70,100)}}{s["text"]}\n'
                     for s in items)
    (OUT / '对白字幕.ass').write_text(header + events, encoding='utf-8-sig')
    return items


def render(specs, tracks, total):
    concat = OUT / '镜头素材' / 'concat.txt'
    concat.write_text('\n'.join("file '" + Path(s['file']).name + "'" for s in specs), encoding='utf-8-sig')
    # concat demuxer rejects UTF-8 BOM; its filenames remain UTF-8.
    concat.write_text(concat.read_text(encoding='utf-8-sig'), encoding='utf-8')
    base = OUT / '画面与原环境声.mp4'
    run(['ffmpeg', '-hide_banner', '-loglevel', 'error', '-f', 'concat', '-safe', '0',
         '-i', str(concat), '-c', 'copy', '-y', str(base)])
    args = ['ffmpeg', '-hide_banner', '-loglevel', 'error', '-i', str(base)]
    filters = []
    mixes = ['[0:a]']
    for number, track in enumerate(tracks, 1):
        args += ['-i', track['file']]
        filters.append(f'[{number}:a]aformat=sample_rates=48000:channel_layouts=stereo,'
                       f'volume={track.get("volume",1)},afade=t=in:d=0.015,'
                       f'afade=t=out:st={max(0,track["duration"]-.06)}:d=0.06,'
                       f'adelay={round(track["start"]*1000)}:all=1[a{number}]')
        mixes.append(f'[a{number}]')
    filters.append(''.join(mixes) + f'amix=inputs={len(mixes)}:duration=first:normalize=0,'
                   f'alimiter=limit=0.89:level=false:latency=true,afade=t=out:st={total-.55}:d=0.55[mixed]')
    mixed = OUT / '坡道_精剪_无字幕.mp4'
    args += ['-filter_complex', ';'.join(filters), '-map', '0:v:0', '-map', '[mixed]',
             '-c:v', 'copy', '-c:a', 'aac', '-b:a', '192k', '-t', str(total),
             '-movflags', '+faststart', '-y', str(mixed)]
    run(args)
    final = OUT / '坡道_精剪_字幕配音.mp4'
    # Relative ASS path avoids Windows drive-colon escaping in libass.
    command = ['ffmpeg', '-hide_banner', '-loglevel', 'error', '-i', str(mixed),
               '-vf', f'fade=t=in:d=0.18,fade=t=out:st={total-.55}:d=0.55,ass=对白字幕.ass',
               '-c:v', 'libx264', '-preset', 'fast', '-crf', '18', '-pix_fmt', 'yuv420p',
               '-c:a', 'copy', '-t', str(total), '-movflags', '+faststart', '-y', str(final)]
    result = subprocess.run(command, cwd=OUT, capture_output=True, text=True,
                            encoding='utf-8', errors='replace', timeout=120)
    if result.returncode:
        raise RuntimeError(result.stderr[-4000:])
    return final


def make_draft(specs, tracks, subs, total):
    skill_root = Path(os.environ.get('JY_SKILL_ROOT', str(Path.home() / '.codex/skills/jianying-editor')))
    os.environ['JY_SKILL_ROOT'] = str(skill_root)
    sys.path.insert(0, str(skill_root / 'scripts'))
    from jy_wrapper import JyProject
    from pyJianYingDraft import KeyframeProperty as KP, TextStyle, TextBorder, ClipSettings
    name = '不用麻烦她_坡道精剪_字幕配音_20261009_' + uuid.uuid4().hex[:6]
    project = JyProject(name, width=1280, height=720, drafts_root=str(OUT), overwrite=False)
    project.script.fps = FPS
    for index, item in enumerate(specs):
        segment = project.add_media_safe(item['file'], start_time=round(item['start']*1000000),
                                         duration=round(item['duration']*1000000), track_name='精剪画面')
        if segment is None:
            raise RuntimeError(f'剪映导入失败：{item["title"]}')
        if index == 0:
            segment.add_keyframe(KP.alpha, 0, 0)
            segment.add_keyframe(KP.alpha, 180000, 1)
        if index == len(specs)-1:
            segment.add_keyframe(KP.alpha, round((item['duration']-.55)*1000000), 1)
            segment.add_keyframe(KP.alpha, round(item['duration']*1000000), 0)
    for track in tracks:
        track_name = '对白_徐月禾' if track['id'].startswith(('01_', '02_', '03_')) else '环境音_' + track['id']
        segment = project.add_media_safe(track['file'], start_time=round(track['start']*1000000),
                                         duration=round(track['duration']*1000000), track_name=track_name)
        if segment is None:
            raise RuntimeError(f'音轨导入失败：{track["id"]}')
        segment.volume = track.get('volume', 1)
        segment.add_fade('0.015s', '0.06s')
    for item in subs:
        project.add_text_simple(item['text'], start_time=round(item['start']*1000000),
                                duration=round((item['end']-item['start'])*1000000),
                                track_name='对白同步字幕', style=TextStyle(size=5.0, color=(1,1,1), align=1),
                                border=TextBorder(color=(.08,.08,.08), alpha=.55, width=12),
                                clip_settings=ClipSettings(transform_y=-.81))
    saved = project.save()
    folder = Path(saved['draft_path'])
    content = read(folder / 'draft_info.json')
    content.update(id=str(uuid.uuid4()).upper(), name=name, duration=round(total*1000000))
    write(folder / 'draft_info.json', content)
    write(folder / 'draft_content.json', content)
    cover = folder / 'draft_cover.jpg'
    run(['ffmpeg', '-hide_banner', '-loglevel', 'error', '-ss', '1', '-i', specs[0]['file'],
         '-frames:v', '1', '-vf', 'scale=480:-1', '-y', str(cover)])
    meta = read(folder / 'draft_meta_info.json')
    meta.update(draft_name=name, draft_id=content['id'], draft_fold_path=str(folder),
                draft_root_path=str(OUT), draft_cover=str(cover),
                tm_draft_create=int(time.time()*1000000), tm_draft_modified=int(time.time()*1000000),
                tm_duration=round(total*1000000))
    write(folder / 'draft_meta_info.json', meta)
    counts = {kind: sum(len(t['segments']) for t in content['tracks'] if t['type']==kind)
              for kind in ('video', 'audio', 'text')}
    assert counts == {'video': 8, 'audio': 6, 'text': 3}, counts
    for material in content['materials'].get('videos', []) + content['materials'].get('audios', []):
        asset = Path(material['path']).resolve()
        assert asset.is_file() and asset.is_relative_to(folder.resolve()), '草稿素材丢失'
    return folder, counts


def main():
    if not (OUT / 'voice-manifest.json').is_file():
        raise FileNotFoundError('请先运行 prepare_slope_voice.py 生成本地对白')
    specs, total = clips()
    voices = read(OUT / 'voice-manifest.json')
    for voice, start in zip(voices, [5.0, 9.95, 13.9]):
        voice['start'] = start
        voice['volume'] = 1
        assert start + voice['duration'] < total
    tracks = sounds(total) + voices
    subs = subtitles(voices)
    final = render(specs, tracks, total)
    folder, counts = make_draft(specs, tracks, subs, total)
    info = probe(final)
    duration = float(info['format']['duration'])
    assert abs(duration-total) < .1
    video = next(s for s in info['streams'] if s['codec_type']=='video')
    assert video['width']==1280 and video['height']==720 and video['r_frame_rate']=='24/1'
    assert any(s['codec_type']=='audio' for s in info['streams'])
    plan = {'duration': total, 'shots': specs, 'voices': voices, 'subtitles': subs,
            'sound_tracks': tracks, 'voice_backend': 'Windows SAPI (offline)',
            'note': '现有即梦素材的精剪试版；声音、字幕与切点已落实，未重新生成视频。'}
    write(OUT / '精剪方案.json', plan)
    result = {'created_at': datetime.now(timezone(timedelta(hours=8))).isoformat(),
              'title': '坡道精剪 · 字幕与配音', 'duration': total,
              'folder': OUT.relative_to(ROOT).as_posix(),
              'mp4': final.relative_to(ROOT).as_posix(),
              'draft': folder.relative_to(ROOT).as_posix(),
              'srt': (OUT/'对白字幕.srt').relative_to(ROOT).as_posix(),
              'vtt': (OUT/'对白字幕.vtt').relative_to(ROOT).as_posix(),
              'media': {'duration': duration, 'width': 1280, 'height': 720, 'has_audio': True},
              'draft_tracks': counts, 'subtitles_burned': True,
              'note': '精剪试版；字幕已烧录；本地离线女声配音；剪映草稿已生成。',
              'jianying_ui_verified': False, 'native_mp4_export_verified': False}
    write(OUT/'export.json', result)
    write(ROOT/'exports/latest.json', result)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
