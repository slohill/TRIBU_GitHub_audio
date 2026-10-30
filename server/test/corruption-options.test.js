const {test}=require('node:test'),assert=require('node:assert/strict');
const {roomOptions,version,seats}=require('../corruption-options');
test('base options unchanged for supported modes, old games default to base',()=>{
 assert.equal(version(undefined),'base');assert.equal(seats(undefined),5);
 assert.deepEqual(roomOptions({maxHumans:2,bots:3}),{gameVersion:'base',maxHumans:2,bots:3});
 assert.deepEqual(roomOptions({maxHumans:3,bots:2}),{gameVersion:'base',maxHumans:3,bots:2});
 assert.throws(()=>roomOptions({mode:'6h',maxHumans:6}));
});
test('Corruption preview requires opt in and caps total capacity at six',()=>{
 assert.throws(()=>roomOptions({gameVersion:'corruption',maxHumans:6}));
 assert.deepEqual(roomOptions({gameVersion:'corruption',maxHumans:6,bots:4},true),{gameVersion:'corruption',maxHumans:6,bots:0});
 assert.throws(()=>roomOptions({gameVersion:'unknown'},true));
});
