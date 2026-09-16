from pathlib import Path
p=Path('index.html'); s=p.read_text(encoding='utf-8')
repls={
"Tempêtes de sables activée":"Tempête de sable activée",
"si le résultat est impaire les unités sont détruites":"si le résultat est impair, les unités sont détruites",
"par delà les forêts":"par-delà les forêts",
"Tant que En quête de destruction est active":"Tant qu’En quête de destruction est active",
"cela active aussi le dragon":"cela active aussi le Dragon",
"Déplacez le dragon de 5 cases différentes":"Déplacez le Dragon de 5 cases différentes"
}
for old,new in repls.items():
 assert old in s,old
 s=s.replace(old,new)
p.write_text(s,encoding='utf-8')
