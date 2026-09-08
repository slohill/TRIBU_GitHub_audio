from pathlib import Path
p=Path('index.html');s=p.read_text()
old="""    advancePriority(true);
    renderBattle();render();
    prepareCurrentBattleReaction();
  }
}"""
new="""    advancePriority(true);
    renderBattle();render();
    prepareCurrentBattleReaction();
    if(G&&G.online&&G.online.legacySync)onlineLegacyPushNow();
  }
}"""
assert old in s;s=s.replace(old,new,1);p.write_text(s)
