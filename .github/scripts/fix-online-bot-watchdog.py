from pathlib import Path
p=Path('index.html')
s=p.read_text(encoding='utf-8')
old="""const onlineLegacyBaseQueueBot=queueBot;
queueBot=function(reason){
 if(G&&G.online&&G.online.legacySync&&!onlineLegacyIsDriver())return;
 return onlineLegacyBaseQueueBot(reason);
};
"""
new="""const onlineLegacyBaseQueueBot=queueBot;
queueBot=function(reason){
 if(G&&G.online&&G.online.legacySync&&!onlineLegacyIsDriver())return;
 return onlineLegacyBaseQueueBot(reason);
};
// Filet de sécurité Online : le navigateur conducteur doit toujours relancer
// le moteur original lorsqu'un bot devient joueur actif. Cela couvre les cas où
// le passage de tour arrive par synchronisation distante et où aucun timer bot
// local n'était encore armé.
let onlineLegacyBotWatchdog=null;
function onlineLegacyEnsureBotProgress(){
 if(!G||!G.online||!G.online.legacySync||!onlineLegacyIsDriver())return;
 if(!G.players[G.active]||!G.players[G.active].bot)return;
 if(gameOverState||battle||shadowState||paidDrawState||goldReaction||oracleNoticeState||dragonSixState||dragonPublicState||dragonCurseState||caravanState||divinationState)return;
 if(botTimer)return;
 onlineLegacyBaseQueueBot('filet de sécurité Online bot');
}
function onlineLegacyStartBotWatchdog(){
 if(onlineLegacyBotWatchdog)return;
 onlineLegacyBotWatchdog=setInterval(onlineLegacyEnsureBotProgress,900);
}
onlineLegacyStartBotWatchdog();
"""
if old not in s:
    raise SystemExit('queueBot wrapper anchor not found')
s=s.replace(old,new,1)
# Also explicitly kick after receiving a canonical snapshot.
s=s.replace("if(onlineLegacyIsDriver())queueBot('état Online reçu');","if(onlineLegacyIsDriver()){queueBot('état Online reçu');setTimeout(onlineLegacyEnsureBotProgress,1200);}",1)
p.write_text(s,encoding='utf-8')
print('bot watchdog patch applied')
