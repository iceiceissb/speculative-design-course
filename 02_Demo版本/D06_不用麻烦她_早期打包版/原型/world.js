/* A small, navigable Three.js stage. The choreography is illustrative, not a mobility controller. */
class StoryWorld {
  constructor(canvas){
    if(!window.THREE)throw new Error('Three.js did not load');
    this.canvas=canvas;this.scene=new THREE.Scene();this.scene.background=new THREE.Color('#373630');
    this.scene.fog=new THREE.Fog('#373630',27,65);
    this.renderer=new THREE.WebGLRenderer({canvas,antialias:true,preserveDrawingBuffer:true,powerPreference:'high-performance'});
    this.renderer.setPixelRatio(Math.min(devicePixelRatio||1,1.7));this.renderer.shadowMap.enabled=true;
    this.renderer.shadowMap.type=THREE.PCFSoftShadowMap;this.renderer.outputEncoding=THREE.sRGBEncoding;
    this.renderer.toneMapping=THREE.ACESFilmicToneMapping;this.renderer.toneMappingExposure=.79;
    this.camera=new THREE.PerspectiveCamera(39,1,.1,100);this.focus=new THREE.Vector3(0,1.15,0);
    this.orbit={theta:.42,phi:1.19,r:14.8};this.view=0;this.chapter=0;this.action=null;this.time=0;
    this.scene.add(new THREE.HemisphereLight(0xffefd8,0x403d38,.43));
    const key=new THREE.DirectionalLight(0xffd8a7,.93);key.position.set(-7,13,10);key.castShadow=true;
    key.shadow.mapSize.set(2048,2048);Object.assign(key.shadow.camera,{left:-13,right:13,top:12,bottom:-12,near:.1,far:35});
    key.shadow.bias=-.0003;key.shadow.normalBias=.025;this.scene.add(key);
    const fill=new THREE.DirectionalLight(0xb7cead,.27);fill.position.set(8,7,-8);this.scene.add(fill);
    this.stageRoots=[this.buildRoad(),this.buildMarket(),this.buildHome()];
    this.chair=this.buildChair();this.xu=this.buildXu();this.scene.add(this.chair,this.xu);
    this.buildInteractionProps();this.setScene(0,{});this.setupPointer();
    new ResizeObserver(()=>this.resize()).observe(canvas.parentElement);this.resize();
    let previous=performance.now();const frame=now=>{const dt=Math.min((now-previous)/1000,.05);previous=now;this.tick(dt);requestAnimationFrame(frame)};requestAnimationFrame(frame);
  }
  mat(color,metalness=.03){return new THREE.MeshStandardMaterial({color,roughness:.84,metalness})}
  emissive(color,intensity=.75){return new THREE.MeshStandardMaterial({color,emissive:color,emissiveIntensity:intensity,roughness:.5})}
  mesh(geo,mat,parent,x=0,y=0,z=0){const o=new THREE.Mesh(geo,typeof mat==='string'?this.mat(mat):mat);o.position.set(x,y,z);o.castShadow=true;o.receiveShadow=true;parent.add(o);return o}
  box(parent,w,h,d,color,x=0,y=0,z=0){return this.mesh(new THREE.BoxGeometry(w,h,d),color,parent,x,y,z)}
  ball(parent,r,color,x=0,y=0,z=0,sx=1,sy=1,sz=1){const o=this.mesh(new THREE.SphereGeometry(r,14,10),color,parent,x,y,z);o.scale.set(sx,sy,sz);return o}
  cyl(parent,r,h,color,x=0,y=0,z=0,segments=12){return this.mesh(new THREE.CylinderGeometry(r,r,h,segments),color,parent,x,y,z)}
  rod(parent,a,b,r,color){const p=new THREE.Vector3(...a),q=new THREE.Vector3(...b),v=q.clone().sub(p);const o=this.cyl(parent,r,v.length(),color,...p.clone().add(q).multiplyScalar(.5).toArray(),10);o.quaternion.setFromUnitVectors(new THREE.Vector3(0,1,0),v.normalize());return o}
  platform(root,w=14,d=10){this.box(root,w,.36,d,'#696657',0,-.23,0);this.box(root,w,.08,d,'#b6ab8e',0,-.02,0);this.box(root,w+.06,.08,.08,'#5d5b4e',0,-.18,d/2);this.box(root,.08,.08,d,'#5d5b4e',-w/2,-.18,0)}
  leaves(parent,x,y,z,n=6){for(let i=0;i<n;i++){const ang=i*2.4,h=.27+(i%3)*.08;this.rod(parent,[x,y,z],[x+Math.cos(ang)*.18,y+h,z+Math.sin(ang)*.15],.018,'#759163');this.ball(parent,.14,i%2?'#608b5d':'#8ca875',x+Math.cos(ang)*.22,y+h,z+Math.sin(ang)*.19,.66,1.15,.42)}}
  tree(parent,x,z,scale=1){const g=new THREE.Group();parent.add(g);g.position.set(x,0,z);g.scale.setScalar(scale);this.cyl(g,.14,2.8,'#705943',0,1.4,0);for(let i=0;i<7;i++){const a=i*2.4;this.ball(g,.72,i%2?'#718966':'#87966e',Math.sin(a)*.52,2.73+(i%3)*.22,Math.cos(a)*.38,1.2,.8,1)}this.box(g,1.15,.13,1.15,'#897b63',0,.05,0);return g}
  buildRoad(){const root=new THREE.Group();this.scene.add(root);this.platform(root);
    for(let i=-6;i<=6;i++)for(let j=-4;j<=4;j++){const c=(i+j)%4===0?'#ada48e':'#b8af9a';this.box(root,.94,.025,.94,c,i*.99,.03,j*.99)}
    // A shallow actual grade. Actors follow its surface rather than travelling
    // horizontally through it; the entry is almost flush with the paving.
    const ramp=this.box(root,4.4,.08,5.6,'#c5b89b',0,.19,0);ramp.rotation.x=-.055;
    for(let i=-2;i<=2;i++){const line=this.box(root,.03,.009,5.35,'#a59b83',i*.87,.237,0);line.rotation.x=-.055}
    for(const side of [-1,1]){
      const x=side*3.25;
      this.rod(root,[x,.08,-2.7],[x,1.15,-2.7],.045,'#71756d');
      this.rod(root,[x,.08,2.7],[x,1.15,2.7],.045,'#71756d');
      this.rod(root,[x,1.15,-2.7],[x,1.15,2.7],.045,'#71756d');
    }
    this.tree(root,-5.25,-3.1,.85);this.tree(root,5.7,-3.15,1.03);
    const wall=this.box(root,2.0,1.32,.23,'#a9967a',5.75,.66,3.3);for(let i=0;i<4;i++)this.box(root,.03,.6,.02,'#8c7f6d',4.95+i*.48,.45,3.43);
    this.box(root,1.9,.1,.65,'#80634b',-4.6,.6,3.5);for(let x of [-5.42,-3.78])this.box(root,.12,.55,.12,'#635447',x,.3,3.5);
    return root}
  buildMarket(){const root=new THREE.Group();this.scene.add(root);this.platform(root);
    for(let x=-6;x<=6;x++)for(let z=-4;z<=4;z++){this.box(root,.98,.025,.98,(x+z)%3?'#b4aa92':'#a99f88',x,.025,z)}
    for(const side of [-1,1]){const x=side*4.65,g=new THREE.Group();root.add(g);g.position.set(x,0,-1.65);
      this.box(g,3.3,.16,2.45,'#795b42',0,.87,0);for(const xx of [-1.4,1.4])for(const zz of [-.98,.98])this.box(g,.12,.85,.12,'#62513e',xx,.43,zz);
      for(const xx of [-1.5,1.5])this.rod(g,[xx,.92,-1.2],[xx,3.65,-1.2],.055,'#7b6955');
      const canopy=this.box(g,3.6,.12,2.7,side===1?'#a98062':'#799074',0,3.6,-.1);canopy.rotation.z=side*.04;
      for(let i=0;i<3;i++)this.box(g,.12,.05,2.64,side===1?'#c5a080':'#a0aa86',-1.2+i*1.2,3.68,-.1);
      for(let j=0;j<3;j++){const bx=-1.08+j*1.07;this.box(g,.9,.24,.8,'#987451',bx,1.1,.05);for(let k=0;k<5;k++){if(side===1){this.leaves(g,bx+(k%3)*.18-.2,1.25,(k%2)*.24-.12,4)}else this.ball(g,.19,k%2?'#b06d4c':'#d39a63',bx+(k%3)*.24-.23,1.26,(k%2)*.24-.13,1,.85,1)}}
    }
    this.marketBundle=new THREE.Group();root.add(this.marketBundle);this.marketBundle.position.set(2.15,.91,1.05);this.box(this.marketBundle,.82,.24,.48,'#8b6849');for(let k=0;k<6;k++)this.leaves(this.marketBundle,-.28+(k%3)*.25,.12,(k%2)*.14-.08,3);
    this.box(root,2.8,.42,1.25,'#8f8066',-5.05,.23,3.43);this.tree(root,-5.55,-3.56,.75);
    return root}
  cup(parent,x,y,z){const g=new THREE.Group();parent.add(g);g.position.set(x,y,z);this.cyl(g,.105,.19,'#d9c7a5',0,.1,0);this.cyl(g,.08,.014,'#7c5b45',0,.201,0);this.rod(g,[.08,.14,0],[.19,.14,0],.024,'#d9c7a5');return g}
  buildHome(){const root=new THREE.Group();this.scene.add(root);this.platform(root,13,9);
    for(let x=-6;x<=6;x++)this.box(root,.02,.015,8.8,'#977f62',x,.03,0);
    this.box(root,13,4.9,.25,'#b6aa91',0,2.38,-4.35);this.box(root,13,.2,.4,'#8c7963',0,4.75,-4.19);
    this.box(root,2.65,2.55,.09,'#5e675d',-4.05,2.8,-4.2);this.box(root,2.34,2.23,.03,'#bac7b8',-4.05,2.8,-4.13);this.box(root,.08,2.3,.1,'#6e6254',-4.05,2.8,-4.06);this.box(root,2.39,.09,.1,'#6e6254',-4.05,2.8,-4.04);
    this.box(root,2.4,2.5,.85,'#76614c',4.8,1.23,-3.84);for(let i=0;i<3;i++)this.box(root,2.2,.035,.05,'#9b8165',4.8,.46+i*.7,-3.36);
    this.box(root,3,.16,1.75,'#8a6d50',1.8,.94,0);for(const x of [.52,3.08])for(const z of [-.7,.7])this.box(root,.13,.89,.13,'#6e523e',x,.44,z);
    this.homeCupA=this.cup(root,1.35,1.03,-.27);this.homeCupB=this.cup(root,2.15,1.03,-.27);
    this.box(root,.48,.03,.76,'#3f4a45',2.72,1.04,.18);this.box(root,.32,.006,.56,'#263532',2.72,1.061,.18);
    // Keep the storage unit against the back wall, clear of the chair's left arm.
    this.box(root,2.35,.62,1.05,'#747865',-4.35,.3,-2.9);this.box(root,1.05,1,.32,'#9d876c',-5.48,1.0,-2.55);
    this.cyl(root,.17,1.8,'#6b6452',-1.4,.9,-3.1);this.ball(root,.44,'#d7c697',-1.4,1.92,-3.1,1.2,.55,1.2);
    return root}
  buildChair(){const g=new THREE.Group();g.userData={};
    this.box(g,1.45,.32,1.55,'#596c59',0,.67,0);this.box(g,1.2,.22,1.08,'#d6c8ae',0,1.03,.16);
    this.box(g,1.27,1.46,.25,'#6d806b',0,1.78,-.56);this.box(g,1.16,1.14,.15,'#d6cab3',0,1.67,-.37);this.box(g,1.08,.35,.27,'#d8c9b1',0,2.38,-.48);
    for(const side of [-1,1]){this.box(g,.22,1.14,1.42,'#70816c',side*.7,1.11,-.02);this.box(g,.26,.14,1.14,'#815f45',side*.69,1.61,.19);
      this.box(g,.13,.55,.15,'#3d4441',side*.53,1.48,-.75);this.box(g,.35,.1,.13,'#8d6d4c',side*.53,1.77,-.75);
      const wheel=this.cyl(g,.57,.14,'#242b29',side*.93,.61,-.27,18);wheel.rotation.z=Math.PI/2;
      const disc=this.cyl(g,.47,.15,'#77816b',side*1.03,.61,-.27,12);disc.rotation.z=Math.PI/2;this.ball(g,.085,'#bc9d6d',side*1.13,.61,-.27,.25,1,1);
      const caster=this.cyl(g,.19,.11,'#292c28',side*.55,.21,.87,14);caster.rotation.z=Math.PI/2;
      this.rod(g,[side*.72,1.42,.17],[side*1.01,1.29,.48],.105,'#556b58');this.ball(g,.11,'#343c3a',side*1.01,1.29,.48);
      const arm=new THREE.Group();g.add(arm);arm.position.set(side*1.01,1.29,.48);this.rod(arm,[0,0,0],[side*.2,-.36,.32],.086,'#60715c');this.ball(arm,.085,'#353c38',side*.2,-.36,.32);this.rod(arm,[side*.2,-.36,.32],[side*.23,-.15,.64],.07,'#657965');this.box(arm,.2,.09,.19,'#3b423d',side*.23,-.15,.69);for(let k=-1;k<=1;k++)this.rod(arm,[side*.23+k*.06,-.15,.75],[side*.23+k*.06,-.12,.9],.02,'#242a29');if(side===-1)g.userData.hand=arm;
    }
    this.box(g,1.1,.08,.48,'#3c413b',0,.3,1.08);this.box(g,.58,.38,.1,'#697a65',0,.63,-.87);
    this.assistLight=this.ball(g,.075,this.emissive('#d7a46c',.1),.78,.89,-.76);this.assistLight.visible=false;
    this.cup(g,-.72,1.72,.35);this.cup(g,.72,1.72,.35);
    // A seated pose: the pelvis rests just above the cushion, both thighs extend
    // forward, and the lower legs drop to shoes supported by the footplate.
    const q=new THREE.Group();g.add(q);g.userData.q=q;g.userData.qArms=[];g.userData.qShoes=[];
    this.box(q,.79,.61,.43,'#954c3e',0,1.59,-.08);
    this.box(q,.69,.16,.48,'#904e40',0,1.25,.08);
    this.box(q,.47,.17,.42,'#eee0c6',0,1.99,-.06);
    const qHead=new THREE.Group();q.add(qHead);qHead.position.set(0,2.2,0);g.userData.qHead=qHead;
    this.ball(qHead,.34,'#c99b7d',0,.05,-.04,1,.93,.9);
    this.ball(qHead,.35,'#aaa9a1',0,.18,-.13,1,.65,1);
    for(let side of [-1,1]){
      this.ball(qHead,.037,'#3e332e',side*.13,.06,.25);
      this.ball(qHead,.06,'#abaaa5',side*.29,.11,-.11,.5,1,.75);
      const qArm=new THREE.Group();q.add(qArm);qArm.position.set(side*.43,1.82,-.07);this.rod(qArm,[0,0,0],[side*.07,-.15,.39],.105,'#9a5142');this.ball(qArm,.09,'#c99b7d',side*.07,-.13,.46);g.userData.qArms.push(qArm);
      this.rod(q,[side*.22,1.27,.08],[side*.23,1.27,.70],.14,'#444546');
      this.ball(q,.14,'#444546',side*.23,1.23,.70);
      this.rod(q,[side*.23,1.2,.76],[side*.23,.52,.83],.135,'#444546');
      g.userData.qShoes.push(this.box(q,.32,.13,.48,'#603b36',side*.23,.42,1.01));
    }
    return g}
  buildXu(){const g=new THREE.Group();g.userData={arms:[],legs:[]};this.box(g,.77,.96,.42,'#a87e53',0,1.42,0);this.box(g,.49,.22,.43,'#53636a',0,1.77,.03);
    const head=new THREE.Group();g.add(head);head.position.set(0,2.2,0);g.userData.head=head;this.ball(head,.28,'#ca9e7c',0,0,.03,1,1,.9);this.ball(head,.28,'#a7a59e',0,.15,-.04,1,.68,1);this.ball(head,.18,'#aaa8a0',0,.08,-.28,1,1,.8);
    for(const side of [-1,1]){this.ball(head,.03,'#382f2b',side*.12,0,.289);const lens=this.mesh(new THREE.TorusGeometry(.145,.018,6,16),'#714d3c',head,side*.14,.02,.3);lens.scale.set(.85,.6,1);
      const arm=new THREE.Group();g.add(arm);arm.position.set(side*.43,1.81,.02);this.rod(arm,[0,0,0],[side*.11,-.64,.27],.11,'#ab8155');this.ball(arm,.085,'#c99b78',side*.11,-.66,.28);g.userData.arms.push(arm);if(side===1)g.userData.arm=arm;
      const leg=new THREE.Group();g.add(leg);leg.position.set(side*.2,.95,0);this.rod(leg,[0,0,0],[side*.04,-.76,.08],.16,'#3c4750');this.box(leg,.34,.13,.48,'#ddd3bd',side*.04,-.86,.21);g.userData.legs.push(leg);
    }
    this.box(g,.47,.12,.18,'#9e5848',0,1.86,.21);this.box(g,.4,.36,.16,'#817258',-.48,1.15,-.11);
    return g}
  buildInteractionProps(){this.marketBag=new THREE.Group();this.stageRoots[1].add(this.marketBag);this.marketBag.position.set(2.3,.29,2.9);this.box(this.marketBag,.65,.52,.27,'#aa9778');this.rod(this.marketBag,[-.21,.22,0],[-.21,.53,0],.025,'#806c51');this.rod(this.marketBag,[.21,.22,0],[.21,.53,0],.025,'#806c51');this.rod(this.marketBag,[-.21,.53,0],[.21,.53,0],.025,'#806c51');for(const x of [-.2,0,.2])this.ball(this.marketBag,.12,'#719168',x,.3,0,.7,1.2,.7);
    this.carriedBag=this.marketBag.clone();this.chair.userData.hand.add(this.carriedBag);this.carriedBag.position.set(-.44,-.6,.86);this.carriedBag.visible=false;
    this.lapBag=this.marketBag.clone();this.chair.add(this.lapBag);this.lapBag.position.set(0,1.5,.83);this.lapBag.visible=false;
    // The invitation is made on her own phone, resting above her thighs.
    this.homePhone=new THREE.Group();this.chair.add(this.homePhone);this.homePhone.position.set(0,1.46,.43);
    this.box(this.homePhone,.38,.026,.55,'#39433f');this.phoneScreen=this.box(this.homePhone,.32,.004,.48,this.emissive('#aebdb0',.24),0,.017,0);this.homePhone.visible=false}
  rampSurface(z){return z< -2.8?.04:.23+Math.tan(.055)*Math.min(z,2.8)}
  alignToRamp(){this.chair.position.y=this.rampSurface(this.chair.position.z)-.04;this.chair.rotation.x=-.055;if(this.chapter===4||this.chapter===5)this.xu.position.y=this.rampSurface(this.xu.position.z)-.025}
  setScene(index,history={}){this.chapter=index;this.action=null;this.time=0;const stage=[0,1,2,1,0,0][index];this.stageRoots.forEach((root,i)=>root.visible=i===stage);
    const positions=[[0,0,-2.45],[0,0,1.4],[-2.55,0,1.9],[0,0,1.4],[0,0,-2.15],[0,0,-2.15]];
    this.chair.position.set(...positions[index]);this.chair.rotation.set(0,index===2?-.22:0,0);
    this.xu.visible=index!==1&&index!==2;this.xu.position.set(index===0?2.7:index===3?2.45:0,0,index===0?0:index===3?1.45:-3.55);this.xu.rotation.y=index===0?-.18:0;
    if(stage===0)this.alignToRamp();
    this.chair.userData.hand.rotation.x=0;this.chair.userData.q.rotation.y=0;this.chair.userData.qHead.rotation.set(0,0,0);this.chair.userData.qArms.forEach(arm=>arm.rotation.set(0,0,0));this.chair.userData.qShoes.forEach(shoe=>shoe.rotation.set(0,0,0));this.xu.userData.head.rotation.set(0,0,0);this.xu.userData.legs.forEach(leg=>leg.rotation.set(0,0,0));this.xu.userData.arms.forEach(arm=>arm.rotation.set(index>=4?-1.1:0,0,0));this.assistLight.visible=false;this.assistLight.material.emissiveIntensity=.1;
    this.homeCupB.visible=true;this.homePhone.visible=index===2;this.phoneScreen.material.emissiveIntensity=.24;this.marketBundle.position.set(2.15,.91,1.05);this.marketBag.position.set(2.3,.29,2.9);this.marketBag.visible=false;this.carriedBag.visible=index===3&&Boolean(history.gift);this.lapBag.visible=false;if(this.carriedBag.visible)this.chair.userData.hand.rotation.x=-.28;
    this.focus.set(0,1.35,index===2?-.7:index>=4?-.75:0);this.orbit={theta:index===2?.38:index>=4?-1.25:.43,phi:1.19,r:index===2?15.7:index>=4?13.8:14.8};this.view=0;this.applyCamera();this.render()}
  play(id,done){this.action={id,elapsed:0,duration:2.65,done};this.applyAction(id,0)}
  skip(){if(!this.action)return;const a=this.action;this.applyAction(a.id,1);this.action=null;a.done?.()}
  smooth(t){return t*t*(3-2*t)}
  setBagMode(mode){this.marketBag.visible=mode==='ground';this.carriedBag.visible=mode==='carried';this.lapBag.visible=mode==='lap';if(mode==='carried')this.chair.userData.hand.rotation.x=Math.min(this.chair.userData.hand.rotation.x,-.28)}
  applyAction(id,raw){const t=this.smooth(Math.max(0,Math.min(1,raw)));const c=this.chair,x=this.xu;
    if(id==='road_auto'){c.position.z=-2.45+t*3.65;c.userData.hand.rotation.x=-.8*t}
    if(id==='road_wait'){c.position.z=-2.45+t*.35;x.position.x=2.7-t*.8;c.userData.hand.rotation.x=-.35*t}
    // Produce stays on the stall; the arm gestures toward it. No object travels
    // through the wheelchair or the customer during a purchase.
    if(id==='market_auto'){c.userData.hand.rotation.x=-.08*t;if(t>.68)this.setBagMode('carried')}
    if(id==='market_pause'){c.userData.q.rotation.y=-.18*t;c.userData.hand.rotation.x=-.15*t;if(t>.75)this.setBagMode('ground')}
    if(id==='market_refuse'){c.userData.q.rotation.y=-.24*t;c.userData.hand.rotation.x=.18*t;if(t>.75)this.setBagMode('ground')}
    if(id==='invite_lie'){c.userData.hand.rotation.x=-1.25*t;this.phoneScreen.material.emissiveIntensity=.24+.55*t}
    if(id==='invite_honest'){c.userData.hand.rotation.x=.38*t;this.phoneScreen.material.emissiveIntensity=.24+.25*t}
    if(id==='invite_decline'){c.userData.hand.rotation.x=.58*t;this.phoneScreen.material.emissiveIntensity=.24}
    if(id==='meet_cover'||id==='meet_truth'||id==='meet_space'){x.position.x=2.45-t*.4;c.userData.q.rotation.y=id==='meet_cover'?-.1*t:.12*t;c.userData.hand.rotation.x=id==='meet_cover'?-.35*t:.15*t}
    if(id==='slope_auto'){c.position.z=-2.15+t*3.2;x.position.z=-3.55+t*.35;this.assistLight.visible=true;this.assistLight.material.emissiveIntensity=1.2;x.userData.arms.forEach(arm=>arm.rotation.x=-1.1+1.1*t)}
    if(id==='slope_hidden'||id==='slope_tell'){c.position.z=-2.15+t*3.2;x.position.z=c.position.z-1.4;this.assistLight.visible=id==='slope_tell'?t>.58:t>.12;this.assistLight.material.emissiveIntensity=id==='slope_hidden'?.85:1.25;x.userData.arms.forEach(arm=>arm.rotation.x=-1.1)}
    if(id==='tomorrow_update'){c.position.z=-2.15+t*2.7;x.position.z=c.position.z-1.4;this.assistLight.visible=t>.62;this.assistLight.material.emissiveIntensity=.75;x.userData.arms.forEach(arm=>arm.rotation.x=-1.1)}
    if(id==='tomorrow_keep'){c.position.z=-2.15+t*3.2;x.position.z=-3.55+t*.35;this.assistLight.visible=true;this.assistLight.material.emissiveIntensity=1.2;x.userData.arms.forEach(arm=>arm.rotation.x=-1.1+1.1*t)}
    if(id==='road_reopen'||id==='road_ask'){c.userData.q.rotation.y=-.2*t;c.userData.hand.rotation.x=-.2*t;x.userData.arms[1].rotation.x=-.25*t}
    if(id==='road_speak'){c.userData.hand.rotation.x=-.95*t;c.userData.q.rotation.y=.1*t}
    if(id==='road_record'){c.userData.hand.rotation.x=.45*t}
    if(id==='market_exchange'||id==='market_carry_ask'||id==='market_refuse_ask'){c.userData.q.rotation.y=-.22*t;c.userData.hand.rotation.x=-.08*t;if(t>.5)this.setBagMode('carried')}
    if(id==='market_defend'||id==='market_carry_take'){c.userData.hand.rotation.x=-.08*t;if(t>.5)this.setBagMode('carried')}
    if(id==='market_refuse_all'){c.userData.hand.rotation.x=.5*t;if(t>.5)this.setBagMode('lap')}
    if(id==='invite_correct'||id==='invite_private'||id==='invite_prompt'){c.userData.hand.rotation.x=.35*t;this.phoneScreen.material.emissiveIntensity=.24+.22*t}
    if(id==='invite_conceal'||id==='invite_status'){c.userData.hand.rotation.x=-1.1*t;this.phoneScreen.material.emissiveIntensity=.24+.55*t}
    if(id==='invite_silent'){c.userData.hand.rotation.x=.55*t;this.phoneScreen.material.emissiveIntensity=.24}
    if(id==='meet_repair'||id==='meet_time'||id==='meet_confirm'){c.userData.q.rotation.y=.15*t;x.userData.arms[1].rotation.x=-.32*t}
    if(id==='meet_task'||id==='meet_assume'||id==='meet_record'){c.userData.hand.rotation.x=-.75*t;x.userData.arms[1].rotation.x=.15*t}
    if(id==='slope_stop'||id==='slope_limit'||id==='tomorrow_repair'){this.assistLight.visible=false;c.userData.hand.rotation.x=.25*t}
    if(id==='slope_continue'||id==='slope_hide'||id==='slope_force'||id==='tomorrow_repeat'){this.assistLight.visible=true;this.assistLight.material.emissiveIntensity=1.1;c.userData.hand.rotation.x=-.3*t}
    if(id==='slope_disclose'){this.assistLight.visible=true;this.assistLight.material.emissiveIntensity=.8;x.userData.arms[1].rotation.x=-.5*t}
    if(id==='tomorrow_wait'){this.assistLight.visible=t>.58;this.assistLight.material.emissiveIntensity=.75;x.userData.arms.forEach(arm=>arm.rotation.x=-1.1)}
    if(id==='tomorrow_timeout'){this.assistLight.visible=t>.15;this.assistLight.material.emissiveIntensity=1.1}
    if(this.chapter===3&&this.carriedBag.visible)c.userData.hand.rotation.x=Math.min(c.userData.hand.rotation.x,-.28);
    if(this.chapter===0||this.chapter===4||this.chapter===5)this.alignToRamp();
  }
  applyFeedback(kind){if(kind==='tell'||kind==='limit'){this.assistLight.visible=kind==='tell';this.assistLight.material.emissiveIntensity=kind==='tell'?.5:0}
    if(kind==='ask')this.chair.userData.hand.rotation.x=.2}
  audit(){const c=this.chair.position,x=this.xu.position,road=this.chapter===0||this.chapter===4||this.chapter===5;
    return{road,chairInLane:!road||Math.abs(c.x)<1.2&&c.z>=-2.5&&c.z<=1.3,wheelsOnGrade:!road||Math.abs(c.y+.04-this.rampSurface(c.z))<.002&&Math.abs(this.chair.rotation.x+.055)<.002,pusherBehind:!this.xu.visible||this.chapter!==4&&this.chapter!==5||x.z<c.z-1.05&&Math.abs(x.x-c.x)<.25,pusherOnGrade:this.chapter!==4&&this.chapter!==5||Math.abs(x.y+.025-this.rampSurface(x.z))<.002,sideClearance:!road||Math.abs(c.x)+1.2<3.25,roadFriendClearance:this.chapter!==0||Math.abs(x.x)<2.75,marketClearance:this.chapter!==1&&this.chapter!==3||Math.abs(c.x)<1.2&&Math.abs(x.x-c.x)>1.55||this.chapter===1}}
  setView(v){this.view=v;const side=this.chapter>=4;const views=[{theta:side?-1.25:.43,phi:1.19,r:side?13.8:14.8},{theta:side?-.1:.04,phi:1.38,r:14.2},{theta:side?-.65:.15,phi:.46,r:18.5}];this.orbit={...views[v]};this.applyCamera();this.render()}
  applyCamera(){const o=this.orbit,aspect=Math.max(.55,this.canvas.clientWidth/Math.max(1,this.canvas.clientHeight));const r=o.r*(this.canvas.clientWidth<570?.78:Math.max(1,1.35/aspect));this.camera.position.set(this.focus.x+r*Math.sin(o.phi)*Math.sin(o.theta),this.focus.y+r*Math.cos(o.phi),this.focus.z+r*Math.sin(o.phi)*Math.cos(o.theta));this.camera.lookAt(this.focus)}
  setupPointer(){let drag=null;this.canvas.addEventListener('pointerdown',e=>{drag={x:e.clientX,y:e.clientY};this.canvas.setPointerCapture(e.pointerId)});
    this.canvas.addEventListener('pointermove',e=>{if(!drag)return;this.orbit.theta-=(e.clientX-drag.x)*.006;this.orbit.phi=Math.max(.24,Math.min(1.5,this.orbit.phi+(e.clientY-drag.y)*.006));drag={x:e.clientX,y:e.clientY};this.applyCamera()});
    this.canvas.addEventListener('pointerup',()=>drag=null);this.canvas.addEventListener('pointercancel',()=>drag=null);
    this.canvas.addEventListener('wheel',e=>{e.preventDefault();this.orbit.r=Math.max(12,Math.min(32,this.orbit.r+e.deltaY*.015));this.applyCamera()},{passive:false});
    this.canvas.addEventListener('keydown',e=>{const m={ArrowLeft:[-.1,0],ArrowRight:[.1,0],ArrowUp:[0,-.08],ArrowDown:[0,.08]};if(!m[e.key])return;e.preventDefault();this.orbit.theta+=m[e.key][0];this.orbit.phi=Math.max(.24,Math.min(1.5,this.orbit.phi+m[e.key][1]));this.applyCamera()})}
  resize(){const w=this.canvas.clientWidth,h=this.canvas.clientHeight;if(!w||!h)return;this.renderer.setSize(w,h,false);this.camera.aspect=w/h;this.camera.updateProjectionMatrix();this.applyCamera();this.render()}
  animateIdle(){const t=this.time,ch=this.chapter,q=this.chair.userData,x=this.xu.userData;
    q.qHead.rotation.y=[.11,-.16,.09,-.07,.08,.06][ch]+.075*Math.sin(t*.82+ch*.75);q.qHead.rotation.x=.025*Math.sin(t*1.2+ch);q.qHead.rotation.z=.018*Math.sin(t*.93+ch*.6);
    q.qArms.forEach((arm,i)=>{arm.rotation.z=(i?-.028:.028)*Math.sin(t*1.15+ch+i)});q.qShoes.forEach((shoe,i)=>{shoe.rotation.y=.025*Math.sin(t*.94+ch+i*2)});
    if(this.xu.visible){x.head.rotation.y=[-.12,0,0,-.17,.06,.04][ch]+.08*Math.sin(t*.67+ch*.55);x.head.rotation.z=.022*Math.sin(t*.91+ch);const walking=Boolean(this.action&&/^(road_wait|meet_|slope_|tomorrow_)/.test(this.action.id));const stride=walking?.16:.024;const speed=walking?7.5:1.35;x.legs.forEach((leg,i)=>leg.rotation.x=stride*Math.sin(t*speed+i*Math.PI+ch*.7));x.arms.forEach((arm,i)=>{arm.rotation.z=.025*Math.sin(t*.95+i*Math.PI+ch)})}
  }
  tick(dt){this.time+=dt;if(this.action){const a=this.action;a.elapsed+=dt;const t=Math.min(1,a.elapsed/a.duration);this.applyAction(a.id,t);if(t>=1){this.action=null;a.done?.()}}
    this.animateIdle();
    if(this.assistLight.visible&&this.action)this.assistLight.material.emissiveIntensity*=.996;
    this.render()}
  render(){this.renderer.render(this.scene,this.camera)}
  snapshot(){return{chapter:this.chapter,action:this.action?.id||null,chair:this.chair.position.toArray(),xu:this.xu.position.toArray(),assist:this.assistLight.visible,camera:this.camera.position.toArray()}}
}
