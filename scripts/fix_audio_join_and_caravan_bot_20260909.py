from pathlib import Path

idx=Path('index.html')
s=idx.read_text(encoding='utf-8')
server=Path('server/server.js')
ss=server.read_text(encoding='utf-8')

def rep(text, old, new, label):
    if old not in text:
        raise SystemExit('MISSING '+label)
    return text.replace(old,new,1)

# 1) Audio tablette : ne jamais "déverrouiller" en jouant tous les sons.
s=rep(s,
"function audioPrimeSfx(){\n if(audioSfxPrimed)return;\n audioSfxPrimed=true;\n ['gold','oracle','dragon','assassin','thief','fail','drums','horn','cardMove','construction'].forEach(name=>{\n   audioSfxPool(name).forEach(a=>{\n     const v=a.volume;a.volume=0;\n     try{const p=a.play();if(p&&p.then)p.then(()=>{a.pause();try{a.currentTime=0}catch(e){}a.volume=v}).catch(()=>{a.volume=v})}catch(e){a.volume=v}\n   });\n });\n}\n",
"function audioPrimeSfx(){\n if(audioSfxPrimed)return;\n audioSfxPrimed=true;\n // Sur tablette/iOS, lancer toutes les pistes même à volume 0 peut les rendre audibles.\n // On prépare donc seulement les objets Audio au premier geste utilisateur.\n ['gold','oracle','dragon','assassin','thief','fail','drums','horn','cardMove','construction'].forEach(name=>{\n   audioSfxPool(name).forEach(a=>{try{a.load()}catch(e){}});\n });\n}\n",
'audio prime no playback')

# 2) Le canal direct Socket.IO a sa propre séquence serveur. Les snapshots ne rejouent plus l'historique sonore.
s=rep(s,
"let onlineSfxSeq=0,onlineSfxEvents=[],onlineSfxSeenSeq=0,onlineOraclePresentationSeenSeq=0,onlineAssassinNoticeSeenSeq=0,onlineDragonSixPresentationSeenSeq=0,onlineOracleRemoteTick=null,onlineDragonSixRemoteTick=null;",
"let onlineSfxSeq=0,onlineSfxEvents=[],onlineSfxSeenSeq=0,onlineDirectSfxSeenSeq=0,onlineOraclePresentationSeenSeq=0,onlineAssassinNoticeSeenSeq=0,onlineDragonSixPresentationSeenSeq=0,onlineOracleRemoteTick=null,onlineDragonSixRemoteTick=null;",
'direct sfx seq')

s=rep(s,
"function onlineReceiveSfx(ev){\n if(!ev||!AUDIO_SRC[ev.name])return;\n const seq=Number(ev.seq)||0;if(seq&&seq<=onlineSfxSeenSeq)return;\n if(seq)onlineSfxSeenSeq=Math.max(onlineSfxSeenSeq,seq);\n audioPlaySfxLocal(ev.name,Number.isFinite(Number(ev.vol))?Number(ev.vol):.8);\n}\nfunction onlinePlaySyncedSfx(events,seq){\n if(!Array.isArray(events)){onlineSfxSeenSeq=Math.max(onlineSfxSeenSeq,Number(seq)||0);return}\n events.filter(e=>e&&Number(e.seq)>onlineSfxSeenSeq).sort((a,b)=>a.seq-b.seq).forEach(e=>onlineReceiveSfx(e));\n onlineSfxSeenSeq=Math.max(onlineSfxSeenSeq,Number(seq)||0);\n}\n",
"function onlineReceiveSfx(ev){\n if(!ev||!AUDIO_SRC[ev.name])return;\n const serverSeq=Number(ev.serverSeq)||0;\n if(serverSeq&&serverSeq<=onlineDirectSfxSeenSeq)return;\n if(serverSeq)onlineDirectSfxSeenSeq=serverSeq;\n audioPlaySfxLocal(ev.name,Number.isFinite(Number(ev.vol))?Number(ev.vol):.8);\n}\nfunction onlinePlaySyncedSfx(events,seq){\n // Les snapshots conservent les événements pour compatibilité/reconnexion,\n // mais ne doivent jamais rejouer un historique sonore à l'arrivée d'un joueur.\n onlineSfxSeenSeq=Math.max(onlineSfxSeenSeq,Number(seq)||0);\n}\n",
'direct sfx receiver and snapshot no replay')

s=rep(s,
" onlineSfxSeq=0;onlineSfxEvents=[];onlineSfxSeenSeq=0;onlineOraclePresentationSeenSeq=Number(G.oraclePresentation&&G.oraclePresentation.seq||0);onlineAssassinNoticeSeenSeq=Number(G.assassinNotice&&G.assassinNotice.seq||0);onlineDragonSixPresentationSeenSeq=Number(G.dragonSixPresentation&&G.dragonSixPresentation.seq||0);",
" onlineSfxSeq=0;onlineSfxEvents=[];onlineSfxSeenSeq=0;onlineDirectSfxSeenSeq=0;onlineOraclePresentationSeenSeq=Number(G.oraclePresentation&&G.oraclePresentation.seq||0);onlineAssassinNoticeSeenSeq=Number(G.assassinNotice&&G.assassinNotice.seq||0);onlineDragonSixPresentationSeenSeq=Number(G.dragonSixPresentation&&G.dragonSixPresentation.seq||0);",
'bootstrap direct seq')

# 3) Caravane : le navigateur du joueur qui a lancé la Caravane conduit les choix des bots,
# même si le joueur actif n'est pas un bot.
insert="""function onlineLegacyCanDriveCaravanBot(){
 if(!caravanState||!G||!G.online||!G.online.legacySync)return true;
 const me=localViewer(),actor=caravanState.actor;
 if(Number.isInteger(actor)&&G.players[actor]&&!G.players[actor].bot)return me===actor;
 return onlineLegacyCanExecuteBot();
}
"""
needle="function showCaravanChoice(){"
if needle not in s: raise SystemExit('MISSING caravan helper insertion')
s=s.replace(needle,insert+needle,1)

s=rep(s,
"   if(onlineLegacyCanExecuteBot()){const j=Math.floor(Math.random()*caravanState.revealed.length);setTimeout(()=>{if(caravanState&&caravanState.order[caravanState.pick]===chooser)chooseCaravanCard(j)},300)}",
"   if(onlineLegacyCanDriveCaravanBot()){const j=Math.floor(Math.random()*caravanState.revealed.length);setTimeout(()=>{if(caravanState&&caravanState.order[caravanState.pick]===chooser&&onlineLegacyCanDriveCaravanBot())chooseCaravanCard(j)},300)}",
'caravan bot scheduler')

s=rep(s,
" if(G.online&&G.online.legacySync&&G.players[chooser].bot&&!onlineLegacyCanExecuteBot())return;",
" if(G.online&&G.online.legacySync&&G.players[chooser].bot&&!onlineLegacyCanDriveCaravanBot())return;",
'caravan bot permission')

# 4) Séquence SFX unique au niveau de la salle pour éviter les collisions entre J1/J2.
ss=rep(ss,
"    const seq=Math.max(0,Math.floor(Number(payload.seq)||0));\n    const vol=Math.max(0,Math.min(1,Number(payload.vol)||.8));\n    socket.to(room.code).emit('legacySfx',{seq,name,vol});",
"    const clientSeq=Math.max(0,Math.floor(Number(payload.seq)||0));\n    const vol=Math.max(0,Math.min(1,Number(payload.vol)||.8));\n    room.legacySfxSeq=(room.legacySfxSeq||0)+1;\n    socket.to(room.code).emit('legacySfx',{serverSeq:room.legacySfxSeq,clientSeq,name,vol});",
'server room sfx seq')

idx.write_text(s,encoding='utf-8')
server.write_text(ss,encoding='utf-8')
