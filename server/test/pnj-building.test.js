const test=require('node:test'),assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path'),os=require('node:os'),net=require('node:net');
const {spawn}=require('node:child_process');const {io}=require('socket.io-client');
const ack=(socket,event,payload={})=>new Promise((resolve,reject)=>socket.timeout(4000).emit(event,payload,(err,res)=>err?reject(err):resolve(res)));
const connect=url=>new Promise((resolve,reject)=>{const socket=io(url,{transports:['websocket'],forceNew:true,reconnection:false});socket.once('connect',()=>resolve(socket));socket.once('connect_error',reject)});
async function freePort(){const s=net.createServer();await new Promise(r=>s.listen(0,'127.0.0.1',r));const p=s.address().port;await new Promise(r=>s.close(r));return p}
async function start(file){const port=await freePort(),child=spawn(process.execPath,[path.join(__dirname,'../server.js')],{env:{...process.env,PORT:String(port),TRIBU_HISTORY_FILE:file},stdio:['ignore','pipe','pipe']});await new Promise((resolve,reject)=>{const timer=setTimeout(()=>reject(Error('Server start timeout')),5000);child.stdout.on('data',b=>{if(String(b).includes('listening')){clearTimeout(timer);resolve()}});child.once('exit',code=>{clearTimeout(timer);reject(Error('Server exit '+code))});child.stderr.on('data',b=>process.stderr.write(b));});return {child,url:'http://127.0.0.1:'+port}}
const stop=child=>new Promise(resolve=>{child.once('exit',resolve);child.kill()});

test('online Oracle sacrifice restores NPC under surviving defensive building',{timeout:20000},async()=>{const dir=fs.mkdtempSync(path.join(os.tmpdir(),'pnj-oracle-')),file=path.join(dir,'history.json');const server=await start(file),sockets=[];try{ const p1=await connect(server.url),p2=await connect(server.url),spec=await connect(server.url);sockets.push(p1,p2,spec);
 assert((await ack(p1,'createRoom',{code:'OPTIONS',maxHumans:2,bots:0,mode:'2v3',battleReactionSeconds:30,pseudo:'Alice'})).ok);await ack(p2,'joinRoom',{code:'OPTIONS',pseudo:'Bob'});await ack(p1,'setReady',true);await ack(p2,'setReady',true);await ack(p1,'launchGame');
 const v1=(await ack(p1,'requestGameState')).game;assert.equal(v1.battleReactionSeconds,30);
 for(let i=0;i<2;i++){const sock=v1.youIndex===i?p1:p2,g=(await ack(sock,'requestGameState')).game;assert((await ack(sock,'setupComplete',{color:i?'#ffd92f':'#ff4fc3',portrait:i?'R_A':'GB_A',regions:Object.keys(g.board).filter(k=>k[0]===g.players[i].province&&!g.board[k].hostile).slice(0,2)})).ok)}
 const bootstrap=(await ack(p1,'requestLegacyState')).bootstrap;assert.equal(bootstrap.battleReactionSeconds,30);

 const actor=v1.youIndex,types=['Forteresse','Icenia, la cité blanche','Sundo, cité du soleil'];
 const snapshot={g:{...bootstrap,b:bootstrap.board,players:bootstrap.players.map(p=>({...p,hand:[],inPlay:[]}))},rule:{oracleState:{kind:'sacrifice',queues:[{player:actor,need:4,eligible:['A5','B3','C3','A2'],done:false}]}}};
 for(const [i,r] of ['A5','B3','C3','A2'].entries()){Object.assign(snapshot.g.b[r],{owner:actor,units:3,hostile:false,building:{type:types[i%3],owner:actor,cardId:90+i}});snapshot.g.players[actor].inPlay.push(90+i)}
 assert((await ack(p1,'legacyCommit',{actorIndex:actor,baseRevision:0,snapshot})).ok);
 const sacrifice=await ack(p1,'legacyOracleSacrifice',{regions:['A5','B3','C3','A2']});assert(sacrifice.ok,JSON.stringify(sacrifice));
 const state=(await ack(p1,'requestLegacyState')).snapshot;
 for(const r of ['A5','B3','C3']){assert.equal(state.g.b[r].hostile,true);assert.equal(state.g.b[r].building.owner,null);assert.equal(state.g.b[r].units,0)}
 assert.equal(state.g.b.A2.hostile,false);assert.deepEqual(state.g.players[actor].inPlay,[]);
 }finally{for(const s of sockets)s.disconnect();await stop(server.child)}});