from pathlib import Path
p=Path('index.html');s=p.read_text()
old="""   }else if(!(err&&err.current))onlineError(err);
 }).finally(()=>{"""
new="""   }else if(err&&err.current){
     if(Number.isInteger(err.current.revision)){
       onlineLegacyRevision=err.current.revision;
       if(G.online)G.online.revision=err.current.revision;
     }
     onlineLegacyLastDigest='';onlineLegacyBotCommitQueued=true;
   }else onlineError(err);
 }).finally(()=>{"""
pos=s.index('function onlineLegacyPushLiveBot()');idx=s.index(old,pos);s=s[:idx]+s[idx:].replace(old,new,1);p.write_text(s)
