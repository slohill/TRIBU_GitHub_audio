from pathlib import Path
p=Path('index.html')
s=p.read_text()
old="""function onlineLegacyCanPublish(){
 if(!G||!G.online||!G.online.legacySync||onlineLegacyApplying||!onlineSocket)return false;
 const me=G.online.myPlayerIndex;if(!Number.isInteger(me)||!G.players[me]||G.players[me].bot)return false;
 if(G.players[G.active]&&G.players[G.active].bot)return onlineLegacyCanExecuteBot();
 return true;
}"""
new="""function onlineLegacyCanPublish(){
 if(!G||!G.online||!G.online.legacySync||onlineLegacyApplying||!onlineSocket)return false;
 const me=G.online.myPlayerIndex;if(!Number.isInteger(me)||!G.players[me]||G.players[me].bot)return false;
 if(G.players[G.active]&&G.players[G.active].bot)return onlineLegacyCanExecuteBot();
 return true;
}
function onlineLegacyCanPublishLiveBot(){
 return !!(G&&G.online&&G.online.legacySync&&!onlineLegacyApplying&&onlineSocket&&G.players[G.active]&&G.players[G.active].bot&&onlineLegacyCanExecuteBot());
}
function onlineLegacyPushLiveBot(){
 if(!onlineLegacyCanPublishLiveBot())return;
 const now=onlineLegacyDigest();if(!now||now===onlineLegacyLastDigest)return;
 const snapshot=onlineLegacySnapshot(),actorIndex=G.online.myPlayerIndex,baseRevision=onlineLegacyRevision;
 onlineLegacyLastDigest=now;
 onlineAck('legacyCommit',{baseRevision,actorIndex,snapshot}).then(res=>{
   onlineLegacyRevision=res.revision;G.online.revision=res.revision;
 }).catch(err=>{
   onlineLegacyLastDigest='';
   if(err&&err.current)onlineLegacyApply(err.current);else onlineError(err);
 });
}"""
assert old in s
s=s.replace(old,new,1)
old=""" const start=canTurn&&G.phase==='start',recruiting=canTurn&&G.phase==='recruit',playing=canTurn&&G.phase==='play',oracleRoll=canTurn&&G.phase==='oracleRoll';"""
new=""" const start=canTurn&&G.phase==='start'&&!goldReaction&&!paidDrawState&&!dragonRichState&&!dragonCurseState,recruiting=canTurn&&G.phase==='recruit',playing=canTurn&&G.phase==='play',oracleRoll=canTurn&&G.phase==='oracleRoll';"""
assert old in s
s=s.replace(old,new,1)
old="""   const activePlayer=G.players&&G.players[G.active];
   if(!activePlayer||!activePlayer.bot)onlineLegacyMaybePush();"""
new="""   const activePlayer=G.players&&G.players[G.active];
   if(activePlayer&&activePlayer.bot)onlineLegacyPushLiveBot();
   else onlineLegacyMaybePush();"""
assert old in s
s=s.replace(old,new,1)
old="""function doDraw(){if(G&&G.online&&!G.online.legacySync)return onlineGameAction('DRAW_START');if(paidDrawState)return;draw(G.active,2);log(p().name+' pioche 2 cartes.');beginPlay()}"""
new="""function doDraw(){if(G&&G.online&&!G.online.legacySync)return onlineGameAction('DRAW_START');if(paidDrawState||goldReaction||G.phase!=='start')return;draw(G.active,2);log(p().name+' pioche 2 cartes.');beginPlay()}"""
assert old in s
s=s.replace(old,new,1)
old="""function doHarvest(){if(G&&G.online&&!G.online.legacySync)return onlineGameAction('HARVEST_START');if(paidDrawState||goldReaction)return;"""
new="""function doHarvest(){if(G&&G.online&&!G.online.legacySync)return onlineGameAction('HARVEST_START');if(paidDrawState||goldReaction||G.phase!=='start')return;"""
assert old in s
s=s.replace(old,new,1)
old=""" if(paidDrawState)return;
 recruitSnapshot={player:G.active,gold:p().gold,units:{}};"""
new=""" if(paidDrawState||goldReaction||G.phase!=='start')return;
 recruitSnapshot={player:G.active,gold:p().gold,units:{}};"""
assert old in s
s=s.replace(old,new,1)
p.write_text(s)
