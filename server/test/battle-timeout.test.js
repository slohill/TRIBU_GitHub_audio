const {test}=require('node:test'),assert=require('node:assert/strict');
const {createBattleTimeout}=require('../battle-timeout');
function fixture(){let time=0,published=0;const room={legacyMode:true,legacyRevision:0,legacySnapshot:{g:{active:0,players:[{},{}]},rule:{turnEpoch:1,battle:{kind:'land',target:'A',attacker:0,defender:1,seconds:15,priorityOrder:[1,0],priorityIndex:0,consecutivePasses:0,stack:[]}}}};const api=createBattleTimeout({now:()=>time,connected:()=>[0,1],publish:()=>published++});return {room,api,set:t=>time=t,published:()=>published}}
test('idle tablet deadline grants another connected player a single legacy pass lease',()=>{
 const f=fixture(),r=f.room;f.api.sync(r);f.set(14999);assert(!f.api.tick(r));f.set(15000);assert(f.api.tick(r));
 const lease=r.legacySnapshot.rule.battleTimeout;assert.equal(lease.executor,0);assert(!f.api.tick(r));
 const s=structuredClone(r.legacySnapshot);s.rule.battle.consecutivePasses=1;s.rule.battle.priorityIndex=1;s.rule.battleTimeoutResolved=lease.id;
 assert(!f.api.accept(r,1,structuredClone(s)));assert(f.api.accept(r,0,s));assert(!s.rule.battleTimeout);
 r.legacySnapshot=s;f.api.sync(r);assert.equal(s.rule.battleClock.deadline,30000);
});
test('unresponsive relay is replaced after five seconds; old token rejected',()=>{
 const f=fixture();f.api.sync(f.room);f.set(15000);f.api.tick(f.room);const old=f.room.legacySnapshot.rule.battleTimeout;
 f.set(20000);assert(f.api.tick(f.room));const next=f.room.legacySnapshot.rule.battleTimeout;assert.notEqual(next.id,old.id);assert.equal(next.executor,1);
 const s=structuredClone(f.room.legacySnapshot);s.rule.battleTimeoutResolved=old.id;assert(!f.api.accept(f.room,old.executor,s));
});
test('ordinary snapshots cannot reset elapsed time; card reactions can',()=>{
 const f=fixture();f.api.sync(f.room);f.set(10000);f.api.sync(f.room);assert.equal(f.room.legacySnapshot.rule.battleClock.deadline,15000);
 f.room.legacySnapshot.rule.battle.stack.push({cardId:1});f.api.sync(f.room);assert.equal(f.room.legacySnapshot.rule.battleClock.deadline,25000);
});
for(const flag of ['commercePaused','choiceState','oracleState','goldReaction','shadowState','agentModalState']){
 test(flag+' suspends timeout and preserves remaining time',()=>{
  const f=fixture(),r=f.room.legacySnapshot.rule;f.api.sync(f.room);f.set(5000);r[flag]=true;f.api.sync(f.room);
  f.set(60000);assert(!f.api.tick(f.room));assert.equal(r.battleClock.deadline,null);delete r[flag];f.api.sync(f.room);
  assert.equal(r.battleClock.deadline,70000);f.set(69999);assert(!f.api.tick(f.room));
 });
}
