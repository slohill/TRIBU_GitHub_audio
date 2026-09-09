from pathlib import Path

# Patch ciblé : fermer l'état modal Caravane distant avant le render final.
p=Path('index.html')
s=p.read_text(encoding='utf-8')
old=""" onlineLegacyLastDigest=onlineLegacyDigest();render();
 if(caravanState)showCaravanChoice();
 else if(hadCaravan)closeAgentModal(true);
 onlineApplyPrivatePresentations(me);"""
new=""" onlineLegacyLastDigest=onlineLegacyDigest();
 if(!caravanState&&hadCaravan)closeAgentModal(true);
 render();
 if(caravanState)showCaravanChoice();
 onlineApplyPrivatePresentations(me);"""
if old not in s:
    raise SystemExit('Bloc onlineLegacyApply attendu introuvable')
s=s.replace(old,new,1)
p.write_text(s,encoding='utf-8')
