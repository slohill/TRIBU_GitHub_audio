from pathlib import Path

p = Path('index.html')
s = p.read_text(encoding='utf-8')

def rep(old, new, label):
    global s
    if old not in s:
        raise SystemExit(f'Motif introuvable: {label}')
    s = s.replace(old, new, 1)

rep(
"let onlineSelectedMode=null,onlineReadyState=false,onlineSocket=null,onlineRoom=null;",
"let onlineSelectedMode=null,onlineReadyState=false,onlineSocket=null,onlineRoom=null,onlineGameState=null,onlineSetupSelectedRegions=[];",
"variables online"
)

old_launch = '''function launchOnlineRoom(room){
 if(!room||room.seed===null||room.seed===undefined)return onlineError(new Error('Graine de partie absente. Attendez le redéploiement du serveur Render.'));
 onlineRoom=room;onlineSelectedMode=room.mode;
 const mode=room.mode==='2v3-online'?'2v3':room.mode;
 $('gameMode').value=mode;$('victoryMode').value=String(room.victoryPoints||3);
 $('start').classList.add('hidden');$('game').classList.remove('hidden');
 const nativeRandom=Math.random;Math.random=onlineSeededRandom(room.seed);try{init()}finally{Math.random=nativeRandom}
 room.players.forEach((pl,i)=>{if(G.players[i])G.players[i].name=pl.pseudo});
 G.online={code:room.code,seed:room.seed,mySocketId:onlineSocket&&onlineSocket.id,myPlayerIndex:room.players.findIndex(pl=>onlineSocket&&pl.id===onlineSocket.id),hostId:room.hostId};
 render();
}
'''
new_launch = '''function onlineDisplayGame(state){
 const players=state.players.map((sp,i)=>({
   name:sp.pseudo,faction:Number.isInteger(sp.faction)?sp.faction:0,gold:sp.gold||0,pvPermanent:sp.pvPermanent||0,
   hand:Array.isArray(sp.hand)?sp.hand.slice():[],remoteHandCount:sp.handCount||0,inPlay:[],attackTurnBonus:0,defenseTurnBonus:0,
   bot:!!sp.bot,decimated:false,portrait:sp.portrait||null
 }));
 const board={};Object.entries(state.board||{}).forEach(([r,c])=>board[r]={...c});
 const sea={};Object.keys(SEA).forEach(id=>sea[id]={fleets:{}});
 const active=Number.isInteger(state.active)?state.active:0;
 G={active,turn:state.turn||0,phase:state.phase||'setup',dragon:state.dragon||'E4',victoryTarget:state.victoryPoints||3,
   players,b:board,sea,deck:[],discard:[],log:[],oracleDeck:[],oracleDiscard:[],oracleActive:null,
   online:{code:state.code,seed:state.seed,mySocketId:onlineSocket&&onlineSocket.id,myPlayerIndex:state.youIndex,hostId:onlineRoom&&onlineRoom.hostId,revision:state.revision}};
}
function onlineApplyStateToDisplay(state){
 if(!G||!G.online){onlineDisplayGame(state);return}
 G.active=Number.isInteger(state.active)?state.active:0;G.turn=state.turn||0;G.phase=state.phase||'setup';G.dragon=state.dragon||'E4';G.victoryTarget=state.victoryPoints||3;
 Object.entries(state.board||{}).forEach(([r,c])=>G.b[r]={...c});
 state.players.forEach((sp,i)=>{
   if(!G.players[i])return;
   const pl=G.players[i];pl.name=sp.pseudo;pl.faction=Number.isInteger(sp.faction)?sp.faction:0;pl.gold=sp.gold||0;pl.pvPermanent=sp.pvPermanent||0;pl.bot=!!sp.bot;pl.portrait=sp.portrait||null;pl.remoteHandCount=sp.handCount||0;
   if(Array.isArray(sp.hand))pl.hand=sp.hand.slice();
 });
 G.online.myPlayerIndex=state.youIndex;G.online.revision=state.revision;
}
function onlineSetupRegionsFor(state){const me=state.players[state.youIndex];return me&&me.province?Object.keys(R).filter(r=>R[r][0]===me.province&&!R[r][2]):[]}
function renderOnlineAuthoritativeSetup(state){
 onlineApplyStateToDisplay(state);setupState=null;
 $('start').classList.add('hidden');$('game').classList.remove('hidden');
 const panel=$('setupPanel');panel.classList.remove('hidden');
 const me=state.players[state.youIndex],active=state.setup&&state.setup.activePlayer===state.youIndex,stage=state.setup&&state.setup.stage;
 $('setupTitle').textContent='Installation Online — '+(me?me.pseudo:'TRIBU');
 const box=$('setupChoices');box.innerHTML='';
 if(!active){
   const current=state.players[state.setup.activePlayer];
   $('setupText').innerHTML='Province attribuée : <b>'+(me&&me.province||'—')+'</b><br>En attente de <b>'+(current?current.pseudo:'un autre joueur')+'</b>.';
 }else if(stage==='identity'){
   onlineSetupSelectedRegions=[];
   $('setupText').innerHTML='Province attribuée au hasard : <b>'+me.province+'</b><br>Choisissez votre couleur puis votre encart de faction.';
   BASE_COLORS.forEach((color,i)=>{if(state.setup.usedColors.includes(color))return;const b=document.createElement('button');b.className='setupColorBtn';b.dataset.color=color;b.textContent=COLOR_NAMES[i];b.style.borderColor=color;b.style.color=color;b.onclick=()=>{box.querySelectorAll('.setupColorBtn').forEach(x=>x.classList.remove('selected'));b.classList.add('selected');box.dataset.color=color;onlineSetupIdentityReady(box)}});
   const br=document.createElement('div');br.style.flexBasis='100%';box.appendChild(br);
   Object.entries(FACTION_PORTRAIT_META).forEach(([key,meta])=>{if(state.setup.usedPortraits.includes(key))return;const b=document.createElement('button');b.className='setupFactionPortrait';b.dataset.portrait=key;b.innerHTML='<img src="'+FACTION_PORTRAITS[key]+'" alt="'+meta.label+'"><span>'+meta.label+'</span>';b.onclick=()=>{box.querySelectorAll('.setupFactionPortrait').forEach(x=>x.classList.remove('selected'));b.classList.add('selected');box.dataset.portrait=key;onlineSetupIdentityReady(box)};box.appendChild(b)});
   const br2=document.createElement('div');br2.style.flexBasis='100%';box.appendChild(br2);const ok=document.createElement('button');ok.id='onlineSetupIdentityConfirm';ok.textContent='Valider couleur et faction';ok.disabled=true;ok.onclick=()=>onlineAck('setupIdentity',{color:box.dataset.color,portrait:box.dataset.portrait}).catch(onlineError);box.appendChild(ok);
 }else if(stage==='regions'){
   $('setupText').innerHTML='Province <b>'+me.province+'</b> — choisissez <b>2 régions parmi les 4 régions non hostiles</b>.<br>Sélection : <b>'+onlineSetupSelectedRegions.length+'/2</b>';
   const ok=document.createElement('button');ok.textContent='Valider les 2 régions';ok.disabled=onlineSetupSelectedRegions.length!==2;ok.onclick=()=>onlineAck('setupRegions',{regions:onlineSetupSelectedRegions.slice()}).catch(onlineError);box.appendChild(ok);
 }
 renderMap();renderPlayerRail();
}
function onlineSetupIdentityReady(box){const b=$('onlineSetupIdentityConfirm');if(b)b.disabled=!(box.dataset.color&&box.dataset.portrait)}
function onlineSetupRegionClick(r){
 const state=onlineGameState;if(!state||state.status!=='setup'||!state.setup||state.setup.activePlayer!==state.youIndex||state.setup.stage!=='regions')return;
 const allowed=onlineSetupRegionsFor(state);if(!allowed.includes(r))return;
 const at=onlineSetupSelectedRegions.indexOf(r);if(at>=0)onlineSetupSelectedRegions.splice(at,1);else if(onlineSetupSelectedRegions.length<2)onlineSetupSelectedRegions.push(r);
 renderOnlineAuthoritativeSetup(state);
}
function onlineLockControls(){
 if(!G||!G.online||!onlineGameState)return;
 const mine=onlineGameState.active===onlineGameState.youIndex&&onlineGameState.status==='playing';
 $('startTurn').classList.toggle('hidden',!mine||onlineGameState.phase!=='start');
 $('draw').disabled=!(mine&&onlineGameState.phase==='start');
 ['harvest','recruit','endRecruit','toOracle','roll'].forEach(id=>{const el=$(id);if(el)el.disabled=true});
 const h=$('hand');if(h)h.querySelectorAll('.card').forEach(c=>{c.onclick=null;c.classList.remove('playablePermanent','battlePlayable');c.classList.add('battleBlocked')});
 const n=$('status');if(n)n.innerHTML+='<div class="botNotice">🌐 Online autoritaire — seules les actions déjà migrées vers le serveur sont activées.</div>';
}
function applyOnlineGameState(state){
 onlineGameState=state;
 if(state.status==='setup'){renderOnlineAuthoritativeSetup(state);return}
 onlineApplyStateToDisplay(state);setupState=null;$('setupPanel').classList.add('hidden');$('start').classList.add('hidden');$('game').classList.remove('hidden');render();onlineLockControls();
}
function launchOnlineRoom(room){
 if(!room||room.seed===null||room.seed===undefined)return onlineError(new Error('Graine de partie absente.'));
 onlineRoom=room;onlineSelectedMode=room.mode;$('victoryMode').value=String(room.victoryPoints||3);
 $('start').classList.add('hidden');$('game').classList.remove('hidden');
 onlineAck('requestGameState',{}).then(res=>applyOnlineGameState(res.game)).catch(onlineError);
}
function onlineGameAction(type,payload={}){return onlineAck('gameAction',{type,...payload}).catch(onlineError)}
'''
rep(old_launch, new_launch, 'launchOnlineRoom')

rep(
"  socket.on('gameLaunched',room=>{onlineRoom=room;$('onlineLaunch').disabled=true;$('onlineReady').disabled=true;launchOnlineRoom(room)});",
"  socket.on('gameLaunched',room=>{onlineRoom=room;$('onlineLaunch').disabled=true;$('onlineReady').disabled=true;launchOnlineRoom(room)});\n  socket.on('gameState',applyOnlineGameState);",
"listener gameState"
)

rep(
"function clickSpot(id){\n if(setupState){if(setupState.stage==='regions')setupRegionClick(id);return}",
"function clickSpot(id){\n if(G&&G.online&&onlineGameState){if(onlineGameState.status==='setup')onlineSetupRegionClick(id);return}\n if(setupState){if(setupState.stage==='regions')setupRegionClick(id);return}",
"blocage map Online"
)

rep(
" if(setupState&&setupState.stage==='regions'){\n   const prov=setupState.assignedProvinces[setupState.index];\n   if(setupProvinceRegions(prov).includes(id))b.classList.add(setupState.selectedRegions.includes(id)?'setupRegionChosen':'setupRegionReady');\n }",
" if(setupState&&setupState.stage==='regions'){\n   const prov=setupState.assignedProvinces[setupState.index];\n   if(setupProvinceRegions(prov).includes(id))b.classList.add(setupState.selectedRegions.includes(id)?'setupRegionChosen':'setupRegionReady');\n }\n if(G&&G.online&&onlineGameState&&onlineGameState.status==='setup'&&onlineGameState.setup&&onlineGameState.setup.activePlayer===onlineGameState.youIndex&&onlineGameState.setup.stage==='regions'){\n   if(onlineSetupRegionsFor(onlineGameState).includes(id))b.classList.add(onlineSetupSelectedRegions.includes(id)?'setupRegionChosen':'setupRegionReady');\n }",
"surbrillance régions Online"
)

rep(
"function doDraw(){if(paidDrawState)return;draw(G.active,2);log(p().name+' pioche 2 cartes.');beginPlay()}",
"function doDraw(){if(G&&G.online)return onlineGameAction('DRAW_START');if(paidDrawState)return;draw(G.active,2);log(p().name+' pioche 2 cartes.');beginPlay()}",
"pioche autoritaire"
)

p.write_text(s, encoding='utf-8')
