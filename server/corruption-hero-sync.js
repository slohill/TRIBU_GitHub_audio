'use strict';
const H=require('../assets/corruption-heroes');
const Gold=require('../assets/gold-reaction-state');
const Guild=require('../assets/corruption-guild');
const Guide=require('../assets/corruption-guide'),Revolts=require('../assets/corruption-revolts');
const shuffle=a=>{for(let i=a.length-1;i>0;i--){const j=require('crypto').randomInt(i+1);[a[i],a[j]]=[a[j],a[i]]}return a};
function action(room,actor,payload,cards){
 const snap=room.legacySnapshot,g=snap?.g,r=snap?.rule;
 const fail=error=>({ok:false,error});
 if(room.gameVersion!=='corruption'||!room.legacyMode||room.game?.status!=='playing'||!g||!r||!Number.isInteger(actor)||!g.players[actor]||g.players[actor].bot)return fail('Héros indisponibles.');
 if(payload.revision!==(room.legacyRevision||0))return fail('La partie a évolué. Vérifiez votre choix.');
 const guide=typeof payload.kind==='string'&&payload.kind.startsWith('guide');
 const guildContinue=payload.kind==='guildResolve'&&g.pendingGuildFury?.actor===actor&&r.agentModalState?.kind==='guildFury';
 const continuing=guildContinue||(guide&&r.agentModalState?.kind==='guideDivination'&&r.agentModalState.actor===actor);
 if(g.active!==actor||g.phase!==(guide?'start':'play')||g.players[actor].decimated)return fail('Action réservée à votre phase de jeu.');
 if(g.allianceLoss||g.guildCompletion||(g.pendingGuildFury&&!guildContinue)||(g.morcattAuction&&g.morcattAuction.stage!=='finished')||['gameOverState','oracleState','oracleNoticeState','divinationState','caravanState','egnoState','shadowState','portalMode'].some(k=>r[k])||(r.agentModalState&&!continuing)||(guide&&(r.goldReaction||r.paidDrawState||r.battle))||r.choiceState?.kind==='council')return fail('Une résolution est en cours.');
 if(!Number.isInteger(r.turnEpoch))return fail('Tour indisponible.');
 // Apply to a copy: stale identities and rejected confirmation never mutate the game.
 const next=JSON.parse(JSON.stringify(g));let label;
 if(guide){
  let state=r.agentModalState?JSON.parse(JSON.stringify(r.agentModalState)):null,recycled=false;
  if(payload.kind==='guideStart'){
   if(state||H.current(next,actor,cards)?.card.heroKey!=='guide'||!H.consumeActive(next,actor,cards,r.turnEpoch,'divination'))return fail('Divination indisponible.');
   const prepared=Guide.prepare(next,actor,Array.from({length:9},(_,i)=>i),shuffle);state=prepared.state;recycled=prepared.recycled;
   if(recycled&&next.revolts)Revolts.replace(next.revolts);
  }else{
   if(!continuing)return fail('Aucune Divination à résoudre.');
   if(payload.kind==='guideSelect'){if(!Guide.select(state,payload.index))return fail('Position indisponible.');}
   else if(payload.kind==='guideReset')state.order=[];
   else if(payload.kind==='guideConfirm'){
    if(payload.keep===true)state.order=[0,1,2];
    if(!Guide.confirm(next,state))return fail('Ordre incomplet ou devenu invalide.');state=null;
   }else return fail('Action de Divination inconnue.');
  }
  snap.g=next;r.agentModalState=state;
  if(recycled){r.oracleClimateVisual=null;r.oraclePendingNormalMap=false;}
  room.legacyRevision=(room.legacyRevision||0)+1;return {ok:true};
 }

 if(payload.kind==='guildStart'){
  if(H.current(next,actor,cards)?.card.heroKey!=='guild'||!H.consumeActive(next,actor,cards,r.turnEpoch,'fury'))return fail('Furie Nocturne indisponible.');
  const roll=require('crypto').randomInt(1,7),target=next.revolts?.active?.target;
  if(Number.isInteger(target)&&next.players[target]?.faction===6&&H.hasPassive(next,target,cards,'noblesse'))Revolts.suppress(next.revolts);
  next.revoltRollSequence=(next.revoltRollSequence||0)+1;
  const token=next.revolts?Revolts.capture(next.revolts,actor,roll,'roll:'+next.revoltRollSequence):null;
  const state={kind:'guildFury',actor,roll,token,pauseContext:{goldWasPaused:!!r.goldReaction?.pausedByCard,paidWasPaused:!!r.paidDrawState?.pausedByCard}};
  next.pendingGuildFury=state;r.agentModalState=state;
  if(r.goldReaction)r.goldReaction.pausedByCard=true;if(r.paidDrawState)r.paidDrawState.pausedByCard=true;
  label=next.players[actor].name+' utilise Furie Nocturne : dé '+roll+'.';
 }else if(payload.kind==='guildResolve'){
  if(!guildContinue)return fail('Aucune Furie Nocturne à résoudre.');
  const state=next.pendingGuildFury,result=Guild.resolve(next,state,payload.target,cards,n=>require('crypto').randomInt(n));
  if(!result)return fail('Cible devenue indisponible.');
  delete next.pendingGuildFury;r.agentModalState=null;next.guildCompletion={...state,success:result.success};
  const ev={seq:(r.onlineSfxSeq||0)+1,name:result.sfx,vol:.82};r.onlineSfxSeq=ev.seq;r.onlineSfxEvents=[...(r.onlineSfxEvents||[]),ev].slice(-24);
  label=result.success?(state.roll===6?next.players[actor].name+' élimine '+result.name+' de '+next.players[result.owner].name+'.':next.players[actor].name+' vole une carte dans la main de '+next.players[result.owner].name+'.'):next.players[actor].name+' : Furie Nocturne échoue.';
 }else if(payload.kind==='noblesse'){
  if(r.goldReaction||r.paidDrawState||H.current(next,actor,cards)?.card.heroKey!=='noblesse'||!H.consumeActive(next,actor,cards,r.turnEpoch,'mercantile'))return fail('Doigté mercantile indisponible.');
  const roll=require('crypto').randomInt(1,7);
  const target=next.revolts?.active?.target;
  if(Number.isInteger(target)&&next.players[target]?.faction===6&&H.hasPassive(next,target,cards,'noblesse'))Revolts.suppress(next.revolts);
  next.revoltRollSequence=(next.revoltRollSequence||0)+1;
  const heroRevolt=next.revolts?Revolts.capture(next.revolts,actor,roll,'roll:'+next.revoltRollSequence):null;
  r.goldReaction=Gold.create(actor,roll*2,'Doigté mercantile','play',next.active,r.turnEpoch,!!r.battle,{heroRevolt});
  label=next.players[actor].name+' utilise Doigté mercantile : dé '+roll+', gain de '+(roll*2)+' Or.';
 }else if(payload.kind==='place'){
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
function active(room){return room.legacySnapshot?.rule?.agentModalState?.kind==='guideDivination'}
function mergeProposals(room,incoming){
 const rule=room.legacySnapshot.rule,previous=rule.commerceDeals||[],deals=incoming.rule?.commerceDeals;
 if(!Array.isArray(deals))return true;
 if(deals.some(d=>d.status==='done'&&previous.find(x=>x.id===d.id)?.status!=='done'))return false;
 rule.commerceDeals=deals;rule.commerceSeq=incoming.rule.commerceSeq;return true;
}
module.exports={action,active,mergeProposals};

