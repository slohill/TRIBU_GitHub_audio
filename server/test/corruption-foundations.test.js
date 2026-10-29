const {test}=require('node:test');
const assert=require('node:assert/strict');
const C=require('../../assets/corruption.js');
test('NPC allocation preserves base, exact counts, existing allocation and round-trip',()=>{
 const game={gameVersion:'base',b:Object.fromEntries(Array.from({length:9},(_,i)=>[i,{originalHostile:true}]))};
 assert.equal(C.assignNpcs(game),false);
 game.gameVersion='corruption';assert.equal(C.assignNpcs(game,()=>0.5),true);
 for(const [tribe,n] of Object.entries(C.tribes))assert.equal(Object.values(game.b).filter(c=>c.npcTribe===tribe).length,n);
 const saved=JSON.stringify(game);assert.equal(C.assignNpcs(game),false);assert.equal(JSON.stringify(game),saved);
 const restored=JSON.parse(saved);assert.equal(C.assignNpcs(restored),false);assert.equal(JSON.stringify(restored),saved);
});
test('Incomplete map cannot partially assign tribes',()=>{
 const game={gameVersion:'corruption',b:{A:{originalHostile:true}}};
 assert.throws(()=>C.assignNpcs(game));assert.equal(game.b.A.npcTribe,undefined);
});
test('Additional portal retains legacy identity and stable indices, only distinct card token changes',()=>{
 const cards=[{name:'Other',count:3},{name:'Portails',count:1,type:'Permanent',effect:'Legacy'}];
 const original=JSON.stringify(cards);const id=C.installPortal(cards);
 assert.equal(id,2);assert.equal(JSON.stringify(cards.slice(0,2)),original);
 assert.equal(cards[id].name,'Portails');assert.equal(cards[id].effect,'Legacy');
 assert.equal(C.installPortal(cards),id);assert.equal(cards.length,3);
 assert.equal(C.portalImage(cards[1]),'assets/images/tokens/portail.png');
 assert.equal(C.portalImage(cards[id]),'assets/images/tokens/portail2.webp');
});
