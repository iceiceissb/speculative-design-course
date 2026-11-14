"""Verify the Jianying wrapper with the project's draft library, without UI control."""
import json
import os
from pathlib import Path
import sys
import uuid


def main():
    root = Path(__file__).resolve().parent
    codex_root = Path(os.environ.get('CODEX_HOME', str(Path.home() / '.codex')))
    skill_root = Path(os.environ.get('JY_SKILL_ROOT', str(codex_root / 'skills' / 'jianying-editor'))).resolve()
    if not (skill_root / 'scripts' / 'jy_wrapper.py').is_file():
        raise FileNotFoundError(f'找不到完整剪映 Skill：{skill_root}')
    # Reuse the project's draft library, whose optional UI imports are guarded.
    # Preload it before the wrapper adds the skill vendor directory to sys.path.
    sys.path.insert(0, str(root / 'vendor'))
    import pyJianYingDraft as draft_library
    os.environ['JY_SKILL_ROOT'] = str(skill_root)
    sys.path.insert(0, str(skill_root / 'scripts'))
    from jy_wrapper import JyProject
    from pyJianYingDraft import KeyframeProperty as KP

    state = json.loads((root / 'state.json').read_text(encoding='utf-8-sig'))
    source = next((root / item['file'] for item in state['candidates']
                   if item.get('status') == 'succeeded' and (root / item['file']).is_file()), None)
    if source is None:
        raise FileNotFoundError('需要一条已有候选视频来验证 Skill。')
    drafts_root = root / 'reports' / 'jianying-skill-checks'
    name = '剪映Skill_运行验证_' + uuid.uuid4().hex[:12]
    project = JyProject(name, width=1280, height=720,
                        drafts_root=str(drafts_root), overwrite=False)
    segment = project.add_media_safe(str(source), start_time='0s',
                                    source_start='0.2s', duration='3s', track_name='画面验证')
    if segment is None:
        raise RuntimeError('Skill 未能导入候选视频。')
    segment.add_keyframe(KP.uniform_scale, 0, 1.0)
    segment.add_keyframe(KP.uniform_scale, 2900000, 1.02)
    segment.add_keyframe(KP.volume, 0, 0.0)
    segment.add_keyframe(KP.volume, 150000, 0.5)
    segment.add_keyframe(KP.volume, 2800000, 0.5)
    segment.add_keyframe(KP.volume, 3000000, 0.0)
    subtitle = project.add_text_simple('剪映 Skill 运行验证', start_time='0.5s',
                                       duration='1.5s', track_name='字幕验证')
    if subtitle is None:
        raise RuntimeError('Skill 未能添加字幕。')
    saved = project.save()
    draft_dir = Path(saved['draft_path'])
    content_path = draft_dir / 'draft_info.json'
    if not content_path.is_file():
        content_path = draft_dir / 'draft_content.json'
    content = json.loads(content_path.read_text(encoding='utf-8-sig'))
    videos = [s for t in content['tracks'] if t['type'] == 'video' for s in t['segments']]
    texts = [s for t in content['tracks'] if t['type'] == 'text' for s in t['segments']]
    assert len(videos) == 1 and len(texts) == 1, '视频或字幕轨不完整'
    assert videos[0]['source_timerange'] == {'start': 200000, 'duration': 3000000}, '切点没有正确保存'
    assert texts[0]['target_timerange'] == {'start': 500000, 'duration': 1500000}, '字幕时间没有正确保存'
    keyframes = videos[0].get('common_keyframes', [])
    assert any(k['property_type'] == 'KFTypeVolume' for k in keyframes), '缺少音量关键帧'
    assert any(k['property_type'] == 'KFTypeScaleX' for k in keyframes), '缺少缩放关键帧'
    for material in content['materials'].get('videos', []):
        path = Path(material['path']).resolve()
        assert path.is_file() and path.is_relative_to(draft_dir.resolve()), '草稿素材没有自包含'
    report = {
        'ok': True, 'skill_root': str(skill_root), 'python': sys.executable,
        'draft_library': str(Path(draft_library.__file__).resolve()),
        'draft': str(draft_dir), 'source': str(source),
        'verified': ['完整 JyProject 接口', '素材自包含', '精确源切点',
                     '字幕时间线', '缩放关键帧', '音量淡入淡出关键帧'],
        'jianying_ui_verified': False, 'native_mp4_export_verified': False,
        'note': '使用已安装 JyProject 封装与项目内草稿库；未验证剪映窗口控制，没有改动选片、原工程或执行视频生成 API。'
    }
    report_path = root / 'reports' / 'jianying-skill-check.json'
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
