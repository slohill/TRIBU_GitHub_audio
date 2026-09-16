from pathlib import Path
p=Path('index.html')
s=p.read_text()
old="""function resumeBattleTimer(){
 clearInterval(battleTick);if(!battle)return;
 if(!isHotseatMode()&&onlineLegacyOwnsBattlePriority())battleTick=setInterval(()=>{if(!battle)return;battle.seconds--;renderBattle();if(battle.seconds<=0)passPriority()},1000);
 showBattle();renderBattle();
 if(!isHotseatMode()&&onlineLegacyOwnsBattlePriority())prepareCurrentBattleReaction();
}"""
new="""function resumeBattleTimer(){
 clearInterval(battleTick);clearTimeout(botReactionTimer);botReactionTimer=null;if(!battle)return;
 // En Online, une résolution prioritaire qui vient juste de se fermer doit d'abord
 // publier son snapshot terminal. Ne jamais relancer ici le chrono ou la réaction bot
 // avant ce commit : Divination, Caravane, Egnobombe, Section de l'ombre, Conseil, etc.
 if(G&&G.online&&G.online.legacySync&&onlineLegacyPriorityWasActive&&!priorityCardResolutionActive())return;
 if(!isHotseatMode()&&onlineLegacyOwnsBattlePriority())battleTick=setInterval(()=>{if(!battle)return;battle.seconds--;renderBattle();if(battle.seconds<=0)passPriority()},1000);
 showBattle();renderBattle();
 if(!isHotseatMode()&&onlineLegacyOwnsBattlePriority())prepareCurrentBattleReaction();
}"""
assert old in s
s=s.replace(old,new,1)
old2=""" onlineLegacyPushPriorityTerminalNow(actor).then(()=>{
   // Les reprises de chrono/gain d'Or/pioche ne sont autorisées qu'après le commit terminal.
   if(G&&G.online&&G.online.legacySync&&!onlineLegacyApplying)render();
 });"""
new2=""" onlineLegacyPushPriorityTerminalNow(actor).then(()=>{
   // Les reprises de chrono/gain d'Or/pioche ne sont autorisées qu'après le commit terminal.
   // Reconstituer ensuite la vue bataille via le chemin Online central, qui respecte aussi
   // les pauses imbriquées (Or, autre résolution prioritaire, spectateur, bot).
   if(G&&G.online&&G.online.legacySync&&!onlineLegacyApplying){render();onlineLegacyResumeBattleView();onlineLegacyResumeGoldView()}
 });"""
assert old2 in s
s=s.replace(old2,new2,1)
p.write_text(s)
