from pathlib import Path

INDEX=Path('index.html')
SERVER=Path('server/server.js')
idx=INDEX.read_text(encoding='utf-8')
srv=SERVER.read_text(encoding='utf-8')

def repl(text, old, new, label, count=1):
    if old not in text:
        raise SystemExit(f'anchor not found: {label}')
    return text.replace(old,new,count)

# ---- CLIENT: conserve le moteur original et le synchronise en Online ----
idx=repl(idx,
"let onlineSelectedMode=null,onlineReadyState=false,onlineSocket=null,onlineRoom=null,onlineGameState=null,onlineSetupSelectedRegions=[],onlineSetupDraft={color:null,portrait:null};",
"let onlineSelectedMode=null,onlineReadyState=false,onlineSocket=null,onlineRoom=null,onlineGameState=null,onlineSetupSelectedRegions=[],onlineSetupDraft={color:null,portrait:null};\nlet onlineLegacyApplying=false,onlineLegacyPushTimer=null,onlineLegacyLastSent='';",
'online globals')

idx=repl(idx,
"hand:Array.isArray(sp.hand)?sp.hand.slice():[],remoteHandCount:sp.handCount||0,inPlay:[],attackTurnBonus:0,defenseTurnBonus:0,\n   bot:!!sp.bot,decimated:false,portrait:sp.portrait||null,color:sp.color||null",
"hand:Array.isArray(sp.hand)?sp.hand.slice():[],remoteHandCount:sp.handCount||0,inPlay:Array.isArray(sp.inPlay)?JSON.parse(JSON.stringify(sp.inPlay)):[],attackTurnBonus:Number(sp.attackTurnBonus||0),defenseTurnBonus:Number(sp.defenseTurnBonus||0),\n   bot:!!sp.bot,decimated:!!sp.decimated,portrait:sp.portrait||null,color:sp.color||null",
'online player legacy fields')

idx=repl(idx,
"players,b:board,sea,deck:[],discard:[],log:[],oracleDeck:[],oracleDiscard:[],oracleActive:state.oracleActive===null?null:state.oracleActive,",
"players,b:board,sea,deck:Array.isArray(state.deck)?state.deck.slice():[],discard:Array.isArray(state.discard)?state.discard.slice():[],log:[],oracleDeck:Array.isArray(state.oracleDeck)?state.oracleDeck.slice():[],oracleDiscard:Array.isArray(state.oracleDiscard)?state.oracleDiscard.slice():[],oracleActive:state.oracleActive===null?null:state.oracleActive,",
'online initial decks')

idx=repl(idx,
"online:{code:state.code,seed:state.seed,mySocketId:onlineSocket&&onlineSocket.id,myPlayerIndex:state.youIndex,hostId:onlineRoom&&onlineRoom.hostId,revision:state.revision}};",
"online:{code:state.code,seed:state.seed,mySocketId:onlineSocket&&onlineSocket.id,myPlayerIndex:state.youIndex,hostId:onlineRoom&&onlineRoom.hostId,revision:state.revision,fullLegacy:true,legacyRevision:Number(state.legacyRevision||0),legacyDriverIndex:Number.isInteger(state.legacyDriverIndex)?state.legacyDriverIndex:null}};",
'online legacy flags')

idx=repl(idx,
"const pl=G.players[i];pl.name=sp.pseudo;pl.faction=Number.isInteger(sp.faction)?sp.faction:0;pl.gold=sp.gold||0;pl.pvPermanent=sp.pvPermanent||0;pl.bot=!!sp.bot;pl.portrait=sp.portrait||null;pl.color=sp.color||null;pl.remoteHandCount=sp.handCount||0;",
"const pl=G.players[i];pl.name=sp.pseudo;pl.faction=Number.isInteger(sp.faction)?sp.faction:0;pl.gold=sp.gold||0;pl.pvPermanent=sp.pvPermanent||0;pl.bot=!!sp.bot;pl.portrait=sp.portrait||null;pl.color=sp.color||null;pl.remoteHandCount=sp.handCount||0;pl.inPlay=Array.isArray(sp.inPlay)?JSON.parse(JSON.stringify(sp.inPlay)):pl.inPlay||[];pl.attackTurnBonus=Number(sp.attackTurnBonus||0);pl.defenseTurnBonus=Number(sp.defenseTurnBonus||0);pl.decimated=!!sp.decimated;",
'online apply player legacy fields')

idx=repl(idx,
" G.online.myPlayerIndex=state.youIndex;G.online.revision=state.revision;\n}",
" G.online.myPlayerIndex=state.youIndex;G.online.revision=state.revision;G.online.fullLegacy=true;G.online.legacyRevision=Number(state.legacyRevision||0);G.online.legacyDriverIndex=Number.isInteger(state.legacyDriverIndex)?state.legacyDriverIndex:null;\n G.deck=Array.isArray(state.deck)?state.deck.slice():G.deck||[];G.discard=Array.isArray(state.discard)?state.discard.slice():G.discard||[];G.oracleDeck=Array.isArray(state.oracleDeck)?state.oracleDeck.slice():G.oracleDeck||[];G.oracleDiscard=Array.isArray(state.oracleDiscard)?state.oracleDiscard.slice():G.oracleDiscard||[];\n}",
'online apply deck fields')

# Les fonctions originales redeviennent la source des règles en Online complet.
for old,new,label in [
("function beginPlay(){if(G&&G.online){","function beginPlay(){if(G&&G.online&&!G.online.fullLegacy){",'beginPlay'),
("function doDraw(){if(G&&G.online)return onlineGameAction('DRAW_START');","function doDraw(){if(G&&G.online&&!G.online.fullLegacy)return onlineGameAction('DRAW_START');",'doDraw'),
("function doHarvest(){if(G&&G.online)return onlineGameAction('HARVEST_START');","function doHarvest(){if(G&&G.online&&!G.online.fullLegacy)return onlineGameAction('HARVEST_START');",'doHarvest'),
(" if(G&&G.online)return onlineGameAction('RECRUIT_START');"," if(G&&G.online&&!G.online.fullLegacy)return onlineGameAction('RECRUIT_START');",'doRecruit'),
(" if(G&&G.online)return onlineGameAction('RESET_RECRUIT');"," if(G&&G.online&&!G.online.fullLegacy)return onlineGameAction('RESET_RECRUIT');",'resetRecruit'),
(" if(G&&G.online)return onlineGameAction('RECRUIT_AT',{region:r});"," if(G&&G.online&&!G.online.fullLegacy)return onlineGameAction('RECRUIT_AT',{region:r});",'recruitAt'),
(" if(G&&G.online)return onlineGameAction('END_PLAY');"," if(G&&G.online&&!G.online.fullLegacy)return onlineGameAction('END_PLAY');",'toOracle'),
(" if(G&&G.online)return onlineGameAction('ORACLE_ROLL');"," if(G&&G.online&&!G.online.fullLegacy)return onlineGameAction('ORACLE_ROLL');",'roll'),
]:
    idx=repl(idx,old,new,label)

idx=repl(idx,
"function queueBot(reason){\n if(gameOverState)return;",
"function queueBot(reason){\n if(gameOverState)return;\n if(G&&G.online&&G.online.fullLegacy&&!onlineLegacyIsDriver())return;",
'bot driver')

bridge=r'''function onlineLegacyIsDriver(){return !!(G&&G.online&&G.online.fullLegacy&&G.online.legacyDriverIndex===G.online.myPlayerIndex)}
function onlineLegacySnapshot(){
 if(!G)return null;
 const g=JSON.parse(JSON.stringify(G));delete g.online;
 const raw={G:g,dest,picks,movable,usedDest:[...usedDest],destinationUseCount,attacked:[...attacked],cycle,battle,buildingMode,portalMode,choiceState,paidDrawState,goldReaction,shadowState,battleStack,egnoState,returnState,dragonRichState,dragonCurseState,dragonPublicState,dragonSixState,caravanState,oraclePassArmed,oracleState,seaStormState,oracleNoticeState,oracleClimateVisual,oraclePendingNormalMap,oracleResolutionAfter,oracleResolutionTurnEpoch,turnEpoch,divinationState,recruitSnapshot,gameOverState,botActionsThisTurn,commerceDeals,commerceSeq,commerceBattlePaused};
 return JSON.parse(JSON.stringify(raw));
}
function onlineLegacyApplySnapshot(snapshot,state){
 if(!snapshot||!snapshot.G)return false;
 onlineLegacyApplying=true;
 clearTimeout(onlineLegacyPushTimer);clearTimeout(botTimer);clearTimeout(botReactionTimer);clearInterval(battleTick);clearInterval(paidDrawTick);clearInterval(goldReactionTick);clearInterval(shadowTick);clearInterval(dragonSixTick);clearInterval(oracleNoticeTick);
 const oldOnline=G&&G.online?{...G.online}:{};const s=JSON.parse(JSON.stringify(snapshot));G=s.G;
 G.online={...oldOnline,code:state.code,seed:state.seed,mySocketId:onlineSocket&&onlineSocket.id,myPlayerIndex:state.youIndex,hostId:onlineRoom&&onlineRoom.hostId,revision:state.revision,fullLegacy:true,legacyRevision:Number(state.legacyRevision||0),legacyDriverIndex:Number.isInteger(state.legacyDriverIndex)?state.legacyDriverIndex:null};
 const set=(k,v)=>v===undefined?k:v;
 dest=s.dest??null;picks=s.picks||{};movable=s.movable||{};usedDest=new Set(s.usedDest||[]);destinationUseCount=s.destinationUseCount||{};attacked=new Set(s.attacked||[]);cycle=Number(s.cycle||1);battle=s.battle||null;buildingMode=s.buildingMode||null;portalMode=s.portalMode||null;choiceState=s.choiceState||null;paidDrawState=s.paidDrawState||null;goldReaction=s.goldReaction||null;shadowState=s.shadowState||null;battleStack=s.battleStack||[];egnoState=s.egnoState||null;returnState=s.returnState||null;dragonRichState=s.dragonRichState||null;dragonCurseState=s.dragonCurseState||null;dragonPublicState=s.dragonPublicState||null;dragonSixState=s.dragonSixState||null;caravanState=s.caravanState||null;oraclePassArmed=!!s.oraclePassArmed;oracleState=s.oracleState||null;seaStormState=s.seaStormState||null;oracleNoticeState=s.oracleNoticeState||null;oracleClimateVisual=s.oracleClimateVisual||null;oraclePendingNormalMap=!!s.oraclePendingNormalMap;oracleResolutionAfter=s.oracleResolutionAfter??null;oracleResolutionTurnEpoch=s.oracleResolutionTurnEpoch??null;turnEpoch=Number(s.turnEpoch||0);divinationState=s.divinationState||null;recruitSnapshot=s.recruitSnapshot||null;gameOverState=s.gameOverState||null;botActionsThisTurn=Number(s.botActionsThisTurn||0);commerceDeals=Array.isArray(s.commerceDeals)?s.commerceDeals:[];commerceSeq=Number(s.commerceSeq||1);commerceBattlePaused=!!s.commerceBattlePaused;
 onlineLegacyLastSent=JSON.stringify(s);onlineLegacyApplying=false;return true;
}
function onlineLegacyViewerCanAct(){
 if(!G||!G.online||!G.online.fullLegacy||onlineWelcomeActive)return false;const v=localViewer();if(v===null||v<0)return false;
 if(battle&&battle.kind!=='seaChoice'&&Array.isArray(battle.priorityOrder)&&battle.priorityOrder.length){const a=currentPriorityPlayer();return a===v||(G.players[a]&&G.players[a].bot&&onlineLegacyIsDriver())}
 if(caravanState&&Array.isArray(caravanState.order))return caravanState.order[caravanState.pick]===v||(G.players[caravanState.order[caravanState.pick]]&&G.players[caravanState.order[caravanState.pick]].bot&&onlineLegacyIsDriver());
 for(const s of [choiceState,shadowState,divinationState,returnState,dragonRichState,dragonCurseState,dragonPublicState,dragonSixState]){if(s&&Number.isInteger(s.player))return s.player===v}
 if(divinationState&&Number.isInteger(divinationState.actor))return divinationState.actor===v;
 if(G.players[G.active]&&G.players[G.active].bot)return onlineLegacyIsDriver();return G.active===v;
}
function onlineLegacyLockControls(){
 const mine=onlineLegacyViewerCanAct(),m=$('map'),h=$('hand');if(m)m.style.pointerEvents=mine?'':'none';if(h)h.style.pointerEvents=mine?'':'none';
 if(!mine)['draw','harvest','recruit','resetRecruit','endRecruit','toOracle','roll'].forEach(id=>{const b=$(id);if(b)b.disabled=true});
 const n=$('status');if(n&&!n.querySelector('.onlineLegacyNotice'))n.insertAdjacentHTML('beforeend','<div class="botNotice onlineLegacyNotice">🌐 Online — moteur original TRIBU synchronisé.</div>');
}
function onlineLegacySchedulePush(){
 if(onlineLegacyApplying||!G||!G.online||!G.online.fullLegacy||!onlineSocket||!onlineSocket.connected)return;clearTimeout(onlineLegacyPushTimer);onlineLegacyPushTimer=setTimeout(onlineLegacyPush,90);
}
function onlineLegacyPush(){
 if(onlineLegacyApplying||!G||!G.online||!G.online.fullLegacy||!onlineSocket||!onlineSocket.connected)return;const snap=onlineLegacySnapshot();if(!snap)return;const sig=JSON.stringify(snap);if(sig===onlineLegacyLastSent)return;
 const rev=Number(G.online.legacyRevision||0);onlineSocket.emit('legacyStatePush',{revision:rev,snapshot:snap},res=>{if(res&&res.ok){G.online.legacyRevision=Number(res.legacyRevision||rev+1);onlineLegacyLastSent=sig;return}onlineAck('requestGameState',{}).then(r=>applyOnlineGameState(r.game)).catch(onlineError)});
}
'''
idx=repl(idx,"function onlineLockControls(){",bridge+"function onlineLockControls(){\n if(G&&G.online&&G.online.fullLegacy){onlineLegacyLockControls();return}",'legacy bridge before lock')

old_apply="""function applyOnlineGameState(state){
 const wasSetup=onlineGameState&&onlineGameState.status==='setup',oldPhase=onlineGameState&&onlineGameState.phase;onlineGameState=state;if(oldPhase!==state.phase||state.active!==G?.active)onlineResetMoveDraft();
 if(state.status==='setup'){renderOnlineAuthoritativeSetup(state);return}
 onlineApplyStateToDisplay(state);setupState=null;onlineSetupLayout(false);$('setupPanel').classList.add('hidden');$('start').classList.add('hidden');$('game').classList.remove('hidden');render();
 if(state.status==='playing'&&(wasSetup||onlineWelcomeShownKey!==String(state.seed||'game')))onlineShowGameWelcome(state);
 onlineLockControls();
}"""
new_apply="""function applyOnlineGameState(state){
 const wasSetup=onlineGameState&&onlineGameState.status==='setup',oldPhase=onlineGameState&&onlineGameState.phase;onlineGameState=state;if(oldPhase!==state.phase||state.active!==G?.active)onlineResetMoveDraft();
 if(state.status==='setup'){renderOnlineAuthoritativeSetup(state);return}
 if(state.legacySnapshot)onlineLegacyApplySnapshot(state.legacySnapshot,state);else{onlineApplyStateToDisplay(state);G.online.fullLegacy=true;G.online.legacyRevision=Number(state.legacyRevision||0);G.online.legacyDriverIndex=Number.isInteger(state.legacyDriverIndex)?state.legacyDriverIndex:null;onlineLegacyLastSent=''}
 setupState=null;onlineSetupLayout(false);$('setupPanel').classList.add('hidden');$('start').classList.add('hidden');$('game').classList.remove('hidden');render();
 if(state.status==='playing'&&(wasSetup||onlineWelcomeShownKey!==String(state.seed||'game')))onlineShowGameWelcome(state);
 onlineLockControls();if(!state.legacySnapshot)onlineLegacySchedulePush();if(G&&G.online&&G.online.fullLegacy&&isBot()&&onlineLegacyIsDriver())queueBot('synchronisation Online');
}"""
idx=repl(idx,old_apply,new_apply,'apply online state')

idx=repl(idx,
"function onlineGameAction(type,payload={}){return onlineAck('gameAction',{type,...payload}).catch(onlineError)}\nfunction renderOnlineLobby(room){",
"function onlineGameAction(type,payload={}){return onlineAck('gameAction',{type,...payload}).catch(onlineError)}\nconst onlineLegacyBaseRender=render;render=function(){onlineLegacyBaseRender();if(G&&G.online&&G.online.fullLegacy){onlineLockControls();onlineLegacySchedulePush()}};\nfunction renderOnlineLobby(room){",
'render sync wrapper')

# ---- SERVEUR: état canonique de compatibilité du moteur original ----
helper=r'''function cloneJson(value){return value===undefined?undefined:JSON.parse(JSON.stringify(value))}
function legacyDriverIndex(room){if(!room||!room.game)return -1;for(let i=0;i<room.game.players.length;i++){const p=room.game.players[i];if(!p.bot&&p.connected!==false)return i}return -1}
function projectLegacySnapshot(game,snapshot){
 const g=snapshot&&snapshot.G;if(!g||!Array.isArray(g.players)||!g.b||typeof g.b!=='object')return false;
 if(Number.isInteger(g.active)&&g.active>=0&&g.active<game.players.length)game.active=g.active;game.turn=Math.max(0,Math.floor(Number(g.turn)||0));game.phase=cleanText(g.phase,40)||game.phase;game.dragon=String(g.dragon||game.dragon);game.board=cloneJson(g.b);if(g.sea&&typeof g.sea==='object')game.sea=cloneJson(g.sea);if(Array.isArray(g.deck))game.deck=g.deck.slice();if(Array.isArray(g.discard))game.discard=g.discard.slice();if(Array.isArray(g.oracleDeck))game.oracleDeck=g.oracleDeck.slice();if(Array.isArray(g.oracleDiscard))game.oracleDiscard=g.oracleDiscard.slice();game.oracleActive=g.oracleActive===null?null:Number(g.oracleActive);
 g.players.forEach((src,i)=>{const dst=game.players[i];if(!dst||!src)return;dst.gold=Number(src.gold||0);dst.pvPermanent=Number(src.pvPermanent||0);dst.hand=Array.isArray(src.hand)?src.hand.slice():dst.hand;dst.inPlay=Array.isArray(src.inPlay)?cloneJson(src.inPlay):dst.inPlay||[];dst.attackTurnBonus=Number(src.attackTurnBonus||0);dst.defenseTurnBonus=Number(src.defenseTurnBonus||0);dst.decimated=!!src.decimated;if(Number.isInteger(src.faction))dst.faction=src.faction;if(src.portrait)dst.portrait=String(src.portrait);if(src.color)dst.color=String(src.color)});return true;
}
'''
srv=repl(srv,"function publicGameView(room, socketId) {",helper+"function publicGameView(room, socketId) {",'server legacy helpers')

srv=repl(srv,
"    lastRoll: game.lastRoll,\n    play: game.status==='playing' ? {",
"    lastRoll: game.lastRoll,\n    deck: game.deck.slice(),\n    discard: game.discard.slice(),\n    oracleDeck: game.oracleDeck.slice(),\n    oracleDiscard: game.oracleDiscard.slice(),\n    legacyRevision: Number(game.legacyRevision||0),\n    legacyDriverIndex: legacyDriverIndex(room),\n    legacySnapshot: game.legacySnapshot ? cloneJson(game.legacySnapshot) : null,\n    play: game.status==='playing' ? {",
'public legacy state')

srv=repl(srv,
"      hand: i === youIndex ? p.hand.slice() : undefined,\n      handCount: p.hand.length",
"      hand: i === youIndex ? p.hand.slice() : undefined,\n      handCount: p.hand.length,\n      inPlay: Array.isArray(p.inPlay)?cloneJson(p.inPlay):[],\n      attackTurnBonus: Number(p.attackTurnBonus||0),\n      defenseTurnBonus: Number(p.defenseTurnBonus||0),\n      decimated: !!p.decimated",
'public player legacy fields')

# Initialiser les champs du moteur historique pour humains et bots.
srv=srv.replace("    hand: []\n  }));","    hand: [],\n    inPlay: [], attackTurnBonus: 0, defenseTurnBonus: 0, decimated: false\n  }));",1)
srv=srv.replace("      hand: []\n    });","      hand: [],\n      inPlay: [], attackTurnBonus: 0, defenseTurnBonus: 0, decimated: false\n    });",1)

srv=repl(srv,
"    movePool: {}, destinationUseCount: {}, attacked: [], lastEvent:null, lastRoll:null,\n    players,",
"    movePool: {}, destinationUseCount: {}, attacked: [], lastEvent:null, lastRoll:null,\n    legacyRevision:0, legacySnapshot:null,\n    players,",
'game legacy initial state')

legacy_event=r'''  socket.on('legacyStatePush', (payload = {}, ack = () => {}) => {
    const room=roomForSocket(socket);if(!room||!room.game||room.game.status!=='playing')return rejectGameAction(ack,'La partie n’est pas en cours.');const game=room.game,index=humanGameIndex(room,socket.id);if(index<0)return rejectGameAction(ack,'Joueur introuvable.');
    const revision=Math.max(0,Math.floor(Number(payload.revision)||0));if(revision!==Number(game.legacyRevision||0)){ack({ok:false,error:'État Online déjà mis à jour.',conflict:true,legacyRevision:Number(game.legacyRevision||0)});socket.emit('gameState',publicGameView(room,socket.id));return}
    let snapshot=payload.snapshot;if(!snapshot||typeof snapshot!=='object'||!snapshot.G||!Array.isArray(snapshot.G.players)||snapshot.G.players.length!==game.players.length)return rejectGameAction(ack,'État TRIBU invalide.');
    try{const packed=JSON.stringify(snapshot);if(packed.length>750000)return rejectGameAction(ack,'État TRIBU trop volumineux.');snapshot=JSON.parse(packed)}catch(_){return rejectGameAction(ack,'État TRIBU illisible.')}if(snapshot.G)delete snapshot.G.online;
    if(!projectLegacySnapshot(game,snapshot))return rejectGameAction(ack,'Impossible de synchroniser cet état.');game.legacySnapshot=snapshot;game.legacyRevision=Number(game.legacyRevision||0)+1;game.revision++;game.lastEvent={kind:'legacySync',player:index};ack({ok:true,legacyRevision:game.legacyRevision});emitGame(room);
  });

'''
srv=repl(srv,"  socket.on('gameAction', (payload = {}, ack = () => {}) => {",legacy_event+"  socket.on('gameAction', (payload = {}, ack = () => {}) => {",'legacy push socket')

INDEX.write_text(idx,encoding='utf-8')
SERVER.write_text(srv,encoding='utf-8')
print('full online legacy bridge patched')
