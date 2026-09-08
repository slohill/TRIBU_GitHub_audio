from pathlib import Path
p=Path('index.html');s=p.read_text()
old=""" // Une synchro distante ne relance pas un bot partiellement exécuté.
 // Le conducteur conserve le vrai timer/règles. Les autres écrans ne font
 // qu'animer le décompte reçu, sans appeler passPriority().
 clearInterval(battleTick);
 if(battle){
   if(onlineLegacyOwnsBattlePriority())resumeBattleTimer();
   else{
     showBattle();renderBattle();
     battleTick=setInterval(()=>{if(!battle){clearInterval(battleTick);return}if(battle.seconds>0)battle.seconds--;renderBattle()},1000);
   }
 }"""
new=""" // Une synchro distante ne relance pas un bot partiellement exécuté.
 // Si la priorité de bataille appartient à CE joueur humain, son écran prend
 // uniquement la fenêtre de réaction (timer + cartes/passer), sans devenir le
 // conducteur des bots. Sinon le décompte est seulement visuel.
 clearInterval(battleTick);
 if(battle){
   const priority=currentPriorityPlayer();
   const myHumanPriority=Number.isInteger(priority)&&priority===G.online.myPlayerIndex&&!G.players[priority].bot;
   if(myHumanPriority||onlineLegacyOwnsBattlePriority())resumeBattleTimer();
   else{
     showBattle();renderBattle();
     battleTick=setInterval(()=>{if(!battle){clearInterval(battleTick);return}if(battle.seconds>0)battle.seconds--;renderBattle()},1000);
   }
 }"""
assert old in s;s=s.replace(old,new,1);p.write_text(s)
