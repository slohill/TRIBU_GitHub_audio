from pathlib import Path

p=Path('index.html')
s=p.read_text(encoding='utf-8')

old="let onlineLegacyRevision=0,onlineLegacyApplying=false,onlineLegacyLastDigest='',onlineLegacyPushTimer=null,onlineLegacyBotDriverIndex=null,onlineLegacyBattleViewSeconds=null,onlineLegacyGoldViewSeconds=null,onlineLegacyGoldTickRender=false,onlineLegacyPriorityWasActive=false,onlineLegacyPriorityTrackedActor=null,onlineLegacyPriorityTerminalPending=false;"
new="let onlineLegacyRevision=0,onlineLegacyApplying=false,onlineLegacyLastDigest='',onlineLegacyPushTimer=null,onlineLegacyBotDriverIndex=null,onlineLegacyBattleViewSeconds=null,onlineLegacyGoldViewSeconds=null,onlineLegacyGoldTickRender=false,onlineLegacyPriorityWasActive=false,onlineLegacyPriorityTrackedActor=null,onlineLegacyPriorityTerminalPending=false,onlineLegacyRecoveryPending=false,onlineLegacyRecoveryAttempted=false;"
assert old in s
s=s.replace(old,new,1)

old="if(!G||!G.online||!G.online.legacySync||onlineLegacyApplying||onlineLegacyPriorityTerminalPending||!onlineSocket)return false;"
new="if(!G||!G.online||!G.online.legacySync||onlineLegacyApplying||onlineLegacyPriorityTerminalPending||onlineLegacyRecoveryPending||!onlineSocket)return false;"
assert old in s
s=s.replace(old,new,1)

old="const cardPause=priorityCardResolutionActive();"
new="const cardPause=priorityCardResolutionActive()||onlineLegacyRecoveryPending;"
assert old in s
s=s.replace(old,new,1)

old="const map=$('map');if(map)map.style.pointerEvents=onlineLegacyPriorityTerminalPending?'none':'';\n const n=$('status');if(n&&!n.querySelector('.onlineLegacyNotice'))n.insertAdjacentHTML('beforeend','<div class=\"botNotice onlineLegacyNotice\">🌐 Online — moteur original TRIBU synchronisé.</div>');"
new="const map=$('map');if(map)map.style.pointerEvents=(onlineLegacyPriorityTerminalPending||onlineLegacyRecoveryPending)?'none':'';\n const n=$('status');if(n){let notice=n.querySelector('.onlineLegacyNotice');if(!notice){n.insertAdjacentHTML('beforeend','<div class=\"botNotice onlineLegacyNotice\">🌐 Online — moteur original TRIBU synchronisé.</div>');notice=n.querySelector('.onlineLegacyNotice')}if(notice)notice.textContent=onlineLegacyRecoveryPending?'🌐 Resynchronisation de la partie…':'🌐 Online — moteur original TRIBU synchronisé.';}"
assert old in s
s=s.replace(old,new,1)

old="function onlineAck(action,payload){return connectOnline().then(socket=>new Promise((resolve,reject)=>socket.emit(action,payload,res=>{if(res&&res.ok){resolve(res);return}const err=new Error(res&&res.error||'Erreur serveur.');if(res&&res.current)err.current=res.current;reject(err)})))}\nfunction onlineError(err){alert(err&&err.message?err.message:String(err))}"
new="""function onlineAck(action,payload){return connectOnline().then(socket=>new Promise((resolve,reject)=>socket.emit(action,payload,res=>{if(res&&res.ok){resolve(res);return}const err=new Error(res&&res.error||'Erreur serveur.');if(res&&res.current)err.current=res.current;reject(err)})))}
function onlineLegacyCanAutoRecover(err){
 return !!(err&&err.message==='Synchronisation complète indisponible.'&&G&&G.online&&G.online.legacySync&&!onlineLegacyRecoveryPending&&!onlineLegacyRecoveryAttempted&&onlineResumeRead());
}
async function onlineLegacyRecoverSession(){
 const saved=onlineResumeRead();if(!saved)throw new Error('Aucune reprise de partie disponible.');
 onlineLegacyRecoveryAttempted=true;onlineLegacyRecoveryPending=true;
 clearTimeout(onlineLegacyPushTimer);onlineLegacyPushTimer=null;
 clearInterval(battleTick);clearTimeout(botReactionTimer);clearInterval(paidDrawTick);clearGoldReactionTimer();clearTimeout(botTimer);botTimer=null;botToken++;
 onlineLegacyLockControls();
 try{
   const resumed=await onlineAck('resumeRoom',saved);
   onlineResumeSave(resumed.resume);onlineRoom=resumed.room;onlineSelectedMode=resumed.room.mode;onlineGameState=resumed.game;
   const full=await onlineAck('requestLegacyState',{});
   if(!full||!full.snapshot)throw new Error('Aucun snapshot complet disponible pour reprendre la partie.');
   onlineLegacyRecoveryPending=false;
   if(!G||!G.online||!G.online.legacySync)onlineLegacyBootstrap(full.bootstrap,resumed.game);
   onlineLegacyApply({snapshot:full.snapshot,revision:full.revision,youIndex:full.youIndex});
   onlineLegacyRecoveryAttempted=false;
   return true;
 }catch(e){
   onlineLegacyRecoveryPending=false;onlineLegacyLockControls();throw e;
 }
}
function onlineError(err){
 if(onlineLegacyCanAutoRecover(err)){
   onlineLegacyRecoverSession().catch(recoveryErr=>alert('Synchronisation complète indisponible.\\nLa resynchronisation automatique a échoué : '+(recoveryErr&&recoveryErr.message?recoveryErr.message:String(recoveryErr))+'\\nRechargez la page pour reprendre la partie.'));
   return;
 }
 alert(err&&err.message?err.message:String(err));
}"""
assert old in s
s=s.replace(old,new,1)

# Preserve key invariants.
assert "$('localTestBtn').onclick=()=>{onlinePseudo();launchLegacyMode('2v3',3)};" in s
assert "nav.textContent='Naviguer'" in s
assert "function onlineLegacyPushPriorityTerminalNow(owner)" in s
assert "if(!full||!full.snapshot)throw new Error('Aucun snapshot complet disponible pour reprendre la partie.');" in s

p.write_text(s,encoding='utf-8')
print('Patch récupération automatique Online appliqué.')
