from pathlib import Path

p=Path('index.html')
s=p.read_text()
old=""" if(setupState){if(setupState.stage==='regions')setupRegionClick(id);return}\n if(divinationState)return;\n if(oracleNoticeState)return;\n if(oracleState&&oracleState.kind==='dragon5'){oracleDragon5Click(id);return}\n if(oracleState&&oracleState.kind==='sacrifice'){oracleSacrificeClick(id);return}\n"""
new=""" if(setupState){if(setupState.stage==='regions')setupRegionClick(id);return}\n // Une Divination peut déclencher un Oracle interactif. Dans ce cas, l'Oracle\n // doit recevoir les clics de carte AVANT le verrou général de Divination.\n if(oracleState&&oracleState.kind==='dragon5'){oracleDragon5Click(id);return}\n if(oracleState&&oracleState.kind==='sacrifice'){oracleSacrificeClick(id);return}\n if(divinationState)return;\n if(oracleNoticeState)return;\n"""
if old not in s:
    raise SystemExit('target block not found')
s=s.replace(old,new,1)
p.write_text(s)
