from pathlib import Path
p=Path('server/server.js'); s=p.read_text()
old="  socket.on('setupIdentity', (payload = {}, ack = () => {}) => {"
insert="""  socket.on('setupComplete', (payload = {}, ack = () => {}) => {
    const room = roomForSocket(socket);
    if (!room || !room.game || !room.game.setup) return rejectGameAction(ack, 'Installation indisponible.');
    const game = room.game;
    const index = humanGameIndex(room, socket.id);
    if (index < 0) return rejectGameAction(ack, 'Joueur introuvable.');
    if (game.setup.activePlayer !== index) return rejectGameAction(ack, 'Ce n’est pas votre tour de vous installer.');
    const color = String(payload.color || '');
    const portrait = String(payload.portrait || '');
    const regions = Array.isArray(payload.regions) ? payload.regions.map(String) : [];
    const unique = [...new Set(regions)];
    const player = game.players[index];
    const allowed = PROVINCE_REGIONS[player.province] || [];
    if (!COLORS.includes(color)) return rejectGameAction(ack, 'Couleur invalide.');
    if (!PORTRAITS.includes(portrait)) return rejectGameAction(ack, 'Faction invalide.');
    if (game.players.some((p, i) => i !== index && p.color === color)) return rejectGameAction(ack, 'Cette couleur est déjà prise.');
    if (game.players.some((p, i) => i !== index && p.portrait === portrait)) return rejectGameAction(ack, 'Cet encart de faction est déjà pris.');
    if (unique.length !== 2 || !unique.every(r => allowed.includes(r))) return rejectGameAction(ack, 'Choisissez exactement deux régions valides de votre province.');
    player.color = color; player.portrait = portrait; player.faction = PORTRAIT_FACTION[portrait]; player.regions = unique;
    unique.forEach(r => { game.board[r].owner = index; game.board[r].units = 3; game.board[r].hostile = false; });
    game.setup.activePlayer++; game.setup.stage = 'identity'; game.revision++;
    ack({ ok: true }); completeSetupIfReady(room); if (game.setup) emitGame(room);
  });

"""+old
assert old in s
p.write_text(s.replace(old,insert,1))

p=Path('index.html'); s=p.read_text()
old="let onlineSocket=null,onlineRoom=null,onlineSelectedMode='3h',onlineReadyState=false,onlineGameState=null,onlineSetupSelectedRegions=[];"
new="let onlineSocket=null,onlineRoom=null,onlineSelectedMode='3h',onlineReadyState=false,onlineGameState=null,onlineSetupSelectedRegions=[],onlineSetupDraft={color:null,portrait:null};"
assert old in s; s=s.replace(old,new,1)
start=s.index('function renderOnlineAuthoritativeSetup(state){'); end=s.index('function onlineSetupIdentityReady(box)',start)
replacement=r'''function onlineSetupLayout(active){
 const panel=$('setupPanel'),right=document.querySelector('.rightSection'),map=$('map');
 if(active){if(right&&panel.parentNode!==right)right.insertBefore(panel,right.firstChild);if(right){const title=right.querySelector(':scope > b');if(title)title.style.display='none';const grid=right.querySelector(':scope > .turnGrid');if(grid)grid.style.display='none'}panel.classList.add('onlineSetupSide')}
 else{if(map&&panel.parentNode!==map)map.insertBefore(panel,$('divinationPanel'));panel.classList.remove('onlineSetupSide');if(right){const title=right.querySelector(':scope > b');if(title)title.style.display='';const grid=right.querySelector(':scope > .turnGrid');if(grid)grid.style.display=''}}
}
function renderOnlineAuthoritativeSetup(state){
 onlineApplyStateToDisplay(state);setupState=null;$('start').classList.add('hidden');$('game').classList.remove('hidden');onlineSetupLayout(true);
 const panel=$('setupPanel');panel.classList.remove('hidden');const me=state.players[state.youIndex],active=state.setup&&state.setup.activePlayer===state.youIndex;$('setupTitle').textContent='Installation — '+(me?me.pseudo:'TRIBU');const box=$('setupChoices');box.innerHTML='';
 if(!active){const current=state.players[state.setup.activePlayer];$('setupText').innerHTML='Votre province : <b>'+(me&&me.province||'—')+'</b><br>En attente de <b>'+(current?current.pseudo:'un autre joueur')+'</b>.'}
 else{
  $('setupText').innerHTML='Province <b>'+me.province+'</b><br>Choisissez votre couleur et votre faction, puis cliquez sur <b>2 régions</b> de votre province directement sur la carte.<br>Placement : <b>'+onlineSetupSelectedRegions.length+'/2</b>';
  BASE_COLORS.forEach((color,i)=>{if(state.setup.usedColors.includes(color))return;const b=document.createElement('button');b.className='setupColorBtn'+(onlineSetupDraft.color===color?' selected':'');b.textContent=COLOR_NAMES[i];b.style.borderColor=color;b.style.color=color;b.onclick=()=>{onlineSetupDraft.color=color;renderOnlineAuthoritativeSetup(state)};box.appendChild(b)});const br=document.createElement('div');br.style.flexBasis='100%';box.appendChild(br);
  Object.entries(FACTION_PORTRAIT_META).forEach(([key,meta])=>{if(state.setup.usedPortraits.includes(key))return;const b=document.createElement('button');b.className='setupFactionPortrait'+(onlineSetupDraft.portrait===key?' selected':'');b.innerHTML='<img src="'+FACTION_PORTRAITS[key]+'" alt="'+meta.label+'"><span>'+meta.label+'</span>';b.onclick=()=>{onlineSetupDraft.portrait=key;renderOnlineAuthoritativeSetup(state)};box.appendChild(b)});const br2=document.createElement('div');br2.style.flexBasis='100%';box.appendChild(br2);
  const ok=document.createElement('button');ok.textContent='Valider mon installation';ok.disabled=!(onlineSetupDraft.color&&onlineSetupDraft.portrait&&onlineSetupSelectedRegions.length===2);ok.onclick=()=>onlineAck('setupComplete',{color:onlineSetupDraft.color,portrait:onlineSetupDraft.portrait,regions:onlineSetupSelectedRegions.slice()}).then(()=>{onlineSetupSelectedRegions=[];onlineSetupDraft={color:null,portrait:null}}).catch(onlineError);box.appendChild(ok);
  const restart=document.createElement('button');restart.textContent='Recommencer le placement';restart.disabled=onlineSetupSelectedRegions.length===0;restart.onclick=()=>{onlineSetupSelectedRegions=[];renderOnlineAuthoritativeSetup(state)};box.appendChild(restart)
 }
 const boardMapImage=$('boardMapImage');if(boardMapImage)boardMapImage.src='assets/images/maps/map_normal.png';renderMap();renderPlayerRail()
}
'''
s=s[:start]+replacement+s[end:]
old="const state=onlineGameState;if(!state||state.status!=='setup'||!state.setup||state.setup.activePlayer!==state.youIndex||state.setup.stage!=='regions')return;"
new="const state=onlineGameState;if(!state||state.status!=='setup'||!state.setup||state.setup.activePlayer!==state.youIndex)return;"
assert old in s; s=s.replace(old,new,1)
old="onlineApplyStateToDisplay(state);setupState=null;$('setupPanel').classList.add('hidden');$('start').classList.add('hidden');$('game').classList.remove('hidden');render();onlineLockControls();"
new="onlineApplyStateToDisplay(state);setupState=null;onlineSetupLayout(false);$('setupPanel').classList.add('hidden');$('start').classList.add('hidden');$('game').classList.remove('hidden');render();onlineLockControls();"
assert old in s; s=s.replace(old,new,1)
css="""\n/* Installation Online en colonne de droite */\n.setupPanel.onlineSetupSide{position:static;left:auto;top:auto;transform:none;width:auto;box-sizing:border-box;margin:0 0 10px;background:#111e;box-shadow:none;z-index:auto}\n.setupPanel.onlineSetupSide .setupChoices{max-height:62vh;overflow-y:auto;align-content:flex-start}\n.setupPanel.onlineSetupSide .setupFactionPortrait{min-width:92px}\n@media(max-width:760px){.setupPanel.onlineSetupSide .setupChoices{max-height:none}.setupPanel.onlineSetupSide{margin-bottom:8px}}\n"""
s=s.replace('</style>',css+'</style>',1); p.write_text(s)
