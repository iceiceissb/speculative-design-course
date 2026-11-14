"""Bake explicit triangles for Unity to avoid ambiguous decorative n-gon tessellation."""
import bpy,json
from pathlib import Path
BASE=Path(__file__).resolve().parents[1]
code=(BASE/'Tools/v2_asset_helpers.py').read_text(encoding='utf-8').split("stage=os.environ")[0]
code=code.replace("mesh_smooth_type='FACE'","mesh_smooth_type='FACE',use_triangles=True")
exec(compile(code,'export_helpers','exec'))
BASE=Path(__file__).resolve().parents[1];OUT=str(BASE/'UnityProject/Assets/Resources/Models')
reports=[]
for path in sorted(Path(OUT).glob('*.fbx')):
    name=path.stem;r=bpy.data.objects.get(('V3-' if name=='Hero' else 'V2-')+name)
    if r:reports.append(bake_export(name,r))
(BASE/'Blender/manifest_triangulated.json').write_text(json.dumps(reports,indent=2),encoding='utf-8')
bpy.context.scene.name='SunnyPathV3_Assets'
bpy.ops.wm.save_as_mainfile(filepath=str(BASE/'Blender/sunny_assets_v003.blend'))
print('TRIANGULATED_ASSETS',len(reports))
