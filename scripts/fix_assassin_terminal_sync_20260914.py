from pathlib import Path

path = Path('index.html')
text = path.read_text(encoding='utf-8')

old_resolve = """function resolveAssassin(target){
 const s=agentModalState;if(!s||s.kind!=='assassin')return;
 const actor=s.actor,idx=G.players[actor].hand.indexOf(s.cardId);
 if(idx<0){closeAgentModal();render();return}
 // Le choix d'une cible engage définitivement la carte : seulement maintenant
 // le gain d'Or est interrompu, puis il reprendra à 10 s après résolution.
 if(goldReaction)pauseGoldReactionForCard();
 discardHandCard(actor,idx);
 const roll=1+Math.floor(Math.random()*6);
 let killed=false;
 const pl=G.players[target.owner];agentDefaults(target.owner);
 const current=pl.inPlay[target.index];
 if(roll>=4&&current===target.id&&agentUID(target.owner,target.index)===target.uid){
   const removed=pl.inPlay.splice(target.index,1)[0];
   if(pl.inPlayUID)pl.inPlayUID.splice(target.index,1);
   G.discard.push(removed);killed=true;
 }
 closeAgentModal();
 audioPlaySfx(killed?'assassin':'fail',killed?.9:.75);
 log(p(actor).name+' joue Assassin sur '+p(target.owner).name+' — '+target.name+' : dé '+roll+'. '+(killed?'Agent éliminé.':'Échec.'));
 G.assassinNotice={seq:Number(G.assassinNotice&&G.assassinNotice.seq||0)+1,targetOwner:target.owner,targetName:target.name,actor,killed};
 if(!G.online||!G.online.legacySync||localViewer()===target.owner)showAssassinMapMessage(target.owner,target.name,actor,killed);
 render();
}
"""
new_resolve = """function resolveAssassin(target){
 const s=agentModalState;if(!s||s.kind!=='assassin')return;
 const actor=s.actor,idx=G.players[actor].hand.indexOf(s.cardId);
 if(idx<0){closeAgentModal();render();return}
 // Le choix d'une cible engage définitivement la carte : seulement maintenant
 // le gain d'Or est interrompu, puis il reprendra à 10 s après résolution.
 if(goldReaction)pauseGoldReactionForCard();
 discardHandCard(actor,idx);
 const roll=1+Math.floor(Math.random()*6);
 let killed=false;
 const pl=G.players[target.owner];agentDefaults(target.owner);
 const current=pl.inPlay[target.index];
 if(roll>=4&&current===target.id&&agentUID(target.owner,target.index)===target.uid){
   const removed=pl.inPlay.splice(target.index,1)[0];
   if(pl.inPlayUID)pl.inPlayUID.splice(target.index,1);
   G.discard.push(removed);killed=true;
 }
 // Assassin peut être joué hors du tour de son propriétaire. Après fermeture du modal,
 // priorityCardResolutionActor() ne désigne plus cet acteur : un push générique n'est donc
 // plus autorisé. On ferme sans relancer le jeu, on sérialise d'abord l'état terminal,
 // puis seulement on reprend les timers/contrôles locaux.
 closeAgentModal(true);
 audioPlaySfx(killed?'assassin':'fail',killed?.9:.75);
 log(p(actor).name+' joue Assassin sur '+p(target.owner).name+' — '+target.name+' : dé '+roll+'. '+(killed?'Agent éliminé.':'Échec.'));
 G.assassinNotice={seq:Number(G.assassinNotice&&G.assassinNotice.seq||0)+1,targetOwner:target.owner,targetName:target.name,actor,killed};
 if(!G.online||!G.online.legacySync||localViewer()===target.owner)showAssassinMapMessage(target.owner,target.name,actor,killed);
 if(G&&G.online&&G.online.legacySync){
   onlineLegacyPushAssassinNow(actor).then(()=>{
     render();
     resumeGameAfterPriorityCard('reprise après Assassin');
   });
   return;
 }
 render();
 resumeGameAfterPriorityCard('reprise après Assassin');
}
"""
if old_resolve not in text:
    raise SystemExit('resolveAssassin exact block not found')
text = text.replace(old_resolve, new_resolve, 1)

old_click = """ if(G&&G.online&&G.online.legacySync){
   const me=G.online.myPlayerIndex;
   const reactionMap=(oracleState&&oracleState.kind==='sacrifice'&&oracleState.queues&&oracleState.queues[oracleState.index]&&oracleState.queues[oracleState.index].player===me)||(oracleState&&oracleState.kind==='dragon5'&&oracleState.player===me)||(dragonRichState&&dragonRichState.player===me)||(egnoState&&egnoState.player===me)||(shadowState&&shadowState.player===me);
   if(me!==G.active&&!reactionMap)return;
 }
"""
new_click = """ if(G&&G.online&&G.online.legacySync){
   const me=G.online.myPlayerIndex;
   const reactionMap=(oracleState&&oracleState.kind==='sacrifice'&&oracleState.queues&&oracleState.queues[oracleState.index]&&oracleState.queues[oracleState.index].player===me)||(oracleState&&oracleState.kind==='dragon5'&&oracleState.player===me)||(dragonRichState&&dragonRichState.player===me)||(egnoState&&egnoState.player===me)||(shadowState&&shadowState.player===me)||(portalMode&&portalMode.owner===me);
   if(me!==G.active&&!reactionMap)return;
   // Pendant une résolution prioritaire, la carte est la seule interaction autorisée.
   // Les cartes qui utilisent réellement la map sont explicitement listées ci-dessus.
   // Cela empêche notamment le joueur actif de déplacer des unités derrière le modal
   // Assassin d'un adversaire et de republier un snapshot encore pré-résolution.
   if(priorityCardResolutionActive()&&!reactionMap)return;
 }
"""
if old_click not in text:
    raise SystemExit('online clickSpot guard exact block not found')
text = text.replace(old_click, new_click, 1)

anchor = """function onlineLegacyPushCaravanNow(){
"""
new_func = """function onlineLegacyPushAssassinNow(actor){
 if(!G||!G.online||!G.online.legacySync||onlineLegacyApplying||!onlineSocket)return Promise.resolve(null);
 const actorIndex=G.online.myPlayerIndex;
 if(!Number.isInteger(actorIndex)||actorIndex!==actor||!G.players[actorIndex]||G.players[actorIndex].bot)return Promise.resolve(null);
 clearTimeout(onlineLegacyPushTimer);
 const snapshot=onlineLegacySnapshot(),digest=onlineLegacyDigest();
 const send=(baseRevision,retries)=>onlineAck('legacyCommit',{baseRevision,actorIndex,snapshot}).then(res=>{
   onlineLegacyRevision=Math.max(onlineLegacyRevision,res.revision||0);G.online.revision=onlineLegacyRevision;onlineLegacyLastDigest=digest;
   return res;
 }).catch(err=>{
   // L'état terminal d'Assassin (carte consommée, cible résolue, modal fermé) appartient
   // à l'acteur de la carte. En cas de conflit de révision, on rejoue ce même snapshot
   // terminal plutôt que de restaurer le snapshot serveur où Assassin était encore ouvert.
   if(err&&err.current&&retries>0&&Number.isInteger(err.current.revision)){
     onlineLegacyRevision=Math.max(onlineLegacyRevision,err.current.revision);G.online.revision=onlineLegacyRevision;
     return send(onlineLegacyRevision,retries-1);
   }
   onlineLegacyLastDigest='';if(err&&err.current)onlineLegacyApply(err.current);else onlineError(err);
   return null;
 });
 return send(onlineLegacyRevision,2);
}
""" + anchor
if anchor not in text:
    raise SystemExit('onlineLegacyPushCaravanNow anchor not found')
text = text.replace(anchor, new_func, 1)

# Invariants / regression checks.
assert "onlineLegacyPushAssassinNow(actor).then" in text
assert "closeAgentModal(true);" in new_resolve
assert "if(priorityCardResolutionActive()&&!reactionMap)return;" in text
assert "(portalMode&&portalMode.owner===me)" in text
assert "$('localTestBtn').onclick=()=>{onlinePseudo();launchLegacyMode('2v3',3)};" in text
assert "peaceful.textContent='Naviguer'" in text

path.write_text(text, encoding='utf-8')
