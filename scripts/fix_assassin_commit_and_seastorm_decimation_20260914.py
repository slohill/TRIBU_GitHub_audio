from pathlib import Path
p=Path('index.html')
s=p.read_text()
old="""function startAssassin(handIndex){
 const actor=localViewer(),id=G.players[actor].hand[handIndex];
 if(id===undefined||CARDS[id].name!=='Assassin'||isDecimated(actor))return;
 const targets=assassinTargets(actor);
 if(!targets.length){log('Assassin : aucun Agent adverse à cibler.');render();return}
 if(goldReaction)pauseGoldReactionForCard();
 agentModalState={kind:'assassin',actor,handIndex,cardId:id};
 pauseGameForPriorityCard();
"""
new="""function startAssassin(handIndex){
 const actor=localViewer(),id=G.players[actor].hand[handIndex];
 if(id===undefined||CARDS[id].name!=='Assassin'||isDecimated(actor))return;
 const targets=assassinTargets(actor);
 if(!targets.length){log('Assassin : aucun Agent adverse à cibler.');render();return}
 // Ouvrir le choix de cible ne joue pas encore Assassin : le chrono d'Or continue.
 agentModalState={kind:'assassin',actor,handIndex,cardId:id};
 pauseGameForPriorityCard();
"""
assert old in s
s=s.replace(old,new,1)
old="""function resolveAssassin(target){
 const s=agentModalState;if(!s||s.kind!=='assassin')return;
 const actor=s.actor,idx=G.players[actor].hand.indexOf(s.cardId);
 if(idx<0){closeAgentModal();render();return}
 discardHandCard(actor,idx);
"""
new="""function resolveAssassin(target){
 const s=agentModalState;if(!s||s.kind!=='assassin')return;
 const actor=s.actor,idx=G.players[actor].hand.indexOf(s.cardId);
 if(idx<0){closeAgentModal();render();return}
 // Le choix d'une cible engage définitivement la carte : seulement maintenant
 // le gain d'Or est interrompu, puis il reprendra à 10 s après résolution.
 if(goldReaction)pauseGoldReactionForCard();
 discardHandCard(actor,idx);
"""
assert old in s
s=s.replace(old,new,1)
old="""    if(goldReaction&&c.name!=='Embuscade')pauseGoldReactionForCard();
    return cardAction.call(d,ev);
"""
new="""    if(goldReaction&&c.name!=='Embuscade'&&c.name!=='Assassin')pauseGoldReactionForCard();
    return cardAction.call(d,ev);
"""
assert old in s
s=s.replace(old,new,1)
old="""   if(stormRoll%2===1){
     const lost=consumePickedSources().length;
     log(lost+' unité(s) sont perdues dans la Tempête en mer.');
     dest=null;picks={};checkDecimations();render();return;
   }
"""
new="""   if(stormRoll%2===1){
     const lost=consumePickedSources().length;
     log(lost+' unité(s) sont perdues dans la Tempête en mer.');
     dest=null;picks={};checkDecimations();
     // Si la Tempête vient de décimer le joueur actif, il ne peut plus passer
     // manuellement à l'Oracle : terminer immédiatement son tour évite le blocage
     // et son prochain tour proposera normalement le retour après décimation.
     if(isDecimated(G.active)){advanceTurn('décimation par Tempête en mer');return}
     render();return;
   }
"""
assert old in s
s=s.replace(old,new,1)
p.write_text(s)
