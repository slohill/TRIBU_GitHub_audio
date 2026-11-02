const {test}=require('node:test'),assert=require('node:assert/strict');
const A=require('../../assets/corruption-alliances');
function fixture(){return {game:{gameVersion:'corruption',players:[{inPlay:[0]},{inPlay:[]}],b:{A:{owner:0,units:3,npcTribe:'dwarves'},B:{owner:null,units:0,npcTribe:'dwarves',hostile:true,building:{type:'Forteresse'}},C:{owner:1,units:2,npcTribe:'dwarves'}}},cards:[{allianceTribe:'dwarves'}],battles:[{attacker:0,target:'B',attackOrigins:[{region:'A',moves:[1,1,1,1]}]},{attacker:0,target:'D',attackOrigins:[{region:'A',moves:[0,0]}]}]}}
test('peaceful allied NPC conquest includes buildings, excludes opponent and base game',()=>{
 const {game,cards}=fixture();assert(A.peaceful(game,0,'B',cards));assert.equal(A.peaceful(game,0,'C',cards),false);
 game.gameVersion='base';assert.equal(A.peaceful(game,0,'B',cards),false);
});
test('one stationed + four committed losses come from same source, never mutate before confirmation',()=>{
 const {game,battles}=fixture(),before=JSON.stringify({game,battles}),plan=A.createLossPlan(game,0,'dwarves',battles);
 assert(A.choose(plan,'A','stationed'));for(let i=0;i<4;i++)assert(A.choose(plan,'A','battle:0:0'));
 assert(A.ready(plan));assert(A.validate(plan,game,battles));assert.equal(A.choose(plan,'A','stationed'),false);
 const commands=A.commands(plan);assert.equal(commands.length,2);assert.deepEqual(commands.map(c=>c.loss),[1,4]);
 assert.equal(JSON.stringify({game,battles}),before);
});
test('two simultaneous battle groups selectable, restart clears all chosen losses',()=>{
 const {game,battles}=fixture(),plan=A.createLossPlan(game,0,'dwarves',battles);
 assert(A.choose(plan,'A','battle:1:0'));assert(A.choose(plan,'A','battle:0:0'));assert.equal(A.ready(plan),false);
 assert(A.reset(plan,'A'));assert.deepEqual(plan.regions[0].chosen,{});
});
test('five or fewer auto-selected; source with only committed units still included',()=>{
 const {game,battles}=fixture();game.b.A.owner=null;game.b.A.units=0;battles.pop();
 const plan=A.createLossPlan(game,0,'dwarves',battles);assert.equal(plan.regions.length,1);assert.equal(plan.regions[0].required,4);assert(A.ready(plan));
 assert.equal(A.commands(plan)[0].loss,4);
});
test('each allied region independently owes five, opponent region excluded',()=>{
 const {game,battles}=fixture();game.b.E={owner:0,units:7,npcTribe:'dwarves'};
 const plan=A.createLossPlan(game,0,'dwarves',battles);assert.deepEqual(plan.regions.map(r=>[r.region,r.required]),[['A',5],['E',5]]);
 assert.equal(A.choose(plan,'C','stationed'),false);assert.equal(A.commands(plan),null);
});
test('reject stale plan after troops change; bonuses immediately disappear without alliance',()=>{
 const {game,battles,cards}=fixture(),plan=A.createLossPlan(game,0,'dwarves',battles);
 for(let i=0;i<3;i++)A.choose(plan,'A','stationed');for(let i=0;i<2;i++)A.choose(plan,'A','battle:0:0');
 battles[0].attackOrigins[0].moves.pop();assert.equal(A.validate(plan,game,battles),false);
 assert.equal(A.bonus(game,0,cards,'dwarves',5),5);game.players[0].inPlay=[];assert.equal(A.bonus(game,0,cards,'dwarves',5),0);
});

test('forged choices cannot remove more units than a group contains or use unknown group',()=>{
 const {game,battles}=fixture(),plan=A.createLossPlan(game,0,'dwarves',battles);
 plan.regions[0].chosen={stationed:5};assert.equal(A.ready(plan),false);
 plan.regions[0].chosen={unknown:5};assert.equal(A.validate(plan,game,battles),false);
 plan.regions[0].chosen={stationed:-1,'battle:0:0':6};assert.equal(A.ready(plan),false);
});
