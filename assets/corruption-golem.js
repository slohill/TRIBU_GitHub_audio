/* Golem selections: actual player units, one nonadjacent land origin. */
(function(root){'use strict';
function neighbors(game,data,id){
 const n=data.SEA[id]?[...data.SEA[id],...data.PORTS[id]]:[...data.R[id][3],...data.R[id][4]];
 const building=game.b[id]?.building,mate=game.b[building?.pair]?.building;
 if(building?.type==='Portail'&&mate?.type==='Portail'&&mate.pair===id&&mate.cardId===building.cardId&&!n.includes(building.pair))n.push(building.pair);
 return n;
}
function battles(rule){return [...new Set([rule.battle,...(rule.battleStack||[]).map(x=>x.battle),rule.egnoState?.parentBattle].filter(Boolean))]}
function plan(game,actor,roll,battles,neighbors){
 const own=new Set(Object.keys(game.b).filter(r=>game.b[r].owner===actor));
 Object.keys(game.sea).forEach(r=>{if(game.sea[r].fleets[actor]>0)own.add(r)});
 battles.forEach(b=>{if(!b.environmentResolved&&b.attacker===actor)(b.attackOrigins||[]).forEach(o=>{if(o.moves.length)own.add(o.region)})});
 const excluded=new Set(own);own.forEach(r=>neighbors(r).forEach(n=>excluded.add(n)));
 const regions=[];
 for(const region of Object.keys(game.b)){
  if(excluded.has(region))continue;const c=game.b[region],groups=[];
  if(c.owner!==null&&c.units>0)groups.push({key:'stationed',kind:'stationed',player:c.owner,available:c.units});
  battles.forEach((b,battleIndex)=>{if(b.environmentResolved)return;(b.attackOrigins||[]).forEach((o,originIndex)=>{
   if(o.region===region&&o.moves.length)groups.push({key:'battle:'+battleIndex+':'+originIndex,kind:'attacking',player:b.attacker,battleIndex,originIndex,target:b.target,available:o.moves.length,moves:o.moves.slice()});
  })});
  if(groups.length)regions.push({region,groups,required:Math.min(roll,groups.reduce((n,g)=>n+g.available,0))});
 }
 return {kind:'golem',player:actor,roll,regions,origin:null,chosen:{},confirmed:false};
}
function choose(p,region,key){
 const row=p.regions.find(r=>r.region===region),g=row?.groups.find(g=>g.key===key);
 if(p.confirmed||!g||p.origin!==null&&p.origin!==region||Object.values(p.chosen).reduce((a,b)=>a+b,0)>=row.required||(p.chosen[key]||0)>=g.available)return false;
 p.origin=region;p.chosen[key]=(p.chosen[key]||0)+1;return true;
}
function reset(p){if(p.confirmed)return false;p.origin=null;p.chosen={};return true}
function commands(p){
 const row=p.regions.find(r=>r.region===p.origin);
 if(p.confirmed||!row||Object.values(p.chosen).reduce((a,b)=>a+b,0)!==row.required||!Object.entries(p.chosen).every(([k,n])=>Number.isInteger(n)&&n>0&&n<=(row.groups.find(g=>g.key===k)?.available||0)))return null;
 return row.groups.filter(g=>p.chosen[g.key]).map(g=>({region:row.region,...g,loss:p.chosen[g.key]}));
}
function validate(p,game,battles,neighbors){
 if(!Number.isInteger(p.roll)||p.roll<1||p.roll>6||!commands(p))return false;
 const fresh=plan(game,p.player,p.roll,battles,neighbors).regions.find(r=>r.region===p.origin);
 return !!fresh&&JSON.stringify(fresh)===JSON.stringify(p.regions.find(r=>r.region===p.origin));
}
const api=Object.freeze({plan,choose,reset,commands,validate,neighbors,battles});root.TribuGolem=api;if(typeof module==='object'&&module.exports)module.exports=api;
})(typeof globalThis==='object'?globalThis:this);
