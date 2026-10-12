const test=require('node:test'),assert=require('node:assert/strict');
const {create}=require('../../assets/audio-effects');
const tick=()=>new Promise(r=>setImmediate(r));
function harness(){
 const errors=[],starts=[],gains=[];let ctx,gesture=false,fetches=0,failFetch=false,release=null;
 class Context{
  constructor(){ctx=this;this.state='suspended';this.destination={};this.sampleRate=48000;this.calls=0}
  resume(){this.calls++;if(!gesture)return new Promise(()=>{});this.state='running';return Promise.resolve()}
  createBuffer(){return {silent:true}}
  createBufferSource(){return {connect(){},disconnect(){},start(){starts.push(this)},stop(){this.stopped=true}}}
  createGain(){const gain={gain:{value:1},connect(){},disconnect(){}};gains.push(gain);return gain}
  decodeAudioData(data,resolve){resolve({duration:1})}
 }
 const environment={AudioContext:Context,fetch:async()=>{fetches++;if(failFetch)throw Error('offline');if(release!==null)await new Promise(r=>{release=r});return {ok:true,arrayBuffer:async()=>new ArrayBuffer(1)}}};
 const effects=create({sources:{horn:'horn.mp3',drums:'drums.mp3'},names:['horn','drums'],onError:e=>errors.push(e),environment});
 return {effects,errors,starts,gains,get ctx(){return ctx},get fetches(){return fetches},gesture:()=>gesture=true,fail:v=>failFetch=v,delay:()=>release=()=>{},release:()=>release()};
}
test('a rejected first gesture does not prevent a later touch from unlocking all effects',async()=>{
 const h=harness();h.effects.unlock();assert.equal(h.effects.state,'suspended');h.effects.play('horn',.9);assert.equal(h.errors.at(-1).error,'NotAllowedError');
 h.gesture();h.effects.unlock();await tick();assert.equal(h.ctx.calls,2);assert.equal(h.effects.state,'running');h.effects.play('horn',.9);h.effects.play('drums',.7);await tick();assert.equal(h.starts.filter(s=>!s.buffer.silent).length,2);assert.equal(h.fetches,2);
});
test('muting stops running voices and invalidates asynchronous pending sounds',async()=>{
 const h=harness();h.gesture();h.effects.unlock();await tick();h.effects.play('horn',0);await tick();assert.equal(h.gains.at(-1).gain.value,0);h.effects.stopAll();assert(h.starts.at(-1).stopped);
 const delayed=harness();delayed.gesture();delayed.delay();delayed.effects.unlock();delayed.effects.play('drums',.8);delayed.effects.stopAll();delayed.release();await tick();assert.equal(delayed.starts.filter(s=>!s.buffer.silent).length,0);
});
test('load errors are reported and a later effect retries, suspended contexts resume on another gesture',async()=>{
 const h=harness();h.fail(true);h.gesture();h.effects.unlock();await tick();assert(h.errors.some(e=>e.stage==='load'));h.fail(false);h.effects.play('horn',.8);await tick();assert.equal(h.starts.filter(s=>!s.buffer.silent).length,1);
 h.ctx.state='suspended';h.effects.play('drums',.8);assert.equal(h.errors.at(-1).error,'NotAllowedError');h.effects.unlock();h.effects.play('drums',.8);await tick();assert.equal(h.starts.filter(s=>!s.buffer.silent).length,2);
});
test('legacy fallback remains available without AudioContext',()=>{const effects=create({sources:{},names:[],environment:{}});assert.equal(effects.unlock(),false);assert.equal(effects.play('horn',1),false)});
