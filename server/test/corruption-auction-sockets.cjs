const fs=require('fs'),path=require('path'),assert=require('assert/strict'),{spawn}=require('child_process');
const {io}=require('socket.io-client');
const root=path.resolve(__dirname,'..'),fixture=path.join(root,'.auction-fixture-'+process.pid+'.js');
const sockets=[];const ack=(s,e,p={})=>new Promise((r,j)=>s.timeout(4000).emit(e,p,(err,v)=>err?j(err):r(v)));
const connect=()=>new Promise((r,j)=>{const s=io('http://127.0.0.1:8791',{transports:['websocket']});sockets.push(s);s.once('connect',()=>r(s));s.once('connect_error',j)});
const hook=[
"io.on('connection',socket=>socket.on('testAuctionFixture',(_,ack)=>{",
" const room=roomForSocket(socket);room.gameVersion='corruption';room.legacyMode=true;room.legacyRevision=0;",
" room.game={status:'playing',players:room.players.map(p=>({socketId:p.id})),phase:'start'};",
" room.legacySnapshot={g:{gameVersion:'corruption',active:0,phase:'auction',players:room.players.map((p,i)=>({name:p.pseudo,gold:10,hand:[],faction:i===0?6:0})),discard:[],morcattAuction:require('../assets/corruption-auction').create(0,[0,1],6)},rule:{commerceDeals:[],commerceSeq:1}};",
" ack({ok:true});}));"
].join('\n');
(async()=>{
 fs.writeFileSync(fixture,fs.readFileSync(path.join(root,'server.js'),'utf8')+'\n'+hook);
 const child=spawn(process.execPath,[fixture],{env:{...process.env,PORT:'8791',TRIBU_CORRUPTION_PREVIEW:'1',TRIBU_HISTORY_FILE:path.join(require('os').tmpdir(),'tribu-auction-test-'+process.pid+'.json')},stdio:['ignore','pipe','pipe']});
 try{
 await new Promise((r,j)=>{const timeout=setTimeout(()=>j(Error('server timeout')),6000);child.stdout.on('data',b=>{if(String(b).includes('listening')){clearTimeout(timeout);r()}});child.stderr.on('data',b=>process.stderr.write(b))});
 const a=await connect(),b=await connect(),c=await connect();
 assert((await ack(a,'createRoom',{code:'BIDS',gameVersion:'corruption',maxHumans:3,mode:'3h',pseudo:'Seller'})).ok);
 await ack(b,'joinRoom',{code:'BIDS',pseudo:'Buyer1'});await ack(c,'joinRoom',{code:'BIDS',pseudo:'Buyer2'});
 await ack(a,'testAuctionFixture');
 const start=await ack(a,'morcattAuctionAction',{kind:'start',revision:0});assert(start.ok);
 const rev=start.current.snapshot.g.morcattAuction.revision;
 const [one,two]=await Promise.all([ack(b,'morcattAuctionAction',{kind:'bid',amount:2,revision:rev}),ack(c,'morcattAuctionAction',{kind:'bid',amount:3,revision:rev})]);
 assert.equal([one,two].filter(x=>x.ok).length,1);
 const latest=two.current.snapshot.g.morcattAuction.revision>=one.current.snapshot.g.morcattAuction.revision?two:one;
 const auction=latest.current.snapshot.g.morcattAuction,winner=auction.bids[0].player,amount=auction.bids[0].amount,loser=winner===1?c:b;
 const leading=winner===1?b:c;
 const undone=await ack(leading,'morcattAuctionAction',{kind:'cancel',index:0,revision:auction.revision});assert(undone.ok);
 const snap=undone.current.snapshot;assert.equal(snap.g.morcattAuction.bids[0],null);
 assert.equal(snap.g.players[winner].gold,10);assert.deepEqual(snap.g.players[winner].hand,[]);
 const forged=JSON.parse(JSON.stringify(snap));forged.g.players[winner].gold=999;forged.g.morcattAuction.stage='finished';
 const commit=await ack(a,'legacyCommit',{actorIndex:0,baseRevision:undone.current.revision,snapshot:forged});assert(commit.ok);
 const noAction=await ack(a,'morcattAuctionAction',{kind:'price',revision:-1});
 assert.equal(noAction.current.snapshot.g.players[winner].gold,10);assert.equal(noAction.current.snapshot.g.morcattAuction.stage,'bidding');
 assert.equal((await ack(loser,'morcattAuctionAction',{kind:'extend',revision:auction.revision})).ok,false);
 console.log('PASS real sockets: concurrent bids serialized, undo verified, stale snapshot cannot change balances or finish auction.');
 }finally{sockets.forEach(s=>s.disconnect());child.kill();await new Promise(r=>child.once('exit',r));fs.unlinkSync(fixture)}
})().catch(e=>{console.error(e);process.exitCode=1});
