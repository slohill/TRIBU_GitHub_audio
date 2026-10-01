/* UI confirmations delegate to the legacy actions; bots keep direct access. */
let pendingActionConfirmation=null;
const interactionOverlay=document.createElement('div');
interactionOverlay.id='actionConfirmOverlay';interactionOverlay.className='interactionOverlay hidden';
interactionOverlay.innerHTML='<section role="dialog" aria-modal="true" aria-labelledby="actionConfirmTitle"><h2 id="actionConfirmTitle"></h2><div id="actionConfirmText"></div><div id="actionConfirmChoices"></div><button id="actionConfirmCancel">Annuler</button></section>';
document.body.appendChild(interactionOverlay);
function closeActionConfirmation(){pendingActionConfirmation=null;interactionOverlay.classList.add('hidden')}
$('actionConfirmCancel').onclick=closeActionConfirmation;
interactionOverlay.onclick=e=>{if(e.target===interactionOverlay)closeActionConfirmation()};
document.addEventListener('keydown',e=>{if(e.key==='Escape'){closeActionConfirmation();$('factionInfoOverlay').classList.add('hidden')}});
function requestActionConfirmation(title,text,actions,valid){
 closeActionConfirmation();pendingActionConfirmation={valid};
 $('actionConfirmTitle').textContent=title;$('actionConfirmText').textContent=text;
 const box=$('actionConfirmChoices');box.replaceChildren();
 actions.forEach(({label,run})=>{const b=document.createElement('button');b.textContent=label;b.onclick=()=>{
   const request=pendingActionConfirmation;closeActionConfirmation();
   if(request&&request.valid())run();
 };box.appendChild(b)});
 interactionOverlay.classList.remove('hidden');$('actionConfirmCancel').focus();
}
function interactionContextValid(){
 const game=G,active=G.active,turn=G.turn,phase=G.phase,epoch=turnEpoch,viewer=localViewer();
 const hand=JSON.stringify(G.players[viewer].hand),fight=battle,priority=battle?currentPriorityPlayer():null;
 const gold=goldReaction,paid=paidDrawState;
 return ()=>G===game&&!gameOverState&&G.active===active&&G.turn===turn&&G.phase===phase&&turnEpoch===epoch&&localViewer()===viewer&&
   JSON.stringify(G.players[viewer].hand)===hand&&battle===fight&&goldReaction===gold&&paidDrawState===paid&&
   (!battle||(currentPriorityPlayer()===priority&&(isHotseatMode()||battle.seconds>0)));
}
function confirmStartAction(name,action){
 if(!G||G.phase!=='start'||localViewer()!==G.active||isBot()||paidDrawState||goldReaction)return;
 const texts={Piocher:'Piochez 2 cartes TRIBU, puis passez à la phase de jeu. Vous ne pourrez pas choisir Récolter ou Recruter à la place ce tour-ci.',
 Récolter:'Gagnez 2 Or par région contrôlée, plus les bonus de vos cités. Ce gain peut être intercepté par Embuscade. Vous choisirez Récolter à la place de Piocher ou Recruter.',
 Recruter:'Entrez dans la phase de recrutement à la place de Piocher ou Récolter. Dépensez votre Or sur vos régions, selon les règles de votre faction et votre plafond d’unités. Aucun Or n’est dépensé par cette confirmation.'};
 requestActionConfirmation(name,texts[name],[{label:'Confirmer : '+name.toLowerCase(),run:action}],interactionContextValid());
}
function addBalistesTurnBonus(owner,side){
 if(side==='attacker')G.players[owner].attackTurnBonus=(G.players[owner].attackTurnBonus||0)+2;
 if(side==='defender')G.players[owner].defenseTurnBonus=(G.players[owner].defenseTurnBonus||0)+2;
}
function canPlayBalistesOutsideBattle(owner){
 return G&&['start','recruit','play','oracleMove','oracleRoll'].includes(G.phase)&&!battle&&!gameOverState&&!choiceState&&!goldReaction&&!paidDrawState&&!caravanState&&!divinationState&&!oracleState&&!oracleNoticeState&&!dragonSixState&&!dragonPublicState&&!shadowState&&!egnoState&&!returnState&&!dragonRichState&&!dragonCurseState&&!buildingMode&&!portalMode&&
   owner===localViewer()&&!G.players[owner].bot&&!isDecimated(owner)&&!(G.online&&!G.online.legacySync);
}
function playBalistesOutsideBattle(handIndex,side){
 const owner=localViewer();if(!canPlayBalistesOutsideBattle(owner)||!['attacker','defender'].includes(side))return;
 const id=G.players[owner].hand[handIndex];if(id===undefined||CARDS[id].name!=='Balistes')return;
 if(G.phase==='recruit'&&recruitSnapshot)resetRecruitmentForPriorityCard(owner,'Balistes');
 discardHandCard(owner,handIndex);addBalistesTurnBonus(owner,side);
 log(p(owner).name+' joue Balistes : +2 '+(side==='attacker'?'Attaque':'Défense')+' jusqu’à la fin du tour en cours.');
 render();if(G.online&&G.online.legacySync)onlineLegacyPushNow();
}
function wireCardConfirmations(){
 const owner=displayedHandViewer();if(owner===null||owner!==localViewer()||G.players[owner].bot)return;
 [...$('hand').children].forEach((el,index)=>{
   const id=G.players[owner].hand[index],c=CARDS[id];if(!c)return;
   if(c.name==='Balistes'&&canPlayBalistesOutsideBattle(owner)){
     el.classList.add('playablePermanent');el.title='Balistes : choisir un bonus jusqu’à la fin du tour';
     el.onclick=()=>requestActionConfirmation('Balistes','Choisissez +2 à chacune de vos attaques OU +2 à chacune de vos défenses jusqu’à la fin du tour actuellement en cours. La carte sera défaussée.',[
       {label:'Confirmer +2 Attaque',run:()=>playBalistesOutsideBattle(index,'attacker')},
       {label:'Confirmer +2 Défense',run:()=>playBalistesOutsideBattle(index,'defender')}],interactionContextValid());return;
   }
   if(!el.onclick||el.onclick===el._confirmationHandler||!['Taxe','Conseil de guerre','Montures','Balistes'].includes(c.name))return;
   const action=el.onclick;
   el.onclick=ev=>{
     let text=c.name==='Taxe'?'Gagnez 1 Or par case occupée par vos unités. Ce gain peut être intercepté par Embuscade.':
       c.name==='Conseil de guerre'?'Piochez 2 cartes TRIBU, puis choisissez 2 cartes de votre main à défausser.':
       c.name==='Montures'?(battle?'Ajoutez +4 Attaque pour cette bataille.':'Toutes vos unités gagnent 1 point de déplacement jusqu’à la fin de votre tour. Une même région ne peut toujours pas être attaquée deux fois par les déplacements normaux.'):
       '+2 '+(battle&&owner===battle.attacker?'Attaque sur chacune de vos attaques':'Défense sur chacune de vos défenses')+' jusqu’à la fin du tour actuellement en cours.';
     requestActionConfirmation(c.name,text+' La carte sera consommée uniquement après confirmation.',[{label:'Confirmer : jouer la carte',run:()=>action.call(el,ev)}],interactionContextValid());
   };
   el._confirmationHandler=el.onclick;
 });
}
const factionInfoOverlay=document.createElement('div');factionInfoOverlay.id='factionInfoOverlay';factionInfoOverlay.className='interactionOverlay hidden';
factionInfoOverlay.innerHTML='<section role="dialog" aria-modal="true" aria-labelledby="factionInfoTitle"><h2 id="factionInfoTitle"></h2><img id="factionInfoImage" alt=""><p id="factionInfoText"></p><button id="factionInfoClose">Fermer</button></section>';
document.body.appendChild(factionInfoOverlay);
$('factionInfoClose').onclick=()=>factionInfoOverlay.classList.add('hidden');
factionInfoOverlay.onclick=e=>{if(e.target===factionInfoOverlay)factionInfoOverlay.classList.add('hidden')};
function addSetupFactionInfo(button,key){
 if(tutorial.active)return; // The tutorial already supplies its own faction magnifiers.
 const hint=document.createElement('span');hint.className='factionInfoBtn';hint.textContent='⌕';hint.tabIndex=0;hint.setAttribute('role','button');hint.setAttribute('aria-label','Informations sur '+FACTION_PORTRAIT_META[key].label);
 const open=e=>{e.preventDefault();e.stopPropagation();const f=FACTIONS[FACTION_PORTRAIT_META[key].faction];
   $('factionInfoTitle').textContent=f.name;$('factionInfoImage').src=FACTION_PORTRAITS[key];$('factionInfoImage').alt=f.name;
   $('factionInfoText').textContent='Plafond : '+f.cap+' unités par région contrôlée. Défense : '+f.def+' par unité. '+(f.name==='Griffes-Blanches'?'Recrutement : 2 unités par Or dans la neige, 1 en terrain tempéré, interdit dans le désert. Immunité à Givre mortel.':f.name==='Reptones'?'Recrutement : 2 unités par Or dans le désert, 1 en terrain tempéré, interdit dans la neige. Immunité à Tempête de sable.':'Recrutement : 1 unité par Or, sur tous les terrains.');
   factionInfoOverlay.classList.remove('hidden');$('factionInfoClose').focus();
 };
 hint.onclick=open;hint.onkeydown=e=>{if(e.key==='Enter'||e.key===' ')open(e)};hint.onpointerdown=e=>e.stopPropagation();button.appendChild(hint);
}
function movementSuggestionTargets(){
 if(!G||G.phase!=='play'||localViewer()!==G.active||isBot()||battle||gameOverState||paidDrawState||goldReaction||choiceState||caravanState||divinationState||oracleState||shadowState||egnoState||returnState||dragonRichState||dragonCurseState||buildingMode||portalMode)return [];
 if(G.online&&!G.online.legacySync)return Object.keys(POS).filter(id=>onlineLegalMoveSources(id).length);
 return Object.keys(POS).filter(id=>legalSources(id).length&&(enemyRegion(id)?!attacked.has(id):destinationAvailable(id)));
}
['draw','harvest','recruit'].forEach((id,i)=>{const action=$(id).onclick;$(id).onclick=()=>confirmStartAction(['Piocher','Récolter','Recruter'][i],action)});
