from pathlib import Path
p=Path('index.html'); s=p.read_text(encoding='utf-8')
old="const target=onlineMoveDraft.target,t=map.querySelector('.spot[data-region=\"'+target+'\"]');if(t){t.classList.add('dest');const total=onlineMoveSelected();if(total){const g=document.createElement('span');g.className='ghost';g.textContent=total;t.appendChild(g)}}"
new="const target=onlineMoveDraft.target,t=map.querySelector('.spot[data-region=\"'+target+'\"]');if(t){t.classList.add('dest');const total=onlineMoveSelected();if(total){const g=document.createElement('span');g.className='ghost';g.textContent=onlineOwnUnits(target)+total;t.appendChild(g)}}"
assert old in s, 'movement preview block not found'
s=s.replace(old,new,1)
p.write_text(s,encoding='utf-8')
