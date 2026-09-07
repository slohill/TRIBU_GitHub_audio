from pathlib import Path

# ---------- server ----------
p=Path('server/server.js'); s=p.read_text()
anchor="const FACTION_CAP = [3,3,2];\n"
insert="""const FACTION_CAP = [3,3,2];
const FACTION_DEF = [1,1,3];
const LAND_NEIGHBORS = {
  A1:['A2'],A2:['A1'],A3:['A4'],A4:['A3'],A5:['B1','B2'],
  B1:['A5','B2'],B2:['A5','B1'],B3:['B4'],B4:['B3'],B5:[],
  C1:['C2','C4'],C2:['C1','C3','C4'],C3:['C2','C4','E1','F1'],C4:['C1','C2','C3','C5','E1'],C5:['C4','E1','E2','D1'],
  D1:['C5','E2','D2','D5'],D2:['D1','D3','D4','D5'],D3:['D2','D4'],D4:['D2','D3','D5','G1'],D5:['D1','D2','D4','E2','E3','G1'],
  E1:['C3','C4','C5','E2','E4','F1','F2'],E2:['E1','E3','E4','C5','D1','D5'],E3:['E2','E4','E5','D5','G1','G2'],E4:['E1','E2','E3','E5','F2','F4'],E5:['E3','E4','F4','F5','G2','G3'],
  F1:['C3','E1','F2','F3'],F2:['E1','E4','F1','F3','F4'],F3:['F1','F2','F4'],F4:['F2','F3','F5','E4','E5'],F5:['E5','F4','G3'],
  G1:['D4','D5','E3','G2'],G2:['G1','G3','G4','E3','E5'],G3:['G2','G4','G5','F5','E5'],G4:['G2','G3','G5'],G5:['G3','G4'],
  H1:['H2','H3'],H2:['H1','H3','H5'],H3:['H1','H2','H4','H5'],H4:['H3','H5','I1'],H5:['H2','H3','H4','I1','I2'],
  I1:['H4','H5','I2','I3'],I2:['H5','I1','I3','I4'],I3:['I1','I2','I4','I5'],I4:['I2','I3','I5'],I5:['I3','I4']
};
const SEA_NEIGHBORS={U:['W','V'],V:['U','Z'],W:['U','X','Y'],X:['W','Z','Y'],Y:['W','X','Z'],Z:['V','X','Y']};
const PORTS={U:['A1','A3','A5','C1'],V:['B2','B4','B5','F1','F5'],W:['C5','D1'],X:['D4','G1','H4'],Y:['H5','I2'],Z:['G5','I5']};
"""
assert anchor in s
s=s.replace(anchor,insert,1)

anchor="function unitCapFor(game, playerIndex) {\n  const faction=game.players[playerIndex].faction;\n  return ownedRegionCount(game,playerIndex)*(FACTION_CAP[faction]||2);\n}\n"
insert=anchor+"""function isSeaId(id){ return Object.prototype.hasOwnProperty.call(SEA_NEIGHBORS,id); }
function physicalNeighbors(id){ return isSeaId(id) ? [...(SEA_NEIGHBORS[id]||[]),...(PORTS[id]||[])] : [...(LAND_NEIGHBORS[id]||[]),...Object.entries(PORTS).filter(([,rs])=>rs.includes(id)).map(([sea])=>sea)]; }
function beginAuthoritativePlay(game,index){
  game.phase='play';game.movePool={};game.destinationUseCount={};game.attacked=[];
  Object.entries(game.board).forEach(([r,c])=>{game.movePool[r]=c.owner===index?c.units:0});
  Object.entries(game.sea||{}).forEach(([id,c])=>{game.movePool[id]=(c.fleets&&c.fleets[index])||0});
}
function gameRand(game){
  let a=(game.rngState>>>0)||0x6d2b79f5;a=(a+0x6D2B79F5)>>>0;game.rngState=a;
  let t=a;t=Math.imul(t^(t>>>15),t|1);t^=t+Math.imul(t^(t>>>7),t|61);return ((t^(t>>>14))>>>0)/4294967296;
}
function gameDie(game){return 1+Math.floor(gameRand(game)*6)}
function currentOracleName(game){return game.oracleActive===null?null:['Canicule','En quête de destruction','Givre mortel','Tempête de sable','Tempête en mer','Vague de froid'][game.oracleActive]||null}
function refillOracle(game){if(game.oracleDeck.length)return;if(!game.oracleDiscard.length)return;game.oracleDeck=shuffle(game.oracleDiscard.splice(0),()=>gameRand(game))}
function activateNextOracle(game){
  if(game.oracleActive!==null)game.oracleDiscard.push(game.oracleActive);refillOracle(game);
  const id=game.oracleDeck.pop();if(id!==undefined)game.oracleActive=id;return id;
}
function destroyAtDragon(game){
  const id=game.dragon;
  if(isSeaId(id)){if(game.sea[id])game.sea[id].fleets={};return}
  const c=game.board[id];if(!c)return;c.owner=null;c.units=0;c.hostile=c.originalHostile;c.building=null;
}
function advanceAuthoritativeTurn(room){
  const game=room.game;if(!game)return;
  game.active=(game.active+1)%game.players.length;if(game.active===0)game.turn++;
  game.phase='start';game.movePool={};game.destinationUseCount={};game.attacked=[];game.recruitSnapshot=null;game.lastRoll=null;game.revision++;
  emitGame(room);scheduleBotTurn(room);
}
function resolveOracleRoll(room){
  const game=room.game,n=gameDie(game);game.lastRoll=n;
  const destruction=n===6||(currentOracleName(game)==='En quête de destruction'&&(n===4||n===5));
  if(n===1)activateNextOracle(game);
  if(destruction)destroyAtDragon(game);
  advanceAuthoritativeTurn(room);
  return n;
}
function resolveBasicLandBattle(game,index,target,n){
  const c=game.board[target],hostile=!!c.hostile,defender=hostile?null:c.owner;
  const d=hostile?5:(defender===null?0:c.units*(FACTION_DEF[game.players[defender].faction]||1));
  const a=n;
  let result='defense',survivors=0;
  if(a>d){
    survivors=Math.min(n,a-d);if(d>=10)game.players[index].pvPermanent=(game.players[index].pvPermanent||0)+1;
    c.owner=index;c.units=survivors;c.hostile=false;result='attack';
  }else if(hostile){c.owner=null;c.units=0;c.hostile=true;survivors=0}
  else if(defender!==null){
    if(a>=10)game.players[defender].pvPermanent=(game.players[defender].pvPermanent||0)+1;
    const coeff=FACTION_DEF[game.players[defender].faction]||1;
    survivors=a===d?1:Math.max(1,Math.min(c.units,Math.ceil((d-a)/coeff)));c.units=survivors;
  }
  return {kind:'battle',target,attacker:index,defender,hostile,attack:a,defense:d,result,survivors};
}
function scheduleBotTurn(room){
  if(!room||!room.game||room.game.status!=='playing')return;
  const game=room.game,pl=game.players[game.active];if(!pl||!pl.bot)return;
  clearTimeout(room.botTimer);room.botTimer=setTimeout(()=>runBotTurn(room),650);
}
function runBotTurn(room){
  const game=room.game;if(!game||game.status!=='playing'||!game.players[game.active]||!game.players[game.active].bot)return;
  const i=game.active;
  if(game.phase==='start'){drawCards(game,i,2);beginAuthoritativePlay(game,i);game.revision++;emitGame(room);return scheduleBotTurn(room)}
  if(game.phase==='play'){game.phase='oracleMove';game.revision++;emitGame(room);return scheduleBotTurn(room)}
  if(game.phase==='oracleMove'){
    const choices=physicalNeighbors(game.dragon);if(choices.length)game.dragon=choices[Math.floor(gameRand(game)*choices.length)];
    game.phase='oracleRoll';game.revision++;emitGame(room);return scheduleBotTurn(room);
  }
  if(game.phase==='oracleRoll'){resolveOracleRoll(room);return}
}
"""
assert anchor in s
s=s.replace(anchor,insert,1)

# public game additions
s=s.replace("    dragon: game.dragon,\n", "    dragon: game.dragon,\n    sea: game.sea,\n    oracleActive: game.oracleActive,\n    oracleNext: game.oracleDeck.length ? game.oracleDeck[game.oracleDeck.length-1] : null,\n    lastRoll: game.lastRoll,\n    play: game.status==='playing' ? { movePool: game.active===youIndex ? {...(game.movePool||{})} : {}, destinationUseCount: {...(game.destinationUseCount||{})}, attacked: [...(game.attacked||[])], lastEvent: game.lastEvent||null } : null,\n",1)

# start play after setup
s=s.replace("  game.phase = 'start';\n  game.turn = 1;\n  game.active = 0;\n", "  game.phase = 'start';\n  game.turn = 1;\n  game.active = 0;\n  game.movePool = {}; game.destinationUseCount = {}; game.attacked = []; game.lastEvent=null; game.lastRoll=null;\n",1)

# game initial state
s=s.replace("    dragon: 'E4',\n    board: makeBoard(),\n", "    dragon: 'E4',\n    board: makeBoard(),\n    sea: Object.fromEntries(Object.keys(SEA_NEIGHBORS).map(id=>[id,{fleets:{}}])),\n",1)
s=s.replace("    oracleActive: null,\n    players,\n", "    oracleActive: null,\n    rngState: (room.seed ^ 0x9e3779b9) >>> 0,\n    movePool: {}, destinationUseCount: {}, attacked: [], lastEvent:null, lastRoll:null,\n    players,\n",1)

# draw / harvest / recruitment finish enter play with movement pool
s=s.replace("drawCards(game, index, 2); game.phase = 'play'; game.revision++;", "drawCards(game, index, 2); beginAuthoritativePlay(game,index); game.revision++;")
s=s.replace("game.players[index].gold += ownedRegionCount(game,index)*2; game.phase='play'; game.revision++;", "game.players[index].gold += ownedRegionCount(game,index)*2; beginAuthoritativePlay(game,index); game.revision++;")
s=s.replace("game.recruitSnapshot=null; game.phase='play'; game.revision++;", "game.recruitSnapshot=null; beginAuthoritativePlay(game,index); game.revision++;")

# append authoritative play actions before final rejection
needle="    if (type === 'END_RECRUIT') {\n      if (game.phase !== 'recruit') return rejectGameAction(ack, 'Vous n’êtes pas en phase de recrutement.');\n      game.recruitSnapshot=null; beginAuthoritativePlay(game,index); game.revision++; ack({ok:true}); emitGame(room); return;\n    }\n    return rejectGameAction(ack, 'Action Online pas encore migrée vers le serveur.');"
replacement="""    if (type === 'END_RECRUIT') {
      if (game.phase !== 'recruit') return rejectGameAction(ack, 'Vous n’êtes pas en phase de recrutement.');
      game.recruitSnapshot=null; beginAuthoritativePlay(game,index); game.revision++; ack({ok:true}); emitGame(room); return;
    }
    if(type==='MOVE_LAND'){
      if(game.phase!=='play')return rejectGameAction(ack,'Vous ne pouvez pas déplacer maintenant.');
      const target=String(payload.target||''),tc=game.board[target],raw=payload.sources&&typeof payload.sources==='object'?payload.sources:{};
      if(!tc)return rejectGameAction(ack,'Destination terrestre invalide.');
      const enemy=tc.hostile||(tc.owner!==null&&tc.owner!==index&&tc.units>0);
      if(enemy&&(game.attacked||[]).includes(target))return rejectGameAction(ack,'Cette région a déjà été attaquée ce tour.');
      if(!enemy&&Number((game.destinationUseCount||{})[target]||0)>=1)return rejectGameAction(ack,'Cette région a déjà reçu un déplacement ce tour.');
      const picks=[];let total=0;
      for(const [src,v] of Object.entries(raw)){
        const q=Math.max(0,Math.floor(Number(v)||0));if(!q)continue;
        const sc=game.board[src];if(!sc||sc.owner!==index)return rejectGameAction(ack,'Source de déplacement invalide.');
        if(!(LAND_NEIGHBORS[target]||[]).includes(src))return rejectGameAction(ack,'Une source n’est pas adjacente à la destination.');
        const available=Math.min(sc.units,Number((game.movePool||{})[src]||0));if(q>available)return rejectGameAction(ack,'Pas assez d’unités encore déplaçables sur une source.');
        picks.push([src,q]);total+=q;
      }
      if(total<1)return rejectGameAction(ack,'Sélectionnez au moins une unité.');
      picks.forEach(([src,q])=>{const sc=game.board[src];sc.units-=q;game.movePool[src]=Math.max(0,(game.movePool[src]||0)-q);if(sc.units===0){sc.owner=null;sc.hostile=sc.originalHostile}});
      if(enemy){game.attacked=game.attacked||[];game.attacked.push(target);game.lastEvent=resolveBasicLandBattle(game,index,target,total)}
      else{tc.owner=index;tc.units+=total;tc.hostile=false;game.lastEvent={kind:'move',target,player:index,units:total}}
      game.destinationUseCount=game.destinationUseCount||{};game.destinationUseCount[target]=(game.destinationUseCount[target]||0)+1;
      game.revision++;ack({ok:true,event:game.lastEvent});emitGame(room);return;
    }
    if(type==='END_PLAY'){
      if(game.phase!=='play')return rejectGameAction(ack,'La phase de jeu n’est pas active.');
      game.phase='oracleMove';game.lastEvent={kind:'oracleMove',player:index};game.revision++;ack({ok:true});emitGame(room);return;
    }
    if(type==='DRAGON_MOVE'){
      if(game.phase!=='oracleMove')return rejectGameAction(ack,'Le Dragon ne peut pas être déplacé maintenant.');
      const target=String(payload.target||'');if(!physicalNeighbors(game.dragon).includes(target))return rejectGameAction(ack,'Le Dragon doit être déplacé vers une case voisine.');
      game.dragon=target;game.phase='oracleRoll';game.lastEvent={kind:'dragonMove',target,player:index};game.revision++;ack({ok:true});emitGame(room);return;
    }
    if(type==='ORACLE_ROLL'){
      if(game.phase!=='oracleRoll')return rejectGameAction(ack,'Le dé de l’Oracle ne peut pas être lancé maintenant.');
      const roll=resolveOracleRoll(room);ack({ok:true,roll});return;
    }
    return rejectGameAction(ack, 'Action Online pas encore migrée vers le serveur.');"""
assert needle in s
s=s.replace(needle,replacement,1)
p.write_text(s)

# ---------- client ----------
p=Path('index.html'); s=p.read_text()
# CSS
s=s.replace("@media(max-width:760px){.onlineGameWelcomeCard{font-size:20px;padding:20px}}\n", "@media(max-width:760px){.onlineGameWelcomeCard{font-size:20px;padding:20px}}\n.onlineMoveAvailable{outline:4px solid #46e37a!important;background:#46e37a30!important}.onlineMovePickBadge{position:absolute;left:50%;bottom:-18px;transform:translateX(-50%);z-index:45;background:#111e;color:#fff;border:1px solid #eee;border-radius:10px;padding:1px 6px;font-size:10px;font-weight:900;line-height:1.2;pointer-events:none}.onlineOracleTarget{outline:5px solid #bb5cff!important;background:#bb5cff55!important}\n")
# dataset region in renderMap
old="Object.entries(POS).forEach(([id,xy])=>{const b=document.createElement('button');b.className='spot'+(isSea(id)?' sea':'');b.style.left=xy[0]+'%';b.style.top=xy[1]+'%';"
new="Object.entries(POS).forEach(([id,xy])=>{const b=document.createElement('button');b.className='spot'+(isSea(id)?' sea':'');b.dataset.region=id;b.style.left=xy[0]+'%';b.style.top=xy[1]+'%';"
assert old in s;s=s.replace(old,new,1)
# robust setup feedback
old="const map=$('map');if(!map)return;const ids=Object.keys(POS),spots=[...map.querySelectorAll('.spot')],allowed=active?onlineSetupRegionsFor(state):[];\n ids.forEach((id,i)=>{const spot=spots[i];if(!spot)return;"
new="const map=$('map');if(!map)return;const ids=Object.keys(POS),allowed=active?onlineSetupRegionsFor(state):[];\n ids.forEach(id=>{const spot=map.querySelector('.spot[data-region=\"'+id+'\"]');if(!spot)return;"
assert old in s;s=s.replace(old,new,1)
# movement state/functions after online resume refresh
anchor="function onlineResumeRefresh(){const v=onlineResumeRead(),b=$('onlineResumeRoom'),h=$('onlineResumeHint');if(!b||!h)return;b.classList.toggle('hidden',!v);h.classList.toggle('hidden',!v);if(v){b.textContent='Partie en cours';h.textContent=(v.pseudo||'Joueur')+' · '+v.code}}\n"
insert=anchor+"""let onlineMoveDraft={target:null,picks:{}};
function onlineResetMoveDraft(){onlineMoveDraft={target:null,picks:{}}}
function onlineLandNeighbors(id){return R[id]?R[id][3].slice():[]}
function onlineMovePool(id){return Number(onlineGameState&&onlineGameState.play&&onlineGameState.play.movePool&&onlineGameState.play.movePool[id]||0)}
function onlineTargetEnemy(id){const c=onlineGameState&&onlineGameState.board&&onlineGameState.board[id];return !!(c&&(c.hostile||(c.owner!==null&&c.owner!==onlineGameState.youIndex&&c.units>0)))}
function onlineLegalMoveSources(target){
 const st=onlineGameState;if(!st||st.phase!=='play'||st.active!==st.youIndex||!R[target])return[];
 const enemy=onlineTargetEnemy(target),play=st.play||{};
 if(enemy&&(play.attacked||[]).includes(target))return[];
 if(!enemy&&Number((play.destinationUseCount||{})[target]||0)>=1)return[];
 return onlineLandNeighbors(target).filter(src=>{const c=st.board[src];return c&&c.owner===st.youIndex&&onlineMovePool(src)>0});
}
function onlineMoveSelected(){return Object.values(onlineMoveDraft.picks||{}).reduce((a,b)=>a+(Number(b)||0),0)}
function onlineMoveClick(id){
 if(!onlineGameState||onlineGameState.phase!=='play'||onlineGameState.active!==onlineGameState.youIndex)return;
 const legal=onlineMoveDraft.target?onlineLegalMoveSources(onlineMoveDraft.target):[];
 if(onlineMoveDraft.target&&legal.includes(id)){
   const max=onlineMovePool(id),cur=Number(onlineMoveDraft.picks[id]||0);const next=cur>=max?0:cur+1;
   if(next)onlineMoveDraft.picks[id]=next;else delete onlineMoveDraft.picks[id];onlineRefreshPlayUi();return;
 }
 const src=onlineLegalMoveSources(id);if(!src.length)return;
 onlineMoveDraft={target:id,picks:{}};onlineRefreshPlayUi();
}
function onlineCommitMove(){
 if(!onlineMoveDraft.target||onlineMoveSelected()<1)return;
 const target=onlineMoveDraft.target,sources={...onlineMoveDraft.picks};onlineResetMoveDraft();
 onlineGameAction('MOVE_LAND',{target,sources});
}
function onlinePhysicalNeighbors(id){return isSea(id)?[...(SEA[id]||[]),...(PORTS[id]||[])]:[...(R[id]?R[id][3]:[]),...(R[id]?R[id][4]:[])]}
function onlineDragonClick(id){
 const st=onlineGameState;if(!st||st.phase!=='oracleMove'||st.active!==st.youIndex)return;
 if(!onlinePhysicalNeighbors(st.dragon).includes(id))return;onlineGameAction('DRAGON_MOVE',{target:id});
}
function onlineRefreshPlayUi(){
 const st=onlineGameState,map=$('map'),srcBox=$('sources'),hint=$('hint');if(!st||!map)return;
 map.querySelectorAll('.spot').forEach(x=>{x.classList.remove('onlineMoveAvailable','dest','src','onlineOracleTarget');x.querySelectorAll('.onlineMovePickBadge').forEach(b=>b.remove())});
 if(st.status!=='playing'||st.active!==st.youIndex){if(srcBox)srcBox.innerHTML='';return}
 if(st.phase==='play'){
   Object.keys(R).forEach(id=>{if(onlineLegalMoveSources(id).length){const sp=map.querySelector('.spot[data-region=\"'+id+'\"]');if(sp)sp.classList.add('onlineMoveAvailable')}});
   if(onlineMoveDraft.target){
     const t=map.querySelector('.spot[data-region=\"'+onlineMoveDraft.target+'\"]');if(t)t.classList.add('dest');
     onlineLegalMoveSources(onlineMoveDraft.target).forEach(id=>{const sp=map.querySelector('.spot[data-region=\"'+id+'\"]');if(!sp)return;sp.classList.add('src');const q=Number(onlineMoveDraft.picks[id]||0);if(q){const b=document.createElement('span');b.className='onlineMovePickBadge';b.textContent=q+' sélectionnée'+(q>1?'s':'');sp.appendChild(b)}});
     if(hint)hint.textContent='Cliquez sur une région source en jaune pour sélectionner les unités (clics successifs), puis validez.';
     if(srcBox)srcBox.innerHTML='<div class="note">Unités sélectionnées : <b>'+onlineMoveSelected()+'</b></div><div class="row"><button id="onlineMoveConfirm" '+(onlineMoveSelected()?'':'disabled')+'>Valider le déplacement</button><button id="onlineMoveCancel">Annuler</button></div>';
     const ok=$('onlineMoveConfirm'),no=$('onlineMoveCancel');if(ok)ok.onclick=onlineCommitMove;if(no)no.onclick=()=>{onlineResetMoveDraft();onlineRefreshPlayUi()};
   }else{if(hint)hint.textContent='Cliquez sur une destination en surbrillance verte.';if(srcBox)srcBox.innerHTML='<div class="note">Déplacements autoritaires : choisissez d’abord la destination sur la carte.</div>'}
 }
 if(st.phase==='oracleMove'){
   onlinePhysicalNeighbors(st.dragon).forEach(id=>{const sp=map.querySelector('.spot[data-region=\"'+id+'\"]');if(sp)sp.classList.add('onlineOracleTarget')});
 }
}
"""
assert anchor in s;s=s.replace(anchor,insert,1)
# apply sea/oracle state to display
s=s.replace("G.active=Number.isInteger(state.active)?state.active:0;G.turn=state.turn||0;G.phase=state.phase||'setup';G.dragon=state.dragon||'E4';G.victoryTarget=state.victoryPoints||3;", "G.active=Number.isInteger(state.active)?state.active:0;G.turn=state.turn||0;G.phase=state.phase||'setup';G.dragon=state.dragon||'E4';G.victoryTarget=state.victoryPoints||3;G.oracleActive=state.oracleActive===null?null:state.oracleActive;",1)
# clickSpot online route
old="if(G&&G.online&&onlineGameState){if(onlineGameState.status==='setup')onlineSetupRegionClick(id);else if(onlineGameState.status==='playing'&&onlineGameState.phase==='recruit'&&onlineGameState.active===onlineGameState.youIndex)recruitAt(id);return}"
new="if(G&&G.online&&onlineGameState){if(onlineGameState.status==='setup')onlineSetupRegionClick(id);else if(onlineGameState.status==='playing'&&onlineGameState.phase==='recruit'&&onlineGameState.active===onlineGameState.youIndex)recruitAt(id);else if(onlineGameState.status==='playing'&&onlineGameState.phase==='play'&&onlineGameState.active===onlineGameState.youIndex)onlineMoveClick(id);else if(onlineGameState.status==='playing'&&onlineGameState.phase==='oracleMove'&&onlineGameState.active===onlineGameState.youIndex)onlineDragonClick(id);return}"
assert old in s;s=s.replace(old,new,1)
# online lock controls rewrite targeted block
old="const mine=onlineGameState.active===onlineGameState.youIndex&&onlineGameState.status==='playing'&&!onlineWelcomeActive,start=mine&&onlineGameState.phase==='start',recruiting=mine&&onlineGameState.phase==='recruit';\n $('startTurn').classList.toggle('hidden',!start);\n $('draw').disabled=!start;$('harvest').disabled=!start;$('recruit').disabled=!start;\n $('endRecruit').disabled=!recruiting;const rr=$('resetRecruit');if(rr)rr.disabled=!recruiting;\n ['toOracle','roll'].forEach(id=>{const el=$(id);if(el)el.disabled=true});"
new="const mine=onlineGameState.active===onlineGameState.youIndex&&onlineGameState.status==='playing'&&!onlineWelcomeActive,start=mine&&onlineGameState.phase==='start',recruiting=mine&&onlineGameState.phase==='recruit',playing=mine&&onlineGameState.phase==='play',oracleMove=mine&&onlineGameState.phase==='oracleMove',oracleRoll=mine&&onlineGameState.phase==='oracleRoll';\n $('startTurn').classList.toggle('hidden',!start);\n $('draw').disabled=!start;$('harvest').disabled=!start;$('recruit').disabled=!start;\n $('endRecruit').disabled=!recruiting;const rr=$('resetRecruit');if(rr)rr.disabled=!recruiting;\n $('toOracle').disabled=!playing;$('roll').disabled=!oracleRoll;"
assert old in s;s=s.replace(old,new,1)
s=s.replace("const n=$('status');if(n)n.innerHTML+='<div class=\"botNotice\">🌐 Online autoritaire — début de tour synchronisé par le serveur.</div>';", "const n=$('status');if(n)n.innerHTML+='<div class=\"botNotice\">🌐 Online autoritaire — tour, déplacements et Oracle synchronisés par le serveur.</div>';onlineRefreshPlayUi();")
# reset draft when state phase changes / after state apply
s=s.replace("function applyOnlineGameState(state){\n const wasSetup=onlineGameState&&onlineGameState.status==='setup';onlineGameState=state;", "function applyOnlineGameState(state){\n const wasSetup=onlineGameState&&onlineGameState.status==='setup',oldPhase=onlineGameState&&onlineGameState.phase;onlineGameState=state;if(oldPhase!==state.phase||state.active!==G?.active)onlineResetMoveDraft();",1)
# toOracle and roll online entry
s=s.replace("function toOracle(){\n if(battle||caravanState", "function toOracle(){\n if(G&&G.online)return onlineGameAction('END_PLAY');\n if(battle||caravanState",1)
s=s.replace("function roll(){\n // Un seul lancer Oracle", "function roll(){\n if(G&&G.online)return onlineGameAction('ORACLE_ROLL');\n // Un seul lancer Oracle",1)
p.write_text(s)
