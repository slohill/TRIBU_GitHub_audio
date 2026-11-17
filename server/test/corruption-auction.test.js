const {test}=require('node:test'),assert=require('node:assert/strict');
const A=require('../../assets/corruption-auction');
const {createAuctionSync}=require('../corruption-auction-sync');
const players=()=>[{gold:4,hand:[]},{gold:12,hand:[]},{gold:8,hand:[]}];
test('three simultaneous cards, preparation is untimed and seller alone starts',()=>{
 const p=players(),s=A.create(0,[4,5,6],6),d=[];
 assert.equal(s.deadline,null);assert.equal(A.price(s,1,0,3),false);
 assert(A.price(s,0,0,3));assert(A.start(s,0,p,d,1000));assert.equal(s.deadline,61000);
 assert.equal(A.price(s,0,0,4),false);assert.equal(A.start(s,0,p,d,2000),false);
 assert(A.bid(s,1,3,p,d,s.revision,2000,0));assert(A.bid(s,2,4,p,d,s.revision,3000,2));
 assert.equal(s.deadline,61000);assert.deepEqual(p.map(x=>x.gold),[4,12,8]);assert.equal(s.stage,'bidding');
});
test('combined reservations, self raise, stale bid and invalid amounts',()=>{
 const p=players(),s=A.create(0,[4,5,6],6),d=[];A.start(s,0,p,d,0);
 assert(A.bid(s,1,8,p,d,s.revision,1,0));assert(A.bid(s,1,4,p,d,s.revision,2,1));
 assert.equal(A.bid(s,1,1,p,d,s.revision,3,2),false);
 assert.equal(A.bid(s,1,9,p,d,s.revision,3,0),false);
 assert(A.bid(s,2,9,p,d,s.revision,4,0)===false);
 assert.equal(A.bid(s,0,1,p,d,s.revision,1,2),false);
 assert.equal(A.bid(s,2,1.5,p,d,s.revision,1,2),false);
 const rev=s.revision;assert(A.bid(s,2,1,p,d,rev,5,2));assert.equal(A.bid(s,1,2,p,d,rev,6,2),false);
});
test('only leader can undo; restoration skips previous offers no longer affordable',()=>{
 const p=players(),s=A.create(0,[4,5,6],6),d=[];A.start(s,0,p,d,0);
 A.bid(s,2,2,p,d,s.revision,1,0);A.bid(s,1,3,p,d,s.revision,2,0);
 assert.equal(A.cancel(s,2,p,s.revision,3,0),false);
 assert(A.cancel(s,1,p,s.revision,3,0));assert.deepEqual(s.bids[0],{player:2,amount:2});
 A.bid(s,1,3,p,d,s.revision,4,0);A.bid(s,2,8,p,d,s.revision,5,1);
 assert(A.cancel(s,1,p,s.revision,6,0));assert.equal(s.bids[0],null);
 assert.equal(s.deadline,60000);
});
test('extension repeatable by non seller; expiry settles once, unsold penalty and gold total',()=>{
 const p=players(),s=A.create(0,[4,5,6],6),d=[];A.start(s,0,p,d,0);
 assert.equal(A.extend(s,0,p,s.revision,1),false);
 assert(A.extend(s,1,p,s.revision,1));assert(A.extend(s,1,p,s.revision,2));assert.equal(s.deadline,90000);
 A.bid(s,1,4,p,d,s.revision,3,0);A.bid(s,1,5,p,d,s.revision,4,1);
 assert.equal(A.tick(s,p,d,89999),false);assert(A.tick(s,p,d,90000));
 assert.deepEqual(p[1],{gold:3,hand:[4,5]});assert.deepEqual(d,[6]);assert.equal(A.total(s),14);
 assert.equal(A.tick(s,p,d,99999),false);assert.equal(A.extend(s,1,p,s.revision,99999),false);
});
test('reconnect preserves bids, undo history and absolute deadline',()=>{
 const p=players(),s=A.create(0,[4,5,6],0),d=[];A.start(s,0,p,d,1000);A.bid(s,1,3,p,d,s.revision,2000,2);
 const saved=JSON.parse(JSON.stringify(s));assert.equal(saved.deadline,61000);
 assert(A.cancel(saved,1,p,saved.revision,3000,2));assert(A.tick(saved,p,d,61000));assert.equal(A.total(saved),0);
 assert.deepEqual(d,[4,5,6]);
});
test('bots use joint budgets and singleton caps without extending or bidding against themselves',()=>{
 const cards=[{name:'Hero',count:1},{name:'Taxe',count:3},{name:'Portails',count:1},{name:'Portails',count:1,extension:'corruption'}];
 assert.equal(A.botPrice(0,cards),5);assert.equal(A.botPrice(2,cards),1);
 const p=players(),s=A.create(0,[0,1,2],6),d=[];A.price(s,0,0,5);A.start(s,0,p,d,0);
 assert.deepEqual(A.botAction(s,1,p,cards),{kind:'bid',amount:5,index:0});
 A.bid(s,1,5,p,d,s.revision,1,0);assert.deepEqual(A.botAction(s,1,p,cards),{kind:'bid',amount:1,index:1});
});
test('server owns bidding, undo, extensions and deadline; late or stale actions rejected',()=>{
 let time=1000,published=0;const p=players(),s=A.create(0,[4,5,6],6);
 const room={gameVersion:'corruption',legacySnapshot:{g:{players:p,discard:[],morcattAuction:s},rule:{}}};
 const sync=createAuctionSync({now:()=>time,publish:()=>published++});
 const act=(actor,kind,extra={})=>sync.action(room,actor,{kind,revision:s.revision,...extra});
 assert(act(0,'start').ok);assert(act(1,'bid',{index:2,amount:4}).ok);
 assert(act(1,'cancel',{index:2}).ok);assert(act(2,'extend').ok);
 assert.equal(act(0,'extend').ok,false);time=s.deadline;
 assert.equal(act(1,'bid',{index:0,amount:1}).ok,false);assert(sync.tick(room,[]));assert.equal(s.stage,'finished');assert.equal(published,5);
});
