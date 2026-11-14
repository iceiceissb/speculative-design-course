from pathlib import Path
import json,sys
ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'output/AI视频工作流';sys.path.insert(0,str(OUT))
from workflow import Workflow,read_json,write_json,probe
w=Workflow(OUT);latest=read_json(OUT/'exports/latest.json');draft_dir=OUT/latest['draft']
content=read_json(draft_dir/'draft_info.json');videos=content['materials']['videos']
checks={'mp4_playable':abs(probe(OUT/latest['mp4'])['duration']-20)<.15,
        'draft_duration_20s':content['duration']==20000000,
        'draft_video_segments_5':sum(len(t['segments']) for t in content['tracks'] if t['type']=='video')==5,
        'draft_subtitle_segments_2':sum(len(t['segments']) for t in content['tracks'] if t['type']=='text')==2,
        'materials_reused_correctly':len(videos)==4,
        'material_paths_valid':all(Path(v['path']).is_file() and Path(v['path']).resolve().is_relative_to(draft_dir.resolve()) for v in videos),
        'material_ids_unique':len({v['local_material_id'] for v in videos})==len(videos),
        'browser_checks_passed':read_json(OUT/'reports/browser-check.json')['passed'],
        'no_paid_generation':not any(c['source']=='seedance' for c in w.state()['candidates']),
        'api_key_absent':not w.key_ready(),
        'license_included':(OUT/'vendor/PYJIANYINGDRAFT_LICENSE.txt').is_file()}
installed=read_json(OUT/'reports/installed-draft.json');install_dir=Path(installed['draft'])
install_content=read_json(install_dir/'draft_info.json');install_meta=read_json(install_dir/'draft_meta_info.json')
checks['installed_draft_self_contained']=all(Path(v['path']).is_file() and Path(v['path']).resolve().is_relative_to(install_dir.resolve()) for v in install_content['materials']['videos'])
checks['installed_metadata_correct']=install_meta['draft_fold_path']==str(install_dir) and install_meta['draft_name']==install_dir.name
assert all(checks.values()),checks
write_json(OUT/'reports/final-check.json',{'passed':True,'checks':checks,'exports':latest,'installed_draft':installed})
print(json.dumps({'passed':True,'checks':checks,'mp4':str(OUT/latest['mp4']),'draft':str(install_dir)},ensure_ascii=False,indent=2))
