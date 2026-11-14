import bpy,math,os
from pathlib import Path
from mathutils import Vector
BASE=Path(__file__).resolve().parents[1]
subject=os.environ.get('SUNNY_PREVIEW','hero')
scene=bpy.context.scene
if subject=='hero':
    root=bpy.data.objects['V3-Hero'];objects=[root]+list(root.children_recursive)
else:
    objects=list(bpy.data.collections['COL-V3_Quaternius'].objects)
    rig=next(o for o in objects if o.type=='ARMATURE')
    rig.animation_data.action=next(a for a in bpy.data.actions if a.name.endswith('|Idle'))
    scene.frame_set(1)
    palette={'Skin':'E7BC9F','Shirt':'EBA184','Pants':'5C8C98','Belt':'715949','Face':'FCF5DC','Hair':'343847'}
    def lin(h):
        return tuple(((int(h[i:i+2],16)/255+.055)/1.055)**2.4 for i in (0,2,4))+(1,)
    for o in objects:
        if o.type!='MESH':continue
        for m in o.data.materials:
            n=next(n for n in m.node_tree.nodes if n.type=='BSDF_PRINCIPLED')
            n.inputs['Base Color'].default_value=lin(palette.get(m.name.split('.')[0],'F7DCCA'));n.inputs['Alpha'].default_value=1;n.inputs['Metallic'].default_value=0;n.inputs['Roughness'].default_value=.75

state={o:o.hide_render for o in scene.objects}
for o in state:o.hide_render=o not in objects
scene.view_settings.view_transform='Standard';scene.view_settings.look='None';scene.view_settings.exposure=0;scene.view_settings.gamma=1
scene.world.use_nodes=True;scene.world.node_tree.nodes['Background'].inputs[0].default_value=(.8,.86,.83,1);scene.world.node_tree.nodes['Background'].inputs[1].default_value=.6
bpy.context.view_layer.update();deps=bpy.context.evaluated_depsgraph_get()
vs=[]
for o in objects:
    if o.type not in {'MESH','CURVE'}:continue
    ev=o.evaluated_get(deps)
    vs.extend(ev.matrix_world@Vector(v) for v in ev.bound_box)
mn=Vector(tuple(min(v[i] for v in vs) for i in range(3)));mx=Vector(tuple(max(v[i] for v in vs) for i in range(3)));center=(mn+mx)/2;h=mx.z-mn.z

cam=bpy.data.objects.get('CAM-V3_Preview')
if not cam:
    cam=bpy.data.objects.new('CAM-V3_Preview',bpy.data.cameras.new('CAM-V3_Preview'));scene.collection.objects.link(cam)
cam.hide_render=False;scene.camera=cam
cam.location=center+Vector((h*1.6,-h*2.15,h*.9));cam.rotation_euler=(center-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.type='ORTHO';cam.data.ortho_scale=h*1.25
for name,offset,power,size in [('Key',(2,-3,5),450,4),('Fill',(-3,-1,3),250,3),('Rim',(-1,3,4),350,3)]:
    o=bpy.data.objects.get('LGT-V3_'+name)
    if not o:o=bpy.data.objects.new('LGT-V3_'+name,bpy.data.lights.new('LGT-V3_'+name,'AREA'));scene.collection.objects.link(o)
    o.hide_render=False;o.location=center+Vector(offset)*h/1.8;o.rotation_euler=(center-o.location).to_track_quat('-Z','Y').to_euler();o.data.energy=power*(h/1.8)**2;o.data.shape='DISK';o.data.size=size*h/1.8
scene.render.engine='CYCLES';scene.cycles.samples=24;scene.cycles.use_denoising=True;scene.render.resolution_x=1000;scene.render.resolution_y=1000;scene.render.resolution_percentage=100
scene.render.filepath=str(BASE/'QA'/('hero_detail_v3.png' if subject=='hero' else 'npc_detail_v3.png'))
bpy.ops.render.render(write_still=True)
for o,value in state.items():o.hide_render=value
print('PREVIEW_READY',subject,'bounds',list(mn),list(mx))
