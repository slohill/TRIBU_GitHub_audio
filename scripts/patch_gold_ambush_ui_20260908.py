from pathlib import Path
p=Path('index.html')
s=p.read_text()

# 1) Battle banner above deck/discard.
s=s.replace(".battleBanner{position:absolute;left:50%;top:10px;transform:translateX(-50%);z-index:40;", ".battleBanner{position:absolute;left:50%;top:10px;transform:translateX(-50%);z-index:180;", 1)

# 2) Oracle panels light blue-grey, including Oracle notice text.
s=s.replace(".oracleMini{height:100%;width:82px;min-width:82px;padding:3px 4px;border:2px solid #727d77;border-radius:7px;background:#18201d;color:#d4d8d6;", ".oracleMini{height:100%;width:82px;min-width:82px;padding:3px 4px;border:2px solid #8799a3;border-radius:7px;background:#bcc8ce;color:#1d2930;", 1)
needle=".oracleMini small{font-size:7px;line-height:1;opacity:.85}.oracleMini b{font-size:9px;line-height:1.05;max-width:100%;overflow:hidden;text-overflow:ellipsis}"
assert needle in s
s=s.replace(needle, needle+"\n#oracleNoticeText{background:#bcc8ce;color:#1d2930;border:1px solid #8799a3;border-radius:8px;padding:10px}",1)

# 3) Gold display can use a spectator-only visual countdown.
old="""   let gh='<b>⚠️ Gain d’Or en attente — '+goldReaction.seconds+' s</b><br>'+p(goldReaction.receiver).name+' doit recevoir <b>'+goldReaction.amount+' Or</b> ('+goldReaction.source+').';"""
new="""   const goldSeconds=(G&&G.online&&G.online.legacySync&&!onlineLegacyOwnsGoldTimer()&&onlineLegacyGoldViewSeconds!==null)?onlineLegacyGoldViewSeconds:goldReaction.seconds;
   let gh='<b>⚠️ Gain d’Or en attente — '+goldSeconds+' s</b><br>'+p(goldReaction.receiver).name+' doit recevoir <b>'+goldReaction.amount+' Or</b> ('+goldReaction.source+').';"""
assert old in s
s=s.replace(old,new,1)

# 4) Hide turn-phase controls for the entire gold reaction window.
old=""" $('recruitBox').classList.toggle('hidden',G.phase!=='recruit');
 $('playBox').classList.toggle('hidden',G.phase!=='play');
 $('oracleBox').classList.toggle('hidden',!['oracleMove','oracleRoll'].includes(G.phase));"""
new=""" $('recruitBox').classList.toggle('hidden',G.phase!=='recruit');
 $('playBox').classList.toggle('hidden',G.phase!=='play');
 $('oracleBox').classList.toggle('hidden',!['oracleMove','oracleRoll'].includes(G.phase));
 if(goldReaction){['startTurn','recruitBox','playBox','oracleBox'].forEach(id=>{const el=$(id);if(el)el.classList.add('hidden')})}"""
assert old in s
s=s.replace(old,new,1)

# 5) Explicit Ambush commit: retry harmless revision conflicts caused by the gold countdown.
old=""" if(G&&G.online&&G.online.legacySync)onlineLegacyPushNow();
 maybeBotAmbush();
}"""
new=""" if(G&&G.online&&G.online.legacySync)onlineLegacyPushGoldReactionNow();
 maybeBotAmbush();
}"""
# only playAmbush occurrence: locate after function name
pos=s.index('function playAmbush(playerIndex)')
idx=s.index(old,pos)
s=s[:idx]+s[idx:].replace(old,new,1)

# 6) Online gold timer ownership / visual spectator timer + robust reaction push.
old_decl="let onlineLegacyRevision=0,onlineLegacyApplying=false,onlineLegacyLastDigest='',onlineLegacyPushTimer=null,onlineLegacyBotDriverIndex=null,onlineLegacyBattleViewSeconds=null;"
new_decl="let onlineLegacyRevision=0,onlineLegacyApplying=false,onlineLegacyLastDigest='',onlineLegacyPushTimer=null,onlineLegacyBotDriverIndex=null,onlineLegacyBattleViewSeconds=null,onlineLegacyGoldViewSeconds=null;"
assert old_decl in s
s=s.replace(old_decl,new_decl,1)

anchor="""function onlineLegacyOwnsBattlePriority(){
 if(!G||!G.online||!G.online.legacySync||!battle)return true;"""
insert="""function onlineLegacyOwnsGoldTimer(){
 if(!G||!G.online||!G.online.legacySync||!goldReaction)return true;
 const me=G.online.myPlayerIndex;
 if(!Number.isInteger(me)||!G.players[me]||G.players[me].bot)return false;
 if(G.players[G.active]&&G.players[G.active].bot)return onlineLegacyCanExecuteBot();
 return G.active===me;
}
function onlineLegacyStartGoldViewTimer(){
 clearGoldReactionTimer();
 if(!goldReaction){onlineLegacyGoldViewSeconds=null;return}
 onlineLegacyGoldViewSeconds=Math.max(0,Number(goldReaction.seconds)||0);
 goldReactionTick=setInterval(()=>{
   if(!goldReaction){clearGoldReactionTimer();onlineLegacyGoldViewSeconds=null;return}
   if(goldReaction.pausedByCard)return;
   onlineLegacyGoldViewSeconds=Math.max(0,onlineLegacyGoldViewSeconds-1);
   render();
   if(onlineLegacyGoldViewSeconds<=0)clearGoldReactionTimer();
 },1000);
}
function onlineLegacyResumeGoldView(){
 clearGoldReactionTimer();
 if(!goldReaction){onlineLegacyGoldViewSeconds=null;return}
 if(onlineLegacyOwnsGoldTimer()){onlineLegacyGoldViewSeconds=null;startGoldReactionTimer()}
 else onlineLegacyStartGoldViewTimer();
}
function onlineLegacyOwnsBattlePriority(){
 if(!G||!G.online||!G.online.legacySync||!battle)return true;"""
assert anchor in s
s=s.replace(anchor,insert,1)

# Make startGoldReactionTimer respect Online timer ownership.
old="""function startGoldReactionTimer(){
 clearGoldReactionTimer();
 if(!goldReaction)return;
 if(isHotseatMode()){"""
new="""function startGoldReactionTimer(){
 clearGoldReactionTimer();
 if(!goldReaction)return;
 if(G&&G.online&&G.online.legacySync&&!onlineLegacyOwnsGoldTimer()){onlineLegacyStartGoldViewTimer();return}
 if(G&&G.online&&G.online.legacySync)onlineLegacyGoldViewSeconds=null;
 if(isHotseatMode()){"""
assert old in s
s=s.replace(old,new,1)

# Resume gold timer/view after applying a remote canonical snapshot.
old=""" onlineLegacyResumeBattleView();
}"""
new=""" onlineLegacyResumeBattleView();
 onlineLegacyResumeGoldView();
}"""
# replace first occurrence after onlineLegacyApply
pos=s.index('function onlineLegacyApply(packet)')
idx=s.index(old,pos)
s=s[:idx]+s[idx:].replace(old,new,1)

# Add robust gold-reaction push after onlineLegacyPushNow.
anchor="""function onlineLegacyPushBotHandoff(previousActive,previousDriver){"""
helper="""function onlineLegacyPushGoldReactionNow(){
 if(!G||!G.online||!G.online.legacySync||onlineLegacyApplying||!onlineSocket||!goldReaction)return;
 const actorIndex=G.online.myPlayerIndex;if(!Number.isInteger(actorIndex)||!G.players[actorIndex]||G.players[actorIndex].bot)return;
 clearTimeout(onlineLegacyPushTimer);
 const snapshot=onlineLegacySnapshot(),digest=onlineLegacyDigest();
 const localGold=onlineLegacyDecode(snapshot.rule&&snapshot.rule.goldReaction||null);
 const send=(baseRevision,retries)=>onlineAck('legacyCommit',{baseRevision,actorIndex,snapshot}).then(res=>{
   onlineLegacyRevision=Math.max(onlineLegacyRevision,res.revision||0);G.online.revision=onlineLegacyRevision;onlineLegacyLastDigest=digest;
 }).catch(err=>{
   if(err&&err.current&&retries>0&&err.current.snapshot){
     const remote=onlineLegacyDecode(err.current.snapshot),remoteGold=remote&&remote.rule&&remote.rule.goldReaction;
     const sameWindow=remoteGold&&localGold&&remoteGold.amount===localGold.amount&&remoteGold.turnEpoch===localGold.turnEpoch&&remoteGold.turnOwner===localGold.turnOwner;
     if(sameWindow&&Number.isInteger(err.current.revision)){
       onlineLegacyRevision=Math.max(onlineLegacyRevision,err.current.revision);G.online.revision=onlineLegacyRevision;
       return send(onlineLegacyRevision,retries-1);
     }
     onlineLegacyLastDigest='';onlineLegacyApply(err.current);return;
   }
   onlineLegacyLastDigest='';if(err&&err.current)onlineLegacyApply(err.current);else onlineError(err);
 });
 send(onlineLegacyRevision,2);
}
function onlineLegacyPushBotHandoff(previousActive,previousDriver){"""
assert anchor in s
s=s.replace(anchor,helper,1)

# Online lock must also hide phase controls during gold countdown.
old=""" const s=$('startTurn');if(s)s.classList.toggle('hidden',!start);
 if(!mine){['recruitBox','playBox','oracleBox'].forEach(id=>{const el=$(id);if(el)el.classList.add('hidden')})}"""
new=""" const s=$('startTurn');if(s)s.classList.toggle('hidden',!start);
 if(!mine||goldReaction){['recruitBox','playBox','oracleBox'].forEach(id=>{const el=$(id);if(el)el.classList.add('hidden')})}
 if(goldReaction&&s)s.classList.add('hidden')"""
assert old in s
s=s.replace(old,new,1)

p.write_text(s)
