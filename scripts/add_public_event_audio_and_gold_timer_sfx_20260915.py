from pathlib import Path

p=Path('index.html')
s=p.read_text(encoding='utf-8')

def rep(old,new,count=1):
    global s
    if s.count(old)!=count:
        raise SystemExit(f'expected {count} occurrence(s), got {s.count(old)} for:\n{old[:180]}')
    s=s.replace(old,new,count)

# Public event overlay, using the existing full-screen event style.
old='''<div id="dragonCurseOverlay" class="dragonCurseOverlay hidden">\n  <div class="dragonCurseModal">\n    <div class="dragonCurseIcon">🐉</div>\n    <h2>MALÉDICTION DU DRAGON</h2>\n    <div id="dragonCurseText" class="dragonCurseText"></div>\n    <button id="dragonCurseContinue">Continuer</button>\n  </div>\n</div>\n<div id="agentOverlay" class="agentOverlay hidden">'''
new='''<div id="dragonCurseOverlay" class="dragonCurseOverlay hidden">\n  <div class="dragonCurseModal">\n    <div class="dragonCurseIcon">🐉</div>\n    <h2>MALÉDICTION DU DRAGON</h2>\n    <div id="dragonCurseText" class="dragonCurseText"></div>\n    <button id="dragonCurseContinue">Continuer</button>\n  </div>\n</div>\n<div id="publicEventOverlay" class="dragonCurseOverlay hidden">\n  <div class="dragonCurseModal">\n    <div id="publicEventIcon" class="dragonCurseIcon">⚔️</div>\n    <h2 id="publicEventTitle">ÉVÉNEMENT</h2>\n    <div id="publicEventText" class="dragonCurseText"></div>\n    <div id="publicEventTimer" style="margin-top:10px;font-weight:900">8 s</div>\n    <button id="publicEventPass">Passer</button>\n  </div>\n</div>\n<div id="agentOverlay" class="agentOverlay hidden">'''
rep(old,new)

# Audio sources: preserve the exact uploaded filename for Egnobombe (capital E).
old=''' construction:"assets/audio/construction.mp3"\n};'''
new=''' construction:"assets/audio/construction.mp3",\n egnobombe:"assets/audio/Egnobombe.mp3",\n epicbattle:"assets/audio/epicbattle.mp3",\n gaindor:"assets/audio/gaindor.mp3"\n};'''
rep(old,new)

# Add public-event state and a dedicated restartable gain-of-gold soundtrack.
old='''let onlineSfxSeq=0,onlineSfxEvents=[],onlineSfxSeenSeq=0,onlineDirectSfxSeenSeq=0,onlineOraclePresentationSeenSeq=0,onlineAssassinNoticeSeenSeq=0,onlineDragonSixPresentationSeenSeq=0,onlineOracleRemoteTick=null,onlineDragonSixRemoteTick=null;\nconst audioSfxPools={};let audioSfxPoolCursor=0,audioSfxPrimed=false;'''
new='''let onlineSfxSeq=0,onlineSfxEvents=[],onlineSfxSeenSeq=0,onlineDirectSfxSeenSeq=0,onlineOraclePresentationSeenSeq=0,onlineAssassinNoticeSeenSeq=0,onlineDragonSixPresentationSeenSeq=0,onlinePublicEventSeenSeq=0,onlineOracleRemoteTick=null,onlineDragonSixRemoteTick=null,onlinePublicEventTick=null;\nconst audioSfxPools={};let audioSfxPoolCursor=0,audioSfxPrimed=false,goldReactionSfx=null,goldReactionSfxActive=false;'''
rep(old,new)

old=""" ['gold','oracle','dragon','assassin','thief','fail','drums','horn','cardMove','construction'].forEach(name=>{\n   audioSfxPool(name).forEach(a=>{try{a.load()}catch(e){}});\n });\n}"""
new=""" ['gold','oracle','dragon','assassin','thief','fail','drums','horn','cardMove','construction','egnobombe','epicbattle'].forEach(name=>{\n   audioSfxPool(name).forEach(a=>{try{a.load()}catch(e){}});\n });\n try{goldReactionAudio().load()}catch(e){}\n}\nfunction goldReactionAudio(){\n if(!goldReactionSfx){goldReactionSfx=new Audio(AUDIO_SRC.gaindor);goldReactionSfx.preload='auto';goldReactionSfx.loop=true}\n return goldReactionSfx;\n}\nfunction startGoldReactionSfx(){\n if(!audioSfxEnabled||!goldReaction||goldReaction.pausedByCard||isHotseatMode())return;\n const a=goldReactionAudio();\n try{a.pause();a.currentTime=0}catch(e){}\n a.volume=.78;goldReactionSfxActive=true;\n try{const pr=a.play();if(pr&&pr.catch)pr.catch(()=>{})}catch(e){}\n}\nfunction stopGoldReactionSfx(){\n if(!goldReactionSfx)return;\n try{goldReactionSfx.pause();goldReactionSfx.currentTime=0}catch(e){}\n goldReactionSfxActive=false;\n}"""
rep(old,new)

old="function audioSetSfx(on){audioSfxEnabled=!!on;try{localStorage.setItem('tribu_sfx',on?'on':'off')}catch(e){}audioUpdateButtons()}"
new="function audioSetSfx(on){audioSfxEnabled=!!on;try{localStorage.setItem('tribu_sfx',on?'on':'off')}catch(e){}if(!audioSfxEnabled)stopGoldReactionSfx();else if(goldReaction&&!goldReaction.pausedByCard)startGoldReactionSfx();audioUpdateButtons()}"
rep(old,new)

# Gold sound follows the timer lifecycle exactly: stop on any clear/pause, restart from 0 on each timed window.
old="function clearGoldReactionTimer(){\n if(goldReactionTick){clearInterval(goldReactionTick);goldReactionTick=null}\n}"
new="function clearGoldReactionTimer(){\n if(goldReactionTick){clearInterval(goldReactionTick);goldReactionTick=null}\n stopGoldReactionSfx();\n}"
rep(old,new)

old=""" if(isHotseatMode()){\n   goldReaction.hotseatFreeReaction=true;\n   render();\n   maybeBotAmbush();\n   return;\n }\n goldReactionTick=setInterval(()=>{"""
new=""" if(isHotseatMode()){\n   goldReaction.hotseatFreeReaction=true;\n   render();\n   maybeBotAmbush();\n   return;\n }\n startGoldReactionSfx();\n goldReactionTick=setInterval(()=>{"""
rep(old,new)

old="""function onlineLegacyStartGoldViewTimer(){\n clearGoldReactionTimer();\n if(!goldReaction){onlineLegacyGoldViewSeconds=null;return}\n onlineLegacyGoldViewSeconds=Math.max(0,Number(goldReaction.seconds)||0);\n goldReactionTick=setInterval(()=>{"""
new="""function onlineLegacyStartGoldViewTimer(){\n clearGoldReactionTimer();\n if(!goldReaction){onlineLegacyGoldViewSeconds=null;return}\n onlineLegacyGoldViewSeconds=Math.max(0,Number(goldReaction.seconds)||0);\n if(goldReaction.pausedByCard)return;\n startGoldReactionSfx();\n goldReactionTick=setInterval(()=>{"""
rep(old,new)

# Public presentation helpers. Snapshot delivery carries the presentation; sound is played locally on each screen exactly once.
marker='''function onlineApplyPrivatePresentations(me){\n const op=G&&G.oraclePresentation;'''
insert='''function publicEventText(ev){\n if(!ev)return '';\n if(ev.kind==='egnobombe')return p(ev.actor).name+\" a utilisé l'Egnobombe : le nuage mortel de cette arme Egnorax dévastatrice a décimé les populations de nombreuses Régions... Il y a très peu de survivants...\";\n if(ev.kind==='epicbattle'){\n   const loser=Number.isInteger(ev.other)&&G.players[ev.other]?p(ev.other).name:'les forces hostiles';\n   return p(ev.actor).name+' a vaincu '+loser+' lors d’une grande et périlleuse bataille. Cette victoire sera chantée dans les tavernes de Myrmigate et ces chants traverseront les âges';\n }\n return '';\n}\nfunction showPublicEventPresentation(ev){\n if(!ev||!publicEventText(ev))return;\n clearInterval(onlinePublicEventTick);\n const epic=ev.kind==='epicbattle';\n $('publicEventIcon').textContent=epic?'🏆⚔️':'💣☠️';\n $('publicEventTitle').textContent=epic?'BATAILLE ÉPIQUE':'EGNOBOMBE';\n $('publicEventText').textContent=publicEventText(ev);\n let seconds=8;$('publicEventTimer').textContent='8 s';$('publicEventOverlay').classList.remove('hidden');\n audioPlaySfxLocal(epic?'epicbattle':'egnobombe',.92);\n const close=()=>{clearInterval(onlinePublicEventTick);$('publicEventOverlay').classList.add('hidden')};\n const pass=$('publicEventPass');if(pass)pass.onclick=close;\n onlinePublicEventTick=setInterval(()=>{seconds--;$('publicEventTimer').textContent=Math.max(0,seconds)+' s';if(seconds<=0)close()},1000);\n}\nfunction announcePublicEvent(kind,actor,other=null){\n if(!G)return;\n const ev={seq:Number(G.publicEventPresentation&&G.publicEventPresentation.seq||0)+1,kind,actor,other,at:Date.now()};\n G.publicEventPresentation=ev;onlinePublicEventSeenSeq=ev.seq;showPublicEventPresentation(ev);\n}\nfunction onlineApplyPrivatePresentations(me){\n const pe=G&&G.publicEventPresentation;\n if(pe&&Number(pe.seq)>onlinePublicEventSeenSeq){onlinePublicEventSeenSeq=Number(pe.seq);if(!pe.at||Date.now()-Number(pe.at)<30000)showPublicEventPresentation(pe)}\n const op=G&&G.oraclePresentation;'''
rep(marker,insert)

# Bootstrap should not replay an old public event after reconnect.
old="onlineSfxSeq=0;onlineSfxEvents=[];onlineSfxSeenSeq=0;onlineDirectSfxSeenSeq=0;onlineOraclePresentationSeenSeq=Number(G.oraclePresentation&&G.oraclePresentation.seq||0);onlineAssassinNoticeSeenSeq=Number(G.assassinNotice&&G.assassinNotice.seq||0);onlineDragonSixPresentationSeenSeq=Number(G.dragonSixPresentation&&G.dragonSixPresentation.seq||0);"
new="onlineSfxSeq=0;onlineSfxEvents=[];onlineSfxSeenSeq=0;onlineDirectSfxSeenSeq=0;onlineOraclePresentationSeenSeq=Number(G.oraclePresentation&&G.oraclePresentation.seq||0);onlineAssassinNoticeSeenSeq=Number(G.assassinNotice&&G.assassinNotice.seq||0);onlineDragonSixPresentationSeenSeq=Number(G.dragonSixPresentation&&G.dragonSixPresentation.seq||0);onlinePublicEventSeenSeq=Number(G.publicEventPresentation&&G.publicEventPresentation.seq||0);"
rep(old,new)

# Egnobombe presentation at irreversible resolution, before any resume/turn branch.
old=""" log(p(actor).name+' déclenche Egnobombe en '+r+' : '+sacrificed+' unité(s) sacrifiée(s), unités détruites sur '+affected.join(', ')+'.');checkDecimations();\n\n // If a paused battle's defending region was hit, refresh its board-based defense."""
new=""" log(p(actor).name+' déclenche Egnobombe en '+r+' : '+sacrificed+' unité(s) sacrifiée(s), unités détruites sur '+affected.join(', ')+'.');checkDecimations();\n announcePublicEvent('egnobombe',actor);\n\n // If a paused battle's defending region was hit, refresh its board-based defense."""
rep(old,new)

# Epic presentation only where the permanent epic VP is actually awarded.
old="""     G.players[attacker].pvPermanent=(G.players[attacker].pvPermanent||0)+1;\n     log('🏆 BATAILLE ÉPIQUE : '+p(attacker).name+' gagne 1 Point de victoire permanent en battant une puissance militaire totale de '+d+'.');"""
new="""     G.players[attacker].pvPermanent=(G.players[attacker].pvPermanent||0)+1;\n     log('🏆 BATAILLE ÉPIQUE : '+p(attacker).name+' gagne 1 Point de victoire permanent en battant une puissance militaire totale de '+d+'.');\n     announcePublicEvent('epicbattle',attacker,defender);"""
rep(old,new)

old="""     G.players[defender].pvPermanent=(G.players[defender].pvPermanent||0)+1;\n     log('🏆 BATAILLE ÉPIQUE : '+p(defender).name+' gagne 1 Point de victoire permanent en battant une puissance militaire totale de '+a+'.');"""
new="""     G.players[defender].pvPermanent=(G.players[defender].pvPermanent||0)+1;\n     log('🏆 BATAILLE ÉPIQUE : '+p(defender).name+' gagne 1 Point de victoire permanent en battant une puissance militaire totale de '+a+'.');\n     announcePublicEvent('epicbattle',defender,attacker);"""
rep(old,new)

p.write_text(s,encoding='utf-8')
print('patched index.html')
