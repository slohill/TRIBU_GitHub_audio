/* Short effects share one gesture-unlocked context; music and the gold clock stay on their existing players. */
(function(root){
 'use strict';
 function create({sources,names,onError=()=>{},onReady=()=>{},environment=root}){
  const Context=environment.AudioContext||environment.webkitAudioContext;
  const buffers=new Map(),voices=new Set();let context=null,generation=0,preloaded=false;
  const report=(stage,name,error)=>onError({stage,name,error:error?.name||'AudioError',message:String(error?.message||error||'').slice(0,180)});
  function buffer(name){
   if(!buffers.has(name)){
    const task=environment.fetch(sources[name]).then(response=>{if(!response.ok)throw Error('Audio HTTP '+response.status);return response.arrayBuffer()}).then(data=>new Promise((resolve,reject)=>context.decodeAudioData(data,resolve,reject)));
    buffers.set(name,task);task.catch(()=>{if(buffers.get(name)===task)buffers.delete(name)});
   }
   return buffers.get(name);
  }
  function unlock(){
   if(!Context)return false;
   try{
    if(!context||context.state==='closed'){context=new Context();buffers.clear();preloaded=false}
    // Call resume in the gesture itself, never after a fetch or metadata callback.
    if(context.state!=='running'){
     Promise.resolve(context.resume()).catch(error=>report('unlock','',error));
     const silent=context.createBufferSource(),gain=context.createGain();gain.gain.value=0;silent.buffer=context.createBuffer(1,1,context.sampleRate);silent.connect(gain);gain.connect(context.destination);silent.onended=()=>{silent.disconnect();gain.disconnect()};silent.start(0);
    }
    if(!preloaded){preloaded=true;for(const name of names)buffer(name).catch(error=>report('load',name,error))}
   }catch(error){report('unlock','',error)}
   return true;
  }
  function play(name,volume){
   if(!Context)return false;
   if(!context||context.state!=='running'){report('play',name,{name:'NotAllowedError',message:'Toucher Sons pour activer les effets audio.'});return true}
   const ticket=generation,requestedAt=Date.now();
   buffer(name).then(decoded=>{
    // Never replay old effects after muting, leaving a game, or a slow download.
    if(ticket!==generation||Date.now()-requestedAt>3000)return;
    if(context.state!=='running'){report('play',name,{name:'NotAllowedError',message:'Le lecteur audio est suspendu.'});return}
    const source=context.createBufferSource(),gain=context.createGain();source.buffer=decoded;gain.gain.value=Math.max(0,Math.min(1,Number.isFinite(Number(volume))?Number(volume):.8));source.connect(gain);gain.connect(context.destination);
    const voice={source,gain};voices.add(voice);source.onended=()=>{voices.delete(voice);source.disconnect();gain.disconnect()};source.start(0);onReady();
   }).catch(error=>report('play',name,error));
   return true;
  }
  function stopAll(){generation++;for(const {source,gain} of voices){try{source.stop()}catch(_){}source.disconnect();gain.disconnect()}voices.clear()}
  return {unlock,play,stopAll,get state(){return context?.state||'locked'}};
 }
 if(typeof module==='object'&&module.exports)module.exports={create};else root.TribuEffects={create};
})(typeof window!=='undefined'?window:globalThis);
