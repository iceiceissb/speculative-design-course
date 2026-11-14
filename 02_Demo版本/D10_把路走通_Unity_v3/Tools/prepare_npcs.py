"""Clean engine FBX exports from the authorised Quaternius CC0 originals."""
import bpy,re,json
from pathlib import Path
from mathutils import Matrix
BASE=Path(__file__).resolve().parents[1]
scene=bpy.context.scene;scene.unit_settings.system='METRIC';scene.unit_settings.scale_length=1;scene.render.fps=30
reports=[]
for name in ['Casual_Female','Casual_Male','OldClassy_Female']:
    cname='COL-V3_Q_'+name
    c=bpy.data.collections.get(cname)
    if not c:
        before=set(bpy.data.objects);actions=set(bpy.data.actions)
        bpy.ops.import_scene.fbx(filepath=str(BASE/'ThirdParty/Quaternius'/(name+'.fbx')))
        objs=list(set(bpy.data.objects)-before);new_actions=list(set(bpy.data.actions)-actions)
        c=bpy.data.collections.new(cname);scene.collection.children.link(c)
        for o in objs:
            for old in list(o.users_collection):old.objects.unlink(o)
            c.objects.link(o)
        rig=next(o for o in objs if o.type=='ARMATURE')
        rig['source_asset']=name;rig['source_license']='Quaternius CC0 1.0'
        for track in list(rig.animation_data.nla_tracks):rig.animation_data.nla_tracks.remove(track)
        rig.animation_data.action=None
        for clipname in ['Idle','Walk']:
            action=next(a for a in new_actions if re.search(r'\|'+clipname+r'(?:\.\d+)?$',a.name))
            track=rig.animation_data.nla_tracks.new();track.name=clipname
            strip=track.strips.new(clipname,1,action);strip.name=clipname
            strip.action_frame_start=action.frame_range[0];strip.action_frame_end=action.frame_range[1]
    objs=list(c.objects);rig=next(o for o in objs if o.type=='ARMATURE')
    rig.location=(0,0,0)
    if not rig.get('v3_canonical_geometry'):
        mesh=next(o for o in objs if o.type=='MESH')
        height=max(v.co.z for v in mesh.data.vertices)-min(v.co.z for v in mesh.data.vertices)
        target=1.64 if name=='OldClassy_Female' else 1.80 if name=='Casual_Male' else 1.72
        factor=target/height
        rig.data.transform(Matrix.Scale(factor,4))
        for o in objs:
            if o.type=='MESH':o.data.transform(Matrix.Scale(factor,4));o.location*=factor
        actions={strip.action for track in rig.animation_data.nla_tracks for strip in track.strips}
        for action in actions:
            for layer in action.layers:
                for strip in layer.strips:
                    for bag in strip.channelbags:
                        for curve in bag.fcurves:
                            if curve.data_path.endswith('location'):
                                for point in curve.keyframe_points:
                                    point.co.y*=factor;point.handle_left.y*=factor;point.handle_right.y*=factor
        rig['v3_canonical_geometry']=True;rig['v3_target_height']=target
    scene.frame_set(1);bpy.context.view_layer.update()
    for o in objs:
        if o.type=='MESH':
            for m in o.data.materials:
                for node in m.node_tree.nodes:
                    if node.type=='BSDF_PRINCIPLED':node.inputs['Alpha'].default_value=1;node.inputs['Metallic'].default_value=0;node.inputs['Roughness'].default_value=.75
    bpy.ops.object.select_all(action='DESELECT')
    for o in objs:o.select_set(True)
    bpy.context.view_layer.objects.active=rig
    # Root, mesh and bone units are converted together; only the two everyday clips are retained.
    bpy.ops.export_scene.fbx(filepath=str(BASE/'UnityProject/Assets/Resources/NPCs'/(name+'.fbx')),
        use_selection=True,object_types={'ARMATURE','MESH'},apply_unit_scale=True,apply_scale_options='FBX_SCALE_UNITS',
        axis_forward='-Z',axis_up='Y',add_leaf_bones=False,use_armature_deform_only=True,use_triangles=True,
        bake_anim=True,bake_anim_use_all_actions=False,bake_anim_use_nla_strips=True,bake_anim_simplify_factor=0,
        path_mode='AUTO')
    reports.append({'asset':name,'license':'CC0','clips':['Idle','Walk'],'source_objects':len(objs),'canonical_height':rig.get('v3_target_height')})
    rig.location=(12+len(reports)*4,-7,0)
(BASE/'Blender/manifest_npcs.json').write_text(json.dumps(reports,indent=2),encoding='utf-8')
bpy.ops.wm.save_as_mainfile(filepath=str(BASE/'Blender/sunny_assets_v003.blend'))
print('CLEAN_NPC_EXPORTS',len(reports))
