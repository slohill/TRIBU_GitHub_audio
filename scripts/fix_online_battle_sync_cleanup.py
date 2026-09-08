from pathlib import Path
p=Path('index.html')
s=p.read_text()
# 1) passPriority always publishes the new canonical priority/battle result in Online.
old="""function passPriority(){
  if(caravanState||divinationState)return;
  if(!battle)return;
  battle.consecutivePasses++;
  if(battle.consecutivePasses>=battle.priorityOrder.length){
    clearInterval(battleTick);
    resolveBattle();
    return;
  }
  advancePriority(false);
  renderBattle();
  prepareCurrentBattleReaction();
}"""
new="""function passPriority(){
  if(caravanState||divinationState)return;
  if(!battle)return;
  battle.consecutivePasses++;
  if(battle.consecutivePasses>=battle.priorityOrder.length){
    clearInterval(battleTick);
    resolveBattle();
    if(G&&G.online&&G.online.legacySync)onlineLegacyPushNow();
    return;
  }
  advancePriority(false);
  renderBattle();
  prepareCurrentBattleReaction();
  if(G&&G.online&&G.online.legacySync)onlineLegacyPushNow();
}"""
assert old in s
s=s.replace(old,new,1)
# 2) reaction cards also immediately publish the new priority.
old="""    advancePriority(true);
    renderBattle();render();
    prepareCurrentBattleReaction();
  }
}"""
new="""    advancePriority(true);
    renderBattle();render();
    prepareCurrentBattleReaction();
    if(G&&G.online&&G.online.legacySync)onlineLegacyPushNow();
  }
}"""
assert old in s
s=s.replace(old,new,1)
# 3) hide stale battle UI when canonical battle is gone.
old="""function renderBattle(){
  if(!battle || battle.kind==='seaChoice'){renderBattleBanner();return;}"""
new="""function renderBattle(){
  if(!battle || battle.kind==='seaChoice'){
    renderBattleBanner();
    if(!battle){hideBattle();const t=$('tacticalButtons');if(t)t.innerHTML='';const pi=$('priorityInfo');if(pi)pi.innerHTML='';const pt=$('priorityTimer');if(pt)pt.textContent='';}
    return;
  }"""
assert old in s
s=s.replace(old,new,1)
# 4) spectators animate a local display value only; never mutate canonical battle.seconds.
old="""let onlineLegacyRevision=0,onlineLegacyApplying=false,onlineLegacyLastDigest='',onlineLegacyPushTimer=null,onlineLegacyBotDriverIndex=null;"""
new="""let onlineLegacyRevision=0,onlineLegacyApplying=false,onlineLegacyLastDigest='',onlineLegacyPushTimer=null,onlineLegacyBotDriverIndex=null,onlineLegacyBattleViewSeconds=null;"""
assert old in s
s=s.replace(old,new,1)
old="""function onlineLegacyResumeBattleView(){
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
}"""
new="""function onlineLegacyResumeBattleView(){
 clearInterval(battleTick);clearTimeout(botReactionTimer);
 if(!battle){onlineLegacyBattleViewSeconds=null;hideBattle();return;}
 showBattle();renderBattle();
 const priority=currentPriorityPlayer(),me=G.online&&G.online.myPlayerIndex;
 const myHumanPriority=Number.isInteger(priority)&&priority===me&&G.players[priority]&&!G.players[priority].bot;
 if(myHumanPriority){
   battleTick=setInterval(()=>{
     if(!battle){clearInterval(battleTick);hideBattle();return}
     battle.seconds=Math.max(0,battle.seconds-1);renderBattle();
     if(battle.seconds<=0){clearInterval(battleTick);passPriority()}
   },1000);
   return;
 }
 if(Number.isInteger(priority)&&G.players[priority]&&G.players[priority].bot&&onlineLegacyCanExecuteBot()){
   resumeBattleTimer();
   return;
 }
 // Spectateur : le chrono affiché descend, mais l'état canonique reste intact.
 onlineLegacyBattleViewSeconds=Math.max(0,Number(battle.seconds)||0);
 battleTick=setInterval(()=>{
   if(!battle){clearInterval(battleTick);hideBattle();return}
   onlineLegacyBattleViewSeconds=Math.max(0,onlineLegacyBattleViewSeconds-1);
   const pt=$('priorityTimer');if(pt)pt.textContent=onlineLegacyBattleViewSeconds+' s';
   if(onlineLegacyBattleViewSeconds<=0)clearInterval(battleTick);
 },1000);
}"""
assert old in s
s=s.replace(old,new,1)
p.write_text(s)
