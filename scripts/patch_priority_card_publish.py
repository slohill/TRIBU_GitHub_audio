from pathlib import Path
p=Path('index.html');s=p.read_text()
# Commit immediately after a reaction card has fully advanced priority.
old="""  advancePriority(true);render();prepareCurrentBattleReaction();
}"""
new="""  advancePriority(true);render();prepareCurrentBattleReaction();
  if(G&&G.online&&G.online.legacySync)onlineLegacyPushNow();
}"""
# This exact tail is playReaction's normal completion.
assert old in s;s=s.replace(old,new,1)
p.write_text(s)
