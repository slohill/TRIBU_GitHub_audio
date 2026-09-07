from pathlib import Path

# --- server ---
p=Path('server/server.js')
s=p.read_text()

anchor="const FACTION_DEF = [1,1,3];\n"
insert="""const FACTION_DEF = [1,1,3];
const BATTLE_CARD_NAMES = {1:'Balistes',3:'Catapultes',11:'Mur de pique',12:'Montures',14:'Pluie de flèches',21:'Pyrodontes de guerre'};
"""
assert anchor in s
s=s.replace(anchor,insert,1)

anchor="function resolveBasicLandBattle(game,index,target,n){"
start=s.index(anchor)
end=s.index("function ownedMovableAt", start)
new_block=r'''function battleDefenseBase(game,target,defender,hostile,kind){
  if(hostile)return 5;
  if(defender===null||defender===undefined)return 0;
  const units=kind==='sea'?Number(game.sea[target].fleets[defender]||0):Number(game.board[target].units||0);
  return units*(FACTION_DEF[game.players[defender].faction]||1);
}
function battlePower(game,side){
  const b=game.battle;if(!b)return 0;
  if(side==='attacker')return b.attackUnits+(game.players[b.attacker].attackTurnBonus||0)+(b.attackBonus||0);
  return b.defenseBase+((b.defender!==null&&b.defender!==undefined)?(game.players[b.defender].defenseTurnBonus||0):0)+(b.defenseBonus||0);
}
function battlePublicView(game,youIndex){
  const b=game.battle;if(!b)return null;
  const priority=b.priorityOrder[b.priorityIndex]??null;
  return {kind:b.kind,target:b.target,attacker:b.attacker,defender:b.defender,hostile:b.hostile,attackUnits:b.attackUnits,defenseBase:b.defenseBase,attack:battlePower(game,'attacker'),defense:battlePower(game,'defender'),stack:b.stack.slice(),priority,deadline:b.deadline||null,canAct:priority===youIndex};
}
function battleCardLegalityServer(game,owner,cardId,choice){
  const b=game.battle,name=BATTLE_CARD_NAMES[cardId];if(!b||!name)return {ok:false,error:'Cette carte ne peut pas être jouée dans cette bataille.'};
  if(owner!==b.attacker&&owner!==b.defender)return {ok:false,error:'Vous ne participez pas à cette bataille.'};
  if(name==='Mur de pique'&&owner!==b.defender)return {ok:false,error:'Mur de pique est réservé au défenseur.'};
  if(name==='Montures'&&owner!==b.attacker)return {ok:false,error:'Montures donne +4 uniquement à l’attaquant pendant une bataille.'};
  if(name==='Pyrodontes de guerre'){
    if(owner!==b.attacker)return {ok:false,error:'Seul l’attaquant peut jouer Pyrodontes.'};
    if(b.kind!=='land')return {ok:false,error:'Pyrodontes ne peut être joué qu’en bataille terrestre.'};
    if(TERRAIN[b.target]!=='t')return {ok:false,error:'La région doit être tempérée.'};
  }
  if(name==='Balistes'&&!['attack','defense'].includes(choice))return {ok:false,error:'Choisissez Attaque ou Défense pour Balistes.'};
  return {ok:true,name};
}
function applyBattleCard(game,owner,cardId,choice){
  const b=game.battle,name=BATTLE_CARD_NAMES[cardId];let bonus=0,side=owner===b.attacker?'attacker':'defender';
  if(name==='Catapultes')bonus=5;
  else if(name==='Mur de pique'){bonus=4;side='defender'}
  else if(name==='Montures'){bonus=4;side='attacker'}
  else if(name==='Pluie de flèches')bonus=3;
  else if(name==='Pyrodontes de guerre'){bonus=5;side='attacker'}
  else if(name==='Balistes'){
    if(choice==='attack')game.players[owner].attackTurnBonus=(game.players[owner].attackTurnBonus||0)+2;
    else game.players[owner].defenseTurnBonus=(game.players[owner].defenseTurnBonus||0)+2;
  }
  if(side==='attacker')b.attackBonus=(b.attackBonus||0)+bonus;else b.defenseBonus=(b.defenseBonus||0)+bonus;
  b.stack.push({owner,cardId,name,side:choice||side,bonus});
}
function resolveAuthoritativeBattle(room){
  const game=room.game,b=game&&game.battle;if(!b)return null;
  clearTimeout(room.battleTimer);room.battleTimer=null;
  const a=battlePower(game,'attacker'),d=battlePower(game,'defender'),attacker=b.attacker,defender=b.defender,target=b.target;
  let result='defense',survivors=0;
  if(b.kind==='land'){
    const c=game.board[target];
    if(a>d){survivors=Math.min(b.attackUnits,a-d);if(d>=10)game.players[attacker].pvPermanent=(game.players[attacker].pvPermanent||0)+1;c.owner=attacker;c.units=survivors;c.hostile=false;result='attack'}
    else if(b.hostile){c.owner=null;c.units=0;c.hostile=true}
    else if(defender!==null){if(a>=10)game.players[defender].pvPermanent=(game.players[defender].pvPermanent||0)+1;const coeff=FACTION_DEF[game.players[defender].faction]||1;survivors=a===d?1:Math.max(1,Math.min(b.defOriginalUnits,Math.ceil((d-a)/coeff)));c.units=survivors}
  }else{
    const sea=game.sea[target];
    if(a>d){survivors=Math.min(b.attackUnits,a-d);if(d>=10)game.players[attacker].pvPermanent=(game.players[attacker].pvPermanent||0)+1;sea.fleets[defender]=0;sea.fleets[attacker]=(sea.fleets[attacker]||0)+survivors;result='attack'}
    else{if(a>=10)game.players[defender].pvPermanent=(game.players[defender].pvPermanent||0)+1;const coeff=FACTION_DEF[game.players[defender].faction]||1;survivors=a===d?1:Math.max(1,Math.min(b.defOriginalUnits,Math.ceil((d-a)/coeff)));sea.fleets[defender]=survivors}
  }
  game.lastEvent={kind:b.kind==='sea'?'seaBattle':'battle',target,attacker,defender,hostile:b.hostile,attack:a,defense:d,result,survivors,stack:b.stack.slice()};
  game.battle=null;game.revision++;emitGame(room);return game.lastEvent;
}
function battlePass(room,index){
  const b=room.game&&room.game.battle;if(!b)return false;
  const priority=b.priorityOrder[b.priorityIndex];if(priority!==index)return false;
  b.consecutivePasses++;
  if(b.consecutivePasses>=b.priorityOrder.length){resolveAuthoritativeBattle(room);return true}
  b.priorityIndex=(b.priorityIndex+1)%b.priorityOrder.length;scheduleBattlePriority(room);room.game.revision++;emitGame(room);return true;
}
function scheduleBattlePriority(room){
  clearTimeout(room.battleTimer);const game=room.game,b=game&&game.battle;if(!b)return;
  const priority=b.priorityOrder[b.priorityIndex],pl=game.players[priority];b.deadline=Date.now()+(pl&&pl.bot?700:15000);
  room.battleTimer=setTimeout(()=>{
    if(!room.game||room.game.battle!==b)return;
    if(pl&&pl.bot){
      const options=pl.hand.map((id,handIndex)=>({id,handIndex,legal:battleCardLegalityServer(game,priority,id,id===1?(priority===b.attacker?'attack':'defense'):undefined)})).filter(x=>x.legal.ok);
      const mine=priority===b.attacker?battlePower(game,'attacker'):battlePower(game,'defender'),other=priority===b.attacker?battlePower(game,'defender'):battlePower(game,'attacker');
      if(options.length&&mine<=other+2){const pick=options[0],choice=pick.id===1?(priority===b.attacker?'attack':'defense'):undefined;pl.hand.splice(pick.handIndex,1);game.discard.push(pick.id);applyBattleCard(game,priority,pick.id,choice);b.consecutivePasses=0;b.priorityIndex=(b.priorityIndex+1)%b.priorityOrder.length;game.revision++;emitGame(room);scheduleBattlePriority(room);return}
    }
    battlePass(room,priority);
  },pl&&pl.bot?700:15000);
}
function startAuthoritativeBattle(room,index,target,n,kind='land',defender=null){
  const game=room.game,hostile=kind==='land'&&!!game.board[target].hostile;
  if(kind==='land'&&defender===null&&!hostile)defender=game.board[target].owner;
  const defOriginalUnits=hostile?0:(kind==='sea'?Number(game.sea[target].fleets[defender]||0):Number(game.board[target].units||0));
  const priorityOrder=hostile?[index]:[defender,index];
  game.battle={kind,target,attacker:index,defender,hostile,attackUnits:n,defOriginalUnits,defenseBase:battleDefenseBase(game,target,defender,hostile,kind),attackBonus:0,defenseBonus:0,stack:[],priorityOrder,priorityIndex:0,consecutivePasses:0,deadline:null};
  scheduleBattlePriority(room);return game.battle;
}
'''
s=s[:start]+new_block+s[end:]

# public battle state
anchor="    play: game.status==='playing' ? { movePool: game.active===youIndex ? {...(game.movePool||{})} : {}, destinationUseCount: {...(game.destinationUseCount||{})}, attacked: [...(game.attacked||[])], lastEvent: game.lastEvent||null } : null,\n"
assert anchor in s
s=s.replace(anchor,anchor+"    battle: battlePublicView(game,youIndex),\n",1)

# player turn bonuses
s=s.replace("    hand: []\n  }));","    hand: [],\n    attackTurnBonus: 0,\n    defenseTurnBonus: 0\n  }));",1)
s=s.replace("      hand: []\n    });","      hand: [],\n      attackTurnBonus: 0,\n      defenseTurnBonus: 0\n    });",1)
# reset active player's temporary turn bonuses at turn advance
anchor="  game.phase='start';game.movePool={};game.destinationUseCount={};game.attacked=[];game.recruitSnapshot=null;game.revision++;\n"
assert anchor in s
s=s.replace(anchor,"  game.phase='start';game.movePool={};game.destinationUseCount={};game.attacked=[];game.recruitSnapshot=null;game.battle=null;game.players[game.active].attackTurnBonus=0;game.players[game.active].defenseTurnBonus=0;game.revision++;\n",1)
# initialize game.battle
s=s.replace("    movePool: {}, destinationUseCount: {}, attacked: [], lastEvent:null, lastRoll:null,\n","    movePool: {}, destinationUseCount: {}, attacked: [], battle:null, lastEvent:null, lastRoll:null,\n",1)

# gameAction permission: battle reactions before active-turn gate
old="""    const index = humanGameIndex(room, socket.id);
    if (index < 0) return rejectGameAction(ack, 'Joueur introuvable.');
    if (game.active !== index) return rejectGameAction(ack, 'Ce n’est pas votre tour.');

    const type = String(payload.type || '');
"""
new="""    const index = humanGameIndex(room, socket.id);
    if (index < 0) return rejectGameAction(ack, 'Joueur introuvable.');
    const type = String(payload.type || '');
    if(game.battle){
      const b=game.battle,priority=b.priorityOrder[b.priorityIndex];
      if(type==='BATTLE_PASS'){
        if(priority!==index)return rejectGameAction(ack,'Vous n’avez pas la priorité.');
        ack({ok:true});battlePass(room,index);return;
      }
      if(type==='BATTLE_CARD'){
        if(priority!==index)return rejectGameAction(ack,'Vous n’avez pas la priorité.');
        const handIndex=Math.floor(Number(payload.handIndex));if(handIndex<0||handIndex>=game.players[index].hand.length)return rejectGameAction(ack,'Carte introuvable.');
        const cardId=game.players[index].hand[handIndex],choice=payload.choice===undefined?undefined:String(payload.choice),legal=battleCardLegalityServer(game,index,cardId,choice);if(!legal.ok)return rejectGameAction(ack,legal.error);
        game.players[index].hand.splice(handIndex,1);game.discard.push(cardId);applyBattleCard(game,index,cardId,choice);b.consecutivePasses=0;b.priorityIndex=(b.priorityIndex+1)%b.priorityOrder.length;game.revision++;ack({ok:true});emitGame(room);scheduleBattlePriority(room);return;
      }
      return rejectGameAction(ack,'Une bataille est en cours : terminez d’abord les réactions.');
    }
    if (game.active !== index) return rejectGameAction(ack, 'Ce n’est pas votre tour.');
"""
assert old in s
s=s.replace(old,new,1)

s=s.replace("if(enemy){game.attacked=game.attacked||[];game.attacked.push(target);game.lastEvent=resolveBasicLandBattle(game,index,target,total)}","if(enemy){game.attacked=game.attacked||[];game.attacked.push(target);startAuthoritativeBattle(room,index,target,total,'land',null);game.lastEvent={kind:'battlePending',target,attacker:index}}",1)
s=s.replace("if(defender===null){sea.fleets[index]=(sea.fleets[index]||0)+total;game.lastEvent={kind:'seaMove',target,player:index,units:total}}else game.lastEvent=resolveBasicSeaBattle(game,index,target,total,defender);","if(defender===null){sea.fleets[index]=(sea.fleets[index]||0)+total;game.lastEvent={kind:'seaMove',target,player:index,units:total}}else{startAuthoritativeBattle(room,index,target,total,'sea',defender);game.lastEvent={kind:'seaBattlePending',target,attacker:index,defender}}",1)

p.write_text(s)

# --- client ---
p=Path('index.html')
s=p.read_text()
# add battle render helper before onlineLockControls
anchor="function onlineLockControls(){\n"
helper=r'''function onlineBattleCardName(id){return CARDS[id]&&CARDS[id].name||('Carte '+id)}
function onlineRenderAuthoritativeBattle(){
 const st=onlineGameState,b=st&&st.battle,panel=$('battlePanel');if(!panel)return;
 panel.classList.toggle('hidden',!b);if(!b)return;
 const attacker=st.players[b.attacker],defender=b.hostile?null:st.players[b.defender];
 $('battleSideInfo').innerHTML='<b>'+onlineEscape(attacker?attacker.pseudo:'Attaquant')+'</b> : '+b.attack+' Attaque<br>'+(b.hostile?'PNJ hostile':('<b>'+onlineEscape(defender?defender.pseudo:'Défenseur')+'</b> : '+b.defense+' Défense'));
 const mine=b.priority===st.youIndex;$('priorityInfo').innerHTML=mine?'<b>À vous de réagir.</b> Jouez une carte tactique ou passez.':'Priorité : <b>'+onlineEscape(st.players[b.priority]?st.players[b.priority].pseudo:'—')+'</b>';
 const seconds=b.deadline?Math.max(0,Math.ceil((b.deadline-Date.now())/1000)):0;$('priorityTimer').textContent=seconds+' s';
 const buttons=$('tacticalButtons');buttons.innerHTML='';
 if(mine){
   const hand=(st.players[st.youIndex]&&st.players[st.youIndex].hand)||[];
   hand.forEach((id,handIndex)=>{
     const name=onlineBattleCardName(id);if(!['Catapultes','Mur de pique','Montures','Pluie de flèches','Pyrodontes de guerre','Balistes'].includes(name))return;
     if(name==='Mur de pique'&&st.youIndex!==b.defender)return;if(name==='Montures'&&st.youIndex!==b.attacker)return;if(name==='Pyrodontes de guerre'&&(st.youIndex!==b.attacker||b.kind!=='land'||R[b.target][1]!=='t'))return;
     if(name==='Balistes'){
       [['attack','Balistes +2 Attaque'],['defense','Balistes +2 Défense']].forEach(([choice,label])=>{const bt=document.createElement('button');bt.textContent=label;bt.onclick=()=>onlineGameAction('BATTLE_CARD',{handIndex,choice});buttons.appendChild(bt)});return;
     }
     const bt=document.createElement('button');bt.textContent=name;bt.onclick=()=>onlineGameAction('BATTLE_CARD',{handIndex});buttons.appendChild(bt);
   });
   const pass=document.createElement('button');pass.textContent='Passer';pass.onclick=()=>onlineGameAction('BATTLE_PASS');buttons.appendChild(pass);
 }
 const stack=$('priorityStack');stack.innerHTML=(b.stack||[]).map(x=>'<div class="stackCard">'+onlineEscape(st.players[x.owner]?st.players[x.owner].pseudo:'Joueur')+' — '+onlineEscape(x.name)+(x.bonus?' (+'+x.bonus+')':'')+'</div>').join('');
 const spot=$('map')&&$('map').querySelector('.spot[data-region="'+b.target+'"]');if(spot)spot.classList.add('battleLoc');
}
'''
assert anchor in s
s=s.replace(anchor,helper+anchor,1)

# onlineRefreshPlayUi: stop movement when battle active
anchor=" if(st.status!=='playing'||st.active!==st.youIndex)return;\n"
assert anchor in s
s=s.replace(anchor," if(st.battle){if(hint)hint.textContent='Bataille en cours — terminez les réactions.';return}\n"+anchor,1)
# lock controls and battle rendering
anchor=" const mine=onlineGameState.active===onlineGameState.youIndex&&onlineGameState.status==='playing'&&!onlineWelcomeActive,start=mine&&onlineGameState.phase==='start',recruiting=mine&&onlineGameState.phase==='recruit',playing=mine&&onlineGameState.phase==='play',oracleMove=mine&&onlineGameState.phase==='oracleMove',oracleRoll=mine&&onlineGameState.phase==='oracleRoll';\n"
assert anchor in s
s=s.replace(anchor," const battleActive=!!onlineGameState.battle;\n"+anchor.replace("start=mine&&","start=mine&&!battleActive&&").replace("recruiting=mine&&","recruiting=mine&&!battleActive&&").replace("playing=mine&&","playing=mine&&!battleActive&&").replace("oracleMove=mine&&","oracleMove=mine&&!battleActive&&").replace("oracleRoll=mine&&","oracleRoll=mine&&!battleActive&&"),1)
anchor=" const n=$('status');if(n)n.innerHTML+='<div class=\"botNotice\">🌐 Online autoritaire — tour, déplacements et Oracle synchronisés par le serveur.'+(onlineGameState.lastRoll?' Dernier dé Oracle : <b>'+onlineGameState.lastRoll+'</b>.':'')+'</div>';onlineRefreshPlayUi();\n"
assert anchor in s
s=s.replace(anchor,anchor.replace("onlineRefreshPlayUi();","onlineRenderAuthoritativeBattle();onlineRefreshPlayUi();"),1)

p.write_text(s)
