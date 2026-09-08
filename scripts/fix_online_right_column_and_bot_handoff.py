from pathlib import Path
p=Path('index.html')
s=p.read_text()

# 1) Seul le joueur réellement prioritaire peut cliquer sur Passer en bataille.
old="""    if(!isBot(priority)){
      const pass=document.createElement('button');
      pass.id='battlePass';pass.textContent='Passer';pass.onclick=passPriority;buttons.appendChild(pass);
      if(!participant){const info=document.createElement('div');info.className='note';info.textContent='Vous pouvez intervenir depuis votre main ou passer immédiatement.';buttons.appendChild(info)}
    }else{"""
new="""    if(!isBot(priority)){
      const mayReact=!G.online||!G.online.legacySync||priority===localViewer();
      if(mayReact){
        const pass=document.createElement('button');
        pass.id='battlePass';pass.textContent='Passer';pass.onclick=()=>{passPriority();if(G&&G.online&&G.online.legacySync)onlineLegacyPushNow()};buttons.appendChild(pass);
        if(!participant){const info=document.createElement('div');info.className='note';info.textContent='Vous pouvez intervenir depuis votre main ou passer immédiatement.';buttons.appendChild(info)}
      }else{
        const info=document.createElement('div');info.className='note';info.textContent='En attente de la réaction de '+p(priority).name+'…';buttons.appendChild(info)
      }
    }else{"""
assert old in s
s=s.replace(old,new,1)

# 2) Capturer le conducteur bot avant le changement de joueur.
old="""function advanceTurn(reason='nouveau tour'){
 if(gameOverState)return;
 const previousActive=G.active;"""
new="""function advanceTurn(reason='nouveau tour'){
 if(gameOverState)return;
 const previousActive=G.active;
 const previousOnlineBotDriver=(G&&G.online&&G.online.legacySync)?onlineLegacyBotDriverIndex:null;"""
assert old in s
s=s.replace(old,new,1)

# 3) A la fin de la chaîne de bots, publier explicitement le retour au joueur humain.
old=""" if(isDecimated(G.active)){
   beginReturnChoice();
   if(G&&G.online&&G.online.legacySync&&G.players[G.active]&&!G.players[G.active].bot)onlineLegacyPushHumanHandoff(previousActive);
   return
 }
 render();
 if(G&&G.online&&G.online.legacySync&&G.players[G.active]&&!G.players[G.active].bot)onlineLegacyPushHumanHandoff(previousActive);
 queueBot(reason);"""
new=""" if(isDecimated(G.active)){
   beginReturnChoice();
   if(G&&G.online&&G.online.legacySync&&G.players[G.active]&&!G.players[G.active].bot){
     if(G.players[previousActive]&&G.players[previousActive].bot)onlineLegacyPushBotHandoff(previousActive,previousOnlineBotDriver);
     else onlineLegacyPushHumanHandoff(previousActive);
   }
   return
 }
 render();
 if(G&&G.online&&G.online.legacySync&&G.players[G.active]&&!G.players[G.active].bot){
   if(G.players[previousActive]&&G.players[previousActive].bot)onlineLegacyPushBotHandoff(previousActive,previousOnlineBotDriver);
   else onlineLegacyPushHumanHandoff(previousActive);
 }
 queueBot(reason);"""
assert old in s
s=s.replace(old,new,1)

# 4) Helpers de publication immédiate + fin de chaîne bot.
marker="""function onlineLegacyPushHumanHandoff(previousActive){"""
insert="""function onlineLegacyPushNow(){
 if(!G||!G.online||!G.online.legacySync||onlineLegacyApplying||!onlineSocket)return;
 const actorIndex=G.online.myPlayerIndex;if(!Number.isInteger(actorIndex)||!G.players[actorIndex]||G.players[actorIndex].bot)return;
 clearTimeout(onlineLegacyPushTimer);
 const snapshot=onlineLegacySnapshot(),digest=onlineLegacyDigest();
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
function onlineLegacyPushBotHandoff(previousActive,previousDriver){
 if(!G||!G.online||!G.online.legacySync||onlineLegacyApplying||!onlineSocket)return;
 const me=G.online.myPlayerIndex;
 if(!G.players[previousActive]||!G.players[previousActive].bot||previousDriver!==me||!G.players[G.active]||G.players[G.active].bot)return;
 onlineLegacyPushNow();
}
function onlineLegacyPushHumanHandoff(previousActive){"""
assert marker in s
s=s.replace(marker,insert,1)

# 5) Reprendre correctement le chrono de bataille sur chaque écran.
old=""" onlineLegacyLastDigest=onlineLegacyDigest();render();onlineLegacyLastDigest=onlineLegacyDigest();onlineLegacyApplying=false;onlineLegacyLockControls();
 // Une synchro distante reste passive : elle affiche l'état publié sans relancer le moteur bot.
 if(battle){clearInterval(battleTick);clearTimeout(botReactionTimer);renderBattle();}
}"""
new=""" onlineLegacyLastDigest=onlineLegacyDigest();render();onlineLegacyLastDigest=onlineLegacyDigest();onlineLegacyApplying=false;onlineLegacyLockControls();
 onlineLegacyResumeBattleView();
}"""
assert old in s
s=s.replace(old,new,1)

marker="""function onlineLegacyStart(state){"""
insert="""function onlineLegacyResumeBattleView(){
 clearInterval(battleTick);clearTimeout(botReactionTimer);
 if(!battle)return;
 showBattle();renderBattle();
 const priority=currentPriorityPlayer(),me=G.online&&G.online.myPlayerIndex;
 const myHumanPriority=Number.isInteger(priority)&&priority===me&&G.players[priority]&&!G.players[priority].bot;
 if(myHumanPriority){
   battleTick=setInterval(()=>{
     if(!battle){clearInterval(battleTick);return}
     battle.seconds=Math.max(0,battle.seconds-1);renderBattle();
     if(battle.seconds<=0){clearInterval(battleTick);passPriority();onlineLegacyPushNow()}
   },1000);
   return;
 }
 if(Number.isInteger(priority)&&G.players[priority]&&G.players[priority].bot&&onlineLegacyCanExecuteBot()){
   resumeBattleTimer();
   return;
 }
 // Spectateur : animation locale uniquement, aucune mutation de règles à 0.
 battleTick=setInterval(()=>{
   if(!battle){clearInterval(battleTick);return}
   if(battle.seconds>0)battle.seconds--;
   renderBattle();
   if(battle.seconds<=0)clearInterval(battleTick);
 },1000);
}
function onlineLegacyStart(state){"""
assert marker in s
s=s.replace(marker,insert,1)

# 6) Les boutons de phase ne doivent jamais apparaître pendant le tour d'un adversaire ou d'un bot.
old="""function onlineLegacyLockControls(){
 if(!G||!G.online||!G.online.legacySync)return;
 const me=G.online.myPlayerIndex,mine=me===G.active&&!G.players[me].bot,botDriver=G.players[G.active]&&G.players[G.active].bot&&onlineLegacyIsDriver();
 const canTurn=mine||botDriver;
 const start=canTurn&&G.phase==='start'&&!paidDrawState&&!goldReaction,recruiting=canTurn&&G.phase==='recruit',playing=canTurn&&G.phase==='play',oracleRoll=canTurn&&G.phase==='oracleRoll';
 const s=$('startTurn');if(s)s.classList.toggle('hidden',!start);
 if($('draw'))$('draw').disabled=!start;if($('harvest'))$('harvest').disabled=!start;if($('recruit'))$('recruit').disabled=!start;
 if($('endRecruit'))$('endRecruit').disabled=!recruiting;if($('resetRecruit'))$('resetRecruit').disabled=!recruiting;
 if($('toOracle'))$('toOracle').disabled=!playing;if($('roll'))$('roll').disabled=!oracleRoll;
 const map=$('map');if(map)map.style.pointerEvents='';
 const n=$('status');if(n&&!n.querySelector('.onlineLegacyNotice'))n.insertAdjacentHTML('beforeend','<div class=\"botNotice onlineLegacyNotice\">🌐 Online — moteur original TRIBU synchronisé.</div>');
}"""
new="""function onlineLegacyLockControls(){
 if(!G||!G.online||!G.online.legacySync)return;
 const me=G.online.myPlayerIndex,mine=me===G.active&&!G.players[me].bot;
 const start=mine&&G.phase==='start'&&!paidDrawState&&!goldReaction,recruiting=mine&&G.phase==='recruit',playing=mine&&G.phase==='play',oracleRoll=mine&&G.phase==='oracleRoll';
 const s=$('startTurn');if(s)s.classList.toggle('hidden',!start);
 if(!mine){['recruitBox','playBox','oracleBox'].forEach(id=>{const el=$(id);if(el)el.classList.add('hidden')})}
 if($('draw'))$('draw').disabled=!start;if($('harvest'))$('harvest').disabled=!start;if($('recruit'))$('recruit').disabled=!start;
 if($('endRecruit'))$('endRecruit').disabled=!recruiting;if($('resetRecruit'))$('resetRecruit').disabled=!recruiting;
 if($('toOracle'))$('toOracle').disabled=!playing;if($('roll'))$('roll').disabled=!oracleRoll;
 const map=$('map');if(map)map.style.pointerEvents='';
 const n=$('status');if(n&&!n.querySelector('.onlineLegacyNotice'))n.insertAdjacentHTML('beforeend','<div class=\"botNotice onlineLegacyNotice\">🌐 Online — moteur original TRIBU synchronisé.</div>');
}"""
assert old in s
s=s.replace(old,new,1)

p.write_text(s)
