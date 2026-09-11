from pathlib import Path
p=Path('index.html')
s=p.read_text(encoding='utf-8')

old="""function oracleSacrificeClick(r){
 const q=oracleState&&oracleState.kind==='sacrifice'?oracleState.queues[oracleState.index]:null;
 if(!q||q.player!==localViewer()||!q.eligible.includes(r)||q.chosen.includes(r))return;
 q.chosen.push(r);
 if(q.chosen.length>=q.need){
   q.chosen.forEach(destroyUnitsOnRegion);
   log(p(q.player).name+' sacrifie '+q.chosen.join(', ')+'.');
   oracleState.index++;advanceOracleSacrifice();
 }else render();
 if(G&&G.online&&G.online.legacySync)onlineLegacyPushNow();
}
"""
new="""let oracleSacrificeSyncPending=false;
function oracleSacrificeClick(r){
 if(oracleSacrificeSyncPending)return;
 const q=oracleState&&oracleState.kind==='sacrifice'?oracleState.queues[oracleState.index]:null;
 if(!q||q.player!==localViewer()||!q.eligible.includes(r)||q.chosen.includes(r))return;
 q.chosen.push(r);
 if(q.chosen.length>=q.need){
   q.chosen.forEach(destroyUnitsOnRegion);
   log(p(q.player).name+' sacrifie '+q.chosen.join(', ')+'.');
   oracleState.index++;advanceOracleSacrifice();
 }else render();
 if(G&&G.online&&G.online.legacySync){
   oracleSacrificeSyncPending=true;
   onlineLegacyPushOracleSacrificeNow().finally(()=>{oracleSacrificeSyncPending=false});
 }
}
"""
if old not in s: raise SystemExit('oracleSacrificeClick block not found')
s=s.replace(old,new,1)

anchor="""function onlineLegacyPushCaravanNow(){
 if(!G||!G.online||!G.online.legacySync||onlineLegacyApplying||!onlineSocket)return Promise.resolve(null);
 const actorIndex=G.online.myPlayerIndex;if(!Number.isInteger(actorIndex)||!G.players[actorIndex]||G.players[actorIndex].bot)return Promise.resolve(null);
 clearTimeout(onlineLegacyPushTimer);
 const snapshot=onlineLegacySnapshot(),digest=onlineLegacyDigest();
 const send=(baseRevision,retries)=>onlineAck('legacyCommit',{baseRevision,actorIndex,snapshot}).then(res=>{
   onlineLegacyRevision=Math.max(onlineLegacyRevision,res.revision||0);G.online.revision=onlineLegacyRevision;onlineLegacyLastDigest=digest;
   return res;
 }).catch(err=>{
   if(err&&err.current&&retries>0&&Number.isInteger(err.current.revision)){
     onlineLegacyRevision=Math.max(onlineLegacyRevision,err.current.revision);G.online.revision=onlineLegacyRevision;
     return send(onlineLegacyRevision,retries-1);
   }
   onlineLegacyLastDigest='';if(err&&err.current)onlineLegacyApply(err.current);else onlineError(err);
   return null;
 });
 return send(onlineLegacyRevision,2);
}
"""
if anchor not in s: raise SystemExit('onlineLegacyPushCaravanNow block not found')
addition=anchor+"""function onlineLegacyPushOracleSacrificeNow(){
 if(!G||!G.online||!G.online.legacySync||onlineLegacyApplying||!onlineSocket)return Promise.resolve(null);
 const actorIndex=G.online.myPlayerIndex;if(!Number.isInteger(actorIndex)||!G.players[actorIndex]||G.players[actorIndex].bot)return Promise.resolve(null);
 clearTimeout(onlineLegacyPushTimer);
 const snapshot=onlineLegacySnapshot(),digest=onlineLegacyDigest();
 const send=(baseRevision,retries)=>onlineAck('legacyCommit',{baseRevision,actorIndex,snapshot}).then(res=>{
   onlineLegacyRevision=Math.max(onlineLegacyRevision,res.revision||0);G.online.revision=onlineLegacyRevision;onlineLegacyLastDigest=digest;
   return res;
 }).catch(err=>{
   if(err&&err.current&&retries>0&&Number.isInteger(err.current.revision)){
     onlineLegacyRevision=Math.max(onlineLegacyRevision,err.current.revision);G.online.revision=onlineLegacyRevision;
     return send(onlineLegacyRevision,retries-1);
   }
   onlineLegacyLastDigest='';if(err&&err.current)onlineLegacyApply(err.current);else onlineError(err);
   return null;
 });
 return send(onlineLegacyRevision,2);
}
"""
s=s.replace(anchor,addition,1)

old_apply="""function onlineLegacyApply(packet){
 if(!packet||!packet.snapshot)return;
 if(!G||!G.online||!G.online.legacySync)return;
 const me=packet.youIndex;
"""
new_apply="""function onlineLegacyApply(packet){
 if(!packet||!packet.snapshot)return;
 if(!G||!G.online||!G.online.legacySync)return;
 oracleSacrificeSyncPending=false;
 const me=packet.youIndex;
"""
if old_apply not in s: raise SystemExit('onlineLegacyApply anchor not found')
s=s.replace(old_apply,new_apply,1)

p.write_text(s,encoding='utf-8')
