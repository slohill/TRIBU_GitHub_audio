/* Alliance rules shared by legacy integration and server validation.
   Loss plans never mutate the board or battle objects. */
(function(root){
'use strict';
const definitions=[
 {name:'Accord avec les nains',tribe:'dwarves',count:3,image:'accord_avec_les_nains.webp'},
 {name:'Armistice avec les humains',tribe:'humans',count:3,image:'armistice_avec_les_humains.webp'},
 {name:'Cohabitation elfique',tribe:'elves',count:4,image:'cohabitation_elfique.webp'},
 {name:'Pacte avec les Ogres',tribe:'ogres',count:1,image:'pacte_avec_les_ogres.webp'}
];
function alliance(player,cards){
 const held=(player.inPlay||[]).map(id=>({id,card:cards[id]})).filter(x=>x.card?.allianceTribe);
 if(held.length>1)throw new Error('Un seul accord d’alliance peut être en jeu.');
 return held[0]||null;
}
function peaceful(game,player,region,cards){
 if(game.gameVersion!=='corruption')return false;
 const c=game.b[region],a=alliance(game.players[player],cards);
 return !!c&&c.owner===null&&c.hostile===true&&!!a&&c.npcTribe===a.card.allianceTribe;
}
function ownedTribe(game,player,tribe){return Object.keys(game.b).filter(r=>game.b[r].owner===player&&game.b[r].npcTribe===tribe)}
function bonus(game,player,cards,tribe,perRegion){
 if(game.gameVersion!=='corruption')return 0;
 const a=alliance(game.players[player],cards);
 return a?.card.allianceTribe===tribe?ownedTribe(game,player,tribe).length*perRegion:0;
}
function createLossPlan(game,player,tribe,battles){
 const regions=[];
 for(const [region,cell]of Object.entries(game.b)){
  if(cell.npcTribe!==tribe)continue;
  const groups=[];
  if(cell.owner===player&&cell.units>0)groups.push({key:'stationed',kind:'stationed',available:cell.units});
  battles.forEach((b,battleIndex)=>{
   if(b.environmentResolved||b.attacker!==player)return;
   (b.attackOrigins||[]).forEach((o,originIndex)=>{
    if(o.region===region&&o.moves.length)groups.push({key:'battle:'+battleIndex+':'+originIndex,kind:'attacking',battleIndex,originIndex,target:b.target,available:o.moves.length,moves:o.moves.slice()});
   });
  });
  // An emptied origin can retain committed troops. A region owned by an opponent is excluded.
  if(cell.owner!==player&&!(cell.owner===null&&groups.some(g=>g.kind==='attacking')))continue;
  const total=groups.reduce((n,g)=>n+g.available,0);if(!total)continue;
  const required=Math.min(5,total),chosen={};
  if(total<=5)groups.forEach(g=>chosen[g.key]=g.available);
  regions.push({region,groups,total,required,chosen,automatic:total<=5});
 }
 return {player,tribe,regions,confirmed:false};
}
function selected(row){return Object.values(row.chosen).reduce((n,v)=>n+v,0)}
function choose(plan,region,key){
 if(plan.confirmed)return false;
 const row=plan.regions.find(r=>r.region===region),group=row?.groups.find(g=>g.key===key);
 if(!row||!group||row.automatic||selected(row)>=row.required||(row.chosen[key]||0)>=group.available)return false;
 row.chosen[key]=(row.chosen[key]||0)+1;return true;
}
function reset(plan,region){
 const row=plan.regions.find(r=>r.region===region);
 if(plan.confirmed||!row||row.automatic)return false;row.chosen={};return true;
}
function ready(plan){
 return !plan.confirmed&&plan.regions.every(r=>
  selected(r)===r.required&&Object.entries(r.chosen).every(([key,n])=>{
   const group=r.groups.find(g=>g.key===key);
   return !!group&&Number.isSafeInteger(n)&&n>=0&&n<=group.available;
  })
 );
}
function commands(plan){
 if(!ready(plan))return null;
 return plan.regions.flatMap(row=>row.groups.filter(g=>row.chosen[g.key]>0).map(g=>({region:row.region,...g,loss:row.chosen[g.key]})));
}
function validate(plan,game,battles){
 if(game.gameVersion!=='corruption'||!Number.isInteger(plan.player)||!game.players[plan.player]||!definitions.some(d=>d.tribe===plan.tribe)||!ready(plan))return false;
 const fresh=createLossPlan(game,plan.player,plan.tribe,battles);
 if(fresh.regions.length!==plan.regions.length||new Set(plan.regions.map(r=>r.region)).size!==plan.regions.length)return false;
 return plan.regions.every(row=>{
  const next=fresh.regions.find(r=>r.region===row.region);
  if(!next||next.total!==row.total||next.required!==row.required||next.groups.length!==row.groups.length||new Set(row.groups.map(g=>g.key)).size!==row.groups.length)return false;
  return row.groups.every(g=>{
   const n=next.groups.find(n=>n.key===g.key);
   return n&&['kind','available','target','battleIndex','originIndex'].every(k=>n[k]===g[k])&&JSON.stringify(n.moves)===JSON.stringify(g.moves);
  });
 });
}

const api=Object.freeze({definitions,alliance,peaceful,ownedTribe,bonus,createLossPlan,choose,reset,ready,commands,validate});
root.TribuAlliances=api;if(typeof module==='object'&&module.exports)module.exports=api;
})(typeof globalThis==='object'?globalThis:this);
