/* v1.1: deterministic narrative state; no sensors, network, storage or robot control. */
(() => {
  const clone = value => JSON.parse(JSON.stringify(value));
  const RULES = {
    A: {name:'每次主动问',benefit:'轮椅先把原因与选择说出来，较少依赖使用者主动寻找入口。',cost:'每次停顿都开启一次确认对话，可能打断当下的生活。'},
    B: {name:'由我发起',benefit:'先给出安静的停止提示，把何时处理留给使用者。',cost:'使用者需要主动打开原因与选项；有人可能因此不知道下一步。'}
  };
  const FIXTURES = {
    obscured:{name:'遮挡仍在',detail:'现场复核后仍不能确认通行空间；两条规则都不能直接通过。'},
    clear:{name:'门扇展开后可确认',detail:'现场复核可确认当前通行条件；两条规则都可由本人确认继续。'}
  };
  const ROUTES={detour:{name:'绕行',minutes:10},help:{name:'现场协助',minutes:9},wait:{name:'维修方复核',minutes:19},pass:{name:'确认通过',minutes:1},cancel:{name:'取消出行',minutes:0}};
  function create(){return {version:'v1.1',step:'intro',tab:'experience',fixture:'obscured',pair:null,trip:null,result:null,runs:[],serial:0,pairSerial:0,memory:{rule:null,proof:null},petition:null,reflection:'',perspective:'user',pausedStep:null,notice:'',draft:{rule:'',keepRule:false,keepProof:false},nextDraft:{kind:'same',rule:''},logs:[]};}
  function proofMatches(state,body,door,fixture){const p=state.memory.proof;return !!p&&p.body===body&&p.door===door&&fixture==='clear';}
  function newTrip(state,options){
    if(!RULES[options.rule])throw Error('必须明确选择本次提问规则');
    const {rule,fixture,body,door,origin,allowReuse}=options;
    state.trip={id:++state.serial,rule,fixture,body,door,origin,pairId:origin==='pair'?state.pair.id:null,elapsed:0,checked:false,reviewCost:0,allowReuse,proofReused:!!allowReuse&&proofMatches(state,body,door,fixture),prompts:rule==='A'?1:0,initiations:0,opened:false,holdCount:0};
    state.result=null;state.step='arrival';state.tab='experience';state.notice='';state.perspective='user';
    state.logs.push({event:'start',trip:state.trip.id,rule,fixture,body,door,origin});
  }
  function beginPair(state,rule){state.pair={id:++state.pairSerial,fixture:state.fixture,body:'B2',door:1};newTrip(state,{...state.pair,rule,origin:'pair',allowReuse:false});}
  function counterpart(state){if(!state.pair||state.trip?.origin!=='pair')throw Error('边界演示不能冒充同条件对照');newTrip(state,{...state.pair,rule:state.trip.rule==='A'?'B':'A',origin:'pair',allowReuse:false});}
  function openChoices(state){const t=state.trip;if(!t)throw Error('出行尚未开始');if(!t.opened&&t.rule==='B')t.initiations++;t.opened=true;state.step='choice';}
  function hold(state){state.trip.elapsed+=2;state.trip.holdCount++;state.step='arrival';state.notice='已保持暂停 2 分钟（剧情时间），不会自动改成绕行。';}
  function canPass(state){const t=state.trip;return !!t&&t.fixture==='clear'&&(t.checked||t.proofReused);}
  function review(state){const t=state.trip;if(!t.checked){t.elapsed+=3;t.reviewCost+=3;t.checked=true;}state.step='review';}
  function finish(state,route){const t=state.trip;if(!t||!ROUTES[route])throw Error('不存在的路径');if(state.result)throw Error('本次结果已封存');if(route==='pass'&&!canPass(state))throw Error('当前条件未确认，不能通过');
    t.elapsed+=ROUTES[route].minutes;
    const result=clone({...t,route,routeName:ROUTES[route].name,arrival:route==='cancel'?null:t.elapsed-6,petition:state.petition?.status||'未提出'});
    state.result=result;state.runs.push(clone(result));state.logs.push({event:'finish',trip:t.id,route,minutes:t.elapsed});state.step='outcome';
  }
  function feedback(state){state.draft={rule:state.trip.rule,keepRule:false,keepProof:false};state.step='feedback';}
  function save(state,none=false){const t=state.trip,d=state.draft;state.memory.rule=!none&&d.keepRule?d.rule:null;
    state.memory.proof=!none&&d.keepProof&&canPass(state)?{body:t.body,door:t.door,scope:'活动室门口',checkedInTrip:t.id}:null;
    state.nextDraft={kind:'same',rule:state.memory.rule||''};state.step='next';state.notice=none?'本轮不保留任何演示记录。':'已按勾选范围更新会话记录；没有上传。';
  }
  function beginNext(state){const t=state.trip,n=state.nextDraft;let body=t.body,door=t.door,fixture=t.fixture;if(n.kind==='body')body='B'+(Number(body.slice(1))+1);if(n.kind==='door'){door++;fixture='obscured';}
    newTrip(state,{rule:n.rule,fixture,body,door,origin:'next',allowReuse:true});
  }
  function revoke(state,scope){if(scope==='rule'||scope==='all')state.memory.rule=null;if(scope==='proof'||scope==='all')state.memory.proof=null;state.nextDraft.rule=state.memory.rule||'';state.notice='所选记录已撤回；后续出行按剩余记录处理。';}
  function pause(state){if(state.step==='paused')return;state.pausedStep=state.step;state.step='paused';}
  function resume(state){state.step=state.pausedStep||'arrival';state.pausedStep=null;}
  function submitPetition(state,text){const message=String(text||'').trim().slice(0,800);if(!message)return false;state.petition={text:message,status:'已记录，未处理',automaticChange:false};state.logs.push({event:'petition',status:state.petition.status});return true;}
  function exportData(state){return clone({project:'这一次，轮椅该听谁的？',version:state.version,nature:'虚构情境中的网页演示；非用户研究数据、非真实机器人试验',rules:RULES,fixtureDefinitions:FIXTURES,runs:state.runs,currentMemory:state.memory,petition:state.petition,reflection:state.reflection,events:state.logs});}
  window.WheelchairModel={RULES,FIXTURES,ROUTES,create,beginPair,counterpart,openChoices,hold,canPass,review,finish,feedback,save,beginNext,revoke,pause,resume,submitPetition,exportData};
})();
