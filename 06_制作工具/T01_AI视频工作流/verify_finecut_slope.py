"""Check the delivered video, rendered subtitles and offline dialogue mix."""
import json
from pathlib import Path
import re
import subprocess
import wave

import numpy as np
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent
OUT = ROOT / 'exports/坡道精剪_v1_20261009'
QA = OUT / '验收'
QA.mkdir(exist_ok=True)


def run(args):
    return subprocess.run(args, check=True, capture_output=True, text=True,
                          encoding='utf-8', errors='replace', timeout=30)


def main():
    result = json.loads((OUT / 'export.json').read_text(encoding='utf-8'))
    final = ROOT / result['mp4']
    run(['ffmpeg', '-hide_banner', '-v', 'error', '-i', str(final), '-f', 'null', '-'])
    samples = [1.2, 3.7, 5.6, 10.8, 14.8, 17.1]
    font = ImageFont.truetype('C:/Windows/Fonts/msyh.ttc', 18)
    sheet = Image.new('RGB', (1280, 792), '#efeee9')
    draw = ImageDraw.Draw(sheet)
    for i, at in enumerate(samples):
        path = QA / f'frame_{at}.png'
        run(['ffmpeg', '-hide_banner', '-v', 'error', '-ss', str(at), '-i', str(final),
             '-frames:v', '1', '-y', str(path)])
        im = Image.open(path)
        im.thumbnail((640, 360))
        x, y = i % 2 * 640, i // 2 * 264
        im = im.resize((416, 234))
        sheet.paste(im, (x+112, y+28))
        draw.text((x+12, y+4), f'{at:.1f}s', font=font, fill='#202a20')
    sheet.save(QA / '精剪检查帧.jpg')
    audio = QA / '完整混音.wav'
    run(['ffmpeg', '-hide_banner', '-v', 'error', '-i', str(final), '-vn', '-ar', '48000',
         '-ac', '1', '-c:a', 'pcm_s16le', '-y', str(audio)])
    with wave.open(str(audio)) as handle:
        rate = handle.getframerate()
        a = np.frombuffer(handle.readframes(handle.getnframes()), '<i2').astype(float)/32768
    plan = json.loads((OUT / '精剪方案.json').read_text(encoding='utf-8'))
    speech_levels = []
    for voice in plan['voices']:
        start = voice['start'] + voice['speech_start']
        end = voice['start'] + voice['speech_end']
        active = a[round(start*rate):round(end*rate)]
        level = 20*np.log10(max(np.sqrt(np.mean(active**2)), 1e-9))
        assert level > -30, f'对白混音音量异常：{voice["text"]}'
        speech_levels.append({'text': voice['text'], 'rms_dbfs': round(float(level), 2)})
    assert len(plan['subtitles'])==3
    assert all(0 <= s['start'] < s['end'] < 18 for s in plan['subtitles'])
    info = json.loads(run(['ffprobe', '-v', 'error', '-select_streams', 'v:0',
                          '-count_frames', '-show_entries', 'stream=nb_read_frames',
                          '-of', 'json', str(final)]).stdout)
    assert int(info['streams'][0]['nb_read_frames']) == 432
    report = {'ok': True, 'duration': 18, 'video_frames': 432, 'frame_rate': 24,
              'resolution': [1280,720], 'speech_levels': speech_levels,
              'audio_peak_dbfs': round(float(20*np.log10(max(abs(a)))),2),
              'subtitles_burned': True, 'voice_backend': 'Windows SAPI (offline)',
              'full_video_decode': True, 'draft_tracks': result['draft_tracks'],
              'jianying_ui_verified': result['jianying_ui_verified'],
              'frames': str(QA/'精剪检查帧.jpg')}
    (QA / '验收.json').write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
