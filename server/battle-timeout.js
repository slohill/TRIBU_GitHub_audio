'use strict';
// Server owns elapsed time and a single execution lease. The legacy client
// still performs Pass/resolveBattle; no battle rules are duplicated here.
function createBattleTimeout({publish,connected,now=Date.now}){
 const clocks=new WeakMap();let sequence=0;
 function paused(room){
  const r=room.legacySnapshot?.rule||{},g=room.legacySnapshot?.g||{};
  return !!(r.commercePaused||r.commerceEditors||r.choiceState||r.agentModalState||r.divinationState||r.caravanState||
   r.egnoState||r.shadowState||r.portalMode||r.goldReaction||r.paidDrawState||r.oracleState||r.oracleNoticeState||
   r.dragonRichState||r.dragonCurseState||r.dragonPublicState||r.dragonSixState||r.gameOverState||
   r.battle?.elfChoice||g.allianceLoss||g.guildCompletion||g.pendingGuildFury||g.noblesseRevolts?.length||
   g.morcattAuction&&g.morcattAuction.stage!=='finished');
 }
 function sync(room){
  const r=room.legacySnapshot?.rule,b=r?.battle,time=now();
  if(!b||b.kind==='seaChoice'||b.environmentResolved||!Array.isArray(b.priorityOrder)||!b.priorityOrder.length){
   clocks.delete(room);if(r){delete r.battleClock;delete r.battleTimeout}return null;
  }
  const g=room.legacySnapshot.g;
  const key=JSON.stringify([r.turnEpoch,g.active,b.kind,b.target,b.attacker,b.defender,b.priorityOrder,b.priorityIndex,b.consecutivePasses,b.stack]);
  let c=clocks.get(room);
  if(!c||c.key!==key){c={key,remaining:Math.max(0,Number(b.seconds)||0)*1000,deadline:null,lease:null,lastExecutor:null};clocks.set(room,c)}
  if(paused(room)){
   if(c.deadline!==null)c.remaining=Math.max(0,c.deadline-time);
   c.deadline=null;c.lease=null;delete r.battleTimeout;
  }else if(c.deadline===null)c.deadline=time+c.remaining;
  r.battleClock={deadline:c.deadline,remaining:c.remaining,serverTime:time};
  if(c.lease)r.battleTimeout=c.lease;else delete r.battleTimeout;
  delete r.battleTimeoutResolved;
  return c;
 }
 function tick(room){
  if(!room.legacyMode||!room.legacySnapshot)return false;
  const previous=room.legacySnapshot.rule.battleTimeout?.id,c=sync(room),time=now();
  if(previous&&!c?.lease){room.legacyRevision=(room.legacyRevision||0)+1;publish(room);return true}
  if(!c||c.deadline===null||time<c.deadline||c.lease&&time<c.lease.retryAt)return false;
  const b=room.legacySnapshot.rule.battle,priority=b.priorityOrder[b.priorityIndex];
  const peers=connected(room).filter(i=>!room.legacySnapshot.g.players[i]?.bot);
  if(!peers.length)return false;
  const executor=peers.find(i=>i!==priority&&i!==c.lastExecutor)??peers.find(i=>i!==c.lastExecutor)??peers[0];
  c.lastExecutor=executor;c.lease={id:'battle-timeout-'+(++sequence),executor,retryAt:time+5000};
  room.legacySnapshot.rule.battleTimeout=c.lease;
  room.legacyRevision=(room.legacyRevision||0)+1;publish(room);return true;
 }
 function accept(room,actor,snapshot){
  const c=clocks.get(room),lease=c?.lease;
  if(lease){
   if(paused(room)||actor!==lease.executor||snapshot.rule.battleTimeoutResolved!==lease.id)return false;
   const old=room.legacySnapshot.rule.battle,next=snapshot.rule.battle;
   if(next&&next.target===old.target&&next.attacker===old.attacker&&
     Number(next.consecutivePasses)!==Number(old.consecutivePasses||0)+1)return false;
  }
  delete snapshot.rule.battleClock;delete snapshot.rule.battleTimeout;delete snapshot.rule.battleTimeoutResolved;
  if(c&&lease){c.lease=null;clocks.delete(room)}
  return true;
 }
 return {sync,tick,accept,paused};
}
module.exports={createBattleTimeout};
