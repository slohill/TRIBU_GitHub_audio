from pathlib import Path
p=Path('index.html')
s=p.read_text(encoding='utf-8')

old="""function onlineLegacyIsDriver(){return !!(G&&G.online&&G.online.legacySync&&G.online.myPlayerIndex===onlineLegacyDriverIndex())}"""
new="""function onlineLegacyIsDriver(){return !!(G&&G.online&&G.online.legacySync&&G.online.myPlayerIndex===onlineLegacyDriverIndex())}\nfunction onlineLegacyCanExecuteBot(){\n return !!(G&&G.online&&G.online.legacySync&&Number.isInteger(G.online.myPlayerIndex)&&G.players[G.online.myPlayerIndex]&&!G.players[G.online.myPlayerIndex].bot);\n}\nfunction onlineLegacyOwnsBattlePriority(){\n if(!G||!G.online||!G.online.legacySync||!battle)return true;\n const priority=currentPriorityPlayer();\n if(!Number.isInteger(priority)||!G.players[priority])return false;\n if(G.players[priority].bot)return onlineLegacyCanExecuteBot();\n return priority===G.online.myPlayerIndex;\n}"""
assert old in s
s=s.replace(old,new,1)

old=""" if(G.players[G.active]&&G.players[G.active].bot)return onlineLegacyIsDriver();\n return true;"""
new=""" if(G.players[G.active]&&G.players[G.active].bot)return onlineLegacyCanExecuteBot();\n return true;"""
assert old in s
s=s.replace(old,new,1)

old=""" if(onlineLegacyIsDriver())queueBot('synchronisation Online');"""
new=""" if(onlineLegacyCanExecuteBot())queueBot('synchronisation Online');"""
assert old in s
s=s.replace(old,new,1)

old=""" if(onlineLegacyIsDriver())queueBot('état Online reçu');"""
new=""" if(onlineLegacyCanExecuteBot())queueBot('état Online reçu');\n if(battle)resumeBattleTimer();"""
assert old in s
s=s.replace(old,new,1)

old="""queueBot=function(reason){\n if(G&&G.online&&G.online.legacySync&&!onlineLegacyIsDriver())return;\n return onlineLegacyBaseQueueBot(reason);\n};"""
new="""queueBot=function(reason){\n if(G&&G.online&&G.online.legacySync&&G.players[G.active]&&G.players[G.active].bot&&!onlineLegacyCanExecuteBot())return;\n return onlineLegacyBaseQueueBot(reason);\n};"""
assert old in s
s=s.replace(old,new,1)

old="""function onlineLegacyEnsureBotProgress(){\n if(!G||!G.online||!G.online.legacySync||!onlineLegacyIsDriver())return;"""
new="""function onlineLegacyEnsureBotProgress(){\n if(!G||!G.online||!G.online.legacySync||!onlineLegacyCanExecuteBot())return;"""
assert old in s
s=s.replace(old,new,1)

old="""  battleTick=setInterval(()=>{\n    if(!battle)return;\n    battle.seconds--;\n    renderBattle();\n    if(battle.seconds<=0) passPriority();\n  },1000);"""
new="""  if(onlineLegacyOwnsBattlePriority())battleTick=setInterval(()=>{\n    if(!battle)return;\n    battle.seconds--;\n    renderBattle();\n    if(battle.seconds<=0) passPriority();\n  },1000);"""
assert old in s
s=s.replace(old,new,1)

old="""function resumeBattleTimer(){\n clearInterval(battleTick);if(!battle)return;\n if(!isHotseatMode())battleTick=setInterval(()=>{if(!battle)return;battle.seconds--;renderBattle();if(battle.seconds<=0)passPriority()},1000);\n showBattle();renderBattle();\n if(!isHotseatMode())prepareCurrentBattleReaction();\n}"""
new="""function resumeBattleTimer(){\n clearInterval(battleTick);if(!battle)return;\n if(!isHotseatMode()&&onlineLegacyOwnsBattlePriority())battleTick=setInterval(()=>{if(!battle)return;battle.seconds--;renderBattle();if(battle.seconds<=0)passPriority()},1000);\n showBattle();renderBattle();\n if(!isHotseatMode()&&onlineLegacyOwnsBattlePriority())prepareCurrentBattleReaction();\n}"""
assert old in s
s=s.replace(old,new,1)

p.write_text(s,encoding='utf-8')
print('patched bot execution and battle timer ownership')
