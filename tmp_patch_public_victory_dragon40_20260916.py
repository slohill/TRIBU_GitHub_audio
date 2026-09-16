from pathlib import Path

p=Path('index.html')
s=p.read_text(encoding='utf-8')

old="""let onlineSfxSeq=0,onlineSfxEvents=[],onlineSfxSeenSeq=0,onlineDirectSfxSeenSeq=0,onlineOraclePresentationSeenSeq=0,onlineAssassinNoticeSeenSeq=0,onlineDragonSixPresentationSeenSeq=0,onlinePublicEventSeenSeq=0,onlineOracleRemoteTick=null,onlineDragonSixRemoteTick=null,onlinePublicEventTick=null;"""
new="""let onlineSfxSeq=0,onlineSfxEvents=[],onlineSfxSeenSeq=0,onlineDirectSfxSeenSeq=0,onlineOraclePresentationSeenSeq=0,onlineAssassinNoticeSeenSeq=0,onlineDragonSixPresentationSeenSeq=0,onlineDragonCursePresentationSeenSeq=0,onlinePublicEventSeenSeq=0,onlineOracleRemoteTick=null,onlineDragonSixRemoteTick=null,onlineDragonCurseRemoteTick=null,onlinePublicEventTick=null,victoryPresentationSeenKey=null;"""
assert old in s
s=s.replace(old,new,1)

old="""function showDragonCurse(i,after){
 const targets=richestDragonRegions(i);
 const paused=!!battle;
 if(paused){clearInterval(battleTick);clearTimeout(botReactionTimer)}
 dragonCurseState={player:i,targets,after,pausedBattle:paused,pausedBattleSeconds:paused?battle.seconds:null};

 // Annonce publique : chaque joueur humain valide l'avoir vue.
 const humans=G.players.map((pl,j)=>({pl,j})).filter(x=>!x.pl.bot).map(x=>x.j);
 dragonPublicState={victim:i,acks:humans,index:0};
 $('dragonPublicText').textContent='La Malédiction du Dragon frappe '+p(i).name+' !';
 $('dragonPublicOverlay').classList.remove('hidden');
 updateDragonPublicPass();
}"""
new="""function showDragonCurseVictimNotice(i){
 $('dragonCurseText').textContent=
`Vous ne vous rassasiez jamais, vous en voulez toujours plus, toujours plus d’or et de diamants…

Cela fait des mois que vous ne parlez plus à vos sujets et votre famille. Vous errez constamment dans vos salles des coffres…

Vos soldats désertent car la malédiction plane sur votre empire…

Vous êtes maudit et le Dragon arrive. Il est là pour s’emparer de vos trésors !`;
 $('dragonCurseOverlay').classList.remove('hidden');
}
function showDragonCurse(i,after){
 const targets=richestDragonRegions(i);
 const paused=!!battle;
 if(paused){clearInterval(battleTick);clearTimeout(botReactionTimer)}
 dragonCurseState={player:i,targets,after,pausedBattle:paused,pausedBattleSeconds:paused?battle.seconds:null};
 audioPlaySfx('dragon',.675);
 if(G&&G.online&&G.online.legacySync){
   G.dragonCursePresentation={seq:Number(G.dragonCursePresentation&&G.dragonCursePresentation.seq||0)+1,victim:i,at:Date.now()};
   onlineDragonCursePresentationSeenSeq=Number(G.dragonCursePresentation.seq);
   if(i===localViewer()&&!G.players[i].bot)showDragonCurseVictimNotice(i);
   else if(G.players[i].bot)setTimeout(continueDragonCurse,350);
   return;
 }

 // Local / hot-seat : chaque joueur humain valide l'annonce avant le texte privé.
 const humans=G.players.map((pl,j)=>({pl,j})).filter(x=>!x.pl.bot).map(x=>x.j);
 dragonPublicState={victim:i,acks:humans,index:0};
 $('dragonPublicText').textContent='La Malédiction du Dragon frappe '+p(i).name+' !';
 $('dragonPublicOverlay').classList.remove('hidden');
 updateDragonPublicPass();
}"""
assert old in s
s=s.replace(old,new,1)

old=""" if(isViewer){
   $('dragonCurseText').textContent=
`Vous ne vous rassasiez jamais, vous en voulez toujours plus, toujours plus d’or et de diamants…

Cela fait des mois que vous ne parlez plus à vos sujets et votre famille. Vous errez constamment dans vos salles des coffres…

Vos soldats désertent car la malédiction plane sur votre empire…

Vous êtes maudit et le Dragon arrive. Il est là pour s’emparer de vos trésors !`;
   $('dragonCurseOverlay').classList.remove('hidden');
 }else{"""
new=""" if(isViewer){
   showDragonCurseVictimNotice(i);
 }else{"""
assert old in s
s=s.replace(old,new,1)

old="""function checkVictory(){
 if(!G||gameOverState)return false;
 let winner=-1,best=-1;"""
new="""function showVictoryPresentation(state){
 if(!state||!Number.isInteger(state.winner)||!G.players[state.winner])return false;
 const winner=state.winner,points=Number(state.points)||victoryPoints(winner);
 $('victoryTitle').textContent='🏆 '+p(winner).name.toUpperCase()+' REMPORTE LA PARTIE !';
 $('victoryText').textContent=p(winner).name+' a '+points+' Point'+(points>1?'s':'')+' de victoire et remporte la partie !';
 $('victoryOverlay').classList.remove('hidden');
 const key=winner+':'+points;
 if(victoryPresentationSeenKey!==key){victoryPresentationSeenKey=key;audioPlaySfxLocal('epicbattle',.92)}
 return true;
}
function checkVictory(){
 if(!G)return false;
 if(gameOverState)return showVictoryPresentation(gameOverState);
 let winner=-1,best=-1;"""
assert old in s
s=s.replace(old,new,1)

old=""" gameOverState={winner,points:best};
 clearTimeout(botTimer);clearTimeout(botReactionTimer);clearInterval(battleTick);clearInterval(shadowTick);
 $('victoryTitle').textContent='🏆 '+p(winner).name.toUpperCase()+' REMPORTE LA PARTIE !';
 $('victoryText').textContent=p(winner).name+' atteint '+best+' Point'+(best>1?'s':'')+' de victoire. Objectif du mode : '+G.victoryTarget+' PV.';
 $('victoryOverlay').classList.remove('hidden');
 log('🏆 '+p(winner).name+' remporte la partie avec '+best+' PV.');
 return true;"""
new=""" gameOverState={winner,points:best};
 clearTimeout(botTimer);clearTimeout(botReactionTimer);clearInterval(battleTick);clearInterval(shadowTick);
 showVictoryPresentation(gameOverState);
 log('🏆 '+p(winner).name+' remporte la partie avec '+best+' PV.');
 return true;"""
assert old in s
s=s.replace(old,new,1)

old="""function showOracleRemoteNotice(name){
 clearInterval(onlineOracleRemoteTick);"""
new="""function showDragonCurseRemoteNotice(victim){
 clearInterval(onlineDragonCurseRemoteTick);
 if(victim===localViewer())return showDragonCurseVictimNotice(victim);
 $('dragonPublicText').textContent='La Malédiction du Dragon frappe '+p(victim).name+' !';
 $('dragonPublicOverlay').classList.remove('hidden');
 let seconds=5;
 const pass=$('dragonPublicPass');
 const close=()=>{clearInterval(onlineDragonCurseRemoteTick);$('dragonPublicOverlay').classList.add('hidden')};
 if(pass){pass.textContent='Passer';pass.onclick=close}
 onlineDragonCurseRemoteTick=setInterval(()=>{seconds--;if(seconds<=0)close()},1000);
}
function showOracleRemoteNotice(name){
 clearInterval(onlineOracleRemoteTick);"""
assert old in s
s=s.replace(old,new,1)

old=""" const dp=G&&G.dragonSixPresentation;
 if(dp&&Number(dp.seq)>onlineDragonSixPresentationSeenSeq){onlineDragonSixPresentationSeenSeq=Number(dp.seq);showDragonSixRemoteNotice(dp.victim)}
 const an=G&&G.assassinNotice;"""
new=""" const dp=G&&G.dragonSixPresentation;
 if(dp&&Number(dp.seq)>onlineDragonSixPresentationSeenSeq){onlineDragonSixPresentationSeenSeq=Number(dp.seq);showDragonSixRemoteNotice(dp.victim)}
 const cp=G&&G.dragonCursePresentation;
 if(cp&&Number(cp.seq)>onlineDragonCursePresentationSeenSeq){onlineDragonCursePresentationSeenSeq=Number(cp.seq);if(!cp.at||Date.now()-Number(cp.at)<30000)showDragonCurseRemoteNotice(cp.victim)}
 const an=G&&G.assassinNotice;"""
assert old in s
s=s.replace(old,new,1)

old="""onlineOraclePresentationSeenSeq=Number(G.oraclePresentation&&G.oraclePresentation.seq||0);onlineAssassinNoticeSeenSeq=Number(G.assassinNotice&&G.assassinNotice.seq||0);onlineDragonSixPresentationSeenSeq=Number(G.dragonSixPresentation&&G.dragonSixPresentation.seq||0);onlinePublicEventSeenSeq=Number(G.publicEventPresentation&&G.publicEventPresentation.seq||0);"""
new="""onlineOraclePresentationSeenSeq=Number(G.oraclePresentation&&G.oraclePresentation.seq||0);onlineAssassinNoticeSeenSeq=Number(G.assassinNotice&&G.assassinNotice.seq||0);onlineDragonSixPresentationSeenSeq=Number(G.dragonSixPresentation&&G.dragonSixPresentation.seq||0);onlineDragonCursePresentationSeenSeq=Number(G.dragonCursePresentation&&G.dragonCursePresentation.seq||0);onlinePublicEventSeenSeq=Number(G.publicEventPresentation&&G.publicEventPresentation.seq||0);"""
assert old in s
s=s.replace(old,new)

# The local test mode must remain exactly unchanged.
assert "$('localTestBtn').onclick=()=>{onlinePseudo();launchLegacyMode('2v3',3)};" in s
p.write_text(s,encoding='utf-8')
