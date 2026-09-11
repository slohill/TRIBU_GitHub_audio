from pathlib import Path
p=Path('index.html')
s=p.read_text(encoding='utf-8')
old1="function resumeGoldReactionAfterCard(){if(!goldReaction||!goldReaction.pausedByCard)return;goldReaction.seconds=10;delete goldReaction.pausedByCard;startGoldReactionTimer();render();if(G&&G.online&&G.online.legacySync)onlineLegacyPushNow()}"
new1="function resumeGoldReactionAfterCard(){if(!goldReaction||!goldReaction.pausedByCard)return;goldReaction.seconds=10;delete goldReaction.pausedByCard;startGoldReactionTimer();render();if(G&&G.online&&G.online.legacySync)onlineLegacyPushGoldReactionNow()}"
if old1 not in s: raise SystemExit('resumeGoldReactionAfterCard pattern not found')
s=s.replace(old1,new1,1)
old2="""function activateInPlayCard(i,id,index=null){
 if(!inPlayCardUsable(i,id,index))return false;
 const name=CARDS[id].name;
 hideInPlayPreview();
 if(name==='Espion'){agentModalState={kind:'spy',actor:i,agentIndex:index};useSpy(index);return true}
 if(name==='Voleur'){agentModalState={kind:'thief',actor:i,agentIndex:index};useThief(index);return true}
 if(name==='Plan des trébuchets'){activateTrebuchets();return true}
 return false;
}"""
new2="""function activateInPlayCard(i,id,index=null){
 if(!inPlayCardUsable(i,id,index))return false;
 const name=CARDS[id].name;
 hideInPlayPreview();
 if(name==='Espion'||name==='Voleur'){
   if(goldReaction)pauseGoldReactionForCard();
   pauseGameForPriorityCard();
   if(name==='Espion'){agentModalState={kind:'spy',actor:i,agentIndex:index};useSpy(index)}
   else{agentModalState={kind:'thief',actor:i,agentIndex:index};useThief(index)}
   if(G&&G.online&&G.online.legacySync)onlineLegacyPushPriorityCardNow();
   return true;
 }
 if(name==='Plan des trébuchets'){activateTrebuchets();return true}
 return false;
}"""
if old2 not in s: raise SystemExit('activateInPlayCard pattern not found')
s=s.replace(old2,new2,1)
p.write_text(s,encoding='utf-8')
