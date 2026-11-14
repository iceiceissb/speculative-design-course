"""Read only Jianying's UI controls before attempting native preview/export."""
import json
from pathlib import Path
import uiautomation as uia

windows = []
for control in uia.GetRootControl().GetChildren():
    if '剪映' in control.Name or 'Jianying' in control.Name or 'CapCut' in control.Name:
        windows.append(control)


def describe(control, depth=0):
    item = {'name': control.Name, 'class': control.ClassName, 'type': control.ControlTypeName}
    try:
        item['description'] = control.GetPropertyValue(30159)
    except Exception:
        pass
    if depth < 3:
        item['children'] = [describe(c, depth+1) for c in control.GetChildren()]
    return item


result = [describe(w) for w in windows]
root = Path(__file__).resolve().parents[2] / 'output/AI视频工作流'
(root / 'reports/jianying-ui-probe.json').write_text(json.dumps(result, ensure_ascii=False,
                                                               indent=2), encoding='utf-8')
print(json.dumps([{'name': w.Name, 'class': w.ClassName, 'controls': len(w.GetChildren())}
                  for w in windows], ensure_ascii=False))
