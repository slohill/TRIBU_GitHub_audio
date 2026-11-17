'use strict';
const A=require('../assets/corruption-auction');
function active(room){const s=room.legacySnapshot?.g?.morcattAuction;return s&&s.stage!=='finished'}
function createAuctionSync({publish,now=Date.now}){
 function changed(room){room.legacyRevision=(room.legacyRevision||0)+1;publish(room)}
 function action(room,actor,payload){
  const snap=room.legacySnapshot,g=snap?.g,s=A.upgrade(g?.morcattAuction);
  if(room.gameVersion!=='corruption'||!s||!g.players[actor]||g.players[actor].bot)return {ok:false,error:'Enchères indisponibles.'};
  if(payload.revision!==s.revision)return {ok:false,error:'Une autre offre est arrivée. Vérifiez le prix actuel.'};
  let ok=false;const time=now();
  if(payload.kind==='price')ok=A.price(s,actor,payload.index,payload.amount);
  if(payload.kind==='start')ok=A.start(s,actor,g.players,g.discard,time);
  if(payload.kind==='bid')ok=A.bid(s,actor,payload.amount,g.players,g.discard,payload.revision,time,payload.index);
  if(payload.kind==='cancel')ok=A.cancel(s,actor,g.players,payload.revision,time,payload.index);
  if(payload.kind==='extend')ok=A.extend(s,actor,g.players,payload.revision,time);
  if(ok)changed(room);
  return ok?{ok:true}:{ok:false,error:'Cette action n’est plus disponible.'};
 }
 function tick(room,cards){
  if(!active(room))return false;
  const g=room.legacySnapshot.g,s=A.upgrade(g.morcattAuction),time=now();
  let updated=false;
  if(s.stage==='prepare'&&g.players[s.seller].bot){
   s.cards.forEach((id,i)=>A.price(s,s.seller,i,A.botPrice(id,cards)));
   updated=A.start(s,s.seller,g.players,g.discard,time);
  }else if(s.stage==='bidding'){
   updated=A.tick(s,g.players,g.discard,time);
   if(!updated)updated=A.botTick(s,g.players,cards,g.discard,time);
  }
  if(updated)changed(room);return updated;
 }
 // During a server-owned auction snapshots may only update Commerce proposals.
 // Never accept stale balances, cards, timer, bids or a forged auction completion.
 function mergeProposals(room,incoming){
  if(!active(room))return false;
  const rule=room.legacySnapshot.rule;
  if(Array.isArray(incoming.rule?.commerceDeals)){
   const previous=rule.commerceDeals||[];
   for(const d of incoming.rule.commerceDeals){
    const old=previous.find(x=>x.id===d.id);
    if(d.status==='done'&&old?.status!=='done')return false;
   }
   rule.commerceDeals=incoming.rule.commerceDeals;
   rule.commerceSeq=incoming.rule.commerceSeq;
  }
  return true;
 }
 return {action,tick,mergeProposals,active};
}
module.exports={createAuctionSync,active};
