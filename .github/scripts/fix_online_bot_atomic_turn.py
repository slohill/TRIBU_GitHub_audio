from pathlib import Path
p=Path('index.html')
s=p.read_text(encoding='utf-8')

def rep(old,new,label):
    global s
    if old not in s:
        raise SystemExit('pattern missing: '+label)
    s=s.replace(old,new,1)

# Pendant une séquence de bots, ne publie plus chaque render/phase intermédiaire.
# Le moteur original exécute toute la chaîne localement et ne publie qu'au retour
# vers un joueur humain. Cela évite de perdre les timers/callbacks locaux des bots.
rep("render=function(){\n onlineLegacyBaseRender();\n if(G&&G.online&&G.online.legacySync){onlineLegacyLockControls();onlineLegacyMaybePush()}\n};",
"render=function(){\n onlineLegacyBaseRender();\n if(G&&G.online&&G.online.legacySync){\n   onlineLegacyLockControls();\n   const activePlayer=G.players&&G.players[G.active];\n   if(!activePlayer||!activePlayer.bot)onlineLegacyMaybePush();\n }\n};", 'render sync')

# Une réception distante ne doit jamais démarrer/reprendre un bot : seul le navigateur
# qui vient localement de céder le tour au premier bot exécute la chaîne complète.
rep(" if(onlineLegacyCanExecuteBot())queueBot('synchronisation Online');", " // Les bots ne sont pas démarrés depuis un bootstrap distant.", 'bootstrap bot')
rep(" if(onlineLegacyCanExecuteBot()){queueBot('état Online reçu');setTimeout(onlineLegacyEnsureBotProgress,1200);}", " // Une synchro distante ne relance pas un bot partiellement exécuté.\n if(battle)resumeBattleTimer();", 'remote apply bot')

# Désactive le watchdog multi-navigateurs : il créait plusieurs moteurs bot concurrents.
rep("function onlineLegacyStartBotWatchdog(){\n if(onlineLegacyBotWatchdog)return;\n onlineLegacyBotWatchdog=setInterval(onlineLegacyEnsureBotProgress,900);\n}\nonlineLegacyStartBotWatchdog();",
"function onlineLegacyStartBotWatchdog(){\n // Désactivé : un tour bot Online est exécuté atomiquement par le navigateur\n // qui a terminé le dernier tour humain, sans concurrence entre clients.\n}\n", 'watchdog disable')

p.write_text(s,encoding='utf-8')
print('patched atomic online bot turns')
