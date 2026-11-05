const {test}=require('node:test'),assert=require('node:assert/strict'),H=require('../../assets/corruption-heroes');
const cards=[{heroKey:'golem',activeAbilities:['violence']},{heroKey:'guide',activeAbilities:['divination'],activePhase:'start'},{type:'Agent'}];
function fixture(){return {gameVersion:'corruption',active:0,phase:'play',players:[{hand:[0,1],inPlay:[2],inPlayUID:['agent:1'],bot:false},{hand:[],inPlay:[],inPlayUID:[],bot:false}]}}
function place(g,id=0,epoch=1){const intent=H.preparePlacement(g,0,g.players[0].hand.indexOf(id),cards);assert(H.place(g,intent,cards,epoch));}
test('own play phase only; base and invalid hands excluded without mutation',()=>{
 for(const change of [{phase:'start'},{active:1},{gameVersion:'base'}]){const g=Object.assign(fixture(),change),before=JSON.stringify(g);assert.equal(H.preparePlacement(g,0,0,cards),null);assert.equal(JSON.stringify(g),before)}
});
test('next owner turn unlocks passive; active waits for own play and only once',()=>{
 const g=fixture();place(g);assert(!H.passiveReady(g,0,cards));g.active=1;assert(!H.beginOwnerTurn(g,0,cards,2));
 g.active=0;g.phase='start';assert(!H.beginOwnerTurn(g,0,cards,1));assert(H.beginOwnerTurn(g,0,cards,3));assert(H.passiveReady(g,0,cards));assert(!H.activeReady(g,0,cards,3,'violence'));
 g.phase='play';assert(H.consumeActive(g,0,cards,3,'violence'));assert(!H.consumeActive(g,0,cards,3,'violence'));assert(!H.consumeActive(g,0,cards,3,'invented'));assert(H.activeReady(g,0,cards,5,'violence'));
});
test('replacement must be confirmed; old hero returns to hand and new one waits',()=>{
 const g=fixture();place(g);H.beginOwnerTurn(g,0,cards,3);const intent=H.preparePlacement(g,0,0,cards),before=JSON.stringify(g);
 assert(intent.requiresConfirmation);assert(!H.place(g,intent,cards,3));assert.equal(JSON.stringify(g),before);assert(H.place(g,intent,cards,3,true));
 assert.deepEqual(g.players[0].hand,[0]);assert.deepEqual(g.players[0].inPlay,[2,1]);assert(!H.passiveReady(g,0,cards));assert(!H.place(g,intent,cards,3,true));
});
test('use then return allowed; replay resets delay and stale deployment never activates',()=>{
 const g=fixture();place(g);H.beginOwnerTurn(g,0,cards,3);assert(H.consumeActive(g,0,cards,3,'violence'));assert(H.returnToHand(g,0,cards));place(g,0,3);assert(!H.passiveReady(g,0,cards));
 H.beginOwnerTurn(g,0,cards,5);g.players[0].inPlay.pop();g.players[0].inPlayUID.pop();assert(!H.passiveReady(g,0,cards));assert(!H.consumeActive(g,0,cards,5,'violence'));
});
test('bots place heroes and use passives, never activate or return; JSON restore preserves use',()=>{
 let g=fixture();g.players[0].bot=true;place(g);H.beginOwnerTurn(g,0,cards,3);assert(H.passiveReady(g,0,cards));assert(!H.consumeActive(g,0,cards,3,'violence'));assert(!H.returnToHand(g,0,cards));
 g.players[0].bot=false;assert(H.consumeActive(g,0,cards,3,'violence'));g=JSON.parse(JSON.stringify(g));assert(H.passiveReady(g,0,cards));assert(!H.consumeActive(g,0,cards,3,'violence'));
});
test('replacement rejects changed instance even when the same card reappears',()=>{
 const g=fixture();place(g);const intent=H.preparePlacement(g,0,0,cards);g.players[0].inPlayUID[1]='another-instance';const before=JSON.stringify(g);assert(!H.place(g,intent,cards,3,true));assert.equal(JSON.stringify(g),before);
});

test('Guide Divination is available at start only after next owner turn',()=>{
 const g=fixture();place(g,1);assert(!H.activeReady(g,0,cards,1,'divination'));
 g.phase='start';H.beginOwnerTurn(g,0,cards,3);assert(H.consumeActive(g,0,cards,3,'divination'));assert(!H.consumeActive(g,0,cards,3,'divination'));
 g.phase='play';assert(!H.activeReady(g,0,cards,5,'divination'));
});
