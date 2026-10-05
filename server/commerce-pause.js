'use strict';
// Server-owned editor leases. Closing one of several editors cannot release the others.
function createCommercePause({emit,changed,now=Date.now}){
 const leases=new WeakMap();
 const editors=room=>{if(!leases.has(room))leases.set(room,new Set());return leases.get(room)};
 const frozen=room=>editors(room).size>0&&!!room.legacySnapshot?.rule?.battle;
 const clockRunning=room=>{const r=room.legacySnapshot?.rule||{};return r.battle&&!r.divinationState&&!r.caravanState&&!r.egnoState&&!r.shadowState&&!r.portalMode&&!r.choiceState&&!r.agentModalState&&!r.goldReaction};
 function publish(room){const snap=room.legacySnapshot;if(!snap)return;const paused=frozen(room);snap.rule.commercePaused=paused;room.legacyRevision=(room.legacyRevision||0)+1;emit(room,'commercePause',{paused,editors:editors(room).size,seconds:snap.rule.battle?.seconds??null});changed(room)}
 function set(room,id,open){const set=editors(room),was=frozen(room);if(open)set.add(id);else set.delete(id);const paused=frozen(room),b=room.legacySnapshot?.rule?.battle;
   if(!was&&paused&&b&&Number.isFinite(b.seconds)&&room.battleClockAt){const elapsed=Math.max(0,Math.floor((now()-room.battleClockAt)/1000));b.seconds=Math.max(0,b.seconds-elapsed)}
   if(was&&!paused)room.battleClockAt=clockRunning(room)?now():null;publish(room);
 }
 function stable(snapshot){const copy=JSON.parse(JSON.stringify(snapshot));delete copy.public;delete copy.g.log;delete copy.g.publicLog;delete copy.g.online;
   // Exchanges may transfer cards and gold, but cannot play cards or change the battle.
   for(const p of copy.g.players||[]){delete p.hand;delete p.gold}
   delete copy.rule.commerceDeals;delete copy.rule.commerceSeq;delete copy.rule.commercePaused;
   delete copy.rule.onlineSfxSeq;delete copy.rule.onlineSfxEvents;
   if(copy.rule.battle)delete copy.rule.battle.seconds;
   return JSON.stringify(copy);
 }
 function accept(room,snapshot){const current=room.legacySnapshot;if(frozen(room)){
   if(!snapshot?.g||!snapshot?.rule||stable(snapshot)!==stable(current))return false;
   // A trade conserves the total gold and the multiset of cards held by all players.
   const resources=s=>({gold:s.g.players.reduce((n,p)=>n+(p.gold||0),0),cards:s.g.players.flatMap(p=>p.hand||[]).sort((a,b)=>a-b)});
   if(JSON.stringify(resources(snapshot))!==JSON.stringify(resources(current)))return false;
   snapshot.rule.battle.seconds=current.rule.battle.seconds;
 }
 if(snapshot.rule)snapshot.rule.commercePaused=editors(room).size>0&&!!snapshot.rule.battle;
 return true;
 }
 return {set,leave(room,id){if(editors(room).has(id))set(room,id,false)},accept,committed(room){if(!frozen(room))room.battleClockAt=clockRunning(room)?now():null},frozen};
}
module.exports={createCommercePause};
