from pathlib import Path
p=Path('index.html');s=p.read_text()
old="""function onlineLegacyDriverIndex(){
 if(!G)return -1;
 return G.players.findIndex(pl=>!pl.bot);
}
function onlineLegacyIsDriver(){return !!(G&&G.online&&G.online.legacySync&&G.online.myPlayerIndex===onlineLegacyDriverIndex())}
function onlineLegacyCanExecuteBot(){
 return !!(G&&G.online&&G.online.legacySync&&Number.isInteger(G.online.myPlayerIndex)&&G.players[G.online.myPlayerIndex]&&!G.players[G.online.myPlayerIndex].bot);
}"""
new="""let onlineLegacyBotDriverOwner=null;
function onlineLegacyDriverIndex(){
 if(!G)return -1;
 if(Number.isInteger(onlineLegacyBotDriverOwner)&&G.players[onlineLegacyBotDriverOwner]&&!G.players[onlineLegacyBotDriverOwner].bot)return onlineLegacyBotDriverOwner;
 return G.players.findIndex(pl=>!pl.bot);
}
function onlineLegacyIsDriver(){return !!(G&&G.online&&G.online.legacySync&&G.online.myPlayerIndex===onlineLegacyDriverIndex())}
function onlineLegacyCanExecuteBot(){
 return !!(G&&G.online&&G.online.legacySync&&G.online.myPlayerIndex===onlineLegacyDriverIndex());
}"""
assert old in s;s=s.replace(old,new,1)
old=""" G.players.forEach(pl=>{pl.attackTurnBonus=0;pl.defenseTurnBonus=0});
 G.active=(G.active+1)%G.players.length;if(G.active===0)G.turn++;"""
new=""" G.players.forEach(pl=>{pl.attackTurnBonus=0;pl.defenseTurnBonus=0});
 const previousActive=G.active;
 G.active=(G.active+1)%G.players.length;if(G.active===0)G.turn++;
 if(G.online&&G.online.legacySync&&G.players[G.active]&&G.players[G.active].bot&&G.players[previousActive]&&!G.players[previousActive].bot)onlineLegacyBotDriverOwner=previousActive;
 if(G.online&&G.online.legacySync&&G.players[G.active]&&!G.players[G.active].bot)onlineLegacyBotDriverOwner=null;"""
assert old in s;s=s.replace(old,new,1)
# Applying a live snapshot during bots must not turn a spectator into a bot executor.
old=""" onlineLegacyRevision=packet.revision||0;dest=null;picks={};
 (G.players||[]).forEach((_,i)=>agentDefaults(i));"""
new=""" onlineLegacyRevision=packet.revision||0;dest=null;picks={};
 if(G.players[G.active]&&!G.players[G.active].bot)onlineLegacyBotDriverOwner=null;
 (G.players||[]).forEach((_,i)=>agentDefaults(i));"""
assert old in s;s=s.replace(old,new,1)
p.write_text(s)
