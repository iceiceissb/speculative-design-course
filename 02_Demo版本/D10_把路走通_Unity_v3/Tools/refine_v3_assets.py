"""V3 original seated girl; preserves the existing wheelchair and all V2 source data."""
import bpy,math,json,os
from pathlib import Path
from mathutils import Vector
BASE=Path(__file__).resolve().parents[1]
code=(BASE/'Tools/v2_asset_helpers.py').read_text(encoding='utf-8').split("stage=os.environ")[0]
code=code.replace('V2_','V3_').replace('V2-','V3-').replace('Path(__file__).resolve().parents[1]','Path(__file__).resolve().parents[1]')
exec(compile(code,'v3_helpers','exec'))
BASE=Path(__file__).resolve().parents[1];OUT=str(BASE/'UnityProject/Assets/Resources/Models')

def newmat(name,h,rough=.64):
    m=bpy.data.materials.get('MAT-V3_'+name) or bpy.data.materials.new('MAT-V3_'+name);m.use_nodes=True
    n=next(n for n in m.node_tree.nodes if n.type=='BSDF_PRINCIPLED')
    n.inputs['Base Color'].default_value=color(h);n.inputs['Roughness'].default_value=rough
    m.diffuse_color=color(h);mats[name]=m

for name,h in {'GirlSkin':'F7DCCA','GirlHair':'252937','Rose':'EE9C97','Cardigan':'F2AE8B','Pinafore':'79BEB9'}.items():newmat(name,h)

def smooth_sphere(name,loc,size,mat):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=32,ring_count=20,radius=1,location=loc)
    o=bpy.context.object;o.scale=size;finish(o,name,mat)
    for p in o.data.polygons:p.use_smooth=True
    return o

def tube(name,points,radii,mat,segments=16):
    ps=[Vector(p) for p in points];verts=[];faces=[]
    for i,(p,r) in enumerate(zip(ps,radii)):
        tangent=(ps[min(i+1,len(ps)-1)]-ps[max(i-1,0)]).normalized()
        u=tangent.cross(Vector((0,1,0))).normalized()
        if u.length<.1:u=Vector((1,0,0))
        v=tangent.cross(u).normalized()
        for j in range(segments):verts.append(tuple(p+r*(u*math.cos(j*math.tau/segments)+v*math.sin(j*math.tau/segments))))
    for i in range(len(ps)-1):
        for j in range(segments):faces.append((i*segments+j,i*segments+(j+1)%segments,(i+1)*segments+(j+1)%segments,(i+1)*segments+j))
    faces.extend([tuple(reversed(range(segments))),tuple((len(ps)-1)*segments+j for j in range(segments))])
    mesh=bpy.data.meshes.new(name);mesh.from_pydata(verts,[],faces);mesh.update()
    o=finish(bpy.data.objects.new(name,mesh),name,mat)
    for p in mesh.polygons:p.use_smooth=True
    mod=o.modifiers.new('SoftSurface','SUBSURF');mod.levels=1;mod.render_levels=1
    return o

def cardigan():
    rings=[(.82,-.18,.16,.22),(.88,-.17,.205,.24),(.98,-.18,.206,.245),(1.10,-.19,.195,.245),(1.19,-.20,.175,.23),(1.25,-.20,.115,.155),(1.27,-.20,.075,.09)]
    verts=[];faces=[];n=32
    for z,x,rx,ry in rings:
        for j in range(n):a=j*math.tau/n;verts.append((x+rx*math.cos(a),ry*math.sin(a),z))
    for k in range(len(rings)-1):
        for j in range(n):faces.append((k*n+j,k*n+(j+1)%n,(k+1)*n+(j+1)%n,(k+1)*n+j))
    faces.extend([tuple(reversed(range(n))),tuple((len(rings)-1)*n+j for j in range(n))])
    mesh=bpy.data.meshes.new('GirlCardigan');mesh.from_pydata(verts,[],faces);mesh.update()
    o=finish(bpy.data.objects.new('GirlCardigan',mesh),'GirlCardigan','Cardigan')
    for f in mesh.polygons:f.use_smooth=True
    mod=o.modifiers.new('TailoredSilhouette','SUBSURF');mod.levels=2

def hair_cap():
    center=Vector((-.165,0,1.475));verts=[];faces=[];rows=18;cols=56
    for i in range(rows+1):
        for j in range(cols):
            phi=j*math.tau/cols
            end=1.01+max(0,-math.cos(phi))*.95+abs(math.sin(phi))**2*.40
            theta=.015+(end-.015)*i/rows
            verts.append(tuple(center+Vector((.211*math.sin(theta)*math.cos(phi),.216*math.sin(theta)*math.sin(phi),.235*math.cos(theta)))))
    for i in range(rows):
        for j in range(cols):faces.append((i*cols+j,i*cols+(j+1)%cols,(i+1)*cols+(j+1)%cols,(i+1)*cols+j))
    mesh=bpy.data.meshes.new('GirlHairCap');mesh.from_pydata(verts,[],faces);mesh.update()
    o=finish(bpy.data.objects.new('GirlHairCap',mesh),'GirlHairCap','GirlHair')
    for f in mesh.polygons:f.use_smooth=True
    solid=o.modifiers.new('HairThickness','SOLIDIFY');solid.thickness=.008

def fringe():
    verts=[];faces=[];cols=40;rows=6
    for k in range(rows+1):
        t=k/rows
        for j in range(cols+1):
            y=-.17+.34*j/cols
            low=1.553+.019*abs(y/.17)+.004*math.cos(y/.17*3*math.pi)
            z=1.655*(1-t)+low*t
            x=-.165+.215*math.sqrt(max(.025,1-(y/.219)**2-((z-1.475)/.242)**2))+.008
            verts.append((x,y,z))
    for k in range(rows):
        for j in range(cols):
            a=k*(cols+1)+j;faces.append((a,a+1,a+cols+2,a+cols+1))
    mesh=bpy.data.meshes.new('SoftFringe');mesh.from_pydata(verts,[],faces);mesh.update()
    o=finish(bpy.data.objects.new('SoftFringe',mesh),'SoftFringe','GirlHair')
    for f in mesh.polygons:f.use_smooth=True
    solid=o.modifiers.new('FringeThickness','SOLIDIFY');solid.thickness=.008
    bevel=o.modifiers.new('FringeSoftEdge','BEVEL');bevel.width=.003;bevel.segments=2

def girl():
    global group
    detailed_hero()
    for o in list(active.children_recursive):
        if o.get('export_group')=='Person' or o.name.startswith('GEO-V3_Forearm'):bpy.data.objects.remove(o,do_unlink=True)
    group='Torso'
    box('SeatedOveralls',(-.10,0,.78),(.40,.43,.22),'Pinafore',.09)
    cardigan()
    box('OverallBib',(.016,0,1.025),(.035,.29,.29),'Pinafore',.045)
    for s in [-1,1]:
        tube('OverallStrap',[(.029,s*.124,1.10),(-.013,s*.13,1.19),(-.09,s*.13,1.245),(-.2,s*.13,1.255)],[.025,.025,.026,.028],'Pinafore',10)
        smooth_sphere('StrapButton',(.039,s*.124,1.108),(.008,.017,.017),'Cream')
        smooth_sphere('ShirtCollar',(-.062,s*.055,1.247),(.080,.060,.024),'Cream')
        tube('CardiganSleeve',[(-.20,s*.215,1.20),(-.205,s*.268,1.16),(-.18,s*.31,1.08),(-.13,s*.33,1.04)],[.083,.084,.077,.070],'Cardigan')
        box('RibbedCuff',(-.09,s*.335,1.04),(.07,.127,.12),'Cream',.025)
    box('FrontPocket',(.040,0,1.002),(.018,.15,.09),'Teal',.018)
    for j in range(5):box('PocketStitch',(.050,-.06+j*.03,.972),(.006,.012,.004),'Cream',.001)
    cyl('GirlNeck',(-.17,0,1.284),.064,.12,'GirlSkin')
    group='Head'
    smooth_sphere('GirlHead',(-.15,0,1.475),(.198,.202,.218),'GirlSkin')
    hair_cap()
    fringe()
    for s in [-1,1]:
        smooth_sphere('GirlEar',(-.17,s*.192,1.445),(.038,.026,.052),'GirlSkin')
        smooth_sphere('InnerEar',(-.141,s*.207,1.447),(.009,.014,.028),'Rose')
        # Flat almond eyes sit against the face, without protruding eyeballs.
        smooth_sphere('GirlEye',(.026,s*.089,1.509),(.008,.031,.014),'GirlHair')
        smooth_sphere('EyeCatchlight',(.033,s*.082,1.513),(.003,.007,.006),'Cream')
        line('UpperEyelid',[(.021,s*.063,1.515),(.027,s*.087,1.525),(.019,s*.114,1.515)],.0038,'GirlHair')
        line('GirlBrow',[(.004,s*.064,1.548),(.010,s*.087,1.553),(.000,s*.115,1.546)],.0048,'GirlHair')
        smooth_sphere('GirlCheek',(.012,s*.123,1.454),(.005,.030,.012),'Rose')
        smooth_sphere('BobSide',(-.22,s*.182,1.447),(.107,.049,.148),'GirlHair')
        tube('SoftPigtail',[(-.29,s*.175,1.44),(-.31,s*.212,1.38),(-.31,s*.205,1.31),(-.27,s*.19,1.285)],[.059,.066,.057,.024],'GirlHair')
        smooth_sphere('HairTie',(-.298,s*.201,1.402),(.066,.058,.018),'Rose')
    smooth_sphere('GirlNose',(.048,0,1.467),(.020,.024,.024),'GirlSkin')
    line('GirlSmile',[(.030,-.027,1.414),(.035,-.014,1.407),(.037,0,1.405),(.035,.014,1.407),(.030,.027,1.414)],.0035,'Rose')
    # Small bow, visible from the street camera on the left side of the head.
    for s in [-1,1]:
        o=smooth_sphere('RibbonLoop',(-.12+s*.037,-.222,1.59+s*.018),(.048,.017,.028),'Rose');o.rotation_euler.y=s*.45
    smooth_sphere('RibbonKnot',(-.12,-.235,1.59),(.018,.013,.020),'Coral')
    group='Hands'
    for s in [-1,1]:
        tube('GirlForearm',[(-.105,s*.335,1.04),(-.015,s*.337,1.038),(.10,s*.338,1.032),(.205,s*.34,1.038)],[.053,.054,.047,.037],'GirlSkin')
        smooth_sphere('GirlHand',(.225,s*.34,1.038),(.058,.044,.031),'GirlSkin')
        for j in range(4):
            y=s*.34+(j-1.5)*.019
            tube('GirlFinger',[(.238,y,1.038),(.276,y,1.032),(.292-(abs(j-1.5)*.006),y,1.023)],[.009,.009,.006],'GirlSkin',10)
        tube('GirlThumb',[(.214,s*.376,1.033),(.249,s*.383,1.021),(.264,s*.377,1.018)],[.014,.013,.007],'GirlSkin',10)
    group='Legs'
    for s in [-1,1]:
        tube('OverallLeg',[(-.14,s*.125,.80),(.03,s*.13,.79),(.24,s*.13,.754),(.374,s*.13,.72),(.42,s*.13,.61),(.447,s*.13,.40)],[.105,.110,.108,.10,.084,.070],'Pinafore',20)
        box('OverallCuff',(.447,s*.13,.405),(.142,.149,.060),'Pinafore',.020)
        cyl('CreamSock',(.448,s*.13,.364),.071,.10,'Cream')
        box('GirlSneaker',(.535,s*.13,.286),(.285,.17,.142),'Rose',.055)
        box('GirlSole',(.55,s*.13,.223),(.29,.18,.029),'Cream',.012)
        for j in range(3):box('GirlLace',(.487+j*.032,s*.13,.358),(.012,.103,.010),'Cream',.004)
    return active

hero=girl()
report=bake_export('Hero',hero)
hero.location=(0,0,0)
(BASE/'Blender/manifest_v3_hero.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
bpy.ops.wm.save_as_mainfile(filepath=str(BASE/'Blender/sunny_assets_v003.blend'))
print(json.dumps(report))
