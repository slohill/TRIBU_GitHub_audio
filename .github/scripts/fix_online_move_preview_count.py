from pathlib import Path
p=Path('index.html')
s=p.read_text()
old_die="function die(owner,count,region=null){\n const d=document.createElement('span');d.className='die';"
new_die="function die(owner,count,region=null){\n const d=document.createElement('span');d.className='die';d.dataset.owner=owner;"
if old_die not in s:
    raise SystemExit('die marker not found')
s=s.replace(old_die,new_die,1)
old="sp.classList.add('src','srcHold');const q=Number(onlineMoveDraft.picks[id]||0);if(q>0){"
new="sp.classList.add('src','srcHold');const q=Number(onlineMoveDraft.picks[id]||0),remaining=Math.max(0,onlineOwnUnits(id)-q),ownDie=sp.querySelector('.die[data-owner=\"'+st.youIndex+'\"]');if(ownDie){ownDie.textContent=remaining;ownDie.title='Unités : '+remaining;ownDie.style.display=remaining>0?'':'none'}if(q>0){"
if old not in s:
    raise SystemExit('online source render marker not found')
s=s.replace(old,new,1)
p.write_text(s)
