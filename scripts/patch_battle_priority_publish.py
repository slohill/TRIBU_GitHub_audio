from pathlib import Path
p=Path('index.html');s=p.read_text()
old=""" if(G.players[G.active]&&G.players[G.active].bot)return onlineLegacyCanExecuteBot();
 return true;
}"""
new=""" if(G.players[G.active]&&G.players[G.active].bot){
   if(battle&&currentPriorityPlayer()===me&&!G.players[me].bot)return true;
   return onlineLegacyCanExecuteBot();
 }
 return true;
}"""
# replace only onlineLegacyCanPublish occurrence
pos=s.index('function onlineLegacyCanPublish()');idx=s.index(old,pos);s=s[:idx]+s[idx:].replace(old,new,1);p.write_text(s)
