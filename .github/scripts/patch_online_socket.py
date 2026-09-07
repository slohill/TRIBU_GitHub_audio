from pathlib import Path
p=Path('index.html')
s=p.read_text(encoding='utf-8')
# Logo officiel déjà ajouté au dépôt sous assets/tribu-title.png.
old='<div class="onlineBrand"><h1>Tribu Le Jeu Online</h1><span class="onlineBeta">version bêta</span></div>'
new='<div class="onlineBrand"><img class="onlineTitleLogo" src="assets/tribu-title.png" alt="Tribu — Conquest of Myrmigate"><div class="onlineTitleOnline">ONLINE</div><span class="onlineBeta">version bêta</span></div>'
if old not in s: raise SystemExit('online brand not found')
s=s.replace(old,new,1)
css='.onlineBrand{text-align:center;margin-bottom:18px}'
if css not in s: raise SystemExit('brand css not found')
s=s.replace(css,css+'.onlineTitleLogo{display:block;width:min(430px,88%);max-height:260px;object-fit:contain;margin:0 auto -8px}.onlineTitleOnline{font-size:clamp(20px,4vw,30px);font-weight:1000;letter-spacing:.24em;color:#f1d77c;text-shadow:0 2px 8px #000;margin-left:.24em}',1)
# Online bot modes reuse the existing local engine shapes, but are entered simultaneously on gameLaunched.
old="function launchLegacyMode(mode,victory=3){$('gameMode').value=mode;$('victoryMode').value=String(victory);$('start').classList.add('hidden');$('game').classList.remove('hidden');init()}"
new="function launchLegacyMode(mode,victory=3){$('gameMode').value=mode;$('victoryMode').value=String(victory);$('start').classList.add('hidden');$('game').classList.remove('hidden');init()}\nfunction onlineEngineMode(room){return room.mode==='2v3-online'?'2v3':room.mode==='3v2-online'?'5h':room.mode}\nfunction launchOnlineRoom(room){onlineRoom=room;launchLegacyMode(onlineEngineMode(room),room.victoryPoints);if(!G)return;G.online={code:room.code,mode:room.mode,hostId:room.hostId,mySocketId:onlineSocket&&onlineSocket.id,players:room.players.map(x=>({id:x.id,pseudo:x.pseudo}))};room.players.forEach((rp,i)=>{if(G.players[i])G.players[i].name=rp.pseudo});if(room.mode==='3v2-online')G.players.forEach((pl,i)=>pl.bot=i>=3);const pcb=$('playerCountBadge');if(pcb)pcb.textContent=onlineModeLabel(room.mode)+' — Online — victoire à '+room.victoryPoints+' PV';render()}"
if old not in s: raise SystemExit('launchLegacyMode not found')
s=s.replace(old,new,1)
old="socket.on('gameLaunched',room=>{onlineRoom=room;onlineNotice('Partie lancée. Synchronisation du moteur de jeu à venir à l’étape suivante.');$('onlineLaunch').disabled=true;$('onlineReady').disabled=true});"
new="socket.on('gameLaunched',room=>{onlineRoom=room;launchOnlineRoom(room)});"
if old not in s: raise SystemExit('gameLaunched handler not found')
s=s.replace(old,new,1)
p.write_text(s,encoding='utf-8')
