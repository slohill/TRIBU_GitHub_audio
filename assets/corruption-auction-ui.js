/* Local auction UI; online entry stays gated until server-authoritative actions are ready. */
function morcattAuctionActive(){return !!G?.morcattAuction&&G.morcattAuction.stage!=='finished'}
function startMorcattAuction(seller,gain){
 if(morcattAuctionActive())return;
 const cards=[];for(let i=0;i<G.players.length;i++){const id=drawOneToPool();if(id===null||id===undefined)break;cards.push(id)}
 G.morcattAuction=TribuAuction.create(seller,cards,gain);G.phase='auction';render();
 if(!G.online&&p(seller).bot){cards.forEach((id,i)=>TribuAuction.price(G.morcattAuction,seller,i,TribuAuction.botPrice(id,CARDS)));TribuAuction.start(G.morcattAuction,seller,G.players,G.discard);morcattAuctionChanged()}
}
function morcattAuctionChanged(){
 const s=G.morcattAuction;
 if(s?.stage==='finished'&&!s.gainOffered){
  s.gainOffered=true;const gain=TribuAuction.total(s);
  log(p(s.seller).name+' termine ses enchères : '+s.receipts+' Or de ventes, '+s.unsold+' invendue(s).');
  G.phase='start';offerGoldGain(s.seller,gain,'Récolte Morcatt','beginPlay');return;
 }
 render();
}
function morcattAuctionAction(kind,value,index){
 const s=G?.morcattAuction;if(!s)return;
 if(G.online){
  onlineAck('morcattAuctionAction',{kind,amount:value,index,revision:s.revision}).then(result=>{if(result.current)onlineLegacyApply(result.current)}).catch(error=>{if(error.current)onlineLegacyApply(error.current);else onlineError(error)});
  return;
 }
 const actor=localViewer();let changed=false;
 if(kind==='price')changed=TribuAuction.price(s,actor,index,value);
 if(kind==='start')changed=TribuAuction.start(s,actor,G.players,G.discard);
 if(kind==='bid')changed=TribuAuction.bid(s,actor,value,G.players,G.discard,s.revision);
 if(kind==='pass')changed=TribuAuction.pass(s,actor,G.players,G.discard,s.revision);
 if(changed)morcattAuctionChanged();
}
function renderMorcattAuction(){
 document.getElementById('morcattAuctionPanel')?.remove();document.getElementById('morcattAuctionNotice')?.remove();
 const pending=G?.morcattAuction;
 if(pending?.stage==='finished'&&!pending.gainOffered&&(!G.online||G.online.myPlayerIndex===pending.seller||p(pending.seller).bot&&onlineLegacyCanExecuteBot())){
  setTimeout(()=>{if(G?.morcattAuction===pending&&!pending.gainOffered)morcattAuctionChanged()},0);
 }
 if(!morcattAuctionActive())return;
 const s=G.morcattAuction,root=$('commerceBoard');if(!root)return;
 const notice=document.createElement('button');notice.id='morcattAuctionNotice';
 notice.textContent='Enchères Morcatt en cours : Faites un tour dans Commerce ↓';
 notice.style.cssText='position:absolute;top:4px;left:10%;width:80%;z-index:95';
 notice.onclick=()=>root.scrollIntoView({behavior:'smooth',block:'center'});$('map').appendChild(notice);
 const panel=document.createElement('section');panel.id='morcattAuctionPanel';panel.className='commerceBoardRow';
 const title=document.createElement('h3');title.textContent='Enchères — '+p(s.seller).name;panel.appendChild(title);
 const list=document.createElement('div');list.style.cssText='display:flex;gap:10px;flex-wrap:wrap';panel.appendChild(list);
 s.cards.forEach((id,i)=>{
  const card=CARDS[id],box=document.createElement('div');box.style.cssText='padding:8px;border:1px solid #888;max-width:160px';
  const zoom=document.createElement('button');zoom.textContent=(i+1)+'. '+card.name+' ⌕';
  const art=OFFICIAL_CARD_ART[card.name];if(art){const img=document.createElement('img');img.src=art;img.alt=card.name;img.style.cssText='display:block;width:80px';zoom.prepend(img)}
  zoom.onclick=()=>openOfficialCard(card.name,card.type,card.effect);box.appendChild(zoom);
  if(s.stage==='prepare'&&localViewer()===s.seller){
   const input=document.createElement('input');input.type='number';input.min='1';input.step='1';input.value=s.prices[i];input.setAttribute('aria-label','Mise de départ carte '+(i+1));input.style.width='75px';
   input.onchange=()=>morcattAuctionAction('price',Number(input.value),i);box.appendChild(input);
  }else{const price=document.createElement('div');price.textContent='Départ : '+s.prices[i]+' Or';box.appendChild(price)}
  if(i<s.results.length){const result=s.results[i],done=document.createElement('div');done.textContent=result.buyer===null?'Invendue':p(result.buyer).name+' : '+result.amount+' Or';box.appendChild(done)}
  if(s.stage==='bidding'&&i===s.round)box.style.borderColor='#ffd92f';
  list.appendChild(box);
 });
 const add=(text,action)=>{const b=document.createElement('button');b.textContent=text;b.onclick=action;panel.appendChild(b);return b};
 if(s.stage==='prepare'){if(localViewer()===s.seller)add('Lancer les enchères',()=>morcattAuctionAction('start'))}
 else{
  const status=document.createElement('p');status.textContent='Carte '+(s.round+1)+' — '+(s.bid?p(s.bid.player).name+' propose '+s.bid.amount+' Or':'Aucune offre');panel.appendChild(status);
  const timer=document.createElement('strong');timer.id='morcattAuctionTimer';panel.appendChild(timer);
  if(TribuAuction.eligible(s,G.players).includes(localViewer())){
   const amount=document.createElement('input');amount.type='number';amount.min=String(TribuAuction.minimum(s));amount.max=String(p(localViewer()).gold);amount.value=amount.min;amount.setAttribute('aria-label','Votre enchère');panel.appendChild(amount);
   add('Surenchérir',()=>morcattAuctionAction('bid',Number(amount.value)));
   const pass=add('Passer',()=>morcattAuctionAction('pass'));pass.disabled=s.passed.includes(localViewer());
  }
 }
 root.appendChild(panel);updateMorcattAuctionTimer();
}
function updateMorcattAuctionTimer(){const timer=$('morcattAuctionTimer'),s=G?.morcattAuction;if(timer&&s?.deadline)timer.textContent=Math.max(0,Math.ceil((s.deadline-Date.now())/1000))+' s'}
const morcattBaseRenderCommerceBoard=renderCommerceBoard;
renderCommerceBoard=function(){morcattBaseRenderCommerceBoard();renderMorcattAuction()};
setInterval(()=>{
 if(!morcattAuctionActive())return;
 updateMorcattAuctionTimer();
 if(G.online)return;
 const s=G.morcattAuction;
 if(s.stage!=='bidding')return;
 if(TribuAuction.tick(s,G.players,G.discard)){morcattAuctionChanged();return}
 for(let i=0;i<G.players.length;i++){
  if(!p(i).bot)continue;const action=TribuAuction.botAction(s,i,G.players,CARDS);if(!action)continue;
  const changed=action.kind==='bid'?TribuAuction.bid(s,i,action.amount,G.players,G.discard,s.revision):TribuAuction.pass(s,i,G.players,G.discard,s.revision);
  if(changed){morcattAuctionChanged();break}
 }
 updateMorcattAuctionTimer();
},500);
