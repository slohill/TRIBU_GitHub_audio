from pathlib import Path

path = Path('index.html')
text = path.read_text(encoding='utf-8')

old_listener = """  socket.on('roomState',renderOnlineLobby);\n  socket.on('gameLaunched',room=>{onlineRoom=room;$('onlineLaunch').disabled=true;$('onlineReady').disabled=true;launchOnlineRoom(room)});"""
new_listener = """  socket.on('roomState',renderOnlineLobby);\n  socket.on('gameLaunched',room=>{\n    onlineRoom=room;$('onlineLaunch').disabled=true;$('onlineReady').disabled=true;\n    socket.emit('requestGameState',{},res=>{if(res&&res.ok&&res.game)onlineApplyServerGame(res.game)});\n  });\n  socket.on('gameState',onlineApplyServerGame);"""
if old_listener in text:
    text = text.replace(old_listener, new_listener, 1)
elif new_listener not in text:
    raise SystemExit('Online socket listener block not found')

marker = "function connectOnline(){"
block = r"""
let onlineServerGame=null,onlineSetupDraft={color:null,portrait:null,regions:[]};
function onlineAuthorityMode(mode){return mode==='2v3-online'?'2v3':mode}
function onlineAuthorityInit(game){
 if(G&&G.onlineAuthority)return;
 $('gameMode').value=onlineAuthorityMode(game.mode);$('victoryMode').value=String(game.victoryPoints||3);
 $('start').classList.add('hidden');$('game').classList.remove('hidden');
 init();
 clearTimeout(botTimer);clearTimeout(botReactionTimer);botToken++;
 setupState=null;hotseatViewerOverride=null;
 const sp=$('setupPanel');if(sp)sp.classList.add('hidden');
 G.onlineAuthority=true;
}
function onlineAuthorityPlayerShell(serverPlayer,index){
 const previous=G.players[index]||{};
 const mine=onlineServerGame&&onlineServerGame.permissions&&onlineServerGame.permissions.seat===index;
 const hand=mine&&Array.isArray(serverPlayer.hand)?serverPlayer.hand.slice():Array(serverPlayer.handCount||0).fill(0);
 return {...previous,name:serverPlayer.pseudo,bot:!!serverPlayer.bot,faction:Number.isInteger(serverPlayer.faction)?serverPlayer.faction:0,gold:serverPlayer.gold||0,hand,inPlay:previous.inPlay||[],pvPermanent:previous.pvPermanent||0,attackTurnBonus:0,defenseTurnBonus:0};
}
function onlineApplyServerBoard(game){
 Object.entries(game.board||{}).forEach(([r,state])=>{
   if(!G.b[r])return;
   G.b[r].owner=state.owner;G.b[r].units=state.units||0;G.b[r].hostile=!!state.hostile;
 });
}
function onlineApplyServerGame(game){
 if(!game||!game.players)return;
 onlineServerGame=game;onlineAuthorityInit(game);
 G.players=game.players.map(onlineAuthorityPlayerShell);
 game.players.forEach((sp,i)=>{if(sp.color)COLORS[i]=sp.color});
 onlineApplyServerBoard(game);
 G.dragon=game.dragon||G.dragon;G.active=Number.isInteger(game.activeSeat)?game.activeSeat:0;G.phase=game.phase;
 G.online={code:game.code,myPlayerIndex:game.permissions&&game.permissions.seat,authoritative:true};
 clearTimeout(botTimer);clearTimeout(botReactionTimer);botToken++;
 render();onlineApplyPermissions();onlineRenderServerSetup();
}
function onlineApplyPermissions(){
 if(!onlineServerGame||!G||!G.online||!G.online.authoritative)return;
 const p=onlineServerGame.permissions||{};
 const start=$('startTurn');if(start)start.classList.toggle('hidden',!(p.canDraw||p.canHarvest||p.canRecruit));
 const drawBtn=$('draw');if(drawBtn){drawBtn.disabled=!p.canDraw;drawBtn.style.display=p.canDraw?'':'none';drawBtn.onclick=()=>onlineGameAction('DRAW')}
 const harvestBtn=$('harvest');if(harvestBtn){harvestBtn.disabled=true;harvestBtn.style.display='none'}
 const recruitBtn=$('recruit');if(recruitBtn){recruitBtn.disabled=true;recruitBtn.style.display='none'}
 const oracleBtn=$('toOracle');if(oracleBtn)oracleBtn.disabled=true;
 const rollBtn=$('roll');if(rollBtn)rollBtn.disabled=true;
}
function onlineGameAction(type,payload={}){
 if(!onlineSocket)return;
 onlineSocket.emit('gameAction',{type,...payload},res=>{if(!res||!res.ok)onlineError(new Error(res&&res.error||'Action refusée par le serveur.'))});
}
function onlineSetupResetDraft(){onlineSetupDraft={color:null,portrait:null,regions:[]}}
function onlineSetupSubmit(){
 if(!onlineServerGame||!onlineServerGame.permissions.canSetup||!onlineSocket)return;
 if(!onlineSetupDraft.color||!onlineSetupDraft.portrait||onlineSetupDraft.regions.length!==2)return;
 onlineSocket.emit('setupChoice',{color:onlineSetupDraft.color,portrait:onlineSetupDraft.portrait,regions:onlineSetupDraft.regions.slice()},res=>{
   if(!res||!res.ok)return onlineError(new Error(res&&res.error||'Choix refusé par le serveur.'));
   onlineSetupResetDraft();
 });
}
function onlineRenderServerSetup(){
 const panel=$('setupPanel');if(!panel||!onlineServerGame)return;
 if(onlineServerGame.phase!=='setup'){panel.classList.add('hidden');return}
 panel.classList.remove('hidden');
 const game=onlineServerGame,p=game.permissions||{},me=game.players[p.seat],active=game.players[game.setup&&game.setup.activeSeat];
 $('setupTitle').textContent=p.canSetup?'Installation — '+me.pseudo:'Installation Online';
 const box=$('setupChoices');box.innerHTML='';
 if(!p.canSetup){
   $('setupText').innerHTML='En attente de <b>'+(active?active.pseudo:'la fin de l’installation')+'</b>. Les choix sont validés par le serveur.';
   return;
 }
 $('setupText').innerHTML='Province attribuée au hasard : <b>'+me.province+'</b><br>Choisissez votre couleur, votre encart de faction puis exactement <b>2 régions</b> de cette province.';
 const usedColors=new Set((game.setup&&game.setup.usedColors)||[]),usedPortraits=new Set((game.setup&&game.setup.usedPortraits)||[]);
 BASE_COLORS.forEach((color,i)=>{
   if(usedColors.has(color))return;
   const b=document.createElement('button');b.className='setupColorBtn';b.textContent=COLOR_NAMES[i]||color;b.style.borderColor=color;b.style.color=color;
   b.classList.toggle('selected',onlineSetupDraft.color===color);
   b.onclick=()=>{onlineSetupDraft.color=color;onlineRenderServerSetup()};box.appendChild(b);
 });
 const br=document.createElement('div');br.style.flexBasis='100%';box.appendChild(br);
 Object.entries(FACTION_PORTRAIT_META).forEach(([key,meta])=>{
   if(usedPortraits.has(key))return;
   const b=document.createElement('button');b.className='setupFactionPortrait';
   b.innerHTML='<img src="'+FACTION_PORTRAITS[key]+'" alt="'+meta.label+'"><span>'+meta.label+'</span>';
   b.classList.toggle('selected',onlineSetupDraft.portrait===key);
   b.onclick=()=>{onlineSetupDraft.portrait=key;onlineRenderServerSetup()};box.appendChild(b);
 });
 const br2=document.createElement('div');br2.style.flexBasis='100%';box.appendChild(br2);
 setupProvinceRegions(me.province).forEach(r=>{
   const b=document.createElement('button');b.textContent=r;b.className='setupFactionBtn';b.classList.toggle('selected',onlineSetupDraft.regions.includes(r));
   b.onclick=()=>{const at=onlineSetupDraft.regions.indexOf(r);if(at>=0)onlineSetupDraft.regions.splice(at,1);else if(onlineSetupDraft.regions.length<2)onlineSetupDraft.regions.push(r);onlineRenderServerSetup()};box.appendChild(b);
 });
 const br3=document.createElement('div');br3.style.flexBasis='100%';box.appendChild(br3);
 const ok=document.createElement('button');ok.textContent='Valider mes choix';ok.disabled=!onlineSetupDraft.color||!onlineSetupDraft.portrait||onlineSetupDraft.regions.length!==2;ok.onclick=onlineSetupSubmit;box.appendChild(ok);
}
"""
if block.strip() not in text:
    if marker not in text:
        raise SystemExit('connectOnline marker not found')
    text = text.replace(marker, block + '\n' + marker, 1)

path.write_text(text, encoding='utf-8')
