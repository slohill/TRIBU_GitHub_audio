const fs=require('fs'),vm=require('vm'),assert=require('assert'),{test}=require('node:test');
const src=fs.readFileSync(require('path').join(__dirname,'../../index.html'),'utf8');
const normal=src.slice(src.indexOf('function onlineLegacyMaybePush(){'),src.indexOf('function onlineLegacyViewerNeedsMap('));
const immediate=src.slice(src.indexOf('function onlineLegacyPushNow(){'),src.indexOf('function onlineLegacyPushPriorityCardNow('));
const sleep=ms=>new Promise(r=>setTimeout(r,ms));
for(const phase of ['recruit','play'])test('ordered rapid '+phase+' snapshots under delayed acknowledgement',async()=>{
 let remoteValue=0,revision=0,inFlight=0,maxFlight=0,requests=0;const accepted=[],errors=[];
 const ctx={setTimeout,clearTimeout,onlineLegacyPendingPush:null,onlineLegacyPushTimer:null,onlineLegacyLastDigest:'',onlineLegacyRevision:0,onlineLegacyApplying:false,onlineSocket:{},G:{value:1,phase,players:[{bot:false}],online:{legacySync:true,myPlayerIndex:0,revision:0}},onlineLegacyCanPublish:()=>true,onlineError:e=>errors.push(e)};
 ctx.onlineLegacyDigest=()=>String(ctx.G.value);ctx.onlineLegacySnapshot=()=>({g:{phase:ctx.G.phase,value:ctx.G.value}});ctx.onlineLegacyApply=p=>{ctx.G.value=p.snapshot.g.value};
 ctx.onlineAck=(_,p)=>new Promise((resolve,reject)=>{const request=++requests;maxFlight=Math.max(maxFlight,++inFlight);setTimeout(()=>{inFlight--;if(p.baseRevision!==revision)return reject({current:{revision,snapshot:{g:{value:remoteValue}}}});remoteValue=p.snapshot.g.value;accepted.push(remoteValue);resolve({revision:++revision})},request===1?350:30)});
 vm.createContext(ctx);vm.runInContext(normal+'\n'+immediate,ctx);ctx.onlineLegacyMaybePush();await sleep(130);ctx.G.value=2;ctx.onlineLegacyMaybePush();await sleep(110);ctx.G.value=3;ctx.onlineLegacyMaybePush();await sleep(600);
 assert.equal(remoteValue,3);assert.equal(ctx.G.value,3);assert.equal(maxFlight,1);assert.deepEqual(accepted,[1,3]);assert.deepEqual(errors,[]);
 // End-of-phase/priority flush while an ordinary snapshot is still in flight.
 ctx.G.value=4;ctx.onlineLegacyMaybePush();await sleep(100);ctx.G.value=5;ctx.G.phase='oracleRoll';await ctx.onlineLegacyPushNow();await sleep(180);assert.equal(remoteValue,5);assert.equal(maxFlight,1);assert.equal(ctx.onlineLegacyRevision,revision);clearTimeout(ctx.onlineLegacyPushTimer);
});
