from pathlib import Path

p=Path('index.html')
s=p.read_text(encoding='utf-8')

def rep(old,new,count=1):
    global s
    n=s.count(old)
    if n!=count:
        raise SystemExit(f'expected {count} occurrence(s), found {n}: {old[:120]!r}')
    s=s.replace(old,new,count)

# 1) Divination: pass canonical Oracle ids from the buttons instead of looking up again by label.
rep(""" const names=[...new Set(ORACLES.map(o=>o.name))];
 names.forEach(name=>{
   const b=document.createElement('button');b.className='oraclePick';b.textContent=name;
   b.onclick=()=>divinationSetVisible(name);box.appendChild(b);
 });
""",""" const choices=[];const seenOracleNames=new Set();
 ORACLES.forEach((o,id)=>{if(!seenOracleNames.has(o.name)){seenOracleNames.add(o.name);choices.push({id,name:o.name})}});
 choices.forEach(({id,name})=>{
   const b=document.createElement('button');b.className='oraclePick';b.textContent=name;
   b.onclick=()=>divinationSetVisible(id);box.appendChild(b);
 });
""")
rep("function divinationSetVisible(name){","function divinationSetVisible(oracleId){")
rep(""" const pos=pool.findIndex(id=>ORACLES[id].name===name);
 if(pos<0){$('divinationText').textContent='Oracle introuvable.';return}
 const chosen=pool.splice(pos,1)[0];
 shuffleArray(pool);
 G.oracleDeck=pool;
 G.oracleDeck.push(chosen);

 divinationState=null;$('divinationPanel').classList.add('hidden');
 log(p(s.actor).name+' remélange tous les Oracles : '+name+' devient l’Oracle visible.');
""",""" const chosenId=Number(oracleId);
 const pos=pool.indexOf(chosenId);
 if(pos<0||!ORACLES[chosenId]){$('divinationText').textContent='Oracle introuvable.';return}
 const chosen=pool.splice(pos,1)[0],name=ORACLES[chosen].name;
 shuffleArray(pool);
 G.oracleDeck=pool;
 G.oracleDeck.push(chosen);

 divinationState=null;$('divinationPanel').classList.add('hidden');
 log(p(s.actor).name+' remélange tous les Oracles : '+name+' devient l’Oracle visible.');
""")

# 2) Egnobombe: off-turn actor may use the map; only the actor may cancel/target; clear state must sync and resume the bot.
rep("""function cancelEgnobombe(){
 if(!egnoState)return;
 const s=egnoState;egnoState=null;
 clearTopBanner();
 log('Egnobombe annulée : la carte reste en main.');
 if(s.parentBattle){battle=s.parentBattle;battle.seconds=s.parentSeconds||15;resumeBattleTimer()}
 render();
}
function egnoTargetLegal(r){
 return !!egnoState&&units(r,egnoState.player)>=5;
}
""","""function cancelEgnobombe(){
 if(!egnoState||localViewer()!==egnoState.player)return;
 const s=egnoState;egnoState=null;
 clearTopBanner();
 log('Egnobombe annulée : la carte reste en main.');
 if(s.parentBattle){battle=s.parentBattle;battle.seconds=15;resumeBattleTimer()}
 render();
 resumeGameAfterPriorityCard('reprise après annulation Egnobombe');
 if(G&&G.online&&G.online.legacySync)onlineLegacyPushNow();
}
function egnoTargetLegal(r){
 return !!egnoState&&localViewer()===egnoState.player&&units(r,egnoState.player)>=5;
}
""")
rep(""" if(parent){
   battle=parent;battle.seconds=s.parentSeconds||15;resumeBattleTimer();
   render();return;
 }
""",""" if(parent){
   battle=parent;battle.seconds=15;resumeBattleTimer();
   render();
   if(G&&G.online&&G.online.legacySync)onlineLegacyPushNow();
   return;
 }
""")
rep(""" render();queueBot('reprise après Egnobombe');
}
""",""" render();
 resumeGameAfterPriorityCard('reprise après Egnobombe');
 if(G&&G.online&&G.online.legacySync)onlineLegacyPushNow();
}
""")
rep("""   const reactionMap=(oracleState&&oracleState.kind==='sacrifice'&&oracleState.queues&&oracleState.queues[oracleState.index]&&oracleState.queues[oracleState.index].player===me)||(oracleState&&oracleState.kind==='dragon5'&&oracleState.player===me)||(dragonRichState&&dragonRichState.player===me);
""","""   const reactionMap=(oracleState&&oracleState.kind==='sacrifice'&&oracleState.queues&&oracleState.queues[oracleState.index]&&oracleState.queues[oracleState.index].player===me)||(oracleState&&oracleState.kind==='dragon5'&&oracleState.player===me)||(dragonRichState&&dragonRichState.player===me)||(egnoState&&egnoState.player===me)||(shadowState&&shadowState.player===me);
""")

# 3) Nested gold timers: Tax may interrupt a gold reaction; each suspended reaction restarts at 10 s.
rep("goldReaction=null,goldReactionTick=null,shadowState=null","goldReaction=null,goldReactionTick=null,goldReactionStack=[],shadowState=null")
rep("clearGoldReactionTimer();goldReaction=null;botToken++;","clearGoldReactionTimer();goldReaction=null;goldReactionStack=[];botToken++;")
rep("paidDrawState=null;goldReaction=null;shadowState=null;","paidDrawState=null;goldReaction=null;goldReactionStack=[];shadowState=null;")
rep("paidDrawState,goldReaction,shadowState,battleStack","paidDrawState,goldReaction,goldReactionStack,shadowState,battleStack")
rep("battle=r.battle||null;buildingMode=r.buildingMode||null;portalMode=r.portalMode||null;choiceState=r.choiceState||null;paidDrawState=r.paidDrawState||null;goldReaction=r.goldReaction||null;","battle=r.battle||null;buildingMode=r.buildingMode||null;portalMode=r.portalMode||null;choiceState=r.choiceState||null;paidDrawState=r.paidDrawState||null;goldReaction=r.goldReaction||null;goldReactionStack=Array.isArray(r.goldReactionStack)?r.goldReactionStack:[];")
rep("function resumeGoldReactionAfterCard(){if(!goldReaction||!goldReaction.pausedByCard)return;delete goldReaction.pausedByCard;startGoldReactionTimer();render();if(G&&G.online&&G.online.legacySync)onlineLegacyPushNow()}","""function resumeGoldReactionAfterCard(){if(!goldReaction||!goldReaction.pausedByCard)return;goldReaction.seconds=10;delete goldReaction.pausedByCard;startGoldReactionTimer();render();if(G&&G.online&&G.online.legacySync)onlineLegacyPushNow()}
function resumeGoldReactionStack(){
 if(!goldReactionStack.length)return false;
 goldReaction=goldReactionStack.pop();goldReaction.seconds=10;delete goldReaction.pausedByCard;
 startGoldReactionTimer();render();maybeBotAmbush();
 if(G&&G.online&&G.online.legacySync)onlineLegacyPushGoldReactionNow();
 return true;
}
function continueAfterGold(after){
 if(after==='resumeGoldStack'&&resumeGoldReactionStack())return;
 if(after==='beginPlay')beginPlay();else render();
}
""")
rep("if(s.after==='beginPlay')beginPlay();else render();","continueAfterGold(s.after);",2)
rep("if(r.after==='beginPlay')beginPlay();else render();","continueAfterGold(r.after);")
rep("if(amount<=0){if(after==='beginPlay')beginPlay();else render();return}","if(amount<=0){continueAfterGold(after);return}")
rep("""   if(after==='beginPlay')beginPlay();else render();
   return;
""","""   continueAfterGold(after);
   return;
""",1)
rep("""function playTax(handIndex){
 if(choiceState||goldReaction)return;
 const found=cardFromViewerHand(handIndex,'Taxe');if(!found)return;
 const receiver=found.viewer,gain=occupiedCaseCount(receiver);
 G.players[receiver].hand.splice(handIndex,1);G.discard.push(found.id);
 log(p(receiver).name+' joue Taxe : '+gain+' Or sont sur le point d’être gagnés.');
 offerGoldGain(receiver,gain,'Taxe','render');
 if(G&&G.online&&G.online.legacySync)onlineLegacyPushGoldReactionNow();
}
""","""function playTax(handIndex){
 if(choiceState)return;
 const found=cardFromViewerHand(handIndex,'Taxe');if(!found)return;
 const nestedGold=!!goldReaction;
 if(nestedGold){
   clearGoldReactionTimer();goldReaction.seconds=10;goldReaction.pausedByCard=true;
   goldReactionStack.push(goldReaction);goldReaction=null;
 }
 const receiver=found.viewer,gain=occupiedCaseCount(receiver);
 G.players[receiver].hand.splice(handIndex,1);G.discard.push(found.id);
 log(p(receiver).name+' joue Taxe : '+gain+' Or sont sur le point d’être gagnés.');
 offerGoldGain(receiver,gain,'Taxe',nestedGold?'resumeGoldStack':'render');
 if(G&&G.online&&G.online.legacySync)onlineLegacyPushGoldReactionNow();
}
""")
# Once a priority card ends during a gold window, restart that window even if a battle is underneath it.
rep("if(goldReaction&&goldReaction.pausedByCard&&!choiceState&&!divinationState&&!caravanState&&!egnoState&&!shadowState&&!agentModalState&&!portalMode&&!buildingMode&&!battle)resumeGoldReactionAfterCard();","if(goldReaction&&goldReaction.pausedByCard&&!choiceState&&!divinationState&&!caravanState&&!egnoState&&!shadowState&&!agentModalState&&!portalMode&&!buildingMode)resumeGoldReactionAfterCard();")

# 4) A priority-card interruption of a battle restarts that battle timer from the beginning.
rep("""function resumeGameAfterPriorityCard(reason='reprise après carte prioritaire'){
 if(priorityCardResolutionActive())return;
 if(G&&G.phase==='play')render();
 if(G&&G.players&&G.players[G.active]&&G.players[G.active].bot)queueBot(reason);
}
""","""function resumeGameAfterPriorityCard(reason='reprise après carte prioritaire'){
 if(priorityCardResolutionActive())return;
 if(battle&&!goldReaction){battle.seconds=15;resumeBattleTimer()}
 if(G&&G.phase==='play')render();
 if(G&&G.players&&G.players[G.active]&&G.players[G.active].bot)queueBot(reason);
}
""")

# 5) Remote completion of an off-turn human priority action must wake the designated bot driver.
rep(""" onlineLegacyResumeBattleView();
 onlineLegacyResumeGoldView();
}
""",""" onlineLegacyResumeBattleView();
 onlineLegacyResumeGoldView();
 onlineLegacyEnsureBotProgress();
}
""")

p.write_text(s,encoding='utf-8')
