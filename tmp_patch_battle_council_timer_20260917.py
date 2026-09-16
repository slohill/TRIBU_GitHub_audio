from pathlib import Path
p=Path('index.html')
s=p.read_text(encoding='utf-8')
old="""function hideBattle(){
  $('battlePanel').classList.add('hidden');
  $('battleBanner').classList.add('hidden');
  clearInterval(battleTick);
}"""
new="""function hideBattle(){
  $('battlePanel').classList.add('hidden');
  $('battleBanner').classList.add('hidden');
  clearInterval(battleTick);
  clearTimeout(botReactionTimer);botReactionTimer=null;
}"""
assert old in s, 'hideBattle exact target missing'
s=s.replace(old,new,1)
old2=""" if(wasBattle&&battle){
   // Conseil de guerre compte comme une réaction jouée : les passes sont remises à zéro,
   // puis la priorité passe au joueur suivant une fois son effet entièrement résolu.
   advancePriority(true);
   battle.seconds=15;
   resumeBattleTimer();render();return;
 }"""
new2=""" if(wasBattle&&battle){
   // Conseil de guerre compte comme une réaction jouée : les passes sont remises à zéro,
   // puis la priorité passe au joueur suivant une fois son effet entièrement résolu.
   advancePriority(true);
   battle.seconds=15;
   // En Online, publier d'abord l'état terminal du Conseil. Sinon le chrono / la réaction
   // du joueur suivant (notamment un bot) peut repartir avant que la fermeture du Conseil
   // soit canonique et entrer en course avec un ancien snapshot.
   if(G&&G.online&&G.online.legacySync){
     onlineLegacyPushPriorityTerminalNow(actor).then(()=>{
       if(!battle||priorityCardResolutionActive())return;
       resumeBattleTimer();render();
     });
     return;
   }
   resumeBattleTimer();render();return;
 }"""
assert old2 in s, 'confirmCouncil battle target missing'
s=s.replace(old2,new2,1)
p.write_text(s,encoding='utf-8')
