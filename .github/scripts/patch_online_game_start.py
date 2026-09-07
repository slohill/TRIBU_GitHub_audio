from pathlib import Path

# --- Client ---
p=Path('index.html')
s=p.read_text(encoding='utf-8')

css='''\n/* Début de partie Online */\n.onlineGameWelcome{position:absolute;inset:0;z-index:180;display:flex;align-items:center;justify-content:center;padding:24px;background:#0007;pointer-events:none}\n.onlineGameWelcomeCard{max-width:640px;background:#111e;border:2px solid #d9c776;border-radius:14px;padding:24px 30px;text-align:center;font-size:25px;font-weight:900;line-height:1.3;box-shadow:0 10px 34px #000c}\n@media(max-width:760px){.onlineGameWelcomeCard{font-size:20px;padding:20px}}\n'''
assert '</style>' in s
s=s.replace('</style>',css+'\n</style>',1)

old="""function audioStartAmbient(index=0,time=0,fade=true){\n audioAmbientIndex=index%2;audioMode='ambient';\n const name=audioAmbientIndex===0?'ambient1':'ambient2',a=audioTrack(name),other=audioTrack(audioAmbientIndex===0?'ambient2':'ambient1');\n other.pause();\n a.onended=()=>{if(audioMode!=='ambient')return;audioAmbientIndex=1-audioAmbientIndex;audioStartAmbient(audioAmbientIndex,0,false)};\n if(!audioMusicEnabled)return;\n a.volume=fade?0:.36;audioSafePlay(a,time);if(fade)audioFadeTo(a,.36,900);\n}"""
new="""function audioStartAmbient(index=0,time=0,fade=true){\n audioAmbientIndex=index%2;audioMode='ambient';\n const name=audioAmbientIndex===0?'ambient1':'ambient2',a=audioTrack(name),other=audioTrack(audioAmbientIndex===0?'ambient2':'ambient1');\n other.pause();other.ontimeupdate=null;\n a._tribuFading=false;\n a.ontimeupdate=()=>{if(audioMode!=='ambient'||a._tribuFading||!Number.isFinite(a.duration))return;if(a.duration-a.currentTime<=1.15){a._tribuFading=true;audioFadeTo(a,0,950)}};\n a.onended=()=>{if(audioMode!=='ambient')return;a._tribuFading=false;audioAmbientIndex=1-audioAmbientIndex;audioStartAmbient(audioAmbientIndex,0,true)};\n if(!audioMusicEnabled)return;\n a.volume=fade?0:.36;audioSafePlay(a,time);if(fade)audioFadeTo(a,.36,900);\n}"""
assert old in s
s=s.replace(old,new,1)

old="function beginPlay(){if(paidDrawState)return;recruitSnapshot=null;G.phase='play';setMovable();render()}\nfunction doDraw(){if(G&&G.online)return onlineGameAction('DRAW_START');if(paidDrawState)return;draw(G.active,2);log(p().name+' pioche 2 cartes.');beginPlay()}\nfunction doHarvest(){if(paidDrawState||goldReaction)return;"
new="function beginPlay(){if(G&&G.online){if(onlineGameState&&onlineGameState.phase==='recruit')return onlineGameAction('END_RECRUIT');return}if(paidDrawState)return;recruitSnapshot=null;G.phase='play';setMovable();render()}\nfunction doDraw(){if(G&&G.online)return onlineGameAction('DRAW_START');if(paidDrawState)return;draw(G.active,2);log(p().name+' pioche 2 cartes.');beginPlay()}\nfunction doHarvest(){if(G&&G.online)return onlineGameAction('HARVEST_START');if(paidDrawState||goldReaction)return;"
assert old in s
s=s.replace(old,new,1)

old="function doRecruit(){\n if(paidDrawState)return;"
new="function doRecruit(){\n if(G&&G.online)return onlineGameAction('RECRUIT_START');\n if(paidDrawState)return;"
assert old in s
s=s.replace(old,new,1)

old="function resetRecruitment(){\n if(!recruitSnapshot||recruitSnapshot.player!==G.active||G.phase!=='recruit')return;"
new="function resetRecruitment(){\n if(G&&G.online)return onlineGameAction('RESET_RECRUIT');\n if(!recruitSnapshot||recruitSnapshot.player!==G.active||G.phase!=='recruit')return;"
assert old in s
s=s.replace(old,new,1)

old="function recruitAt(r){\n const c=G.b[r];if(c.owner!==G.active)return;"
new="function recruitAt(r){\n if(G&&G.online)return onlineGameAction('RECRUIT_AT',{region:r});\n const c=G.b[r];if(c.owner!==G.active)return;"
assert old in s
s=s.replace(old,new,1)

old="function clickSpot(id){\n if(G&&G.online&&onlineGameState){if(onlineGameState.status==='setup')onlineSetupRegionClick(id);return}"
new="function clickSpot(id){\n if(G&&G.online&&onlineGameState){if(onlineGameState.status==='setup')onlineSetupRegionClick(id);else if(onlineGameState.status==='playing'&&onlineGameState.phase==='recruit'&&onlineGameState.active===onlineGameState.youIndex)recruitAt(id);return}"
assert old in s
s=s.replace(old,new,1)

marker="function onlineSeatCount(mode){"
assert marker in s
intro="""let onlineWelcomeShownKey=null,onlineWelcomeActive=false,onlineWelcomeTimer=null;\nfunction onlineShowGameWelcome(state){\n const key=String(state.seed||'game');if(onlineWelcomeShownKey===key)return;onlineWelcomeShownKey=key;onlineWelcomeActive=true;\n clearTimeout(onlineWelcomeTimer);const map=$('map');if(map){const old=map.querySelector('.onlineGameWelcome');if(old)old.remove();const ov=document.createElement('div');ov.className='onlineGameWelcome';ov.innerHTML='<div class=\"onlineGameWelcomeCard\">Bienvenu·e·s dans Myrmigate : la partie peut commencer</div>';map.appendChild(ov);onlineWelcomeTimer=setTimeout(()=>{ov.remove();onlineWelcomeActive=false;onlineLockControls()},3000)}else{onlineWelcomeTimer=setTimeout(()=>{onlineWelcomeActive=false;onlineLockControls()},3000)}\n audioEnterGame();\n}\n"""
s=s.replace(marker,intro+marker,1)

old="""function onlineLockControls(){\n if(!G||!G.online||!onlineGameState)return;\n const mine=onlineGameState.active===onlineGameState.youIndex&&onlineGameState.status==='playing';\n $('startTurn').classList.toggle('hidden',!mine||onlineGameState.phase!=='start');\n $('draw').disabled=!(mine&&onlineGameState.phase==='start');\n ['harvest','recruit','endRecruit','toOracle','roll'].forEach(id=>{const el=$(id);if(el)el.disabled=true});\n const h=$('hand');if(h)h.querySelectorAll('.card').forEach(c=>{c.onclick=null;c.classList.remove('playablePermanent','battlePlayable');c.classList.add('battleBlocked')});\n const n=$('status');if(n)n.innerHTML+='<div class=\"botNotice\">🌐 Online autoritaire — seules les actions déjà migrées vers le serveur sont activées.</div>';\n}"""
new="""function onlineLockControls(){\n if(!G||!G.online||!onlineGameState)return;\n const mine=onlineGameState.active===onlineGameState.youIndex&&onlineGameState.status==='playing'&&!onlineWelcomeActive,start=mine&&onlineGameState.phase==='start',recruiting=mine&&onlineGameState.phase==='recruit';\n $('startTurn').classList.toggle('hidden',!start);\n $('draw').disabled=!start;$('harvest').disabled=!start;$('recruit').disabled=!start;\n $('endRecruit').disabled=!recruiting;const rr=$('resetRecruit');if(rr)rr.disabled=!recruiting;\n ['toOracle','roll'].forEach(id=>{const el=$(id);if(el)el.disabled=true});\n const h=$('hand');if(h)h.querySelectorAll('.card').forEach(c=>{c.onclick=null;c.classList.remove('playablePermanent','battlePlayable');c.classList.add('battleBlocked')});\n const n=$('status');if(n)n.innerHTML+='<div class=\"botNotice\">🌐 Online autoritaire — début de tour synchronisé par le serveur.</div>';\n}"""
assert old in s
s=s.replace(old,new,1)

old="""function applyOnlineGameState(state){\n onlineGameState=state;\n if(state.status==='setup'){renderOnlineAuthoritativeSetup(state);return}\n onlineApplyStateToDisplay(state);setupState=null;onlineSetupLayout(false);$('setupPanel').classList.add('hidden');$('start').classList.add('hidden');$('game').classList.remove('hidden');render();onlineLockControls();\n}"""
new="""function applyOnlineGameState(state){\n const wasSetup=onlineGameState&&onlineGameState.status==='setup';onlineGameState=state;\n if(state.status==='setup'){renderOnlineAuthoritativeSetup(state);return}\n onlineApplyStateToDisplay(state);setupState=null;onlineSetupLayout(false);$('setupPanel').classList.add('hidden');$('start').classList.add('hidden');$('game').classList.remove('hidden');render();\n if(state.status==='playing'&&(wasSetup||onlineWelcomeShownKey!==String(state.seed||'game')))onlineShowGameWelcome(state);\n onlineLockControls();\n}"""
assert old in s
s=s.replace(old,new,1)

p.write_text(s,encoding='utf-8')

# --- Server ---
p=Path('server/server.js')
s=p.read_text(encoding='utf-8')

old="const ORACLE_IDS = [0,1,2,2,3,3,4,5];"
new="""const ORACLE_IDS = [0,1,2,2,3,3,4,5];\nconst FACTION_CAP = [3,3,2];\nconst TERRAIN = {};\n['A1','A2','A3','A4','A5','B1','B2','C1','C2','C3'].forEach(r=>TERRAIN[r]='e');\n['B3','B4','B5','C4','C5','D1','D2','D3','D4','D5','E1','E2','E3','E4','E5','F1','F2','F3','F4','F5','G1','H1','H2','H3','H4'].forEach(r=>TERRAIN[r]='t');\n['G2','G3','G4','G5','H5','I1','I2','I3','I4','I5'].forEach(r=>TERRAIN[r]='d');"
assert old in s
s=s.replace(old,new,1)

old="""function drawCards(game, playerIndex, count) {\n  const hand = game.players[playerIndex].hand;\n  for (let i = 0; i < count && game.deck.length; i++) hand.push(game.deck.pop());\n}"""
new=old+"""\nfunction ownedRegionCount(game, playerIndex) {\n  return Object.values(game.board).filter(c => c.owner === playerIndex && c.units > 0).length;\n}\nfunction totalUnitsFor(game, playerIndex) {\n  return Object.values(game.board).reduce((n,c)=>n+(c.owner===playerIndex?c.units:0),0);\n}\nfunction unitCapFor(game, playerIndex) {\n  const faction=game.players[playerIndex].faction;\n  return ownedRegionCount(game,playerIndex)*(FACTION_CAP[faction]||2);\n}"""
s=s.replace(old,new,1)

old="""    if (type === 'DRAW_START') {\n      if (game.phase !== 'start') return rejectGameAction(ack, 'Vous ne pouvez pas piocher maintenant.');\n      drawCards(game, index, 2);\n      game.phase = 'play';\n      game.revision++;\n      ack({ ok: true });\n      emitGame(room);\n      return;\n    }\n    return rejectGameAction(ack, 'Action Online pas encore migrée vers le serveur.');"""
new="""    if (type === 'DRAW_START') {\n      if (game.phase !== 'start') return rejectGameAction(ack, 'Vous ne pouvez pas piocher maintenant.');\n      drawCards(game, index, 2);\n      game.phase = 'play';\n      game.revision++;\n      ack({ ok: true }); emitGame(room); return;\n    }\n    if (type === 'HARVEST_START') {\n      if (game.phase !== 'start') return rejectGameAction(ack, 'Vous ne pouvez pas récolter maintenant.');\n      game.players[index].gold += ownedRegionCount(game,index)*2;\n      game.phase='play';game.revision++;ack({ok:true});emitGame(room);return;\n    }\n    if (type === 'RECRUIT_START') {\n      if (game.phase !== 'start') return rejectGameAction(ack, 'Vous ne pouvez pas recruter maintenant.');\n      game.recruitSnapshot={player:index,gold:game.players[index].gold,units:Object.fromEntries(Object.entries(game.board).map(([r,c])=>[r,c.units]))};\n      game.phase='recruit';game.revision++;ack({ok:true});emitGame(room);return;\n    }\n    if (type === 'RESET_RECRUIT') {\n      if (game.phase !== 'recruit' || !game.recruitSnapshot || game.recruitSnapshot.player!==index) return rejectGameAction(ack, 'Aucun recrutement à recommencer.');\n      game.players[index].gold=game.recruitSnapshot.gold;Object.entries(game.recruitSnapshot.units).forEach(([r,u])=>{game.board[r].units=u});\n      game.revision++;ack({ok:true});emitGame(room);return;\n    }\n    if (type === 'RECRUIT_AT') {\n      if (game.phase !== 'recruit') return rejectGameAction(ack, 'Vous n’êtes pas en phase de recrutement.');\n      const r=String(payload.region||''),cell=game.board[r],player=game.players[index];\n      if (!cell || cell.owner!==index) return rejectGameAction(ack, 'Choisissez une de vos régions.');\n      if (player.gold<1) return rejectGameAction(ack, 'Pas assez d’Or.');\n      if (totalUnitsFor(game,index)>=unitCapFor(game,index)) return rejectGameAction(ack, 'Plafond d’unités atteint.');\n      const terrain=TERRAIN[r],faction=player.faction;if(faction===0&&terrain==='d')return rejectGameAction(ack,'Les Griffes-Blanches ne recrutent pas dans le désert.');if(faction===1&&terrain==='e')return rejectGameAction(ack,'Les Reptones ne recrutent pas dans la neige.');\n      let q=(faction===0&&terrain==='e')||(faction===1&&terrain==='d')?2:1;q=Math.min(q,unitCapFor(game,index)-totalUnitsFor(game,index));\n      player.gold--;cell.units+=q;game.revision++;ack({ok:true});emitGame(room);return;\n    }\n    if (type === 'END_RECRUIT') {\n      if (game.phase !== 'recruit') return rejectGameAction(ack, 'Vous n’êtes pas en phase de recrutement.');\n      game.recruitSnapshot=null;game.phase='play';game.revision++;ack({ok:true});emitGame(room);return;\n    }\n    return rejectGameAction(ack, 'Action Online pas encore migrée vers le serveur.');"""
assert old in s
s=s.replace(old,new,1)

p.write_text(s,encoding='utf-8')
