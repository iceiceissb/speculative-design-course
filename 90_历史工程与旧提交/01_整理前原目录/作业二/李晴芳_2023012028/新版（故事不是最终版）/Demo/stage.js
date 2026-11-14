/* Scripted speculative theatre, not a physical navigation or hospital control system. */
class HospitalStage extends HospitalMeshes {
 constructor(canvas){super();this.canvas=canvas;this.scene=new THREE.Scene();this.scene.background=new THREE.Color('#0a172a');this.scene.fog=new THREE.Fog('#0a172a',38,80);
  this.renderer=new THREE.WebGLRenderer({canvas,antialias:true,preserveDrawingBuffer:true,powerPreference:'high-performance'});this.renderer.setPixelRatio(Math.min(devicePixelRatio,1.7));this.renderer.shadowMap.enabled=true;this.renderer.shadowMap.type=THREE.PCFSoftShadowMap;this.renderer.outputEncoding=THREE.sRGBEncoding;this.renderer.toneMapping=THREE.ACESFilmicToneMapping;this.renderer.toneMappingExposure=1.04;
  this.camera=new THREE.PerspectiveCamera(40,1,.1,120);this.focus=new THREE.Vector3(0,1.4,-.7);this.orbit={theta:.27,phi:1.04,r:26};this.view=0;this.speed=1;this.time=0;this.paused=false;this.reduced=matchMedia('(prefers-reduced-motion:reduce)').matches;this.running=null;this.chapter=0;this.padAmount=1;this.musicAmount=0;
  this.scene.add(new THREE.HemisphereLight(0xc5dded,0x3d443b,.46));let sun=new THREE.DirectionalLight(0xffd4a2,1.28);sun.position.set(-7,15,10);sun.castShadow=true;sun.shadow.mapSize.set(2048,2048);Object.assign(sun.shadow.camera,{left:-15,right:15,top:13,bottom:-13,near:.1,far:40});sun.shadow.bias=-.00025;sun.shadow.normalBias=.035;this.scene.add(sun);
  let rim=new THREE.DirectionalLight(0x81cecf,.66);rim.position.set(9,8,-5);this.scene.add(rim);
  this.buildHospital();this.buildActors();this.buildProjections();this.buildBridge();this.buildGarden();this.setupPointer();this.reset(0);
  new ResizeObserver(()=>this.resize()).observe(canvas.parentElement);this.resize();let last=performance.now();const loop=now=>{let dt=Math.min((now-last)/1000,.06);last=now;this.tick(dt);this.frame=requestAnimationFrame(loop)};this.frame=requestAnimationFrame(loop);
 }
 buildHospital(){const s=this.scene,metal=this.mat('#577478',true);this.box(19,.48,12.5,'#43595e',s,[0,-.28,0],.13);this.box(19.05,.06,12.5,'#758080',s,[0,-.05,0]);
  for(let x=-9;x<=9;x++)for(let z=-6;z<=6;z++){const c=(x*7+z*3)%5===0?'#386267':(x+z)%3===0?'#3f686a':'#466f70';const tile=this.box(.965,.035,.965,c,s,[x,-.008,z],.009);tile.receiveShadow=true;}
  for(let x=-8.5;x<9;x+=3)this.box(.027,.006,12.25,'#b89e67',s,[x,.016,0],.002);
  this.box(19.1,.12,.1,'#b5a37b',s,[0,-.09,6.29]);this.box(.1,.12,12.5,'#b5a37b',s,[-9.53,-.09,0]);
  this.box(19,5.2,.5,'#698181',s,[0,2.59,-6.18],.04);this.box(19,.26,.8,'#91a097',s,[0,5.15,-5.93]);
  for(let x=-9;x<=9;x+=1.5){this.box(.035,4.9,.018,'#526d70',s,[x,2.5,-5.918]);for(let y of [.27,4.8])this.ball(.035,metal,s,[x+.08,y,-5.876],[1,1,.4]);}
  // Surface-mounted pipes, brackets and ventilators give the hospital a lived-in industrial body.
  for(let j=0;j<3;j++){let x=7.95+j*.18;this.rod([x,.5,-5.68],[x,5.45,-5.68],.052,'#b56738',s);this.rod([-8,5.42+j*.15,-5.68],[x,5.42+j*.15,-5.68],.052,'#b56738',s);for(let y=1;y<5;y+=1.2)this.box(.7,.09,.13,metal,s,[8.12,y,-5.64]);}
  for(let x of [-8.1,2.6,8.7]){this.box(.73,.68,.16,'#a7a893',s,[x,4.32,-5.72]);for(let y=4.1;y<4.58;y+=.085)this.box(.56,.025,.065,'#243c45',s,[x,y,-5.61]);}
  this.lifts=[];[-5.5,0,5.5].forEach((x,i)=>{let g=new THREE.Group();s.add(g);g.position.set(x,0,-4.2);const c=['#b9713c','#638f82','#a79e85'][i],e=['#ffad47','#80f5cd','#ffe0a0'][i];
   this.box(.45,4.8,.74,c,g,[-1.93,2.4,-.08],.14);this.box(.45,4.8,.74,c,g,[1.93,2.4,-.08],.14);this.box(4.2,1.05,.74,c,g,[0,4.27,-.08],.18);this.box(3.2,.05,2.6,'#89957f',g,[0,.025,-.88]);this.box(3.2,3.5,.09,'#64796f',g,[0,1.85,-2.06]);
   for(let side of [-1,1]){this.box(.14,3.76,2.5,'#7d9387',g,[side*1.59,1.9,-.9]);this.box(.2,3.9,.16,metal,g,[side*1.75,1.94,.46]);this.box(.045,3.64,.065,this.glow(e,.8),g,[side*1.63,1.87,.49]);}
   this.rod([-1.35,1.1,-1.95],[1.35,1.1,-1.95],.045,metal,g);this.box(2.96,.05,1.45,'#d4d9b9',g,[0,3.55,-.9]);this.box(2.4,.035,.28,this.glow(e,2),g,[0,3.46,-.45]);
   const doors=[];for(let side of [-1,1]){let d=this.box(1.55,3.38,.1,this.mat(i===2?'#807c68':'#71887d',true),g,[side*.785,1.73,.3],.025);doors.push(d);for(let yy=.4;yy<3.2;yy+=.46)this.box(.018,.22,.005,'#85968c',d,[side*.5,yy-1.7,.06]);}
   this.sign(['A','B','C'][i],1.2,.63,g,[0,4.13,.31],c,'#122d37',185);this.sign(['效率优先','慢一点也好','请帮我翻译'][i],2.6,.31,g,[0,3.65,.4],'#173338',e,62);
   const eyes=[];for(let side of [-1,1])eyes.push(this.ball(.075,this.glow(e,1.3),g,[side*.58,4.65,.3],[1.7,.45,.35]));
   this.box(.24,.65,.09,'#233b40',g,[1.98,1.48,.36]);for(let j=0;j<3;j++)this.ball(.046,this.glow(j===0?e:'#db8e55',.5),g,[1.98,1.68-j*.2,.42],[1,1,.4]);
   let light=new THREE.PointLight(e,1.1,6,2);light.position.set(0,2.95,-.6);g.add(light);this.lifts.push({g,doors,light,eyes,open:1,active:false});
  });
  this.sign('医院也在学习相处',3.2,.38,s,[-6.4,5.02,-3.74],'#718581','#223c44',57);
  this.sign('7F  花园',2.05,.41,s,[8.26,3.39,-5.75],'#718581','#1a3947',76);
  this.benches=[];for(const x of [-7.6,7.8]){let g=new THREE.Group();s.add(g);g.position.set(x,0,x<0?-1.6:1.4);g.rotation.y=x<0?Math.PI/2:-Math.PI/2;for(let j=-1;j<=1;j++){this.box(.92,.16,.8,'#316a70',g,[j*.97,.68,0],.08);this.box(.92,.78,.15,'#316a70',g,[j*.97,1.04,-.42],.08);this.rod([j*.97,.54,0],[j*.97,.13,0],.055,metal,g);}this.rod([-1.35,.22,0],[1.35,.22,0],.048,metal,g);this.benches.push(g);}
  this.plant(-8.1,-4,1.2);this.plant(8.55,-3.3,1.18);this.plant(-8.4,4.7,1.2);this.plant(7.9,4.7,1.1);
  this.box(3.1,.8,.86,'#899b93',s,[4.8,.39,5.65]);this.box(2.88,.025,.65,'#344b42',s,[4.8,.82,5.65]);for(let i=0;i<15;i++)this.ball(.21,i%2?'#49694d':'#54765b',s,[3.5+(i%7)*.42,.92+(i%3)*.07,5.55+(i%2)*.22],[1.2,.8,1]);
  this.sign('人会变，医院也在学习',3,.3,s,[4.8,.42,6.1],'#899b93','#29444b',54);
 }
 buildActors(){this.chair=this.wheelchair();this.scene.add(this.chair);this.concierge=this.concierge();this.scene.add(this.concierge);this.cleaners=[];for(let i=0;i<3;i++){const g=this.cleaner();this.scene.add(g);this.cleaners.push(g);}
  this.people=[];['#ad9980','#546d79','#9c7160','#6b8066'].forEach((c,i)=>{const g=this.person(c,false,i+1);g.scale.setScalar(1.43);this.scene.add(g);this.people.push(g);});
  // Visible paper ticket establishes the unconnected passenger without reading medical data.
  const paper=this.box(.28,.34,.02,'#e9e0bd',this.people[0],[.29,1.04,.21],.003);paper.rotation.z=-.23;
 }
 buildProjections(){this.pads=[];const colors=['#82ffe1','#ffa955','#8fc9ff','#b8edc3','#ecc4fb','#87ffda'];
  for(let j=0;j<6;j++){const g=new THREE.Group();this.scene.add(g);const mat=new THREE.MeshBasicMaterial({color:colors[j],transparent:true,opacity:.68,depthWrite:false});const plane=this.mesh(new THREE.PlaneGeometry(1.48,1.72),new THREE.MeshBasicMaterial({color:colors[j],transparent:true,opacity:.095,depthWrite:false,side:THREE.DoubleSide}),g,[0,.023,0]);plane.rotation.x=-Math.PI/2;
   const ring=this.mesh(new THREE.TorusGeometry(.35,.026,8,40,Math.PI*1.62),mat,g,[-.06,.034,.2]);ring.rotation.x=-Math.PI/2;ring.rotation.z=.12;
   this.ball(.095,mat,g,[.05,.036,-.42],[1,.06,1]);this.rod([.035,.036,-.29],[.035,.036,.08],.032,mat,g);this.rod([.035,.036,.08],[.37,.036,.08],.032,mat,g);this.rod([.37,.036,.08],[.5,.036,.42],.032,mat,g);this.rod([.5,.036,.42],[.68,.036,.38],.027,mat,g);
   for(let side of [-1,1]){this.box(.024,.005,1.74,mat,g,[side*.75,.038,0],.001);this.box(1.52,.005,.024,mat,g,[0,.038,side*.88],.001);}
   const positions=[[0,-4.7],[-.88,-3.02],[.85,-3.1],[-5.5,-4.8],[5.5,-4.8],[5.5,-2.85]];g.position.set(positions[j][0],.06,positions[j][1]);g.userData.mat=mat;this.pads.push(g);
  }
  this.routes=[];for(let j=0;j<3;j++){const g=new THREE.Group();this.scene.add(g);const mat=new THREE.MeshBasicMaterial({color:j===0?'#ffbb65':j===1?'#7affd8':'#f8dca0',transparent:true,opacity:.8,depthWrite:false});for(let i=0;i<45;i++){let t=i/44,x=-3.3+(j===0?-2.2:j===1?3.3:8.8)*t+Math.sin(t*Math.PI)*.65,z=3.2-7*t;const d=this.mesh(new THREE.CircleGeometry(.039,8),mat,g,[x,.05,z]);d.rotation.x=-Math.PI/2;}this.routes.push(g);}
  this.river=new THREE.Group();this.scene.add(this.river);this.notes=[];for(let i=0;i<32;i++){const t=i/31,x=Math.sin(t*Math.PI*2)*.6,z=3.8-t*6.5;const leaf=this.mesh(new THREE.SphereGeometry(.09,8,6),new THREE.MeshBasicMaterial({color:i%3===0?'#efbb63':'#79f9d6',transparent:true,opacity:.8}),this.river,[x,.05,z]);leaf.scale.set(1.1,.06,2.6);leaf.rotation.y=t*8;this.notes.push(leaf);}
  this.lidar=new THREE.Group();this.chair.add(this.lidar);for(let j=0;j<3;j++){const ring=this.mesh(new THREE.TorusGeometry(1.1+j*.35,.008,4,80,Math.PI*.8),new THREE.MeshBasicMaterial({color:'#68ead0',transparent:true,opacity:.21}),this.lidar,[0,.05,.2]);ring.rotation.x=-Math.PI/2;ring.rotation.z=.3;}
 }
 buildBridge(){this.bridge=new THREE.Group();this.scene.add(this.bridge);this.box(3.0,.55,2.6,'#7e9391',this.bridge,[0,.27,-1.6]);this.box(3.1,.04,2.6,'#bcc1a7',this.bridge,[0,.565,-1.6]);
  this.rampParts=[];for(let i=0;i<3;i++){let p=this.box(1.72,.1,.9,'#c4b478',this.bridge,[0,.16+i*.17,1.22-i*.82],.025);p.rotation.x=.2;this.rampParts.push(p);}
  const geo=new THREE.BufferGeometry();geo.setAttribute('position',new THREE.Float32BufferAttribute([-3.3,0,2,-1.7,0,2,-3.3,.55,-1.5,-1.7,0,2,-1.7,.55,-1.5,-3.3,.55,-1.5],3));geo.computeVertexNormals();this.mesh(geo,this.mat('#728d86'),this.bridge);this.rod([-3.25,.7,2],[-3.25,1.25,-1.5],.035,'#a8b6a6',this.bridge);
 }
 buildGarden(){this.gardenRig=new THREE.Group();this.scene.add(this.gardenRig);for(let x of [-4.3,4.3]){this.box(.45,11,.5,'#657b7c',this.gardenRig,[x,5.5,-4.3]);this.box(.075,10.7,.08,this.mat('#bba986',true),this.gardenRig,[x,5.5,-3.97]);for(let y=.5;y<11;y+=.65)this.box(.61,.09,.12,'#354e59',this.gardenRig,[x,y,-4]);}
  this.garden=new THREE.Group();this.gardenRig.add(this.garden);this.garden.position.set(0,7.7,-2.2);this.box(8.6,.48,4.4,'#80948d',this.garden,[0,0,0],.16);this.box(8.5,.08,4.3,'#a7b397',this.garden,[0,.27,0]);
  for(let i=-4;i<=4;i++)this.box(.025,.01,4,'#788c7d',this.garden,[i,.315,0]);
  const glass=new THREE.MeshPhysicalMaterial({color:'#88c8bf',transparent:true,opacity:.3,roughness:.15,metalness:.1,side:THREE.DoubleSide,depthWrite:false});
  for(const x of [-4.1,4.1]){this.box(.06,.96,3.9,glass,this.garden,[x,.79,0]);this.rod([x,1.3,-2],[x,1.3,2],.035,'#d3ccb1',this.garden);}this.box(8.1,.85,.035,glass,this.garden,[0,.8,-2]);this.rod([-4.1,1.3,-2],[4.1,1.3,-2],.035,'#d3ccb1',this.garden);
  this.box(2.2,.15,.8,'#3e6865',this.garden,[1.7,.8,-.8]);this.box(2.2,.67,.13,'#3e6865',this.garden,[1.7,1.16,-1.2]);for(let x of [.8,2.5])this.rod([x,.32,-.8],[x,.73,-.8],.07,'#3e5559',this.garden);
  this.plant(-3,-1,1.5,this.garden);this.plant(3.1,1.1,.8,this.garden);this.rod([-2.6,.4,-1],[-2.5,3.6,-1],.1,'#625b40',this.garden);for(let i=0;i<14;i++)this.ball(.46,i%2?'#44755c':'#729161',this.garden,[-2.5+Math.sin(i*2.4)*.8,2.9+(i%4)*.29,-1+Math.cos(i*2.4)*.7],[1.2,.8,1]);
  this.friend=this.person('#b18063',false,1);this.friend.scale.setScalar(1.32);this.friend.position.set(1.6,.33,.35);this.garden.add(this.friend);
  this.sign('7F  花园',2,.43,this.garden,[1.8,-.035,2.25],'#587472','#e9f1dc',86);this.box(5.7,.025,.055,this.glow('#ffc06a',1.6),this.garden,[0,-.2,2]);
  this.arms=[];for(let x of [-3.8,3.8]){let arm=new THREE.Group();this.garden.add(arm);arm.position.set(x,-.4,-.8);this.rod([0,0,0],[0,-1.25,-1.1],.15,'#c37938',arm);this.ball(.24,this.mat('#3a545c',true),arm,[0,-1.25,-1.1]);this.rod([0,-1.25,-1.1],[0,-1.7,-2],.13,'#c37938',arm);this.arms.push(arm);}
 }
 reset(chapter){this.running=null;this.paused=false;this.chapter=chapter;this.time=0;this.action=null;this.musicAmount=0;this.afterglow=0;this.padAmount=chapter===0?1:0;this.gardenRig.visible=chapter===4;this.bridge.visible=chapter===3;this.garden.position.y=7.7;this.river.visible=false;this.lidar.visible=false;this.rampParts.forEach(p=>p.visible=false);
  this.chair.position.set(-3.25,0,3.15);this.chair.rotation.set(0,-.22,0);this.concierge.position.set(4.1,0,1.6);this.concierge.rotation.set(0,-.35,0);this.concierge.userData.head.rotation.set(0,0,-.12);this.concierge.userData.arms.forEach(a=>a.rotation.set(0,0,0));
  this.people.forEach((p,i)=>{p.visible=true;p.position.set([-1.75,2,5.9,-6.3][i],0,[-1.2,.4,3.7,-.8][i]);p.rotation.y=[-.2,.45,-.7,.35][i];p.userData.legs.forEach(l=>l.rotation.x=0);});
  this.cleaners.forEach((c,i)=>{c.position.set([2.2,5.9,-6.1][i],0,[3.8,-1.1,2.8][i]);c.scale.set(1,1,1);c.rotation.set(0,0,0);});
  this.lifts.forEach((l,i)=>{l.open=i===1?1:.18;l.active=false;});this.routes.forEach((g,i)=>g.visible=chapter===0&&i===1);this.pads.forEach((g,i)=>g.visible=i<this.padAmount);
  if(chapter===2){this.chair.position.set(0,0,3.6);this.people[0].position.set(-.55,0,.2);this.people[1].position.set(.65,0,-1.1);this.people[2].position.set(.2,0,1.65);this.river.visible=true;this.notes.forEach(n=>n.material.opacity=.19);}
  if(chapter===3){this.chair.position.set(0,0,3.4);this.people.forEach(p=>p.visible=false);this.concierge.position.set(2.2,0,1.8);}
  if(chapter===4){this.people.forEach(p=>p.visible=false);this.chair.position.set(-2.5,0,3.5);this.concierge.position.set(4.9,0,2.5);this.benches.forEach(b=>b.visible=false);}else this.benches.forEach(b=>b.visible=true);
  if(chapter===5){this.people.forEach((p,i)=>p.visible=i===0);this.chair.position.set(-1.7,0,1.7);this.concierge.position.set(2.2,0,.4);}
  this.setView(0);this.updateDoors();this.render();
 }
 setView(v){this.view=v;const tall=this.chapter===4;if(v===0){this.orbit={theta:.23,phi:tall?1.08:1.07,r:tall?31:24.5};this.focus.set(0,tall?4.2:1.45,-.9);}else if(v===1){this.orbit={theta:.02,phi:1.42,r:tall?22:17};this.focus.set(0,tall?4:1.6,-2.3);}else{this.orbit={theta:0,phi:.25,r:tall?33:26};this.focus.set(0,tall?3:0,-.9);}this.applyCamera();}
 applyCamera(){const o=this.orbit,aspect=this.canvas.clientWidth/Math.max(this.canvas.clientHeight,1),adjust=Math.max(1,1.38/aspect);this.camera.position.set(this.focus.x+o.r*adjust*Math.sin(o.phi)*Math.sin(o.theta),this.focus.y+o.r*adjust*Math.cos(o.phi),this.focus.z+o.r*adjust*Math.sin(o.phi)*Math.cos(o.theta));this.camera.lookAt(this.focus);}
 setupPointer(){let drag=null;this.canvas.addEventListener('pointerdown',e=>{drag={x:e.clientX,y:e.clientY};this.canvas.setPointerCapture(e.pointerId);});this.canvas.addEventListener('pointermove',e=>{if(!drag)return;this.orbit.theta-=(e.clientX-drag.x)*.006;this.orbit.phi=Math.max(.2,Math.min(1.52,this.orbit.phi+(e.clientY-drag.y)*.006));drag={x:e.clientX,y:e.clientY};this.applyCamera();});this.canvas.addEventListener('pointerup',()=>drag=null);this.canvas.addEventListener('pointercancel',()=>drag=null);this.canvas.addEventListener('wheel',e=>{e.preventDefault();this.orbit.r=Math.max(12,Math.min(47,this.orbit.r+e.deltaY*.014));this.applyCamera();},{passive:false});this.canvas.addEventListener('keydown',e=>{if(['ArrowLeft','ArrowRight','ArrowUp','ArrowDown'].includes(e.key)){e.preventDefault();if(e.key==='ArrowLeft')this.orbit.theta-=.08;if(e.key==='ArrowRight')this.orbit.theta+=.08;if(e.key==='ArrowUp')this.orbit.phi=Math.max(.2,this.orbit.phi-.07);if(e.key==='ArrowDown')this.orbit.phi=Math.min(1.52,this.orbit.phi+.07);this.applyCamera();}});}
 resize(){let w=this.canvas.clientWidth,h=this.canvas.clientHeight;if(!w||!h)return;this.renderer.setSize(w,h,false);this.camera.aspect=w/h;this.camera.updateProjectionMatrix();this.applyCamera();this.render();}
 play(id,beats,onBeat,onDone,options={}){this.action=id;this.paused=false;this.running={id,elapsed:0,duration:this.reduced?5.2:11.6,beat:-1,beats,onBeat,onDone,options};this.updateAction(0,id,options);}
 skip(){if(!this.running)return;const r=this.running;this.updateAction(1,r.id,r.options);this.running=null;this.paused=false;r.onBeat?.(r.beats.at(-1),r.beats.length-1);r.onDone?.();this.render();}
 progress(t,a=0,b=1){let v=Math.max(0,Math.min(1,(t-a)/(b-a)));return v*v*(3-2*v);}
 move(obj,from,to,f){obj.position.set(from[0]+(to[0]-from[0])*f,from[1]+(to[1]-from[1])*f,from[2]+(to[2]-from[2])*f);}
 updateAction(t,id,options={}){const p=(a,b)=>this.progress(t,a,b);this.lidar.visible=['shadow','delegate','bridge'].includes(id)&&t<.8;
  if(id==='shadow'){this.padAmount=t<.35?1:Math.min(6,2+Math.floor((t-.35)*8));this.chair.rotation.y=Math.PI;this.move(this.chair,[-3.25,0,3.15],[0,0,-1.6],p(.02,.35));this.lifts[1].open=1;this.routes[1].visible=true;this.people[0].rotation.y=.5;}
  if(id==='queue'){this.padAmount=0;this.routes[1].visible=false;this.move(this.people[0],[-1.75,0,-1.2],[0,0,-5.1],p(.1,.7));this.people[0].rotation.y=Math.PI;this.lifts[1].open=1-p(.73,.95);this.people[0].visible=t<.93;this.chair.rotation.y=.15;this.concierge.userData.arms[0].rotation.z=-.7*p(0,.2);}
  if(id==='delegate'){let target=t<.3?0:t<.64?1:2;this.routes.forEach((r,i)=>r.visible=i===target);this.lifts.forEach((l,i)=>l.active=i===target);this.padAmount=0;this.chair.rotation.y=Math.PI;let a,b,f;if(t<.3){a=[-3.25,0,3.15];b=[-5.4,0,.7];f=p(0,.3);}else if(t<.64){a=[-5.4,0,.7];b=[0,0,.7];f=p(.3,.64);}else{a=[0,0,.7];b=[5.3,0,.7];f=p(.64,.97);}this.move(this.chair,a,b,f);this.concierge.position.set(6.9,0,-1.7);this.concierge.rotation.y=Math.PI;}
  if(id==='chooseB'){this.routes.forEach((r,i)=>r.visible=i===1);this.lifts[1].active=true;this.chair.rotation.y=Math.PI;this.move(this.chair,[-3.25,0,3.15],[0,0,-5.05],p(.05,.68));this.lifts[1].open=1-.72*p(.77,1);}
  if(id==='music'||id==='quiet'){this.padAmount=0;this.river.visible=true;this.musicAmount=id==='music'?1:.05;this.notes.forEach(n=>n.material.opacity=id==='music'?.85:.08);this.people[0].position.x=-.55-1.25*p(.12,.42);this.people[1].position.x=.65+1.45*p(.25,.53);this.people[2].position.x=.2+2.1*p(.38,.64);this.chair.rotation.y=Math.PI;this.move(this.chair,[0,0,3.6],[0,0,-2.5],p(.48,.93));this.concierge.userData.arms[0].rotation.z=-.58*p(0,.2);}
  if(id==='bridge'){this.padAmount=0;this.rampParts.forEach((part,i)=>part.visible=t>.22+i*.08&&t<.85);this.cleaners.forEach((c,i)=>{let from=[[2.2,0,3.8],[5.9,0,-1.1],[-6.1,0,2.8]][i],to=[0,.02+i*.17,1.22-i*.82],f=t<.75?p(.02+i*.03,.32+i*.03):1-p(.83,1);this.move(c,from,to,f);c.scale.set(1+f*.25,1,1);});this.chair.rotation.y=Math.PI;this.move(this.chair,[0,0,3.4],[0,.58,-1.35],p(.38,.82));this.concierge.userData.arms[0].rotation.z=-1.38*p(.08,.35);this.concierge.userData.arms[1].rotation.z=.55*p(.08,.35);}
  if(id==='detour'){this.padAmount=0;this.rampParts.forEach(p=>p.visible=false);let a,b,f;if(t<.33){a=[0,0,3.4];b=[-2.5,0,2.3];f=p(.05,.33);}else{a=[-2.5,0,2.3];b=[-2.5,.56,-1.5];f=p(.34,.87);}this.chair.rotation.y=Math.PI;this.move(this.chair,a,b,f);}
  if(id==='down'){this.gardenRig.visible=true;this.garden.position.y=7.7-7.25*p(.05,.8);this.concierge.userData.arms[1].rotation.z=1.13*p(0,.2);this.chair.rotation.y=Math.PI;this.chair.position.x=-2.5+1.5*p(.76,1);this.chair.position.z=3.5-1.9*p(.76,1);this.arms.forEach(a=>a.rotation.x=.5*p(.2,.8));}
  if(id==='up'){this.gardenRig.visible=true;this.garden.position.y=7.7;this.chair.rotation.y=Math.PI;if(t<.43)this.move(this.chair,[-2.5,0,3.5],[0,0,-4.5],p(.03,.42));else this.move(this.chair,[0,0,-4.5],[0,8.03,-.6],p(.43,.96));this.lifts[1].open=1;this.lifts[1].active=true;this.chair.userData.head.rotation.z=-.1;}
  if(id==='ask'){this.padAmount=0;this.river.visible=false;this.lidar.visible=false;this.chair.position.set(-1.7,0,1.7);this.chair.rotation.y=-.22;}
  if(id==='remember'){const useProjection=options.projection!==false;this.padAmount=useProjection&&t>.55?1:0;this.river.visible=useProjection&&t>.55;this.musicAmount=useProjection?1:0;this.notes.forEach(n=>n.material.opacity=.75);this.chair.position.set(-1.7,0,1.7);}
  this.pads.forEach((g,i)=>g.visible=i<this.padAmount);this.updateDoors();
 }
 revoke(){this.running=null;this.action='ask';this.padAmount=0;this.musicAmount=0;this.river.visible=false;this.pads.forEach(p=>p.visible=false);this.lidar.visible=false;this.paused=false;}
 updateDoors(){this.lifts.forEach(l=>{l.doors[0].position.x=-.785-l.open*.775;l.doors[1].position.x=.785+l.open*.775;l.doors.forEach(d=>{d.scale.x=Math.max(.001,1-l.open);d.visible=l.open<.995;});});}
 tick(dt){if(!this.paused){this.time+=dt;const t=this.time;
   if(this.running){const a=this.running;a.elapsed+=dt*this.speed;let ratio=Math.min(1,a.elapsed/a.duration);this.updateAction(ratio,a.id,a.options);let beat=Math.min(a.beats.length-1,Math.floor(ratio*a.beats.length));if(beat!==a.beat){a.beat=beat;a.onBeat?.(a.beats[beat],beat);}if(ratio>=1){this.running=null;a.onDone?.();}}
   if(!this.running&&this.action==='quiet'){this.afterglow+=dt;const fade=Math.max(0,1-this.afterglow/8);this.notes.forEach(n=>n.material.opacity=.08*fade);if(fade===0)this.river.visible=false;}
   if(!this.reduced){this.blinkers.forEach((eyes,i)=>{const blink=(t+i*.77)%4.8>.0&&(t+i*.77)%4.8<.13;eyes.forEach(e=>e.scale.y=blink?.17:1.3);});this.chair.userData.head.rotation.y=Math.sin(t*.7)*.13;this.concierge.userData.head.rotation.z=-.14+Math.sin(t*.8)*.055;
    this.lifts.forEach((l,i)=>{l.light.intensity=(l.active?1.75:1.1)+Math.sin(t*1.6+i)*.16;l.eyes.forEach(e=>e.scale.y=l.active?.7+.3*Math.sin(t*6):.45);});
    this.pads.forEach((g,i)=>g.userData.mat.opacity=.62+.17*Math.sin(t*2+i));this.notes.forEach((n,i)=>{n.scale.z=2.1+Math.sin(t*2+i)*.5;n.rotation.y+=.004*this.musicAmount;});this.lidar.rotation.y=t*.45;
    if(this.running){this.chair.userData.wheels.forEach(w=>w.rotation.x+=dt*1.2);this.people.forEach(g=>g.userData.legs?.forEach((l,i)=>l.rotation.x=Math.sin(t*5+i*Math.PI)*.055));}
   }
  }this.render();
 }
 render(){this.renderer.render(this.scene,this.camera);}
 snapshot(){return {chapter:this.chapter,action:this.action,chair:this.chair.position.toArray(),gardenY:this.garden.position.y,pads:this.pads.filter(p=>p.visible).length,river:this.river.visible,doors:this.lifts.map(l=>l.open),cleaners:this.cleaners.map(c=>c.position.toArray()),camera:this.camera.position.toArray(),time:this.time};}
}
