const test=require('node:test'),assert=require('node:assert/strict'),A=require('../../assets/corruption-auction');
const cards=[{name:'Normal',count:3}],players=()=>[{hand:[],gold:5},{hand:[],gold:10},{hand:[],gold:10,bot:true}];
test('ready cannot close while a bot can bid; new bid clears votes, seller does not vote',()=>{
 const p=players(),s=A.create(0,[0],6),d=[];A.start(s,0,p,d,0);
 assert.equal(A.ready(s,0,p,s.revision,1),false);
 assert(A.ready(s,1,p,s.revision,1));assert.equal(A.finishReady(s,p,cards,d),false);
 assert(A.bid(s,2,3,p,d,s.revision,2));assert.deepEqual(s.ready,[]);
 assert.equal(A.finishReady(s,p,cards,d),false);assert(A.ready(s,1,p,s.revision,3));
 assert(A.finishReady(s,p,cards,d));assert.equal(p[2].gold,7);assert.deepEqual(p[2].hand,[0]);
 assert.equal(A.finishReady(s,p,cards,d),false);assert.equal(s.receipts,3);
});
test('human outbid, cancel and extension reopen consent; disconnected buyer waits for deadline',()=>{
 const p=players();p[2].bot=false;const s=A.create(0,[0],6),d=[];A.start(s,0,p,d,0);
 assert(A.ready(s,1,p,s.revision,1));assert(A.bid(s,2,2,p,d,s.revision,2));assert.deepEqual(s.ready,[]);
 assert(A.ready(s,1,p,s.revision,3));assert(A.cancel(s,2,p,s.revision,4));assert.deepEqual(s.ready,[]);
 assert(A.ready(s,1,p,s.revision,5));assert(A.extend(s,1,p,s.revision,6));assert.deepEqual(s.ready,[]);
 assert(A.ready(s,1,p,s.revision,7));assert.equal(A.finishReady(s,p,cards,d),false);
 assert(A.tick(s,p,d,75000));assert.equal(s.unsold,1);
});
test('all-bot buyers finish only after all useful bids; decimated buyers excluded',()=>{
 const p=players();p[1].decimated=true;const s=A.create(0,[0],6),d=[];A.start(s,0,p,d,0);
 assert.equal(A.finishReady(s,p,cards,d),false);A.bid(s,2,1,p,d,s.revision,1);
 assert(A.finishReady(s,p,cards,d));assert.equal(p[2].gold,9);
});
