from pathlib import Path
p=Path('index.html')
s=p.read_text(encoding='utf-8')

old="""function spendDraw(){
 if(caravanState||divinationState)return;
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
function pausePaidDrawForCard(){
 if(!paidDrawState)return false;
 clearInterval(paidDrawTick);paidDrawState.pausedByCard=true;return true;
}
function resumePaidDrawAfterCard(){
 if(!paidDrawState||!paidDrawState.pausedByCard)return false;
 paidDrawState.seconds=10;delete paidDrawState.pausedByCard;startPaidDrawTimer();render();
 if(G&&G.online&&G.online.legacySync)onlineLegacyPushNow();
 return true;
}
function spendDraw(){
 if(caravanState||divinationState)return;
"""
if old not in s: raise SystemExit('spendDraw anchor not found')
s=s.replace(old,new,1)

old=""" paidDrawState={player:viewer,seconds:10,phase:G.phase};
 log(p(viewer).name+' dépense 5 Or, pioche 1 carte et dispose de 10 secondes pour la consulter ou jouer une carte.');
 clearInterval(paidDrawTick);
 paidDrawTick=setInterval(()=>{
   if(!paidDrawState){clearInterval(paidDrawTick);return}
   paidDrawState.seconds--;
   if(paidDrawState.seconds<=0){
     clearInterval(paidDrawTick);
     log('Fin de la fenêtre de 10 secondes après la pioche payante.');
     paidDrawState=null;
     render();
     queueBot('fin fenêtre pioche');
     return;
   }
   render();
 },1000);
 render();
}
"""
new=""" paidDrawState={player:viewer,seconds:10,phase:G.phase};
 log(p(viewer).name+' dépense 5 Or, pioche 1 carte et dispose de 10 secondes pour la consulter ou jouer une carte.');
 startPaidDrawTimer();
 render();
 if(G&&G.online&&G.online.legacySync)onlineLegacyPushNow();
}
"""
if old not in s: raise SystemExit('paid draw interval block not found')
s=s.replace(old,new,1)

old=""" log(label+who+' interrompt le recrutement de '+p(recruiter).name+' : recrutement remis à zéro (Or et unités restaurés), puis résolution prioritaire.');
 render();
 return true;
"""
new=""" log(label+who+' interrompt le recrutement de '+p(recruiter).name+' : recrutement remis à zéro (Or et unités restaurés), puis résolution prioritaire.');
 return true;
"""
if old not in s: raise SystemExit('recruit reset render block not found')
s=s.replace(old,new,1)

old="""     if(G.phase==='recruit'&&recruitSnapshot&&recruitSnapshot.player===G.active){
       resetRecruitmentForPriorityCard(handPlayer,c.name);
     }
     if(goldReaction&&c.name!=='Embuscade')pauseGoldReactionForCard();
"""
new="""     if(paidDrawState&&paidDrawState.player===handPlayer)pausePaidDrawForCard();
     if(G.phase==='recruit'&&recruitSnapshot&&recruitSnapshot.player===G.active){
       resetRecruitmentForPriorityCard(handPlayer,c.name);
     }
     if(goldReaction&&c.name!=='Embuscade')pauseGoldReactionForCard();
"""
if old not in s: raise SystemExit('generic card wrapper block not found')
s=s.replace(old,new,1)

old=""" onlineLegacyBaseRender();
 wireOracleCardPreviews();
 if(goldReaction&&goldReaction.pausedByCard&&!choiceState&&!divinationState&&!caravanState&&!egnoState&&!shadowState&&!agentModalState&&!portalMode&&!buildingMode)resumeGoldReactionAfterCard();
"""
new=""" onlineLegacyBaseRender();
 wireOracleCardPreviews();
 if(paidDrawState&&paidDrawState.pausedByCard&&!priorityCardResolutionActive()&&!goldReaction)resumePaidDrawAfterCard();
 if(goldReaction&&goldReaction.pausedByCard&&!choiceState&&!divinationState&&!caravanState&&!egnoState&&!shadowState&&!agentModalState&&!portalMode&&!buildingMode)resumeGoldReactionAfterCard();
"""
if old not in s: raise SystemExit('render wrapper block not found')
s=s.replace(old,new,1)

old=""" render();
 if(caravanState)showCaravanChoice();
 onlineApplyPrivatePresentations(me);
"""
new=""" render();
 if(paidDrawState&&paidDrawState.player===me&&!paidDrawState.pausedByCard)startPaidDrawTimer();
 else if(!paidDrawState||paidDrawState.player!==me)clearInterval(paidDrawTick);
 if(caravanState)showCaravanChoice();
 onlineApplyPrivatePresentations(me);
"""
if old not in s: raise SystemExit('online apply paid draw anchor not found')
s=s.replace(old,new,1)

p.write_text(s,encoding='utf-8')
