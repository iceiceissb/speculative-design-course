/* Original mesh characters. Extends the previous prototype's seated human model. */
class HospitalMeshes {
 constructor(){this.materials={};this.geometries={};this.blinkers=[];this.surfaceMap=new THREE.TextureLoader().load(window.HOSPITAL_TEXTURE);this.surfaceMap.wrapS=this.surfaceMap.wrapT=THREE.RepeatWrapping;this.surfaceMap.repeat.set(.7,.7);}
 mat(color,metal=false){let k=color+metal;if(!this.materials[k])this.materials[k]=new THREE.MeshStandardMaterial({color:new THREE.Color(color).convertSRGBToLinear(),roughness:metal?.34:.68,metalness:metal?.64:.06,map:this.surfaceMap,bumpMap:this.surfaceMap,bumpScale:metal?.008:.022});return this.materials[k];}
 glow(color,intensity=1){return new THREE.MeshStandardMaterial({color,emissive:color,emissiveIntensity:intensity,roughness:.35});}
 mesh(geo,color,parent,pos=[0,0,0]){let m=new THREE.Mesh(geo,typeof color==='string'?this.mat(color):color);m.position.set(...pos);m.castShadow=true;m.receiveShadow=true;parent.add(m);return m;}
 box(w,h,d,color,parent,pos=[0,0,0],r=.055){r=Math.min(r,w/3,h/3,d/3);const key=[w,h,d,r].join(',');let geo=this.geometries[key];if(!geo){w-=2*r;h-=2*r;const x=-w/2,y=-h/2;const shape=new THREE.Shape();shape.moveTo(x+r,y);shape.lineTo(x+w-r,y);shape.quadraticCurveTo(x+w,y,x+w,y+r);shape.lineTo(x+w,y+h-r);shape.quadraticCurveTo(x+w,y+h,x+w-r,y+h);shape.lineTo(x+r,y+h);shape.quadraticCurveTo(x,y+h,x,y+h-r);shape.lineTo(x,y+r);shape.quadraticCurveTo(x,y,x+r,y);geo=new THREE.ExtrudeGeometry(shape,{depth:d-2*r,bevelEnabled:true,bevelSegments:2,steps:1,bevelSize:r,bevelThickness:r,curveSegments:3});geo.translate(0,0,-d/2+r);this.geometries[key]=geo;}return this.mesh(geo,color,parent,pos);}
 ball(r,color,parent,pos=[0,0,0],scale=[1,1,1]){let m=this.mesh(new THREE.SphereGeometry(r,20,12),color,parent,pos);m.scale.set(...scale);return m;}
 rod(a,b,r,color,parent){let v1=new THREE.Vector3(...a),v2=new THREE.Vector3(...b),dir=v2.clone().sub(v1);let m=this.mesh(new THREE.CylinderGeometry(r,r,dir.length(),10),color,parent,v1.clone().add(v2).multiplyScalar(.5).toArray());m.quaternion.setFromUnitVectors(new THREE.Vector3(0,1,0),dir.normalize());return m;}
 sign(text,w,h,parent,pos,bg='#132b31',fg='#b9e8d9',font=55){const c=document.createElement('canvas');c.width=1024;c.height=256;const ct=c.getContext('2d');ct.fillStyle=bg;ct.fillRect(0,0,1024,256);ct.fillStyle=fg;ct.font=`600 ${font}px 'Microsoft YaHei',sans-serif`;ct.textAlign='center';ct.textBaseline='middle';ct.fillText(text,512,132,980);const map=new THREE.CanvasTexture(c);map.encoding=THREE.sRGBEncoding;const mat=new THREE.MeshBasicMaterial({map});const p=this.mesh(new THREE.PlaneGeometry(w,h),mat,parent,pos);p.castShadow=false;return p;}
 visor(parent,x,y,z,w=.38,h=.19,color='#89f9dc'){this.box(w,h,.085,'#102731',parent,[x,y,z],.06);const eyes=[];for(const s of [-1,1])eyes.push(this.ball(h*.19,this.glow(color,1.8),parent,[x+s*w*.21,y,z+.05],[.72,1.3,.32]));this.blinkers.push(eyes);return eyes;}
 wheelchair(){const g=this.chair('#2c7773',true);g.scale.setScalar(1.5);g.userData.kind='wheelchair';
  for(const s of [-1,1]){this.box(.14,.42,.65,'#d3ccb7',g,[s*.33,.56,-.1],.09);const ring=this.mesh(new THREE.TorusGeometry(.229,.017,8,40),this.glow('#ffa332',2),g,[s*.455,.315,-.18]);ring.rotation.y=Math.PI/2;this.box(.28,.075,.08,this.glow('#67efd2',1),g,[s*.15,.19,.69]);}
  this.rod([-.31,1.18,-.36],[-.37,1.72,-.38],.025,this.mat('#6a7270',true),g);this.rod([-.37,1.72,-.38],[-.28,1.8,-.27],.022,'#495958',g);
  const head=new THREE.Group();g.add(head);head.position.set(-.28,1.85,-.24);this.box(.52,.31,.32,'#dbd5bd',head,[0,0,0],.1);this.visor(head,0,0,.18,.39,.23);for(const s of [-1,1]){const ear=this.mesh(new THREE.CylinderGeometry(.105,.105,.075,20),this.mat('#434f4b',true),head,[s*.29,0,0]);ear.rotation.z=Math.PI/2;}
  g.userData.head=head;return g;
 }
 concierge(){const g=new THREE.Group(),metal=this.mat('#323f46',true),orange='#d8853c';g.userData.kind='concierge';
  this.box(.67,.92,.39,orange,g,[0,1.6,0],.12);this.box(.51,.64,.045,'#d9c9a5',g,[0,1.61,.228],.025);this.box(.22,.066,.026,'#304d52',g,[0,1.73,.263]);this.box(.07,.23,.03,'#304d52',g,[0,1.73,.265]);
  this.rod([0,2.02,0],[0,2.35,0],.07,metal,g);const head=new THREE.Group();g.add(head);head.position.y=2.52;this.box(.52,.59,.41,orange,head,[0,0,0],.13);this.visor(head,0,-.02,.22,.37,.3);g.userData.head=head;
  g.userData.arms=[];g.userData.legs=[];for(const s of [-1,1]){const leg=new THREE.Group();leg.position.set(s*.23,1.17,0);g.add(leg);g.userData.legs.push(leg);this.ball(.12,metal,leg);this.rod([0,0,0],[s*.05,-.45,0],.088,orange,leg);this.ball(.11,metal,leg,[s*.05,-.47,0]);this.rod([s*.05,-.5,0],[s*.03,-1.04,.02],.07,orange,leg);this.box(.25,.13,.43,orange,leg,[s*.03,-1.05,.1]);
   const arm=new THREE.Group();arm.position.set(s*.44,1.95,0);g.add(arm);g.userData.arms.push(arm);this.ball(.14,metal,arm);this.rod([0,0,0],[s*.13,-.51,0],.084,orange,arm);this.ball(.1,metal,arm,[s*.13,-.53,0]);this.rod([s*.13,-.54,0],[s*.13,-.84,.23],.055,orange,arm);this.box(.16,.12,.23,orange,arm,[s*.13,-.88,.27]);for(let i=0;i<3;i++)this.rod([s*.13-.06+i*.06,-.9,.29],[s*.13-.06+i*.06,-.92,.43],.017,metal,arm);
  }return g;
 }
 cleaner(){const g=new THREE.Group();g.userData.kind='cleaner';this.mesh(new THREE.CylinderGeometry(.48,.5,.23,32),'#c9a63e',g,[0,.23,0]);this.mesh(new THREE.CylinderGeometry(.43,.45,.08,32),'#1c343b',g,[0,.11,0]);this.visor(g,0,.25,.43,.37,.12,'#d4ffff');this.mesh(new THREE.CylinderGeometry(.16,.16,.05,24),'#3c4c47',g,[0,.37,0]);for(let i=0;i<12;i++){const a=i*Math.PI/6;this.rod([Math.cos(a)*.43,.1,Math.sin(a)*.43],[Math.cos(a)*.59,.08,Math.sin(a)*.59],.015,'#2b3c42',g);}return g;}
 plant(x,z,scale=1,parent=this.scene){const g=new THREE.Group();parent.add(g);g.position.set(x,0,z);g.scale.setScalar(scale);this.box(.9,.65,.85,'#a6aa9c',g,[0,.32,0],.07);this.box(.72,.03,.66,'#293b36',g,[0,.66,0]);for(let i=0;i<8;i++){let a=i*2.4,y=1.2+(i%3)*.22;this.rod([0,.65,0],[Math.cos(a)*.35,y,Math.sin(a)*.35],.019,'#41604d',g);let leaf=this.ball(.23,i%2?'#587655':'#396b57',g,[Math.cos(a)*.34,y,Math.sin(a)*.34],[.55,1.9,.8]);leaf.rotation.z=.6*Math.cos(a);}return g;}
  person(color,seated=false,index=0){const g=new THREE.Group(),skin=index%2?'#c79e80':'#d0ab90',hair=seated?'#c6c7bc':index===4?'#423e38':'#45423b',base=seated?.72:.94;
    this.ball(.255,color,g,[0,base+.24,0],[1.02,1.2,.66]);this.box(.38,.27,.28,color,g,[0,base+.08,0]);
    this.rod([0,base+.4,0],[0,base+.52,0],.068,skin,g);
    this.ball(.174,skin,g,[0,base+.66,.02],[.83,1.15,.9]);
    this.ball(.174,hair,g,[0,base+.73,-.025],[.91,.92,.94]);
    if(seated)for(let i=0;i<9;i++){let a=i*.7;this.ball(.051,hair,g,[Math.cos(a)*.13,base+.78+Math.sin(i*2)*.02,-.035+Math.sin(a)*.12],[1,1,.9]);}
    this.ball(.033,skin,g,[0,base+.65,.173],[.65,1,1]);
    [-1,1].forEach(side=>{this.ball(.012,'#353632',g,[side*.064,base+.69,.163]);this.ball(.036,skin,g,[side*.152,base+.66,.01],[.4,1,.65]);});
    this.rod([-.035,base+.592,.166],[.035,base+.592,.166],.006,'#96705b',g);
    const collar=this.box(.11,.25,.014,'#e6dfcf',g,[0,base+.31,.161]);
    for(let y=.13;y<.4;y+=.09)this.ball(.009,'#c7c0ad',g,[.052,base+y,.169]);
    if(index===1&&seated){for(const x of [-.065,.065]){const ring=this.mesh(new THREE.TorusGeometry(.051,.006,6,20),'#626458',g,[x,base+.69,.168]);}this.rod([-.013,base+.695,.177],[.013,base+.695,.177],.006,'#626458',g);}
    g.userData.legs=[];g.userData.arms=[];
    for(const side of [-1,1]){const leg=new THREE.Group();leg.position.set(side*.12,base-.08,0);g.add(leg);g.userData.legs.push(leg);const pants=seated?'#535b55':index%2?'#b2ad9d':'#64716c';
      if(seated){this.rod([0,0,0],[0,-.08,.34],.098,pants,leg);this.rod([0,-.08,.34],[0,-.49,.45],.073,pants,leg);this.box(.17,.1,.29,'#4a504b',leg,[0,-.52,.49]);}
      else{this.rod([0,0,0],[0,-.4,0],.089,pants,leg);this.rod([0,-.4,0],[0,-.8,.015],.07,pants,leg);this.box(.17,.115,.29,'#484e48',leg,[0,-.82,.075]);}
      const arm=new THREE.Group();arm.position.set(side*.215,base+.4,0);g.add(arm);g.userData.arms.push(arm);
      this.rod([0,0,0],[side*.073,-.28,seated?.1:0],.075,color,arm);this.rod([side*.073,-.28,seated?.1:0],[side*.078,seated?-.35:-.55,seated?.34:.015],.058,color,arm);this.ball(.062,skin,arm,[side*.078,seated?-.35:-.57,seated?.34:.04],[.8,1,1.1]);
    }
    if(index===2&&!seated){this.box(.32,.39,.13,'#374c4c',g,[0,1.22,-.22]);for(let side of [-1,1])this.rod([side*.13,1.59,.01],[side*.17,1.01,.07],.02,'#314844',g);}
    if(index===4){this.box(.065,.1,.015,'#eff0e7',g,[.1,1.25,.167]);let clipboard=this.box(.22,.3,.025,'#d6dfd9',g,[-.3,.83,.11]);clipboard.rotation.z=.15;}
    g.userData.seated=seated;return g;
  }
  chair(color,isLin){const g=new THREE.Group(),metal=this.mat('#909f99',true);g.userData.wheels=[];
    this.box(.61,.22,.69,'#d8dcd0',g,[0,.34,-.06]);this.box(.5,.13,.67,'#354440',g,[0,.25,-.08]);
    this.box(.6,.12,.61,'#46514b',g,[0,.64,.01]);this.box(.59,.61,.12,'#3c514b',g,[0,.99,-.33]);
    this.box(.62,.16,.15,'#58655d',g,[0,1.33,-.34]);
    for(let side of [-1,1]){
      this.rod([side*.32,.38,-.32],[side*.32,1.24,-.32],.027,metal,g);
      this.rod([side*.33,.37,-.34],[side*.33,.38,.35],.026,metal,g);
      this.rod([side*.33,.48,.17],[side*.33,.91,.13],.024,metal,g);
      this.box(.15,.072,.59,'#3d4b44',g,[side*.35,.94,.03]);
      const wheel=new THREE.Group();wheel.position.set(side*.395,.315,-.18);g.add(wheel);g.userData.wheels.push(wheel);
      const tire=this.mesh(new THREE.TorusGeometry(.248,.069,16,40),'#303b34',wheel);tire.rotation.y=Math.PI/2;
      const disc=this.mesh(new THREE.CylinderGeometry(.188,.188,.085,30),metal,wheel);disc.rotation.z=Math.PI/2;
      const hub=this.mesh(new THREE.CylinderGeometry(.065,.065,.09,20),'#5a6a61',wheel);hub.rotation.z=Math.PI/2;
      for(let i=0;i<8;i++){let a=i*Math.PI/4;this.rod([0,0,0],[0,Math.sin(a)*.211,Math.cos(a)*.211],.012,'#66766b',wheel);}
      this.rod([side*.31,.37,.29],[side*.31,.12,.46],.027,metal,g);
      const cast=this.mesh(new THREE.CylinderGeometry(.112,.112,.064,20),'#354339',g,[side*.31,.12,.46]);cast.rotation.z=Math.PI/2;
      this.rod([side*.22,.6,.27],[side*.22,.13,.65],.025,metal,g);this.box(.21,.035,.29,'#4e5c50',g,[side*.17,.135,.64]);
      this.box(.027,.11,.29,color,g,[side*.32,.36,.13]);
    }
    const control=this.box(.17,.065,.25,'#293a32',g,[.36,.995,.32]);this.box(.098,.005,.065,'#9ebcb0',g,[.36,1.031,.29]);
    this.rod([.36,1.03,.39],[.36,1.1,.39],.017,'#2b392f',g);this.ball(.035,'#556459',g,[.36,1.1,.39]);
    this.box(.062,.012,.032,'#edba6c',g,[.41,1.032,.22]);
    this.box(.12,.1,.09,'#273d33',g,[0,.43,.31]);this.ball(.025,'#78a99a',g,[0,.44,.36],[1,1,.5]);
    const occupant=this.person(color,true,isLin?0:1);g.add(occupant);
    if(!isLin){const paper=this.box(.31,.014,.24,'#eee9da',g,[0,.778,.27]);paper.rotation.x=-.2;for(let i=0;i<4;i++)this.box(.2,.004,.006,'#c0b8a6',g,[0,.794,.23+i*.03]);}
    const bag=this.box(.4,.35,.08,isLin?'#c7b99c':'#9b947d',g,[0,.79,-.43]);
    g.userData.seated=true;return g;
  }
}
