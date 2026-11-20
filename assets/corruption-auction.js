/* Serializable simultaneous auctions; server is authoritative online. */
(function(root){
'use strict';
const SECONDS=60;
// Resume an auction saved by the previous sequential implementation without
// charging again for cards already sold.
function upgrade(s){
 if(!s||Array.isArray(s.bids))return s;
 const round=s.round||0;
 s.cards=s.cards.slice(round);s.prices=s.prices.slice(round);
 s.bids=s.cards.map((_,i)=>i===0?s.bid||null:null);
 s.history=s.bids.map(b=>b?[b]:[]);
 if(s.stage==='bidding'&&s.deadline)s.deadline+=30000;
 delete s.bid;delete s.round;delete s.passed;
 return s;
}
function create(seller,cards,baseHarvest){
 return {seller,cards:cards.slice(),prices:cards.map(()=>1),bids:cards.map(()=>null),history:cards.map(()=>[]),stage:'prepare',deadline:null,revision:0,receipts:0,unsold:0,baseHarvest,results:[]};
}
function minimum(s,index=0){return s.bids[index]?s.bids[index].amount+1:s.prices[index]}
function available(s,actor,players,index=-1){return players[actor].gold-s.bids.reduce((n,b,i)=>n+(i!==index&&b?.player===actor?b.amount:0),0)}
function eligible(s,players,index=0){return players.map((p,i)=>i).filter(i=>i!==s.seller&&!players[i].decimated&&available(s,i,players,index)>=minimum(s,index))}
function price(s,actor,index,amount){
 if(s.stage!=='prepare'||actor!==s.seller||!Number.isInteger(index)||index<0||index>=s.cards.length||!Number.isSafeInteger(amount)||amount<1)return false;
 s.prices[index]=amount;s.revision++;return true;
}
function start(s,actor,players,discard,now=Date.now()){
 if(s.stage!=='prepare'||actor!==s.seller)return false;
 s.stage='bidding';s.deadline=now+SECONDS*1000;s.revision++;
 if(!s.cards.length)settle(s,players,discard);
 return true;
}
function settle(s,players,discard){
 if(s.stage!=='bidding')return false;
 s.cards.forEach((card,index)=>{
  const bid=s.bids[index];
  if(bid){players[bid.player].gold-=bid.amount;players[bid.player].hand.push(card);s.receipts+=bid.amount}
  else{discard.push(card);s.unsold++}
  s.results.push({round:index,card,buyer:bid?.player??null,amount:bid?.amount??0});
 });
 s.stage='finished';s.deadline=null;s.revision++;return true;
}
function live(s,actor,players,revision,now){return s.stage==='bidding'&&s.revision===revision&&now<s.deadline&&players[actor]&&!players[actor].decimated&&actor!==s.seller}
function bid(s,actor,amount,players,discard,expectedRevision,now=Date.now(),index=0){
 if(!live(s,actor,players,expectedRevision,now)||!Number.isInteger(index)||index<0||index>=s.cards.length||!Number.isSafeInteger(amount)||amount<minimum(s,index)||amount>available(s,actor,players,index))return false;
 const offer={player:actor,amount};s.history[index].push(offer);s.bids[index]=offer;s.ready=[];s.revision++;return true;
}
function cancel(s,actor,players,revision,now=Date.now(),index=0){
 if(!live(s,actor,players,revision,now)||!Number.isInteger(index)||s.bids[index]?.player!==actor)return false;
 const history=s.history[index];history.pop();s.bids[index]=null;
 while(history.length){const previous=history.at(-1);if(!players[previous.player].decimated&&previous.amount<=available(s,previous.player,players,index)){s.bids[index]=previous;break}history.pop()}
 s.ready=[];s.revision++;return true;
}
function extend(s,actor,players,revision,now=Date.now()){
 if(!live(s,actor,players,revision,now))return false;
 s.deadline+=15000;s.ready=(s.ready||[]).filter(i=>i!==actor);s.revision++;return true;
}
function ready(s,actor,players,revision,now=Date.now()){
 if(!live(s,actor,players,revision,now)||players[actor].bot||(s.ready||[]).includes(actor))return false;
 s.ready=[...(s.ready||[]),actor];s.revision++;return true;
}
function finishReady(s,players,cards,discard){
 if(s.stage!=='bidding')return false;
 const buyers=players.map((p,i)=>({p,i})).filter(({p,i})=>i!==s.seller&&!p.decimated);
 if(!buyers.every(({p,i})=>p.bot?!botAction(s,i,players,cards):(s.ready||[]).includes(i)))return false;
 return settle(s,players,discard);
}
function tick(s,players,discard,now=Date.now()){
 if(s.stage!=='bidding'||now<s.deadline)return false;
 return settle(s,players,discard);
}
function total(s){return Math.max(0,s.baseHarvest+s.receipts-s.unsold)}
function singleton(cardId,cards,version='corruption'){
 const c=cards[cardId];if(!c)return false;
 return cards.filter(x=>x.name===c.name&&(!x.extension||x.extension===version)).reduce((sum,x)=>sum+x.count,0)===1;
}
function botPrice(cardId,cards){return singleton(cardId,cards)?5:1}
function botAction(s,actor,players,cards,order=s.cards.map((_,i)=>i)){
 if(s.stage!=='bidding'||actor===s.seller||players[actor].decimated)return null;
 for(const index of order){
  if(s.bids[index]?.player===actor)continue;
  const amount=minimum(s,index),cap=Math.min(available(s,actor,players,index),singleton(s.cards[index],cards)?10:3);
  if(amount<=cap)return {kind:'bid',amount,index};
 }return null;
}
function botTick(s,players,cards,discard,now=Date.now(),random=Math.random){
 if(s.stage!=='bidding'||now>=s.deadline)return false;
 s.botNextAt=s.botNextAt||{};
 const delay=()=>2000+Math.floor(random()*3001);
 for(let actor=0;actor<players.length;actor++){
  if(!players[actor].bot||players[actor].decimated||actor===s.seller)continue;
  if(!Number.isFinite(s.botNextAt[actor])){s.botNextAt[actor]=now+delay();continue}
  if(now<s.botNextAt[actor])continue;
  s.botNextAt[actor]=now+delay();
  const order=s.cards.map((_,i)=>i);
  for(let i=order.length-1;i>0;i--){const j=Math.floor(random()*(i+1));[order[i],order[j]]=[order[j],order[i]]}
  // Recompute against current offers and the joint budget, never a stale plan.
  const action=botAction(s,actor,players,cards,order);
  if(action&&bid(s,actor,action.amount,players,discard,s.revision,now,action.index))return true;
 }
 return false;
}
const api=Object.freeze({upgrade,create,price,start,bid,cancel,extend,ready,finishReady,tick,total,minimum,available,eligible,botPrice,botAction,botTick,seconds:SECONDS});
root.TribuAuction=api;if(typeof module==='object'&&module.exports)module.exports=api;
})(typeof globalThis==='object'?globalThis:this);
