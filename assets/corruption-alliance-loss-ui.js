/* Mandatory alliance loss view. The controller owns pauses, synchronization and commit. */
(function(root){
'use strict';
function mount({map,panel,plan,viewer,playerName,dieImage,onChoose,onReset,onConfirm,mode='alliance',actor=null}){
 const golem=mode==='golem',revolt=golem||mode==='revolts',mine=viewer===(revolt?actor:plan.player);
 const color=golem?'#111111':revolt?'#ef4444':'#22c55e';
 const total=revolt?Object.values(plan.chosen).reduce((a,b)=>a+b,0):0;
 const layer=document.createElement('div');layer.className='allianceLossLayer';
 layer.style.cssText='position:absolute;inset:0;pointer-events:none;z-index:25';
 const box=document.createElement('section');box.className='allianceLossPanel';
 const heading=document.createElement('h3');heading.textContent=golem?'Violence aveugle — dé '+plan.roll:revolt?'Révolte !':plan.kind==='ogre'?'Ogres — pertes adjacentes':'Perte de votre alliance';box.appendChild(heading);
 const message=document.createElement('p');message.textContent=mine&&golem?'Choisissez une Région puis les unités à supprimer. Le nombre requis est indiqué pour chaque Région.':mine&&revolt?'Choisissez une ou deux unités d’une même Région. Cliquez sur OK pour confirmer, ou changez votre choix.':mine?'Choisissez les unités à retirer. Les pertes ne seront appliquées qu’après OK.':'En attente de '+playerName+' pour le choix des unités à retirer.';box.appendChild(message);
 const ns='http://www.w3.org/2000/svg',svg=document.createElementNS(ns,'svg');
 svg.style.cssText='position:absolute;inset:0;width:100%;height:100%;overflow:visible;pointer-events:none;z-index:19';
 const endpoints=[],placed=new Map();
 function button(text,action){const b=document.createElement('button');b.type='button';b.textContent=text;b.onclick=e=>{e.stopPropagation();action()};return b}
 for(const row of plan.regions){
  const choices=revolt?(plan.origin===row.region?plan.chosen:{}):row.chosen;
  const selected=Object.values(choices).reduce((a,b)=>a+b,0);
  const label=document.createElement('p');label.textContent=row.region+' : '+selected+' / '+(golem?row.required:revolt?2:row.required)+' unité(s) choisie(s)';box.appendChild(label);
  for(const group of row.groups){
   const target=group.kind==='attacking'?group.target:row.region;
   const anchor=Array.from(map.querySelectorAll('[data-region]')).find(e=>e.dataset.region===target);if(!anchor)continue;
   const chosen=choices[group.key]||0;
   const chip=button((group.available-chosen)+'',()=>onChoose(row.region,group.key));
   chip.dataset.lossRegion=row.region;chip.dataset.lossGroup=group.key;
   chip.setAttribute('aria-label',row.region+' — '+(group.kind==='attacking'?'attaquants en '+target:'unités sur place')+' — '+chosen+' sur '+group.available+' sélectionnées');
   chip.title=chip.getAttribute('aria-label');
   chip.disabled=!mine||plan.confirmed||chosen>=group.available||(revolt?(total>=(golem?row.required:2)||(plan.origin!==null&&plan.origin!==row.region)):(row.automatic||selected>=row.required));
   chip.style.cssText='position:absolute;width:42px;height:42px;border:3px solid #22c55e;border-radius:10px;color:white;background-color:#17251b;font-weight:bold;text-shadow:0 1px 3px black;pointer-events:auto;transform:translate(-50%,-50%);opacity:1';
   chip.style.borderColor=color;
   if(revolt)chip.style.boxShadow='0 0 12px '+color;
   const groupImage=typeof dieImage==='function'?dieImage(group):dieImage;
   if(groupImage){chip.style.backgroundImage='url("'+groupImage+'")';chip.style.backgroundSize='contain'}
   const key=target,offset=placed.get(key)||0;placed.set(key,offset+1);
   layer.appendChild(chip);endpoints.push({row,group,anchor,chip,offset});
  }
 }
 if(mine){
  const reset=button('Changer mon choix',onReset);reset.dataset.lossReset='';box.appendChild(reset);
  const confirm=button('OK',onConfirm);confirm.dataset.lossConfirm='';confirm.disabled=golem?!root.TribuGolem.commands(plan):revolt?!root.TribuRevolts.commands(plan):!root.TribuAlliances.ready(plan);box.appendChild(confirm);
 }
 map.appendChild(svg);map.appendChild(layer);panel.appendChild(box);
 function layout(){
  const rect=map.getBoundingClientRect();svg.replaceChildren();svg.setAttribute('viewBox','0 0 '+rect.width+' '+rect.height);
  for(const e of endpoints){
   const target=e.anchor.getBoundingClientRect();
   const x=target.x+target.width/2-rect.x+e.offset*46,y=target.y+target.height/2-rect.y;
   e.chip.style.left=x+'px';e.chip.style.top=y+'px';
   if(e.group.kind!=='attacking')continue;
   const origin=Array.from(map.querySelectorAll('[data-region]')).find(a=>a.dataset.region===e.row.region);if(!origin)continue;
   const a=origin.getBoundingClientRect(),sx=a.x+a.width/2-rect.x,sy=a.y+a.height/2-rect.y;
   const line=document.createElementNS(ns,'line');
   line.setAttribute('x1',sx);line.setAttribute('y1',sy);line.setAttribute('x2',x);line.setAttribute('y2',y);
   line.setAttribute('stroke',color);line.setAttribute('stroke-width','3');line.setAttribute('stroke-linecap','round');svg.appendChild(line);
  }
 }
 layout();const observer=typeof ResizeObserver==='function'?new ResizeObserver(layout):null;observer?.observe(map);
 return {destroy(){observer?.disconnect();layer.remove();svg.remove();box.remove()},layout};
}
root.TribuAllianceLossUI=Object.freeze({mount});
})(globalThis);
