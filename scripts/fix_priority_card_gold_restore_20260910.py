from pathlib import Path
p=Path('index.html')
s=p.read_text(encoding='utf-8')

def once(old,new,label):
    global s
    if s.count(old)!=1:
        raise SystemExit(f'{label}: expected 1 occurrence, got {s.count(old)}')
    s=s.replace(old,new,1)

once("function startCaravan(handIndex){\n const actor=localViewer(),id=G.players[actor].hand[handIndex];\n if(id===undefined||CARDS[id].name!=='Caravane de commerce'||isDecimated(actor)||caravanState)return;\n pauseGameForPriorityCard();",
"function startCaravan(handIndex){\n const actor=localViewer(),id=G.players[actor].hand[handIndex];\n if(id===undefined||CARDS[id].name!=='Caravane de commerce'||isDecimated(actor)||caravanState)return;\n if(goldReaction)pauseGoldReactionForCard();\n pauseGameForPriorityCard();","caravan gold pause")

once("function startEgnobombe(handIndex){\n const actor=localViewer(),id=G.players[actor].hand[handIndex];\n if(id===undefined||CARDS[id].name!=='Egnobombe'||!canPlayEgnobombe(actor))return;\n egnoState={player:actor,cardId:id,parentBattle:battle||null,parentSeconds:battle?battle.seconds:null};",
"function startEgnobombe(handIndex){\n const actor=localViewer(),id=G.players[actor].hand[handIndex];\n if(id===undefined||CARDS[id].name!=='Egnobombe'||!canPlayEgnobombe(actor))return;\n if(goldReaction)pauseGoldReactionForCard();\n egnoState={player:actor,cardId:id,parentBattle:battle||null,parentSeconds:battle?battle.seconds:null};","egno gold pause")

once("function startAssassin(handIndex){\n const actor=localViewer(),id=G.players[actor].hand[handIndex];\n if(id===undefined||CARDS[id].name!=='Assassin'||isDecimated(actor))return;\n const targets=assassinTargets(actor);\n if(!targets.length){log('Assassin : aucun Agent adverse à cibler.');render();return}\n agentModalState={kind:'assassin',actor,handIndex,cardId:id};",
"function startAssassin(handIndex){\n const actor=localViewer(),id=G.players[actor].hand[handIndex];\n if(id===undefined||CARDS[id].name!=='Assassin'||isDecimated(actor))return;\n const targets=assassinTargets(actor);\n if(!targets.length){log('Assassin : aucun Agent adverse à cibler.');render();return}\n if(goldReaction)pauseGoldReactionForCard();\n agentModalState={kind:'assassin',actor,handIndex,cardId:id};","assassin gold pause")

anchor="function restoreCouncilChoiceOverlay(){\n const overlay=$('choiceOverlay');if(!overlay)return;\n const mine=!!(choiceState&&choiceState.kind==='council'&&choiceState.player===localViewer());\n overlay.classList.toggle('hidden',!mine);\n if(!mine)return;\n $('choiceTitle').textContent='Conseil de guerre';\n renderCouncilChoices();\n}\n"
insert=anchor+"function restorePriorityCardOverlays(){\n const me=localViewer();\n const div=$('divinationPanel');\n if(div){\n   const mine=!!(divinationState&&divinationState.actor===me&&divinationState.stage!=='resolvingOracle');\n   div.classList.toggle('hidden',!mine);\n   if(mine){\n     if(divinationState.committed){\n       $('divinationText').textContent='Divination en résolution — choisissez l’Oracle qui deviendra visible au-dessus de la pile.';\n       const box=$('divinationChoices');box.innerHTML='';\n       const seen=new Set();ORACLES.forEach((o,id)=>{if(seen.has(o.name))return;seen.add(o.name);const b=document.createElement('button');b.className='oraclePick';b.textContent=o.name;b.onclick=()=>divinationSetVisible(id);box.appendChild(b)});\n     }else{\n       $('divinationText').textContent='Choisissez : activer l’Oracle visible ou choisir un nouvel Oracle.';\n       const box=$('divinationChoices');box.innerHTML='';\n       const a=document.createElement('button');a.textContent='Activer l’Oracle';a.onclick=divinationActivateVisible;box.appendChild(a);\n       const b=document.createElement('button');b.textContent='Choisir nouvel Oracle';b.onclick=divinationChooseNew;box.appendChild(b);\n       const c=document.createElement('button');c.textContent='Annuler';c.onclick=cancelDivination;box.appendChild(c);\n     }\n   }\n }\n if(agentModalState&&agentModalState.kind==='assassin'&&agentModalState.actor===me){\n   openAgentModal('Assassin','Choisissez l’Agent adverse à assassiner.');\n   const box=$('agentChoices');box.innerHTML='';\n   assassinTargets(me).forEach(t=>{const b=document.createElement('button');b.textContent=p(t.owner).name+' — '+t.name;b.onclick=()=>resolveAssassin(t);box.appendChild(b)});\n }\n}\n"
once(anchor,insert,"priority overlay restore helper")

once("   restoreCouncilChoiceOverlay();\n   onlineLegacyLockControls();",
"   restoreCouncilChoiceOverlay();\n   restorePriorityCardOverlays();\n   onlineLegacyLockControls();","restore hook")

p.write_text(s,encoding='utf-8')
