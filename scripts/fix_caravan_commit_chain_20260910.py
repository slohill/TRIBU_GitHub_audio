from pathlib import Path

idx=Path('index.html')
s=idx.read_text(encoding='utf-8')

def rep(old,new,label):
    global s
    if old not in s:
        raise SystemExit('MISSING '+label)
    s=s.replace(old,new,1)

old_choose="""function chooseCaravanCard(j){
 if(!caravanState||j<0||j>=caravanState.revealed.length)return;
 const chooser=caravanState.order[caravanState.pick];
 if(G.online&&G.online.legacySync&&!G.players[chooser].bot&&localViewer()!==chooser)return;
 if(G.online&&G.online.legacySync&&G.players[chooser].bot&&!onlineLegacyCanDriveCaravanBot())return;
 const id=caravanState.revealed.splice(j,1)[0];
 G.players[chooser].hand.push(id);audioCardMove();
 log(p(chooser).name+' choisit '+CARDS[id].name+' dans la Caravane.');
 caravanState.pick++;
 showCaravanChoice();
 if(G&&G.online&&G.online.legacySync)onlineLegacyPushCaravanNow();
}
"""
new_choose="""function chooseCaravanCard(j){
 if(!caravanState||j<0||j>=caravanState.revealed.length)return;
 const chooser=caravanState.order[caravanState.pick];
 if(G.online&&G.online.legacySync&&!G.players[chooser].bot&&localViewer()!==chooser)return;
 if(G.online&&G.online.legacySync&&G.players[chooser].bot&&!onlineLegacyCanDriveCaravanBot())return;
 const id=caravanState.revealed.splice(j,1)[0];
 G.players[chooser].hand.push(id);audioCardMove();
 log(p(chooser).name+' choisit '+CARDS[id].name+' dans la Caravane.');
 caravanState.pick++;
 const done=!caravanState.revealed.length||caravanState.pick>=caravanState.order.length;
 if(done)finishCaravan();
 if(G&&G.online&&G.online.legacySync){
   const expectedPick=caravanState?caravanState.pick:null;
   onlineLegacyPushCaravanNow().then(()=>{
     if(caravanState&&caravanState.pick===expectedPick)showCaravanChoice();
   });
   return;
 }
 if(!done)showCaravanChoice();
}
"""
rep(old_choose,new_choose,'serialized caravan choices')

old_push="""function onlineLegacyPushCaravanNow(){
 if(!G||!G.online||!G.online.legacySync||onlineLegacyApplying||!onlineSocket)return;
 const actorIndex=G.online.myPlayerIndex;if(!Number.isInteger(actorIndex)||!G.players[actorIndex]||G.players[actorIndex].bot)return;
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
new_push="""function onlineLegacyPushCaravanNow(){
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
rep(old_push,new_push,'return caravan commit promise')

idx.write_text(s,encoding='utf-8')
