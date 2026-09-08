from pathlib import Path
p=Path('index.html')
s=p.read_text(encoding='utf-8')

def rep(old,new,label):
    global s
    if old not in s:
        raise SystemExit('MISSING '+label)
    s=s.replace(old,new,1)

rep("""function queueBot(reason){
 if(gameOverState)return;
 clearTimeout(botTimer);
 const token=++botToken;
 if(!G || !isBot() || battle || shadowState || paidDrawState || goldReaction)return;
 botTimer=setTimeout(()=>{
   botTimer=null;
   if(token!==botToken || !G || !isBot() || battle || shadowState || paidDrawState || goldReaction)return;
   botAdvance();
 },650);
}""","""function priorityCardResolutionActive(){
 return !!(divinationState||caravanState||egnoState||shadowState||portalMode||
   (choiceState&&choiceState.kind==='council')||agentModalState);
}
function priorityCardResolutionActor(){
 if(divinationState&&Number.isInteger(divinationState.actor))return divinationState.actor;
 if(choiceState&&choiceState.kind==='council'&&Number.isInteger(choiceState.player))return choiceState.player;
 if(caravanState){
   const chooser=Array.isArray(caravanState.order)?caravanState.order[caravanState.pick]:null;
   if(Number.isInteger(chooser))return chooser;
   if(Number.isInteger(caravanState.actor))return caravanState.actor;
 }
 if(egnoState&&Number.isInteger(egnoState.player))return egnoState.player;
 if(shadowState&&Number.isInteger(shadowState.player))return shadowState.player;
 if(portalMode&&Number.isInteger(portalMode.owner))return portalMode.owner;
 if(agentModalState&&Number.isInteger(agentModalState.actor))return agentModalState.actor;
 if(agentModalState&&Number.isInteger(agentModalState.chooser))return agentModalState.chooser;
 return null;
}
function pauseGameForPriorityCard(){
 clearTimeout(botTimer);botTimer=null;botToken++;
 if(battle){clearInterval(battleTick);clearTimeout(botReactionTimer)}
}
function resumeGameAfterPriorityCard(reason='reprise après carte prioritaire'){
 if(priorityCardResolutionActive())return;
 if(G&&G.players&&G.players[G.active]&&G.players[G.active].bot)queueBot(reason);
}
function queueBot(reason){
 if(gameOverState)return;
 clearTimeout(botTimer);
 const token=++botToken;
 if(!G || !isBot() || battle || shadowState || paidDrawState || goldReaction || priorityCardResolutionActive())return;
 botTimer=setTimeout(()=>{
   botTimer=null;
   if(token!==botToken || !G || !isBot() || battle || shadowState || paidDrawState || goldReaction || priorityCardResolutionActive())return;
   botAdvance();
 },650);
}""","priority helpers + queue bot")

rep("if(!G||gameOverState||!isBot()||battle||shadowState||paidDrawState||goldReaction)return;","if(!G||gameOverState||!isBot()||battle||shadowState||paidDrawState||goldReaction||priorityCardResolutionActive())return;","oracle bot guard")
rep("if(!G || !isBot() || battle || goldReaction)return;","if(!G || !isBot() || battle || goldReaction || priorityCardResolutionActive())return;","bot advance guard")

rep("""function resumeAfterDivination(s){
 if(s&&s.parentBattle&&battle){
   battle.seconds=s.parentSeconds||battle.seconds||15;
   resumeBattleTimer();
 }
 render();
}""","""function resumeAfterDivination(s){
 if(s&&s.parentBattle&&battle){
   battle.seconds=s.parentSeconds||battle.seconds||15;
   resumeBattleTimer();
 }
 render();
 resumeGameAfterPriorityCard('reprise après Divination');
}""","resume divination")

rep(""" divinationState={actor,cardId:id,parentBattle:battle||null,parentSeconds:battle?battle.seconds:null};
 pauseForDivination();
 $('divinationText').textContent='Choisissez : activer l’Oracle visible ou choisir un nouvel Oracle.';""",""" divinationState={actor,cardId:id,parentBattle:battle||null,parentSeconds:battle?battle.seconds:null,stage:'choice'};
 pauseGameForPriorityCard();
 pauseForDivination();
 $('divinationText').textContent='Choisissez : activer l’Oracle visible ou choisir un nouvel Oracle.';""","open divination pause")
rep(""" $('divinationPanel').classList.remove('hidden');
}""",""" $('divinationPanel').classList.remove('hidden');
 render();
 if(G&&G.online&&G.online.legacySync)onlineLegacyPushPriorityCardNow();
}""","open divination publish")

rep(""" s.committed=true;
 divinationState=null;$('divinationPanel').classList.add('hidden');
 log(p(s.actor).name+' joue Divination de l’Oracle et active l’Oracle visible.');
 activateOracle(()=>resumeAfterDivination(s),s.actor);""",""" s.committed=true;
 s.stage='resolvingOracle';
 $('divinationPanel').classList.add('hidden');
 log(p(s.actor).name+' joue Divination de l’Oracle et active l’Oracle visible.');
 // La continuation reste sérialisable dans divinationState : aucune fonction callback
 // n'est nécessaire pour reprendre correctement une Divination Online.
 activateOracle(null,s.actor);""","serializable divination continuation")

rep(""" // Pour l'Oracle normal de fin de tour, la résolution n'a le droit de terminer
 // le tour que si le joueur est encore réellement dans la phase Oracle.
 // Les Divinations ont un callback (cb) et restent autorisées hors de cette phase.
 if(!cb&&G.phase!=='oracleResolving'){""",""" const divinationResume=(divinationState&&divinationState.stage==='resolvingOracle')?divinationState:null;
 // Pour l'Oracle normal de fin de tour, la résolution n'a le droit de terminer
 // le tour que si le joueur est encore réellement dans la phase Oracle.
 // Une Divination conserve un marqueur sérialisable jusqu'à la fin de l'Oracle.
 if(!cb&&!divinationResume&&G.phase!=='oracleResolving'){""","divination phase guard")
rep(""" oracleResolutionAfter=null;
 oracleResolutionTurnEpoch=null;
 if(cb){cb();return}
 advanceTurn('Oracle résolu');""",""" oracleResolutionAfter=null;
 oracleResolutionTurnEpoch=null;
 if(divinationResume){
   divinationState=null;
   resumeAfterDivination(divinationResume);
   return;
 }
 if(cb){cb();return}
 advanceTurn('Oracle résolu');""","divination resume marker")

rep("""function startEgnobombe(handIndex){
 const actor=localViewer(),id=G.players[actor].hand[handIndex];
 if(id===undefined||CARDS[id].name!=='Egnobombe'||!canPlayEgnobombe(actor))return;
 egnoState={player:actor,cardId:id,parentBattle:battle||null,parentSeconds:battle?battle.seconds:null};
 if(battle){clearInterval(battleTick);clearTimeout(botReactionTimer)}
 log(p(actor).name+' prépare Egnobombe : choisissez une case où vous avez au moins 5 unités, région ou aire maritime.');
 render();
}""","""function startEgnobombe(handIndex){
 const actor=localViewer(),id=G.players[actor].hand[handIndex];
 if(id===undefined||CARDS[id].name!=='Egnobombe'||!canPlayEgnobombe(actor))return;
 egnoState={player:actor,cardId:id,parentBattle:battle||null,parentSeconds:battle?battle.seconds:null};
 pauseGameForPriorityCard();
 log(p(actor).name+' prépare Egnobombe : choisissez une case où vous avez au moins 5 unités, région ou aire maritime.');
 render();
 if(G&&G.online&&G.online.legacySync)onlineLegacyPushPriorityCardNow();
}""","egno pause")

rep(""" shadowState={stage:'gather',player:actor,cardId:id,handIndex,seconds:20,picks:{},parentBattle:battle||null,parentBattleSeconds:battle?battle.seconds:null};
 if(battle){clearInterval(battleTick);clearTimeout(botReactionTimer)}""",""" shadowState={stage:'gather',player:actor,cardId:id,handIndex,seconds:20,picks:{},parentBattle:battle||null,parentBattleSeconds:battle?battle.seconds:null};
 pauseGameForPriorityCard();""","shadow pause")
rep(""" if(!isHotseatMode())shadowTick=setInterval(()=>{if(!shadowState||shadowState.stage!=='gather'){clearInterval(shadowTick);return}shadowState.seconds--;if(shadowState.seconds<=0){cancelShadow(true);return}render()},1000);
 render();
}""",""" if(!isHotseatMode())shadowTick=setInterval(()=>{if(!shadowState||shadowState.stage!=='gather'){clearInterval(shadowTick);return}shadowState.seconds--;if(shadowState.seconds<=0){cancelShadow(true);return}render()},1000);
 render();
 if(G&&G.online&&G.online.legacySync)onlineLegacyPushPriorityCardNow();
}""","shadow publish")

rep(""" agentModalState={kind:'assassin',actor,handIndex,cardId:id};
 openAgentModal('Assassin','Choisissez l’Agent adverse à assassiner.');""",""" agentModalState={kind:'assassin',actor,handIndex,cardId:id};
 pauseGameForPriorityCard();
 openAgentModal('Assassin','Choisissez l’Agent adverse à assassiner.');""","assassin pause")
rep(""" targets.forEach(t=>{
   const b=document.createElement('button');
   b.textContent=p(t.owner).name+' — '+t.name;
   b.onclick=()=>resolveAssassin(t);
   box.appendChild(b);
 });
}""",""" targets.forEach(t=>{
   const b=document.createElement('button');
   b.textContent=p(t.owner).name+' — '+t.name;
   b.onclick=()=>resolveAssassin(t);
   box.appendChild(b);
 });
 render();
 if(G&&G.online&&G.online.legacySync)onlineLegacyPushPriorityCardNow();
}""","assassin publish")

rep("""function startCaravan(handIndex){
 const actor=localViewer(),id=G.players[actor].hand[handIndex];
 if(id===undefined||CARDS[id].name!=='Caravane de commerce'||isDecimated(actor)||caravanState)return;
 const pausedBattle=!!battle;""","""function startCaravan(handIndex){
 const actor=localViewer(),id=G.players[actor].hand[handIndex];
 if(id===undefined||CARDS[id].name!=='Caravane de commerce'||isDecimated(actor)||caravanState)return;
 pauseGameForPriorityCard();
 const pausedBattle=!!battle;""","caravan pause")
rep(""" log(p(actor).name+' joue Caravane de commerce : '+revealed.length+' carte(s) révélée(s).'+(pausedBattle?' La bataille est mise en pause.':''));
 showCaravanChoice();
}""",""" log(p(actor).name+' joue Caravane de commerce : '+revealed.length+' carte(s) révélée(s).'+(pausedBattle?' La bataille est mise en pause.':''));
 showCaravanChoice();
 render();
 if(G&&G.online&&G.online.legacySync)onlineLegacyPushPriorityCardNow();
}""","caravan publish")
rep(""" render();
}
function pauseForDivination(){""",""" render();
 resumeGameAfterPriorityCard('reprise après Caravane');
}
function pauseForDivination(){""","caravan resume")

rep(""" const pausedGold=!!goldReaction;if(pausedGold)pauseGoldReactionForCard();
 if(battleCouncil){""",""" const pausedGold=!!goldReaction;if(pausedGold)pauseGoldReactionForCard();
 pauseGameForPriorityCard();
 if(battleCouncil){""","council pause")
rep(""" $('choiceOverlay').classList.remove('hidden');renderCouncilChoices();
}""",""" $('choiceOverlay').classList.remove('hidden');renderCouncilChoices();render();
 if(G&&G.online&&G.online.legacySync)onlineLegacyPushPriorityCardNow();
}""","council publish")
rep(""" render();if(pausedGold)resumeGoldReactionAfterCard();
}""",""" render();if(pausedGold)resumeGoldReactionAfterCard();
 resumeGameAfterPriorityCard('reprise après Conseil de guerre');
}""","council resume")

rep(""" log(p(receiver).name+' joue Taxe : '+gain+' Or sont sur le point d’être gagnés.');
 offerGoldGain(receiver,gain,'Taxe','render');
}""",""" log(p(receiver).name+' joue Taxe : '+gain+' Or sont sur le point d’être gagnés.');
 offerGoldGain(receiver,gain,'Taxe','render');
 if(G&&G.online&&G.online.legacySync)onlineLegacyPushGoldReactionNow();
}""","tax publish")

rep("""function onlineLegacyCanPublish(){
 if(!G||!G.online||!G.online.legacySync||onlineLegacyApplying||!onlineSocket)return false;
 const me=G.online.myPlayerIndex;if(!Number.isInteger(me)||!G.players[me]||G.players[me].bot)return false;""","""function onlineLegacyCanPublish(){
 if(!G||!G.online||!G.online.legacySync||onlineLegacyApplying||!onlineSocket)return false;
 const me=G.online.myPlayerIndex;if(!Number.isInteger(me)||!G.players[me]||G.players[me].bot)return false;
 if(priorityCardResolutionActor()===me)return true;""","priority actor publish")

insert_after="""function onlineLegacyPushGoldReactionNow(){"""
pos=s.find(insert_after)
if pos<0: raise SystemExit('MISSING push gold function')
# insert helper before existing gold helper
helper="""function onlineLegacyPushPriorityCardNow(){
 if(!G||!G.online||!G.online.legacySync||onlineLegacyApplying||!onlineSocket||!priorityCardResolutionActive())return;
 const actorIndex=G.online.myPlayerIndex;if(!Number.isInteger(actorIndex)||priorityCardResolutionActor()!==actorIndex)return;
 clearTimeout(onlineLegacyPushTimer);
 const snapshot=onlineLegacySnapshot(),digest=onlineLegacyDigest();
 const send=(baseRevision,retries)=>onlineAck('legacyCommit',{baseRevision,actorIndex,snapshot}).then(res=>{
   onlineLegacyRevision=Math.max(onlineLegacyRevision,res.revision||0);G.online.revision=onlineLegacyRevision;onlineLegacyLastDigest=digest;
 }).catch(err=>{
   if(err&&err.current&&retries>0&&Number.isInteger(err.current.revision)){
     onlineLegacyRevision=Math.max(onlineLegacyRevision,err.current.revision);G.online.revision=onlineLegacyRevision;
     return send(onlineLegacyRevision,retries-1);
   }
   onlineLegacyLastDigest='';if(err&&err.current)onlineLegacyApply(err.current);else onlineError(err);
 });
 send(onlineLegacyRevision,2);
}
"""
s=s[:pos]+helper+s[pos:]

rep(""" (G.players||[]).forEach((_,i)=>agentDefaults(i));
 onlineLegacyLastDigest=onlineLegacyDigest();render();""",""" (G.players||[]).forEach((_,i)=>agentDefaults(i));
 if(priorityCardResolutionActive()){clearTimeout(botTimer);botTimer=null;botToken++}
 onlineLegacyLastDigest=onlineLegacyDigest();render();""","remote pause bot")

rep(""" const start=mine&&G.phase==='start'&&!paidDrawState&&!goldReaction,recruiting=mine&&G.phase==='recruit',playing=mine&&G.phase==='play',oracleRoll=mine&&G.phase==='oracleRoll';""",""" const cardPause=priorityCardResolutionActive();
 const start=mine&&G.phase==='start'&&!paidDrawState&&!goldReaction&&!cardPause,recruiting=mine&&G.phase==='recruit'&&!cardPause,playing=mine&&G.phase==='play'&&!cardPause,oracleRoll=mine&&G.phase==='oracleRoll'&&!cardPause;""","online control pause")
rep("if(!mine||goldReaction){['recruitBox','playBox','oracleBox'].forEach(id=>{const el=$(id);if(el)el.classList.add('hidden')})}","if(!mine||goldReaction||cardPause){['recruitBox','playBox','oracleBox'].forEach(id=>{const el=$(id);if(el)el.classList.add('hidden')})}","online hide phase boxes")
rep("if(goldReaction&&s)s.classList.add('hidden')","if((goldReaction||cardPause)&&s)s.classList.add('hidden')","online hide start")

rep(""" $('startTurn').classList.toggle('hidden',G.phase!=='start'||isDecimated(G.active));""",""" const cardPause=priorityCardResolutionActive();
 $('startTurn').classList.toggle('hidden',G.phase!=='start'||isDecimated(G.active)||cardPause);""","base start hide")
rep("$('recruitBox').classList.toggle('hidden',G.phase!=='recruit');","$('recruitBox').classList.toggle('hidden',G.phase!=='recruit'||cardPause);","base recruit hide")
rep("$('playBox').classList.toggle('hidden',G.phase!=='play');","$('playBox').classList.toggle('hidden',G.phase!=='play'||cardPause);","base play hide")
rep("$('oracleBox').classList.toggle('hidden',!['oracleMove','oracleRoll'].includes(G.phase));","$('oracleBox').classList.toggle('hidden',!['oracleMove','oracleRoll'].includes(G.phase)||cardPause);","base oracle hide")
rep("if(goldReaction){['startTurn','recruitBox','playBox','oracleBox'].forEach(id=>{const el=$(id);if(el)el.classList.add('hidden')})}","if(goldReaction||cardPause){['startTurn','recruitBox','playBox','oracleBox'].forEach(id=>{const el=$(id);if(el)el.classList.add('hidden')})}","base all hide")

rep("if(gameOverState||battle||shadowState||paidDrawState||goldReaction||oracleNoticeState||dragonSixState||dragonPublicState||dragonCurseState||caravanState||divinationState)return;","if(gameOverState||battle||shadowState||paidDrawState||goldReaction||oracleNoticeState||dragonSixState||dragonPublicState||dragonCurseState||caravanState||divinationState||priorityCardResolutionActive())return;","watchdog pause")

p.write_text(s,encoding='utf-8')
