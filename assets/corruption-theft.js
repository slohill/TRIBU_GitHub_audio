(function(root){'use strict';
const A=typeof module==='object'&&module.exports?require('./corruption-alliances'):root.TribuAlliances;
const H=typeof module==='object'&&module.exports?require('./corruption-heroes'):root.TribuHeroes;
function targets(game,actor,cards){return game.players.flatMap((p,i)=>{
 if(i===actor||p.decimated||(p.faction===6&&H.hasPassive(game,i,cards,'noblesse')))return [];
 const a=A.alliance(p,cards);return a?[{player:i,id:a.id,tribe:a.card.allianceTribe,uid:p.inPlayUID?.[p.inPlay.indexOf(a.id)]}]:[];
})}
function steal(game,state,victim,id,cards){
 const p=game.players[state.actor],at=p.hand.indexOf(state.cardId),target=targets(game,state.actor,cards).find(t=>t.player===victim&&t.id===id);
 const original=state.targets?.find(t=>t.player===victim&&t.id===id);
 if(cards[state.cardId]?.extensionKey!=='corruption-theft'||at<0||p.gold<5||!target||!original||original.uid!==target.uid)return null;
 p.hand.splice(at,1);game.discard.push(state.cardId);p.gold-=5;
 const other=game.players[victim],index=other.inPlay.indexOf(id);other.inPlay.splice(index,1);other.inPlayUID.splice(index,1);p.hand.push(id);return target;
}
function refreshDwarfGain(game,reaction,cards){
 const d=reaction?.dwarfHarvest;if(!d)return;
 if(!A.bonus(game,d.owner,cards,'dwarves',5))d.revoked=true;
 const bonus=d.revoked?0:d.regions.filter(r=>game.b[r]?.owner===d.owner).length*5;
 reaction.amount=Math.max(0,d.baseAmount+bonus);
}
const api=Object.freeze({targets,steal,refreshDwarfGain});root.TribuCorruptionTheft=api;if(typeof module==='object'&&module.exports)module.exports=api;
})(typeof globalThis==='object'?globalThis:this);
