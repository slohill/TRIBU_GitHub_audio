from pathlib import Path
p=Path('index.html');s=p.read_text()
old=""" // Une synchro distante ne relance pas un bot partiellement exécuté.
 if(battle)resumeBattleTimer();
}"""
new=""" // Une synchro distante ne relance pas un bot partiellement exécuté.
 // Le conducteur conserve le vrai timer/règles. Les autres écrans ne font
 // qu'animer le décompte reçu, sans appeler passPriority().
 clearInterval(battleTick);
 if(battle){
   if(onlineLegacyOwnsBattlePriority())resumeBattleTimer();
   else{
     showBattle();renderBattle();
     battleTick=setInterval(()=>{if(!battle){clearInterval(battleTick);return}if(battle.seconds>0)battle.seconds--;renderBattle()},1000);
   }
 }
}"""
assert old in s;s=s.replace(old,new,1);p.write_text(s)
