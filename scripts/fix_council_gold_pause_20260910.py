from pathlib import Path

p=Path('index.html')
s=p.read_text(encoding='utf-8')

old="function pauseGoldReactionForCard(){if(!goldReaction)return false;clearGoldReactionTimer();goldReaction.pausedByCard=true;render();return true}"
new="function pauseGoldReactionForCard(){if(!goldReaction)return false;clearGoldReactionTimer();goldReaction.pausedByCard=true;return true}"
assert old in s, 'pauseGoldReactionForCard attendu introuvable'
s=s.replace(old,new,1)

needle="""function renderCouncilChoices(){
 const actor=choiceState.player,box=$('choiceCards');box.innerHTML='';
"""
insert="""function restoreCouncilChoiceOverlay(){
 const overlay=$('choiceOverlay');if(!overlay)return;
 const mine=!!(choiceState&&choiceState.kind==='council'&&choiceState.player===localViewer());
 overlay.classList.toggle('hidden',!mine);
 if(!mine)return;
 $('choiceTitle').textContent='Conseil de guerre';
 renderCouncilChoices();
}
function renderCouncilChoices(){
 const actor=choiceState.player,box=$('choiceCards');box.innerHTML='';
"""
assert needle in s, 'renderCouncilChoices attendu introuvable'
s=s.replace(needle,insert,1)

needle2=""" if(G&&G.online&&G.online.legacySync){
   onlineLegacyLockControls();
"""
replace2=""" if(G&&G.online&&G.online.legacySync){
   restoreCouncilChoiceOverlay();
   onlineLegacyLockControls();
"""
assert needle2 in s, 'wrapper render Online attendu introuvable'
s=s.replace(needle2,replace2,1)

p.write_text(s,encoding='utf-8')
