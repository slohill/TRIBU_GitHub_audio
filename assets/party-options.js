// UI-only public rendering facts and commerce editor presence; no game rule duplication.
let commerceEditorOpen=false,commerceOpenCount=0;
function commerceClocksPaused(){return commerceBattlePaused=!!(battle||goldReaction)&&(commerceEditorOpen||commerceOpenCount>0)}
function commerceReceivePause(state){
 if(Number.isInteger(state.editors))commerceOpenCount=state.editors;
 commerceBattlePaused=!!(battle||goldReaction)&&(!!state.paused||commerceEditorOpen||commerceOpenCount>0);
 if(battle&&Number.isFinite(state.seconds))battle.seconds=state.seconds;
 if(goldReaction&&Number.isFinite(state.goldSeconds))goldReaction.seconds=state.goldSeconds;
 if(commerceBattlePaused){clearGoldReactionTimer();clearInterval(battleTick);clearTimeout(botReactionTimer);onlineLegacyBattleViewSeconds=null}
 else if(battle){if(G?.online?.legacySync)onlineLegacyResumeBattleView();else if(!priorityCardResolutionActive()&&!goldReaction)resumeBattleTimer()}
 if(!commerceBattlePaused&&goldReaction&&!goldReaction.pausedByCard){onlineLegacyResumeGoldView();maybeBotAmbush()}
 commerceUpdateBar();if(battle)renderBattle();
}
function commerceSetEditor(open){
 if(commerceEditorOpen===!!open)return;
 commerceEditorOpen=!!open;
 if(G?.online?.legacySync){
   if(open)commerceReceivePause({paused:true});
   onlineAck('commerceEditing',{open:!!open}).catch(e=>{commerceEditorOpen=false;commerceReceivePause({paused:false});onlineError(e)});
 }else commerceReceivePause({paused:!!open});
}
function publicMapSpots(){
 const asset=value=>{const match=String(value||'').match(/assets\/images\/(?:tokens|dice)\/[a-zA-Z0-9_.-]+\.(?:png|webp)/);return match?match[0]:null};
 const describe=(node,depth=0)=>{
   if(depth>5||!['SPAN','IMG'].includes(node.tagName))return null;
   if(node.classList.contains('sourceMinus'))return null;
   const img=asset(node.getAttribute('src')),background=asset(node.style.backgroundImage);
   return {tag:node.tagName.toLowerCase(),classes:node.className,text:node.children.length?'':node.textContent.slice(0,40),src:img,background,children:[...node.children].map(n=>describe(n,depth+1)).filter(Boolean)};
 };
 return [...document.querySelectorAll('#map>.spot')].map(spot=>({id:spot.dataset.region,classes:spot.className,children:[...spot.children].map(n=>describe(n)).filter(Boolean)}));
}

function renderFullJournal(root,entries,players,colors){
 const limit=Number(root.dataset.journalLimit)||80;
 root.innerHTML=entries.slice(0,limit).map(text=>'• '+renderLogEntry(text,players,colors)+'<br>').join('');
 if(entries.length>limit){const more=document.createElement('button');more.type='button';more.textContent='Afficher les événements précédents ('+(entries.length-limit)+')';more.onclick=()=>{root.dataset.journalLimit=String(limit+80);renderFullJournal(root,entries,players,colors)};root.appendChild(more)}
}
