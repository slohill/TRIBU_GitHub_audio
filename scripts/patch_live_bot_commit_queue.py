from pathlib import Path
p=Path('index.html');s=p.read_text()
old="""function onlineLegacyCanPublishLiveBot(){
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
new="""let onlineLegacyBotCommitBusy=false,onlineLegacyBotCommitQueued=false;
function onlineLegacyCanPublishLiveBot(){
 return !!(G&&G.online&&G.online.legacySync&&!onlineLegacyApplying&&onlineSocket&&G.players[G.active]&&G.players[G.active].bot&&onlineLegacyCanExecuteBot());
}
function onlineLegacyPushLiveBot(){
 if(!onlineLegacyCanPublishLiveBot())return;
 if(onlineLegacyBotCommitBusy){onlineLegacyBotCommitQueued=true;return}
 const now=onlineLegacyDigest();if(!now||now===onlineLegacyLastDigest)return;
 const snapshot=onlineLegacySnapshot(),actorIndex=G.online.myPlayerIndex,baseRevision=onlineLegacyRevision;
 onlineLegacyLastDigest=now;onlineLegacyBotCommitBusy=true;
 onlineAck('legacyCommit',{baseRevision,actorIndex,snapshot}).then(res=>{
   onlineLegacyRevision=res.revision;G.online.revision=res.revision;
 }).catch(err=>{
   onlineLegacyLastDigest='';
   if(err&&err.current)onlineLegacyApply(err.current);else onlineError(err);
 }).finally(()=>{
   onlineLegacyBotCommitBusy=false;
   if(onlineLegacyBotCommitQueued){onlineLegacyBotCommitQueued=false;onlineLegacyPushLiveBot()}
 });
}"""
assert old in s
p.write_text(s.replace(old,new,1))
