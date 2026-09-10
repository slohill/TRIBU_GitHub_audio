from pathlib import Path

p=Path('index.html')
s=p.read_text(encoding='utf-8')

old="""function closeAgentModal(force=false){
 if(!force&&caravanState&&agentModalState&&agentModalState.kind==='caravan'){
"""
new="""function closeAgentModal(force=false){
 force=force===true;
 if(!force&&caravanState&&agentModalState&&agentModalState.kind==='caravan'){
"""
if old not in s:
    raise SystemExit('closeAgentModal anchor missing')
s=s.replace(old,new,1)

old2="""function onlineLegacyResumeBattleView(){
 clearInterval(battleTick);clearTimeout(botReactionTimer);
 if(!battle){onlineLegacyBattleViewSeconds=null;hideBattle();return;}
 showBattle();renderBattle();
 if(goldReaction&&goldReaction.pausedBattle){
"""
new2="""function onlineLegacyResumeBattleView(){
 clearInterval(battleTick);clearTimeout(botReactionTimer);
 if(!battle){onlineLegacyBattleViewSeconds=null;hideBattle();return;}
 showBattle();renderBattle();
 if(shadowState&&shadowState.parentBattle){
   onlineLegacyBattleViewSeconds=null;
   const pt=$('priorityTimer');if(pt)pt.textContent='En pause — Section de l’ombre';
   return;
 }
 if(goldReaction&&goldReaction.pausedBattle){
"""
if old2 not in s:
    raise SystemExit('onlineLegacyResumeBattleView anchor missing')
s=s.replace(old2,new2,1)

p.write_text(s,encoding='utf-8')
