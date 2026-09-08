from pathlib import Path
p=Path('index.html');s=p.read_text()
# Add an immediate commit helper for remote human priority so bot driver can resume from server event quickly.
marker="""function onlineLegacyMaybePush(){
 if(!onlineLegacyCanPublish())return;"""
insert="""function onlineLegacyPushNow(){
 if(!onlineLegacyCanPublish())return;
 const now=onlineLegacyDigest();if(!now||now===onlineLegacyLastDigest)return;
 const snapshot=onlineLegacySnapshot(),actorIndex=G.online.myPlayerIndex,baseRevision=onlineLegacyRevision;
 onlineLegacyLastDigest=now;
 onlineAck('legacyCommit',{baseRevision,actorIndex,snapshot}).then(res=>{onlineLegacyRevision=res.revision;G.online.revision=res.revision}).catch(err=>{onlineLegacyLastDigest='';if(err&&err.current)onlineLegacyApply(err.current);else onlineError(err)});
}
function onlineLegacyMaybePush(){
 if(!onlineLegacyCanPublish())return;"""
assert marker in s;s=s.replace(marker,insert,1)
# Explicit pass button: publish immediately after mutation.
old="""      pass.id='battlePass';pass.textContent='Passer';pass.onclick=passPriority;buttons.appendChild(pass);"""
new="""      pass.id='battlePass';pass.textContent='Passer';pass.onclick=()=>{passPriority();if(G&&G.online&&G.online.legacySync)onlineLegacyPushNow()};buttons.appendChild(pass);"""
assert old in s;s=s.replace(old,new,1)
# Automatic human-priority timeout: immediate publish.
s=s.replace("if(battle.seconds<=0){passPriority();if(G&&G.online&&G.online.legacySync)onlineLegacyMaybePush()}","if(battle.seconds<=0){passPriority();if(G&&G.online&&G.online.legacySync)onlineLegacyPushNow()}")
p.write_text(s)
