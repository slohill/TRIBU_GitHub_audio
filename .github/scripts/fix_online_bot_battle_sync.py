from pathlib import Path
p=Path('index.html')
s=p.read_text(encoding='utf-8')

def rep(old,new,label):
    global s
    if old not in s:
        raise SystemExit('pattern missing: '+label)
    s=s.replace(old,new,1)

rep("function onlineLegacyIsDriver(){return !!(G&&G.online&&G.online.legacySync&&G.online.myPlayerIndex===onlineLegacyDriverIndex())}",
"function onlineLegacyIsDriver(){return !!(G&&G.online&&G.online.legacySync&&G.online.myPlayerIndex===onlineLegacyDriverIndex())}\nfunction onlineLegacyCanExecuteBot(){\n return !!(G&&G.online&&G.online.legacySync&&Number.isInteger(G.online.myPlayerIndex)&&G.players[G.online.myPlayerIndex]&&!G.players[G.online.myPlayerIndex].bot);\n}\nfunction onlineLegacyOwnsBattlePriority(){\n if(!G||!G.online||!G.online.legacySync||!battle)return true;\n const priority=currentPriorityPlayer();\n if(!Number.isInteger(priority)||!G.players[priority])return false;\n if(G.players[priority].bot)return onlineLegacyCanExecuteBot();\n return priority===G.online.myPlayerIndex;\n}", 'helpers')
rep("if(G.players[G.active]&&G.players[G.active].bot)return onlineLegacyIsDriver();", "if(G.players[G.active]&&G.players[G.active].bot)return onlineLegacyCanExecuteBot();", 'publish bot')
rep("if(onlineLegacyIsDriver())queueBot('synchronisation Online');", "if(onlineLegacyCanExecuteBot())queueBot('synchronisation Online');", 'bootstrap bot')
rep("if(onlineLegacyIsDriver()){queueBot('état Online reçu');setTimeout(onlineLegacyEnsureBotProgress,1200);}", "if(onlineLegacyCanExecuteBot()){queueBot('état Online reçu');setTimeout(onlineLegacyEnsureBotProgress,1200);}\n if(battle)resumeBattleTimer();", 'apply bot/battle')
rep("queueBot=function(reason){\n if(G&&G.online&&G.online.legacySync&&!onlineLegacyIsDriver())return;\n return onlineLegacyBaseQueueBot(reason);\n};", "queueBot=function(reason){\n if(G&&G.online&&G.online.legacySync&&G.players[G.active]&&G.players[G.active].bot&&!onlineLegacyCanExecuteBot())return;\n return onlineLegacyBaseQueueBot(reason);\n};", 'queue wrapper')
rep("function onlineLegacyEnsureBotProgress(){\n if(!G||!G.online||!G.online.legacySync||!onlineLegacyIsDriver())return;", "function onlineLegacyEnsureBotProgress(){\n if(!G||!G.online||!G.online.legacySync||!onlineLegacyCanExecuteBot())return;", 'watchdog')
rep("  battleTick=setInterval(()=>{\n    if(!battle)return;\n    battle.seconds--;\n    renderBattle();\n    if(battle.seconds<=0) passPriority();\n  },1000);", "  if(onlineLegacyOwnsBattlePriority())battleTick=setInterval(()=>{\n    if(!battle)return;\n    battle.seconds--;\n    renderBattle();\n    if(battle.seconds<=0) passPriority();\n  },1000);", 'start battle timer')
rep("function resumeBattleTimer(){\n clearInterval(battleTick);if(!battle)return;\n if(!isHotseatMode())battleTick=setInterval(()=>{if(!battle)return;battle.seconds--;renderBattle();if(battle.seconds<=0)passPriority()},1000);\n showBattle();renderBattle();\n if(!isHotseatMode())prepareCurrentBattleReaction();\n}", "function resumeBattleTimer(){\n clearInterval(battleTick);if(!battle)return;\n if(!isHotseatMode()&&onlineLegacyOwnsBattlePriority())battleTick=setInterval(()=>{if(!battle)return;battle.seconds--;renderBattle();if(battle.seconds<=0)passPriority()},1000);\n showBattle();renderBattle();\n if(!isHotseatMode()&&onlineLegacyOwnsBattlePriority())prepareCurrentBattleReaction();\n}", 'resume battle timer')
p.write_text(s,encoding='utf-8')
print('patched bot execution and battle timer ownership')
