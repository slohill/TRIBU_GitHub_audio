'use strict';
const H=require('../assets/corruption-heroes'),Alliances=require('../assets/corruption-alliances');
const BattleAlliances=require('../assets/corruption-battle-alliances');
const Gold=require('../assets/gold-reaction-state'),Theft=require('../assets/corruption-theft');
const Guild=require('../assets/corruption-guild'),Golem=require('../assets/corruption-golem');
const Guide=require('../assets/corruption-guide'),Revolts=require('../assets/corruption-revolts');
const shuffle=a=>{for(let i=a.length-1;i>0;i--){const j=require('crypto').randomInt(i+1);[a[i],a[j]]=[a[j],a[i]]}return a};
function action(room,actor,payload,cards,mapData){
 const snap=room.legacySnapshot,g=snap?.g,r=snap?.rule;
 const fail=error=>({ok:false,error});
 if(room.gameVersion!=='corruption'||!room.legacyMode||room.game?.status!=='playing'||!g||!r||!Number.isInteger(actor)||!g.players[actor]||g.players[actor].bot)return fail('Héros indisponibles.');
 if(payload.revision!==(room.legacyRevision||0))return fail('La partie a évolué. Vérifiez votre choix.');
 const guide=typeof payload.kind==='string'&&payload.kind.startsWith('guide');
 const guildContinue=payload.kind==='guildResolve'&&g.pendingGuildFury?.actor===actor&&r.agentModalState?.kind==='guildFury';
 const golemContinue=(typeof payload.kind==='string'&&payload.kind.startsWith('golem'))&&g.allianceLoss?.plan.kind==='golem'&&g.allianceLoss.plan.player===actor;
 const allianceContinue=typeof payload.kind==='string'&&payload.kind.startsWith('alliance')&&['alliance','ogre'].includes(g.allianceLoss?.plan.kind)&&g.allianceLoss.plan.player===actor;
 const corruption=typeof payload.kind==='string'&&payload.kind.startsWith('corruption');
 const theftContinue=corruption&&r.agentModalState?.kind==='corruption'&&r.agentModalState.actor===actor;
 const elf=typeof payload.kind==='string'&&payload.kind.startsWith('elf');
 const ogre=payload.kind==='ogreRoll';
 const continuing=theftContinue||guildContinue||(guide&&r.agentModalState?.kind==='guideDivination'&&r.agentModalState.actor===actor);
 if((!elf&&!ogre&&!corruption&&!allianceContinue&&(g.active!==actor||g.phase!==(guide?'start':'play')))||g.phase==='setup'||g.players[actor].decimated)return fail('Action réservée à votre phase de jeu.');
 if((g.allianceLoss&&!golemContinue&&!allianceContinue)||g.guildCompletion||(g.pendingGuildFury&&!guildContinue)||(g.morcattAuction&&g.morcattAuction.stage!=='finished')||['gameOverState','oracleState','oracleNoticeState','divinationState','caravanState','egnoState','shadowState','portalMode'].some(k=>r[k])||(r.agentModalState&&!continuing)||(guide&&(r.goldReaction||r.paidDrawState||r.battle))||r.choiceState?.kind==='council')return fail('Une résolution est en cours.');
 if(!Number.isInteger(r.turnEpoch))return fail('Tour indisponible.');
 // Apply to a copy: stale identities and rejected confirmation never mutate the game.
 const next=JSON.parse(JSON.stringify(g));let label;
 if(elf){
  const b=r.battle,state=b?.elfChoice;
  if(!mapData||state?.player!==actor||state.stage==='authorized'||!BattleAlliances.elfDestinations(next,b,cards,mapData).length)return fail('Fuite indisponible.');
  if(payload.kind==='elfChoose')state.stage='destination';
  else if(payload.kind==='elfDefend'){state.stage='authorized';state.action='defend';}
  else if(payload.kind==='elfFlee'){
   if(state.stage!=='destination'||!BattleAlliances.elfDestinations(next,b,cards,mapData).includes(payload.destination))return fail('Destination interdite.');state.stage='authorized';state.action='flee';state.destination=payload.destination;
  }else return fail('Action inconnue.');
  if(state.stage==='authorized')state.onlineId='elf:'+(room.legacyRevision+1)+':'+actor;
  room.legacyRevision=(room.legacyRevision||0)+1;return {ok:true};
 }
 if(ogre){
  const b=r.battle;
  if(!b||b.attacker!==actor||b.environmentResolved||b.elfChoice||r.goldReaction||next.players[actor].ogreUsedEpoch===r.turnEpoch||!Alliances.bonus(next,actor,cards,'ogres',1))return fail('Ogres indisponibles.');
  const roll=require('crypto').randomInt(1,7);next.players[actor].ogreUsedEpoch=r.turnEpoch;b.ogrePower={actor,roll,cancelled:false,settled:false};
  const target=next.revolts?.active?.target;
  if(Number.isInteger(target)&&next.players[target]?.faction===6&&H.hasPassive(next,target,cards,'noblesse'))Revolts.suppress(next.revolts);
  next.revoltRollSequence=(next.revoltRollSequence||0)+1;
  const token=next.revolts?Revolts.capture(next.revolts,actor,roll,'roll:'+next.revoltRollSequence):null;
  if(token)(next.noblesseRevolts||(next.noblesseRevolts=[])).push(token);
  label=next.players[actor].name+' invoque les Ogres : dé '+roll+', +'+roll+' Attaque pour cette bataille.';
 }else if(corruption){
  if(payload.kind==='corruptionOpen'){
   const cardId=next.players[actor].hand[payload.handIndex],targets=Theft.targets(next,actor,cards);
   if(theftContinue||cardId!==payload.id||cards[cardId]?.extensionKey!=='corruption-theft'||next.players[actor].gold<5||!targets.length)return fail('Corruption indisponible.');
   r.agentModalState={kind:'corruption',actor,cardId,targets,pauseContext:{goldWasPaused:!!r.goldReaction?.pausedByCard,paidWasPaused:!!r.paidDrawState?.pausedByCard}};
   if(r.goldReaction)r.goldReaction.pausedByCard=true;if(r.paidDrawState)r.paidDrawState.pausedByCard=true;
   room.legacyRevision=(room.legacyRevision||0)+1;return {ok:true};
  }
  if(!theftContinue)return fail('Aucune Corruption à résoudre.');
  const state=r.agentModalState;
  if(payload.kind==='corruptionCancel'){
   r.agentModalState=null;
   if(r.goldReaction&&!state.pauseContext.goldWasPaused){delete r.goldReaction.pausedByCard;r.goldReaction.seconds=10}
   if(r.paidDrawState&&!state.pauseContext.paidWasPaused){delete r.paidDrawState.pausedByCard;r.paidDrawState.seconds=10}
   room.legacyRevision=(room.legacyRevision||0)+1;return {ok:true};
  }
  if(payload.kind!=='corruptionResolve')return fail('Action inconnue.');
  const target=Theft.steal(next,state,payload.victim,payload.id,cards);if(!target)return fail('Cette alliance n’est plus disponible.');
  r.agentModalState=null;
  next.allianceSequence=(next.allianceSequence||0)+1;
  const plan=Alliances.createLossPlan(next,target.player,target.tribe,Golem.battles(r));plan.kind='alliance';plan.onlineId='corruption:'+next.allianceSequence+':'+target.player;
  next.allianceLoss={plan,stage:'selection',queue:[],...state.pauseContext};
  if(next.players[target.player].bot){for(const row of plan.regions)for(const group of row.groups)while(Alliances.choose(plan,row.region,group.key)){}plan.resolver=actor;next.allianceLoss.stage='authorized';}
  [r.goldReaction,...(r.goldReactionStack||[])].forEach(gain=>Theft.refreshDwarfGain(next,gain,cards));
  label=next.players[actor].name+' joue Corruption et vole '+cards[target.id].name+' à '+next.players[target.player].name+'.';
 }else if(guide){
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
 }else if(typeof payload.kind==='string'&&payload.kind.startsWith('alliance')){
  if(payload.kind==='alliancePlace'){
   if(allianceContinue)return fail('Pertes d’alliance en cours.');
   const placed=Alliances.place(next,actor,payload.handIndex,payload.id,cards);
   if(!placed)return fail('Alliance indisponible.');
   if(placed.oldTribe){
    const plan=Alliances.createLossPlan(next,actor,placed.oldTribe,Golem.battles(r));plan.kind='alliance';plan.onlineId='alliance:'+next.allianceSequence+':'+actor;
    next.allianceLoss={plan,stage:'selection',queue:[],goldWasPaused:!!r.goldReaction?.pausedByCard,paidWasPaused:!!r.paidDrawState?.pausedByCard};
    if(r.goldReaction)r.goldReaction.pausedByCard=true;if(r.paidDrawState)r.paidDrawState.pausedByCard=true;
   }
   label=next.players[actor].name+' met '+cards[placed.id].name+' en jeu.';
  }else{
   const state=next.allianceLoss;
   if(!allianceContinue||state.stage!=='selection')return fail('Choix indisponible.');
   if(payload.kind==='allianceChoose'){if(!Alliances.choose(state.plan,payload.region,payload.group))return fail('Groupe indisponible.');}
   else if(payload.kind==='allianceReset')state.plan.regions.forEach(row=>Alliances.reset(state.plan,row.region));
   else if(payload.kind==='allianceConfirm'){
    if(!Alliances.validate(state.plan,next,Golem.battles(r)))return fail('Pertes incomplètes ou devenues invalides.');state.stage='authorized';
   }else return fail('Action d’alliance inconnue.');
   snap.g=next;room.legacyRevision=(room.legacyRevision||0)+1;return {ok:true};
  }
 }else if((typeof payload.kind==='string'&&payload.kind.startsWith('golem'))){
  if(!mapData)return fail('Carte indisponible.');
  const battles=Golem.battles(r),neighbors=id=>Golem.neighbors(next,mapData,id);
  if(payload.kind==='golemStart'){
   if(golemContinue||H.current(next,actor,cards)?.card.heroKey!=='golem'||!H.activeReady(next,actor,cards,r.turnEpoch,'violence')||!Golem.plan(next,actor,6,battles,neighbors).regions.length)return fail('Violence aveugle indisponible.');
   H.consumeActive(next,actor,cards,r.turnEpoch,'violence');
   const roll=require('crypto').randomInt(1,7),plan=Golem.plan(next,actor,roll,battles,neighbors),target=next.revolts?.active?.target;
   if(Number.isInteger(target)&&next.players[target]?.faction===6&&H.hasPassive(next,target,cards,'noblesse'))Revolts.suppress(next.revolts);
   next.revoltRollSequence=(next.revoltRollSequence||0)+1;
   plan.revoltToken=next.revolts?Revolts.capture(next.revolts,actor,roll,'roll:'+next.revoltRollSequence):null;
   plan.onlineId='golem:'+r.turnEpoch+':'+next.revoltRollSequence+':'+actor;
   next.allianceLoss={plan,stage:'selection',queue:[],goldWasPaused:!!r.goldReaction?.pausedByCard,paidWasPaused:!!r.paidDrawState?.pausedByCard};
   if(r.goldReaction)r.goldReaction.pausedByCard=true;if(r.paidDrawState)r.paidDrawState.pausedByCard=true;
   label=next.players[actor].name+' utilise Violence aveugle : dé '+roll+'.';
  }else{
   const state=next.allianceLoss;
   if(!golemContinue||state.stage!=='selection')return fail('Choix indisponible.');
   if(payload.kind==='golemChoose'){if(!Golem.choose(state.plan,payload.region,payload.group))return fail('Groupe indisponible.');}
   else if(payload.kind==='golemReset')Golem.reset(state.plan);
   else if(payload.kind==='golemConfirm'){
    if(!Golem.validate(state.plan,next,battles,neighbors))return fail('Pertes incomplètes ou devenues invalides.');state.stage='authorized';
   }else return fail('Action du Golem inconnue.');
   snap.g=next;room.legacyRevision=(room.legacyRevision||0)+1;return {ok:true};
  }
 }else if(payload.kind==='guildStart'){
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
function golemActive(room){return ['golem','alliance','ogre'].includes(room.legacySnapshot?.g?.allianceLoss?.plan.kind)}
function acceptGolemResolution(room,actor,incoming){
 const state=room.legacySnapshot?.g?.allianceLoss;
 return ['golem','alliance','ogre'].includes(state?.plan.kind)&&state.stage==='authorized'&&actor===(state.plan.resolver??state.plan.player)&&incoming.g?.[state.plan.kind==='golem'?'golemResolved':'allianceResolved']===state.plan.onlineId;
}
function elfAuthorized(room){return room.legacySnapshot?.rule?.battle?.elfChoice?.stage==='authorized'}
function acceptElfResolution(room,actor,incoming){const state=room.legacySnapshot?.rule?.battle?.elfChoice;return elfAuthorized(room)&&actor===state.player&&incoming.g?.elfResolved===state.onlineId}
module.exports={action,active,mergeProposals,golemActive,acceptGolemResolution,elfAuthorized,acceptElfResolution};

