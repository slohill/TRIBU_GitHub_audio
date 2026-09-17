from pathlib import Path
p=Path('index.html')
s=p.read_text(encoding='utf-8')
old=""" if(!isSea(id)&&G.b[id].building&&G.b[id].building.type==='Portail'){
   const pi=document.createElement('img');pi.className='portalIcon'+((G.b[id].units||0)>0?' withUnits':'')+(isPvpBattle?' battleWithDice':'');pi.src='assets/images/tokens/portail.png';pi.title='Portail vers '+G.b[id].building.pair;b.appendChild(pi);
 }"""
new=""" const movementPreviewHere=dest===id&&selected()>0&&!isPvpPreview;
 if(!isSea(id)&&G.b[id].building&&G.b[id].building.type==='Portail'){
   const pi=document.createElement('img');pi.className='portalIcon'+(((G.b[id].units||0)>0||movementPreviewHere)?' withUnits':'')+(isPvpBattle?' battleWithDice':'');pi.src='assets/images/tokens/portail.png';pi.title='Portail vers '+G.b[id].building.pair;b.appendChild(pi);
 }"""
assert old in s, 'bloc Portail introuvable'
s=s.replace(old,new,1)
old2=""" if(dest===id&&selected()>0&&!isPvpPreview){const g=document.createElement('span');g.className='ghost';g.textContent=previewDestinationUnits(id);b.appendChild(g)}"""
new2=""" if(movementPreviewHere){const g=document.createElement('span');g.className='ghost';g.textContent=previewDestinationUnits(id);b.appendChild(g)}"""
assert old2 in s, 'bloc ghost introuvable'
s=s.replace(old2,new2,1)
old3="""   const hasUnits=st.children.length>0;
   const dr=document.createElement('img');
   dr.className='dragon'+(hasUnits?' withUnits':'')+(cellBuilding&&!hasUnits?' withBuildingOnly':'')+(cellBuilding&&hasUnits?' withUnitsAndBuilding':'')+(!hasUnits&&!cellBuilding&&!isSea(id)&&G.b[id].hostile?' withPnjOnly':'');dr.src='assets/images/tokens/dragon.png';dr.alt='Dragon';b.appendChild(dr)}"""
new3="""   // Le prévisionnel de déplacement occupe visuellement la place d'un vrai pion :
   // Dragon et objets déjà capables de se décaler avec des unités doivent donc se décaler aussi.
   const hasUnits=st.children.length>0||movementPreviewHere;
   const dr=document.createElement('img');
   dr.className='dragon'+(hasUnits?' withUnits':'')+(cellBuilding&&!hasUnits?' withBuildingOnly':'')+(cellBuilding&&hasUnits?' withUnitsAndBuilding':'')+(!hasUnits&&!cellBuilding&&!isSea(id)&&G.b[id].hostile?' withPnjOnly':'');dr.src='assets/images/tokens/dragon.png';dr.alt='Dragon';b.appendChild(dr)}"""
assert old3 in s, 'bloc Dragon introuvable'
s=s.replace(old3,new3,1)
p.write_text(s,encoding='utf-8')
