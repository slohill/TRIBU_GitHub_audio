/* Serializable auction state. Gold reaction and card drawing stay in the legacy engine. */
(function(root){
'use strict';
const SECONDS=30;
function create(seller,cards,baseHarvest){
 return {seller,cards:cards.slice(),prices:cards.map(()=>1),stage:'prepare',round:0,bid:null,passed:[],deadline:null,revision:0,receipts:0,unsold:0,baseHarvest,results:[]};
}
function minimum(s){return s.bid?s.bid.amount+1:s.prices[s.round]}
function eligible(s,players){return players.map((p,i)=>i).filter(i=>i!==s.seller&&i!==s.bid?.player&&!players[i].decimated&&players[i].gold>=minimum(s))}
function price(s,actor,index,amount){
 if(s.stage!=='prepare'||actor!==s.seller||!Number.isInteger(index)||index<0||index>=s.cards.length||!Number.isSafeInteger(amount)||amount<1)return false;
 s.prices[index]=amount;s.revision++;return true;
}
function next(s,players,discard,now){
 s.bid=null;s.passed=[];
 if(s.round>=s.cards.length){s.stage='finished';s.deadline=null;return}
 s.stage='bidding';s.deadline=now+SECONDS*1000;
 if(!eligible(s,players).length)settle(s,players,discard,now);
}
function start(s,actor,players,discard,now=Date.now()){
 if(s.stage!=='prepare'||actor!==s.seller)return false;
 s.revision++;next(s,players,discard,now);return true;
}
function settle(s,players,discard,now){
 if(s.stage!=='bidding')return false;
 const card=s.cards[s.round],bid=s.bid;
 if(bid){players[bid.player].gold-=bid.amount;players[bid.player].hand.push(card);s.receipts+=bid.amount}
 else{discard.push(card);s.unsold++}
 s.results.push({round:s.round,card,buyer:bid?.player??null,amount:bid?.amount??0});
 s.round++;s.revision++;next(s,players,discard,now);return true;
}
function finishIfPassed(s,players,discard,now){
 if(!eligible(s,players).some(i=>!s.passed.includes(i)))settle(s,players,discard,now);
}
function bid(s,actor,amount,players,discard,expectedRevision,now=Date.now()){
 if(s.stage!=='bidding'||s.revision!==expectedRevision||now>=s.deadline||!eligible(s,players).includes(actor)||!Number.isSafeInteger(amount)||amount<minimum(s)||amount>players[actor].gold)return false;
 s.bid={player:actor,amount};s.passed=[];s.deadline=now+SECONDS*1000;s.revision++;
 finishIfPassed(s,players,discard,now);return true;
}
function pass(s,actor,players,discard,expectedRevision,now=Date.now()){
 if(s.stage!=='bidding'||s.revision!==expectedRevision||now>=s.deadline||!eligible(s,players).includes(actor)||s.passed.includes(actor))return false;
 s.passed.push(actor);s.revision++;finishIfPassed(s,players,discard,now);return true;
}
function tick(s,players,discard,now=Date.now()){
 if(s.stage!=='bidding'||now<s.deadline)return false;
 return settle(s,players,discard,now);
}
function total(s){return Math.max(0,s.baseHarvest+s.receipts-s.unsold)}
function singleton(cardId,cards,version='corruption'){
 const c=cards[cardId];if(!c)return false;
 // Same-name copies, including the second independent Portails card, count together.
 return cards.filter(x=>x.name===c.name&&(!x.extension||x.extension===version)).reduce((sum,x)=>sum+x.count,0)===1;
}
function botPrice(cardId,cards){return singleton(cardId,cards)?5:1}
function botAction(s,actor,players,cards){
 if(s.stage!=='bidding'||actor===s.seller||actor===s.bid?.player||s.passed.includes(actor))return null;
 const amount=minimum(s),cap=Math.min(players[actor].gold,singleton(s.cards[s.round],cards)?10:3);
 return amount<=cap?{kind:'bid',amount}:{kind:'pass'};
}
const api=Object.freeze({create,price,start,bid,pass,tick,total,minimum,eligible,botPrice,botAction,seconds:SECONDS});
root.TribuAuction=api;if(typeof module==='object'&&module.exports)module.exports=api;
})(typeof globalThis==='object'?globalThis:this);
