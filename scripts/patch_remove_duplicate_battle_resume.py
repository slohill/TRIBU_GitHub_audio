from pathlib import Path
p=Path('index.html');s=p.read_text();old=""" if(battle)resumeBattleTimer();
 if(battle)resumeBattleTimer();""";assert old in s;s=s.replace(old," if(battle)resumeBattleTimer();",1);p.write_text(s)
