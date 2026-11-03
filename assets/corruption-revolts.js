/* Révoltes timing and provisional selection; no board mutations here. */
(function(root){
'use strict';
const definition=Object.freeze({name:'Révoltes',count:1,image:'assets/images/cards/revoltes.webp',effect:'Chaque joueur.euse faisant 3 ou 4 au dé doit choisir une Région du.de la joueur.euse ayant activé les révoltes et en retirer au choix une ou deux unités.'});
function create(){return {epoch:0,active:null,queue:[],seen:{}}}
function activate(state,target,oracleId){state.epoch++;state.active={target,oracleId,epoch:state.epoch,suppressed:false};state.queue=[];state.seen={}}
function replace(state){state.epoch++;state.active=null;state.queue=[];state.seen={}}
function suppress(state){if(state.active)state.active.suppressed=true;state.queue=[]}
function capture(state,actor,value,eventId){
 const a=state.active;if(!a||a.suppressed||![3,4].includes(value))return null;
 if(!Number.isInteger(actor)||actor<0||typeof eventId!=='string'||!eventId)return null;
 return {epoch:a.epoch,target:a.target,oracleId:a.oracleId,actor,value,eventId};
}
function current(state,token){const a=state.active;return !!token&&!!a&&!a.suppressed&&token.epoch===a.epoch&&token.target===a.target&&token.oracleId===a.oracleId}
function afterAction(state,token,hasTargets=true){
 if(!current(state,token)||Object.prototype.hasOwnProperty.call(state.seen,token.eventId))return false;
 Object.defineProperty(state.seen,token.eventId,{value:true,enumerable:true,configurable:true});
 if(!hasTargets)return false;state.queue.push({...token});return true;
}
function next(state){while(state.queue.length){const t=state.queue.shift();if(current(state,t))return t}return null}
function plan(game,target,battles){
 const regions=[];
 const ids=new Set([...Object.keys(game.b),...Object.keys(game.sea)]);
 for(const b of battles)for(const o of b.attackOrigins||[])ids.add(o.region);
 for(const region of ids){
  const groups=[],sea=!!game.sea[region],cell=game.b[region];
  const count=sea?(game.sea[region].fleets[target]||0):(cell?.owner===target?cell.units:0);
  if(count>0)groups.push({key:'stationed',kind:'stationed',available:count});
  battles.forEach((b,battleIndex)=>{
   if(b.environmentResolved||b.attacker!==target)return;
   (b.attackOrigins||[]).forEach((o,originIndex)=>{
    if(o.region===region&&o.moves.length)groups.push({key:'battle:'+battleIndex+':'+originIndex,kind:'attacking',battleIndex,originIndex,target:b.target,available:o.moves.length,moves:o.moves.slice()});
   });
  });
  if(groups.length)regions.push({region,sea,groups});
 }
 return {target,regions,origin:null,chosen:{},confirmed:false};
}
function count(p){return Object.values(p.chosen).reduce((a,b)=>a+b,0)}
function choose(p,region,key){
 if(p.confirmed||p.origin!==null&&p.origin!==region||count(p)>=2)return false;
 const row=p.regions.find(r=>r.region===region),group=row?.groups.find(g=>g.key===key);
 if(!group||(p.chosen[key]||0)>=group.available)return false;
 p.origin=region;p.chosen[key]=(p.chosen[key]||0)+1;return true;
}
function reset(p){if(p.confirmed)return false;p.origin=null;p.chosen={};return true}
function commands(p){
 if(p.confirmed||![1,2].includes(count(p)))return null;
 const row=p.regions.find(r=>r.region===p.origin);if(!row)return null;
 if(!Object.entries(p.chosen).every(([key,n])=>Number.isInteger(n)&&n>0&&n<=(row.groups.find(g=>g.key===key)?.available||0)))return null;
 return row.groups.filter(g=>p.chosen[g.key]).map(g=>({region:row.region,sea:row.sea,...g,loss:p.chosen[g.key]}));
}
function validate(p,game,battles){
 if(!commands(p))return false;
 const fresh=plan(game,p.target,battles),row=fresh.regions.find(r=>r.region===p.origin),before=p.regions.find(r=>r.region===p.origin);
 return !!row&&JSON.stringify(row)===JSON.stringify(before);
}
const api=Object.freeze({definition,create,activate,replace,suppress,capture,afterAction,next,plan,choose,reset,commands,validate});
root.TribuRevolts=api;if(typeof module==='object'&&module.exports)module.exports=api;
})(typeof globalThis==='object'?globalThis:this);
