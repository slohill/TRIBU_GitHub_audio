const {test}=require('node:test'),assert=require('node:assert/strict');
const A=require('../../assets/corruption-auction');
const players=()=>[{gold:4,hand:[]},{gold:12,hand:[]},{gold:8,hand:[]}];
test('public preparation has no deadline; seller alone sets prices; launch locks them',()=>{
 const p=players(),s=A.create(0,[4,5],6),discard=[];
 assert.equal(s.deadline,null);assert.equal(A.price(s,1,0,3),false);
 assert.equal(A.price(s,0,0,0),false);assert(A.price(s,0,0,3));
 assert(A.start(s,0,p,discard,1000));assert.equal(s.deadline,31000);
 assert.equal(A.price(s,0,0,4),false);assert.equal(A.start(s,0,p,discard,2000),false);
});
test('new offer resets common timer and passes; stale simultaneous offer cannot overwrite',()=>{
 const p=players(),s=A.create(0,[4],6),d=[];A.start(s,0,p,d,0);
 assert(A.pass(s,1,p,d,s.revision,100));const revision=s.revision;
 assert(A.bid(s,2,2,p,d,revision,200));assert.deepEqual(s.passed,[]);assert.equal(s.deadline,30200);
 assert.equal(A.bid(s,1,3,p,d,revision,300),false);
 assert(A.bid(s,1,3,p,d,s.revision,300));assert.equal(s.deadline,30300);
 assert(A.pass(s,2,p,d,s.revision,400));assert.equal(s.stage,'finished');
 assert.equal(p[1].gold,9);assert.deepEqual(p[1].hand,[4]);assert.equal(A.total(s),9);
 assert.equal(A.tick(s,p,d,100000),false);assert.equal(p[1].gold,9);
});
test('timeout settles once and next sale uses remaining budget, not previous balance',()=>{
 const p=players(),s=A.create(0,[4,5],6),d=[];p[2].gold=10;A.start(s,0,p,d,0);
 assert.equal(A.bid(s,0,1,p,d,s.revision,10),false);
 assert.equal(A.bid(s,1,13,p,d,s.revision,10),false);
 assert(A.bid(s,1,8,p,d,s.revision,10));assert.equal(A.tick(s,p,d,30009),false);
 assert(A.tick(s,p,d,30010));assert.equal(p[1].gold,4);assert.equal(s.round,1);
 assert.equal(A.bid(s,1,5,p,d,s.revision,30011),false);
 assert(A.tick(s,p,d,60010));assert.deepEqual(d,[5]);assert.equal(A.total(s),13);
});
test('unaffordable or passed cards discarded, never negative harvest; empty deck finishes',()=>{
 const p=players(),s=A.create(0,[4,5],0),d=[];A.price(s,0,0,99);A.start(s,0,p,d,0);
 assert.equal(s.round,1);assert.deepEqual(d,[4]);
 A.pass(s,1,p,d,s.revision,1);A.pass(s,2,p,d,s.revision,2);
 assert.equal(s.stage,'finished');assert.equal(A.total(s),0);assert.deepEqual(d,[4,5]);
 const empty=A.create(0,[],6);A.start(empty,0,p,d,0);assert.equal(empty.stage,'finished');assert.equal(A.total(empty),6);
});
test('save/reconnect preserves prices, pass state and deadline without a timer reset',()=>{
 const p=players(),s=A.create(0,[4],6),d=[];A.start(s,0,p,d,1000);A.bid(s,1,2,p,d,s.revision,2000);
 const restored=JSON.parse(JSON.stringify(s));assert.equal(restored.deadline,32000);
 assert(A.tick(restored,p,d,33000));assert.deepEqual(p[1].hand,[4]);assert.equal(p[1].gold,10);
});
test('bot budgets are 3/10; singleton comes from deck composition including both Portails',()=>{
 const cards=[{name:'Hero',count:1},{name:'Taxe',count:3},{name:'Portails',count:1},{name:'Portails',count:1,extension:'corruption'}];
 assert.equal(A.botPrice(0,cards),5);assert.equal(A.botPrice(1,cards),1);assert.equal(A.botPrice(2,cards),1);
 const p=players(),s=A.create(0,[0],6),d=[];A.price(s,0,0,5);A.start(s,0,p,d,0);
 assert.deepEqual(A.botAction(s,1,p,cards),{kind:'bid',amount:5});
 p[1].gold=4;assert.deepEqual(A.botAction(s,1,p,cards),{kind:'pass'});
});
