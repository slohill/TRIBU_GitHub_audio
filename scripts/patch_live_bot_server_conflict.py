from pathlib import Path
p=Path('index.html');s=p.read_text()
old="""   if(!(G&&G.players[G.active]&&G.players[G.active].bot)){
     if(err&&err.current)onlineLegacyApply(err.current);else onlineError(err);
   }else if(!(err&&err.current))onlineError(err);"""
new="""   if(!(G&&G.players[G.active]&&G.players[G.active].bot)){
     if(err&&err.current)onlineLegacyApply(err.current);else onlineError(err);
   }else if(err&&err.current){
     // Conflit de révision pendant la chaîne bot : garder le moteur local,
     // mais reprendre la révision serveur afin que le prochain snapshot live
     // puisse être accepté sans interrompre le tour.
     if(Number.isInteger(err.current.revision)){
       onlineLegacyRevision=err.current.revision;
       if(G.online)G.online.revision=err.current.revision;
     }
     onlineLegacyLastDigest='';onlineLegacyBotCommitQueued=true;
   }else onlineError(err);"""
assert old in s;s=s.replace(old,new,1)
p.write_text(s)
