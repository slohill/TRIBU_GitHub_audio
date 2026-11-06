(function(root){'use strict';
function prepare(game,actor,oracleIds,shuffle){
 let recycled=false;
 if(game.oracleDeck.length<3){
  const kept=game.oracleDeck.slice(),others=oracleIds.filter(id=>!kept.includes(id));
  game.oracleDeck=shuffle(others).concat(kept);game.oracleDiscard=[];game.oracleActive=null;recycled=true;
 }
 return {state:{kind:'guideDivination',actor,cards:game.oracleDeck.slice(-3).reverse(),order:[]},recycled};
}
function select(state,index){
 if(!Number.isInteger(index)||index<0||index>2||state.order.includes(index)||state.order.length>=3)return false;
 state.order.push(index);return true;
}
function confirm(game,state){
 if(state.order.length!==3||new Set(state.order).size!==3||state.order.some(i=>!Number.isInteger(i)||i<0||i>2)||JSON.stringify(game.oracleDeck.slice(-3).reverse())!==JSON.stringify(state.cards))return false;
 game.oracleDeck.splice(-3,3,...state.order.map(i=>state.cards[i]).reverse());return true;
}
const api=Object.freeze({prepare,select,confirm});root.TribuGuide=api;if(typeof module==='object'&&module.exports)module.exports=api;
})(typeof globalThis==='object'?globalThis:this);
