const {test}=require('node:test'),assert=require('node:assert/strict');
const A=require('../../assets/corruption-auction');
const {createAuctionSync}=require('../corruption-auction-sync');
const cards=[{name:'A',count:3},{name:'B',count:3},{name:'Hero',count:1}];
function setup(){const p=[{gold:10,hand:[]},{gold:10,hand:[],bot:true},{gold:10,hand:[]}],s=A.create(0,[0,1,2],6),d=[];A.start(s,0,p,d,0);return {p,s,d}}
test('bot waits 2 seconds minimum, shuffles cards, waits again and preserves auction deadline',()=>{
 const {p,s,d}=setup();
 assert.equal(A.botTick(s,p,cards,d,0,()=>0),false);
 assert.equal(s.botNextAt[1],2000);
 assert.equal(A.botTick(s,p,cards,d,1999,()=>0),false);
 assert(A.botTick(s,p,cards,d,2000,()=>0));
 assert.equal(s.bids[0],null);assert.deepEqual(s.bids[1],{player:1,amount:1});
 assert.equal(A.botTick(s,p,cards,d,3999,()=>0),false);
 assert(A.botTick(s,p,cards,d,4000,()=>0));assert.equal(s.bids[1].amount,1);
 assert.equal(s.deadline,60000);
});
test('maximum delay is 5 seconds; waiting state survives serialization',()=>{
 const {p,s,d}=setup();A.botTick(s,p,cards,d,0,()=>0.999999);
 assert.equal(s.botNextAt[1],5000);
 const saved=JSON.parse(JSON.stringify(s));
 assert.equal(A.botTick(saved,p,cards,d,4999,()=>0.999999),false);
 assert(A.botTick(saved,p,cards,d,5000,()=>0.999999));assert.equal(saved.bids[0].amount,1);
});
test('bot rechecks changed offers and budget after delay, never extends or bids after expiry',()=>{
 const {p,s,d}=setup();p[1].gold=2;A.botTick(s,p,cards,d,0,()=>0);
 A.bid(s,2,3,p,d,s.revision,100,1);A.bid(s,2,3,p,d,s.revision,100,2);
 assert(A.botTick(s,p,cards,d,2000,()=>0));assert.equal(s.bids[0].amount,1);
 assert.equal(A.botTick(s,p,cards,d,4000,()=>0),false);
 assert.equal(A.botTick(s,p,cards,d,60000,()=>0),false);assert.equal(s.deadline,60000);
});
test('server seller bot keeps 1/5 starting prices; buyer bids only when due',()=>{
 const {p,s,d}=setup();p[0].bot=true;s.stage='prepare';
 let time=0;const room={gameVersion:'corruption',legacySnapshot:{g:{morcattAuction:s,players:p,discard:d}}};
 const sync=createAuctionSync({now:()=>time,publish:()=>{}});
 assert(sync.tick(room,cards));assert.deepEqual(s.prices,[1,1,5]);
 assert.equal(sync.tick(room,cards),false);time=s.botNextAt[1]-1;assert.equal(sync.tick(room,cards),false);
 time=s.botNextAt[1];assert(sync.tick(room,cards));assert.equal(s.bids.filter(Boolean).length,1);
});
