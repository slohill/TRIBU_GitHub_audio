/* Corruption foundations. Mechanics stay in the legacy engine. */
(function(root){
 'use strict';
 const tribes=Object.freeze({humans:2,ogres:1,dwarves:3,elves:3});
 const tokens=Object.freeze({humans:'tokenhumans',ogres:'tokenogrest',dwarves:'tokendwarves',elves:'tokenelves'});
 function enabled(game){return game?.gameVersion==='corruption'}
 function assignNpcs(game,random=Math.random){
  if(!enabled(game)||game.corruptionNpcAssigned)return false;
  const regions=Object.keys(game.b).filter(r=>game.b[r].originalHostile);
  const bag=Object.entries(tribes).flatMap(([tribe,n])=>Array(n).fill(tribe));
  if(regions.length!==bag.length)throw new Error('Corruption requires nine original NPC regions.');
  for(let i=bag.length-1;i>0;i--){const j=Math.floor(random()*(i+1));[bag[i],bag[j]]=[bag[j],bag[i]]}
  regions.forEach((r,i)=>game.b[r].npcTribe=bag[i]);
  game.corruptionNpcAssigned=true;return true;
 }
 function npcImage(tribe){return tokens[tribe]?'assets/images/tokens/'+tokens[tribe]+'.webp':null}
 function installPortal(cards){
  const existing=cards.findIndex(c=>c.extensionKey==='corruption-portal');
  if(existing>=0)return existing;
  const base=cards.find(c=>c.name==='Portails');
  if(!base)throw new Error('Legacy Portails card missing');
  return cards.push({...base,count:1,extension:'corruption',extensionKey:'corruption-portal'})-1;
 }
 function portalImage(card){return card?.extensionKey==='corruption-portal'?'assets/images/tokens/portail2.webp':'assets/images/tokens/portail.png'}
 const api=Object.freeze({enabled,assignNpcs,npcImage,installPortal,portalImage,tribes});
 root.TribuCorruption=api;
 if(typeof module==='object'&&module.exports)module.exports=api;
})(typeof globalThis==='object'?globalThis:this);
