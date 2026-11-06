'use strict';
const H=require('../assets/corruption-heroes');
function action(room,actor,payload,cards){
 const snap=room.legacySnapshot,g=snap?.g,r=snap?.rule;
 const fail=error=>({ok:false,error});
 if(room.gameVersion!=='corruption'||!room.legacyMode||room.game?.status!=='playing'||!g||!r||!Number.isInteger(actor)||!g.players[actor]||g.players[actor].bot)return fail('Héros indisponibles.');
 if(payload.revision!==(room.legacyRevision||0))return fail('La partie a évolué. Vérifiez votre choix.');
 if(g.active!==actor||g.phase!=='play'||g.players[actor].decimated)return fail('Action réservée à votre phase de jeu.');
 if(g.allianceLoss||g.pendingGuildFury||(g.morcattAuction&&g.morcattAuction.stage!=='finished')||['gameOverState','oracleState','oracleNoticeState','divinationState','caravanState','egnoState','shadowState','portalMode','agentModalState'].some(k=>r[k])||r.choiceState?.kind==='council')return fail('Une résolution est en cours.');
 if(!Number.isInteger(r.turnEpoch))return fail('Tour indisponible.');
 // Apply to a copy: stale identities and rejected confirmation never mutate the game.
 const next=JSON.parse(JSON.stringify(g));let label;
 if(payload.kind==='place'){
  const intent=payload.intent;
  if(!intent||intent.actor!==actor||!H.place(next,intent,cards,r.turnEpoch,payload.confirmed===true))return fail('Ce Héros ou ce remplacement n’est plus disponible.');
  label=next.players[actor].name+' met '+cards[intent.id].name+' en jeu.';
 }else if(payload.kind==='return'){
  const held=H.current(next,actor,cards);
  if(!held||held.uid!==payload.uid||held.id!==payload.id||!H.returnToHand(next,actor,cards))return fail('Ce Héros n’est plus en jeu.');
  label=next.players[actor].name+' reprend '+cards[held.id].name+' en main.';
 }else return fail('Action de Héros inconnue.');
 (next.log||(next.log=[])).unshift(label);
 (next.publicLog||(next.publicLog=[])).unshift(label);
 if(snap.public)snap.public.journal=next.publicLog.slice();
 snap.g=next;room.legacyRevision=(room.legacyRevision||0)+1;
 return {ok:true};
}
module.exports={action};
