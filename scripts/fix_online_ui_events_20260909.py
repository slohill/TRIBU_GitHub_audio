from pathlib import Path
p=Path('index.html')
s=p.read_text(encoding='utf-8')

def rep(old,new,label):
    global s
    if old not in s: raise SystemExit('MISSING '+label)
    s=s.replace(old,new,1)

# Divination: stable layout on narrow/tablet screens.
rep(".divinationChoices .oraclePick{min-width:125px;font-size:11px}",".divinationChoices .oraclePick{min-width:125px;font-size:11px}\n.divinationPanel{max-height:min(78vh,560px);overflow:auto;line-height:1.35}\n.divinationPanel h3{line-height:1.25;margin-bottom:10px}\n#divinationText{display:block;line-height:1.4;margin:0 0 10px;padding:8px}\n.divinationChoices{align-items:stretch;margin-top:8px}\n.divinationChoices button{white-space:normal;line-height:1.25;min-height:38px;height:auto}\n@media(max-width:760px){.divinationPanel{width:min(460px,90%);padding:10px}.divinationChoices{display:grid;grid-template-columns:1fr}.divinationChoices button,.divinationChoices .oraclePick{min-width:0;width:100%}}","divination css")

# Local-only presentation sequence trackers.
rep("let onlineSfxSeq=0,onlineSfxEvents=[],onlineSfxSeenSeq=0;","let onlineSfxSeq=0,onlineSfxEvents=[],onlineSfxSeenSeq=0,onlineOraclePresentationSeenSeq=0,onlineAssassinNoticeSeenSeq=0,onlineOracleRemoteTick=null;","presentation trackers")

# Assassin notice is canonical data, but visual text is private to victim.
rep(" closeAgentModal();\n audioPlaySfx(killed?'assassin':'fail',killed?.9:.75);\n log(p(actor).name+' joue Assassin sur '+p(target.owner).name+' — '+target.name+' : dé '+roll+'. '+(killed?'Agent éliminé.':'Échec.'));\n showAssassinMapMessage(target.owner,target.name,actor,killed);\n render();"," closeAgentModal();\n audioPlaySfx(killed?'assassin':'fail',killed?.9:.75);\n log(p(actor).name+' joue Assassin sur '+p(target.owner).name+' — '+target.name+' : dé '+roll+'. '+(killed?'Agent éliminé.':'Échec.'));\n G.assassinNotice={seq:Number(G.assassinNotice&&G.assassinNotice.seq||0)+1,targetOwner:target.owner,targetName:target.name,actor,killed};\n if(!G.online||!G.online.legacySync||localViewer()===target.owner)showAssassinMapMessage(target.owner,target.name,actor,killed);\n render();","assassin private event")

# Caravan: visible to everyone; only current human chooser can click Online.
old="""function showCaravanChoice(){
 if(!caravanState)return;
 if(!caravanState.revealed.length||caravanState.pick>=caravanState.order.length){finishCaravan();return}
 const chooser=caravanState.order[caravanState.pick];
 if(G.players[chooser].bot){const j=Math.floor(Math.random()*caravanState.revealed.length);setTimeout(()=>chooseCaravanCard(j),300);return}
 agentModalState={kind:'caravan',chooser};
 openAgentModal('Caravane de commerce',p(chooser).name+' choisit une carte.');
 const close=$('agentClose');if(close){close.disabled=true;close.textContent='Choix obligatoire'}
 const box=$('agentChoices');
 caravanState.revealed.forEach((id,j)=>{
   const c=CARDS[id],b=document.createElement('button');
   b.innerHTML='<b>'+c.name+'</b><br><small>'+c.effect+'</small>';
   b.onclick=()=>chooseCaravanCard(j);
   box.appendChild(b);
 });
 // En mode test local, même les choix des bots restent sous le contrôle du testeur.
}
function chooseCaravanCard(j){
 if(!caravanState||j<0||j>=caravanState.revealed.length)return;
 const chooser=caravanState.order[caravanState.pick];
 const id=caravanState.revealed.splice(j,1)[0];
 G.players[chooser].hand.push(id);audioCardMove();
 log(p(chooser).name+' choisit '+CARDS[id].name+' dans la Caravane.');
 caravanState.pick++;
 showCaravanChoice();
}"""
new="""function showCaravanChoice(){
 if(!caravanState)return;
 if(!caravanState.revealed.length||caravanState.pick>=caravanState.order.length){finishCaravan();return}
 const chooser=caravanState.order[caravanState.pick];
 const online=!!(G.online&&G.online.legacySync),me=localViewer();
 agentModalState={kind:'caravan',chooser};
 openAgentModal('Caravane de commerce',p(chooser).name+' choisit une carte.');
 const close=$('agentClose');if(close){close.disabled=true;close.textContent='Choix obligatoire'}
 const box=$('agentChoices');
 const mayChoose=!online||(!G.players[chooser].bot&&me===chooser);
 caravanState.revealed.forEach((id,j)=>{
   const c=CARDS[id],b=document.createElement('button');
   b.innerHTML='<b>'+c.name+'</b><br><small>'+c.effect+'</small>';
   b.disabled=!mayChoose;
   b.onclick=mayChoose?()=>chooseCaravanCard(j):null;
   box.appendChild(b);
 });
 if(online&&G.players[chooser].bot){
   const info=document.createElement('div');info.className='note';info.textContent='Le bot choisit sa carte…';box.appendChild(info);
   if(onlineLegacyCanExecuteBot()){const j=Math.floor(Math.random()*caravanState.revealed.length);setTimeout(()=>{if(caravanState&&caravanState.order[caravanState.pick]===chooser)chooseCaravanCard(j)},300)}
 }
}
function chooseCaravanCard(j){
 if(!caravanState||j<0||j>=caravanState.revealed.length)return;
 const chooser=caravanState.order[caravanState.pick];
 if(G.online&&G.online.legacySync&&!G.players[chooser].bot&&localViewer()!==chooser)return;
 if(G.online&&G.online.legacySync&&G.players[chooser].bot&&!onlineLegacyCanExecuteBot())return;
 const id=caravanState.revealed.splice(j,1)[0];
 G.players[chooser].hand.push(id);audioCardMove();
 log(p(chooser).name+' choisit '+CARDS[id].name+' dans la Caravane.');
 caravanState.pick++;
 showCaravanChoice();
 if(G&&G.online&&G.online.legacySync)onlineLegacyPushPriorityCardNow();
}"""
rep(old,new,"caravan shared modal")

# Friendly destination preview shows resulting total, not just selected movers.
rep("function selected(){return Object.values(picks).reduce((a,b)=>a+b,0)}","function selected(){return Object.values(picks).reduce((a,b)=>a+b,0)}\nfunction previewDestinationUnits(id){\n const moving=selected();if(!moving)return 0;\n if(isSea(id))return (G.sea[id].fleets[G.active]||0)+moving;\n const c=G.b[id];return c&&c.owner===G.active?c.units+moving:moving;\n}","destination preview helper")
rep("if(dest===id&&selected()>0&&!isPvpPreview){const g=document.createElement('span');g.className='ghost';g.textContent=selected();b.appendChild(g)}","if(dest===id&&selected()>0&&!isPvpPreview){const g=document.createElement('span');g.className='ghost';g.textContent=previewDestinationUnits(id);b.appendChild(g)}","destination ghost total")

# Oracle presentation event is part of canonical G; recipients replay visual + synced SFX.
rep(" G.oracleActive=id;const o=ORACLES[id];\n log('🔮 Oracle activé : '+o.name+'.');\n audioPlaySfx('oracle',.82);"," G.oracleActive=id;const o=ORACLES[id];\n G.oraclePresentation={seq:Number(G.oraclePresentation&&G.oraclePresentation.seq||0)+1,name:o.name};\n log('🔮 Oracle activé : '+o.name+'.');\n audioPlaySfx('oracle',.82);","oracle presentation event")

# Remote notice is visual only: never owns/resumes Oracle rules.
insert="""function showOracleRemoteNotice(name){
 clearInterval(onlineOracleRemoteTick);
 $('oracleNoticeTitle').textContent='ORACLE ACTIVÉ — '+name.toUpperCase();
 $('oracleNoticeText').textContent=oracleEffectText(name);
 let seconds=5;$('oracleNoticeTimer').textContent='5 s';$('oracleNoticeOverlay').classList.remove('hidden');
 onlineOracleRemoteTick=setInterval(()=>{seconds--;$('oracleNoticeTimer').textContent=Math.max(0,seconds)+' s';if(seconds<=0){clearInterval(onlineOracleRemoteTick);$('oracleNoticeOverlay').classList.add('hidden')}},1000);
}
function onlineApplyPrivatePresentations(me){
 const op=G&&G.oraclePresentation;
 if(op&&Number(op.seq)>onlineOraclePresentationSeenSeq){onlineOraclePresentationSeenSeq=Number(op.seq);showOracleRemoteNotice(op.name)}
 const an=G&&G.assassinNotice;
 if(an&&Number(an.seq)>onlineAssassinNoticeSeenSeq){onlineAssassinNoticeSeenSeq=Number(an.seq);if(an.targetOwner===me)showAssassinMapMessage(an.targetOwner,an.targetName,an.actor,!!an.killed)}
}
"""
needle="function onlineLegacyApply(packet){"
if needle not in s: raise SystemExit('MISSING apply insertion')
s=s.replace(needle,insert+needle,1)

# On received snapshot, reopen Caravan for all and replay private/global presentations.
rep("onlineLegacyLastDigest=onlineLegacyDigest();render();onlineLegacyLastDigest=onlineLegacyDigest();onlineLegacyApplying=false;onlineLegacyLockControls();","onlineLegacyLastDigest=onlineLegacyDigest();render();\n if(caravanState)showCaravanChoice();\n onlineApplyPrivatePresentations(me);\n onlineLegacyLastDigest=onlineLegacyDigest();onlineLegacyApplying=false;onlineLegacyLockControls();","apply presentations")

# Bootstrap should not replay old presentation events from before joining.
rep("onlineSfxSeq=0;onlineSfxEvents=[];onlineSfxSeenSeq=0;","onlineSfxSeq=0;onlineSfxEvents=[];onlineSfxSeenSeq=0;onlineOraclePresentationSeenSeq=Number(G.oraclePresentation&&G.oraclePresentation.seq||0);onlineAssassinNoticeSeenSeq=Number(G.assassinNotice&&G.assassinNotice.seq||0);","bootstrap presentation seq")

p.write_text(s,encoding='utf-8')
