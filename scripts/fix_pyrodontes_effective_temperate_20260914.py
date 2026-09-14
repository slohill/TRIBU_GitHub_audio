from pathlib import Path
p=Path('index.html')
s=p.read_text(encoding='utf-8')
repls={
"if(R[battle.target][1]!=='t'||currentTerrain(battle.target)!=='t') return {ok:false,reason:'La région doit être naturellement tempérée et être actuellement tempérée.'};":"if(currentTerrain(battle.target)!=='t') return {ok:false,reason:'La région doit être actuellement tempérée.'};",
"return side==='attacker' && battle.kind==='land' && R[battle.target][1]==='t' && currentTerrain(battle.target)==='t' ? 5 : 0;":"return side==='attacker' && battle.kind==='land' && currentTerrain(battle.target)==='t' ? 5 : 0;",
"if(c.name==='Pyrodontes de guerre' && !isSea(target) && R[target][1]==='t' && currentTerrain(target)==='t')best=Math.max(best,5);":"if(c.name==='Pyrodontes de guerre' && !isSea(target) && currentTerrain(target)==='t')best=Math.max(best,5);"
}
for old,new in repls.items():
    if s.count(old)!=1: raise SystemExit(f'expected exactly one match: {old}')
    s=s.replace(old,new)
p.write_text(s,encoding='utf-8')
