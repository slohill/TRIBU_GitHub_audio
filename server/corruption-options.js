'use strict';
// Experimental rooms are opt-in; full Corruption gameplay is not enabled yet.
function version(value){return value==='corruption'?'corruption':'base'}
function seats(value){return version(value)==='corruption'?6:5}
function roomOptions(payload,enabled=false){
 if(payload.gameVersion!=null&&!['base','corruption'].includes(payload.gameVersion))throw new Error('Version de jeu inconnue.');
 const gameVersion=version(payload.gameVersion);
 if(gameVersion==='corruption'&&!enabled)throw new Error('Corruption est encore en cours d’intégration.');
 if((payload.mode==='6h'||Number(payload.maxHumans)>5)&&gameVersion!=='corruption')throw new Error('Six joueurs nécessitent Corruption.');
 const maxHumans=Math.max(2,Math.min(seats(gameVersion),Math.floor(Number(payload.maxHumans)||3)));
 const bots=Math.max(0,Math.min(seats(gameVersion)-maxHumans,Math.floor(Number(payload.bots)||0)));
 return {gameVersion,maxHumans,bots};
}
module.exports={version,seats,roomOptions};
