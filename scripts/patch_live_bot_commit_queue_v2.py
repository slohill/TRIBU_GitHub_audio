from pathlib import Path
p=Path('index.html');s=p.read_text()
old=""" }).catch(err=>{
   onlineLegacyLastDigest='';
   if(err&&err.current)onlineLegacyApply(err.current);else onlineError(err);
 }).finally(()=>{
   onlineLegacyBotCommitBusy=false;
   if(onlineLegacyBotCommitQueued){onlineLegacyBotCommitQueued=false;onlineLegacyPushLiveBot()}
 });"""
new=""" }).catch(err=>{
   onlineLegacyLastDigest='';
   // Pendant un tour bot, le conducteur continue d'exécuter le moteur original.
   // Ne jamais lui réappliquer un snapshot serveur intermédiaire : les autres
   // écrans le reçoivent, mais le conducteur garde sa chaîne locale intacte.
   if(!(G&&G.players[G.active]&&G.players[G.active].bot)){
     if(err&&err.current)onlineLegacyApply(err.current);else onlineError(err);
   }else if(!(err&&err.current))onlineError(err);
 }).finally(()=>{
   onlineLegacyBotCommitBusy=false;
   if(onlineLegacyBotCommitQueued){onlineLegacyBotCommitQueued=false;onlineLegacyPushLiveBot()}
 });"""
# only replace the live-bot catch (the first occurrence after function marker)
pos=s.index('function onlineLegacyPushLiveBot()')
idx=s.index(old,pos)
s=s[:idx]+s[idx:].replace(old,new,1)
p.write_text(s)
