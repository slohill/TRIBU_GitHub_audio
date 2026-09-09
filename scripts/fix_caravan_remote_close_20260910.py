from pathlib import Path

p=Path('index.html')
s=p.read_text(encoding='utf-8')
old1="""function onlineLegacyApply(packet){
 if(!packet||!packet.snapshot)return;
 if(!G||!G.online||!G.online.legacySync)return;
 const me=packet.youIndex;
 onlineLegacyApplying=true;
"""
new1="""function onlineLegacyApply(packet){
 if(!packet||!packet.snapshot)return;
 if(!G||!G.online||!G.online.legacySync)return;
 const me=packet.youIndex;
 const hadCaravan=!!caravanState;
 onlineLegacyApplying=true;
"""
old2=""" onlineLegacyLastDigest=onlineLegacyDigest();render();
 if(caravanState)showCaravanChoice();
 onlineApplyPrivatePresentations(me);
"""
new2=""" onlineLegacyLastDigest=onlineLegacyDigest();render();
 if(caravanState)showCaravanChoice();
 else if(hadCaravan)closeAgentModal(true);
 onlineApplyPrivatePresentations(me);
"""
for old,new in ((old1,new1),(old2,new2)):
    if old not in s:
        raise SystemExit('Expected block not found; main changed or code shape differs')
    if s.count(old)!=1:
        raise SystemExit('Expected block is not unique')
    s=s.replace(old,new,1)
p.write_text(s,encoding='utf-8')
