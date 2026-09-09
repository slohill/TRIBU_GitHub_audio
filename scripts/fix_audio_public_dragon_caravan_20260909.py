from pathlib import Path

idx=Path('index.html')
s=idx.read_text(encoding='utf-8')
server=Path('server/server.js')
ss=server.read_text(encoding='utf-8')

def rep(text, old, new, label):
    if old not in text:
        raise SystemExit('MISSING '+label)
    return text.replace(old,new,1)

# --- Audio: direct Socket.IO relay + iPad/tablet unlock + snapshot fallback ---
s=rep(s,
"let onlineSfxSeq=0,onlineSfxEvents=[],onlineSfxSeenSeq=0,onlineOraclePresentationSeenSeq=0,onlineAssassinNoticeSeenSeq=0,onlineOracleRemoteTick=null;\nfunction audioPlaySfx(name,vol=.8){\n if(!audioSfxEnabled||!AUDIO_SRC[name])return;\n if(G&&G.online&&G.online.legacySync&&!onlineLegacyApplying){\n   const ev={seq:++onlineSfxSeq,name,vol};\n   onlineSfxEvents.push(ev);if(onlineSfxEvents.length>24)onlineSfxEvents=onlineSfxEvents.slice(-24);\n   onlineSfxSeenSeq=ev.seq;\n }\n const a=new Audio(AUDIO_SRC[name]);a.volume=vol;const p=a.play();if(p&&p.catch)p.catch(()=>{});\n}\nfunction onlinePlaySyncedSfx(events,seq){\n if(!Array.isArray(events)){onlineSfxSeenSeq=Math.max(onlineSfxSeenSeq,Number(seq)||0);return}\n events.filter(e=>e&&Number(e.seq)>onlineSfxSeenSeq).sort((a,b)=>a.seq-b.seq).forEach(e=>{\n   onlineSfxSeenSeq=Math.max(onlineSfxSeenSeq,Number(e.seq)||0);\n   audioPlaySfx(e.name,Number.isFinite(Number(e.vol))?Number(e.vol):.8);\n });\n onlineSfxSeenSeq=Math.max(onlineSfxSeenSeq,Number(seq)||0);\n}\n",
"let onlineSfxSeq=0,onlineSfxEvents=[],onlineSfxSeenSeq=0,onlineOraclePresentationSeenSeq=0,onlineAssassinNoticeSeenSeq=0,onlineDragonSixPresentationSeenSeq=0,onlineOracleRemoteTick=null,onlineDragonSixRemoteTick=null;\nconst audioSfxPools={};let audioSfxPoolCursor=0,audioSfxPrimed=false;\nfunction audioSfxPool(name){\n if(!AUDIO_SRC[name])return [];\n if(!audioSfxPools[name])audioSfxPools[name]=Array.from({length:3},()=>{const a=new Audio(AUDIO_SRC[name]);a.preload='auto';return a});\n return audioSfxPools[name];\n}\nfunction audioPrimeSfx(){\n if(audioSfxPrimed)return;\n audioSfxPrimed=true;\n ['gold','oracle','dragon','assassin','thief','fail','drums','horn','cardMove','construction'].forEach(name=>{\n   audioSfxPool(name).forEach(a=>{\n     const v=a.volume;a.volume=0;\n     try{const p=a.play();if(p&&p.then)p.then(()=>{a.pause();try{a.currentTime=0}catch(e){}a.volume=v}).catch(()=>{a.volume=v})}catch(e){a.volume=v}\n   });\n });\n}\nfunction audioPlaySfxLocal(name,vol=.8){\n if(!audioSfxEnabled||!AUDIO_SRC[name])return;\n const pool=audioSfxPool(name);if(!pool.length)return;\n let a=pool.find(x=>x.paused||x.ended);\n if(!a){a=pool[(audioSfxPoolCursor++)%pool.length];a.pause()}\n try{a.currentTime=0}catch(e){}a.volume=Math.max(0,Math.min(1,Number(vol)||.8));\n try{const p=a.play();if(p&&p.catch)p.catch(()=>{})}catch(e){}\n}\nfunction audioPlaySfx(name,vol=.8){\n if(!AUDIO_SRC[name])return;\n if(G&&G.online&&G.online.legacySync&&!onlineLegacyApplying){\n   const ev={seq:++onlineSfxSeq,name,vol};\n   onlineSfxEvents.push(ev);if(onlineSfxEvents.length>24)onlineSfxEvents=onlineSfxEvents.slice(-24);\n   onlineSfxSeenSeq=ev.seq;\n   if(onlineSocket&&onlineSocket.connected)onlineSocket.emit('legacySfx',ev);\n }\n audioPlaySfxLocal(name,vol);\n}\nfunction onlineReceiveSfx(ev){\n if(!ev||!AUDIO_SRC[ev.name])return;\n const seq=Number(ev.seq)||0;if(seq&&seq<=onlineSfxSeenSeq)return;\n if(seq)onlineSfxSeenSeq=Math.max(onlineSfxSeenSeq,seq);\n audioPlaySfxLocal(ev.name,Number.isFinite(Number(ev.vol))?Number(ev.vol):.8);\n}\nfunction onlinePlaySyncedSfx(events,seq){\n if(!Array.isArray(events)){onlineSfxSeenSeq=Math.max(onlineSfxSeenSeq,Number(seq)||0);return}\n events.filter(e=>e&&Number(e.seq)>onlineSfxSeenSeq).sort((a,b)=>a.seq-b.seq).forEach(e=>onlineReceiveSfx(e));\n onlineSfxSeenSeq=Math.max(onlineSfxSeenSeq,Number(seq)||0);\n}\ndocument.addEventListener('pointerdown',audioPrimeSfx,{capture:true,passive:true});\ndocument.addEventListener('touchend',audioPrimeSfx,{capture:true,passive:true});\n",
'audio relay and unlock')

# --- Caravan: persist human -> bot handoff, no freeze ---
s=rep(s,
" if(G&&G.online&&G.online.legacySync){if(G.players[chooser].bot)onlineLegacyPushNow();else onlineLegacyPushPriorityCardNow()}\n}\nfunction finishCaravan(){",
" if(G&&G.online&&G.online.legacySync)onlineLegacyPushCaravanNow();\n}\nfunction finishCaravan(){",
'caravan publish call')

needle="function onlineLegacyPushGoldReactionNow(){"
helper="""function onlineLegacyPushCaravanNow(){
 if(!G||!G.online||!G.online.legacySync||onlineLegacyApplying||!onlineSocket)return;
 const actorIndex=G.online.myPlayerIndex;if(!Number.isInteger(actorIndex)||!G.players[actorIndex]||G.players[actorIndex].bot)return;
 clearTimeout(onlineLegacyPushTimer);
 const snapshot=onlineLegacySnapshot(),digest=onlineLegacyDigest();
 const send=(baseRevision,retries)=>onlineAck('legacyCommit',{baseRevision,actorIndex,snapshot}).then(res=>{
   onlineLegacyRevision=Math.max(onlineLegacyRevision,res.revision||0);G.online.revision=onlineLegacyRevision;onlineLegacyLastDigest=digest;
 }).catch(err=>{
   if(err&&err.current&&retries>0&&Number.isInteger(err.current.revision)){
     onlineLegacyRevision=Math.max(onlineLegacyRevision,err.current.revision);G.online.revision=onlineLegacyRevision;
     return send(onlineLegacyRevision,retries-1);
   }
   onlineLegacyLastDigest='';if(err&&err.current)onlineLegacyApply(err.current);else onlineError(err);
 });
 send(onlineLegacyRevision,2);
}
"""
if needle not in s: raise SystemExit('MISSING caravan helper insertion')
s=s.replace(needle,helper+needle,1)

# --- Public Dragon destruction notice on every client ---
s=rep(s,
" if(had){audioPlaySfx('dragon',.9);checkDecimations();showDragonSixNotice(victim,()=>advanceTurn('nouveau tour'));render();return}",
" if(had){\n   G.dragonSixPresentation={seq:Number(G.dragonSixPresentation&&G.dragonSixPresentation.seq||0)+1,victim};\n   onlineDragonSixPresentationSeenSeq=Number(G.dragonSixPresentation.seq);\n   audioPlaySfx('dragon',.9);checkDecimations();showDragonSixNotice(victim,()=>advanceTurn('nouveau tour'));render();return\n }",
'dragon public event')

s=rep(s,
"function showDragonSixNotice(victim,next){\n clearInterval(dragonSixTick);",
"function showDragonSixNotice(victim,next){\n clearInterval(dragonSixTick);\n const pass=$('dragonSixPass');if(pass)pass.onclick=finishDragonSixNotice;",
'dragon local pass reset')

insert="""function showDragonSixRemoteNotice(victim){
 clearInterval(onlineDragonSixRemoteTick);
 const viewer=localViewer();
 $('dragonSixTitle').textContent='LE DRAGON SÈME LA DESTRUCTION';
 $('dragonSixText').textContent=victim!==null&&viewer===victim
   ? 'Le dragon sème la destruction dans votre empire !\\nUne de vos régions a été dévastée par le feu…'
   : (victim!==null?'Le dragon a détruit une région de '+p(victim).name+'.':'Le dragon a dévasté une région.');
 let seconds=5;$('dragonSixTimer').textContent='5 s';$('dragonSixOverlay').classList.remove('hidden');
 const close=()=>{clearInterval(onlineDragonSixRemoteTick);$('dragonSixOverlay').classList.add('hidden')};
 const pass=$('dragonSixPass');if(pass)pass.onclick=close;
 onlineDragonSixRemoteTick=setInterval(()=>{seconds--;$('dragonSixTimer').textContent=Math.max(0,seconds)+' s';if(seconds<=0)close()},1000);
}
"""
needle="function showOracleRemoteNotice(name){"
if needle not in s: raise SystemExit('MISSING remote notice insertion')
s=s.replace(needle,insert+needle,1)

# Remote Oracle pass must close its visual instead of trying to execute rules.
s=rep(s,
" let seconds=5;$('oracleNoticeTimer').textContent='5 s';$('oracleNoticeOverlay').classList.remove('hidden');\n onlineOracleRemoteTick=setInterval(()=>{seconds--;$('oracleNoticeTimer').textContent=Math.max(0,seconds)+' s';if(seconds<=0){clearInterval(onlineOracleRemoteTick);$('oracleNoticeOverlay').classList.add('hidden')}},1000);",
" let seconds=5;$('oracleNoticeTimer').textContent='5 s';$('oracleNoticeOverlay').classList.remove('hidden');\n const close=()=>{clearInterval(onlineOracleRemoteTick);$('oracleNoticeOverlay').classList.add('hidden')};\n const pass=$('oracleNoticePass');if(pass)pass.onclick=close;\n onlineOracleRemoteTick=setInterval(()=>{seconds--;$('oracleNoticeTimer').textContent=Math.max(0,seconds)+' s';if(seconds<=0)close()},1000);",
'oracle remote close')

s=rep(s,
" const op=G&&G.oraclePresentation;\n if(op&&Number(op.seq)>onlineOraclePresentationSeenSeq){onlineOraclePresentationSeenSeq=Number(op.seq);showOracleRemoteNotice(op.name)}\n const an=G&&G.assassinNotice;",
" const op=G&&G.oraclePresentation;\n if(op&&Number(op.seq)>onlineOraclePresentationSeenSeq){onlineOraclePresentationSeenSeq=Number(op.seq);showOracleRemoteNotice(op.name)}\n const dp=G&&G.dragonSixPresentation;\n if(dp&&Number(dp.seq)>onlineDragonSixPresentationSeenSeq){onlineDragonSixPresentationSeenSeq=Number(dp.seq);showDragonSixRemoteNotice(dp.victim)}\n const an=G&&G.assassinNotice;",
'apply dragon presentation')

s=rep(s,
"onlineSfxSeq=0;onlineSfxEvents=[];onlineSfxSeenSeq=0;onlineOraclePresentationSeenSeq=Number(G.oraclePresentation&&G.oraclePresentation.seq||0);onlineAssassinNoticeSeenSeq=Number(G.assassinNotice&&G.assassinNotice.seq||0);",
"onlineSfxSeq=0;onlineSfxEvents=[];onlineSfxSeenSeq=0;onlineOraclePresentationSeenSeq=Number(G.oraclePresentation&&G.oraclePresentation.seq||0);onlineAssassinNoticeSeenSeq=Number(G.assassinNotice&&G.assassinNotice.seq||0);onlineDragonSixPresentationSeenSeq=Number(G.dragonSixPresentation&&G.dragonSixPresentation.seq||0);",
'bootstrap dragon seq')

# Oracle source should not replay its own public notice later.
s=rep(s,
" G.oraclePresentation={seq:Number(G.oraclePresentation&&G.oraclePresentation.seq||0)+1,name:o.name};\n log('🔮 Oracle activé : '+o.name+'.');",
" G.oraclePresentation={seq:Number(G.oraclePresentation&&G.oraclePresentation.seq||0)+1,name:o.name};\n onlineOraclePresentationSeenSeq=Number(G.oraclePresentation.seq);\n log('🔮 Oracle activé : '+o.name+'.');",
'oracle source seen')

# Client direct socket SFX receiver.
s=rep(s,
"  socket.on('gameState',applyOnlineGameState);\n  socket.on('legacyState',packet=>onlineLegacyApply(packet));",
"  socket.on('gameState',applyOnlineGameState);\n  socket.on('legacyState',packet=>onlineLegacyApply(packet));\n  socket.on('legacySfx',onlineReceiveSfx);",
'client legacy sfx socket')

# --- Server direct SFX relay ---
ss=rep(ss,
"  socket.on('legacyCommit', (payload = {}, ack = () => {}) => {",
"  socket.on('legacySfx', (payload = {}) => {\n    const room=roomForSocket(socket);\n    if(!room||!room.game||room.game.status!=='playing'||!room.legacyMode)return;\n    const index=humanGameIndex(room,socket.id);if(index<0)return;\n    const allowed=new Set(['gold','oracle','dragon','assassin','thief','fail','drums','horn','cardMove','construction']);\n    const name=String(payload.name||'');if(!allowed.has(name))return;\n    const seq=Math.max(0,Math.floor(Number(payload.seq)||0));\n    const vol=Math.max(0,Math.min(1,Number(payload.vol)||.8));\n    socket.to(room.code).emit('legacySfx',{seq,name,vol});\n  });\n\n  socket.on('legacyCommit', (payload = {}, ack = () => {}) => {",
'server legacy sfx relay')

idx.write_text(s,encoding='utf-8')
server.write_text(ss,encoding='utf-8')
