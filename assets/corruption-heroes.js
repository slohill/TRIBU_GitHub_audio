/* Shared hero lifecycle. The caller owns mandatory-action guards and UI confirmation. */
(function(root){
'use strict';
const replacementMessage='Vous ne pouvez avoir qu’un seul Héros en jeu. Celui en jeu va regagner votre main. Êtes-vous sûr.e de vouloir le remplacer ?';
const definitions=[{"name": "Défenseuse du peuple", "heroKey": "defenseuse", "type": "Agent — Héros", "count": 1, "extension": "corruption", "extensionKey": "hero-defenseuse", "activeAbilities": [], "effect": "Capacité « L’union fait la force » : Toutes vos Régions munies d’une seule unité ont +2 de défense.<br><br>Capacité « Givre de guerre » : Si vous êtes Griffe-Blanche, toutes vos Régions sont enneigées.", "image": "assets/images/cards/defenseuse_du_peuple.webp"}];
function install(cards){return definitions.map(d=>{const at=cards.findIndex(c=>c.extensionKey===d.extensionKey);return at>=0?at:cards.push({...d})-1})}
function current(game,actor,cards){
 const p=game.players[actor];if(!p)return null;
 const found=p.inPlay.map((id,index)=>({id,index,card:cards[id],uid:p.inPlayUID?.[index]})).filter(x=>x.card?.heroKey);
 if(found.length!==1)return null;return found[0];
}
function ownPlay(game,actor){return game.gameVersion==='corruption'&&game.active===actor&&game.phase==='play'&&!!game.players[actor]&&!game.players[actor].decimated}
function preparePlacement(game,actor,handIndex,cards){
 if(!ownPlay(game,actor))return null;
 const p=game.players[actor],id=p.hand[handIndex];if(!cards[id]?.heroKey)return null;
 const all=p.inPlay.filter(x=>cards[x]?.heroKey);if(all.length>1)return null;
 const old=current(game,actor,cards);
 // Existing instance identity is required for safe replacement confirmation.
 if(old&&old.uid===undefined)return null;
 return {actor,handIndex,id,oldId:old?.id??null,oldUid:old?.uid??null,requiresConfirmation:!!old};
}
function place(game,intent,cards,epoch,confirmed=false){
 if(!intent||!Number.isInteger(epoch))return false;
 const fresh=preparePlacement(game,intent.actor,intent.handIndex,cards);
 if(!fresh||JSON.stringify(fresh)!==JSON.stringify(intent)||fresh.requiresConfirmation&&!confirmed)return false;
 const p=game.players[intent.actor],old=current(game,intent.actor,cards);
 if(!Array.isArray(p.inPlayUID)||p.inPlayUID.length!==p.inPlay.length)return false;
 p.hand.splice(intent.handIndex,1);
 if(old){p.inPlay.splice(old.index,1);p.inPlayUID.splice(old.index,1);p.hand.push(old.id)}
 const uid='hero:'+String(game.heroSequence=(game.heroSequence||0)+1);
 p.inPlay.push(intent.id);p.inPlayUID.push(uid);
 p.heroDeployment={id:intent.id,uid,placedEpoch:epoch,ready:false,uses:{}};
 return true;
}
function deployment(game,actor,cards){
 const held=current(game,actor,cards),d=game.players[actor]?.heroDeployment;
 return held&&d&&held.id===d.id&&held.uid===d.uid?d:null;
}
function beginOwnerTurn(game,actor,cards,epoch){
 if(game.active!==actor||!Number.isInteger(epoch))return false;
 const d=deployment(game,actor,cards);if(!d||epoch<=d.placedEpoch)return false;
 d.ready=true;return true;
}
function passiveReady(game,actor,cards){return game.gameVersion==='corruption'&&!!deployment(game,actor,cards)?.ready}
function activeReady(game,actor,cards,epoch,ability){
 const held=current(game,actor,cards);
 if(!held||game.active!==actor||game.phase!==(held.card.activePhase||'play')||game.players[actor].decimated||game.players[actor].bot||!passiveReady(game,actor,cards))return false;
 const d=deployment(game,actor,cards);
 return Number.isInteger(epoch)&&epoch>d.placedEpoch&&held.card.activeAbilities?.includes(ability)&&d.uses[ability]!==epoch;
}
function consumeActive(game,actor,cards,epoch,ability){
 if(!activeReady(game,actor,cards,epoch,ability))return false;
 deployment(game,actor,cards).uses[ability]=epoch;return true;
}
function returnToHand(game,actor,cards){
 if(!ownPlay(game,actor)||game.players[actor].bot)return false;
 const held=current(game,actor,cards);if(!held)return false;
 const p=game.players[actor];p.inPlay.splice(held.index,1);p.inPlayUID.splice(held.index,1);p.hand.push(held.id);delete p.heroDeployment;return true;
}
function hasPassive(game,actor,cards,key){return passiveReady(game,actor,cards)&&current(game,actor,cards)?.card.heroKey===key}
function unionDefense(game,actor,region,cards){
 const cell=game.b[region];return cell&&cell.owner===actor&&cell.units===1&&hasPassive(game,actor,cards,'defenseuse')?2:0;
}
const api=Object.freeze({definitions,install,hasPassive,unionDefense,replacementMessage,current,preparePlacement,place,beginOwnerTurn,passiveReady,activeReady,consumeActive,returnToHand});
root.TribuHeroes=api;if(typeof module==='object'&&module.exports)module.exports=api;
})(typeof globalThis==='object'?globalThis:this);
