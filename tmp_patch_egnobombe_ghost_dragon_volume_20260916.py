from pathlib import Path

p=Path('index.html')
s=p.read_text(encoding='utf-8')

needle="""function egnoEligibleRegions(i){
 return Object.keys(POS).filter(r=>units(r,i)>=5);
}
"""
insert="""function egnoEligibleRegions(i){
 return Object.keys(POS).filter(r=>units(r,i)>=5);
}
function invalidateMovementOnDestroyedCase(r){
 // Egnobombe détruit les unités physiques : leurs anciens points de déplacement
 // ne doivent jamais rester dans movable (sinon unités fantômes déplaçables).
 movable[r]=[];
 if(picks&&Object.prototype.hasOwnProperty.call(picks,r))delete picks[r];
 if(dest===r){dest=null;picks={}}
}
"""
assert s.count(needle)==1, 'point insertion Egnobombe inattendu'
s=s.replace(needle,insert,1)

old=""" if(isSea(r)){
   Object.keys(G.sea[r].fleets).forEach(k=>G.sea[r].fleets[k]=0);
 }else{
   const c=G.b[r];
   c.units=0;c.owner=null;
   const neutralized=neutralizeSurvivingDefensiveBuilding(r);
   c.hostile=neutralized?false:c.originalHostile;
 }
"""
new=""" if(isSea(r)){
   Object.keys(G.sea[r].fleets).forEach(k=>G.sea[r].fleets[k]=0);
 }else{
   const c=G.b[r];
   c.units=0;c.owner=null;
   const neutralized=neutralizeSurvivingDefensiveBuilding(r);
   c.hostile=neutralized?false:c.originalHostile;
 }
 invalidateMovementOnDestroyedCase(r);
"""
assert s.count(old)==1, 'destruction case centrale Egnobombe inattendue'
s=s.replace(old,new,1)

old_land="""   if(c.units>0){
     c.units=0;c.owner=null;
     const neutralized=neutralizeSurvivingDefensiveBuilding(x);
     c.hostile=neutralized?false:c.originalHostile;
   }
"""
new_land="""   if(c.units>0){
     c.units=0;c.owner=null;
     const neutralized=neutralizeSurvivingDefensiveBuilding(x);
     c.hostile=neutralized?false:c.originalHostile;
   }
   invalidateMovementOnDestroyedCase(x);
"""
assert s.count(old_land)>=1, 'destruction terrestre adjacente introuvable'
# Limité au premier bloc correspondant, qui est celui de resolveEgnobombe dans cette zone.
pos=s.index('function resolveEgnobombe(r)')
idx=s.index(old_land,pos)
s=s[:idx]+s[idx:].replace(old_land,new_land,1)

old_sea=""" seas.forEach(x=>{
   Object.keys(G.sea[x].fleets).forEach(k=>G.sea[x].fleets[k]=0);
 });
"""
new_sea=""" seas.forEach(x=>{
   Object.keys(G.sea[x].fleets).forEach(k=>G.sea[x].fleets[k]=0);
   invalidateMovementOnDestroyedCase(x);
 });
"""
assert s.count(old_sea)==1, 'destruction maritime adjacente Egnobombe inattendue'
s=s.replace(old_sea,new_sea,1)

# -25 % par rapport au volume Dragon actuel 0.9 => 0.675.
count=s.count("audioPlaySfx('dragon',.9)")
assert count==2, f'nombre appels Dragon inattendu: {count}'
s=s.replace("audioPlaySfx('dragon',.9)","audioPlaySfx('dragon',.675)")

p.write_text(s,encoding='utf-8')
