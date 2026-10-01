/* Two clicks or a long press activate existing legacy actions. */
let pendingActionConfirmation=null,actionPreviewState=null,suppressActionClick=false;
const actionPreview=document.createElement('div');actionPreview.id='actionInfoPreview';actionPreview.className='inPlayPreview hidden';
actionPreview.setAttribute('role','status');document.body.appendChild(actionPreview);
const interactionOverlay=document.createElement('div');
interactionOverlay.id='actionConfirmOverlay';interactionOverlay.className='interactionOverlay hidden';
interactionOverlay.innerHTML='<section role="dialog" aria-modal="true" aria-labelledby="actionConfirmTitle"><h2 id="actionConfirmTitle"></h2><div id="actionConfirmText"></div><div id="actionConfirmChoices"></div><button id="actionConfirmCancel">Annuler</button></section>';
document.body.appendChild(interactionOverlay);
function closeActionPreview(){actionPreviewState=null;actionPreview.classList.add('hidden');document.querySelectorAll('.actionPreviewSelected').forEach(el=>el.classList.remove('actionPreviewSelected'))}
function closeActionConfirmation(){pendingActionConfirmation=null;interactionOverlay.classList.add('hidden');closeActionPreview()}
$('actionConfirmCancel').onclick=closeActionConfirmation;
interactionOverlay.onclick=e=>{if(e.target===interactionOverlay)closeActionConfirmation()};
document.addEventListener('keydown',e=>{if(e.key==='Escape'){closeActionConfirmation();$('factionInfoOverlay').classList.add('hidden')}});
document.addEventListener('click',e=>{
 if(suppressActionClick){suppressActionClick=false;e.preventDefault();e.stopImmediatePropagation();return}
 if(!e.target.closest('[data-action-gesture],#actionInfoPreview'))closeActionPreview();
},true);
document.addEventListener('pointerup',()=>{if(suppressActionClick)setTimeout(()=>suppressActionClick=false,0)},true);
function requestActionConfirmation(title,text,actions,valid){
 closeActionConfirmation();pendingActionConfirmation={valid};
 $('actionConfirmTitle').textContent=title;$('actionConfirmText').textContent=text;
 const box=$('actionConfirmChoices');box.replaceChildren();
 actions.forEach(({label,run})=>{const b=document.createElement('button');b.textContent=label;b.onclick=()=>{
   const request=pendingActionConfirmation;closeActionConfirmation();if(request&&request.valid())run();
 };box.appendChild(b)});
 interactionOverlay.classList.remove('hidden');$('actionConfirmCancel').focus();
}
function interactionContextValid(startAction=false){
 const game=G,active=G.active,turn=G.turn,phase=G.phase,epoch=turnEpoch,viewer=localViewer();
 const hand=JSON.stringify(G.players[viewer].hand),fight=battle,priority=battle?currentPriorityPlayer():null;
 const gold=goldReaction,paid=paidDrawState;
 return ()=>G===game&&!gameOverState&&G.active===active&&G.turn===turn&&G.phase===phase&&turnEpoch===epoch&&
   (startAction?canUseStartAction():localViewer()===viewer&&JSON.stringify(G.players[viewer].hand)===hand)&&
   battle===fight&&goldReaction===gold&&paidDrawState===paid&&
   (!battle||(currentPriorityPlayer()===priority&&(isHotseatMode()||battle.seconds>0)));
}
function canUseStartAction(){
 return G&&G.phase==='start'&&!gameOverState&&!isBot()&&!isDecimated(G.active)&&!paidDrawState&&!goldReaction&&
   (isHotseatMode()||localViewer()===G.active);
}
function bindActionGesture(el,key,title,text,run,available=()=>true,startAction=false){
 el.dataset.actionGesture=key;el._actionSpec={key,title,text,run,available,startAction};
 el.classList.toggle('actionPreviewSelected',!!actionPreviewState&&actionPreviewState.key===key&&actionPreviewState.valid());
 if(el._gestureClick&&el.onclick===el._gestureClick)return;
 let timer=null,origin=null;
 const cancel=()=>{clearTimeout(timer);timer=null};
 const execute=(spec,event,valid)=>{closeActionConfirmation();if(spec.available()&&valid())spec.run(event)};
 el._gestureClick=event=>{
   const spec=el._actionSpec;if(!spec.available())return;
   if(actionPreviewState&&actionPreviewState.key===spec.key&&actionPreviewState.valid()){
     execute(spec,event,actionPreviewState.valid);return;
   }
   closeActionPreview();actionPreviewState={key:spec.key,valid:interactionContextValid(spec.startAction)};
   const h=document.createElement('h3');h.textContent=spec.title;
   const body=document.createElement('div');body.className='previewEffect';body.textContent=spec.text;
   const hint=document.createElement('div');hint.className='previewHint';hint.textContent='Recliquez sur le même élément pour l’utiliser · appui long = utilisation directe';
   actionPreview.replaceChildren(h,body,hint);actionPreview.classList.remove('hidden');el.classList.add('actionPreviewSelected');
   const r=el.getBoundingClientRect(),width=actionPreview.offsetWidth,height=actionPreview.offsetHeight;
   const left=r.left>=width+20?r.left-width-12:Math.max(8,Math.min(innerWidth-width-8,r.left));
   const top=r.left>=width+20?Math.max(8,Math.min(innerHeight-height-8,r.top)):r.top>=height+16?r.top-height-8:Math.min(innerHeight-height-8,r.bottom+8);
   actionPreview.style.left=left+'px';actionPreview.style.top=Math.max(8,top)+'px';
 };
 el.onclick=el._gestureClick;
 el.onpointerdown=e=>{
   if(e.button!==0||e.target.closest('.cardArtHint'))return;
   cancel();origin={x:e.clientX,y:e.clientY};const spec=el._actionSpec;if(!spec.available())return;
   const valid=interactionContextValid(spec.startAction);
   timer=setTimeout(()=>{timer=null;if(!valid()||!spec.available())return;suppressActionClick=true;execute(spec,e,valid)},520);
 };
 el.onpointermove=e=>{if(origin&&Math.hypot(e.clientX-origin.x,e.clientY-origin.y)>8)cancel()};
 el.onpointerup=el.onpointercancel=el.onpointerleave=el.ondragstart=cancel;
}
function wireStartActionGestures(){
 const texts=['Piochez 2 cartes TRIBU, puis passez à la phase de jeu. Cela remplace Récolter ou Recruter pour ce tour.',
 'Gagnez 2 Or par région contrôlée, plus les bonus de vos cités. Ce gain peut être intercepté par Embuscade. Cela remplace Piocher ou Recruter.',
 'Recrutez en dépensant votre Or sur vos régions, selon votre faction et votre plafond d’unités. Cela remplace Piocher ou Récolter. Entrer dans cette phase ne dépense pas d’Or.'];
 ['draw','harvest','recruit'].forEach((id,i)=>bindActionGesture($(id),'start:'+G?.active+':'+id,['Piocher','Récolter','Recruter'][i],texts[i],()=>{
   if(isHotseatMode())hotseatViewerOverride=G.active;
   [doDraw,doHarvest,doRecruit][i]();
 },canUseStartAction,true));
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
 wireStartActionGestures();
 const owner=displayedHandViewer();if(owner===null||owner!==localViewer()||G.players[owner].bot)return;
 [...$('hand').children].forEach((el,index)=>{
   const id=G.players[owner].hand[index],c=CARDS[id];if(!c)return;
   const key='card:'+owner+':'+index+':'+id;
   if(c.name==='Balistes'&&canPlayBalistesOutsideBattle(owner)){
     el.classList.add('playablePermanent');el.title='Balistes : choisir un bonus jusqu’à la fin du tour';
     const text='Choisissez +2 à chacune de vos attaques OU +2 à chacune de vos défenses jusqu’à la fin du tour actuellement en cours.';
     bindActionGesture(el,key,'Balistes',text,()=>requestActionConfirmation('Balistes — choisir le bonus',text,[
       {label:'+2 Attaque',run:()=>playBalistesOutsideBattle(index,'attacker')},
       {label:'+2 Défense',run:()=>playBalistesOutsideBattle(index,'defender')}],interactionContextValid()),()=>canPlayBalistesOutsideBattle(owner));return;
   }
   if(!el.onclick||el.onclick===el._gestureClick||!['Taxe','Conseil de guerre','Montures','Balistes'].includes(c.name))return;
   const action=el.onclick;
   const text=c.name==='Taxe'?'Gagnez 1 Or par case occupée par vos unités. Ce gain peut être intercepté par Embuscade.':
     c.name==='Conseil de guerre'?'Piochez 2 cartes TRIBU, puis choisissez 2 cartes de votre main à défausser.':
     c.name==='Montures'?(battle?'Ajoutez +4 Attaque pour cette bataille.':'Toutes vos unités gagnent 1 point de déplacement jusqu’à la fin de votre tour. Une même région ne peut toujours pas être attaquée deux fois par les déplacements normaux.'):
     '+2 '+(battle&&owner===battle.attacker?'Attaque sur chacune de vos attaques':'Défense sur chacune de vos défenses')+' jusqu’à la fin du tour actuellement en cours.';
   bindActionGesture(el,key,c.name,text,event=>action.call(el,event),()=>localViewer()===owner&&!gameOverState&&G.players[owner].hand[index]===id&&(!battle||isHotseatMode()||battle.seconds>0));
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

wireStartActionGestures();
