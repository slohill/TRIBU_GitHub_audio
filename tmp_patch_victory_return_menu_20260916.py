from pathlib import Path
p=Path('index.html')
s=p.read_text(encoding='utf-8')
old='<button id="victoryRestart">Recommencer</button>'
new='<button id="victoryRestart">Retour au menu principal</button>'
assert old in s
s=s.replace(old,new,1)
old2="$ ('victoryRestart')" # guard against accidental typo pattern
assert old2 not in s
old3="$('victoryRestart').onclick=init;"
new3="$('victoryRestart').onclick=()=>{location.reload()};"
assert old3 in s
s=s.replace(old3,new3,1)
p.write_text(s,encoding='utf-8')
