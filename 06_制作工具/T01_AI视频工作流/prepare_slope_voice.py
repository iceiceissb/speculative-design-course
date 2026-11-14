"""Create the existing slope dialogue with Windows' installed offline voice."""
import json
import os
from pathlib import Path
import subprocess
import wave
import numpy as np

ROOT = Path(__file__).resolve().parent
OUT = ROOT / 'exports' / '坡道精剪_v1_20261009'
LINES = [
    ('01_发现', '灯怎么亮了？'),
    ('02_追问', '刚才这一路，你也在推？'),
    ('03_边界', '帮我可以，先让我知道。'),
]


def run(args, **kwargs):
    return subprocess.run(args, check=True, capture_output=True, text=True,
                          encoding='utf-8', errors='replace', **kwargs).stdout


def main():
    folder = OUT / 'voice'
    folder.mkdir(parents=True, exist_ok=True)
    (folder / 'lines.json').write_text(json.dumps([{'id': name, 'text': text}
                                                for name, text in LINES],
                                               ensure_ascii=False), encoding='utf-8')
    env = dict(os.environ, SLOPE_VOICE_OUT=str(folder))
    script = (ROOT / 'synth_slope_voice.ps1').read_text(encoding='utf-8')
    shell = Path(os.environ['WINDIR']) / 'System32/WindowsPowerShell/v1.0/powershell.exe'
    run([str(shell), '-NoProfile', '-Command', script], env=env, timeout=50)
    voice = json.loads((folder / 'local-voice.json').read_text(encoding='utf-8-sig'))
    results = []
    for name, text in LINES:
        source = folder / (name + '_local.wav')
        wav = folder / (name + '.wav')
        run(['ffmpeg', '-hide_banner', '-loglevel', 'error', '-i', str(source),
             '-af', 'loudnorm=I=-18:TP=-2:LRA=8', '-ar', '48000', '-ac', '1',
             '-c:a', 'pcm_s16le', '-y', str(wav)])
        with wave.open(str(wav)) as handle:
            rate = handle.getframerate()
            samples = np.frombuffer(handle.readframes(handle.getnframes()), dtype='<i2').astype(float)
        duration = len(samples) / rate
        size = round(rate * .01)
        blocks = samples[:len(samples) // size * size].reshape(-1, size)
        active = np.where(np.sqrt(np.mean(blocks ** 2, axis=1)) > 32768 * 10 ** (-42 / 20))[0]
        if not len(active):
            raise RuntimeError('本地语音文件没有有效声音')
        result = {'id': name, 'text': text, 'file': str(wav), 'duration': duration,
                  'speech_start': max(0, active[0] * .01 - .03),
                  'speech_end': min(duration, (active[-1] + 1) * .01 + .06),
                  'voice': voice['name'], 'backend': 'Windows SAPI (offline)', 'rate': -1}
        results.append(result)
        print(json.dumps(result, ensure_ascii=False), flush=True)
    (OUT / 'voice-manifest.json').write_text(json.dumps(results, ensure_ascii=False,
                                                      indent=2), encoding='utf-8')


if __name__ == '__main__':
    main()
