from pathlib import Path
p=Path('index.html');s=p.read_text()
old="""function onlineLegacyPushNow(){
 if(!onlineLegacyCanPublish())return;
 const now=onlineLegacyDigest();if(!now||now===onlineLegacyLastDigest)return;
 const snapshot=onlineLegacySnapshot(),actorIndex=G.online.myPlayerIndex,baseRevision=onlineLegacyRevision;
 onlineLegacyLastDigest=now;
 onlineAck('legacyCommit',{baseRevision,actorIndex,snapshot}).then(res=>{onlineLegacyRevision=res.revision;G.online.revision=res.revision}).catch(err=>{onlineLegacyLastDigest='';if(err&&err.current)onlineLegacyApply(err.current);else onlineError(err)});
}"""
new="""function onlineLegacyPushNow(){
 if(!onlineLegacyCanPublish())return;
 const now=onlineLegacyDigest();if(!now||now===onlineLegacyLastDigest)return;
 const snapshot=onlineLegacySnapshot(),actorIndex=G.online.myPlayerIndex,baseRevision=onlineLegacyRevision;
 onlineLegacyLastDigest=now;
 onlineAck('legacyCommit',{baseRevision,actorIndex,snapshot}).then(res=>{onlineLegacyRevision=res.revision;G.online.revision=res.revision}).catch(err=>{onlineLegacyLastDigest='';if(err&&err.current)onlineLegacyApply(err.current);else onlineError(err)});
}"""
# no-op anchor sanity, then patch remote apply: conductor should continue reaction engine only, not general bot.
assert old in s
old2="""   if(onlineLegacyCanExecuteBot())prepareCurrentBattleReaction();
 }"""
new2="""   if(onlineLegacyCanExecuteBot())prepareCurrentBattleReaction();
 }"""
assert old2 in s
# Keep explicit marker to ensure expected architecture; no semantic change needed here.
p.write_text(s)
