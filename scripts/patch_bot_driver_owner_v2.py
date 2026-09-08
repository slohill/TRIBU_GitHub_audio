from pathlib import Path
p=Path('index.html');s=p.read_text()
old=""" if(G.online&&G.online.legacySync&&G.players[G.active]&&G.players[G.active].bot&&G.players[previousActive]&&!G.players[previousActive].bot)onlineLegacyBotDriverOwner=previousActive;"""
new=""" if(G.online&&G.online.legacySync&&G.players[G.active]&&G.players[G.active].bot&&G.players[previousActive]&&!G.players[previousActive].bot){
   onlineLegacyBotDriverOwner=previousActive;
   if(G.online.myPlayerIndex===previousActive)G.online.botDriverOwner=previousActive;
 }"""
assert old in s;s=s.replace(old,new,1)
# Keep driver in G.online as well; G.online is already part of snapshot except viewer-specific fields.
old="""function onlineLegacyDriverIndex(){
 if(!G)return -1;
 if(Number.isInteger(onlineLegacyBotDriverOwner)&&G.players[onlineLegacyBotDriverOwner]&&!G.players[onlineLegacyBotDriverOwner].bot)return onlineLegacyBotDriverOwner;
 return G.players.findIndex(pl=>!pl.bot);
}"""
new="""function onlineLegacyDriverIndex(){
 if(!G)return -1;
 const synced=G.online&&Number.isInteger(G.online.botDriverOwner)?G.online.botDriverOwner:onlineLegacyBotDriverOwner;
 if(Number.isInteger(synced)&&G.players[synced]&&!G.players[synced].bot)return synced;
 return G.players.findIndex(pl=>!pl.bot);
}"""
assert old in s;s=s.replace(old,new,1)
old=""" if(G.players[G.active]&&!G.players[G.active].bot)onlineLegacyBotDriverOwner=null;"""
new=""" if(G.players[G.active]&&!G.players[G.active].bot){onlineLegacyBotDriverOwner=null;if(G.online)delete G.online.botDriverOwner;}"""
s=s.replace(old,new)
p.write_text(s)
