from pathlib import Path
p=Path('index.html');s=p.read_text()
old="""   if(myHumanPriority||onlineLegacyOwnsBattlePriority())resumeBattleTimer();
   else{"""
new="""   if(myHumanPriority){
     showBattle();renderBattle();
     battleTick=setInterval(()=>{if(!battle)return;battle.seconds--;renderBattle();if(battle.seconds<=0){passPriority();onlineLegacyPushNow()}},1000);
   }else if(onlineLegacyOwnsBattlePriority())resumeBattleTimer();
   else{"""
assert old in s;s=s.replace(old,new,1);p.write_text(s)
