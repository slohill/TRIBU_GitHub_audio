from pathlib import Path

p = Path('index.html')
s = p.read_text(encoding='utf-8')
old1 = """ if(!queues.length){
   log(name+' : aucune région éligible à sacrifier.');
   checkDecimations();
   render();
   completeOracleResolution();
   return;
 }"""
new1 = """ if(!queues.length){
   log(name+' : aucune région éligible à sacrifier.');
   checkDecimations();
   finishOracleResolution();
   render();
   completeOracleResolution();
   return;
 }"""
old2 = """ if(oracleState&&oracleState.index>=oracleState.queues.length){
   oracleState=null;
   checkDecimations();
   render();
   completeOracleResolution();
 }"""
new2 = """ if(oracleState&&oracleState.index>=oracleState.queues.length){
   oracleState=null;
   checkDecimations();
   finishOracleResolution();
   render();
   completeOracleResolution();
 }"""
for old, new in ((old1,new1),(old2,new2)):
    if s.count(old) != 1:
        raise SystemExit(f'Bloc attendu introuvable ou non unique: {s.count(old)}')
    s = s.replace(old,new,1)
p.write_text(s,encoding='utf-8')
