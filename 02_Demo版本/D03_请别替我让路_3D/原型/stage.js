/* Original procedural scene. Three.js is distributed under the MIT license. */
class YieldStage {
 constructor(canvas){
  this.canvas=canvas;this.scene=new THREE.Scene();this.scene.background=new THREE.Color('#edece5');
  this.renderer=new THREE.WebGLRenderer({canvas,antialias:true,preserveDrawingBuffer:true});this.renderer.setPixelRatio(Math.min(devicePixelRatio,2));this.renderer.shadowMap.enabled=true;this.renderer.shadowMap.type=THREE.PCFSoftShadowMap;this.renderer.outputEncoding=THREE.sRGBEncoding;this.renderer.toneMapping=THREE.ACESFilmicToneMapping;this.renderer.toneMappingExposure=1;
  this.camera=new THREE.OrthographicCamera(-10,10,5,-5,.1,100);this.view='overview';this.paused=false;this.speed=1;this.clock=0;this.wheels=[];this.people=[];this.labels=[];
  this.scene.add(new THREE.HemisphereLight(0xffffff,0xb2b6a0,.9));let sun=new THREE.DirectionalLight(0xfff5e6,1.05);sun.position.set(-3,12,8);sun.castShadow=true;sun.shadow.mapSize.set(2048,2048);Object.assign(sun.shadow.camera,{left:-13,right:13,top:9,bottom:-9});sun.shadow.bias=-.0003;this.scene.add(sun);
  this.buildRoom();this.chair=this.buildChair();this.scene.add(this.chair);
  ['#355061','#ae7155','#b4995d'].forEach((c,i)=>{const p=this.person(c,false,i);this.people.push(p);this.scene.add(p)});
  this.actors=[this.chair,...this.people];this.reset();this.addLabel('林岚',()=>this.chair.position.clone().add(new THREE.Vector3(0,1.95,0)));this.addLabel('对向行人',()=>this.people[1].position.clone().add(new THREE.Vector3(0,2.05,0)));
  this.addLabel('轮椅一侧的错身空间',()=>new THREE.Vector3(-4.5,.1,2.6));this.addLabel('行人一侧的错身空间',()=>new THREE.Vector3(5.2,.1,-2.65));
  new ResizeObserver(()=>this.resize()).observe(canvas.parentElement);this.resize();let last=performance.now();const frame=t=>{const dt=Math.min((t-last)/1000,.06);last=t;this.tick(dt);requestAnimationFrame(frame)};requestAnimationFrame(frame);
 }
 mat(c,rough=.75){return new THREE.MeshStandardMaterial({color:new THREE.Color(c).convertSRGBToLinear(),roughness:rough,metalness:rough<.5?.45:0})}
 mesh(geo,c,parent,pos=[0,0,0]){let m=new THREE.Mesh(geo,typeof c==='string'?this.mat(c):c);m.position.set(...pos);m.castShadow=true;m.receiveShadow=true;parent.add(m);return m}
 box(w,h,d,c,p,pos){return this.mesh(new THREE.BoxGeometry(w,h,d),c,p,pos)}
 sphere(r,c,p,pos,scale){let m=this.mesh(new THREE.SphereGeometry(r,20,14),c,p,pos);if(scale)m.scale.set(...scale);return m}
 rod(a,b,r,c,p){let va=new THREE.Vector3(...a),vb=new THREE.Vector3(...b),v=vb.clone().sub(va);let m=this.mesh(new THREE.CylinderGeometry(r,r,v.length(),12),c,p,va.clone().add(vb).multiplyScalar(.5).toArray());m.quaternion.setFromUnitVectors(new THREE.Vector3(0,1,0),v.normalize());return m}
 labelTexture(text,bg='#e6e4da',ink='#496054'){let c=document.createElement('canvas');c.width=1024;c.height=256;let x=c.getContext('2d');x.fillStyle=bg;x.fillRect(0,0,1024,256);x.fillStyle=ink;x.textAlign='center';x.font='bold 68px Microsoft YaHei';x.fillText(text,512,154);return new THREE.CanvasTexture(c)}
 buildRoom(){const s=this.scene;this.box(19,.18,6.1,'#dddcd2',s,[0,-.17,0]);this.box(18,.06,1.36,'#f4f2e8',s,[0,-.045,0]);this.box(2.8,.065,1.95,'#d2e0d4',s,[-4.5,-.04,1.6]);this.box(3.9,.065,1.95,'#e5d8c3',s,[5.1,-.04,-1.6]);
  // Low cutaway walls expose the bodies and the two recesses.
  [[-7.45,3.1],[2.95,12.1]].forEach(([x,w])=>this.box(w,.28,.13,'#c5c9bc',s,[x,.14,.78]));
  [[-3.2,11.6],[8,2]].forEach(([x,w])=>this.box(w,.36,.13,'#d1cfc0',s,[x,.18,-.78]));
  this.box(2.8,.3,.14,'#bbc6b8',s,[-4.5,.15,2.65]);this.box(3.9,1.5,.16,'#d2d0c2',s,[5.1,.75,-2.65]);
  for(let x=-8;x<9;x++){this.box(.012,.003,1.35,'#dfded4',s,[x,.001,0]);}
  let sign=this.mesh(new THREE.PlaneGeometry(3.3,.72),new THREE.MeshBasicMaterial({map:this.labelTexture('社区活动中心')}),s,[5.1,1.02,-2.55]);
  this.box(2.4,.12,.55,'#b89a70',s,[-7.4,.45,-1.6]);this.box(2.4,.4,.09,'#b89a70',s,[-7.4,.72,-1.87]);[-8.3,-6.5].forEach(x=>this.box(.08,.45,.42,'#57615b',s,[x,.23,-1.6]));
  [[-8.65,1.6],[8.5,-1.8]].forEach(([x,z])=>{this.mesh(new THREE.CylinderGeometry(.27,.2,.5,18),'#d4c4aa',s,[x,.25,z]);for(let i=0;i<9;i++){let a=i*2.4;this.rod([x,.4,z],[x+.36*Math.cos(a),1.15+Math.sin(i)*.15,z+.28*Math.sin(a)],.016,'#6c7c52',s);let leaf=this.sphere(.19,'#758861',s,[x+.33*Math.cos(a),1.05+Math.sin(i)*.15,z+.25*Math.sin(a)],[.5,1.6,.8]);leaf.rotation.z=a;}});
 }
 person(color,seated=false,index=0){let g=new THREE.Group(),skin='#c99b7e',hair=seated?'#bfc0b4':index===2?'#9b9e95':'#393e37';const base=seated?.7:.94;
  this.sphere(.24,color,g,[0,base+.27,0],[1,.95,.64]);this.box(.4,.4,.28,color,g,[0,base+.14,0]);
  this.rod([0,base+.39,0],[0,base+.5,0],.073,skin,g);this.sphere(.17,skin,g,[0,base+.65,.025],[.85,1.15,.85]);this.sphere(.176,hair,g,[0,base+.72,-.018],[.9,.9,.9]);this.sphere(.034,skin,g,[0,base+.65,.165],[.65,1,1]);
  [-1,1].forEach(side=>{this.sphere(.013,'#3b3733',g,[side*.064,base+.69,.154]);});
  const legs=[];[-1,1].forEach(side=>{let leg=new THREE.Group();leg.position.set(side*.115,base-.04,0);g.add(leg);legs.push(leg);if(seated){this.rod([0,0,0],[0,-.11,.36],.098,'#c0b499',leg);this.rod([0,-.11,.36],[0,-.5,.43],.075,'#c0b499',leg);this.box(.15,.09,.27,'#4b514c',leg,[0,-.55,.49]);}else{this.rod([0,0,0],[0,-.43,0],.09,index===1?'#dad1bb':'#78817a',leg);this.rod([0,-.43,0],[0,-.81,.015],.069,index===1?'#dad1bb':'#78817a',leg);this.box(.16,.11,.29,'#4e514a',leg,[0,-.86,.07]);}
  let shoulder=[side*.24,base+.35,0],elbow=[side*.29,base+.08,seated?.13:0],hand=[side*.29,base+(seated?.06:-.17),seated?.37:.035];this.rod(shoulder,elbow,.068,color,g);this.rod(elbow,hand,.057,color,g);this.sphere(.061,skin,g,hand,[.85,1,1.15]);});
  if(index===1&&!seated){this.box(.22,.32,.13,'#dfd6bb',g,[.34,.75,.06]);this.rod([.3,1.24,0],[.36,.8,.05],.018,'#c5bca1',g);}
  g.userData.legs=legs;g.userData.seated=seated;return g;
 }
 buildChair(){let g=new THREE.Group(),metal=this.mat('#8a9690',.3);this.box(.59,.15,.63,'#2e403b',g,[0,.32,-.06]);this.box(.58,.12,.59,'#4a645a',g,[0,.65,.02]);this.box(.59,.65,.12,'#316659',g,[0,.96,-.3]);this.box(.54,.19,.08,'#3b5b50',g,[0,1.32,-.32]);
  [-1,1].forEach(side=>{this.rod([side*.33,.42,-.33],[side*.33,.97,-.33],.029,metal,g);this.rod([side*.33,.42,-.33],[side*.33,.4,.35],.025,metal,g);this.rod([side*.32,.75,-.23],[side*.32,.9,.29],.026,metal,g);this.box(.14,.075,.62,'#36423d',g,[side*.34,.9,.03]);
   const wheel=new THREE.Group();wheel.position.set(side*.39,.31,-.15);g.add(wheel);let tire=this.mesh(new THREE.TorusGeometry(.25,.06,12,32),'#303631',wheel);tire.rotation.y=Math.PI/2;let hub=this.mesh(new THREE.CylinderGeometry(.18,.18,.075,24),metal,wheel);hub.rotation.z=Math.PI/2;for(let i=0;i<8;i++){let a=i*Math.PI/4;this.rod([0,0,0],[0,.21*Math.sin(a),.21*Math.cos(a)],.012,'#bac2b7',wheel);}this.wheels.push(wheel);
   const cast=this.mesh(new THREE.CylinderGeometry(.105,.105,.065,16),'#353d37',g,[side*.3,.11,.43]);cast.rotation.z=Math.PI/2;this.rod([side*.3,.35,.35],[side*.3,.12,.43],.025,metal,g);this.rod([side*.23,.6,.3],[side*.23,.14,.61],.025,metal,g);this.box(.22,.045,.28,'#3e4c44',g,[side*.16,.14,.6]);});
  this.box(.12,.05,.2,'#253c34',g,[.34,.96,.32]);this.rod([.34,.96,.36],[.34,1.06,.36],.019,'#252e27',g);this.sphere(.03,'#343e34',g,[.34,1.075,.36]);this.occupant=this.person('#427567',true);g.add(this.occupant);return g;
 }
 addLabel(text,pos){let el=document.createElement('div');el.className='label3d';el.textContent=text;document.getElementById('labels').append(el);this.labels.push({el,pos})}
 reset(){this.interrupt();this.chair.position.set(-.8,0,0);this.chair.rotation.y=Math.PI/2;this.people.forEach((p,i)=>{p.position.set(1.5+i*.85,0,0);p.rotation.y=-Math.PI/2});this.paused=false;this.render()}
 resize(){const w=this.canvas.clientWidth,h=this.canvas.clientHeight;if(!w||!h)return;this.renderer.setSize(w,h,false);let width=w<650?20.5:21;let hh=width/(w/h)/2;this.camera.left=-width/2;this.camera.right=width/2;this.camera.top=hh;this.camera.bottom=-hh;this.camera.updateProjectionMatrix();this.setCamera(this.view)}
 setCamera(view){this.view=view;if(view==='passenger'){const p=this.chair.position;this.camera.position.set(p.x-5,4.1,6.5);this.camera.lookAt(p.x+3,.6,0);this.camera.zoom=1.8;}else{this.camera.position.set(2,12,15);this.camera.lookAt(0,.25,0);this.camera.zoom=1;}this.camera.updateProjectionMatrix();this.render()}
 snapshot(){return this.actors.map(a=>({x:a.position.x,z:a.position.z,yaw:a.rotation.y}))}
 interrupt(){this.animation=null;this.actors?.forEach(p=>p.userData.legs?.forEach(l=>l.rotation.x=0));return this.snapshot?.()}
 play(segments,done,step){this.paused=false;this.animation={segments,index:0,elapsed:0,start:this.snapshot(),done,step};step?.(segments[0].note);}
 tick(dt){if(this.animation&&!this.paused){let a=this.animation,s=a.segments[a.index];a.elapsed+=dt*this.speed;let f=Math.min(a.elapsed/s.duration,1),smooth=f*f*(3-2*f);for(let i=0;i<4;i++){const goal=s.poses[i];if(!goal)continue;const p=this.actors[i],st=a.start[i];let old=p.position.clone();p.position.x=st.x+(goal.x-st.x)*smooth;p.position.z=st.z+(goal.z-st.z)*smooth;if(goal.yaw!==undefined)p.rotation.y=st.yaw+(goal.yaw-st.yaw)*smooth;let dist=p.position.distanceTo(old);if(i===0)this.wheels.forEach(w=>w.rotation.x+=dist/.25);else p.userData.legs.forEach((l,k)=>l.rotation.x=dist>.0001?Math.sin(a.elapsed*8+k*Math.PI)*.34:0);}
   if(f>=1){a.index++;if(a.index===a.segments.length){this.animation=null;this.people.forEach(p=>p.userData.legs.forEach(l=>l.rotation.x=0));a.done?.();}else{a.elapsed=0;a.start=this.snapshot();a.step?.(a.segments[a.index].note)}}}
  if(this.view==='passenger'){let p=this.chair.position;this.camera.position.set(p.x-5,4.1,6.5);this.camera.lookAt(p.x+3,.6,0)}this.render();}
 render(){if(!this.renderer)return;this.renderer.render(this.scene,this.camera);this.labels?.forEach(({el,pos})=>{let v=pos().project(this.camera);el.style.left=(v.x*.5+.5)*this.canvas.clientWidth+'px';el.style.top=(-v.y*.5+.5)*this.canvas.clientHeight+'px';el.hidden=this.view==='passenger'||Math.abs(v.x)>.98||Math.abs(v.y)>.96||(this.canvas.clientWidth<650&&el.textContent.includes('空间'));})}
 route(branch){const ch=(x,z,yaw=Math.PI/2)=>({x,z,yaw});const ps=(xs,z=0,yaw=-Math.PI/2)=>Object.fromEntries(xs.map((x,i)=>[i+1,ch(x,z,yaw)]));if(branch==='self')return[
   {duration:5,poses:{0:ch(-4.5,0)},note:'轮椅带着林岚向后退。'},
   {duration:2,poses:{0:ch(-4.5,1.65,0)},note:'轮椅进入近处的错身空间。'},
   {duration:5,poses:ps([-7.5,-6.65,-5.8]),note:'林岚等候，行人先通过。'},
   {duration:2,poses:{0:ch(-4.5,0,0)},note:'行人已通过，轮椅回到走廊。'},
   {duration:5,poses:{0:ch(8,0)},note:'轮椅继续前往合唱教室。'}];
  return [{duration:4,poses:ps([4.5,5.35,6.2]),note:'行人愿意配合，向后折返。'},
   {duration:2,poses:ps([4.5,5.35,6.2],-1.65,Math.PI),note:'行人进入较远的错身空间。'},
   {duration:5,poses:{0:ch(8,0)},note:'行人等候，轮椅先通过。'},
   {duration:2,poses:ps([4.5,5.35,6.2],0,Math.PI),note:'轮椅已通过，行人回到走廊。'},
   {duration:5,poses:ps([-7.5,-6.65,-5.8]),note:'行人继续去接家人。'}];}
}
window.YieldStage=YieldStage;


