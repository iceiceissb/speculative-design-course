import bpy, math, os, json
from pathlib import Path
from mathutils import Vector, Matrix

SCRIPT_BASE=Path(__file__).resolve().parents[1]
BASE=SCRIPT_BASE
helper=(BASE/'Tools/v1_asset_helpers.py').read_text(encoding='utf-8').split('\nhero()\nif os.environ')[0]
helper=helper.replace("'MAT-'","'MAT-V2_'").replace("'COL-SunnyPath'","'COL-SunnyPathV2'")
exec(compile(helper,'v1_asset_helpers.py','exec'))
BASE=SCRIPT_BASE
OUT=str(BASE/'UnityProject/Assets/Resources/Models')
group='Body'
for name,h in {'Steel':'94B0B7','RoofDark':'CE624C','Paper':'FAF5DC','Cobalt':'4C7BBA','Lilac':'B6A4D5','DarkWood':'94664B','Soil':'665145'}.items():
    m=bpy.data.materials.get('MAT-V2_'+name) or bpy.data.materials.new('MAT-V2_'+name);m.use_nodes=True
    n=next(n for n in m.node_tree.nodes if n.type=='BSDF_PRINCIPLED')
    n.inputs['Base Color'].default_value=color(h);n.inputs['Roughness'].default_value=.66
    m.diffuse_color=color(h);mats[name]=m

def root(name):
    global active,group
    existing=bpy.data.objects.get('V2-'+name)
    if existing:
        for child in list(existing.children_recursive):bpy.data.objects.remove(child,do_unlink=True)
        bpy.data.objects.remove(existing,do_unlink=True)
    o=bpy.data.objects.new('V2-'+name,None);collection.objects.link(o)
    roots[name]=o;active=o;group='Body';return o

def finish(o,name,mat):
    relink(o);o.name='GEO-V2_'+name;o.parent=active
    o.data.materials.append(mats[mat]);o['export_group']=group
    return o

def line(name,points,r,mat):
    c=bpy.data.curves.new(name,'CURVE');c.dimensions='3D';c.bevel_depth=r;c.bevel_resolution=2
    s=c.splines.new('POLY');s.points.add(len(points)-1)
    for p,v in zip(s.points,points):p.co=(*v,1)
    return finish(bpy.data.objects.new(name,c),name,mat)

def label3d(name,text,loc,size,mat='Ink'):
    c=bpy.data.curves.new(name,'FONT');c.body=text;c.size=size;c.align_x='CENTER';c.extrude=.003;c.resolution_u=3
    o=finish(bpy.data.objects.new(name,c),name,mat);o.location=loc;o.rotation_euler=(math.pi/2,0,0)
    return o

def detailed_hero():
    global group
    hero()
    # Preserve animation groups without retaining hundreds of renderers in Unity.
    person_words=('Hips','Jacket','Neck','Head','Hair','Nose','Ear','Eye','Arm','Hand','Thigh','Shin','Sneaker')
    for o in active.children:
        n=o.name
        if n.startswith('GEO-V2_Eye'):
            bpy.data.objects.remove(o,do_unlink=True);continue
        if any(k in n for k in ('WheelRear','WheelHub','WheelCenter','PushRing','Spoke')):o['export_group']='WheelRearL' if o.location.y<0 else 'WheelRearR'
        elif any(k in n for k in ('WheelFront','FrontHub')):o['export_group']='WheelFrontL' if o.location.y<0 else 'WheelFrontR'
        else:o['export_group']='Person' if any(k in n for k in person_words) and 'Armrest' not in n and 'ArmSupport' not in n else 'Body'
        if 'GEO-V2_Hand' in n:o.location.x=.23;o.scale=(.062,.047,.039)
        if 'GEO-V2_Nose' in n:o.location.x=.028;o.scale=(.043,.045,.040)
    group='Body'
    for side in [-1,1]:
        y=side*.34
        rod('ChassisRail',(-.48,y,.42),(.5,y,.36),.032,'Steel')
        rod('SeatBracket',(-.39,y,.40),(-.18,y,.62),.034,'Teal')
        rod('FootSupport',(.28,y,.39),(.59,y,.18),.029,'Steel')
        for x in [-.4,.25]:cyl('FrameBolt',(x,side*.39,.45),.026,.035,'Steel','Y',12)
        box('SideShell',(-.1,side*.36,.48),(.57,.055,.21),'Teal',.048)
        for j in range(4):box('Vent',(-.29+j*.11,side*.395,.48),(.045,.012,.085),'Ink',.008)
        box('Reflector',(-.5,side*.33,.60),(.02,.12,.055),'Coral',.008)
    box('SeatPiping',(-.12,0,.66),(.67,.67,.04),'Coral',.02)
    box('BackCushion',(-.39,0,1.05),(.07,.53,.57),'Ink',.04)
    for z in [.87,1.03,1.19]:line('SeatStitch',[(-.344,-.21,z),(-.344,.21,z)],.004,'Cobalt')
    box('Display',(.17,-.393,1.083),(.112,.076,.016),'Ink',.012)
    box('Screen',(.17,-.393,1.093),(.083,.053,.006),'Glass',.004)
    for j in range(3):sphere('ControlButton',(.11+j*.052,-.433,1.094),(.014,.011,.005),'Coral' if j==0 else 'Yellow')
    for side in [-1,1]:
        group='WheelRearL' if side<0 else 'WheelRearR'
        for j in range(32):
            a=j*math.tau/32
            o=box('TireTread',(-.32+math.sin(a)*.383,side*.43,.4+math.cos(a)*.383),(.044,.112,.012),'Tire',.004)
            o.rotation_euler.y=a
        for j in range(8):
            a=j*math.tau/8
            cyl('RimBolt',(-.32+math.sin(a)*.18,side*.513,.4+math.cos(a)*.18),.012,.009,'Steel','Y',10)
    group='Person'
    # A collar, placket, cuffs and individual fingers make the sitter read at close range.
    for side in [-1,1]:
        o=box('Collar',(-.08,side*.079,1.40),(.17,.105,.055),'Cream',.018);o.rotation_euler.z=side*.28
        line('JacketSeam',[(-.095,side*.21,.96),(-.073,side*.24,1.12),(-.08,side*.21,1.27)],.004,'Orange')
        sphere('SleeveShoulder',(-.23,side*.25,1.34),(.083,.075,.084),'Yellow')
        sphere('SleeveElbow',(-.14,side*.34,1.08),(.076,.075,.080),'Yellow')
        box('Cuff',(.16,side*.34,1.041),(.07,.13,.13),'Cream',.02)
        for finger in range(4):
            y=side*.34+(finger-1.5)*.022
            rod('Finger',(.245,y,1.04),(.313,y,1.025),.011,'Skin')
        rod('Thumb',(.235,side*.39,1.035),(.284,side*.385,1.015),.016,'Skin')
        sphere('EyeWhite',(-.009,side*.104,1.716),(.012,.023,.025),'White')
        sphere('Iris',(.003,side*.104,1.716),(.006,.012,.014),'Ink')
        line('Brow',[(.001,side*.08,1.758),(.002,side*.105,1.767),(-.008,side*.13,1.756)],.009,'Hair')
        sphere('Cheek',(-.022,side*.119,1.649),(.008,.026,.018),'Pink')
        sphere('SoftKnee',(.40,side*.15,.74),(.112,.118,.11),'Denim')
        for lace in range(3):box('Lace',(.52+lace*.038,side*.15,.353),(.015,.125,.012),'Cream',.004)
        line('DenimSeam',[(.04,side*.225,.82),(.31,side*.225,.79),(.43,side*.225,.67),(.49,side*.225,.38)],.006,'Cobalt')
    line('JacketZip',[(.011,0,.93),(.044,0,1.12),(-.01,0,1.36)],.007,'Cream')
    sphere('ZipPull',(.04,0,1.22),(.012,.022,.035),'Steel')
    line('Smile',[(.027,-.058,1.616),(.039,-.03,1.599),(.041,0,1.594),(.039,.03,1.599),(.027,.058,1.616)],.007,'RoofDark')
    for j in range(6):
        y=-.14+j*.055
        line('HairLock',[(-.23,y,1.872),(-.12,y,1.88),(-.005,y,1.79)],.016,'Hair')

def detailed_house(market=False):
    building('Market' if market else 'Home',market)
    global group
    w=7 if market else 5.6
    if not market:
        for o in list(active.children):
            if 'GEO-V2_Roof' in o.name:bpy.data.objects.remove(o,do_unlink=True)
        vs=[(-w/2-.25,-1.47,4.22),(w/2+.25,-1.47,4.22),(w/2+.25,.55,5.12),(-w/2-.25,.55,5.12),(-w/2-.25,2.57,4.22),(w/2+.25,2.57,4.22)]
        mesh=bpy.data.meshes.new('Roof');mesh.from_pydata(vs,[],[(0,1,2,3),(3,2,5,4),(0,3,4),(1,5,2),(0,4,5,1)]);mesh.update()
        finish(bpy.data.objects.new('Roof',mesh),'TileRoof','Coral')
        for x in [i*.23-w/2 for i in range(int(w/.23)+1)]:
            rod('RoofTile',(x,-1.5,4.24),(x,.55,5.14),.028,'RoofDark')
        for t in [.25,.50,.75]:
            y=-1.47+2.02*t;z=4.24+.9*t
            rod('TileRow',(-w/2-.23,y,z),(w/2+.23,y,z),.015,'Orange')
        box('Chimney',(1.65,1.1,4.95),(.48,.51,1.0),'Cream',.03)
        box('ChimneyCap',(1.65,1.1,5.46),(.64,.65,.12),'RoofDark',.025)
    for x in [-1.75,1.75]:
        for side in [-1,1]:
            shutter=x+side*.81
            box('Shutter',(shutter,-1.31,2.3),(.34,.10,1.45),'Teal',.018)
            for j in range(8):box('ShutterSlat',(shutter,-1.38,1.70+j*.17),(.29,.055,.045),'Glass',.006)
        box('WindowHeader',(x,-1.32,3.1),(1.43,.2,.13),'Cream',.025)
    rod('Gutter',(-w/2-.13,-1.46,4.19),(w/2+.13,-1.46,4.19),.05,'Teal')
    line('Downpipe',[(w/2-.12,-1.49,4.2),(w/2-.12,-1.52,.2)],.045,'Teal')
    box('MailSlot',(0,-1.365,.79),(.39,.035,.055),'Steel',.012)
    box('HouseNumber',(-.85,-1.33,1.70),(.28,.04,.26),'Cream',.024)
    label3d('Number','08',(-.85,-1.361,1.62),.14,'Teal')
    for z in [.5,1.6]:cyl('DoorHinge',(-.56,-1.36,z),.025,.12,'Steel')
    if market:
        box('MarketSign',(0,-1.32,3.70),(3.9,.18,.64),'Teal',.04)
        label3d('MarketLettering','FRESH & LOCAL',(0,-1.425,3.53),.30,'Cream')
        for x in [-2.3,2.3]:
            for j in range(8):box('CrateLattice',(x-.52+j*.15,-2.22,.91),(.055,.05,.44),'Cream',.01)
            for j in range(5):
                rod('ProduceStem',(x-.45+j*.2,-1.99,1.19),(x-.44+j*.2,-1.99,1.38),.015,'Leaf')
        for j in range(12):
            sphere('Scallop',(-w/2+w/24+j*w/12,-2.72,2.75),(w/24,.055,.12),'Yellow' if j%2 else 'Cream')
        box('Chalkboard',(4,-1.75,.87),(1.0,.14,1.35),'Wood',.03)
        box('ChalkFace',(4,-1.84,.9),(.84,.025,1.15),'Ink',.02)
        label3d('Menu','TODAY\nFRESH\n2.80',(4,-1.86,1.2),.17,'Cream')

def library():
    root('Library')
    box('LibraryFoundation',(0,0,.10),(8.6,5.1,.2),'Cream',.05)
    box('LibraryBody',(0,.65,2.25),(8.2,3.7,4.4),'Paper',.12)
    box('LibraryCap',(0,.65,4.55),(8.6,4.0,.32),'Cobalt',.05)
    box('LibraryRoof',(0,.65,4.78),(8.3,3.7,.18),'Cream',.035)
    for x in [-3,-1.7,1.7,3]:
        box('WindowNook',(x,-1.235,2.0),(1.05,.10,2.0),'Ink',.05)
        box('WindowFrame',(x,-1.31,2.0),(1.12,.06,2.1),'Teal',.025)
        box('NookInner',(x,-1.355,2.0),(.94,.04,1.89),'Cream',.018)
        for z in [1.2,1.83,2.46]:
            box('Shelf',(x,-1.46,z),(.91,.20,.065),'Wood',.01)
            for j in range(5):
                c=['Cobalt','Coral','Yellow','Leaf','Lilac'][j]
                box('BookSpine',(x-.33+j*.155,-1.48,z+.23),(.12,.16,.38+(j%2)*.08),c,.012)
    box('Entry',(0,-1.31,1.42),(1.5,.12,2.7),'Teal',.06)
    box('EntryGlass',(0,-1.39,1.69),(1.25,.04,1.70),'Glass',.035)
    rod('EntryHandle',(.50,-1.44,.91),(.50,-1.44,1.49),.027,'Steel')
    box('NamePanel',(0,-1.31,3.78),(4.0,.17,.61),'Cobalt',.04)
    label3d('LibraryName','OPEN BOOKS',(0,-1.42,3.62),.34,'Cream')
    for x in [-3.9,3.9]:
        box('EntryColumn',(x,-1.56,1.65),(.25,.43,3.3),'Cream',.025)
    box('EntryCanopy',(0,-1.61,3.33),(8.4,1.02,.18),'Yellow',.04)

def pavilion():
    root('Pavilion')
    box('GardenDeck',(0,0,.08),(8,5.2,.16),'Cream',.04)
    for x in [-3.2,3.2]:
        for y in [-1.5,1.5]:
            cyl('PergolaPost',(x,y,1.9),.11,3.8,'Wood',verts=12)
    for x in [-3.4,3.4]:box('PergolaSide',(x,0,3.8),(.15,4.1,.2),'Wood',.02)
    for j in range(13):box('PergolaBeam',(-3.3+j*.55,0,3.95),(.18,4.25,.19),'Cream',.02)
    box('GardenSign',(0,-2.03,3.18),(4.5,.13,.65),'Teal',.04)
    label3d('GardenLettering','GROW TOGETHER',(0,-2.12,3.02),.28,'Cream')
    for x in [-2.4,2.4]:
        box('GrowingBed',(x,.4,.4),(1.9,2.2,.8),'Wood',.045)
        box('Soil',(x,.4,.81),(1.72,2,.06),'Soil',.01)
        for i in range(8):
            xx=x-.58+(i%3)*.55; yy=-.25+(i//3)*.58
            rod('PlantStem',(xx,yy,.8),(xx,yy,1.45),.018,'Leaf')
            for side in [-1,1]:sphere('HerbLeaf',(xx+side*.14,yy,1.22),(.23,.10,.075),'LeafLight')
    for x in [-3.2,3.2]:
        for j in range(7):sphere('ClimbingVine',(x,-1.55,1.2+j*.4),(.19,.13,.29),'Leaf')

def leaf(name,base,tip,width,mat='Leaf'):
    a,b=Vector(base),Vector(tip);mid=a.lerp(b,.55);side=(b-a).cross(Vector((0,0,1)))
    if side.length<.01:side=Vector((1,0,0))
    side.normalize();side*=width
    vs=[a,mid+side,b,mid-side,mid+Vector((0,0,.055)),mid-Vector((0,0,.018))]
    mesh=bpy.data.meshes.new(name);mesh.from_pydata(vs,[],[(0,1,4),(1,2,4),(2,3,4),(3,0,4),(1,0,5),(2,1,5),(3,2,5),(0,3,5)]);mesh.update()
    return finish(bpy.data.objects.new(name,mesh),name,mat)

def flower(x,y,z,mat='Coral'):
    rod('FlowerStem',(x,y,z-.35),(x,y,z),.009,'Leaf')
    for j in range(5):
        a=j*math.tau/5;sphere('Petal',(x+math.cos(a)*.065,y+math.sin(a)*.065,z),(.062,.047,.025),mat)
    sphere('FlowerCenter',(x,y,z+.01),(.026,.026,.03),'Yellow')

def detailed_props():
    global active,group
    props()
    active=roots['Tree']
    for j in range(6):
        a=j*2.4
        rod('Branch',(0,0,1.65),(math.cos(a)*.7,math.sin(a)*.6,2.5+j%2*.3),.05,'DarkWood')
    for j in range(14):
        a=j*2.4;x=math.cos(a)*.8;y=math.sin(a)*.72;z=2.5+(j%3)*.34
        leaf('CanopyLeaf',(x,y,z),(x+.3*math.cos(a),y+.3*math.sin(a),z+.15),.12,'LeafLight')
    active=roots['Planter']
    for o in list(active.children):
        if 'Bush' in o.name:bpy.data.objects.remove(o,do_unlink=True)
    for j in range(6):
        x=-.61+j*.24
        for k in range(5):
            a=k*2.4;leaf('Foliage',(x,0,.65),(x+math.cos(a)*.28,math.sin(a)*.25,.93+(k%2)*.17),.09,'LeafLight' if k%2 else 'Leaf')
        if j%2==0:flower(x,-.05,1.10,'Lilac' if j%3==0 else 'Coral')
    active=roots['Bench']
    for x in [-.65,.65]:
        for z in [.86,1.09]:cyl('BenchBolt',(x,.245,z),.022,.025,'Steel','Y',10)
    for z in [.85,1.08]:line('WoodGrain',[(-.72,.251,z),(-.2,.247,z+.015),(.65,.25,z)],.004,'DarkWood')
    active=roots['Bollard']
    for j in range(4):
        a=j*math.pi/2;cyl('BaseBolt',(math.cos(a)*.16,math.sin(a)*.16,.15),.018,.02,'Steel',verts=8)
    active=roots['Lamp']
    line('LampCable',[(0,0,4.2),(.05,0,4.6),(.35,0,4.8),(.65,0,4.72)],.035,'Teal')
    cyl('LampLens',(.68,0,4.57),.14,.035,'White')
    root('Scooter')
    for x in [-.6,.62]:
        cyl('ScooterWheel',(x,0,.20),.20,.13,'Tire','Y',24)
        cyl('ScooterHub',(x,-.08,.20),.12,.015,'Cream','Y',20)
        torus('WheelRim',(x,-.09,.20),.14,.013,'Teal')
    box('ScooterDeck',(-.05,0,.3),(1.18,.36,.13),'Teal',.05)
    box('GripMat',(-.09,0,.375),(.86,.27,.018),'Ink',.01)
    rod('ScooterStem',(.56,0,.3),(.47,0,1.36),.045,'Coral')
    rod('Handle',(.47,-.33,1.36),(.47,.33,1.36),.035,'Ink')
    sphere('ScooterLight',(.52,0,1.20),(.055,.075,.065),'Cream')
    rod('Kickstand',(-.1,.08,.30),(-.15,.35,.02),.018,'Steel')
    root('NoticeBoard')
    for x in [-.68,.68]:box('NoticeLeg',(x,0,1.0),(.12,.14,2),'Wood',.022)
    box('NoticeFrame',(0,0,1.65),(1.8,.18,1.55),'Teal',.05)
    box('CorkPanel',(0,-.105,1.65),(1.61,.03,1.36),'Cream',.015)
    for j in range(5):
        x=-.47+(j%3)*.43;z=1.35+(j//3)*.55
        box('Flyer',(x,-.132,z),(.34,.014,.43),['Coral','Yellow','Paper','Cobalt','Lilac'][j],.008)
        cyl('Pin',(x,-.151,z+.16),.018,.018,'Teal','Y',10)
    box('BoardCanopy',(0,0,2.48),(2,.5,.13),'Coral',.03)
    root('BookCart')
    for x in [-.4,.4]:
        for y in [-.25,.25]:cyl('CartWheel',(x,y,.12),.105,.065,'Tire','Y',16)
    for z in [.3,.8]:box('BookCartShelf',(0,0,z),(1.1,.7,.10),'Wood',.02)
    for x in [-.52,.52]:rod('CartRail',(x,.3,.25),(x,.3,1.15),.025,'Teal')
    for j in range(7):box('CartBook',(-.4+j*.13,-.05,.53),(.10,.44,.38),['Coral','Cobalt','Yellow','Leaf','Lilac'][j%5],.01)
    root('Postbox')
    cyl('PostboxLeg',(0,0,.5),.08,1,'Steel')
    box('Mailbox',(0,0,1.05),(.57,.54,.56),'Coral',.12)
    box('MailOpening',(0,-.28,1.12),(.36,.015,.055),'Ink',.009)
    label3d('MailMark','POST',(0,-.285,.96),.10,'Cream')
    root('Bush')
    for j in range(8):
        a=j*2.4;x=math.cos(a)*.45;y=math.sin(a)*.32
        leaf('LeafCluster',(0,0,.03),(x,y,.40+(j%3)*.14),.15,'Leaf' if j%2 else 'LeafLight')
    for j in range(3):flower(j*.23-.2,-.12,.54,'Yellow')
    root('Tomato')
    sphere('Tomato',(0,0,.20),(.24,.23,.20),'Coral')
    for j in range(5):
        a=j*math.tau/5;leaf('TomatoCalyx',(0,0,.39),(math.cos(a)*.13,math.sin(a)*.13,.41),.025,'Leaf')
    root('Carrot')
    bpy.ops.mesh.primitive_cone_add(vertices=20,radius1=.025,radius2=.105,depth=.46,location=(0,0,.25))
    finish(bpy.context.object,'Carrot','Orange')
    for j in range(6):
        a=j*2.4;leaf('CarrotLeaf',(0,0,.48),(math.cos(a)*.15,math.sin(a)*.15,.76),.035,'Leaf')
    root('Orange')
    sphere('Orange',(0,0,.24),(.23,.23,.23),'Orange')
    rod('OrangeStem',(0,0,.46),(0,0,.52),.018,'Wood');leaf('OrangeLeaf',(0,0,.48),(.18,0,.56),.055,'Leaf')
    root('Book')
    box('BookPages',(0,0,.095),(.56,.76,.13),'Paper',.015)
    for z in [.02,.17]:box('BookCover',(0,0,z),(.60,.79,.035),'Cobalt',.015)
    box('BookSpine',(-.295,0,.10),(.035,.79,.18),'Teal',.013)
    for j in range(4):box('PageLine',(.285,0,.05+j*.025),(.008,.68,.004),'Cream',.001)
    root('Seedling')
    cyl('PlantPot',(0,0,.15),.19,.30,'Coral',verts=20)
    cyl('PlantSoil',(0,0,.305),.17,.025,'Soil')
    rod('MintStem',(0,0,.3),(0,0,.78),.015,'Leaf')
    for j in range(6):
        a=j*2.4;z=.40+j*.045
        leaf('MintLeaf',(0,0,z),(math.cos(a)*.23,math.sin(a)*.23,z+.1),.085,'LeafLight' if j%2 else 'Leaf')
    root('WateringCan')
    cyl('CanBody',(0,0,.24),.25,.45,'Teal',verts=24)
    rod('Spout',(.15,0,.20),(.57,0,.50),.06,'Teal')
    sphere('RoseHead',(.59,0,.53),(.10,.10,.08),'Cream')
    line('CanHandle',[(-.2,-.09,.47),(-.2,-.09,.70),(.19,-.09,.70),(.19,-.09,.47)],.025,'Cream')
    root('Walker')
    group='Body'
    box('Coat',(0,0,1.12),(.40,.49,.58),'Cobalt',.13)
    cyl('WalkerNeck',(.01,0,1.45),.07,.17,'Skin')
    sphere('WalkerHead',(.02,0,1.64),(.17,.16,.21),'Skin')
    sphere('WalkerHair',(-.035,0,1.76),(.16,.17,.13),'Hair')
    sphere('WalkerNose',(.177,0,1.65),(.045,.05,.045),'Skin')
    for s in [-1,1]:
        sphere('WalkerEye',(.158,s*.09,1.70),(.013,.015,.021),'Ink')
        rod('WalkerArm',(0,s*.24,1.35),(.05,s*.29,.88),.060,'Cobalt')
        sphere('WalkerHand',(.05,s*.29,.86),(.06,.05,.075),'Skin')
    for s in [-1,1]:
        group='LegL' if s<0 else 'LegR'
        rod('WalkerLeg',(0,s*.12,.87),(.04,s*.12,.20),.085,'Denim')
        box('WalkerShoe',(.12,s*.12,.13),(.31,.19,.16),'Cream',.06)
    group='Body'
    root('Bird')
    sphere('BirdBody',(0,0,.16),(.16,.09,.10),'Cobalt')
    sphere('BirdHead',(.14,0,.23),(.077,.065,.075),'Cream')
    bpy.ops.mesh.primitive_cone_add(vertices=8,radius1=.027,radius2=0,depth=.09,location=(.23,0,.23),rotation=(0,math.pi/2,0))
    finish(bpy.context.object,'Beak','Orange')
    for side in [-1,1]:leaf('BirdWing',(-.02,0,.19),(-.12,side*.25,.26),.075,'Teal')

def bake_export(name,r):
    deps=bpy.context.evaluated_depsgraph_get();bpy.context.view_layer.update()
    groups={}
    for obj in r.children_recursive:
        if obj.type in {'MESH','CURVE','FONT'}:groups.setdefault(obj.get('export_group','Body'),[]).append(obj)
    temp=bpy.data.objects.new('EXPORT-'+name,None);collection.objects.link(temp)
    created=[];facecount=0
    centers={'WheelRearL':(-.32,-.43,.4),'WheelRearR':(-.32,.43,.4),'WheelFrontL':(.48,-.34,.17),'WheelFrontR':(.48,.34,.17),'LegL':(0,-.12,.82),'LegR':(0,.12,.82)}
    for key,objects in groups.items():
        center=Vector(centers.get(key,(0,0,0)));verts=[];faces=[];slots=[];indices=[];smooth=[];normals=[]
        for obj in objects:
            eo=obj.evaluated_get(deps);mesh=eo.to_mesh();matrix=r.matrix_world.inverted()@obj.matrix_world
            normal_matrix=matrix.to_3x3().inverted().transposed();offset=len(verts)
            verts.extend(tuple(matrix@v.co-center) for v in mesh.vertices)
            for poly in mesh.polygons:
                faces.append(tuple(offset+v for v in poly.vertices));smooth.append(poly.use_smooth)
                material=obj.data.materials[min(poly.material_index,len(obj.data.materials)-1)]
                if material not in slots:slots.append(material)
                indices.append(slots.index(material))
                normals.extend(tuple((normal_matrix@mesh.corner_normals[i].vector).normalized()) for i in poly.loop_indices)
            eo.to_mesh_clear()
        mesh=bpy.data.meshes.new('ExportMesh-'+name+key);mesh.from_pydata(verts,[],faces);mesh.update()
        for m in slots:mesh.materials.append(m)
        for p,idx,sm in zip(mesh.polygons,indices,smooth):p.material_index=idx;p.use_smooth=sm
        if len(normals)==len(mesh.loops):mesh.normals_split_custom_set(normals)
        o=bpy.data.objects.new('GEO-'+key,mesh);collection.objects.link(o);o.parent=temp;o.location=center;created.append(o);facecount+=len(faces)
    bpy.ops.object.select_all(action='DESELECT');temp.select_set(True)
    for o in created:o.select_set(True)
    bpy.context.view_layer.objects.active=temp
    bpy.ops.export_scene.fbx(filepath=os.path.join(OUT,name+'.fbx'),use_selection=True,object_types={'MESH','EMPTY'},use_mesh_modifiers=True,
        apply_unit_scale=True,apply_scale_options='FBX_SCALE_UNITS',axis_forward='-Z',axis_up='Y',bake_anim=False,add_leaf_bones=False,mesh_smooth_type='FACE')
    for o in created:
        mesh=o.data;bpy.data.objects.remove(o,do_unlink=True);bpy.data.meshes.remove(mesh)
    bpy.data.objects.remove(temp,do_unlink=True)
    return {'asset':name,'export_objects':len(groups),'faces':facecount,'source_objects':len(r.children_recursive)}

stage=os.environ.get('SUNNY_V2_STAGE','hero')
if stage=='hero':detailed_hero()
if stage=='architecture':
    detailed_house(False);detailed_house(True);library();pavilion()
if stage=='props':detailed_props()

reports=[]
for name,r in roots.items():reports.append(bake_export(name,r))
offsets={'Hero':(0,0,0),'Home':(9,0,0),'Market':(20,0,0),'Library':(33,0,0),'Pavilion':(47,0,0)}
for i,(name,r) in enumerate(roots.items()):r.location=offsets.get(name,(i%8*4,12+i//8*5,0))
report_path=BASE/'Blender'/('manifest_'+stage+'.json');report_path.write_text(json.dumps(reports,indent=2),encoding='utf-8')
bpy.ops.wm.save_as_mainfile(filepath=str(BASE/'Blender/sunny_assets_v002.blend'))
print(json.dumps(reports))
