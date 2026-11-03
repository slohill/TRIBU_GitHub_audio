const {test}=require('node:test'),assert=require('node:assert/strict'),R=require('../../assets/corruption-revolts');
test('only 3/4 while already active; after original action, once per event',()=>{
 const s=R.create();assert.equal(R.capture(s,0,3,'before'),null);R.activate(s,2,8);
 for(const n of [1,2,5,6])assert.equal(R.capture(s,0,n,'x'+n),null);
 const t=R.capture(s,0,4,'ogre:1');assert.equal(R.next(s),null);
 assert(R.afterAction(s,t));assert.equal(R.afterAction(s,t),false);assert.equal(R.next(s).target,2);assert.equal(R.next(s),null);
});
test('replacement/reactivation and suppression invalidate old rolls',()=>{
 const s=R.create();R.activate(s,1,8);const old=R.capture(s,0,3,'thief:1');R.replace(s);R.activate(s,1,8);assert.equal(R.afterAction(s,old),false);
 const t=R.capture(s,1,3,'self');assert(R.afterAction(s,t));R.suppress(s);assert.equal(R.next(s),null);assert.equal(R.capture(s,0,4,'later'),null);
});
function fixture(){return {game:{b:{A:{owner:1,units:3},B:{owner:0,units:4}},sea:{U:{fleets:{1:2,0:4}}}},battles:[{attacker:1,target:'B',attackOrigins:[{region:'A',moves:[0,1]}]},{attacker:1,target:'C',attackOrigins:[{region:'A',moves:[0]}]}]}}
test('one origin, two distinct attacking groups, provisional and resettable',()=>{
 const {game,battles}=fixture(),before=JSON.stringify({game,battles}),p=R.plan(game,1,battles);
 assert(R.choose(p,'A','battle:0:0'));assert.equal(R.choose(p,'U','stationed'),false);assert(R.choose(p,'A','battle:1:0'));assert.equal(R.choose(p,'A','stationed'),false);
 assert(R.validate(p,game,battles));assert.deepEqual(R.commands(p).map(c=>c.loss),[1,1]);assert.equal(JSON.stringify({game,battles}),before);
 assert(R.reset(p));assert.equal(R.commands(p),null);assert(R.choose(p,'U','stationed'));assert.equal(R.commands(p)[0].loss,1);assert(R.commands(p)[0].sea);
});
test('single loss valid; empty source committed troops included; other fleets untouched',()=>{
 const {game,battles}=fixture();game.b.A.owner=null;game.b.A.units=0;const p=R.plan(game,1,battles);
 assert(R.choose(p,'A','battle:1:0'));assert.equal(R.choose(p,'A','battle:1:0'),false);assert(R.validate(p,game,battles));assert.equal(R.commands(p).length,1);
 assert.equal(p.regions.find(r=>r.region==='U').groups[0].available,2);assert(!p.regions.some(r=>r.region==='B'));
});
test('stale or forged groups rejected; no eligible units skips reaction',()=>{
 const {game,battles}=fixture(),p=R.plan(game,1,battles);R.choose(p,'A','battle:0:0');battles[0].attackOrigins[0].moves.pop();assert.equal(R.validate(p,game,battles),false);
 p.chosen={stationed:3};assert.equal(R.commands(p),null);
 const s=R.create();R.activate(s,1,8);assert.equal(R.afterAction(s,R.capture(s,0,3,'empty'),false),false);assert.equal(R.next(s),null);
});

test('event identifiers survive serialization without prototype collisions',()=>{
 const s=R.create();R.activate(s,1,8);
 for(const id of ['constructor','__proto__','toString']){
  const token=R.capture(s,0,3,id);assert(R.afterAction(s,token));assert.equal(R.afterAction(s,token),false);
 }
 const restored=JSON.parse(JSON.stringify(s));
 assert.equal(R.afterAction(restored,R.capture(restored,0,3,'__proto__')),false);
 assert.equal(restored.queue.length,3);
});
