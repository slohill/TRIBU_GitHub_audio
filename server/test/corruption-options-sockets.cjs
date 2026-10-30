const assert=require('assert/strict'),path=require('path'),{spawn}=require('child_process');
const {io}=require('socket.io-client');
const ack=(s,e,p={})=>new Promise((r,j)=>s.timeout(4000).emit(e,p,(err,v)=>err?j(err):r(v)));
const sockets=[];
const connect=()=>new Promise((r,j)=>{const s=io('http://127.0.0.1:8791',{transports:['websocket']});sockets.push(s);s.once('connect',()=>r(s));s.once('connect_error',j)});
(async()=>{
 const child=spawn(process.execPath,[path.join(__dirname,'../server.js')],{env:{...process.env,PORT:'8791',TRIBU_CORRUPTION_PREVIEW:'1',TRIBU_HISTORY_FILE:path.join(require('os').tmpdir(),'tribu-corruption-options-'+process.pid+'.json')},stdio:['ignore','pipe','pipe']});
 try{
 await new Promise((r,j)=>{const timer=setTimeout(()=>j(Error('server start timeout')),6000);child.stdout.on('data',b=>{if(String(b).includes('listening')){clearTimeout(timer);r()}});child.stderr.on('data',b=>process.stderr.write(b))});
 const a=await connect(),b=await connect();
 assert.equal((await ack(a,'createRoom',{code:'BAD',mode:'6h',maxHumans:6})).ok,false);
 const base=await ack(a,'createRoom',{code:'BASE',maxHumans:2,bots:0,mode:'3h',pseudo:'A'});
 assert(base.ok);assert.equal(base.room.gameVersion,'base');
 await ack(b,'joinRoom',{code:'BASE',pseudo:'B'});await ack(a,'setReady',true);await ack(b,'setReady',true);
 assert((await ack(a,'launchGame')).ok);
 const state=(await ack(a,'requestGameState')).game;assert.equal(state.gameVersion,'base');assert.equal(state.players.length,2);
 for(let i=0;i<2;i++){
 const sock=state.youIndex===i?a:b,g=(await ack(sock,'requestGameState')).game;
 assert((await ack(sock,'setupComplete',{color:i?'#ffd92f':'#ff4fc3',portrait:i?'R_A':'GB_A',regions:Object.keys(g.board).filter(k=>k[0]===g.players[i].province&&!g.board[k].hostile).slice(0,2)})).ok);
 }
 const legacy=await ack(a,'requestLegacyState');assert.equal(legacy.bootstrap.gameVersion,'base');assert.equal(legacy.recovery.gameVersion,'base');
 const participants=[];for(let i=0;i<7;i++)participants.push(await connect());
 const room=await ack(participants[0],'createRoom',{code:'CORR',gameVersion:'corruption',maxHumans:6,bots:0,mode:'6h',pseudo:'C0'});
 assert(room.ok);assert.equal(room.room.maxHumans,6);assert.equal(room.room.gameVersion,'corruption');
 for(let i=1;i<6;i++)assert((await ack(participants[i],'joinRoom',{code:'CORR',pseudo:'C'+i})).ok);
 assert.equal((await ack(participants[6],'joinRoom',{code:'CORR',pseudo:'overflow'})).ok,false);
 for(let i=0;i<6;i++)await ack(participants[i],'setReady',true);
 const launch=await ack(participants[0],'launchGame');assert.equal(launch.ok,false);assert(launch.error.includes('intégration'));
 console.log('PASS real sockets: base launch/setup/bootstrap/recovery; Corruption six-seat lobby; overflow refusal; unfinished expansion launch locked.');
 }finally{sockets.forEach(s=>s.disconnect());child.kill()}
})().catch(e=>{console.error(e);process.exitCode=1});
