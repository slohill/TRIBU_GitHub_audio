from pathlib import Path
p=Path('index.html')
s=p.read_text()
old="""function advanceTurn(reason='nouveau tour'){
 if(gameOverState)return;"""
new="""function advanceTurn(reason='nouveau tour'){
 if(gameOverState)return;
 const previousActive=G.active;"""
assert old in s
s=s.replace(old,new,1)
old=""" if(isDecimated(G.active)){beginReturnChoice();return}
 render();queueBot(reason);
}"""
new=""" if(isDecimated(G.active)){
   beginReturnChoice();
   if(G&&G.online&&G.online.legacySync&&G.players[G.active]&&!G.players[G.active].bot)onlineLegacyPushHumanHandoff(previousActive);
   return
 }
 render();
 if(G&&G.online&&G.online.legacySync&&G.players[G.active]&&!G.players[G.active].bot)onlineLegacyPushHumanHandoff(previousActive);
 queueBot(reason);
}"""
assert old in s
s=s.replace(old,new,1)
marker="""function onlineLegacyMaybePush(){
 if(!onlineLegacyCanPublish())return;"""
insert="""function onlineLegacyPushHumanHandoff(previousActive){
 if(!G||!G.online||!G.online.legacySync||onlineLegacyApplying||!onlineSocket)return;
 const me=G.online.myPlayerIndex;
 if(previousActive!==me||G.active===me||!G.players[G.active]||G.players[G.active].bot)return;
 clearTimeout(onlineLegacyPushTimer);
 const snapshot=onlineLegacySnapshot(),digest=onlineLegacyDigest(),actorIndex=me;
 const send=(baseRevision,retry)=>onlineAck('legacyCommit',{baseRevision,actorIndex,snapshot}).then(res=>{
   onlineLegacyRevision=Math.max(onlineLegacyRevision,res.revision||0);G.online.revision=onlineLegacyRevision;onlineLegacyLastDigest=digest;
 }).catch(err=>{
   if(retry&&err&&err.current&&Number.isInteger(err.current.revision)){
     onlineLegacyRevision=Math.max(onlineLegacyRevision,err.current.revision);G.online.revision=onlineLegacyRevision;
     return send(onlineLegacyRevision,false);
   }
   onlineLegacyLastDigest='';onlineError(err);
 });
 send(onlineLegacyRevision,true);
}
function onlineLegacyMaybePush(){
 if(!onlineLegacyCanPublish())return;"""
assert marker in s
s=s.replace(marker,insert,1)
p.write_text(s)
