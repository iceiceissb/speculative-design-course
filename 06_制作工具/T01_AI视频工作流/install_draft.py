"""Install only this workflow's latest draft, without overwriting other projects."""
from pathlib import Path
import json
import os
import shutil
import sys
import time
from workflow import ROOT, read_json, write_json


def install(target_root=None):
    latest=read_json(ROOT/'exports/latest.json', {})
    if not latest.get('draft'):
        raise ValueError('请先在选片台输出剪映草稿。')
    source=(ROOT/latest['draft']).resolve()
    if not source.is_relative_to(ROOT/'exports') or not source.is_dir():
        raise ValueError('源草稿路径无效')
    drafts=Path(target_root or os.environ.get('JY_DRAFTS_ROOT') or
        (Path(os.environ['LOCALAPPDATA'])/'JianyingPro/User Data/Projects/com.lveditor.draft')).resolve()
    if not drafts.is_dir():
        raise ValueError('找不到剪映草稿目录。可在剪映设置查看草稿位置，并设置 JY_DRAFTS_ROOT。')
    target=(drafts/source.name).resolve()
    if target.parent != drafts or target.exists():
        raise ValueError('目标草稿已存在或路径无效；为避免覆盖，已停止。')
    shutil.copytree(source,target)
    for name in ['draft_info.json','draft_content.json','draft_meta_info.json']:
        path=target/name
        content=read_json(path)
        def relocate(obj):
            if isinstance(obj,dict):return {k:relocate(v) for k,v in obj.items()}
            if isinstance(obj,list):return [relocate(v) for v in obj]
            if isinstance(obj,str):return obj.replace(str(source),str(target)).replace(source.as_posix(),target.as_posix())
            return obj
        content=relocate(content)
        if name=='draft_meta_info.json':
            content['draft_fold_path']=str(target);content['draft_root_path']=str(drafts)
            content['tm_draft_modified']=int(time.time()*1000000)
        write_json(path,content)
    result={'draft':str(target),'note':'请在剪映草稿列表刷新后打开；本工具未操作已有草稿。'}
    write_json(ROOT/'reports/installed-draft.json',result)
    return result


if __name__=='__main__':
    try:print(json.dumps(install(sys.argv[1] if len(sys.argv)>1 else None),ensure_ascii=False,indent=2))
    except (OSError,ValueError) as error:
        print('未安装：'+str(error),file=sys.stderr);sys.exit(1)
