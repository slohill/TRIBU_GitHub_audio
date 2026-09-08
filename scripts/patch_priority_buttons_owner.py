from pathlib import Path
p=Path('index.html');s=p.read_text()
old="""    if(!isBot(priority)){
      const pass=document.createElement('button');
      pass.id='battlePass';pass.textContent='Passer';pass.onclick=()=>{passPriority();if(G&&G.online&&G.online.legacySync)onlineLegacyPushNow()};buttons.appendChild(pass);
      if(!participant){const info=document.createElement('div');info.className='note';info.textContent='Vous pouvez intervenir depuis votre main ou passer immédiatement.';buttons.appendChild(info)}
    }else{"""
new="""    if(!isBot(priority)){
      const mayReact=!G.online||!G.online.legacySync||priority===localViewer();
      if(mayReact){
        const pass=document.createElement('button');
        pass.id='battlePass';pass.textContent='Passer';pass.onclick=()=>{passPriority();if(G&&G.online&&G.online.legacySync)onlineLegacyPushNow()};buttons.appendChild(pass);
        if(!participant){const info=document.createElement('div');info.className='note';info.textContent='Vous pouvez intervenir depuis votre main ou passer immédiatement.';buttons.appendChild(info)}
      }else{const info=document.createElement('div');info.className='note';info.textContent='En attente de la réaction de '+p(priority).name+'…';buttons.appendChild(info)}
    }else{"""
assert old in s;s=s.replace(old,new,1);p.write_text(s)
