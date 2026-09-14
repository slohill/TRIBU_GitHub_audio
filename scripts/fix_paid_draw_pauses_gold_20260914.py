from pathlib import Path
p=Path('index.html')
s=p.read_text()
old="""function startPaidDrawTimer(){
 clearInterval(paidDrawTick);
 if(!paidDrawState||paidDrawState.pausedByCard)return;
 if(G&&G.online&&G.online.legacySync&&paidDrawState.player!==localViewer())return;
 paidDrawTick=setInterval(()=>{
   if(!paidDrawState){clearInterval(paidDrawTick);return}
   if(paidDrawState.pausedByCard)return;
   paidDrawState.seconds--;
   if(paidDrawState.seconds<=0){
     clearInterval(paidDrawTick);
     log('Fin de la fenêtre de 10 secondes après la pioche payante.');
     paidDrawState=null;
     render();
     if(G&&G.online&&G.online.legacySync)onlineLegacyPushNow();
     queueBot('fin fenêtre pioche');
     return;
   }
   render();
 },1000);
}
"""
new="""function startPaidDrawTimer(){
 clearInterval(paidDrawTick);
 if(!paidDrawState||paidDrawState.pausedByCard)return;
 if(G&&G.online&&G.online.legacySync&&paidDrawState.player!==localViewer())return;
 paidDrawTick=setInterval(()=>{
   if(!paidDrawState){clearInterval(paidDrawTick);return}
   if(paidDrawState.pausedByCard)return;
   paidDrawState.seconds--;
   if(paidDrawState.seconds<=0){
     clearInterval(paidDrawTick);
     const resumeGold=!!paidDrawState.pausedGold;
     log('Fin de la fenêtre de 10 secondes après la pioche payante.');
     paidDrawState=null;
     if(resumeGold&&goldReaction&&goldReaction.pausedByCard){
       resumeGoldReactionAfterCard();
     }else{
       render();
       if(G&&G.online&&G.online.legacySync)onlineLegacyPushNow();
       queueBot('fin fenêtre pioche');
     }
     return;
   }
   render();
 },1000);
}
"""
assert old in s
s=s.replace(old,new,1)
old2="""function spendDraw(){
 if(caravanState||divinationState)return;
 const viewer=localViewer();
 if(!G||G.players[viewer].bot||G.players[viewer].gold<5||paidDrawState)return;
 G.players[viewer].gold-=5;
 draw(viewer,1);

 // Pendant une bataille, aucun nouveau chrono. Pendant sa propre Phase de Jeu,
"""
new2="""function spendDraw(){
 if(caravanState||divinationState)return;
 const viewer=localViewer();
 if(!G||G.players[viewer].bot||G.players[viewer].gold<5||paidDrawState)return;
 const pausedGold=!!goldReaction;
 if(pausedGold)pauseGoldReactionForCard();
 G.players[viewer].gold-=5;
 draw(viewer,1);

 // Pendant une bataille, aucun nouveau chrono. Pendant sa propre Phase de Jeu,
"""
assert old2 in s
s=s.replace(old2,new2,1)
old3=""" paidDrawState={player:viewer,seconds:10,phase:G.phase};
 log(p(viewer).name+' dépense 5 Or, pioche 1 carte et dispose de 10 secondes pour la consulter ou jouer une carte.');
 startPaidDrawTimer();
 render();
 if(G&&G.online&&G.online.legacySync)onlineLegacyPushNow();
"""
new3=""" paidDrawState={player:viewer,seconds:10,phase:G.phase,pausedGold};
 log(p(viewer).name+' dépense 5 Or, pioche 1 carte et dispose de 10 secondes pour la consulter ou jouer une carte.');
 startPaidDrawTimer();
 render();
 if(G&&G.online&&G.online.legacySync){
   if(pausedGold)onlineLegacyPushGoldReactionNow();
   else onlineLegacyPushNow();
 }
"""
assert old3 in s
s=s.replace(old3,new3,1)
old4=""" if(goldReaction&&goldReaction.pausedByCard&&!choiceState&&!divinationState&&!caravanState&&!egnoState&&!shadowState&&!agentModalState&&!portalMode&&!buildingMode)resumeGoldReactionAfterCard();
"""
new4=""" if(goldReaction&&goldReaction.pausedByCard&&!paidDrawState&&!choiceState&&!divinationState&&!caravanState&&!egnoState&&!shadowState&&!agentModalState&&!portalMode&&!buildingMode)resumeGoldReactionAfterCard();
"""
assert old4 in s
s=s.replace(old4,new4,1)
p.write_text(s)
