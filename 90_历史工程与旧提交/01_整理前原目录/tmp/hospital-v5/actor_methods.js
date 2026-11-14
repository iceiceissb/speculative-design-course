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
