"""Original stylized game assets. Run in the task-owned Blender scene."""
import bpy, math, random, os, json
from mathutils import Vector

BASE = r'D:\课\大四上\思辨设计\02_Demo版本\D08_把路走通_Unity_v1'
OUT = os.path.join(BASE, 'UnityProject', 'Assets', 'Resources', 'Models')
os.makedirs(OUT, exist_ok=True)

def color(hexcode):
    rgb = [int(hexcode[i:i+2], 16)/255 for i in (0,2,4)]
    return tuple(v/12.92 if v<=.04045 else ((v+.055)/1.055)**2.4 for v in rgb)+(1,)

palette = {'Cream':'FFF3DA','Coral':'F57857','Teal':'20A9AA','Ink':'23465C',
           'Yellow':'FFC94D','Leaf':'62BC65','LeafLight':'A5D86F','Skin':'DFA578',
           'Hair':'343B4A','Denim':'375B91','White':'FFFDF1','Wood':'BD8053',
           'Pink':'F2ADA0','Glass':'9DDDE1','Tire':'303E4A','Orange':'FF9F38'}
mats={}
for name,h in palette.items():
    mat=bpy.data.materials.get('MAT-'+name) or bpy.data.materials.new('MAT-'+name)
    mat.use_nodes=True
    bs=next(n for n in mat.node_tree.nodes if n.type=='BSDF_PRINCIPLED')
    bs.inputs['Base Color'].default_value=color(h)
    bs.inputs['Roughness'].default_value=.72
    mat.diffuse_color=color(h)
    mats[name]=mat

collection=bpy.data.collections.get('COL-SunnyPath') or bpy.data.collections.new('COL-SunnyPath')
if collection.name not in bpy.context.scene.collection.children:
    bpy.context.scene.collection.children.link(collection)
roots={}
active=None

def relink(o):
    for c in list(o.users_collection): c.objects.unlink(o)
    collection.objects.link(o)
    return o

def root(name):
    global active
    o=bpy.data.objects.new(name,None); collection.objects.link(o)
    roots[name]=o; active=o
    return o

def finish(o,name,mat):
    relink(o); o.name='GEO-'+name; o.parent=active
    o.data.materials.append(mats[mat]); return o

def box(name,loc,size,mat,bevel=.035):
    bpy.ops.mesh.primitive_cube_add(size=1,location=loc)
    o=bpy.context.object; o.scale=size
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    finish(o,name,mat)
    if bevel:
        mod=o.modifiers.new('SoftEdge','BEVEL'); mod.width=bevel; mod.segments=2
        o.modifiers.new('WeightedNormals','WEIGHTED_NORMAL')
    return o

def sphere(name,loc,size,mat):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=16,ring_count=10,radius=1,location=loc)
    o=bpy.context.object; o.scale=size; finish(o,name,mat)
    for p in o.data.polygons:p.use_smooth=True
    return o

def cyl(name,loc,r,depth,mat,axis='Z',verts=20):
    bpy.ops.mesh.primitive_cylinder_add(vertices=verts,radius=r,depth=depth,location=loc)
    o=bpy.context.object
    if axis=='Y':o.rotation_euler.x=math.pi/2
    if axis=='X':o.rotation_euler.y=math.pi/2
    finish(o,name,mat)
    b=o.modifiers.new('Edge','BEVEL');b.width=.016;b.segments=2
    for p in o.data.polygons:p.use_smooth=True
    return o

def rod(name,a,b,r,mat):
    a,b=Vector(a),Vector(b)
    o=cyl(name,(a+b)/2,r,(b-a).length,mat)
    o.rotation_euler=(b-a).to_track_quat('Z','Y').to_euler()
    return o

def torus(name,loc,major,minor,mat):
    bpy.ops.mesh.primitive_torus_add(major_segments=28,minor_segments=8,location=loc,major_radius=major,minor_radius=minor,rotation=(math.pi/2,0,0))
    o=finish(bpy.context.object,name,mat)
    for p in o.data.polygons:p.use_smooth=True
    return o

def hero():
    root('Hero')
    box('ChairBase',(-.05,0,.36),(.96,.64,.22),'Cream',.09)
    box('Battery',(-.27,0,.31),(.4,.58,.2),'Teal',.045)
    box('Seat',(-.12,0,.62),(.65,.66,.14),'Ink',.055)
    box('Backrest',(-.47,0,.99),(.12,.68,.7),'Teal',.055)
    for s in [-1,1]:
        y=s*.43
        cyl('WheelRear'+str(s),(-.32,y,.4),.38,.12,'Tire','Y',28)
        cyl('WheelHub'+str(s),(-.32,y+s*.071,.4),.27,.02,'Cream','Y',28)
        cyl('WheelCenter'+str(s),(-.32,y+s*.087,.4),.095,.025,'Coral','Y')
        torus('PushRing'+str(s),(-.32,y+s*.095,.4),.28,.017,'Teal')
        for j in range(6):
            a=j*math.tau/6
            rod('Spoke',(-.32,y+s*.09,.4),(-.32+math.cos(a)*.25,y+s*.09,.4+math.sin(a)*.25),.012,'Teal')
        cyl('WheelFront'+str(s),(.48,s*.34,.17),.155,.1,'Tire','Y')
        cyl('FrontHub'+str(s),(.48,s*.399,.17),.08,.016,'Yellow','Y')
        rod('CasterFork',(.48,s*.34,.18),(.43,s*.34,.44),.027,'Cream')
        box('Armrest',(-.03,s*.39,.99),(.61,.09,.09),'Ink',.035)
        rod('ArmSupport',(-.1,s*.38,.62),(-.1,s*.38,.96),.027,'Cream')
    box('Footrest',(.67,0,.18),(.37,.67,.075),'Teal',.025)
    box('Hips',(-.1,0,.78),(.42,.46,.23),'Denim',.09)
    sphere('Jacket',(-.2,0,1.12),(.24,.28,.37),'Yellow')
    cyl('Neck',(-.17,0,1.46),.075,.16,'Skin')
    sphere('Head',(-.15,0,1.66),(.18,.17,.23),'Skin')
    sphere('Hair',(-.20,0,1.78),(.18,.185,.16),'Hair')
    sphere('HairBack',(-.30,0,1.66),(.095,.17,.18),'Hair')
    sphere('Nose',(.023,0,1.66),(.055,.06,.055),'Skin')
    for s in [-1,1]:
        sphere('Ear',(-.17,s*.165,1.65),(.05,.035,.07),'Skin')
        sphere('Eye',(.007,s*.111,1.72),(.018,.018,.025),'Ink')
        rod('UpperArm',(-.23,s*.25,1.34),(-.14,s*.34,1.08),.075,'Yellow')
        rod('Forearm',(-.14,s*.34,1.08),(.23,s*.34,1.04),.059,'Skin')
        sphere('Hand',(.25,s*.34,1.04),(.09,.055,.048),'Skin')
        rod('Thigh',(-.08,s*.15,.79),(.40,s*.15,.74),.116,'Denim')
        rod('Shin',(.40,s*.15,.74),(.48,s*.15,.32),.087,'Denim')
        box('Sneaker',(.59,s*.15,.28),(.33,.19,.15),'White',.065)
        box('SneakerSole',(.61,s*.15,.215),(.34,.20,.035),'Coral',.012)
    box('Joystick',(.22,-.39,1.04),(.18,.13,.07),'Teal',.02)
    cyl('ControlStick',(.24,-.39,1.105),.02,.09,'Ink')
    sphere('ControlTip',(.24,-.39,1.15),(.033,.033,.028),'Coral')

def building(name,market=False):
    root(name)
    w=7 if market else 5.6
    box('Foundation',(0,0,.12),(w+.3,4.5,.24),'Cream',.06)
    box('Facade',(0,.55,2.1),(w,3.4,4),'Cream' if market else 'Pink',.1)
    box('Cornice',(0,.55,4.18),(w+.3,3.7,.22),'Teal',.04)
    if not market:
        box('Roof',(0,.55,4.43),(w+.45,3.95,.3),'Coral',.09)
    for x in [-1.75,1.75]:
        box('WindowFrame',(x,-1.185,2.3),(1.20,.12,1.48),'White',.06)
        box('Window',(x,-1.26,2.3),(1,.05,1.27),'Glass',.025)
        box('WindowMullion',(x,-1.30,2.3),(.045,.03,1.27),'White',.004)
        box('WindowCross',(x,-1.30,2.3),(1,.03,.045),'White',.004)
        box('WindowLedge',(x,-1.35,1.49),(1.35,.32,.13),'Teal',.025)
        box('FlowerBox',(x,-1.43,1.64),(1.1,.23,.23),'Coral',.025)
        for j in range(4):
            sphere('Flowers',(x-.38+j*.25,-1.43,1.83),(.16,.13,.13),'LeafLight' if j%2 else 'Yellow')
    box('DoorFrame',(0,-1.19,1.34),(1.35,.15,2.55),'White',.09)
    box('Door',(0,-1.3,1.32),(1.12,.08,2.38),'Teal',.07)
    box('DoorGlass',(0,-1.36,1.69),(.88,.03,1.15),'Glass',.04)
    sphere('DoorHandle',(.36,-1.42,1.05),(.035,.035,.08),'Yellow')
    if market:
        for j in range(12):
            aw=box('Awning',(j*w/12-w/2+w/24,-1.85,3.05),(w/12+.008,1.7,.12),'Yellow' if j%2 else 'Cream',.015)
            aw.rotation_euler.x=.14
            box('Valance',(j*w/12-w/2+w/24,-2.68,2.89),(w/12,.09,.32),'Yellow' if j%2 else 'Cream',.03)
        for x in [-2.3,2.3]:
            box('ProduceTable',(x,-1.85,.65),(1.25,.7,.8),'Wood',.035)
            for j in range(6):sphere('Produce',(x-.4+j%3*.36,-1.98+j//3*.27,1.12),(.17,.16,.15),'Coral' if x<0 else 'Orange')

def props():
    random.seed(9)
    root('Tree')
    cyl('Trunk',(0,0,1.35),.17,2.7,'Wood',verts=10)
    for i in range(8):
        a=i*2.4
        sphere('Canopy',(math.cos(a)*.6,math.sin(a)*.55,2.6+(i%3)*.43),(.84,.76,.8),'LeafLight' if i%3==0 else 'Leaf')
    root('Planter')
    box('Planter',(0,0,.3),(1.7,.85,.6),'Cream',.09)
    box('Soil',(0,0,.62),(1.5,.65,.07),'Wood',.02)
    for i in range(5):sphere('Bush',(-.58+i*.29,0,.88),(.35,.32,.39),'Leaf' if i%2 else 'LeafLight')
    root('Bench')
    for y in [-.2,0,.2]:box('SeatSlat',(0,y,.51),(1.75,.16,.10),'Wood',.02)
    for z in [.85,1.08]:box('BackSlat',(0,.31,z),(1.75,.1,.18),'Wood',.02)
    for x in [-.64,.64]:
        rod('BenchLeg',(x,-.2,.03),(x,-.2,.52),.045,'Teal')
        rod('BenchBack',(x,.3,.03),(x,.3,1.16),.045,'Teal')
    root('Crate')
    box('CrateBody',(0,0,.42),(.95,.82,.84),'Wood',.035)
    for z in [.18,.43,.7]:box('CrateSlat',(0,-.423,z),(.93,.03,.12),'Orange',.012)
    root('Bollard')
    cyl('BollardBase',(0,0,.07),.24,.14,'Cream')
    cyl('Bollard',(0,0,.6),.12,1.05,'Teal')
    cyl('BollardStripe',(0,0,.95),.125,.13,'Yellow')
    sphere('BollardTop',(0,0,1.13),(.12,.12,.12),'Teal')
    root('Lamp')
    cyl('Pole',(0,0,2.3),.065,4.6,'Teal',verts=12)
    rod('LampArm',(0,0,4.5),(.65,0,4.7),.06,'Teal')
    sphere('LampHead',(.68,0,4.66),(.35,.22,.10),'Cream')
    cyl('Foot',(0,0,.08),.22,.16,'Teal')

hero()
if os.environ.get('SUNNY_STAGE')!='hero':
    building('Home')
    building('Market',True)
    props()
for i,(name,r) in enumerate(roots.items()):r.location=(i%4*9,i//4*8,0)

def export_assets():
    report=[]
    for name,r in roots.items():
        original=r.location.copy()
        r.location=(0,0,0)
        bpy.ops.object.select_all(action='DESELECT')
        r.select_set(True)
        objects=list(r.children_recursive)
        for o in objects:o.select_set(True)
        bpy.context.view_layer.objects.active=r
        bpy.ops.export_scene.fbx(filepath=os.path.join(OUT,name+'.fbx'),use_selection=True,
            object_types={'MESH','EMPTY'},use_mesh_modifiers=True,apply_unit_scale=True,
            apply_scale_options='FBX_SCALE_UNITS',axis_forward='-Z',axis_up='Y',
            bake_anim=False,add_leaf_bones=False,mesh_smooth_type='FACE')
        report.append({'asset':name,'objects':len(objects),'faces':sum(len(o.data.polygons) for o in objects if o.type=='MESH')})
        r.location=original
    with open(os.path.join(BASE,'Blender','asset_manifest.json'),'w',encoding='utf-8') as f:json.dump(report,f,indent=2)
    return report

if os.environ.get('SUNNY_BLOCKOUT')!='1':
    report=export_assets()
    bpy.ops.wm.save_as_mainfile(filepath=os.path.join(BASE,'Blender','sunny_assets_v001.blend'))
    print(json.dumps(report))
