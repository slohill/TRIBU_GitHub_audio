from pathlib import Path
p=Path('index.html')
s=p.read_text()
s=s.replace("function die(owner,count,region=null){\n const d=document.createElement('span');d.className='die';", "function die(owner,count,region=null){\n const d=document.createElement('span');d.className='die';d.dataset.owner=owner;")
old="onlineLegalMoveSources(target).forEach(id=>{const sp=map.querySelector('.spot[data-region=\\\"'+id+'\\\"]');if(!sp)return;sp.classList.add('src','srcHold');const q=Number(onlineMoveDraft.picks[id]||0);if(q>0){const minus=document.createElement('button');minus.className='sourceMinus';minus.textContent='−';minus.title='Remettre 1 unité';minus.onpointerdown=e=>e.stopPropagation();minus.onclick=e=>{e.stopPropagation();onlineMoveAdjust(id,-1)};sp.appendChild(minus)}let timer=null,long=false;"
new="onlineLegalMoveSources(target).forEach(id=>{const sp=map.querySelector('.spot[data-region=\\\"'+id+'\\\"]');if(!sp)return;sp.classList.add('src','srcHold');const q=Number(onlineMoveDraft.picks[id]||0),remaining=Math.max(0,onlineOwnUnits(id)-q),ownDie=sp.querySelector('.die[data-owner=\\\"'+st.youIndex+'\\\"]');if(ownDie){ownDie.textContent=remaining;ownDie.title='Unités : '+remaining;ownDie.style.display=remaining>0?'':'none'}if(q>0){const minus=document.createElement('button');minus.className='sourceMinus';minus.textContent='−';minus.title='Remettre 1 unité';minus.onpointerdown=e=>e.stopPropagation();minus.onclick=e=>{e.stopPropagation();onlineMoveAdjust(id,-1)};sp.appendChild(minus)}let timer=null,long=false;"
if old not in s:
    raise SystemExit('online source render block not found')
s=s.replace(old,new,1)
p.write_text(s)
