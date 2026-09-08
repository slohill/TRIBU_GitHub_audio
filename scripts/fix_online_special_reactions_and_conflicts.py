from pathlib import Path
p=Path('index.html')
s=p.read_text()

def rep(old,new,n=1):
    global s
    assert old in s, old[:120]
    s=s.replace(old,new,n)

# 1) Conserver le snapshot canonique renvoyé par le serveur lors d'un conflit de révision.
rep("function onlineAck(action,payload){return connectOnline().then(socket=>new Promise((resolve,reject)=>socket.emit(action,payload,res=>res&&res.ok?resolve(res):reject(new Error(res&&res.error||'Erreur serveur.')))))}",
"function onlineAck(action,payload){return connectOnline().then(socket=>new Promise((resolve,reject)=>socket.emit(action,payload,res=>{if(res&&res.ok){resolve(res);return}const err=new Error(res&&res.error||'Erreur serveur.');if(res&&res.current)err.current=res.current;reject(err)})))}")

# 2) Un conflit normal ne doit ni afficher une alerte ni écraser un état plus récent.
old=""" }).catch(err=>{
   if(retry&&err&&err.current&&Number.isInteger(err.current.revision)){
     onlineLegacyRevision=Math.max(onlineLegacyRevision,err.current.revision);G.online.revision=onlineLegacyRevision;
     return send(onlineLegacyRevision,false);
   }
   onlineLegacyLastDigest='';onlineError(err);
 });
 send(onlineLegacyRevision,true);
}"""
new=""" }).catch(err=>{
   if(err&&err.current){onlineLegacyLastDigest='';onlineLegacyApply(err.current);return}
   onlineLegacyLastDigest='';onlineError(err);
 });
 send(onlineLegacyRevision,true);
}"""
# Only replace onlineLegacyPushNow's first occurrence; handoff functions keep their explicit retry semantics.
pos=s.index('function onlineLegacyPushNow()')
idx=s.index(old,pos)
s=s[:idx]+s[idx:].replace(old,new,1)

# 3) Pendant le tour d'un humain, son navigateur doit gérer les priorités des bots
#    de la bataille qu'il a déclenchée. Sinon une bataille J2 vs Bot peut rester figée.
rep(""" if(G.players[priority].bot)return onlineLegacyCanExecuteBot();
 return priority===G.online.myPlayerIndex;""",
""" if(G.players[priority].bot){
   const me=G.online.myPlayerIndex;
   const activeHumanOwns=Number.isInteger(me)&&G.active===me&&G.players[me]&&!G.players[me].bot;
   return onlineLegacyCanExecuteBot()||activeHumanOwns;
 }
 return priority===G.online.myPlayerIndex;""")

# 4) Une Embuscade est une réaction hors tour : publication immédiate après son effet.
rep(""" startGoldReactionTimer();
 render();
 maybeBotAmbush();
}""",
""" startGoldReactionTimer();
 render();
 if(G&&G.online&&G.online.legacySync)onlineLegacyPushNow();
 maybeBotAmbush();
}""",1)

# 5) Conseil de guerre n'est pas autorisé au milieu d'une résolution d'Or.
rep("function playCouncil(handIndex){\n if(choiceState)return;",
    "function playCouncil(handIndex){\n if(choiceState||goldReaction)return;")
rep("if(isViewerHand&&!choiceState&&c.name==='Conseil de guerre'){d.classList.add('playablePermanent');d.title='Jouer Conseil de guerre maintenant';d.onclick=()=>playCouncil(handIndex)}",
    "if(isViewerHand&&!choiceState&&!goldReaction&&c.name==='Conseil de guerre'){d.classList.add('playablePermanent');d.title='Jouer Conseil de guerre maintenant';d.onclick=()=>playCouncil(handIndex)}")

# 6) Sacrifices Oracle multi-écrans : chaque choix humain est poussé immédiatement.
old="""function oracleSacrificeClick(r){
 const q=oracleState&&oracleState.kind==='sacrifice'?oracleState.queues[oracleState.index]:null;
 if(!q||q.player!==localViewer()||!q.eligible.includes(r)||q.chosen.includes(r))return;
 q.chosen.push(r);
 if(q.chosen.length>=q.need){
   q.chosen.forEach(destroyUnitsOnRegion);
   log(p(q.player).name+' sacrifie '+q.chosen.join(', ')+'.');
   oracleState.index++;advanceOracleSacrifice();
 }else render();
}"""
new="""function oracleSacrificeClick(r){
 const q=oracleState&&oracleState.kind==='sacrifice'?oracleState.queues[oracleState.index]:null;
 if(!q||q.player!==localViewer()||!q.eligible.includes(r)||q.chosen.includes(r))return;
 q.chosen.push(r);
 if(q.chosen.length>=q.need){
   q.chosen.forEach(destroyUnitsOnRegion);
   log(p(q.player).name+' sacrifie '+q.chosen.join(', ')+'.');
   oracleState.index++;advanceOracleSacrifice();
 }else render();
 if(G&&G.online&&G.online.legacySync)onlineLegacyPushNow();
}"""
rep(old,new)

# 7) Retour après décimation : les décisions doivent être relayées sans attendre le rendu générique.
rep("""function passReturn(){
 if(!returnState)return;
 clearTopBanner();
 log(p().name+' choisit de ne pas revenir ce tour.');
 advanceTurn('retour passé');
}""",
"""function passReturn(){
 if(!returnState)return;
 clearTopBanner();
 log(p().name+' choisit de ne pas revenir ce tour.');
 advanceTurn('retour passé');
 if(G&&G.online&&G.online.legacySync)onlineLegacyPushNow();
}""")
rep(""" G.phase='start';resetMove();render();queueBot('joueur reformé');
}""",
""" G.phase='start';resetMove();render();
 if(G&&G.online&&G.online.legacySync)onlineLegacyPushNow();
 queueBot('joueur reformé');
}""",1)

p.write_text(s)
