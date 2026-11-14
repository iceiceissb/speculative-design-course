"""Produce an editable Jianying draft and an independent FFmpeg rough cut."""
import csv
from datetime import datetime
import json
from pathlib import Path
import shutil
import sys
import time
import uuid

from workflow import probe, read_json, run_tool, stamp, write_json


def timecode(seconds, separator=','):
    ms = round(seconds * 1000)
    hours, ms = divmod(ms, 3600000); minutes, ms = divmod(ms, 60000); secs, ms = divmod(ms, 1000)
    return f'{hours:02}:{minutes:02}:{secs:02}{separator}{ms:03}'


def write_subtitles(folder, project, total):
    items = [s for s in project.get('subtitles', []) if 0 <= s['start'] < total and s['duration'] > 0]
    srt = []; vtt = ['WEBVTT\n']
    for index, item in enumerate(items, 1):
        end = min(total, item['start'] + item['duration'])
        srt.append(f"{index}\n{timecode(item['start'])} --> {timecode(end)}\n{item['text']}\n")
        vtt.append(f"{timecode(item['start'], '.')} --> {timecode(end, '.')}\n{item['text']}\n")
    (folder / '字幕.srt').write_text('\n'.join(srt), encoding='utf-8-sig')
    (folder / '字幕.vtt').write_text('\n'.join(vtt), encoding='utf-8')
    return items


def render_mp4(folder, rows, audio_tracks):
    normalized = folder / 'segments'; normalized.mkdir(exist_ok=True)
    names = []
    for index, row in enumerate(rows):
        dest = normalized / f'{index:02}.mp4'; names.append(dest.name)
        args = ['ffmpeg', '-hide_banner', '-loglevel', 'error', '-ss', str(row['source_start']), '-i', row['file']]
        if not row['media']['has_audio']:
            args += ['-f', 'lavfi', '-i', 'anullsrc=r=48000:cl=stereo']
        args += ['-map', '0:v:0', '-map', '0:a:0' if row['media']['has_audio'] else '1:a:0',
                 '-vf', 'scale=1280:720:force_original_aspect_ratio=decrease,pad=1280:720:(ow-iw)/2:(oh-ih)/2,setsar=1',
                 '-af', 'apad', '-t', str(row['duration']), '-r', '24', '-c:v', 'libx264', '-preset', 'fast',
                 '-crf', '19', '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-ar', '48000', '-ac', '2', '-y', str(dest)]
        run_tool(args)
    (normalized / 'concat.txt').write_text('\n'.join("file '" + n + "'" for n in names), encoding='ascii')
    dest = folder / '坡道_粗剪.mp4'
    run_tool(['ffmpeg', '-hide_banner', '-loglevel', 'error', '-f', 'concat', '-safe', '0',
              '-i', str(normalized / 'concat.txt'), '-c', 'copy', '-movflags', '+faststart', '-y', str(dest)])
    if audio_tracks:
        args = ['ffmpeg', '-hide_banner', '-loglevel', 'error', '-i', str(dest)]
        filters = []; mixes = ['[0:a]']
        for index, track in enumerate(audio_tracks, 1):
            args += ['-i', track['file']]
            source = float(track.get('source_start', 0)); duration = float(track.get('duration', sum(r['duration'] for r in rows)))
            start = float(track.get('start', 0)); volume = float(track.get('volume', 1))
            if min(source, start) < 0 or duration <= 0 or not 0 <= volume <= 4:
                raise ValueError('配音/音效轨配置无效')
            filters.append(f'[{index}:a]atrim=start={source}:duration={duration},asetpts=PTS-STARTPTS,volume={volume},adelay={round(start*1000)}:all=1[a{index}]')
            mixes.append(f'[a{index}]')
        filters.append(''.join(mixes) + f'amix=inputs={len(mixes)}:duration=first:normalize=0[out]')
        mixed = folder / '坡道_粗剪_配音.mp4'
        args += ['-filter_complex', ';'.join(filters), '-map', '0:v', '-map', '[out]',
                 '-c:v', 'copy', '-c:a', 'aac', '-ar', '48000', '-movflags', '+faststart', '-y', str(mixed)]
        run_tool(args); dest = mixed
    info = probe(dest)
    expected = sum(row['duration'] for row in rows)
    if abs(info['duration'] - expected) > .15:
        raise RuntimeError(f'粗剪时长异常：预计{expected}秒，实际{info["duration"]}秒')
    return dest, info


def make_draft(workflow, folder, rows, subtitles, audio_tracks):
    sys.path.insert(0, str(workflow.root / 'vendor'))
    import pyJianYingDraft as draft
    name = '不用麻烦她_坡道试片_' + folder.name
    script = draft.DraftFolder(str(folder)).create_draft(name, 1280, 720, fps=24, allow_replace=False)
    draft_dir = folder / name; media_dir = draft_dir / 'media'; media_dir.mkdir()
    script.add_track(draft.TrackType.video, '画面')
    copied = {}; material_objects = {}
    for row in rows:
        source = Path(row['file'])
        if row['candidate_id'] not in copied:
            target = media_dir / (row['job_id'] + '_' + source.name)
            shutil.copy2(source, target); copied[row['candidate_id']] = target
            material_objects[row['candidate_id']] = draft.VideoMaterial(str(target))
        duration = round(row['duration'] * 1000000)
        segment = draft.VideoSegment(material_objects[row['candidate_id']],
                  draft.Timerange(round(row['target_start'] * 1000000), duration),
                  source_timerange=draft.Timerange(round(row['source_start'] * 1000000), duration))
        script.add_segment(segment, '画面')
    if subtitles:
        script.add_track(draft.TrackType.text, '对白字幕占位')
        for item in subtitles:
            script.add_segment(draft.TextSegment(item['text'], draft.Timerange(round(item['start']*1000000),
                               round(min(item['duration'], sum(r['duration'] for r in rows)-item['start'])*1000000)),
                               style=draft.TextStyle(size=6.5, color=(1, 1, 1), align=1, auto_wrapping=True),
                               clip_settings=draft.ClipSettings(transform_y=-.78)), '对白字幕占位')
    for index, track in enumerate(audio_tracks):
        track_name = '配音音效_' + str(index+1); script.add_track(draft.TrackType.audio, track_name)
        source = Path(track['file']); target = media_dir / f'audio_{index}{source.suffix}'
        shutil.copy2(source, target)
        length = round(float(track.get('duration', sum(r['duration'] for r in rows))) * 1000000)
        segment = draft.AudioSegment(str(target), draft.Timerange(round(float(track.get('start', 0))*1000000), length),
                  source_timerange=draft.Timerange(round(float(track.get('source_start', 0))*1000000), length),
                  volume=float(track.get('volume', 1)))
        script.add_segment(segment, track_name)
    script.save()
    # Unique IDs, timestamps, names and paths are required for a discoverable self-contained draft.
    content_path = draft_dir / 'draft_info.json'; content = read_json(content_path)
    content['id'] = str(uuid.uuid4()).upper(); content['name'] = name
    for material in content['materials'].get('videos', []) + content['materials'].get('audios', []):
        material['local_material_id'] = material.get('local_material_id') or str(uuid.uuid4()).upper()
    write_json(content_path, content)
    write_json(draft_dir / 'draft_content.json', content)
    cover = draft_dir / 'draft_cover.jpg'
    run_tool(['ffmpeg', '-hide_banner', '-loglevel', 'error', '-i', rows[0]['file'], '-frames:v', '1',
              '-vf', 'scale=480:-1', '-y', str(cover)])
    meta = read_json(draft_dir / 'draft_meta_info.json')
    meta.update({'draft_name': name, 'draft_id': content['id'], 'draft_fold_path': str(draft_dir),
                 'draft_root_path': str(folder), 'draft_cover': str(cover),
                 'tm_draft_create': int(time.time()*1000000), 'tm_draft_modified': int(time.time()*1000000),
                 'tm_duration': round(sum(row['duration'] for row in rows)*1000000)})
    write_json(draft_dir / 'draft_meta_info.json', meta)
    return draft_dir


def assemble(workflow, kind='both'):
    rows = workflow.resolved_timeline()
    name = datetime.now().strftime('%Y%m%d_%H%M%S') + '_' + uuid.uuid4().hex[:4]
    folder = workflow.root / 'exports' / name; folder.mkdir(parents=True)
    total = sum(row['duration'] for row in rows)
    subtitles = write_subtitles(folder, workflow.project, total)
    audio_tracks = []
    for track in workflow.project.get('audio_tracks', []):
        copy = dict(track); copy['file'] = str(workflow.local(track['file'])); audio_tracks.append(copy)
    with (folder / '时间线.csv').open('w', newline='', encoding='utf-8-sig') as handle:
        writer = csv.DictWriter(handle, fieldnames=['id', 'job_id', 'title', 'target_start', 'source_start', 'duration', 'candidate_id', 'file'])
        writer.writeheader(); writer.writerows({k: row[k] for k in writer.fieldnames} for row in rows)
    result = {'created_at': stamp(), 'duration': total, 'folder': folder.relative_to(workflow.root).as_posix(),
              'srt': (folder/'字幕.srt').relative_to(workflow.root).as_posix(),
              'vtt': (folder/'字幕.vtt').relative_to(workflow.root).as_posix(),
              'note': '现有素材验证或已选候选的粗剪；字幕另存，无自动配音。'}
    if kind in {'both', 'mp4'}:
        video, info = render_mp4(folder, rows, audio_tracks)
        result['mp4'] = video.relative_to(workflow.root).as_posix(); result['media'] = info
    if kind in {'both', 'draft'}:
        result['draft'] = make_draft(workflow, folder, rows, subtitles, audio_tracks).relative_to(workflow.root).as_posix()
    write_json(folder / 'export.json', result); write_json(workflow.root / 'exports/latest.json', result)
    return result
