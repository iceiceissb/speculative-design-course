/* Locally rendered, scripted 3D scene. No robot control or physical safety model. */
class ElevatorStage {
  constructor(canvas, onActivity) {
    this.canvas=canvas;this.onActivity=onActivity;this.scene=new THREE.Scene();
    this.scene.background=new THREE.Color('#e8e2d7');
    this.renderer=new THREE.WebGLRenderer({canvas,antialias:true,preserveDrawingBuffer:true});
    this.renderer.setPixelRatio(Math.min(devicePixelRatio,2));this.renderer.shadowMap.enabled=true;
    this.renderer.shadowMap.type=THREE.PCFSoftShadowMap;this.renderer.outputEncoding=THREE.sRGBEncoding;
    this.renderer.toneMapping=THREE.ACESFilmicToneMapping;this.renderer.toneMappingExposure=.96;
    this.camera=new THREE.PerspectiveCamera(40,1,.1,80);this.view='overview';this.focus='lin';
    this.materials={};this.actors={};this.labels=[];this.door=0;this.paused=false;this.speed=1;
    this.reduced=matchMedia('(prefers-reduced-motion: reduce)').matches;
    this.scene.add(new THREE.HemisphereLight(0xfff9ee,0x9baca4,.75));
    const sun=new THREE.DirectionalLight(0xfff1d7,1.05);sun.position.set(-4,11,7);sun.castShadow=true;
    sun.shadow.mapSize.set(2048,2048);Object.assign(sun.shadow.camera,{left:-9,right:9,top:9,bottom:-9,near:.1,far:30});sun.shadow.bias=-.0003;sun.shadow.normalBias=.035;this.scene.add(sun);
    const fill=new THREE.DirectionalLight(0xdbebe9,.5);fill.position.set(7,6,-2);this.scene.add(fill);
    this.buildHospital();
    this.actors.lin=this.chair('#34796f',true);this.actors.other=this.chair('#a57a43',false);
    ['#677a76','#d8c9b1','#415666','#b68e78'].forEach((c,i)=>this.actors['p'+i]=this.person(c,false,i));
    this.actors.exit=this.person('#9c9d86',false,1);this.actors.nurse=this.person('#8db7c4',false,4);
    Object.values(this.actors).forEach(a=>this.scene.add(a));
    this.addLabel('林岚','lin');this.addLabel('另一位乘客','other');
    this.reset();new ResizeObserver(()=>this.resize()).observe(canvas.parentElement);this.resize();
    let previous=performance.now();const loop=now=>{let dt=Math.min((now-previous)/1000,.06);previous=now;this.tick(dt);requestAnimationFrame(loop)};requestAnimationFrame(loop);
  }
  mat(color,metal=false){let k=color+metal;if(!this.materials[k])this.materials[k]=new THREE.MeshStandardMaterial({color:new THREE.Color(color).convertSRGBToLinear(),roughness:metal?.38:.76,metalness:metal?.6:0});return this.materials[k]}
  mesh(geometry,color,parent,pos=[0,0,0]){let m=new THREE.Mesh(geometry,typeof color==='string'?this.mat(color):color);m.position.set(...pos);m.castShadow=true;m.receiveShadow=true;parent.add(m);return m}
  box(w,h,d,color,parent,pos){return this.mesh(new THREE.BoxGeometry(w,h,d),color,parent,pos)}
  ball(r,color,parent,pos,scale=[1,1,1]){let m=this.mesh(new THREE.SphereGeometry(r,24,16),color,parent,pos);m.scale.set(...scale);return m}
  rod(a,b,r,color,parent){let va=new THREE.Vector3(...a),vb=new THREE.Vector3(...b),delta=vb.clone().sub(va);let m=this.mesh(new THREE.CylinderGeometry(r,r,delta.length(),12),color,parent,va.clone().add(vb).multiplyScalar(.5).toArray());m.quaternion.setFromUnitVectors(new THREE.Vector3(0,1,0),delta.normalize());return m}
  sign(text,w,h,parent,pos,bg='#e6e1d4',fg='#354e4b',font=54){const c=document.createElement('canvas');c.width=1024;c.height=256;let ctx=c.getContext('2d');ctx.fillStyle=bg;ctx.fillRect(0,0,1024,256);ctx.fillStyle=fg;ctx.font=`500 ${font}px Microsoft YaHei`;ctx.textAlign='center';ctx.textBaseline='middle';ctx.fillText(text,512,128);let map=new THREE.CanvasTexture(c);map.encoding=THREE.sRGBEncoding;let m=this.mesh(new THREE.PlaneGeometry(w,h),new THREE.MeshBasicMaterial({map}),parent,pos);return m}
  buildHospital(){const s=this.scene,metal=this.mat('#a2aba7',true);
    this.box(11,.22,10,'#d8d1c2',s,[0,-.14,.2]);
    for(let x=-5;x<=5;x++)for(let z=-4;z<=5;z++){this.box(.992,.02,.992,(x+z)%3===0?'#e6e1d5':'#eae6dc',s,[x,-.019,z]);}
    // Exposed front of a hospital lobby and cutaway lift cabin.
    this.box(11,3.65,.22,'#d9d4c8',s,[0,1.8,-4.15]);
    [[-4.53,1.94],[-.12,1.16],[4.35,2.3]].forEach(([x,w])=>this.box(w,3.6,.56,'#e9e5da',s,[x,1.8,-1.4]));
    this.box(11,.35,.5,'#e2ded3',s,[0,3.4,-1.4]);
    this.box(.2,3.6,3,'#ded9cf',s,[-5.45,1.8,-2.8]);
    // Active cabin: 2.8m opening; people and wheelchairs use fixed story positions.
    this.box(3.05,.035,2.8,'#c6b397',s,[-2.13,.006,-2.72]);
    this.box(3.12,3.25,.12,'#d3b88b',s,[-2.13,1.63,-4.04]);
    [-3.69,-.57].forEach(x=>this.box(.12,3.25,2.75,'#d6c5a8',s,[x,1.63,-2.71]));
    for(let x=-3.5;x<-.6;x+=.54)this.box(.018,2.9,.025,'#c0a77e',s,[x,1.64,-3.96]);
    this.box(2.55,.11,.13,metal,s,[-2.13,.98,-3.84]);
    const glow=new THREE.PointLight(0xffdc98,.7,6);glow.position.set(-2.1,2.65,-2.45);s.add(glow);
    this.box(2.8,.04,.45,'#fff6cf',s,[-2.12,3.12,-2.7]);
    for(const x of [-3.67,-.57]){this.box(.16,3.3,.28,metal,s,[x,1.64,-1.07]);this.box(.055,3.17,.035,'#f6ead3',s,[x+.09,1.58,-.92]);}
    this.box(3.27,.17,.29,metal,s,[-2.12,3.23,-1.07]);this.box(3.12,.035,.37,metal,s,[-2.12,.018,-1.05]);
    this.doors=[this.box(1.53,3.12,.08,metal,s,[-2.9,1.57,-1.22]),this.box(1.53,3.12,.08,metal,s,[-1.35,1.57,-1.22])];
    this.sign('↑  1',1.05,.27,s,[-2.12,3.48,-1.14],'#283332','#eeb466',86);
    // Adjacent lift stays closed; it gives context rather than an alternate scripted route.
    this.box(2.37,3.04,.15,'#838e8a',s,[1.81,1.53,-1.31]);
    [1.23,2.4].forEach(x=>this.box(1.14,2.97,.05,metal,s,[x,1.51,-1.19]));
    [.58,3.05].forEach(x=>this.box(.12,3.15,.17,metal,s,[x,1.58,-1.05]));this.box(2.58,.14,.17,metal,s,[1.81,3.15,-1.05]);
    this.sign('↓  5',.85,.24,s,[1.81,3.43,-1.14],'#293333','#d6c9a8',86);
    for(const x of [-4.08,-.17,3.38]){this.box(.18,.5,.08,'#667673',s,[x,1.11,-1.08]);this.ball(.044,'#dfab61',s,[x,1.16,-1.025],[1,1,.35]);}
    this.sign('1F  门诊大厅',1.68,.49,s,[-4.56,2.62,-1.11],'#e9e5da','#435752',78);
    this.sign('3F  康复门诊 ↑',1.64,.35,s,[-4.56,2.18,-1.11],'#e9e5da','#61736c',65);
    this.sign('请先下后上',1.55,.35,s,[4.3,2.24,-1.11],'#e9e5da','#61736c',74);
    this.sign('门诊电梯',1.55,.35,s,[4.3,2.72,-1.11],'#e9e5da','#354e4b',76);
    [[-4.53,1.5],[4.35,1.75]].forEach(([x,w])=>{this.box(w,.095,.11,'#b39a77',s,[x,.94,-1.08]);});
    // Waiting chairs.
    const bench=new THREE.Group();s.add(bench);bench.position.set(-4.5,0,1.45);bench.rotation.y=Math.PI/2;
    for(let i=-1;i<=1;i++){this.box(.63,.13,.61,'#426e68',bench,[i*.72,.53,0]);let back=this.box(.63,.62,.09,'#426e68',bench,[i*.72,.88,-.3]);back.rotation.x=-.1;this.rod([i*.72,.45,0],[i*.72,.08,0],.045,metal,bench);}
    this.rod([-1,.16,0],[1,.16,0],.04,metal,bench);
    [-1.07,1.07].forEach(x=>this.rod([x,.65,-.25],[x,.65,.27],.035,metal,bench));
    this.plant(4.65,-.3);this.plant(-4.68,4.35);
    const desk=this.box(.6,.83,.45,'#d4cab6',s,[4.25,.41,1.75]);const board=this.sign('乘梯协助',1,.4,s,[4.12,1.23,1.85],'#f0ede3','#4e635c',75);board.rotation.y=-.25;
    // A reserved clear door zone, not an assigned wheelchair slot.
    for(let x=-3.55;x<-.55;x+=.35)this.box(.19,.007,.025,'#b99564',s,[x,.018,-.55]);
    const floorText=this.sign('请留出下客通道',2.5,.45,s,[-2.1,.022,.01],'#e9e5d9','#9a917e',61);floorText.rotation.x=-Math.PI/2;
  }
  plant(x,z){this.mesh(new THREE.CylinderGeometry(.28,.22,.55,24),'#d1c9b7',this.scene,[x,.27,z]);for(let i=0;i<12;i++){const a=i*2.4,y=.85+(i%4)*.14;this.rod([x,.48,z],[x+Math.cos(a)*.32,y,z+Math.sin(a)*.32],.014,'#668164',this.scene);let leaf=this.ball(.16,i%2?'#718d6e':'#527761',this.scene,[x+Math.cos(a)*.34,y,z+Math.sin(a)*.34],[.48,1.5,.7]);leaf.rotation.z=.5*Math.cos(a);}}
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
  addLabel(text,key){let el=document.createElement('span');el.className='actor-label '+(key==='other'?'other':'');el.textContent=text;document.getElementById('actor-labels').append(el);this.labels.push({key,el});}
  setFocus(key){this.focus=key;this.labels.forEach(l=>l.el.classList.toggle('focus',l.key===key));this.setCamera(this.view)}
  reset(){this.animation=null;this.paused=false;this.door=0;this.closeView=false;
    const poses={lin:[-3.05,1.65,Math.PI],other:[-.83,1.18,Math.PI],p0:[.35,3.1,Math.PI],p1:[1.1,3.7,Math.PI],p2:[1.9,2.65,Math.PI],p3:[2.65,3.3,Math.PI],exit:[-2.15,-2.7,0],nurse:[4,1.1,-1.2]};
    for(const [key,[x,z,yaw]] of Object.entries(poses)){let a=this.actors[key];a.position.set(x,0,z);a.rotation.y=yaw;a.visible=true;a.userData.legs?.forEach(l=>l.rotation.x=0);}
    this.setFocus('lin');this.onActivity?.(false);this.render();
  }
  snapshot(){return Object.fromEntries(Object.entries(this.actors).map(([k,a])=>[k,{x:a.position.x,z:a.position.z,yaw:a.rotation.y,visible:a.visible}]))}
  resize(){const w=this.canvas.clientWidth,h=this.canvas.clientHeight;if(!w||!h)return;this.renderer.setSize(w,h,false);this.camera.aspect=w/h;this.camera.updateProjectionMatrix();this.setCamera(this.view)}
  setCamera(view){this.view=view;const aspect=this.canvas.clientWidth/this.canvas.clientHeight;
    if(view==='top'){this.camera.position.set(0,13,.9);this.camera.lookAt(-.6,0,-.2);this.camera.fov=46;}
    else if(view==='seated'){const a=this.actors[this.focus];this.camera.position.set(a.position.x+.35,1.7,a.position.z+1.6);this.camera.lookAt(-2.1,1.4,-2);this.camera.fov=67;}
    else if(this.closeView){this.camera.position.set(aspect<1?4.1:3.3,5.3,8.1);this.camera.lookAt(-1.6,1,-.85);this.camera.fov=43;}
    else{const extra=aspect<1?1.5:0;this.camera.position.set(5.5+extra,6.6+extra,10.1+extra);this.camera.lookAt(-.4,.9,-.1);this.camera.fov=43;}
    this.camera.updateProjectionMatrix();this.render();
  }
  play(segments,done,onStep){this.animation={segments,index:0,elapsed:0,start:this.snapshot(),startDoor:this.door,done,onStep};this.paused=false;this.onActivity?.(true);this.enterSegment();}
  enterSegment(){let a=this.animation,s=a.segments[a.index];a.onStep?.(s.note||'');if(s.visible)for(const [k,v] of Object.entries(s.visible))this.actors[k].visible=v;}
  togglePause(){if(!this.animation)return;this.paused=!this.paused;return this.paused;}
  tick(dt){if(this.animation&&!this.paused){const a=this.animation,s=a.segments[a.index];a.elapsed+=dt*this.speed*(this.reduced?2:1);const f=Math.min(a.elapsed/s.duration,1),ease=f*f*(3-2*f);
      for(const [key,goal] of Object.entries(s.poses||{})){const obj=this.actors[key],st=a.start[key],before=obj.position.clone();obj.position.x=st.x+(goal.x-st.x)*ease;obj.position.z=st.z+(goal.z-st.z)*ease;if(goal.yaw!==undefined){let delta=Math.atan2(Math.sin(goal.yaw-st.yaw),Math.cos(goal.yaw-st.yaw));obj.rotation.y=st.yaw+delta*ease;}
        const distance=obj.position.distanceTo(before);obj.userData.wheels?.forEach(w=>w.rotation.x+=distance/.25);if(!obj.userData.seated){obj.userData.legs?.forEach((l,i)=>l.rotation.x=distance>.00001?Math.sin(a.elapsed*8+i*Math.PI)*.28:0);obj.userData.arms?.forEach((l,i)=>l.rotation.x=distance>.00001?Math.sin(a.elapsed*8+i*Math.PI+Math.PI)*.13:0);}}
      if(s.door!==undefined)this.door=a.startDoor+(s.door-a.startDoor)*ease;
      if(f>=1){Object.values(this.actors).forEach(o=>{o.userData.legs?.forEach(l=>l.rotation.x=0);o.userData.arms?.forEach(l=>l.rotation.x=0)});a.index++;if(a.index>=a.segments.length){this.animation=null;this.onActivity?.(false);a.done?.();}else{a.elapsed=0;a.start=this.snapshot();a.startDoor=this.door;this.enterSegment();}}
    }
    this.doors[0].position.x=-2.9-this.door*1.55;this.doors[1].position.x=-1.35+this.door*1.55;
    if(this.view==='seated'){const p=this.actors[this.focus].position;this.camera.position.set(p.x+.35,1.7,p.z+1.6);this.camera.lookAt(-2.1,1.4,-2);}
    this.render();
  }
  render(){if(!this.renderer)return;this.renderer.render(this.scene,this.camera);for(const {key,el} of this.labels){const actor=this.actors[key];if(!actor)continue;const p=actor.position.clone().add(new THREE.Vector3(0,1.8,0)).project(this.camera);el.style.left=(p.x*.5+.5)*this.canvas.clientWidth+'px';el.style.top=(-p.y*.5+.5)*this.canvas.clientHeight+'px';el.hidden=!actor.visible||this.view==='seated'||Math.abs(p.x)>.95||Math.abs(p.y)>.95;}}
  firstRide(){const p=(x,z,yaw=Math.PI)=>({x,z,yaw});return[
    {duration:1,door:1,note:'电梯到达。两把轮椅停在门侧，先让里面的人出来。'},
    {duration:1.7,poses:{exit:p(-2.1,1.4,0)},note:'先下后上，门口暂时不能通行。'},
    {duration:1.1,poses:{exit:p(-4,2.8,-1),p0:p(-2.05,-1.6)},note:'后来的人走得更快，先进入电梯。'},
    {duration:1.1,poses:{p0:p(-3.03,-3.3),p1:p(-2.05,-1.6)},note:'小椅提醒大家留出位置。'},
    {duration:1.1,poses:{p1:p(-2.22,-3.3),p2:p(-2.05,-1.6),lin:p(-2.9,1.43)},note:'有人经过轮椅前方，小椅停下。'},
    {duration:1.1,poses:{p2:p(-1.2,-2.65),p3:p(-2.05,-1.6)},note:'电梯余量不足，两把轮椅都留在门外。'},
    {duration:.7,poses:{p3:p(-2.2,-1.96)}},
    {duration:1,door:0,note:'第一班离开，两位乘客各错过一班。'}];}
  prepareSecond(){this.actors.exit.visible=false;for(let i=0;i<4;i++){const a=this.actors['p'+i];a.position.set(.35+i*.72,0,2.6+(i%2)*.5);a.visible=true;}this.actors.nurse.position.set(-4.25,0,-.05);this.actors.nurse.rotation.y=1.3;this.render();}
  secondRide(){const p=(x,z,yaw=Math.PI)=>({x,z,yaw});return[
    {duration:1,door:1,note:'下一班到达，工作人员引导乘客上梯。'},
    {duration:1.5,poses:{other:p(-2.2,-1.6)},note:'另一位乘客先进入。'},
    {duration:1.1,poses:{other:p(-3.03,-2.55),p0:p(-2.05,-1.6)},note:'林岚还在门外，其他人也开始进入。'},
    {duration:1.1,poses:{p0:p(-2.1,-3.25),p1:p(-2,-1.6),lin:p(-2.6,.67)},note:'余量又不够容纳林岚的轮椅。'},
    {duration:1.1,poses:{p1:p(-1.15,-2.7),p2:p(-2,-1.6)},note:'系统向另一把轮椅发出退出请求。'},
    {duration:.7,poses:{p2:p(-1.25,-1.85)},visible:{p3:false},note:'历史偏好被调用，对方设备自动回复接受。'},
    {duration:.75,poses:{other:p(-3.03,-2.37,Math.PI*.55)},note:'轮椅刚转向出口，乘坐者按停了。'},
    {duration:.15,note:'现在暂停在决定发生的这一刻。是否继续这个安排？'}];}
  finishRide(yieldOther){const p=(x,z,yaw=Math.PI)=>({x,z,yaw});let seq=[];
    if(yieldOther)seq=[{duration:1.1,poses:{other:p(-2.4,-1.6,0)},note:'另一位乘客的轮椅转向出口。'},{duration:1.3,poses:{other:p(-2.1,.25,0)},note:'他退出电梯，林岚暂时停在门外。'},{duration:1.2,poses:{other:p(-.65,1.4,.8)},note:'对方离开门区后，林岚才开始移动。'},{duration:1.7,poses:{lin:p(-2.1,-1.65)},note:'林岚进入电梯。'},{duration:1,poses:{lin:p(-3.02,-2.5)},note:'同一班电梯，等待落到了另一位乘客身上。'}];
    else seq=[{duration:.8,poses:{other:p(-3.03,-2.55,Math.PI)},note:'退出请求已撤回。另一位乘客留在轿厢内。'},{duration:1.25,poses:{lin:p(-3.05,1.65,Math.PI),nurse:p(-4,.7,1.1)},note:'林岚退到门侧，工作人员联系门诊。'}];
    seq.push({duration:1,door:0,note:'门区清空，电梯离开。'});
    seq.push({duration:.15,visible:yieldOther?{lin:false,p0:false,p1:false,p2:false}:{other:false,p0:false,p1:false,p2:false},note:yieldOther?'林岚上楼，另一位乘客继续等。':'另一位乘客上楼，林岚继续等。'});return seq;
  }
  prepareRepeat(person){this.reset();this.actors.exit.visible=false;this.setFocus(person);for(let i=0;i<4;i++)this.actors['p'+i].visible=false;this.actors.nurse.visible=false;this.render();}
  yieldOnce(person){let a=this.actors[person];return[{duration:1.7,poses:{[person]:{x:person==='lin'?-3.85:.2,z:2.45,yaw:Math.PI}},note:'轮椅移到一旁，为其他乘客留出通道。'}];}
  undoRepeat(person){return[{duration:1.1,poses:{[person]:{x:person==='lin'?-3.05:-.83,z:person==='lin'?1.65:1.18,yaw:Math.PI}},note:'默认安排已撤销，轮椅回到原来的等候位置。'}];}
}
window.ElevatorStage=ElevatorStage;
