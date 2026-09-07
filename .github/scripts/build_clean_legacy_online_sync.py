from pathlib import Path
import re

INDEX=Path('index.html')
SERVER=Path('server/server.js')
html=INDEX.read_text(encoding='utf-8')
server=SERVER.read_text(encoding='utf-8')

MARK='// ===== CLEAN ONLINE LEGACY SYNC v1 ====='
if MARK in html:
    raise SystemExit('client sync patch already present')

# In Online legacy-sync mode, do NOT divert original game functions to the old
# simplified gameAction engine. Setup still uses the existing authoritative flow
# because legacySync is only enabled once setup is complete.
html=html.replace('if(G&&G.online)', 'if(G&&G.online&&!G.online.legacySync)')

client_sync=r'''// ===== CLEAN ONLINE LEGACY SYNC v1 =====
// The original TRIBU engine remains the only gameplay engine. Online only stores
// and relays complete committed engine snapshots. UI drafts such as dest/picks are
// deliberately not synchronized.
let onlineLegacyRevision=0,onlineLegacyApplying=false,onlineLegacyLastDigest='',onlineLegacyPushTimer=null;
function onlineLegacyDriverIndex(){
 if(!G)return -1;
 return G.players.findIndex(pl=>!pl.bot);
}
function onlineLegacyIsDriver(){return !!(G&&G.online&&G.online.legacySync&&G.online.myPlayerIndex===onlineLegacyDriverIndex())}
function onlineLegacyEncode(value){
 return JSON.parse(JSON.stringify(value,(k,v)=>v instanceof Set?{$tribuSet:[...v]}:(typeof v==='function'?undefined:v)));
}
function onlineLegacyDecode(value){
 const walk=v=>{
   if(!v||typeof v!=='object')return v;
   if(Array.isArray(v))return v.map(walk);
   if(Array.isArray(v.$tribuSet))return new Set(v.$tribuSet.map(walk));
   const out={};Object.entries(v).forEach(([k,x])=>out[k]=walk(x));return out;
 };
 return walk(value);
}
function onlineLegacyRuleState(){
 return {
   movable,usedDest,destinationUseCount,attacked,cycle,battle,buildingMode,portalMode,choiceState,
   paidDrawState,goldReaction,shadowState,battleStack,egnoState,returnState,dragonRichState,dragonCurseState,
   dragonPublicState,agentModalState,caravanState,oraclePassArmed,oracleState,seaStormState,oracleClimateVisual,
   oraclePendingNormalMap,turnEpoch,divinationState,recruitSnapshot,gameOverState,commerceDeals,commerceSeq
 };
}
function onlineLegacySnapshot(){
 const cleanG=onlineLegacyEncode(G);
 if(cleanG&&cleanG.online){
   delete cleanG.online.mySocketId;
   delete cleanG.online.myPlayerIndex;
   delete cleanG.online.revision;
 }
 return {g:cleanG,rule:onlineLegacyEncode(onlineLegacyRuleState())};
}
function onlineLegacyDigest(){try{return JSON.stringify(onlineLegacySnapshot())}catch(_){return ''}}
function onlineLegacyBootstrap(full,state){
 const players=(full.players||[]).map((sp,i)=>({
   name:sp.pseudo||('Joueur '+(i+1)),faction:Number.isInteger(sp.faction)?sp.faction:0,gold:sp.gold||0,pvPermanent:sp.pvPermanent||0,
   hand:Array.isArray(sp.hand)?sp.hand.slice():[],inPlay:Array.isArray(sp.inPlay)?sp.inPlay.slice():[],attackTurnBonus:0,defenseTurnBonus:0,
   bot:!!sp.bot,decimated:false,portrait:sp.portrait||null,color:sp.color||null
 }));
 COLORS.splice(0,COLORS.length,...BASE_COLORS);(full.players||[]).forEach((sp,i)=>{if(sp.color)COLORS[i]=sp.color});
 const board={};Object.entries(full.board||{}).forEach(([r,c])=>board[r]={...c});
 const sea={};Object.keys(SEA).forEach(id=>sea[id]={fleets:{...((full.sea&&full.sea[id]&&full.sea[id].fleets)||{})}});
 G={active:Number.isInteger(full.active)?full.active:0,turn:full.turn||1,phase:full.phase||'start',dragon:full.dragon||'E4',victoryTarget:full.victoryPoints||3,
   players,b:board,sea,deck:(full.deck||[]).slice(),discard:(full.discard||[]).slice(),log:(full.log||[]).slice(),
   oracleDeck:(full.oracleDeck||[]).slice(),oracleDiscard:(full.oracleDiscard||[]).slice(),oracleActive:full.oracleActive===null?null:full.oracleActive,
   online:{code:full.code||state.code,seed:full.seed||state.seed,mySocketId:onlineSocket&&onlineSocket.id,myPlayerIndex:full.youIndex,hostId:onlineRoom&&onlineRoom.hostId,legacySync:true,revision:full.legacyRevision||0}};
 G.players.forEach((_,i)=>agentDefaults(i));
 movable={};usedDest=new Set();destinationUseCount={};attacked=new Set();cycle=1;dest=null;picks={};battle=null;buildingMode=null;portalMode=null;choiceState=null;
 paidDrawState=null;goldReaction=null;shadowState=null;battleStack=[];egnoState=null;returnState=null;dragonRichState=null;dragonCurseState=null;dragonPublicState=null;
 agentModalState=null;caravanState=null;oraclePassArmed=false;oracleState=null;seaStormState=null;oracleClimateVisual=null;oraclePendingNormalMap=false;turnEpoch=0;
 divinationState=null;recruitSnapshot=null;gameOverState=null;commerceDeals=[];commerceSeq=1;
 if(G.phase==='play')setMovable();else resetMove();
 onlineLegacyRevision=full.legacyRevision||0;
 onlineLegacyLastDigest=onlineLegacyDigest();
 setupState=null;onlineSetupLayout(false);$('setupPanel').classList.add('hidden');$('start').classList.add('hidden');$('game').classList.remove('hidden');
 render();onlineLegacyLastDigest=onlineLegacyDigest();onlineLegacyLockControls();
 if(onlineLegacyIsDriver())queueBot('synchronisation Online');
 if(onlineWelcomeShownKey!==String(state.seed||'game'))onlineShowGameWelcome(state);
}
function onlineLegacyApply(packet){
 if(!packet||!packet.snapshot)return;
 if(!G||!G.online||!G.online.legacySync)return;
 const me=packet.youIndex;
 onlineLegacyApplying=true;
 const localOnline={code:G.online.code,seed:G.online.seed,mySocketId:onlineSocket&&onlineSocket.id,myPlayerIndex:me,hostId:onlineRoom&&onlineRoom.hostId,legacySync:true,revision:packet.revision};
 const decoded=onlineLegacyDecode(packet.snapshot),next=decoded.g||{};next.online=localOnline;G=next;
 const r=decoded.rule||{};
 movable=r.movable||{};usedDest=r.usedDest instanceof Set?r.usedDest:new Set(r.usedDest||[]);destinationUseCount=r.destinationUseCount||{};attacked=r.attacked instanceof Set?r.attacked:new Set(r.attacked||[]);cycle=r.cycle||1;
 battle=r.battle||null;buildingMode=r.buildingMode||null;portalMode=r.portalMode||null;choiceState=r.choiceState||null;paidDrawState=r.paidDrawState||null;goldReaction=r.goldReaction||null;
 shadowState=r.shadowState||null;battleStack=r.battleStack||[];egnoState=r.egnoState||null;returnState=r.returnState||null;dragonRichState=r.dragonRichState||null;dragonCurseState=r.dragonCurseState||null;
 dragonPublicState=r.dragonPublicState||null;agentModalState=r.agentModalState||null;caravanState=r.caravanState||null;oraclePassArmed=!!r.oraclePassArmed;oracleState=r.oracleState||null;
 seaStormState=r.seaStormState||null;oracleClimateVisual=r.oracleClimateVisual||null;oraclePendingNormalMap=!!r.oraclePendingNormalMap;turnEpoch=r.turnEpoch||0;divinationState=r.divinationState||null;
 recruitSnapshot=r.recruitSnapshot||null;gameOverState=r.gameOverState||null;commerceDeals=r.commerceDeals||[];commerceSeq=r.commerceSeq||1;
 onlineLegacyRevision=packet.revision||0;dest=null;picks={};
 (G.players||[]).forEach((_,i)=>agentDefaults(i));
 onlineLegacyLastDigest=onlineLegacyDigest();render();onlineLegacyLastDigest=onlineLegacyDigest();onlineLegacyApplying=false;onlineLegacyLockControls();
 if(onlineLegacyIsDriver())queueBot('état Online reçu');
}
function onlineLegacyStart(state){
 onlineGameState=state;
 onlineAck('requestLegacyState',{}).then(res=>{
   if(res.snapshot){
     if(!G||!G.online||!G.online.legacySync){
       // Build a minimal full shell first, then apply the stored canonical snapshot.
       onlineLegacyBootstrap(res.bootstrap,state);
     }
     onlineLegacyApply({snapshot:res.snapshot,revision:res.revision,youIndex:res.youIndex});
   }else onlineLegacyBootstrap(res.bootstrap,state);
 }).catch(onlineError);
}
function onlineLegacyCanPublish(){
 if(!G||!G.online||!G.online.legacySync||onlineLegacyApplying||!onlineSocket)return false;
 const me=G.online.myPlayerIndex;if(!Number.isInteger(me)||!G.players[me]||G.players[me].bot)return false;
 if(G.players[G.active]&&G.players[G.active].bot)return onlineLegacyIsDriver();
 return true;
}
function onlineLegacyMaybePush(){
 if(!onlineLegacyCanPublish())return;
 const digest=onlineLegacyDigest();if(!digest||digest===onlineLegacyLastDigest)return;
 clearTimeout(onlineLegacyPushTimer);
 onlineLegacyPushTimer=setTimeout(()=>{
   if(!onlineLegacyCanPublish())return;
   const now=onlineLegacyDigest();if(!now||now===onlineLegacyLastDigest)return;
   const snapshot=onlineLegacySnapshot(),actorIndex=G.online.myPlayerIndex,baseRevision=onlineLegacyRevision;
   onlineLegacyLastDigest=now;
   onlineAck('legacyCommit',{baseRevision,actorIndex,snapshot}).then(res=>{
     onlineLegacyRevision=res.revision;G.online.revision=res.revision;
   }).catch(err=>{
     onlineLegacyLastDigest='';
     if(err&&err.current)onlineLegacyApply(err.current);else onlineError(err);
   });
 },90);
}
function onlineLegacyViewerNeedsMap(me){
 if(oracleState&&oracleState.kind==='sacrifice'){
   const q=oracleState.queues&&oracleState.queues[oracleState.index];if(q&&q.player===me)return true;
 }
 if(oracleState&&oracleState.kind==='dragon5'&&oracleState.player===me)return true;
 if(dragonRichState&&dragonRichState.player===me)return true;
 return me===G.active;
}
function onlineLegacyLockControls(){
 if(!G||!G.online||!G.online.legacySync)return;
 const me=G.online.myPlayerIndex,mine=me===G.active&&!G.players[me].bot,botDriver=G.players[G.active]&&G.players[G.active].bot&&onlineLegacyIsDriver();
 const canTurn=mine||botDriver;
 const start=canTurn&&G.phase==='start',recruiting=canTurn&&G.phase==='recruit',playing=canTurn&&G.phase==='play',oracleRoll=canTurn&&G.phase==='oracleRoll';
 const s=$('startTurn');if(s)s.classList.toggle('hidden',!start);
 if($('draw'))$('draw').disabled=!start;if($('harvest'))$('harvest').disabled=!start;if($('recruit'))$('recruit').disabled=!start;
 if($('endRecruit'))$('endRecruit').disabled=!recruiting;if($('resetRecruit'))$('resetRecruit').disabled=!recruiting;
 if($('toOracle'))$('toOracle').disabled=!playing;if($('roll'))$('roll').disabled=!oracleRoll;
 const map=$('map');if(map)map.style.pointerEvents=onlineLegacyViewerNeedsMap(me)?'':'none';
 const n=$('status');if(n&&!n.querySelector('.onlineLegacyNotice'))n.insertAdjacentHTML('beforeend','<div class="botNotice onlineLegacyNotice">🌐 Online — moteur original TRIBU synchronisé.</div>');
}
const onlineLegacyBaseRender=render;
render=function(){
 onlineLegacyBaseRender();
 if(G&&G.online&&G.online.legacySync){onlineLegacyLockControls();onlineLegacyMaybePush()}
};
const onlineLegacyBaseQueueBot=queueBot;
queueBot=function(reason){
 if(G&&G.online&&G.online.legacySync&&!onlineLegacyIsDriver())return;
 return onlineLegacyBaseQueueBot(reason);
};
'''
anchor='function onlineSetupRegionsFor(state)'
if anchor not in html: raise SystemExit('client anchor missing')
html=html.replace(anchor,client_sync+'\n'+anchor,1)

# Keep setup locking as-is, but once legacySync is active never call the destructive
# onlineRefreshPlayUi path.
old="function onlineLockControls(){\n if(!G||!G.online||!onlineGameState)return;"
new="function onlineLockControls(){\n if(G&&G.online&&G.online.legacySync){onlineLegacyLockControls();return}\n if(!G||!G.online||!onlineGameState)return;"
if old not in html: raise SystemExit('onlineLockControls anchor missing')
html=html.replace(old,new,1)

pattern=r"function applyOnlineGameState\(state\)\{.*?\n\}\nfunction launchOnlineRoom"
replacement=r'''function applyOnlineGameState(state){
 const wasSetup=onlineGameState&&onlineGameState.status==='setup';onlineGameState=state;
 if(state.status==='setup'){renderOnlineAuthoritativeSetup(state);return}
 if(state.status==='playing'){
   if(G&&G.online&&G.online.legacySync){G.online.serverRevision=state.revision;onlineLegacyLockControls();return}
   onlineLegacyStart(state);return;
 }
 if(wasSetup)onlineSetupLayout(false);
}
function launchOnlineRoom'''
html,n=re.subn(pattern,replacement,html,count=1,flags=re.S)
if n!=1: raise SystemExit('applyOnlineGameState replacement failed')

old="  socket.on('gameState',applyOnlineGameState);"
new="  socket.on('gameState',applyOnlineGameState);\n  socket.on('legacyState',packet=>onlineLegacyApply(packet));"
if old not in html: raise SystemExit('socket gameState anchor missing')
html=html.replace(old,new,1)

# ----- server -----
SMARK='// ===== CLEAN ONLINE LEGACY SYNC v1 ====='
if SMARK in server: raise SystemExit('server sync patch already present')

server=server.replace("function scheduleBotTurn(room){\n  if(!room||!room.game||room.game.status!=='playing')return;",
"function scheduleBotTurn(room){\n  if(room&&room.legacyMode)return;\n  if(!room||!room.game||room.game.status!=='playing')return;",1)

old="  game.players.forEach((_, i) => drawCards(game, i, 3));\n  game.setup = null;\n  game.status = 'playing';"
new="  game.players.forEach((_, i) => drawCards(game, i, 3));\n  game.setup = null;\n  room.legacyMode = true; room.legacyRevision = 0; room.legacySnapshot = null;\n  game.status = 'playing';"
if old not in server: raise SystemExit('completeSetup anchor missing')
server=server.replace(old,new,1)

server_sync=r'''// ===== CLEAN ONLINE LEGACY SYNC v1 =====
function legacyYouIndex(room,socketId){return humanGameIndex(room,socketId)}
function legacyBootstrapView(room,socketId){
  const game=room.game,youIndex=legacyYouIndex(room,socketId);
  return {
    code:room.code,mode:room.mode,victoryPoints:room.victoryPoints,seed:room.seed,youIndex,legacyRevision:room.legacyRevision||0,
    status:game.status,phase:game.phase,turn:game.turn,active:game.active,dragon:game.dragon,
    board:game.board,sea:game.sea,deck:game.deck,discard:game.discard,oracleDeck:game.oracleDeck,oracleDiscard:game.oracleDiscard,oracleActive:game.oracleActive,
    log:[],players:game.players.map((p,i)=>({index:i,pseudo:p.pseudo,bot:p.bot,connected:p.bot?true:p.connected!==false,color:p.color,portrait:p.portrait,faction:p.faction,province:p.province,regions:(p.regions||[]).slice(),gold:p.gold||0,pvPermanent:p.pvPermanent||0,hand:(p.hand||[]).slice(),inPlay:[]}))
  };
}
function emitLegacy(room,exceptSocketId=null){
  if(!room||!room.legacySnapshot)return;
  room.players.forEach(p=>{
    if(p.id===exceptSocketId)return;
    const socket=io.sockets.sockets.get(p.id);if(!socket)return;
    socket.emit('legacyState',{snapshot:room.legacySnapshot,revision:room.legacyRevision||0,youIndex:legacyYouIndex(room,p.id)});
  });
}
'''
anchor='function emitRoom(room) {'
if anchor not in server: raise SystemExit('server emitRoom anchor missing')
server=server.replace(anchor,server_sync+'\n'+anchor,1)

legacy_events=r'''
  socket.on('requestLegacyState', (_payload, ack = () => {}) => {
    const room=roomForSocket(socket);
    if(!room||!room.game||room.game.status!=='playing')return rejectGameAction(ack,'La partie complète n’est pas disponible.');
    const youIndex=humanGameIndex(room,socket.id);if(youIndex<0)return rejectGameAction(ack,'Joueur introuvable.');
    ack({ok:true,revision:room.legacyRevision||0,youIndex,bootstrap:legacyBootstrapView(room,socket.id),snapshot:room.legacySnapshot||null});
  });

  socket.on('legacyCommit', (payload = {}, ack = () => {}) => {
    const room=roomForSocket(socket);
    if(!room||!room.game||room.game.status!=='playing'||!room.legacyMode)return rejectGameAction(ack,'Synchronisation complète indisponible.');
    const index=humanGameIndex(room,socket.id);if(index<0)return rejectGameAction(ack,'Joueur introuvable.');
    if(Number(payload.actorIndex)!==index)return rejectGameAction(ack,'Vous ne pouvez synchroniser que vos propres actions.');
    const base=Number(payload.baseRevision)||0,current=room.legacyRevision||0;
    if(base!==current){
      return ack({ok:false,error:'État de partie plus récent disponible.',current:room.legacySnapshot?{snapshot:room.legacySnapshot,revision:current,youIndex:index}:null});
    }
    if(!payload.snapshot||typeof payload.snapshot!=='object')return rejectGameAction(ack,'État de jeu invalide.');
    room.legacySnapshot=payload.snapshot;room.legacyRevision=current+1;
    ack({ok:true,revision:room.legacyRevision});emitLegacy(room,socket.id);
  });
'''
anchor="  socket.on('gameAction', (payload = {}, ack = () => {}) => {"
if anchor not in server: raise SystemExit('server gameAction anchor missing')
server=server.replace(anchor,legacy_events+'\n'+anchor,1)

INDEX.write_text(html,encoding='utf-8')
SERVER.write_text(server,encoding='utf-8')
print('clean legacy Online sync patch applied')
