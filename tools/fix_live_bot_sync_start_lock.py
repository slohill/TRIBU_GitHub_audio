from pathlib import Path
p=Path('index.html')
s=p.read_text()

def rep(a,b):
 global s
 if a not in s: raise SystemExit('pattern missing: '+a[:100])
 s=s.replace(a,b,1)

rep("function doDraw(){if(G&&G.online&&!G.online.legacySync)return onlineGameAction('DRAW_START');if(paidDrawState)return;draw(G.active,2);log(p().name+' pioche 2 cartes.');beginPlay()}",
"function doDraw(){if(G&&G.online&&!G.online.legacySync)return onlineGameAction('DRAW_START');if(G.phase!=='start'||paidDrawState||goldReaction)return;draw(G.active,2);log(p().name+' pioche 2 cartes.');beginPlay()}")
rep("function doHarvest(){if(G&&G.online&&!G.online.legacySync)return onlineGameAction('HARVEST_START');if(paidDrawState||goldReaction)return;",
"function doHarvest(){if(G&&G.online&&!G.online.legacySync)return onlineGameAction('HARVEST_START');if(G.phase!=='start'||paidDrawState||goldReaction)return;")
rep(" if(paidDrawState)return;\n recruitSnapshot={player:G.active,gold:p().gold,units:{}};",
" if(G.phase!=='start'||paidDrawState||goldReaction)return;\n recruitSnapshot={player:G.active,gold:p().gold,units:{}};")

rep("let onlineLegacyRevision=0,onlineLegacyApplying=false,onlineLegacyLastDigest='',onlineLegacyPushTimer=null;",
"let onlineLegacyRevision=0,onlineLegacyApplying=false,onlineLegacyLastDigest='',onlineLegacyPushTimer=null,onlineLegacyBotDriverIndex=null;")
rep("   oraclePendingNormalMap,turnEpoch,divinationState,recruitSnapshot,gameOverState,commerceDeals,commerceSeq\n };\n}",
"   oraclePendingNormalMap,turnEpoch,divinationState,recruitSnapshot,gameOverState,commerceDeals,commerceSeq,\n   onlineBotDriverIndex:onlineLegacyBotDriverIndex\n };\n}")
rep(" recruitSnapshot=r.recruitSnapshot||null;gameOverState=r.gameOverState||null;commerceDeals=r.commerceDeals||[];commerceSeq=r.commerceSeq||1;",
" recruitSnapshot=r.recruitSnapshot||null;gameOverState=r.gameOverState||null;commerceDeals=r.commerceDeals||[];commerceSeq=r.commerceSeq||1;onlineLegacyBotDriverIndex=Number.isInteger(r.onlineBotDriverIndex)?r.onlineBotDriverIndex:null;")
rep("function onlineLegacyCanExecuteBot(){\n return !!(G&&G.online&&G.online.legacySync&&Number.isInteger(G.online.myPlayerIndex)&&G.players[G.online.myPlayerIndex]&&!G.players[G.online.myPlayerIndex].bot);\n}",
"function onlineLegacyCanExecuteBot(){\n return !!(G&&G.online&&G.online.legacySync&&Number.isInteger(G.online.myPlayerIndex)&&G.players[G.online.myPlayerIndex]&&!G.players[G.online.myPlayerIndex].bot&&onlineLegacyBotDriverIndex===G.online.myPlayerIndex);\n}")
rep(" divinationState=null;recruitSnapshot=null;gameOverState=null;commerceDeals=[];commerceSeq=1;",
" divinationState=null;recruitSnapshot=null;gameOverState=null;commerceDeals=[];commerceSeq=1;onlineLegacyBotDriverIndex=null;")
rep(" if(G.players[G.active]&&G.players[G.active].bot)return onlineLegacyCanExecuteBot();\n return true;",
" if(G.players[G.active]&&G.players[G.active].bot){\n   const priority=battle?currentPriorityPlayer():null;\n   return onlineLegacyCanExecuteBot()||priority===me;\n }\n return G.active===me;")
rep(" const start=canTurn&&G.phase==='start',recruiting=canTurn&&G.phase==='recruit',playing=canTurn&&G.phase==='play',oracleRoll=canTurn&&G.phase==='oracleRoll';",
" const start=canTurn&&G.phase==='start'&&!paidDrawState&&!goldReaction,recruiting=canTurn&&G.phase==='recruit',playing=canTurn&&G.phase==='play',oracleRoll=canTurn&&G.phase==='oracleRoll';")
rep("   const activePlayer=G.players&&G.players[G.active];\n   if(!activePlayer||!activePlayer.bot)onlineLegacyMaybePush();",
"   if(G.players&&G.players[G.active]&&!G.players[G.active].bot)onlineLegacyBotDriverIndex=null;\n   onlineLegacyMaybePush();")
rep("queueBot=function(reason){\n if(G&&G.online&&G.online.legacySync&&G.players[G.active]&&G.players[G.active].bot&&!onlineLegacyCanExecuteBot())return;\n return onlineLegacyBaseQueueBot(reason);\n};",
"queueBot=function(reason){\n if(G&&G.online&&G.online.legacySync&&G.players[G.active]&&G.players[G.active].bot){\n   if(onlineLegacyBotDriverIndex===null&&!onlineLegacyApplying&&Number.isInteger(G.online.myPlayerIndex)){onlineLegacyBotDriverIndex=G.online.myPlayerIndex;onlineLegacyMaybePush()}\n   if(!onlineLegacyCanExecuteBot())return;\n }\n return onlineLegacyBaseQueueBot(reason);\n};")
rep(" // Une synchro distante ne relance pas un bot partiellement exécuté.\n if(battle)resumeBattleTimer();\n if(battle)resumeBattleTimer();",
" // Une synchro distante reste passive : elle affiche l'état publié sans relancer le moteur bot.\n if(battle){clearInterval(battleTick);clearTimeout(botReactionTimer);renderBattle();}")
rep("function queueBotReaction(){\n clearTimeout(botReactionTimer);\n if(!battle)return;",
"function queueBotReaction(){\n clearTimeout(botReactionTimer);\n if(!battle)return;\n if(G&&G.online&&G.online.legacySync&&!onlineLegacyOwnsBattlePriority())return;")

p.write_text(s)
