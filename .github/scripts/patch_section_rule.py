from pathlib import Path

p = Path('index.html')
s = p.read_text(encoding='utf-8')
old = """function shadowTargetLegal(r){
 if(!shadowState||shadowState.stage!=='target'||isSea(r))return false;
 const s=shadowState,c=G.b[r];
 if(s.parentBattle&&s.parentBattle.kind==='land'&&s.parentBattle.target===r){
   // Défendre sa région attaquée OU renforcer sa propre attaque.
   return s.parentBattle.defender===s.player||s.parentBattle.attacker===s.player;
 }
 if(c.owner===s.player)return false;
 return true;
}"""
new = """function shadowTargetLegal(r){
 if(!shadowState||shadowState.stage!=='target'||isSea(r))return false;
 const s=shadowState,c=G.b[r];
 // Une région actuellement en bataille ne peut jamais être ciblée par Section de l'ombre.
 // En revanche, n'importe quel joueur peut lancer sa Section ailleurs pendant la bataille.
 if(s.parentBattle&&s.parentBattle.target===r)return false;
 if(c.owner===s.player)return false;
 return true;
}"""
if old not in s:
    raise SystemExit('shadowTargetLegal anchor missing')
s = s.replace(old, new, 1)
p.write_text(s, encoding='utf-8')
