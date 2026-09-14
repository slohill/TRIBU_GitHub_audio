from pathlib import Path

p = Path('index.html')
s = p.read_text(encoding='utf-8')

old = """function passPriority(){
  if(caravanState||divinationState)return;
  if(!battle)return;
"""
new = """function passPriority(){
  // Une résolution prioritaire suspend réellement la fenêtre de réaction : son chrono
  // ne doit ni avancer la priorité ni rester bloqué à 0 pendant cette résolution.
  if(priorityCardResolutionActive())return;
  if(!battle)return;
"""
assert old in s, 'passPriority anchor missing'
s = s.replace(old, new, 1)

old = """function playBattleCardForOwner(owner,handIndex){
  if(caravanState||divinationState||!battle)return;
  const id=G.players[owner].hand[handIndex];
"""
new = """function playBattleCardForOwner(owner,handIndex){
  if(caravanState||divinationState||!battle)return;
  // 0 seconde équivaut exactement à « Passer » : aucune carte ne peut être engagée
  // dans l'ancienne fenêtre après son expiration.
  if(!isHotseatMode()&&battle.seconds<=0){
    if(owner===currentPriorityPlayer()&&onlineLegacyOwnsBattlePriority())passPriority();
    return;
  }
  const id=G.players[owner].hand[handIndex];
"""
assert old in s, 'playBattleCardForOwner anchor missing'
s = s.replace(old, new, 1)

old = """function renderHandBattleState(){
 if(!G)return;
 const viewer=displayedHandViewer(),hand=$('hand');
 if(!hand||viewer===null)return;
 const cards=[...hand.children];
 cards.forEach((d,idx)=>{
   d.classList.remove('battlePlayable','battleBlocked');
"""
new = """function renderHandBattleState(){
 if(!G)return;
 const viewer=displayedHandViewer(),hand=$('hand');
 if(!hand||viewer===null)return;
 const cards=[...hand.children];
 const battleExpired=!!battle&&!isHotseatMode()&&battle.seconds<=0;
 cards.forEach((d,idx)=>{
   d.classList.remove('battlePlayable','battleBlocked');
   if(battleExpired){d.onclick=null;d.classList.add('battleBlocked');d.title='Fenêtre de réaction expirée';return}
"""
assert old in s, 'renderHandBattleState anchor missing'
s = s.replace(old, new, 1)

old = """ if(goldReaction&&goldReaction.pausedBattle){
   onlineLegacyBattleViewSeconds=null;
   const pt=$('priorityTimer');if(pt)pt.textContent='En pause — gain d’Or';
   return;
 }
 const priority=currentPriorityPlayer(),me=G.online&&G.online.myPlayerIndex;
"""
new = """ if(goldReaction&&goldReaction.pausedBattle){
   onlineLegacyBattleViewSeconds=null;
   const pt=$('priorityTimer');if(pt)pt.textContent='En pause — gain d’Or';
   return;
 }
 // Toute carte/résolution prioritaire gèle la bataille. Sans ce garde, l'application
 // d'un snapshot Online pouvait recréer le timer pendant Divination/Caravane/etc.,
 // atteindre 0 puis laisser une ancienne fenêtre de réaction visible.
 if(priorityCardResolutionActive()){
   onlineLegacyBattleViewSeconds=null;
   const pt=$('priorityTimer');if(pt)pt.textContent='En pause — résolution de carte';
   return;
 }
 const priority=currentPriorityPlayer(),me=G.online&&G.online.myPlayerIndex;
"""
assert old in s, 'onlineLegacyResumeBattleView pause anchor missing'
s = s.replace(old, new, 1)

old = """ onlineLegacyBattleViewSeconds=Math.max(0,Number(battle.seconds)||0);
 battleTick=setInterval(()=>{
   if(!battle){clearInterval(battleTick);hideBattle();return}
   onlineLegacyBattleViewSeconds=Math.max(0,onlineLegacyBattleViewSeconds-1);
   const pt=$('priorityTimer');if(pt)pt.textContent=onlineLegacyBattleViewSeconds+' s';
   if(onlineLegacyBattleViewSeconds<=0)clearInterval(battleTick);
 },1000);
"""
new = """ onlineLegacyBattleViewSeconds=Math.max(0,Number(battle.seconds)||0);
 battleTick=setInterval(()=>{
   if(!battle){clearInterval(battleTick);hideBattle();return}
   onlineLegacyBattleViewSeconds=Math.max(0,onlineLegacyBattleViewSeconds-1);
   const pt=$('priorityTimer');
   if(onlineLegacyBattleViewSeconds<=0){
     // Ce navigateur n'est pas propriétaire de la priorité : il ne peut pas committer
     // le « Passer ». Ne jamais afficher un faux 0 actif ; attendre le snapshot canonique.
     if(pt)pt.textContent='En attente…';
     clearInterval(battleTick);return;
   }
   if(pt)pt.textContent=onlineLegacyBattleViewSeconds+' s';
 },1000);
"""
assert old in s, 'spectator battle timer anchor missing'
s = s.replace(old, new, 1)

p.write_text(s, encoding='utf-8')
print('patched battle timer zero/pass semantics')
