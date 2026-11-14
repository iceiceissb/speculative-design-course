"""Inspect only Jianying windows; explicit export uses the installed skill API."""
import argparse
import json
from pathlib import Path
import os
import sys
from f11_production import ROOT, RUN

sys.path.insert(0,str(ROOT/'runtime/edit_packages'))
sys.path.insert(0,str(ROOT/'vendor'))
import uiautomation as uia


def inspect(activate=False):
    from PIL import ImageGrab
    import csv,subprocess,io,ctypes,time
    user=ctypes.windll.user32
    previous=user.GetForegroundWindow()
    data=subprocess.run(['tasklist','/FI','IMAGENAME eq JianyingPro.exe','/FO','CSV','/NH'],capture_output=True,text=True).stdout
    pids={int(r[1]) for r in csv.reader(io.StringIO(data)) if len(r)>1 and r[1].isdigit()}
    out=RUN/'检查/剪映窗口'
    out.mkdir(parents=True,exist_ok=True)
    wins=[]
    for control in uia.GetRootControl().GetChildren():
        name=control.Name or ''
        cls=control.ClassName or ''
        if control.ProcessId not in pids and '剪映' not in name and 'Jianying' not in name and 'Jianying' not in cls:
            continue
        if activate:
            control.SetActive()
            time.sleep(.5)
        rows=[]
        def walk(c,depth):
            if depth>5 or len(rows)>900:
                return
            try:
                desc=c.GetPropertyValue(30159)
                rows.append({'depth':depth,'name':c.Name,'type':c.ControlTypeName,
                            'class':c.ClassName,'description':desc,
                            'rect':str(c.BoundingRectangle)})
                for child in c.GetChildren():
                    walk(child,depth+1)
            except Exception:
                pass
        walk(control,0)
        r=control.BoundingRectangle
        if activate and user.GetForegroundWindow()==control.NativeWindowHandle and r.right>r.left and r.bottom>r.top:
            ImageGrab.grab(bbox=(r.left,r.top,r.right,r.bottom)).save(out/f'window_{len(wins)}.png')
        wins.append(rows)
    (out/'controls.json').write_text(json.dumps(wins,ensure_ascii=False,indent=2),'utf-8')
    if activate and previous and user.IsWindow(previous):user.SetForegroundWindow(previous)
    print(json.dumps({'windows':len(wins),'controls':[len(x) for x in wins],
                      'top_controls':[[{'name':r['name'],'class':r['class'],'description':r['description']} for r in x[:20]] for x in wins]},ensure_ascii=False),flush=True)


def export(name,output):
    from pyJianYingDraft.jianying_controller import JianyingController,ExportResolution,ExportFramerate
    c=JianyingController(keep_topmost=False)
    c.export_draft(name,output,resolution=ExportResolution.RES_1080P,framerate=ExportFramerate.FR_24,timeout=900)


def reveal():
    import csv,subprocess,io,ctypes
    data=subprocess.run(['tasklist','/FI','IMAGENAME eq JianyingPro.exe','/FO','CSV','/NH'],capture_output=True,text=True).stdout
    pids={int(r[1]) for r in csv.reader(io.StringIO(data)) if len(r)>1 and r[1].isdigit()}
    user=ctypes.windll.user32
    found=[]
    class RECT(ctypes.Structure):
        _fields_=[('left',ctypes.c_long),('top',ctypes.c_long),('right',ctypes.c_long),('bottom',ctypes.c_long)]
    @ctypes.WINFUNCTYPE(ctypes.c_bool,ctypes.c_void_p,ctypes.c_void_p)
    def callback(hwnd,_):
        pid=ctypes.c_ulong();user.GetWindowThreadProcessId(hwnd,ctypes.byref(pid))
        if pid.value not in pids:return True
        title=ctypes.create_unicode_buffer(512);cls=ctypes.create_unicode_buffer(256)
        user.GetWindowTextW(hwnd,title,512);user.GetClassNameW(hwnd,cls,256)
        rect=RECT();user.GetWindowRect(hwnd,ctypes.byref(rect))
        large=rect.right-rect.left>600 and rect.bottom-rect.top>400
        found.append({'handle':int(hwnd),'title':title.value,'class':cls.value,'large':large,'visible':bool(user.IsWindowVisible(hwnd))})
        if large and ('Q' in cls.value or '剪映' in title.value):
            user.ShowWindow(hwnd,9)
        return True
    user.EnumWindows(callback,None)
    print(json.dumps(found,ensure_ascii=False),flush=True)


def capture_native():
    import ctypes,time
    from ctypes import wintypes
    from PIL import ImageGrab
    user=ctypes.windll.user32;user.SetProcessDPIAware()
    class RECT(ctypes.Structure):_fields_=[('left',ctypes.c_long),('top',ctypes.c_long),('right',ctypes.c_long),('bottom',ctypes.c_long)]
    targets=[]
    @ctypes.WINFUNCTYPE(ctypes.c_bool,ctypes.c_void_p,ctypes.c_void_p)
    def callback(hwnd,_):
        title=ctypes.create_unicode_buffer(512);user.GetWindowTextW(hwnd,title,512)
        if title.value=='剪映专业版' and user.IsWindowVisible(hwnd):targets.append(int(hwnd))
        # Restore helper windows that were originally hidden before inspection.
        if int(hwnd) in {133218,330294} and title.value in {'JianyingPro','QTrayIconMessageWindow'}:user.ShowWindow(hwnd,0)
        return True
    user.EnumWindows(callback,None)
    if not targets:raise RuntimeError('No visible Jianying main window')
    hwnd=targets[0];old=user.GetForegroundWindow();r=RECT();user.GetWindowRect(hwnd,ctypes.byref(r))
    user.SetWindowPos(wintypes.HWND(hwnd),wintypes.HWND(-1),0,0,0,0,0x43)
    user.SetForegroundWindow(hwnd);time.sleep(.7)
    out=RUN/'检查/剪映窗口/native_main.png'
    ImageGrab.grab(bbox=(r.left,r.top,r.right,r.bottom)).save(out)
    user.SetWindowPos(wintypes.HWND(hwnd),wintypes.HWND(-2),0,0,0,0,0x3)
    if old:user.SetForegroundWindow(old)
    print(json.dumps({'window':hwnd,'rect':[r.left,r.top,r.right,r.bottom],'image':str(out)},ensure_ascii=False),flush=True)


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('action',choices=['inspect','export','reveal','capture']);p.add_argument('--name');p.add_argument('--output');p.add_argument('--activate',action='store_true');a=p.parse_args()
    if a.action=='inspect': inspect(a.activate)
    elif a.action=='reveal':reveal()
    elif a.action=='capture':capture_native()
    else: export(a.name,a.output)
