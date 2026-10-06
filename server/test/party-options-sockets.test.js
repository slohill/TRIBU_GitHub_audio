const test=require('node:test'),assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path'),os=require('node:os'),net=require('node:net');
const {spawn}=require('node:child_process');const {io}=require('socket.io-client');
const ack=(socket,event,payload={})=>new Promise((resolve,reject)=>socket.timeout(4000).emit(event,payload,(err,res)=>err?reject(err):resolve(res)));
const connect=url=>new Promise((resolve,reject)=>{const socket=io(url,{transports:['websocket'],forceNew:true,reconnection:false});socket.once('connect',()=>resolve(socket));socket.once('connect_error',reject)});
async function freePort(){const s=net.createServer();await new Promise(r=>s.listen(0,'127.0.0.1',r));const p=s.address().port;await new Promise(r=>s.close(r));return p}
async function start(file){const port=await freePort(),child=spawn(process.execPath,[path.join(__dirname,'../server.js')],{env:{...process.env,PORT:String(port),TRIBU_HISTORY_FILE:file},stdio:['ignore','pipe','pipe']});await new Promise((resolve,reject)=>{const timer=setTimeout(()=>reject(Error('Server start timeout')),5000);child.stdout.on('data',b=>{if(String(b).includes('listening')){clearTimeout(timer);resolve()}});child.once('exit',code=>{clearTimeout(timer);reject(Error('Server exit '+code))});child.stderr.on('data',b=>process.stderr.write(b));});return {child,url:'http://127.0.0.1:'+port}}
const stop=child=>new Promise(resolve=>{child.once('exit',resolve);child.kill()});

test('reaction settings, multi-player commerce leases, spectators and full history pages',{timeout:25000},async()=>{
 const dir=fs.mkdtempSync(path.join(os.tmpdir(),'tribu-options-')),file=path.join(dir,'history.json');
 const history=Array.from({length:505},(_,i)=>({id:'12345678-1234-1234-1234-'+String(i).padStart(12,'0'),finishedAt:i,players:[{name:'Test'}],winner:0,journal:Array.from({length:245},(_,j)=>'Événement '+j)}));fs.writeFileSync(file,JSON.stringify(history));
 const server=await start(file),sockets=[];try{
 const p1=await connect(server.url),p2=await connect(server.url),spec=await connect(server.url);sockets.push(p1,p2,spec);
 const all=[];let before=null;do{const res=await ack(spec,'publicHistory',{before});assert(res.ok);all.push(...res.rows);before=res.next}while(before);assert.equal(all.length,505);assert.equal(new Set(all.map(r=>r.id)).size,505);assert(!('journal' in all[0]));let offset=0,lines=[];do{const page=await ack(spec,'publicJournal',{id:all[0].id,offset});assert(page.ok);lines.push(...page.rows);offset=page.next}while(offset!==null);assert.equal(lines.length,245);assert.equal(lines[244],'Événement 244');
 assert((await ack(p1,'createRoom',{code:'OPTIONS',maxHumans:2,bots:0,mode:'2v3',battleReactionSeconds:30,pseudo:'Alice'})).ok);await ack(p2,'joinRoom',{code:'OPTIONS',pseudo:'Bob'});await ack(p1,'setReady',true);await ack(p2,'setReady',true);await ack(p1,'launchGame');
 const v1=(await ack(p1,'requestGameState')).game;assert.equal(v1.battleReactionSeconds,30);
 for(let i=0;i<2;i++){const sock=v1.youIndex===i?p1:p2,g=(await ack(sock,'requestGameState')).game;assert((await ack(sock,'setupComplete',{color:i?'#ffd92f':'#ff4fc3',portrait:i?'R_A':'GB_A',regions:Object.keys(g.board).filter(k=>k[0]===g.players[i].province&&!g.board[k].hostile).slice(0,2)})).ok)}
 const bootstrap=(await ack(p1,'requestLegacyState')).bootstrap;assert.equal(bootstrap.battleReactionSeconds,30);
 const snapshot={g:{...bootstrap,b:bootstrap.board,players:bootstrap.players.map(p=>({...p,hand:[1],inPlay:[]}))},rule:{battle:{seconds:30,attacker:0,defender:1,priorityIndex:0,stack:[]},commerceDeals:[]},public:{scores:[1,0]}};
 assert((await ack(p1,'legacyCommit',{actorIndex:v1.youIndex,baseRevision:0,snapshot})).ok);
 await ack(p1,'commerceEditing',{open:true});await ack(p2,'commerceEditing',{open:true});let state=await ack(p1,'requestLegacyState');assert.equal(state.snapshot.rule.commercePaused,true);const seconds=state.snapshot.rule.battle.seconds;
 const forged=structuredClone(state.snapshot);forged.rule.battle.stack.push({cardId:1});forged.g.players[0].hand=[];assert.equal((await ack(p1,'legacyCommit',{actorIndex:v1.youIndex,baseRevision:state.revision,snapshot:forged})).ok,false);
 assert.equal((await ack(spec,'commerceEditing',{open:false})).ok,false);
 await ack(p1,'commerceEditing',{open:false});state=await ack(p1,'requestLegacyState');assert.equal(state.snapshot.rule.commercePaused,true);
 const pauseEnded=new Promise(resolve=>p1.on('commercePause',s=>{if(!s.paused)resolve(s)}));p2.disconnect();assert.equal((await pauseEnded).seconds,seconds);state=await ack(p1,'requestLegacyState');assert.equal(state.snapshot.rule.commercePaused,false);assert.equal(state.recovery.battleReactionSeconds,30);
 }finally{for(const s of sockets)s.disconnect();await stop(server.child)}
});
