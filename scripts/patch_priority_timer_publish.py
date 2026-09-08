from pathlib import Path
p=Path('index.html');s=p.read_text()
old="""if(!isHotseatMode()&&onlineLegacyOwnsBattlePriority())battleTick=setInterval(()=>{if(!battle)return;battle.seconds--;renderBattle();if(battle.seconds<=0)passPriority()},1000);"""
new="""if(!isHotseatMode()&&onlineLegacyOwnsBattlePriority())battleTick=setInterval(()=>{if(!battle)return;battle.seconds--;renderBattle();if(battle.seconds<=0){passPriority();if(G&&G.online&&G.online.legacySync)onlineLegacyMaybePush()}},1000);"""
# two possible timer sites; replace all exact occurrences
assert old in s;s=s.replace(old,new)
old2="""    if(battle.seconds<=0) passPriority();"""
new2="""    if(battle.seconds<=0){passPriority();if(G&&G.online&&G.online.legacySync)onlineLegacyMaybePush()}"""
assert old2 in s;s=s.replace(old2,new2,1)
p.write_text(s)
