'use strict';
// Server-owned editor leases. Closing one of several editors cannot release the others.
function createCommercePause({emit,now=Date.now}){
 const leases=new WeakMap();
 const editors=room=>{if(!leases.has(room))leases.set(room,new Set());return leases.get(room)};
 const frozen=room=>editors(room).size>0&&!!(room.legacySnapshot?.rule?.battle||room.legacySnapshot?.rule?.goldReaction);
 const clockRunning=room=>{const r=room.legacySnapshot?.rule||{};return r.battle&&!r.divinationState&&!r.caravanState&&!r.egnoState&&!r.shadowState&&!r.portalMode&&!r.choiceState&&!r.agentModalState&&!r.goldReaction};
 function publish(room,was){const snap=room.legacySnapshot;if(!snap)return;const paused=frozen(room);snap.rule.commercePaused=paused;snap.rule.commerceEditors=editors(room).size;
 emit(room,'commercePause',{paused,editors:editors(room).size,...(was!==paused?{seconds:snap.rule.battle?.seconds??null,goldSeconds:snap.rule.goldReaction?.seconds??null}:{})});
 }
 function set(room,id,open){const set=editors(room),was=frozen(room);if(set.has(id)===!!open)return;if(open)set.add(id);else set.delete(id);const paused=frozen(room),b=room.legacySnapshot?.rule?.battle;
   if(!was&&paused&&b&&Number.isFinite(b.seconds)&&room.battleClockAt){const elapsed=Math.max(0,Math.floor((now()-room.battleClockAt)/1000));b.seconds=Math.max(0,b.seconds-elapsed)}
   const g=room.legacySnapshot?.rule?.goldReaction;
   if(!was&&paused&&g&&!g.pausedByCard&&Number.isFinite(g.seconds)&&room.goldClockAt!=null)g.seconds=Math.max(0,g.seconds-Math.max(0,Math.floor((now()-room.goldClockAt)/1000)));
   if(was&&!paused){room.battleClockAt=clockRunning(room)?now():null;room.goldClockAt=g&&!g.pausedByCard?now():null}publish(room,was);
 }
 // Trading freezes clocks, not the legacy actions or their resolutions.
 function accept(room,snapshot){
 const current=room.legacySnapshot?.rule||{},next=snapshot?.rule;
 if(!next)return false;
 if(frozen(room)){
   // Preserve elapsed time only while the same reaction is still in progress.
   const sameReaction=(a,b,keys)=>a&&b&&keys.every(k=>JSON.stringify(a[k])===JSON.stringify(b[k]));
   if(sameReaction(current.battle,next.battle,['attacker','defender','target','priorityIndex','consecutivePasses','stack']))next.battle.seconds=current.battle.seconds;
   if(sameReaction(current.goldReaction,next.goldReaction,['receiver','amount','source','turnEpoch','pausedByCard']))next.goldReaction.seconds=current.goldReaction.seconds;
 }
 next.commerceEditors=editors(room).size;
 next.commercePaused=editors(room).size>0&&!!(next.battle||next.goldReaction);
 return true;
 }
 return {set,leave(room,id){if(editors(room).has(id))set(room,id,false)},accept,committed(room){if(!frozen(room)){room.battleClockAt=clockRunning(room)?now():null;const g=room.legacySnapshot?.rule?.goldReaction;room.goldClockAt=g&&!g.pausedByCard?now():null}},frozen};
}
module.exports={createCommercePause};
