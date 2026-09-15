from pathlib import Path
p=Path('index.html')
s=p.read_text()
old="""function audioPrimeSfx(){
 if(audioSfxPrimed)return;
 audioSfxPrimed=true;
 // Sur tablette/iOS, lancer toutes les pistes même à volume 0 peut les rendre audibles.
 // On prépare donc seulement les objets Audio au premier geste utilisateur.
 ['gold','oracle','dragon','assassin','thief','fail','drums','horn','cardMove','construction','egnobombe','epicbattle'].forEach(name=>{
   audioSfxPool(name).forEach(a=>{try{a.load()}catch(e){}});
 });
 try{goldReactionAudio().load()}catch(e){}
}
"""
new="""function audioUnlockElement(a){
 if(!a)return;
 // Le geste utilisateur déverrouille réellement CET élément média pour les lectures
 // Online ultérieures (qui arrivent souvent depuis un snapshot, donc sans nouveau geste).
 // muted est utilisé plutôt que volume=0 afin que l'amorçage reste réellement silencieux
 // sur tablette/iOS.
 try{
   const wasMuted=a.muted;a.muted=true;
   const pr=a.play();
   if(pr&&pr.then)pr.then(()=>{a.pause();try{a.currentTime=0}catch(e){}a.muted=wasMuted}).catch(()=>{a.muted=wasMuted;try{a.load()}catch(e){}});
   else{a.pause();try{a.currentTime=0}catch(e){}a.muted=wasMuted}
 }catch(e){try{a.muted=false;a.load()}catch(_){}}
}
function audioPrimeSfx(){
 if(audioSfxPrimed)return;
 audioSfxPrimed=true;
 ['gold','oracle','dragon','assassin','thief','fail','drums','horn','cardMove','construction'].forEach(name=>{
   audioSfxPool(name).forEach(a=>{try{a.load()}catch(e){}});
 });
 // Ces trois sons peuvent être déclenchés sans geste local : fenêtre d'Or reçue
 // par snapshot, Egnobombe et bataille épique publiques. On déverrouille donc leur
 // premier lecteur pendant le premier geste réel du joueur.
 ['egnobombe','epicbattle'].forEach(name=>audioUnlockElement(audioSfxPool(name)[0]));
 audioUnlockElement(goldReactionAudio());
}
"""
if old not in s: raise SystemExit('audioPrimeSfx block not found exactly')
s=s.replace(old,new,1)
p.write_text(s)
