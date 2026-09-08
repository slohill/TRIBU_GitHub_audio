from pathlib import Path
p=Path('index.html');s=p.read_text()
old="""function onlineLegacyCanPublishLiveBot(){
 return !!(G&&G.online&&G.online.legacySync&&!onlineLegacyApplying&&onlineSocket&&G.players[G.active]&&G.players[G.active].bot&&onlineLegacyCanExecuteBot());
}"""
new="""function onlineLegacyCanPublishLiveBot(){
 if(!(G&&G.online&&G.online.legacySync&&!onlineLegacyApplying&&onlineSocket&&G.players[G.active]&&G.players[G.active].bot&&onlineLegacyCanExecuteBot()))return false;
 if(battle){const priority=currentPriorityPlayer();if(Number.isInteger(priority)&&!G.players[priority].bot&&priority!==G.online.myPlayerIndex)return false;}
 return true;
}"""
assert old in s;s=s.replace(old,new,1)
p.write_text(s)
