from pathlib import Path

p=Path('index.html')
s=p.read_text(encoding='utf-8')
old=""" // Toutes les cartes Oracle retournent dans le paquet, y compris l'Oracle actif.\n let pool=[...G.oracleDeck,...G.oracleDiscard];\n if(G.oracleActive!==null)pool.push(G.oracleActive);\n G.oracleActive=null;G.oracleDiscard=[];\n"""
new=""" // Divination remélange l'ensemble physique complet des cartes Oracle.\n // On reconstruit donc le paquet canonique depuis ORACLES plutôt que depuis les zones\n // courantes, qui peuvent provenir d'un ancien état Online incomplet/incompatible.\n let pool=ORACLES.map((_,i)=>i);\n G.oracleActive=null;G.oracleDiscard=[];\n"""
if old not in s:
    raise SystemExit('bloc Divination attendu introuvable')
s=s.replace(old,new,1)
p.write_text(s,encoding='utf-8')
