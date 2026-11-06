(function(root){'use strict';
function targets(game,actor,roll,cards){
 if(roll===4||roll===5)return game.players.flatMap((p,i)=>i!==actor&&!p.decimated&&p.hand.length?[i]:[]);
 if(roll!==6)return [];
 return game.players.flatMap((p,owner)=>owner===actor?[]:p.inPlay.flatMap((id,index)=>cards[id]?.type.includes('Agent')?[{owner,index,id,name:cards[id].name,uid:p.inPlayUID?.[index]}]:[]));
}
function resolve(game,state,target,cards,randomIndex){
 const eligible=targets(game,state.actor,state.roll,cards);
 if(!eligible.length)return {success:false,sfx:'fail'};
 if(state.roll===6){
  const t=eligible.find(t=>t.owner===target?.owner&&t.id===target?.id&&t.uid!==undefined&&t.uid===target?.uid);
  if(!t)return null;
  game.players[t.owner].inPlay.splice(t.index,1);game.players[t.owner].inPlayUID.splice(t.index,1);game.discard.push(t.id);
  return {success:true,sfx:'assassin',owner:t.owner,name:t.name};
 }
 if(!eligible.includes(target))return null;
 const hand=game.players[target].hand,at=randomIndex(hand.length);
 if(!Number.isInteger(at)||at<0||at>=hand.length)return null;
 game.players[state.actor].hand.push(hand.splice(at,1)[0]);
 return {success:true,sfx:'thief',owner:target};
}
const api=Object.freeze({targets,resolve});root.TribuGuild=api;if(typeof module==='object'&&module.exports)module.exports=api;
})(typeof globalThis==='object'?globalThis:this);
