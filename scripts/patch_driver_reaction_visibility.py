from pathlib import Path
p=Path('index.html');s=p.read_text()
# When conductor receives remote human reaction, apply() should not leave its local digest stale.
# Existing apply already sets digest after render; add a tiny immediate live publication request after preparing next bot reaction.
old="""   if(onlineLegacyCanExecuteBot())prepareCurrentBattleReaction();
 }"""
new="""   if(onlineLegacyCanExecuteBot()){
     prepareCurrentBattleReaction();
     onlineLegacyPushLiveBot();
   }
 }"""
assert old in s;s=s.replace(old,new,1);p.write_text(s)
