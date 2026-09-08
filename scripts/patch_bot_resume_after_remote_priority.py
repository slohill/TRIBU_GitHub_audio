from pathlib import Path
p=Path('index.html');s=p.read_text()
old="""   if(myHumanPriority||onlineLegacyOwnsBattlePriority())resumeBattleTimer();
   else{
     showBattle();renderBattle();
     battleTick=setInterval(()=>{if(!battle){clearInterval(battleTick);return}if(battle.seconds>0)battle.seconds--;renderBattle()},1000);
   }"""
new="""   if(myHumanPriority||onlineLegacyOwnsBattlePriority())resumeBattleTimer();
   else{
     showBattle();renderBattle();
     battleTick=setInterval(()=>{if(!battle){clearInterval(battleTick);return}if(battle.seconds>0)battle.seconds--;renderBattle()},1000);
   }
   if(onlineLegacyCanExecuteBot())prepareCurrentBattleReaction();"""
assert old in s;s=s.replace(old,new,1);p.write_text(s)
