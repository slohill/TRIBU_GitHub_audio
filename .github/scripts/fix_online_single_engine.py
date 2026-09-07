from pathlib import Path

INDEX=Path('index.html')
SERVER=Path('server/server.js')
idx=INDEX.read_text(encoding='utf-8')
srv=SERVER.read_text(encoding='utf-8')

def repl(text, old, new, label, count=1):
    if old not in text:
        raise SystemExit(f'anchor not found: {label}')
    return text.replace(old,new,count)

# ============================================================
# CLIENT — le moteur historique TRIBU est l'unique moteur de règles.
# La couche Online ne détourne plus déplacements / cartes / Oracle.
# ============================================================
idx=repl(idx,
"let onlineSelectedMode=null,onlineReadyState=false,onlineSocket=null,onlineRoom=null,onlineGameState=null,onlineSetupSelectedRegions=[],onlineSetupDraft={color:null,portrait:null};",
"let onlineSelectedMode=null,onlineReadyState=false,onlineSocket=null,onlineRoom=null,onlineGameState=null,onlineSetupSelectedRegions=[],onlineSetupDraft={color:null,portrait:null};\nlet onlineEngineApplying=false,onlineEnginePushTimer=null,onlineEngineLastSent='',onlineEngineRevision=0;",
'online engine globals')

# Désactive seulement les anciens détours autoritaires lorsque singleEngine est actif.
for old,new,label in [
("function beginPlay(){if(G&&G.online){","function beginPlay(){if(G&&G.online&&!G.online.singleEngine){",'beginPlay'),
("function doDraw(){if(G&&G.online)return onlineGameAction('DRAW_START');","function doDraw(){if(G&&G.online&&!G.online.singleEngine)return onlineGameAction('DRAW_START');",'doDraw'),
("function doHarvest(){if(G&&G.online)return onlineGameAction('HARVEST_START');","function doHarvest(){if(G&&G.online&&!G.online.singleEngine)return onlineGameAction('HARVEST_START');",'doHarvest'),
(" if(G&&G.online)return onlineGameAction('RECRUIT_START');"," if(G&&G.online&&!G.online.singleEngine)return onlineGameAction('RECRUIT_START');",'doRecruit'),
(" if(G&&G.online)return onlineGameAction('RESET_RECRUIT');"," if(G&&G.online&&!G.online.singleEngine)return onlineGameAction('RESET_RECRUIT');",'resetRecruit'),
(" if(G&&G.online)return onlineGameAction('RECRUIT_AT',{region:r});"," if(G&&G.online&&!G.online.singleEngine)return onlineGameAction('RECRUIT_AT',{region:r});",'recruitAt'),
(" if(G&&G.online)return onlineGameAction('END_PLAY');"," if(G&&G.online&&!G.online.singleEngine)return onlineGameAction('END_PLAY');",'toOracle'),
(" if(G&&G.online)return onlineGameAction('ORACLE_ROLL');"," if(G&&G.online&&!G.online.singleEngine)return onlineGameAction('ORACLE_ROLL');",'roll'),
]:
    idx=repl(idx,old,new,label)

idx=repl(idx,
" if(G&&G.online&&onlineGameState){if(onlineGameState.status==='setup')onlineSetupRegionClick(id);else if(onlineGameState.status==='playing'&&onlineGameState.phase==='recruit'&&onlineGameState.active===onlineGameState.youIndex)recruitAt(id);else if(onlineGameState.status==='playing'&&onlineGameState.phase==='play'&&onlineGameState.active===onlineGameState.youIndex)onlineMoveClick(id);else if(onlineGameState.status==='playing'&&onlineGameState.phase==='oracleMove'&&onlineGameState.active===onlineGameState.youIndex)onlineDragonClick(id);return}",
" if(G&&G.online&&!G.online.singleEngine&&onlineGameState){if(onlineGameState.status==='setup')onlineSetupRegionClick(id);else if(onlineGameState.status==='playing'&&onlineGameState.phase==='recruit'&&onlineGameState.active===onlineGameState.youIndex)recruitAt(id);else if(onlineGameState.status==='playing'&&onlineGameState.phase==='play'&&onlineGameState.active===onlineGameState.youIndex)onlineMoveClick(id);else if(onlineGameState.status==='playing'&&onlineGameState.phase==='oracleMove'&&onlineGameState.active===onlineGameState.youIndex)onlineDragonClick(id);return}\n if(G&&G.online&&G.online.singleEngine&&!onlineSingleEngineCanAct())return;",
'clickSpot single engine')

# Un seul navigateur exécute les bots.
idx=repl(idx,
"function queueBot(reason){\n if(gameOverState)return;",
"function queueBot(reason){\n if(gameOverState)return;\n if(G&&G.online&&G.online.singleEngine&&!onlineSingleEngineDriver())return;",
'queue bot driver')

# Champs complets nécessaires au moteur historique lors du premier état Online.
idx=repl(idx,
"hand:Array.isArray(sp.hand)?sp.hand.slice():[],remoteHandCount:sp.handCount||0,inPlay:[],attackTurnBonus:0,defenseTurnBonus:0,\n   bot:!!sp.bot,decimated:false,portrait:sp.portrait||null,color:sp.color||null",
"hand:Array.isArray(sp.hand)?sp.hand.slice():[],remoteHandCount:sp.handCount||0,inPlay:Array.isArray(sp.inPlay)?JSON.parse(JSON.stringify(sp.inPlay)):[],attackTurnBonus:Number(sp.attackTurnBonus||0),defenseTurnBonus:Number(sp.defenseTurnBonus||0),\n   bot:!!sp.bot,decimated:!!sp.decimated,portrait:sp.portrait||null,color:sp.color||null",
'initial player fields')
idx=repl(idx,
"players,b:board,sea,deck:[],discard:[],log:[],oracleDeck:[],oracleDiscard:[],oracleActive:state.oracleActive===null?null:state.oracleActive,",
"players,b:board,sea,deck:Array.isArray(state.deck)?state.deck.slice():[],discard:Array.isArray(state.discard)?state.discard.slice():[],log:[],oracleDeck:Array.isArray(state.oracleDeck)?state.oracleDeck.slice():[],oracleDiscard:Array.isArray(state.oracleDiscard)?state.oracleDiscard.slice():[],oracleActive:state.oracleActive===null?null:state.oracleActive,",
'initial deck fields')
idx=repl(idx,
"online:{code:state.code,seed:state.seed,mySocketId:onlineSocket&&onlineSocket.id,myPlayerIndex:state.youIndex,hostId:onlineRoom&&onlineRoom.hostId,revision:state.revision}};",
"online:{code:state.code,seed:state.seed,mySocketId:onlineSocket&&onlineSocket.id,myPlayerIndex:state.youIndex,hostId:onlineRoom&&onlineRoom.hostId,revision:state.revision,singleEngine:true,engineRevision:Number(state.engineRevision||0),engineDriverIndex:Number.isInteger(state.engineDriverIndex)?state.engineDriverIndex:null}};",
'initial single engine flags')
idx=repl(idx,
"const pl=G.players[i];pl.name=sp.pseudo;pl.faction=Number.isInteger(sp.faction)?sp.faction:0;pl.gold=sp.gold||0;pl.pvPermanent=sp.pvPermanent||0;pl.bot=!!sp.bot;pl.portrait=sp.portrait||null;pl.color=sp.color||null;pl.remoteHandCount=sp.handCount||0;",
"const pl=G.players[i];pl.name=sp.pseudo;pl.faction=Number.isInteger(sp.faction)?sp.faction:0;pl.gold=sp.gold||0;pl.pvPermanent=sp.pvPermanent||0;pl.bot=!!sp.bot;pl.portrait=sp.portrait||null;pl.color=sp.color||null;pl.remoteHandCount=sp.handCount||0;pl.inPlay=Array.isArray(sp.inPlay)?JSON.parse(JSON.stringify(sp.inPlay)):pl.inPlay||[];pl.attackTurnBonus=Number(sp.attackTurnBonus||0);pl.defenseTurnBonus=Number(sp.defenseTurnBonus||0);pl.decimated=!!sp.decimated;",
'apply player fields')
idx=repl(idx,
" G.online.myPlayerIndex=state.youIndex;G.online.revision=state.revision;\n}",
" G.online.myPlayerIndex=state.youIndex;G.online.revision=state.revision;G.online.singleEngine=true;G.online.engineRevision=Number(state.engineRevision||0);G.online.engineDriverIndex=Number.isInteger(state.engineDriverIndex)?state.engineDriverIndex:null;\n G.deck=Array.isArray(state.deck)?state.deck.slice():G.deck||[];G.discard=Array.isArray(state.discard)?state.discard.slice():G.discard||[];G.oracleDeck=Array.isArray(state.oracleDeck)?state.oracleDeck.slice():G.oracleDeck||[];G.oracleDiscard=Array.isArray(state.oracleDiscard)?state.oracleDiscard.slice():G.oracleDiscard||[];\n}",
'apply engine fields')

bridge=r'''function onlineSingleEngineDriver(){return !!(G&&G.online&&G.online.singleEngine&&G.online.engineDriverIndex===G.online.myPlayerIndex)}
function onlineSingleEngineExpectedActor(){
 if(!G)return null;
 if(battle&&battle.kind!=='seaChoice'&&Array.isArray(battle.priorityOrder)&&battle.priorityOrder.length)return battle.priorityOrder[battle.priorityIndex||0];
 if(goldReaction&&Number.isInteger(goldReaction.receiver))return goldReaction.receiver;
 if(caravanState&&Array.isArray(caravanState.order)&&Number.isInteger(caravanState.pick))return caravanState.order[caravanState.pick];
 if(choiceState&&Number.isInteger(choiceState.player))return choiceState.player;
 if(shadowState&&Number.isInteger(shadowState.player))return shadowState.player;
 if(divinationState&&Number.isInteger(divinationState.actor))return divinationState.actor;
 for(const s of [returnState,dragonRichState,dragonCurseState,dragonPublicState,dragonSixState,oracleState])if(s&&Number.isInteger(s.player))return s.player;
 return Number.isInteger(G.active)?G.active:null;
}
function onlineSingleEngineCanAct(){
 if(!G||!G.online||!G.online.singleEngine||onlineWelcomeActive)return false;
 const expected=onlineSingleEngineExpectedActor(),me=G.online.myPlayerIndex;if(!Number.isInteger(expected)||!Number.isInteger(me))return false;
 const ep=G.players[expected];return expected===me||!!(ep&&ep.bot&&onlineSingleEngineDriver());
}
function onlineSingleEngineShared(){
 const copy=v=>v===undefined?null:JSON.parse(JSON.stringify(v));
 return {battle:copy(battle),battleStack:copy(battleStack),goldReaction:copy(goldReaction),caravanState:copy(caravanState),choiceState:copy(choiceState),shadowState:copy(shadowState),egnoState:copy(egnoState),returnState:copy(returnState),dragonRichState:copy(dragonRichState),dragonCurseState:copy(dragonCurseState),dragonPublicState:copy(dragonPublicState),dragonSixState:copy(dragonSixState),oraclePassArmed:!!oraclePassArmed,oracleState:copy(oracleState),seaStormState:copy(seaStormState),oracleNoticeState:copy(oracleNoticeState),oracleClimateVisual:copy(oracleClimateVisual),oraclePendingNormalMap:!!oraclePendingNormalMap,oracleResolutionAfter:copy(oracleResolutionAfter),oracleResolutionTurnEpoch:copy(oracleResolutionTurnEpoch),turnEpoch:Number(turnEpoch||0),divinationState:copy(divinationState),recruitSnapshot:copy(recruitSnapshot),gameOverState:copy(gameOverState),botActionsThisTurn:Number(botActionsThisTurn||0),movable:copy(movable),usedDest:[...usedDest],destinationUseCount:copy(destinationUseCount),attacked:[...attacked],cycle:Number(cycle||1),commerceDeals:copy(commerceDeals),commerceSeq:Number(commerceSeq||1),commerceBattlePaused:!!commerceBattlePaused};
}
function onlineSingleEngineSnapshot(){
 if(!G)return null;const game=JSON.parse(JSON.stringify(G));delete game.online;
 return {game,shared:onlineSingleEngineShared()};
}
function onlineSingleEngineApply(snapshot,state){
 if(!snapshot||!snapshot.game)return false;onlineEngineApplying=true;clearTimeout(onlineEnginePushTimer);clearTimeout(botTimer);clearTimeout(botReactionTimer);clearInterval(battleTick);clearInterval(paidDrawTick);clearInterval(goldReactionTick);clearInterval(shadowTick);clearInterval(dragonSixTick);clearInterval(oracleNoticeTick);
 const me=state.youIndex,oldOnline=G&&G.online?{...G.online}:{};const s=JSON.parse(JSON.stringify(snapshot));G=s.game;G.online={...oldOnline,code:state.code,seed:state.seed,mySocketId:onlineSocket&&onlineSocket.id,myPlayerIndex:me,hostId:onlineRoom&&onlineRoom.hostId,revision:state.revision,singleEngine:true,engineRevision:Number(state.engineRevision||0),engineDriverIndex:Number.isInteger(state.engineDriverIndex)?state.engineDriverIndex:null};
 const sh=s.shared||{};battle=sh.battle||null;battleStack=sh.battleStack||[];goldReaction=sh.goldReaction||null;caravanState=sh.caravanState||null;choiceState=sh.choiceState||null;shadowState=sh.shadowState||null;egnoState=sh.egnoState||null;returnState=sh.returnState||null;dragonRichState=sh.dragonRichState||null;dragonCurseState=sh.dragonCurseState||null;dragonPublicState=sh.dragonPublicState||null;dragonSixState=sh.dragonSixState||null;oraclePassArmed=!!sh.oraclePassArmed;oracleState=sh.oracleState||null;seaStormState=sh.seaStormState||null;oracleNoticeState=sh.oracleNoticeState||null;oracleClimateVisual=sh.oracleClimateVisual||null;oraclePendingNormalMap=!!sh.oraclePendingNormalMap;oracleResolutionAfter=sh.oracleResolutionAfter??null;oracleResolutionTurnEpoch=sh.oracleResolutionTurnEpoch??null;turnEpoch=Number(sh.turnEpoch||0);divinationState=sh.divinationState||null;recruitSnapshot=sh.recruitSnapshot||null;gameOverState=sh.gameOverState||null;botActionsThisTurn=Number(sh.botActionsThisTurn||0);movable=sh.movable||{};usedDest=new Set(sh.usedDest||[]);destinationUseCount=sh.destinationUseCount||{};attacked=new Set(sh.attacked||[]);cycle=Number(sh.cycle||1);commerceDeals=Array.isArray(sh.commerceDeals)?sh.commerceDeals:[];commerceSeq=Number(sh.commerceSeq||1);commerceBattlePaused=!!sh.commerceBattlePaused;
 // Les brouillons de clic restent locaux : jamais de destination/picks distants injectés.
 dest=null;picks={};onlineEngineRevision=Number(state.engineRevision||0);onlineEngineLastSent=JSON.stringify(s);onlineEngineApplying=false;return true;
}
function onlineSingleEngineLock(){
 if(!G||!G.online||!G.online.singleEngine)return;const can=onlineSingleEngineCanAct(),mapEl=$('map'),hand=$('hand');if(mapEl)mapEl.style.pointerEvents=can?'':'none';if(hand)hand.style.pointerEvents=can?'':'none';
 if(!can)['draw','harvest','recruit','resetRecruit','endRecruit','toOracle','roll'].forEach(id=>{const b=$(id);if(b)b.disabled=true});
 const n=$('status');if(n&&!n.querySelector('.onlineSingleEngineNotice'))n.insertAdjacentHTML('beforeend','<div class="botNotice onlineSingleEngineNotice">🌐 Online — règles du jeu original synchronisées.</div>');
}
function onlineSingleEngineSchedulePush(){
 if(onlineEngineApplying||!G||!G.online||!G.online.singleEngine||!onlineSocket||!onlineSocket.connected||!onlineSingleEngineCanAct())return;clearTimeout(onlineEnginePushTimer);onlineEnginePushTimer=setTimeout(onlineSingleEnginePush,80);
}
function onlineSingleEnginePush(){
 if(onlineEngineApplying||!G||!G.online||!G.online.singleEngine||!onlineSocket||!onlineSocket.connected||!onlineSingleEngineCanAct())return;const snapshot=onlineSingleEngineSnapshot();if(!snapshot)return;const sig=JSON.stringify(snapshot);if(sig===onlineEngineLastSent)return;const revision=Number(G.online.engineRevision||onlineEngineRevision||0),actor=G.online.myPlayerIndex;
 onlineSocket.emit('singleEnginePush',{revision,actor,snapshot},res=>{if(res&&res.ok){G.online.engineRevision=Number(res.engineRevision||revision+1);onlineEngineRevision=G.online.engineRevision;onlineEngineLastSent=sig;return}onlineAck('requestGameState',{}).then(r=>applyOnlineGameState(r.game)).catch(onlineError)});
}
'''
idx=repl(idx,"function onlineLockControls(){",bridge+"function onlineLockControls(){\n if(G&&G.online&&G.online.singleEngine){onlineSingleEngineLock();return}",'single engine lock bridge')

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
 if(state.engineSnapshot)onlineSingleEngineApply(state.engineSnapshot,state);else{onlineApplyStateToDisplay(state);G.online.singleEngine=true;G.online.engineRevision=Number(state.engineRevision||0);G.online.engineDriverIndex=Number.isInteger(state.engineDriverIndex)?state.engineDriverIndex:null;onlineEngineRevision=G.online.engineRevision;onlineEngineLastSent=''}
 setupState=null;onlineSetupLayout(false);$('setupPanel').classList.add('hidden');$('start').classList.add('hidden');$('game').classList.remove('hidden');render();
 if(state.status==='playing'&&(wasSetup||onlineWelcomeShownKey!==String(state.seed||'game')))onlineShowGameWelcome(state);
 onlineLockControls();if(!state.engineSnapshot)onlineSingleEngineSchedulePush();if(G&&G.online&&G.online.singleEngine&&isBot()&&onlineSingleEngineDriver())queueBot('synchronisation Online');
}"""
idx=repl(idx,old_apply,new_apply,'apply online state')

idx=repl(idx,
"function onlineGameAction(type,payload={}){return onlineAck('gameAction',{type,...payload}).catch(onlineError)}\nfunction renderOnlineLobby(room){",
"function onlineGameAction(type,payload={}){return onlineAck('gameAction',{type,...payload}).catch(onlineError)}\nconst onlineSingleEngineBaseRender=render;render=function(){onlineSingleEngineBaseRender();if(G&&G.online&&G.online.singleEngine){onlineSingleEngineLock();onlineSingleEngineSchedulePush()}};\nfunction renderOnlineLobby(room){",
'render wrapper')

# ============================================================
# SERVEUR — stocke l'état canonique du moteur original.
# L'ancien moteur autoritaire reste présent mais n'est plus appelé par le client.
# ============================================================
helper=r'''function cloneJson(value){return value===undefined?undefined:JSON.parse(JSON.stringify(value))}
function singleEngineDriverIndex(room){if(!room||!room.game)return -1;for(let i=0;i<room.game.players.length;i++){const p=room.game.players[i];if(!p.bot&&p.connected!==false)return i}return -1}
function singleEngineExpectedActor(game){
 const s=game.engineSnapshot&&game.engineSnapshot.shared||{},b=s.battle;
 if(b&&b.kind!=='seaChoice'&&Array.isArray(b.priorityOrder)&&b.priorityOrder.length)return Number(b.priorityOrder[Number(b.priorityIndex||0)]);
 if(s.goldReaction&&Number.isInteger(s.goldReaction.receiver))return s.goldReaction.receiver;
 if(s.caravanState&&Array.isArray(s.caravanState.order)&&Number.isInteger(s.caravanState.pick))return Number(s.caravanState.order[s.caravanState.pick]);
 if(s.choiceState&&Number.isInteger(s.choiceState.player))return s.choiceState.player;
 if(s.shadowState&&Number.isInteger(s.shadowState.player))return s.shadowState.player;
 if(s.divinationState&&Number.isInteger(s.divinationState.actor))return s.divinationState.actor;
 for(const k of ['returnState','dragonRichState','dragonCurseState','dragonPublicState','dragonSixState','oracleState'])if(s[k]&&Number.isInteger(s[k].player))return s[k].player;
 return Number.isInteger(game.active)?game.active:-1;
}
function singleEngineCanPush(room,index){const game=room.game,expected=singleEngineExpectedActor(game),p=game.players[expected];if(expected===index)return true;return !!(p&&p.bot&&index===singleEngineDriverIndex(room))}
function projectSingleEngine(game,snapshot){
 const g=snapshot&&snapshot.game;if(!g||!Array.isArray(g.players)||!g.b||typeof g.b!=='object')return false;
 game.active=Number.isInteger(g.active)?g.active:game.active;game.turn=Math.max(0,Math.floor(Number(g.turn)||0));game.phase=cleanText(g.phase,40)||game.phase;game.dragon=String(g.dragon||game.dragon);game.board=cloneJson(g.b);if(g.sea&&typeof g.sea==='object')game.sea=cloneJson(g.sea);if(Array.isArray(g.deck))game.deck=g.deck.slice();if(Array.isArray(g.discard))game.discard=g.discard.slice();if(Array.isArray(g.oracleDeck))game.oracleDeck=g.oracleDeck.slice();if(Array.isArray(g.oracleDiscard))game.oracleDiscard=g.oracleDiscard.slice();game.oracleActive=g.oracleActive===null?null:Number(g.oracleActive);
 g.players.forEach((src,i)=>{const dst=game.players[i];if(!dst||!src)return;dst.gold=Number(src.gold||0);dst.pvPermanent=Number(src.pvPermanent||0);dst.hand=Array.isArray(src.hand)?src.hand.slice():dst.hand;dst.inPlay=Array.isArray(src.inPlay)?cloneJson(src.inPlay):dst.inPlay||[];dst.attackTurnBonus=Number(src.attackTurnBonus||0);dst.defenseTurnBonus=Number(src.defenseTurnBonus||0);dst.decimated=!!src.decimated;if(Number.isInteger(src.faction))dst.faction=src.faction;if(src.portrait)dst.portrait=String(src.portrait);if(src.color)dst.color=String(src.color)});return true;
}
'''
srv=repl(srv,"function publicGameView(room, socketId) {",helper+"function publicGameView(room, socketId) {",'server helpers')

srv=repl(srv,
"    lastRoll: game.lastRoll,\n    play: game.status==='playing' ? {",
"    lastRoll: game.lastRoll,\n    deck: game.deck.slice(),\n    discard: game.discard.slice(),\n    oracleDeck: game.oracleDeck.slice(),\n    oracleDiscard: game.oracleDiscard.slice(),\n    engineRevision: Number(game.engineRevision||0),\n    engineDriverIndex: singleEngineDriverIndex(room),\n    engineSnapshot: game.engineSnapshot ? cloneJson(game.engineSnapshot) : null,\n    play: game.status==='playing' ? {",
'public engine fields')
srv=repl(srv,
"      hand: i === youIndex ? p.hand.slice() : undefined,\n      handCount: p.hand.length",
"      hand: i === youIndex ? p.hand.slice() : undefined,\n      handCount: p.hand.length,\n      inPlay: Array.isArray(p.inPlay)?cloneJson(p.inPlay):[],\n      attackTurnBonus: Number(p.attackTurnBonus||0),\n      defenseTurnBonus: Number(p.defenseTurnBonus||0),\n      decimated: !!p.decimated",
'public player fields')

srv=srv.replace("    hand: []\n  }));","    hand: [],\n    inPlay: [], attackTurnBonus: 0, defenseTurnBonus: 0, decimated: false\n  }));",1)
srv=srv.replace("      hand: []\n    });","      hand: [],\n      inPlay: [], attackTurnBonus: 0, defenseTurnBonus: 0, decimated: false\n    });",1)
srv=repl(srv,
"    movePool: {}, destinationUseCount: {}, attacked: [], lastEvent:null, lastRoll:null,\n    players,",
"    movePool: {}, destinationUseCount: {}, attacked: [], lastEvent:null, lastRoll:null,\n    singleEngine:true, engineRevision:0, engineSnapshot:null,\n    players,",
'engine initial game')

# Empêche le squelette de bots serveur de concurrencer les bots historiques du moteur client.
srv=repl(srv,
"function scheduleBotTurn(room){\n  if(!room||!room.game||room.game.status!=='playing')return;",
"function scheduleBotTurn(room){\n  if(!room||!room.game||room.game.status!=='playing')return;\n  if(room.game.singleEngine)return;",
'disable server bots single engine')

socket_event=r'''  socket.on('singleEnginePush', (payload = {}, ack = () => {}) => {
    const room=roomForSocket(socket);if(!room||!room.game||room.game.status!=='playing')return rejectGameAction(ack,'La partie n’est pas en cours.');const game=room.game,index=humanGameIndex(room,socket.id);if(index<0)return rejectGameAction(ack,'Joueur introuvable.');
    if(!singleEngineCanPush(room,index))return rejectGameAction(ack,'Ce joueur ne peut pas agir maintenant.');
    const revision=Math.max(0,Math.floor(Number(payload.revision)||0));if(revision!==Number(game.engineRevision||0)){ack({ok:false,error:'État Online déjà mis à jour.',conflict:true,engineRevision:Number(game.engineRevision||0)});socket.emit('gameState',publicGameView(room,socket.id));return}
    let snapshot=payload.snapshot;if(!snapshot||typeof snapshot!=='object'||!snapshot.game||!Array.isArray(snapshot.game.players)||snapshot.game.players.length!==game.players.length)return rejectGameAction(ack,'État TRIBU invalide.');
    try{const packed=JSON.stringify(snapshot);if(packed.length>650000)return rejectGameAction(ack,'État TRIBU trop volumineux.');snapshot=JSON.parse(packed)}catch(_){return rejectGameAction(ack,'État TRIBU illisible.')}if(snapshot.game)delete snapshot.game.online;
    if(!projectSingleEngine(game,snapshot))return rejectGameAction(ack,'Impossible de synchroniser cet état.');game.engineSnapshot=snapshot;game.engineRevision=Number(game.engineRevision||0)+1;game.revision++;game.lastEvent={kind:'singleEngineSync',player:index};ack({ok:true,engineRevision:game.engineRevision});emitGame(room);
  });

'''
srv=repl(srv,"  socket.on('gameAction', (payload = {}, ack = () => {}) => {",socket_event+"  socket.on('gameAction', (payload = {}, ack = () => {}) => {",'single engine socket')

INDEX.write_text(idx,encoding='utf-8')
SERVER.write_text(srv,encoding='utf-8')
print('single engine online patched')
