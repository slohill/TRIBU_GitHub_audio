/* Guided UI only: setup, movement, combat and Oracle use the legacy engine. */
const tutorial={active:false,step:0,regions:[],pendingTurn:null,helpOpen:false};
const tutorialText=[null,
 'Tout d’abord, il vous faut placer vos unités. Une province (contour noir) vous a été assignée au hasard. Sur cette province, 4 Régions sont disponibles. Les Régions PNJ contiennent 5 unités que vous devrez conquérir durant la partie. Choisissez deux des quatre Régions : chacune recevra 3 unités.',
 'Ensuite, choisissez dans la colonne de droite votre couleur et votre faction. Cliquez sur les loupes pour voir le résumé des factions, puis validez votre placement.',
 'La partie commence et c’est à votre tour. Au début de votre tour, vous avez le choix entre piocher deux cartes, recruter des unités ou récolter deux d’or par Région possédée. Comme vous n’avez pas d’or et que vous n’avez que deux Régions, cliquez sur « Piocher ».',
 'Ensuite arrive votre « phase de jeu » : vous pouvez échanger des cartes et de l’or avec les autres, jouer des cartes et déplacer des unités pour conquérir d’autres territoires.',
 'Plus vous aurez de Régions, plus vos récoltes d’or seront conséquentes. Plus vous aurez de Régions, plus votre capacité de recrutement sera haute également.',
 'Chaque tour, chacune de vos unités a un point de déplacement vers une case adjacente pour conquérir une Région vierge, hostile ou que vous occupez déjà. Cliquez sur une Région éligible comme destination de vos unités.',
 'Ensuite, cliquez sur une ou plusieurs Régions adjacentes contenant vos unités : chaque clic = +1 unité ; un appui prolongé envoie toutes les unités disponibles de la Région. Puis validez avec ✓. Vous pouvez déplacer des unités autant qu’il est possible de le faire durant votre phase de jeu.',
 'Si vous déplacez des unités vers une Région occupée, cela ouvre une bataille. Pour la gagner, vous devez avoir plus de « points de bataille » que l’adversaire qui se défend. Vous pourrez jouer des cartes si vos unités ne suffisent pas.',
 'Durant votre phase de jeu, vous pouvez jouer des cartes permanentes qui restent en jeu (fond noir) ou des cartes tactiques qui partent à la défausse (fond vert), déplacer d’autres unités et commercer avec les autres joueur·euse·s autant que vous voulez. Quand vous avez terminé, cliquez sur « Passer à l’Oracle », puis confirmez pour clore votre phase de jeu.',
 'La phase Oracle consiste à déplacer le Dragon d’une case, puis à lancer le dé de 6 :\n6 — le Dragon détruit la case sur laquelle vous l’avez placé.\n1 — la carte Oracle visible sur le dessus de la pioche s’active.\n2 / 3 / 4 / 5 — rien ne se passe, sauf effet d’un Oracle actif. Terminez les éventuels choix demandés par l’Oracle.',
 'Voilà, vous savez jouer à Tribu ! Aux prochains tours, vous pourrez Piocher comme vous l’avez fait, ou Récolter 2 d’or par Région possédée. Quand vous aurez suffisamment d’or et de Régions, cliquez sur Recruter pour renforcer vos armées ! La victoire est à 3 points. Et pour savoir comment gagner des points de victoire, cliquez sur « Aide de jeu » en haut de votre écran. Bonnes parties !'];
const tutorialFactionHelp={
 0:'Les peuples nordiques ont un recrutement facilité en terres enneigées et sont immunisés au givre.',
 1:'Les peuples du désert ont un recrutement facilité en régions désertiques et sont immunisés aux tempêtes de sable.',
 2:'Le peuple des bâtisseurs, leurs forces valent triple lors de batailles défensives. Cependant, ils ont un plafond de recrutement moins élevé que les autres factions. Ce plafond est égal à 2 × le nombre de Régions possédées, au lieu de 3 × pour les autres.'

};
const tutorialBubble=document.createElement('section');
tutorialBubble.id='tutorialBubble';tutorialBubble.className='hidden';
tutorialBubble.setAttribute('aria-label','Tutoriel TRIBU');
document.querySelector('.boardCol').prepend(tutorialBubble);
const tutorialHelp=document.createElement('div');
tutorialHelp.id='tutorialHelp';tutorialHelp.className='hidden';$('map').appendChild(tutorialHelp);

$('tutorialBtn').onclick=()=>{
 onlinePseudo();tutorial.active=true;tutorial.step=1;tutorial.pendingTurn=null;tutorial.regions=[];
 launchLegacyMode('1v3',3);
};
function startTutorialSetup(){
 const provinces=shuffleInPlace([...new Set(Object.values(R).map(v=>v[0]))]);
 setupState={stage:'regions',index:0,configured:Array(G.players.length).fill(null),assignedProvinces:provinces.slice(0,G.players.length),selectedColor:null,selectedFaction:null,selectedRegions:[]};
 G.phase='setup';G.active=0;G.players[0].name=onlinePseudo();
 onlineSetupLayout(true);render();renderSetupRegions();
 // The second region selection advances to identity; no extra confirmation here.
 $('setupChoices').innerHTML='';
}
function tutorialChooseIdentity(){
 tutorial.regions=setupState.selectedRegions.slice();tutorial.step=2;tutorialCloseHelp();
 renderSetupIdentity();
 $('setupTitle').textContent='Votre couleur et votre faction';
 $('setupText').textContent='Vos deux Régions sont choisies. Validez pour y placer 3 unités chacune.';
 $('setupIdentityConfirm').textContent='Valider mon placement';
 // Keep the existing portrait selection handlers, with a separate help button.
 document.querySelectorAll('#setupChoices .setupFactionPortrait').forEach(button=>{
   const label=button.querySelector('img').alt;
   const meta=Object.values(FACTION_PORTRAIT_META).find(m=>m.label===label);
   const wrap=document.createElement('div');wrap.className='tutorialFaction';button.before(wrap);wrap.appendChild(button);
   const help=document.createElement('button');help.className='tutorialLens';help.textContent='⌕';help.type='button';
   help.setAttribute('aria-label','Aide '+label);help.onclick=()=>tutorialShowHelp(meta.faction);wrap.appendChild(help);
 });
 render();
}
function tutorialConfigureBot(){
 const i=setupState.index;
 const usedColors=new Set(setupState.configured.filter(Boolean).map(c=>c.color));
 const usedPortraits=new Set(setupState.configured.filter(Boolean).map(c=>c.portrait));
 const color=BASE_COLORS.find(c=>!usedColors.has(c));
 const keys=Object.keys(FACTION_PORTRAIT_META).filter(k=>!usedPortraits.has(k));
 const portrait=keys[Math.floor(Math.random()*keys.length)],faction=FACTION_PORTRAIT_META[portrait].faction;
 COLORS[i]=color;Object.assign(G.players[i],{faction,portrait});
 setupState.configured[i]={color,faction,portrait};setupState.stage='regions';
 setupState.selectedRegions=shuffleInPlace(setupProvinceRegions(setupState.assignedProvinces[i])).slice(0,2);
 confirmSetupRegions();
}
function tutorialCloseHelp(){tutorial.helpOpen=false;tutorialHelp.classList.add('hidden');tutorialHelp.replaceChildren()}
function tutorialShowHelp(faction){
 tutorialHelp.replaceChildren();tutorialHelp.className=faction===undefined?'tutorialMapHelp':'tutorialFactionHelp';
 if(faction===undefined){
   const img=document.createElement('img');img.src='assets/images/tutorial/Loupemap.png';img.alt='Aide : provinces, Régions et Régions PNJ';
   tutorialHelp.appendChild(img);img.onload=tutorialPositionMapHelp;tutorialPositionMapHelp();
 }else tutorialHelp.textContent=tutorialFactionHelp[faction]+' Cliquez n’importe où pour fermer.';
 tutorial.helpOpen=true;
}
function tutorialPositionMapHelp(){
 if(!tutorialHelp.classList.contains('tutorialMapHelp'))return;
 const board=$('boardMapImage'),img=tutorialHelp.querySelector('img');
 if(!img||!board.naturalWidth)return;
 // Original-size asset in the map's native pixel coordinate system.
 const scale=board.clientWidth/board.naturalWidth;
 tutorialHelp.style.left=(899*scale)+'px';tutorialHelp.style.top=(63*scale)+'px';
 img.style.width=(img.naturalWidth*scale)+'px';
}
new ResizeObserver(tutorialPositionMapHelp).observe($('boardMapImage'));
function tutorialHoldTurn(reason){
 if(!tutorial.active)return false;
 if(tutorial.step===11)return true;
 // Also catch elimination during free play: retain the legacy result and pause its handoff.
 if(G.active!==0||tutorial.step<9)return false;
 tutorial.pendingTurn=reason;tutorial.step=11;tutorialCloseHelp();
 clearTimeout(botTimer);botTimer=null;botToken++;
 renderTutorial();return true;
}
function tutorialContinue(){
 const reason=tutorial.pendingTurn;
 tutorial.active=false;tutorial.pendingTurn=null;tutorialCloseHelp();renderTutorial();
 advanceTurn(reason||'suite du tutoriel');
}
function tutorialNext(){
 if(![4,5,8].includes(tutorial.step))return;
 tutorial.step++;
 render();
 if(tutorial.step===9&&battle)resumeBattleTimer();
}
function renderTutorial(){
 renderTutorialPlacement();
 document.querySelectorAll('.tutorialHighlight').forEach(e=>e.classList.remove('tutorialHighlight'));
 if(!tutorial.active||gameOverState){tutorialBubble.classList.add('hidden');return}
 if(tutorial.step===3&&G.phase==='play')tutorial.step=4;
 if(tutorial.step===6&&dest)tutorial.step=7;
 if(tutorial.step===7&&!dest&&!battle)tutorial.step=6;
 if(tutorial.step===9&&['oracleMove','oracleRoll','oracleResolving'].includes(G.phase))tutorial.step=10;
 if(tutorial.step===8&&battle){clearInterval(battleTick);clearTimeout(botReactionTimer);botReactionTimer=null}
 const step=tutorial.step;
 if(step===11){$('oracleBox').classList.add('hidden');$('roll').disabled=true}
 tutorialBubble.classList.remove('hidden');
 if(tutorialBubble.dataset.step!==String(step)){
   tutorialBubble.dataset.step=step;tutorialBubble.replaceChildren();
   const title=document.createElement('strong');title.textContent='Partie Tutoriel · '+step+' / 11';tutorialBubble.appendChild(title);
   const text=document.createElement('p');text.textContent=tutorialText[step];tutorialBubble.appendChild(text);
   const add=(label,action,cls)=>{const b=document.createElement('button');b.textContent=label;b.onclick=action;if(cls)b.className=cls;tutorialBubble.appendChild(b)};
   if(step===1)add('⌕ Voir la carte',()=>tutorialShowHelp(),'tutorialLens');
   if([4,5,8].includes(step))add('Suivant',tutorialNext);
   if(step===11){add('Continuer la partie',tutorialContinue);add('Retour au menu',()=>location.reload())}
 }
 const highlight=selector=>document.querySelectorAll(selector).forEach(e=>e.classList.add('tutorialHighlight'));
 if(step===3)highlight('#draw');
 if(step===1)highlight('.setupRegionReady,.setupRegionChosen');
 if(step===6)document.querySelectorAll('.spot').forEach(e=>{if(legalSources(e.dataset.region).length)e.classList.add('tutorialHighlight')});
 if(step===7)highlight('.spot.src,.floatActions .yes');
 if(step===10)highlight(G.phase==='oracleMove'?'.spot.oracle':'#roll');
}
function tutorialAllows(target){
 if(target.closest('.buildingPreview,#cardZoomOverlay,#commerceClose,#commerceDraftCancel,#gameHelpBtn,#gameHelpOverlay,#actionConfirmOverlay,#actionInfoPreview,#factionInfoOverlay,.factionInfoBtn'))return true;
 if(!tutorial.active||gameOverState)return true;
 if(target.closest('#tutorialBubble'))return true;
 const step=tutorial.step;
 // Free play still cannot restart/leave the guided game before the final bubble.
 if(target.closest('#restart,#victoryRestart'))return false;
 if(step===9)return true;
 if(step===2)return !!target.closest('#setupChoices');
 if(step===3)return !!target.closest('#draw');
 const spot=target.closest('.spot');
 if(step===1)return !!spot&&setupProvinceRegions(setupState.assignedProvinces[0]).includes(spot.dataset.region);
 if(step===6)return !!spot&&legalSources(spot.dataset.region).length>0;
 if(step===7)return !!target.closest('.floatActions')||!!spot&&legalSources(dest).includes(spot.dataset.region);
 if(step===10){
   // Oracle resolutions can ask for sacrifices, Dragon moves and notice dismissal.
   if(spot)return G.phase==='oracleMove'?dragonTargets().includes(spot.dataset.region):!!oracleState||!!dragonRichState;
   return !!target.closest('#roll,#oracleNoticeOverlay,#dragonSixOverlay,#dragonPublicOverlay,#dragonCurseOverlay,.dragonRestart,#battleBanner');
 }
 return false;
}
function tutorialCapture(e){
 if(!tutorial.active)return;
 if(e.type==='click'&&tutorial.helpOpen){tutorialCloseHelp();e.preventDefault();e.stopImmediatePropagation();return}
 if(e.type==='keydown'&&!['Enter',' '].includes(e.key))return;
 if(tutorialAllows(e.target))return;
 e.preventDefault();e.stopImmediatePropagation();
}
// Capture all activation routes, including long press and keyboard-generated clicks.
['click','pointerdown','mousedown','touchstart','keydown','contextmenu'].forEach(type=>document.addEventListener(type,tutorialCapture,{capture:true,passive:false}));

function renderTutorialPlacement(){
 document.querySelectorAll('.tutorialPlacementDie').forEach(el=>el.remove());
 if(!tutorial.active||!setupState||tutorial.step>2)return;
 const regions=tutorial.step===1?setupState.selectedRegions:tutorial.regions;
 regions.forEach(region=>{
   const spot=document.querySelector('.spot[data-region="'+region+'"]');if(!spot)return;
   const die=document.createElement('span');die.className='onlineSetupPreviewDie tutorialPlacementDie';
   die.textContent='3';die.style.backgroundColor=setupState.selectedColor||'#fff';spot.appendChild(die);
 });
}

const gameHelpOverlay=document.createElement('div');
gameHelpOverlay.id='gameHelpOverlay';gameHelpOverlay.className='hidden';
gameHelpOverlay.setAttribute('role','dialog');gameHelpOverlay.setAttribute('aria-label','Aide de jeu');gameHelpOverlay.setAttribute('aria-modal','true');
const gameHelpImage=document.createElement('img');gameHelpImage.src='assets/images/tutorial/Aidedejeu.jpg?v=2';gameHelpImage.alt='Aide de jeu TRIBU : comment gagner des points de victoire';
gameHelpOverlay.appendChild(gameHelpImage);document.body.appendChild(gameHelpOverlay);
$('gameHelpBtn').onclick=()=>{tutorialCloseHelp();gameHelpOverlay.classList.remove('hidden')};
gameHelpOverlay.onclick=e=>{if(e.target===gameHelpOverlay){gameHelpOverlay.classList.add('hidden');$('gameHelpBtn').focus()}};
document.addEventListener('keydown',e=>{if(e.key==='Escape'&&!gameHelpOverlay.classList.contains('hidden')){gameHelpOverlay.classList.add('hidden');$('gameHelpBtn').focus()}});

