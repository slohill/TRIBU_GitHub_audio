from pathlib import Path
p=Path('index.html'); s=p.read_text(encoding='utf-8')
old="""  audioPlaySfx('dragon',.675);checkDecimations();showDragonSixNotice(victim,()=>advanceTurn('nouveau tour'));render();return
 }"""
new="""  audioPlaySfx('dragon',.675);checkDecimations();showDragonSixNotice(victim,()=>advanceTurn('nouveau tour'));render();
  // Online : la destruction du Dragon est un état terminal critique. Un commit
  // concurrent (par ex. le déplacement du Dragon juste avant le jet) ne doit
  // jamais restaurer les unités détruites. On republie exactement ce snapshot
  // et, en cas de conflit de révision, on le rejoue sur la révision courante.
  if(G&&G.online&&G.online.legacySync)onlineLegacyPushDragonDestructionNow();
  return
 }"""
assert old in s
s=s.replace(old,new,1)
anchor="""function onlineLegacyPushAssassinNow(actor){
 return onlineLegacyPushPriorityTerminalNow(actor);
}
"""
insert="""function onlineLegacyPushDragonDestructionNow(){
 if(!G||!G.online||!G.online.legacySync||onlineLegacyApplying||!onlineSocket)return Promise.resolve(null);
 const actorIndex=G.online.myPlayerIndex;
 if(!Number.isInteger(actorIndex)||!G.players[actorIndex]||G.players[actorIndex].bot)return Promise.resolve(null);
 if(G.players[G.active]&&G.players[G.active].bot&&!onlineLegacyCanExecuteBot())return Promise.resolve(null);
 clearTimeout(onlineLegacyPushTimer);
 const snapshot=onlineLegacySnapshot(),digest=onlineLegacyDigest();
 const send=(baseRevision,retries)=>onlineAck('legacyCommit',{baseRevision,actorIndex,snapshot}).then(res=>{
   onlineLegacyRevision=Math.max(onlineLegacyRevision,res.revision||0);G.online.revision=onlineLegacyRevision;onlineLegacyLastDigest=digest;
   return res;
 }).catch(err=>{
   // Ne jamais appliquer err.current ici : il peut contenir la région avant
   // destruction. Le même snapshot destructif est rejoué sur la révision reçue.
   if(err&&err.current&&retries>0&&Number.isInteger(err.current.revision)){
     onlineLegacyRevision=Math.max(onlineLegacyRevision,err.current.revision);G.online.revision=onlineLegacyRevision;
     return send(onlineLegacyRevision,retries-1);
   }
   onlineLegacyLastDigest='';onlineError(err);return null;
 });
 return send(onlineLegacyRevision,2);
}
"""
assert anchor in s
s=s.replace(anchor,insert+anchor,1)
p.write_text(s,encoding='utf-8')
