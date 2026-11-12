const fs=require('fs'),path=require('path'),http=require('http'),assert=require('assert'),{spawn}=require('child_process');
const {chromium}=require(process.env.TRIBU_PLAYWRIGHT_MODULE||'playwright');
const {io}=require(process.env.TRIBU_SOCKET_CLIENT_MODULE||'socket.io-client');
const ROOT=path.resolve(__dirname,'../..'),ASSETS=process.env.TRIBU_TEST_ASSET_ROOT;
const ack=(s,e,p={})=>new Promise((r,j)=>s.timeout(4000).emit(e,p,(err,v)=>err?j(err):r(v)));
const connect=()=>new Promise((r,j)=>{const s=io('http://127.0.0.1:8791',{transports:['websocket']});s.once('connect',()=>r(s));s.once('connect_error',j)});
const server=http.createServer((req,res)=>{
 let rel=req.url.split('?')[0];if(rel==='/')rel='/index.html';
 const candidates=[path.join(ROOT,rel)];
 if(ASSETS){for(const dir of ['work/card-access-audit','work/tutorial-scroll-build','work/sacrifice-links-build','work/oct10-build','work/audio-repair','work/october-build','work/webp-build'])candidates.push(path.join(ASSETS,dir,rel));if(rel.startsWith('/assets/images/maps/'))candidates.push(path.join(ASSETS,'outputs/audit-maps-audio/maps',path.basename(rel,'.webp'),'q90.webp'))}
 const file=candidates.find(f=>fs.existsSync(f)&&fs.statSync(f).isFile());if(!file)return res.writeHead(404).end();
 res.setHeader('Content-Type',file.endsWith('.js')?'application/javascript':file.endsWith('.css')?'text/css':file.endsWith('.html')?'text/html':'application/octet-stream');let data=fs.readFileSync(file);if(file.endsWith('.html'))data=data.toString().replaceAll('https://tribu-online.onrender.com','http://127.0.0.1:8791');res.end(data);
});
const fixture=path.join(ROOT,'server/.browser-nested-ogre-fixture.js');
fs.writeFileSync(fixture,fs.readFileSync(path.join(ROOT,'server/server.js'),'utf8')+"\nconst originalRandomInt=require('crypto').randomInt;require('crypto').randomInt=(...args)=>args[0]===1&&args[1]===7?6:originalRandomInt(...args);\nio.on('connection',s=>s.on('testCorruption',(_,ack)=>{roomForSocket(s).gameVersion='corruption';ack({ok:true})}));");
(async()=>{const child=spawn(process.execPath,[fixture],{env:{...process.env,PORT:'8791',TRIBU_HISTORY_FILE:path.join(require('os').tmpdir(),'tribu-cascade-test-'+Date.now()+'.json')},stdio:['ignore','pipe','pipe']});let browser,p1,p2;try{await new Promise(r=>child.stdout.on('data',b=>{if(String(b).includes('listening'))r()}));await new Promise(r=>server.listen(8792,'127.0.0.1',r));p1=await connect();p2=await connect();await ack(p1,'createRoom',{code:'UITEST',name:'La partie des amis',maxHumans:2,bots:0,mode:'2v3',pseudo:'Alice'});const joined=await ack(p2,'joinRoom',{code:'UITEST',pseudo:'Bob'});await ack(p1,'setReady',true);await ack(p2,'setReady',true);assert((await ack(p1,'launchGame')).ok);
browser=await chromium.launch({channel:process.env.TRIBU_BROWSER_CHANNEL||'msedge',headless:true});const page=await browser.newPage();const errors=[];page.on('pageerror',e=>errors.push(e.message));await page.goto('http://127.0.0.1:8792');
const v1=(await ack(p1,'requestGameState')).game;
for(let i=0;i<2;i++){const sock=v1.youIndex===i?p1:p2,g=(await ack(sock,'requestGameState')).game;assert((await ack(sock,'setupComplete',{color:i?'#ffd92f':'#ff4fc3',portrait:i?'R_A':'GB_A',regions:Object.keys(g.board).filter(k=>k[0]===g.players[i].province&&!g.board[k].hostile).slice(0,2)})).ok)}

await ack(p1,'testCorruption');
const bootstrap=(await ack(p1,'requestLegacyState')).bootstrap;
const actor=v1.youIndex,other=1-actor;
await page.evaluate(({bootstrap,actor,other})=>{
 onlineLegacyBootstrap(bootstrap,{code:'UITEST'});
 G.active=actor;G.phase='play';G.gameVersion='corruption';G.players.forEach(p=>{p.hand=[];p.inPlay=[];p.inPlayUID=[];p.gold=10;p.bot=false;p.decimated=false});Object.values(G.b).forEach(c=>{c.owner=null;c.units=0;c.hostile=false;c.npcTribe=null;c.building=null});Object.values(G.sea).forEach(c=>c.fleets={});
 p(actor).inPlay=[CARDS.findIndex(c=>c.allianceTribe==='ogres')];p(actor).inPlayUID=['ogre'];Object.assign(G.b.H3,{owner:actor,units:2,npcTribe:'ogres'});Object.assign(G.b.C2,{owner:actor,units:3});Object.assign(G.b.C4,{owner:other,units:3});
 const parent={kind:'land',target:'C3',attacker:actor,defender:other,attackUnits:4,attackOrigins:[{region:'F1',moves:[0,0,0,0]}],stack:[{cardId:1}],ogrePower:{actor,roll:4,cancelled:false,settled:false}};
 battle={kind:'land',target:'D3',attacker:other,defender:actor,attackUnits:2,attackOrigins:[{region:'E1',moves:[0,0]}],stack:[{cardId:2}],fromShadow:true};battleStack=[{battle:parent,seconds:9}];
 for(const b of [parent,battle])Object.assign(b,{priorityOrder:[actor,other],priorityIndex:0,consecutivePasses:0,seconds:15,defenseBase:2,defOriginalUnits:2,epicDefenderUnits:2,attackMove:[]});
 goldReaction={receiver:actor,amount:2,source:'test',after:'play',seconds:8,pausedByBattle:true};G.discard=[];
 clearTimeout(onlineLegacyPushTimer);
},{bootstrap,actor,other});
const seed=await page.evaluate(()=>onlineLegacySnapshot());
assert((await ack(p1,'legacyCommit',{baseRevision:0,actorIndex:actor,snapshot:seed})).ok);
const page2=await browser.newPage();await page2.goto('http://127.0.0.1:8792');
const pages=[page,page2],ss=[p1,p2];
for(let i=0;i<2;i++){
 await pages[i].exposeFunction('auctionServerAck',(event,payload)=>ack(ss[i],event,payload));
 const initial=await ack(ss[i],'requestLegacyState');
 await pages[i].evaluate(({packet,bootstrap})=>{
 onlineSocket={id:'test',connected:true,emit(){}};
 if(!G?.online)onlineLegacyBootstrap(bootstrap,{code:'UITEST'});
 onlineAck=async(event,payload)=>{const res=await auctionServerAck(event,payload);if(res.ok)return res;const e=new Error(res.error);e.current=res.current;throw e};
 onlineLegacyApply(packet);
 },{packet:initial,bootstrap:initial.bootstrap});
 ss[i].on('legacyState',packet=>pages[i].evaluate(packet=>onlineLegacyApply(packet),packet).catch(()=>{}));
}

await page.evaluate(async()=>{applyBattleRegionDestruction(['F1','E1']);finishDestroyedBattle();render();await onlineLegacyPushPriorityTerminalNow(localViewer())});
await page2.waitForFunction(()=>G.allianceLoss?.plan.kind==='ogre');
assert.equal(await page.evaluate(()=>resolveBattle()),false);
for(let turn=0;turn<2;turn++){
 const owner=await page.evaluate(()=>G.allianceLoss.plan.player),chooser=owner===actor?page:page2,sock=owner===actor?p1:p2;
 await chooser.waitForFunction(i=>G.allianceLoss?.plan.player===i,owner);assert(await chooser.evaluate(()=>goldReaction.pausedByCard));
 if(turn===1){const recovery=await ack(sock,'requestLegacyState');await chooser.reload();await chooser.evaluate(packet=>{onlineSocket={id:'test',connected:true,emit(){}};onlineLegacyBootstrap(packet.bootstrap,{code:'UITEST'});onlineAck=async(event,payload)=>{const res=await auctionServerAck(event,payload);if(res.ok)return res;const e=new Error(res.error);e.current=res.current;throw e};onlineLegacyApply(packet)},recovery)}
 const region=owner===actor?'C2':'C4';await chooser.locator('[data-loss-region="'+region+'"][data-loss-group="stationed"]').click();await chooser.waitForFunction(()=>G.allianceLoss.plan.regions[0].chosen.stationed===1);
 await chooser.locator('[data-loss-confirm]').click();await page.waitForFunction(i=>!G.allianceLoss||G.allianceLoss.plan.player!==i,owner);
 if(turn===0){assert(await page.evaluate(()=>goldReaction.pausedByCard));assert.equal(await page.evaluate(i=>p(i).gold,actor),10)}
}
await page2.waitForFunction(()=>!G.allianceLoss);for(const view of pages){assert.deepEqual(await view.evaluate(()=>({battle:!!battle,stack:battleStack.length,c2:G.b.C2.units,c4:G.b.C4.units,discard:G.discard.slice().sort(),paused:!!goldReaction.pausedByCard})),{battle:false,stack:0,c2:2,c4:2,discard:[1,2],paused:false});assert((await view.evaluate(()=>goldReaction.seconds))>=9)}
await page.evaluate(()=>{clearGoldReactionTimer();resolveGoldGain()});await page2.waitForFunction(()=>!goldReaction);assert.equal(await page2.evaluate(i=>p(i).gold,actor),12);
const final=await ack(p1,'requestLegacyState');assert.equal(final.snapshot.g.players[actor].gold,12);assert.equal(final.snapshot.g.allianceLoss,undefined);
assert.deepEqual(errors,[]);console.log('PASS online nested Ogre cascade: both attacks destroyed, cards discarded once, two owner loss choices, reload during second choice, Gold held until completion and paid once.');
}finally{if(browser)await browser.close();p1?.disconnect();p2?.disconnect();child.kill();server.close();await new Promise(r=>child.once('exit',r));fs.unlinkSync(fixture)}})().catch(e=>{console.error(e);process.exitCode=1});
