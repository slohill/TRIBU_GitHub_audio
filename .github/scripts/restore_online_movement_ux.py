from pathlib import Path
p=Path('index.html')
s=p.read_text()
s=s.replace("function onlineMoveSelected(){return Object.values(onlineMoveDraft.picks||{}).reduce((a,b)=>a+(Number(b)||0),0)}\nfunction onlineMoveClick(id){", "function onlineMoveSelected(){return Object.values(onlineMoveDraft.picks||{}).reduce((a,b)=>a+(Number(b)||0),0)}\nfunction onlineMoveAdjust(src,delta){const max=onlineMovePool(src),cur=Number(onlineMoveDraft.picks[src]||0),next=Math.max(0,Math.min(max,cur+delta));if(next)onlineMoveDraft.picks[src]=next;else delete onlineMoveDraft.picks[src];onlineRefreshPlayUi()}\nfunction onlineMoveAll(src){const max=onlineMovePool(src);if(max>0)onlineMoveDraft.picks[src]=max;onlineRefreshPlayUi()}\nfunction onlineMoveClick(id){")
s=s.replace("   const max=onlineMovePool(id),cur=Number(onlineMoveDraft.picks[id]||0);const next=cur>=max?0:cur+1;\n   if(next)onlineMoveDraft.picks[id]=next;else delete onlineMoveDraft.picks[id];onlineRefreshPlayUi();return;", "   onlineMoveAdjust(id,1);return;")
old="""   if(onlineMoveDraft.target){
     const t=map.querySelector('.spot[data-region="'+onlineMoveDraft.target+'"]');if(t)t.classList.add('dest');
     onlineLegalMoveSources(onlineMoveDraft.target).forEach(id=>{const sp=map.querySelector('.spot[data-region="'+id+'"]');if(!sp)return;sp.classList.add('src');const q=Number(onlineMoveDraft.picks[id]||0);if(q){const b=document.createElement('span');b.className='onlineMovePickBadge';b.textContent=q+' sélectionnée'+(q>1?'s':'');sp.appendChild(b)}});
     if(hint)hint.textContent='Cliquez sur une région source en jaune pour sélectionner les unités (clics successifs), puis validez.';
     if(srcBox)srcBox.innerHTML='<div class="note">Unités sélectionnées : <b>'+onlineMoveSelected()+'</b></div><div class="row"><button id="onlineMoveConfirm" '+(onlineMoveSelected()?'':'disabled')+'>Valider le déplacement</button><button id="onlineMoveCancel">Annuler</button></div>';
     const ok=$('onlineMoveConfirm'),no=$('onlineMoveCancel');if(ok)ok.onclick=onlineCommitMove;if(no)no.onclick=()=>{onlineResetMoveDraft();onlineRefreshPlayUi()};
   }else{if(hint)hint.textContent='Cliquez sur une destination en surbrillance verte.';if(srcBox)srcBox.innerHTML='<div class="note">Déplacements autoritaires : choisissez d’abord la destination sur la carte.</div>'}
"""
new="""   if(onlineMoveDraft.target){
     const t=map.querySelector('.spot[data-region="'+onlineMoveDraft.target+'"]');if(t){t.classList.add('dest');const total=onlineMoveSelected();if(total){const g=document.createElement('span');g.className='ghost';g.textContent=total;t.appendChild(g)}}
     const sources=onlineLegalMoveSources(onlineMoveDraft.target);
     sources.forEach(id=>{const sp=map.querySelector('.spot[data-region="'+id+'"]');if(!sp)return;sp.classList.add('src','srcHold');const q=Number(onlineMoveDraft.picks[id]||0);if(q){const minus=document.createElement('button');minus.className='sourceMinus';minus.textContent='−';minus.title='Remettre 1 unité';minus.onpointerdown=e=>e.stopPropagation();minus.onclick=e=>{e.stopPropagation();onlineMoveAdjust(id,-1)};sp.appendChild(minus);const b=document.createElement('span');b.className='onlineMovePickBadge';b.textContent=q+' sélectionnée'+(q>1?'s':'');sp.appendChild(b)}});
     if(hint)hint.innerHTML='Destination choisie — cliquez sur les <b>sources jaunes</b>, ou utilisez les boutons ci-dessous.';
     if(srcBox){srcBox.innerHTML='';sources.forEach(id=>{const q=Number(onlineMoveDraft.picks[id]||0),max=onlineMovePool(id),d=document.createElement('div');d.className='source';d.innerHTML='<button title="Clic : +1">'+id+'</button><button>−</button><span>'+q+'/'+max+'</span><button>+</button><button>Tout</button>';const bs=d.querySelectorAll('button');bs[0].onclick=()=>onlineMoveAdjust(id,1);bs[1].onclick=()=>onlineMoveAdjust(id,-1);bs[2].onclick=()=>onlineMoveAdjust(id,1);bs[3].onclick=()=>onlineMoveAll(id);srcBox.appendChild(d)});const actions=document.createElement('div');actions.className='row';actions.innerHTML='<button id="onlineMoveConfirm" '+(onlineMoveSelected()?'':'disabled')+'>Valider le déplacement</button><button id="onlineMoveCancel">Annuler</button>';srcBox.appendChild(actions)}
     const ok=$('onlineMoveConfirm'),no=$('onlineMoveCancel');if(ok)ok.onclick=onlineCommitMove;if(no)no.onclick=()=>{onlineResetMoveDraft();onlineRefreshPlayUi()};
   }else{if(hint)hint.textContent='Cliquez sur la destination.';if(srcBox)srcBox.innerHTML=''}
"""
if old not in s: raise SystemExit('movement block not found')
s=s.replace(old,new)
p.write_text(s)
