const test=require('node:test'),assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path'),os=require('node:os'),net=require('node:net');
const {spawn}=require('node:child_process');const {io}=require('socket.io-client');
const ack=(socket,event,payload={})=>new Promise((resolve,reject)=>socket.timeout(4000).emit(event,payload,(err,res)=>err?reject(err):resolve(res)));
const connect=url=>new Promise((resolve,reject)=>{const socket=io(url,{transports:['websocket'],forceNew:true,reconnection:false});socket.once('connect',()=>resolve(socket));socket.once('connect_error',reject)});
async function freePort(){const s=net.createServer();await new Promise(r=>s.listen(0,'127.0.0.1',r));const p=s.address().port;await new Promise(r=>s.close(r));return p}
async function start(file){const port=await freePort(),child=spawn(process.execPath,[path.join(__dirname,'../server.js')],{env:{...process.env,PORT:String(port),TRIBU_HISTORY_FILE:file},stdio:['ignore','pipe','pipe']});await new Promise((resolve,reject)=>{const timer=setTimeout(()=>reject(Error('Server start timeout')),5000);child.stdout.on('data',b=>{if(String(b).includes('listening')){clearTimeout(timer);resolve()}});child.once('exit',code=>{clearTimeout(timer);reject(Error('Server exit '+code))});child.stderr.on('data',b=>process.stderr.write(b));});return {child,url:'http://127.0.0.1:'+port}}
const stop=child=>new Promise(resolve=>{child.once('exit',resolve);child.kill()});
test('spectators get live public state, cannot act, take no seat, and history survives restart',{timeout:25000},async()=>{
 const dir=fs.mkdtempSync(path.join(os.tmpdir(),'tribu-sockets-test-')),file=path.join(dir,'history.json');let server=await start(file),sockets=[];
 try{const p1=await connect(server.url),p2=await connect(server.url),spec=await connect(server.url);sockets.push(p1,p2,spec);
   const received=[];spec.onAny((event,data)=>received.push({event,data}));
   assert((await ack(p1,'createRoom',{code:'SPEC-TEST',name:'Test public',maxHumans:2,bots:0,mode:'2v3',pseudo:'Alice'})).ok);
   assert((await ack(p2,'joinRoom',{code:'SPEC-TEST',pseudo:'Bob'})).ok);await ack(p1,'setReady',true);await ack(p2,'setReady',true);assert((await ack(p1,'launchGame')).ok);
   let activity=(await ack(spec,'subscribeActivity')).activity;assert.equal(activity.games.length,1);const id=activity.games[0].id;const joined=await ack(spec,'spectateGame',{id});assert(joined.ok);assert.equal(joined.state.players.length,2);
   const view1=(await ack(p1,'requestGameState')).game,view2=(await ack(p2,'requestGameState')).game;
   for(let i=0;i<2;i++){const socket=view1.youIndex===i?p1:p2,state=(await ack(socket,'requestGameState')).game,province=state.players[i].province;const regions=Object.keys(state.board).filter(k=>k[0]===province&&!state.board[k].hostile).slice(0,2);assert((await ack(socket,'setupComplete',{color:i===0?'#ff4fc3':'#ffd92f',portrait:i===0?'GB_A':'R_A',regions})).ok)}
   const bootstrap=(await ack(p1,'requestLegacyState')).bootstrap;
   const snapshot={g:{...bootstrap,b:bootstrap.board,players:bootstrap.players.map(p=>({...p,name:p.pseudo,hand:[0,1,'SECRET_HAND'],seenCards:['SECRET_SPY']})),seed:'SECRET_SEED',log:['SECRET_LOG'],deck:['SECRET_DECK']},rule:{gameOverState:null,divinationState:{secret:'SECRET_DIVINATION'},commerceDeals:['SECRET_TRADE']},public:{scores:[1,0]}};
   const nextState=new Promise((resolve,reject)=>{const timer=setTimeout(()=>reject(Error('No live state')),4000);spec.on('spectatorState',state=>{if(state.players[0]?.handCount===3){clearTimeout(timer);resolve(state)}})});
   assert((await ack(p1,'legacyCommit',{actorIndex:view1.youIndex,baseRevision:0,snapshot})).ok);
   const publicState=await nextState;assert.equal(publicState.players[0].score,1);assert(!JSON.stringify(publicState).includes('SECRET'));assert.equal(publicState.oracleNext,null);
   for(const event of ['createRoom','joinRoom','resumeRoom','setReady','launchGame','requestGameState','requestLegacyState','setupComplete','setupIdentity','setupRegions','legacyCommit','legacyOracleSacrifice','gameAction','legacySfx','leaveRoom']){const result=await ack(spec,event,{code:'SPEC-TEST',type:'DRAW_START',actorIndex:view1.youIndex,snapshot});assert.equal(result.ok,false,event+' allowed');assert.match(result.error,/lecture seule/)}
   const after=(await ack(p1,'requestLegacyState'));assert.equal(after.revision,1);assert.equal(after.snapshot.g.players.length,2);
   assert.equal((await ack(p1,'subscribeActivity')).ok,false,'player socket became spectator');
   await ack(spec,'leaveSpectator');assert.equal((await ack(spec,'spectateGame',{id})).ok,true);
   snapshot.rule.gameOverState={winner:0,points:3};snapshot.public.scores=[3,0];assert((await ack(p1,'legacyCommit',{actorIndex:view1.youIndex,baseRevision:1,snapshot})).ok);
   activity=(await ack(spec,'subscribeActivity')).activity;assert.equal(activity.games.length,0);assert.equal(activity.recent.length,1);assert.equal(activity.recent[0].winner,0);
   assert(!JSON.stringify(received).includes('SECRET'));assert(!received.some(x=>['legacyState','gameState','roomState','legacySfx','gameLaunched'].includes(x.event)));
   for(const socket of sockets)socket.disconnect();sockets=[];await stop(server.child);server=await start(file);
   const fresh=await connect(server.url);sockets.push(fresh);const restored=(await ack(fresh,'subscribeActivity')).activity;assert.equal(restored.games.length,0);assert.equal(restored.recent.length,1);assert.equal(restored.recent[0].id,id);
 }finally{for(const socket of sockets)socket.disconnect();await stop(server.child)}
});
