from pathlib import Path
p=Path('index.html')
s=p.read_text(encoding='utf-8')
old="""const ONLINE_RANDOM_NAMES=['Aube-Rousse','Corne-de-Brume','Loup-Serein','Éclat-de-Silex','Rivière-Noire','Chêne-Ardent','Renard-d’Or','Lune-Fauve','Vent-du-Nord','Pierre-Claire'];
let onlineSelectedMode=null,onlineReadyState=false;
function onlinePseudo(){const input=$('onlinePseudo');let v=(input&&input.value||'').trim();if(!v){v=ONLINE_RANDOM_NAMES[Math.floor(Math.random()*ONLINE_RANDOM_NAMES.length)];if(input)input.value=v}return v}
function showOnlineScreen(id){document.querySelectorAll('.onlineScreen').forEach(x=>x.classList.add('hidden'));$(id).classList.remove('hidden')}
function launchLegacyMode(mode,victory=3){$('gameMode').value=mode;$('victoryMode').value=String(victory);$('start').classList.add('hidden');$('game').classList.remove('hidden');init()}
function onlineModeLabel(mode){return ({'2v3-online':'2 joueurs vs 3 bots','3v2-online':'3 joueurs vs 2 bots','3h':'3 joueurs','4h':'4 joueurs','5h':'5 joueurs'})[mode]||mode}
function onlineSeatCount(mode){return mode==='2v3-online'?2:mode==='3v2-online'?3:mode==='3h'?3:mode==='4h'?4:5}
function renderPrototypeLobby(){
 const seats=onlineSeatCount(onlineSelectedMode),name=onlinePseudo();
 $('lobbyName').textContent=($('onlineRoomName').value||'Partie TRIBU').trim();$('lobbyCode').textContent=($('onlineRoomCode').value||'TRIBU').trim().toUpperCase();$('lobbyMode').textContent=onlineModeLabel(onlineSelectedMode)+' — victoire à '+$('onlineVictory').value+' points';
 let h='<div class=\"onlinePlayerRow\"><span>'+name+' <small>(créateur)</small></span><span class=\"'+(onlineReadyState?'readyBadge':'waitingBadge')+'\">'+(onlineReadyState?'Prêt·e':'Pas prêt·e')+'</span></div>';
 for(let i=1;i<seats;i++)h+='<div class=\"onlinePlayerRow\"><span>Place '+(i+1)+'</span><span class=\"waitingBadge\">En attente</span></div>';
 $('lobbyPlayers').innerHTML=h;$('onlineLaunch').disabled=true;$('lobbyNotice').textContent='En attente des joueurs et des joueuses… Le lancement sera disponible quand toutes les places seront occupées et que tout le monde sera prêt.';
}
$('startBtn').onclick=()=>launchLegacyMode($('gameMode').value,+$('victoryMode').value||3);
$('onlineCreate').onclick=()=>{onlinePseudo();showOnlineScreen('onlineCreateScreen')};
$('onlineJoin').onclick=()=>{onlinePseudo();showOnlineScreen('onlineJoinScreen')};
$('localTestBtn').onclick=()=>{onlinePseudo();launchLegacyMode('2v3',3)};
document.querySelectorAll('[data-online-mode]').forEach(b=>b.onclick=()=>{onlineSelectedMode=b.dataset.onlineMode;if(onlineSelectedMode==='1v4'){launchLegacyMode('1v4',3);return}showOnlineScreen('onlineConfigScreen')});
document.querySelectorAll('[data-online-back]').forEach(b=>b.onclick=()=>showOnlineScreen('onlineHome'));
$('onlineCreateRoom').onclick=()=>{onlinePseudo();if(!$('onlineRoomCode').value.trim())$('onlineRoomCode').value='TRB-'+Math.floor(1000+Math.random()*9000);onlineReadyState=false;renderPrototypeLobby();showOnlineScreen('onlineLobbyScreen')};
$('onlineReady').onclick=()=>{onlineReadyState=!onlineReadyState;$('onlineReady').textContent=onlineReadyState?'Annuler prêt·e':'Prêt·e';renderPrototypeLobby()};
$('onlineJoinRoom').onclick=()=>{const code=$('onlineJoinCode').value.trim();if(!code){$('onlineJoinCode').focus();return}onlineSelectedMode='3h';$('onlineRoomName').value='Partie rejointe';$('onlineRoomCode').value=code;onlineReadyState=false;renderPrototypeLobby();showOnlineScreen('onlineLobbyScreen')};
$('onlineLaunch').onclick=()=>{};
"""
new="""const ONLINE_RANDOM_NAMES=['Aube-Rousse','Corne-de-Brume','Loup-Serein','Éclat-de-Silex','Rivière-Noire','Chêne-Ardent','Renard-d’Or','Lune-Fauve','Vent-du-Nord','Pierre-Claire'];
const ONLINE_SERVER='https://tribu-online.onrender.com';
let onlineSelectedMode=null,onlineReadyState=false,onlineSocket=null,onlineRoom=null;
function onlinePseudo(){const input=$('onlinePseudo');let v=(input&&input.value||'').trim();if(!v){v=ONLINE_RANDOM_NAMES[Math.floor(Math.random()*ONLINE_RANDOM_NAMES.length)];if(input)input.value=v}return v}
function showOnlineScreen(id){document.querySelectorAll('.onlineScreen').forEach(x=>x.classList.add('hidden'));$(id).classList.remove('hidden')}
function launchLegacyMode(mode,victory=3){$('gameMode').value=mode;$('victoryMode').value=String(victory);$('start').classList.add('hidden');$('game').classList.remove('hidden');init()}
function onlineModeLabel(mode){return ({'2v3-online':'2 joueurs vs 3 bots','3v2-online':'3 joueurs vs 2 bots','3h':'3 joueurs','4h':'4 joueurs','5h':'5 joueurs'})[mode]||mode}
function onlineSeatCount(mode){return mode==='2v3-online'?2:mode==='3v2-online'?3:mode==='3h'?3:mode==='4h'?4:5}
function onlineBotCount(mode){return mode==='2v3-online'?3:mode==='3v2-online'?2:0}
function onlineEscape(v){return String(v??'').replace(/[&<>\"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','\"':'&quot;',\"'\":'&#39;'}[c]))}
function onlineNotice(msg){$('lobbyNotice').textContent=msg}
function renderOnlineLobby(room){
 onlineRoom=room;onlineSelectedMode=room.mode;
 $('lobbyName').textContent=room.name;$('lobbyCode').textContent=room.code;$('lobbyMode').textContent=onlineModeLabel(room.mode)+' — victoire à '+room.victoryPoints+' points';
 let h='';room.players.forEach(pl=>{h+='<div class=\"onlinePlayerRow\"><span>'+onlineEscape(pl.pseudo)+(pl.host?' <small>(créateur)</small>':'')+'</span><span class=\"'+(pl.ready?'readyBadge':'waitingBadge')+'\">'+(pl.ready?'Prêt·e':'Pas prêt·e')+'</span></div>'});
 for(let i=room.players.length;i<room.maxHumans;i++)h+='<div class=\"onlinePlayerRow\"><span>Place '+(i+1)+'</span><span class=\"waitingBadge\">En attente</span></div>';
 $('lobbyPlayers').innerHTML=h;
 const me=room.players.find(pl=>onlineSocket&&pl.id===onlineSocket.id);onlineReadyState=!!(me&&me.ready);$('onlineReady').textContent=onlineReadyState?'Annuler prêt·e':'Prêt·e';
 const allHere=room.players.length===room.maxHumans,allReady=allHere&&room.players.every(pl=>pl.ready),host=onlineSocket&&room.hostId===onlineSocket.id;
 $('onlineLaunch').disabled=!(host&&allReady);onlineNotice(allReady?(host?'Tout le monde est prêt. Vous pouvez lancer la partie.':'Tout le monde est prêt. En attente du lancement par le créateur.'):'En attente des joueurs et des joueuses…');
 showOnlineScreen('onlineLobbyScreen');
}
function connectOnline(){
 if(onlineSocket)return Promise.resolve(onlineSocket);
 return new Promise((resolve,reject)=>{
  if(typeof io!=='function')return reject(new Error('Socket.IO indisponible.'));
  const socket=io(ONLINE_SERVER,{transports:['websocket','polling']});onlineSocket=socket;
  const fail=err=>reject(err instanceof Error?err:new Error('Connexion au serveur impossible.'));
  socket.once('connect',()=>resolve(socket));socket.once('connect_error',fail);
  socket.on('roomState',renderOnlineLobby);
  socket.on('gameLaunched',room=>{onlineRoom=room;onlineNotice('Partie lancée. Synchronisation du moteur de jeu à venir à l’étape suivante.');$('onlineLaunch').disabled=true;$('onlineReady').disabled=true});
 });
}
function onlineAck(action,payload){return connectOnline().then(socket=>new Promise((resolve,reject)=>socket.emit(action,payload,res=>res&&res.ok?resolve(res):reject(new Error(res&&res.error||'Erreur serveur.')))))}
function onlineError(err){alert(err&&err.message?err.message:String(err))}
$('startBtn').onclick=()=>launchLegacyMode($('gameMode').value,+$('victoryMode').value||3);
$('onlineCreate').onclick=()=>{onlinePseudo();showOnlineScreen('onlineCreateScreen')};
$('onlineJoin').onclick=()=>{onlinePseudo();showOnlineScreen('onlineJoinScreen')};
$('localTestBtn').onclick=()=>{onlinePseudo();launchLegacyMode('2v3',3)};
document.querySelectorAll('[data-online-mode]').forEach(b=>b.onclick=()=>{onlineSelectedMode=b.dataset.onlineMode;if(onlineSelectedMode==='1v4'){launchLegacyMode('1v4',3);return}showOnlineScreen('onlineConfigScreen')});
document.querySelectorAll('[data-online-back]').forEach(b=>b.onclick=()=>{if(onlineSocket&&onlineRoom)onlineSocket.emit('leaveRoom');onlineRoom=null;showOnlineScreen('onlineHome')});
$('onlineCreateRoom').onclick=async()=>{try{onlinePseudo();if(!$('onlineRoomCode').value.trim())$('onlineRoomCode').value='TRB-'+Math.floor(1000+Math.random()*9000);const res=await onlineAck('createRoom',{pseudo:onlinePseudo(),name:$('onlineRoomName').value,code:$('onlineRoomCode').value,mode:onlineSelectedMode,maxHumans:onlineSeatCount(onlineSelectedMode),bots:onlineBotCount(onlineSelectedMode),victoryPoints:+$('onlineVictory').value});renderOnlineLobby(res.room)}catch(e){onlineError(e)}};
$('onlineReady').onclick=async()=>{try{await onlineAck('setReady',!onlineReadyState)}catch(e){onlineError(e)}};
$('onlineJoinRoom').onclick=async()=>{try{const code=$('onlineJoinCode').value.trim();if(!code){$('onlineJoinCode').focus();return}const res=await onlineAck('joinRoom',{code,pseudo:onlinePseudo()});renderOnlineLobby(res.room)}catch(e){onlineError(e)}};
$('onlineLaunch').onclick=async()=>{try{await onlineAck('launchGame',{})}catch(e){onlineError(e)}};
"""
if old not in s: raise SystemExit('online prototype block not found')
s=s.replace(old,new,1)
# Load Socket.IO client from the deployed server, before the inline game script runs.
needle='</body></html>'
# The main inline script is already running before body close, so inject client before that script instead.
marker='<script>\n'
pos=s.rfind(marker)
if pos<0: raise SystemExit('main script marker not found')
s=s[:pos]+'<script src="https://tribu-online.onrender.com/socket.io/socket.io.js"></script>\n'+s[pos:]
p.write_text(s,encoding='utf-8')
