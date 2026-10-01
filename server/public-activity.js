'use strict';
const fs=require('fs');
const path=require('path');
const crypto=require('crypto');
const REGIONS=[...'ABCDEFGHI'].flatMap(p=>[1,2,3,4,5].map(n=>p+n));
const SEAS=['U','V','W','X','Y','Z'];
const LOCATIONS=new Set([...REGIONS,...SEAS]);
const clean=(v,max=60)=>typeof v==='string'?v.replace(/[\u0000-\u001f]/g,' ').slice(0,max):'';
const integer=(v,max=100000)=>Number.isFinite(v)?Math.max(0,Math.min(max,Math.floor(v))):0;
const seat=(v,n)=>Number.isInteger(v)&&v>=0&&v<n?v:null;
const card=v=>Number.isInteger(v)&&v>=0&&v<22?v:null;
const oracle=v=>Number.isInteger(v)&&v>=0&&v<8?v:null;
const cards=v=>(Array.isArray(v)?v:[]).slice(0,200).map(card).filter(v=>v!==null);
const phase=v=>['setup','start','recruit','play','oracleMove','oracleRoll'].includes(v)?v:'play';
function projectPublicState(room){
 const snapshot=room.legacySnapshot,legacy=snapshot&&snapshot.g;
 const game=legacy||room.game||{},rule=legacy?(snapshot.rule||{}):{},facts=legacy?(snapshot.public||{}):{};
 const srcPlayers=Array.isArray(game.players)?game.players.slice(0,5).map(p=>p&&typeof p==='object'?p:{}):[],n=srcPlayers.length;
 const board=legacy?game.b:game.board;
 const players=srcPlayers.map((p,i)=>({index:i,name:clean(p.name||p.pseudo,24)||'Joueur '+(i+1),bot:!!p.bot,
   connected:!!p.bot||!!room.players.find(x=>x.playerId===(room.game?.players?.[i]||{}).playerId&&x.connected!==false),
   faction:integer(p.faction,4),portrait:['GB_A','GB_B','R_A','R_B','Y_A','Y_B'].includes(p.portrait)?p.portrait:null,
   color:/^#[0-9a-f]{6}$/i.test(p.color||'')?p.color:['#ff4fc3','#ffd92f','#6ab34c','#7ec8ff','#ff3b30'][i],
   gold:integer(p.gold),handCount:Array.isArray(p.hand)?p.hand.length:0,inPlay:cards(p.inPlay),
   score:Array.isArray(facts.scores)&&Number.isFinite(facts.scores[i])?integer(facts.scores[i],999):null}));
 const publicBoard={};for(const id of REGIONS){const cell=board&&board[id]||{},building=cell.building;
   publicBoard[id]={owner:seat(cell.owner,n),units:integer(cell.units),hostile:!!cell.hostile,building:null};
   if(building&&['Forteresse','Icenia, la cité blanche','Sundo, cité du soleil','Portail'].includes(building.type))publicBoard[id].building={type:building.type,owner:seat(building.owner,n),pair:LOCATIONS.has(building.pair)?building.pair:null};
 }
 const sea={};for(const id of SEAS){sea[id]={fleets:{}};for(let i=0;i<n;i++){const count=integer(game.sea&&game.sea[id]&&game.sea[id].fleets&&game.sea[id].fleets[i]);if(count)sea[id].fleets[i]=count}}
 const battle=rule.battle,visibleBattle=battle?{target:LOCATIONS.has(battle.target)?battle.target:null,attacker:seat(battle.attacker,n),defender:seat(battle.defender,n),attackUnits:integer(battle.attackUnits),defenseUnits:integer(battle.defOriginalUnits),
   attackPower:Number.isFinite(facts.attackPower)?integer(facts.attackPower):null,defensePower:Number.isFinite(facts.defensePower)?integer(facts.defensePower):null,
   stack:(Array.isArray(battle.stack)?battle.stack:[]).slice(0,100).map(x=>({cardId:card(x.cardId),owner:seat(x.owner,n)})).filter(x=>x.cardId!==null)}:null;
 const winner=seat(rule.gameOverState&&rule.gameOverState.winner,n);
 return {id:room.activityId,name:clean(room.name,30),mode:clean(room.mode,20),startedAt:room.startedAt,
   status:winner!==null?'finished':room.game&&room.game.status==='setup'?'setup':'playing',turn:integer(game.turn),phase:phase(game.phase),active:seat(game.active,n),victoryTarget:integer(room.victoryPoints,5),
   players,board:publicBoard,sea,dragon:LOCATIONS.has(game.dragon)?game.dragon:null,battle:visibleBattle,
   oracleActive:oracle(game.oracleActive),oracleNext:rule.divinationState?null:oracle(Array.isArray(game.oracleDeck)?game.oracleDeck.at(-1):null),
   climate:['Canicule','Vague de froid'].includes(rule.oracleClimateVisual)?rule.oracleClimateVisual:null,
   discard:cards(game.discard),deckCount:Array.isArray(game.deck)?game.deck.length:0,winner,
   connectedHumans:players.filter(p=>!p.bot&&p.connected).length};
}
function createPublicActivity({file=process.env.TRIBU_HISTORY_FILE||path.join(__dirname,'data','history.json'),now=Date.now,logger=console}={}){
 let history=[],storageError=false;const states=new Map();
 try{const parsed=JSON.parse(fs.readFileSync(file,'utf8'));if(Array.isArray(parsed))history=parsed.slice(-500)}catch(e){if(e.code!=='ENOENT'){storageError=true;logger.error('Historique TRIBU illisible:',e.message)}}
 function save(){try{fs.mkdirSync(path.dirname(file),{recursive:true});const temp=file+'.tmp';fs.writeFileSync(temp,JSON.stringify(history));fs.renameSync(temp,file);storageError=false}catch(e){storageError=true;logger.error('Historique TRIBU non enregistré:',e.message)}}
 function attach(room){if(!/^[a-f0-9-]{36}$/.test(room.activityId||''))room.activityId=crypto.randomUUID();if(!Number.isFinite(room.startedAt)||room.startedAt<=0)room.startedAt=now()}
 function summary(state){return {id:state.id,name:state.name,mode:state.mode,startedAt:state.startedAt,turn:state.turn,status:state.status,humans:state.players.filter(p=>!p.bot).length,bots:state.players.filter(p=>p.bot).length,connectedHumans:state.connectedHumans,victoryTarget:state.victoryTarget}}
 function update(room){if(!room||!room.launched||!room.game)return null;attach(room);const next=projectPublicState(room),previous=states.get(room.activityId),events=previous?previous.events.slice():[];
   const add=text=>events.push({at:now(),text});
   if(!previous)add('Observation de la partie disponible.');
   if(!previous||previous.turn!==next.turn||previous.active!==next.active)add('Tour '+next.turn+' — '+(next.players[next.active]?.name||'Installation'));
   if(previous&&previous.phase!==next.phase)add('Phase : '+({start:'début du tour',recruit:'recrutement',play:'jeu',oracleMove:'déplacement du Dragon',oracleRoll:'Oracle',setup:'placement'}[next.phase]));
   if(previous&&previous.dragon!==next.dragon)add('Le Dragon se déplace en '+next.dragon+'.');
   if(previous&&JSON.stringify(previous.board)!==JSON.stringify(next.board))add('Le plateau a été mis à jour.');
   if(next.battle&&(!previous?.battle||next.battle.target!==previous.battle.target))add('Bataille en '+(next.battle.target||'mer')+'.');
   if(previous?.battle&&!next.battle)add('La bataille est terminée.');
   if(previous&&previous.oracleActive!==next.oracleActive)add('L’Oracle actif a changé.');
   if(next.winner!==null&&previous?.winner!==next.winner)add(next.players[next.winner].name+' remporte la partie !');
   next.events=events.slice(-60);states.set(next.id,next);
   if(next.winner!==null&&!history.some(h=>h.id===next.id)){
     history.push({...summary(next),finishedAt:now(),durationSeconds:Math.max(0,Math.round((now()-next.startedAt)/1000)),winner:next.winner,players:next.players.map(p=>({name:p.name,bot:p.bot,faction:p.faction,score:p.score}))});history=history.slice(-500);save();
   }
   return next;
 }
 function list(rooms){const active=[];for(const room of rooms.values()){const state=update(room);if(state&&state.winner===null&&state.connectedHumans>0)active.push(summary(state))}return {games:active.sort((a,b)=>b.startedAt-a.startedAt).slice(0,50),recent:history.slice(-100).reverse(),historyAvailable:!storageError}}
 return {update,list,attach,get:id=>states.get(id),history:()=>history.slice()};
}
module.exports={projectPublicState,createPublicActivity};
