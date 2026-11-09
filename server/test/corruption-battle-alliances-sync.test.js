const test=require('node:test'),assert=require('node:assert/strict');
const A=require('../../assets/corruption-alliances'),B=require('../../assets/corruption-battle-alliances'),R=require('../../assets/corruption-revolts'),S=require('../corruption-hero-sync');
const cards=[];A.install(cards);const elf=cards.findIndex(c=>c.allianceTribe==='elves'),ogre=cards.findIndex(c=>c.allianceTribe==='ogres');
const data={R:{A:[0,0,0,['B','C'],[]],B:[0,0,0,['A'],[]],C:[0,0,0,['A'],[]],D:[0,0,0,[],[]]},SEA:{},PORTS:{}};
function fixture(){return {gameVersion:'corruption',legacyMode:true,game:{status:'playing'},legacyRevision:0,legacySnapshot:{g:{gameVersion:'corruption',active:0,phase:'play',players:[{name:'A',hand:[],inPlay:[ogre],inPlayUID:['ogre']},{name:'B',hand:[],inPlay:[elf],inPlayUID:['elf']}],b:{A:{owner:1,units:4,npcTribe:'elves'},B:{owner:null,units:0,hostile:true,npcTribe:'elves'},C:{owner:0,units:2,npcTribe:'ogres'},D:{owner:null,units:0,hostile:false}},sea:{},discard:[]},rule:{turnEpoch:2,battle:{kind:'land',attacker:0,defender:1,target:'A',attackUnits:3,attackOrigins:[{region:'C',moves:[1,1,1]}],elfChoice:{player:1,stage:'choice'}}}}}}
const send=(r,actor,kind,extra={})=>S.action(r,actor,{kind,revision:r.legacyRevision,...extra},cards,data);
test('Elf defender outside own turn: persisted choice, destination revalidation, replay blocked',()=>{
 const r=fixture();assert.equal(send(r,0,'elfChoose').ok,false);assert(send(r,1,'elfChoose').ok);
 assert.equal(r.legacySnapshot.rule.battle.elfChoice.stage,'destination');
 assert.equal(send(r,1,'elfFlee',{destination:'C'}).ok,false);assert(send(r,1,'elfFlee',{destination:'B'}).ok);
 assert.equal(r.legacySnapshot.rule.battle.elfChoice.stage,'authorized');assert.equal(send(r,1,'elfFlee',{destination:'B'}).ok,false);
 assert(S.elfAuthorized(r));const receipt={g:{elfResolved:r.legacySnapshot.rule.battle.elfChoice.onlineId}};
 assert(S.acceptElfResolution(r,1,receipt));assert(!S.acceptElfResolution(r,0,receipt));assert(!S.acceptElfResolution(r,1,{g:{}}));
 assert.equal(r.legacySnapshot.g.b.A.units,4); // Legacy engine applies only after authorization.
 const d=fixture();assert(send(d,1,'elfDefend').ok);assert.equal(d.legacySnapshot.rule.battle.elfChoice.action,'defend');
 const stale=fixture();assert(send(stale,1,'elfChoose').ok);stale.legacySnapshot.g.players[1].inPlay=[];assert.equal(send(stale,1,'elfFlee',{destination:'B'}).ok,false);
});
test('Elf destinations use only a matching Portal pair',()=>{
 const r=fixture(),g=r.legacySnapshot.g,b=r.legacySnapshot.rule.battle;
 g.b.A.building={type:'Portail',pair:'D',cardId:22};g.b.D.building={type:'Portail',pair:'A',cardId:22};
 assert(B.elfDestinations(g,b,cards,data).includes('D'));g.b.D.building.cardId=23;assert(!B.elfDestinations(g,b,cards,data).includes('D'));
});
test('Ogre server roll: attack only, once per epoch, no roll during Elf choice or another resolution',()=>{
 const r=fixture();assert.equal(send(r,0,'ogreRoll').ok,false);delete r.legacySnapshot.rule.battle.elfChoice;
 assert.equal(send(r,1,'ogreRoll').ok,false);assert(send(r,0,'ogreRoll').ok);
 const b=r.legacySnapshot.rule.battle;assert(b.ogrePower.roll>=1&&b.ogrePower.roll<=6);assert.equal(send(r,0,'ogreRoll').ok,false);
 r.legacySnapshot.rule.turnEpoch++;r.legacySnapshot.g.players[0].inPlay=[];assert.equal(send(r,0,'ogreRoll').ok,false);
});
test('Ogre losses are selected by the owner and authorized before legacy consequences',()=>{
 const r=fixture(),g=r.legacySnapshot.g;delete r.legacySnapshot.rule.battle.elfChoice;
 const plan=A.createOgreLossPlan(g,1,['A'],[]);plan.onlineId='ogre:1';g.allianceLoss={plan,stage:'selection'};
 assert.equal(send(r,0,'allianceChoose',{region:'A',group:'stationed'}).ok,false);
 assert.equal(send(r,1,'allianceConfirm').ok,false);assert(send(r,1,'allianceChoose',{region:'A',group:'stationed'}).ok);
 assert(send(r,1,'allianceConfirm').ok);assert(S.acceptGolemResolution(r,1,{g:{allianceResolved:'ogre:1'}}));
 assert(!S.acceptGolemResolution(r,0,{g:{allianceResolved:'ogre:1'}}));
});
test('Ogre roll3 captures Revolts immediately after its ability, before battle ends',t=>{
 t.mock.method(require('crypto'),'randomInt',()=>3);const r=fixture();delete r.legacySnapshot.rule.battle.elfChoice;
 r.legacySnapshot.g.revolts=R.create();R.activate(r.legacySnapshot.g.revolts,1,8);
 assert(send(r,0,'ogreRoll').ok);assert.equal(r.legacySnapshot.g.noblesseRevolts[0].value,3);
 assert.equal(r.legacySnapshot.g.noblesseRevolts[0].target,1);assert.equal(r.legacySnapshot.rule.battle.ogrePower.roll,3);
});
