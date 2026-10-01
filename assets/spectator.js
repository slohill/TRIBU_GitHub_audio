/* Public-only UI. Never applies spectator snapshots to the legacy game engine. */
(()=>{
 const el=(tag,text,cls)=>{const n=document.createElement(tag);if(text!==undefined)n.textContent=text;if(cls)n.className=cls;return n};
 const panel=el('aside',undefined,'activityPanel');panel.setAttribute('aria-label','Activité TRIBU en ligne');
 panel.innerHTML='<h2>🌐 TRIBU en ligne</h2><p class="activityStatus" id="activityStatus">Connexion à l’activité…</p><h3>Parties en cours</h3><div id="activityGames"></div><h3>Parties récentes</h3><div id="activityRecent"></div><button id="activityHistory">Voir l’historique</button><button id="activityRefresh">Actualiser</button>';
 $('start').appendChild(panel);
 const view=el('section',undefined,'spectatorView hidden');view.id='spectatorView';
 view.innerHTML='<header class="spectatorHeader"><span class="spectatorBadge">👁 MODE SPECTATEUR</span><h1 id="spectatorTitle"></h1><button id="spectatorLeave">Retour à l’accueil</button></header><p>Lecture seule · Informations publiques uniquement</p><div id="spectatorNotice" class="spectatorNotice"></div><div class="spectatorGrid"><div><div class="spectatorMap" id="spectatorMap"></div><div class="spectatorPlayers" id="spectatorPlayers"></div></div><aside class="spectatorSide"><section><h2>Tour en cours</h2><div id="spectatorTurn"></div></section><section><h2>Bataille</h2><div id="spectatorBattle"></div></section><section><h2>Oracle</h2><div id="spectatorOracle"></div></section><section><h2>Pioche et défausse</h2><div id="spectatorDeck"></div></section></aside></div><section class="spectatorJournal"><h2>Journal public</h2><ol id="spectatorLog"></ol></section>';
 document.body.appendChild(view);
 const historyOverlay=el('div',undefined,'activityHistoryOverlay hidden');historyOverlay.id='activityHistoryOverlay';historyOverlay.innerHTML='<section class="activityHistoryDialog" role="dialog" aria-modal="true" aria-labelledby="activityHistoryTitle"><header><h2 id="activityHistoryTitle">Historique des parties</h2><button id="activityHistoryClose">Fermer</button></header><p>Les 100 dernières parties terminées depuis l’activation de l’historique.</p><div id="activityHistoryBody"></div></section>';document.body.appendChild(historyOverlay);
 let socket=null,activity={games:[],recent:[]},watching=null,requestId=0;
 const date=value=>Number.isFinite(value)?new Date(value).toLocaleString('fr-FR',{dateStyle:'short',timeStyle:'short'}):'—';
 const faction=id=>FACTIONS[id]?.name||'—';
 function button(text,fn){const b=el('button',text);b.type='button';b.onclick=fn;return b}
 function publicCard(id,oracle=false){const c=oracle?ORACLES[id]:CARDS[id];if(!c)return el('span','—');return button(c.name,()=>openOfficialCard(c.name,oracle?'Oracle':c.type,c.effect||''))}
 function renderActivity(data){if(!data||!Array.isArray(data.games)||!Array.isArray(data.recent))return;activity=data;
   $('activityStatus').textContent=data.games.length+' partie(s) en cours'+(data.historyAvailable?'':' · Historique temporairement non enregistré');
   const games=$('activityGames');games.replaceChildren();
   for(const g of data.games){const row=el('div',undefined,'activityEntry');row.append(el('strong',g.name),el('small',(g.status==='setup'?'Placement':'Tour '+g.turn)+' · '+g.humans+' joueur(s) + '+g.bots+' bot(s)'),button('👁 Regarder',()=>watch(g.id)));games.appendChild(row)}
   if(!data.games.length)games.appendChild(el('p','Aucune partie en cours pour le moment.','spectatorEmpty'));
   const recent=$('activityRecent');recent.replaceChildren();for(const g of data.recent.slice(0,3)){const w=g.players[g.winner];const row=el('div',undefined,'activityEntry');row.append(el('strong',g.name),el('small',(w?w.name+' 🏆 · '+faction(w.faction):'Terminée')+' · '+g.turn+' tours'),el('small',date(g.finishedAt)));recent.appendChild(row)}
   if(!data.recent.length)recent.appendChild(el('p','Les prochaines parties terminées apparaîtront ici.','spectatorEmpty'));
   if(!historyOverlay.classList.contains('hidden'))renderHistory();
 }
 function renderHistory(){const body=$('activityHistoryBody');body.replaceChildren();if(!activity.recent.length){body.appendChild(el('p','Aucune partie terminée enregistrée pour le moment.'));return}
   const table=el('table'),head=el('tr');for(const label of ['Partie','Fin','Durée / tours','Joueurs et factions','Vainqueur'])head.appendChild(el('th',label));table.appendChild(head);
   for(const g of activity.recent){const row=el('tr');for(const value of [g.name+' · '+g.humans+'J + '+g.bots+' bots · '+g.victoryTarget+' PV',date(g.finishedAt),Math.floor(g.durationSeconds/60)+' min · '+g.turn+' tours',g.players.map(p=>p.name+' — '+faction(p.faction)+(p.bot?' (bot)':'')).join('\n'),g.players[g.winner]?.name||'—'])row.appendChild(el('td',value));table.appendChild(row)}body.appendChild(table);
 }
 function ack(event,payload={}){return new Promise((resolve,reject)=>{if(!socket?.connected)return reject(Error('Connexion au serveur indisponible.'));socket.timeout(12000).emit(event,payload,(err,res)=>err?reject(Error('Le serveur ne répond pas encore.')):res?.ok?resolve(res):reject(Error(res?.error||'Action indisponible.')))})}
 async function refresh(){try{connect();if(socket?.connected)renderActivity((await ack('subscribeActivity')).activity)}catch(e){$('activityStatus').textContent=e.message}}
 function connect(){if(socket)return;if(typeof io!=='function'){$('activityStatus').textContent='Le serveur est indisponible. Réessayez avec Actualiser.';return}
   socket=io(ONLINE_SERVER,{forceNew:true,transports:['websocket','polling']});
   socket.on('connect',async()=>{try{renderActivity((await ack('subscribeActivity')).activity);if(watching){const id=watching;const res=await ack('spectateGame',{id});if(watching===id)renderSpectator(res.state)}}catch(e){$('activityStatus').textContent=e.message;if(watching)$('spectatorNotice').textContent=e.message}});
   socket.on('publicActivity',renderActivity);socket.on('spectatorState',state=>{if(state.id===watching)renderSpectator(state)});
   socket.on('disconnect',()=>{$('activityStatus').textContent='Reconnexion au serveur…';if(watching)$('spectatorNotice').textContent='Connexion interrompue : le plateau est figé jusqu’à la reconnexion.'});
   socket.on('connect_error',()=>{$('activityStatus').textContent='Serveur indisponible ou en cours de réveil. Vous pouvez réessayer.'});
 }
 async function watch(id){if($('start').classList.contains('hidden'))return;const ticket=++requestId;try{const res=await ack('spectateGame',{id});if(ticket!==requestId||$('start').classList.contains('hidden')){await ack('leaveSpectator');return}
   watching=id;$('start').classList.add('hidden');view.classList.remove('hidden');audioEnterGame();renderSpectator(res.state);window.scrollTo(0,0);
 }catch(e){$('activityStatus').textContent=e.message}}
 function leave(){requestId++;watching=null;view.classList.add('hidden');$('start').classList.remove('hidden');closeOfficialCard();if(socket?.connected)ack('leaveSpectator').catch(()=>{});Object.values(audioTracks).forEach(a=>audioStopTrack(a));audioMaybeWelcome();window.scrollTo(0,0)}
 function renderSpectator(state){
   $('spectatorTitle').textContent=state.name;
   $('spectatorNotice').textContent=state.winner!==null?(state.players[state.winner]?.name||'Un joueur')+' remporte la partie !':state.connectedHumans===0?'Tous les joueurs sont déconnectés. En attente de leur retour.':state.status==='setup'?'Placement des joueurs en cours.':'Partie suivie en direct.';
   const name=i=>state.players[i]?.name||'Peuple hostile';
   const phases={setup:'Placement',start:'Début du tour',recruit:'Recrutement',play:'Phase de jeu',oracleMove:'Déplacement du Dragon',oracleRoll:'Oracle'};
   $('spectatorTurn').textContent=state.status==='setup'?'Placement initial · Victoire à '+state.victoryTarget+' PV':'Tour '+state.turn+' · '+name(state.active)+' · '+(phases[state.phase]||'Jeu')+' · Victoire à '+state.victoryTarget+' PV';
   const map=$('spectatorMap');map.replaceChildren();const img=el('img');img.alt='Carte publique de la partie';img.src=state.climate==='Canicule'?MAP_HEAT_SRC:state.climate==='Vague de froid'?MAP_COLD_SRC:MAP_NORMAL_SRC;map.appendChild(img);
   for(const [id,xy] of Object.entries(POS)){const spot=el('span',undefined,'spectatorSpot'+(state.battle?.target===id?' spectatorBattleSpot':''));spot.style.left=xy[0]+'%';spot.style.top=xy[1]+'%';const cell=state.board[id];let label=id;
     const token=(owner,count)=>{const t=el('span',String(count),'spectatorToken');t.style.backgroundColor=state.players[owner]?.color||'#ddd';t.title=name(owner)+' : '+count+' unités';spot.appendChild(t);label+=' · '+t.title};
     if(cell){if(cell.owner!==null&&cell.units>0)token(cell.owner,cell.units);else if(cell.hostile)spot.appendChild(el('span','PNJ','spectatorToken'));if(cell.building){const b=el('span',cell.building.type==='Portail'?'🌀':cell.building.type==='Forteresse'?'🏰':'🏛','spectatorBuilding');b.title=cell.building.type;spot.appendChild(b)}}
     else for(const [owner,count] of Object.entries(state.sea[id]?.fleets||{}))token(+owner,count);
     if(id===state.dragon)spot.appendChild(el('span','🐉','spectatorDragon'));spot.setAttribute('aria-label',label);spot.title=label;map.appendChild(spot);
   }
   const players=$('spectatorPlayers');players.replaceChildren();for(const p of state.players){const box=el('article',undefined,'spectatorPlayer');box.style.borderLeftColor=p.color;box.append(el('h2',p.name+(p.bot?' 🤖':'')),el('div',faction(p.faction)),el('div',(p.score===null?'PV en attente':p.score+' PV')+' · '+p.gold+' Or · '+p.handCount+' cartes en main'));const cards=el('div',undefined,'spectatorCards');for(const id of p.inPlay)cards.appendChild(publicCard(id));box.appendChild(cards);players.appendChild(box)}
   const battle=$('spectatorBattle');battle.replaceChildren();if(!state.battle)battle.textContent='Aucune bataille en cours.';else{const b=state.battle;battle.append(el('p',name(b.attacker)+' → '+name(b.defender)+' · '+(b.target||'Mer')),el('p','Attaque : '+(b.attackPower??'—')+' · Défense : '+(b.defensePower??'—')));for(const entry of b.stack)battle.appendChild(publicCard(entry.cardId))}
   const oracle=$('spectatorOracle');oracle.replaceChildren();oracle.append(el('p','Oracle actif'),state.oracleActive===null?el('span','Aucun'):publicCard(state.oracleActive,true),el('p','Oracle prochain'),state.oracleNext===null?el('span','Non visible actuellement'):publicCard(state.oracleNext,true));
   const deck=$('spectatorDeck');deck.replaceChildren(el('p',state.deckCount+' cartes dans la pioche · '+state.discard.length+' dans la défausse'));const publicDiscard=el('details');publicDiscard.appendChild(el('summary','Voir la défausse'));const list=el('div',undefined,'spectatorCards');for(const id of [...state.discard].reverse())list.appendChild(publicCard(id));publicDiscard.appendChild(list);deck.appendChild(publicDiscard);
   const log=$('spectatorLog');log.replaceChildren();for(const event of [...state.events].reverse())log.appendChild(el('li',event.text));
 }
 $('spectatorLeave').onclick=leave;$('activityRefresh').onclick=refresh;$('activityHistory').onclick=()=>{renderHistory();historyOverlay.classList.remove('hidden');$('activityHistoryClose').focus()};$('activityHistoryClose').onclick=()=>historyOverlay.classList.add('hidden');historyOverlay.onclick=e=>{if(e.target===historyOverlay)historyOverlay.classList.add('hidden')};
 document.addEventListener('keydown',e=>{if(e.key==='Escape')historyOverlay.classList.add('hidden')});
 connect();
})();
