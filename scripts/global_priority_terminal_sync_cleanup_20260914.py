from pathlib import Path
import re

p=Path('index.html')
s=p.read_text(encoding='utf-8')

old="let onlineLegacyRevision=0,onlineLegacyApplying=false,onlineLegacyLastDigest='',onlineLegacyPushTimer=null,onlineLegacyBotDriverIndex=null,onlineLegacyBattleViewSeconds=null,onlineLegacyGoldViewSeconds=null,onlineLegacyGoldTickRender=false;"
new="let onlineLegacyRevision=0,onlineLegacyApplying=false,onlineLegacyLastDigest='',onlineLegacyPushTimer=null,onlineLegacyBotDriverIndex=null,onlineLegacyBattleViewSeconds=null,onlineLegacyGoldViewSeconds=null,onlineLegacyGoldTickRender=false,onlineLegacyPriorityWasActive=false,onlineLegacyPriorityTrackedActor=null,onlineLegacyPriorityTerminalPending=false;"
assert old in s
s=s.replace(old,new,1)

needle="function onlineLegacyCanPublish(){\n if(!G||!G.online||!G.online.legacySync||onlineLegacyApplying||!onlineSocket)return false;"
insert="""function onlineLegacyCanCommitPriorityTerminal(owner){
 if(!G||!G.online||!G.online.legacySync||onlineLegacyApplying||!onlineSocket)return false;
 const me=G.online.myPlayerIndex;
 if(!Number.isInteger(me)||!G.players[me]||G.players[me].bot)return false;
 if(Number.isInteger(owner)&&G.players[owner]&&!G.players[owner].bot)return owner===me;
 if(Number.isInteger(owner)&&G.players[owner]&&G.players[owner].bot)return onlineLegacyCanExecuteBot();
 return false;
}
function onlineLegacyPushPriorityTerminalNow(owner){
 // Une fois une résolution prioritaire terminée, son état a déjà disparu des variables
 // de résolution. On conserve donc explicitement l'acteur et on commite le snapshot
 // terminal exact, au lieu de dépendre du joueur actif ou d'un prochain render.
 onlineLegacyPriorityWasActive=false;onlineLegacyPriorityTrackedActor=null;
 if(!onlineLegacyCanCommitPriorityTerminal(owner)||onlineLegacyPriorityTerminalPending)return Promise.resolve(null);
 onlineLegacyPriorityTerminalPending=true;
 clearTimeout(onlineLegacyPushTimer);
 const snapshot=onlineLegacySnapshot(),digest=onlineLegacyDigest(),actorIndex=G.online.myPlayerIndex;
 const send=(baseRevision,retries)=>onlineAck('legacyCommit',{baseRevision,actorIndex,snapshot}).then(res=>{
   onlineLegacyRevision=Math.max(onlineLegacyRevision,res.revision||0);G.online.revision=onlineLegacyRevision;onlineLegacyLastDigest=digest;
   return res;
 }).catch(err=>{
   // Important : un conflit de révision ne doit jamais restaurer le snapshot où la
   // carte était encore ouverte. On rejoue le même état terminal sur la nouvelle révision.
   if(err&&err.current&&retries>0&&Number.isInteger(err.current.revision)){
     onlineLegacyRevision=Math.max(onlineLegacyRevision,err.current.revision);G.online.revision=onlineLegacyRevision;
     return send(onlineLegacyRevision,retries-1);
   }
   onlineLegacyLastDigest='';if(err&&err.current)onlineLegacyApply(err.current);else onlineError(err);
   return null;
 }).finally(()=>{onlineLegacyPriorityTerminalPending=false});
 return send(onlineLegacyRevision,2);
}
function onlineLegacyTrackPriorityTerminal(){
 const active=priorityCardResolutionActive();
 if(active){
   onlineLegacyPriorityWasActive=true;
   const actor=priorityCardResolutionActor();
   if(Number.isInteger(actor))onlineLegacyPriorityTrackedActor=actor;
   return;
 }
 if(!onlineLegacyPriorityWasActive)return;
 const actor=onlineLegacyPriorityTrackedActor;
 onlineLegacyPriorityWasActive=false;onlineLegacyPriorityTrackedActor=null;
 if(onlineLegacyApplying||!Number.isInteger(actor)||!onlineLegacyCanCommitPriorityTerminal(actor))return;
 onlineLegacyPushPriorityTerminalNow(actor).then(()=>{
   // Les reprises de chrono/gain d'Or/pioche ne sont autorisées qu'après le commit terminal.
   if(G&&G.online&&G.online.legacySync&&!onlineLegacyApplying)render();
 });
}
function onlineLegacyCanPublish(){
 if(!G||!G.online||!G.online.legacySync||onlineLegacyApplying||onlineLegacyPriorityTerminalPending||!onlineSocket)return false;"""
assert needle in s
s=s.replace(needle,insert,1)

pat=r"function onlineLegacyPushAssassinNow\(actor\)\{.*?\n\}\nfunction onlineLegacyPushCaravanNow\(\)\{"
m=re.search(pat,s,re.S)
assert m, 'Assassin push function not found'
replacement="""function onlineLegacyPushAssassinNow(actor){
 return onlineLegacyPushPriorityTerminalNow(actor);
}
function onlineLegacyPushCaravanNow(){"""
s=s[:m.start()]+replacement+s[m.end():]

old=" const cardPause=priorityCardResolutionActive();"
new=" const cardPause=priorityCardResolutionActive()||onlineLegacyPriorityTerminalPending;"
assert old in s
s=s.replace(old,new,1)

old=" const map=$('map');if(map)map.style.pointerEvents='';"
new=" const map=$('map');if(map)map.style.pointerEvents=onlineLegacyPriorityTerminalPending?'none':'';"
assert old in s
s=s.replace(old,new,1)

old=""" if(G&&G.online&&G.online.legacySync){
   const me=G.online.myPlayerIndex;
   const reactionMap="""
new=""" if(G&&G.online&&G.online.legacySync){
   const me=G.online.myPlayerIndex;
   if(onlineLegacyPriorityTerminalPending)return;
   const reactionMap="""
assert old in s
s=s.replace(old,new,1)

old="""render=function(){
 onlineLegacyBaseRender();
 wireOracleCardPreviews();
 if(paidDrawState&&paidDrawState.pausedByCard&&!priorityCardResolutionActive()&&!goldReaction)resumePaidDrawAfterCard();
 if(goldReaction&&goldReaction.pausedByCard&&!paidDrawState&&!choiceState&&!divinationState&&!caravanState&&!egnoState&&!shadowState&&!agentModalState&&!portalMode&&!buildingMode)resumeGoldReactionAfterCard();
 if(G&&G.online&&G.online.legacySync){
   restoreCouncilChoiceOverlay();"""
new="""render=function(){
 onlineLegacyBaseRender();
 wireOracleCardPreviews();
 // Détecter la fermeture d'une résolution AVANT de relancer un chrono interrompu :
 // le snapshot terminal doit être accepté par le serveur avant toute nouvelle action.
 if(G&&G.online&&G.online.legacySync)onlineLegacyTrackPriorityTerminal();
 if(!onlineLegacyPriorityTerminalPending&&paidDrawState&&paidDrawState.pausedByCard&&!priorityCardResolutionActive()&&!goldReaction)resumePaidDrawAfterCard();
 if(!onlineLegacyPriorityTerminalPending&&goldReaction&&goldReaction.pausedByCard&&!paidDrawState&&!choiceState&&!divinationState&&!caravanState&&!egnoState&&!shadowState&&!agentModalState&&!portalMode&&!buildingMode)resumeGoldReactionAfterCard();
 if(G&&G.online&&G.online.legacySync){
   restoreCouncilChoiceOverlay();"""
assert old in s
s=s.replace(old,new,1)

# Important invariants kept intact.
assert "$('localTestBtn').onclick=()=>{onlinePseudo();launchLegacyMode('2v3',3)};" in s
assert "peaceful.textContent='Naviguer'" in s
assert "if(priorityCardResolutionActive()&&!reactionMap)return;" in s
assert "onlineLegacyPushAssassinNow(actor).then" in s

p.write_text(s,encoding='utf-8')
print('global priority terminal sync cleanup applied')
