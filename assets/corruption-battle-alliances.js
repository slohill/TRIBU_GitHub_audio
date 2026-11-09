(function(root){'use strict';
const A=typeof module==='object'&&module.exports?require('./corruption-alliances'):root.TribuAlliances;
const Map=typeof module==='object'&&module.exports?require('./corruption-golem'):root.TribuGolem;
function elfDestinations(game,b,cards,data){
 if(!b||b.environmentResolved||!Number.isInteger(b.defender)||!['land','sea'].includes(b.kind)||!A.bonus(game,b.defender,cards,'elves',1))return [];
 const n=game.sea[b.target]?game.sea[b.target].fleets[b.defender]||0:game.b[b.target]?.owner===b.defender?game.b[b.target].units:0;
 if(n<=0)return [];
 return Map.neighbors(game,data,b.target).filter(r=>game.sea[r]||game.b[r].owner===b.defender||(game.b[r].owner===null&&(!game.b[r].hostile||A.peaceful(game,b.defender,r,cards))));
}
const api=Object.freeze({elfDestinations});root.TribuBattleAlliances=api;if(typeof module==='object'&&module.exports)module.exports=api;
})(typeof globalThis==='object'?globalThis:this);
