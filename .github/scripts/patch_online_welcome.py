from pathlib import Path

p=Path('index.html')
s=p.read_text(encoding='utf-8')

style_anchor=""".audioControls{display:flex;gap:5px;align-items:center;margin-left:auto}.audioControls button{padding:5px 8px;font-size:11px;white-space:nowrap}.audioControls button.off{opacity:.55;filter:grayscale(1)}
@media(max-width:760px){header{flex-wrap:wrap}.audioControls{margin-left:0}.audioControls button{font-size:10px;padding:4px 6px}}
"""
style_new=style_anchor+"""
/* TRIBU Online beta — accueil et salons (étape 1, sans serveur réseau) */
#start{background:radial-gradient(circle at 50% 20%,#24392f 0,#101713 56%,#080c0a 100%);min-height:100vh;padding:22px;box-sizing:border-box;display:flex;align-items:center;justify-content:center}
#start.hidden{display:none}
.onlineStartBox{width:min(720px,96vw);background:#111a16f2;border:2px solid #64746c;border-radius:18px;padding:22px;box-shadow:0 18px 55px #000b;color:#eef4f0}
.onlineBrand{text-align:center;margin-bottom:18px}.onlineBrand h1{margin:0;font-size:clamp(30px,6vw,52px);letter-spacing:1px}.onlineBeta{display:inline-block;margin-top:5px;padding:3px 9px;border:1px solid #d8bd63;border-radius:999px;color:#f1d77c;font-size:11px;font-weight:900;text-transform:uppercase;letter-spacing:.08em}
.onlineScreen.hidden{display:none}.onlineLead{text-align:center;opacity:.82;margin:0 0 14px}.onlineField{display:flex;flex-direction:column;gap:5px;margin:10px 0}.onlineField label{font-size:12px;font-weight:900}.onlineField input,.onlineField select{width:100%;box-sizing:border-box;padding:10px 11px;border-radius:8px;border:1px solid #56645e;background:#1b2521;color:#fff;font-size:14px}
.onlineActions{display:grid;grid-template-columns:1fr 1fr;gap:10px;margin-top:14px}.onlineActions button,.onlineModeGrid button,.onlineBack,.onlinePrimary{padding:11px 12px;border-radius:9px;font-weight:900}.onlinePrimary{border:2px solid #d8bd63;background:#332f18;color:#fff}.onlineSecondary{border:1px solid #607169;background:#202b26;color:#fff}.onlineModeGrid{display:grid;grid-template-columns:1fr 1fr;gap:9px;margin-top:12px}.onlineModeGrid button{background:#1e2924;border:1px solid #5b6d64;color:#fff;text-align:left}.onlineModeGrid button b{display:block;font-size:14px}.onlineModeGrid button small{display:block;margin-top:3px;opacity:.72;font-size:10px}.onlineSectionTitle{font-size:14px;font-weight:900;margin:15px 0 6px;color:#e7cf77}.onlineBack{margin-top:14px;background:#1a211e;border:1px solid #4d5a54;color:#ddd}.localTestBtn{display:block;margin:18px auto 0;background:transparent!important;border:1px dashed #59645f!important;color:#9da8a2!important;font-size:10px!important;padding:6px 10px!important;width:auto!important}.onlineLobby{border:1px solid #59675f;border-radius:11px;background:#19221e;padding:12px;margin-top:12px}.onlineLobbyHead{display:flex;justify-content:space-between;gap:8px;align-items:center}.onlineCode{font-family:monospace;font-size:16px;font-weight:900;letter-spacing:.12em;color:#f0d271}.onlinePlayerRow{display:flex;align-items:center;justify-content:space-between;padding:8px 0;border-top:1px solid #334039;font-size:12px}.onlinePlayerRow:first-of-type{margin-top:8px}.readyBadge{padding:3px 7px;border-radius:999px;background:#254b32;color:#bdf0c9;font-size:10px;font-weight:900}.waitingBadge{padding:3px 7px;border-radius:999px;background:#353b38;color:#b8c0bc;font-size:10px}.onlineNotice{font-size:11px;line-height:1.4;padding:9px;border-radius:8px;background:#2b2b1d;border:1px solid #665f32;margin-top:10px;color:#e8dda8}.onlineReadyRow{display:flex;gap:8px;margin-top:10px}.onlineReadyRow button{flex:1}.onlineStatus{text-align:center;font-size:11px;opacity:.75;margin-top:8px}
@media(max-width:620px){.onlineActions,.onlineModeGrid{grid-template-columns:1fr}.onlineStartBox{padding:16px}}
"""
if style_anchor not in s: raise SystemExit('style anchor missing')
s=s.replace(style_anchor,style_new,1)

old_start="""<section id=\"start\"><div class=\"startbox\"><h1>TRIBU</h1><p>Prototype technique — map calibrée, unités, cartes et tours.</p><div class=\"row\" style=\"justify-content:center;margin-top:12px\">
<label>Nombre de joueurs :
<select id=\"gameMode\">
<option value=\"1v3\">1 joueur vs 3 bots</option>
<option value=\"1v4\">1 joueur vs 4 bots</option>
<option value=\"2v3\">2 joueurs vs 3 bots — même support</option>
<option value=\"3h\">3 joueurs — en ligne</option>
<option value=\"4h\">4 joueurs — en ligne</option>
<option value=\"5h\">5 joueurs — en ligne</option>
</select></label>
<label>Mode de partie :
<select id=\"victoryMode\">
<option value=\"3\">Facile (3 points)</option>
<option value=\"4\">Initié (4 points)</option>
<option value=\"5\">Expert (5 points)</option>
</select></label></div>
<button id=\"startBtn\">DÉMARRER LA PARTIE</button></div></section>"""
new_start="""<section id=\"start\"><div class=\"onlineStartBox\">
  <div class=\"onlineBrand\"><h1>Tribu Le Jeu Online</h1><span class=\"onlineBeta\">version bêta</span></div>

  <div id=\"onlineHome\" class=\"onlineScreen\">
    <p class=\"onlineLead\">Préparez votre tribu et rejoignez la partie.</p>
    <div class=\"onlineField\"><label for=\"onlinePseudo\">Pseudo</label><input id=\"onlinePseudo\" maxlength=\"24\" placeholder=\"Laissez vide pour un nom aléatoire\"></div>
    <div class=\"onlineActions\"><button id=\"onlineCreate\" class=\"onlinePrimary\">Créer une partie</button><button id=\"onlineJoin\" class=\"onlineSecondary\">Rejoindre une partie</button></div>
    <button id=\"localTestBtn\" class=\"localTestBtn\">Mode test local — 2 joueurs vs 3 bots</button>
  </div>

  <div id=\"onlineCreateScreen\" class=\"onlineScreen hidden\">
    <div class=\"onlineSectionTitle\">Joueurs vs bots</div>
    <div class=\"onlineModeGrid\">
      <button data-online-mode=\"1v4\"><b>1 joueur vs 4 bots</b><small>Lancement local immédiat — pas de salon.</small></button>
      <button data-online-mode=\"2v3-online\"><b>2 joueurs vs 3 bots</b><small>Salon Online pour 2 joueurs humains.</small></button>
      <button data-online-mode=\"3v2-online\"><b>3 joueurs vs 2 bots</b><small>Salon Online pour 3 joueurs humains.</small></button>
    </div>
    <div class=\"onlineSectionTitle\">Joueurs vs joueurs</div>
    <div class=\"onlineModeGrid\">
      <button data-online-mode=\"3h\"><b>3 joueurs</b></button><button data-online-mode=\"4h\"><b>4 joueurs</b></button><button data-online-mode=\"5h\"><b>5 joueurs</b></button>
    </div>
    <button class=\"onlineBack\" data-online-back>← Retour</button>
  </div>

  <div id=\"onlineConfigScreen\" class=\"onlineScreen hidden\">
    <div class=\"onlineField\"><label>Nom de la partie</label><input id=\"onlineRoomName\" maxlength=\"30\" placeholder=\"Ex. Les Loups du Nord\"></div>
    <div class=\"onlineField\"><label>Code de la partie</label><input id=\"onlineRoomCode\" maxlength=\"12\" placeholder=\"Ex. TRIBU42\"></div>
    <div class=\"onlineField\"><label>Objectif de victoire</label><select id=\"onlineVictory\"><option value=\"3\">3 points</option><option value=\"4\">4 points</option><option value=\"5\">5 points</option></select></div>
    <div class=\"onlineActions\"><button id=\"onlineCreateRoom\" class=\"onlinePrimary\">Créer le salon</button><button class=\"onlineBack\" data-online-back>← Retour</button></div>
  </div>

  <div id=\"onlineJoinScreen\" class=\"onlineScreen hidden\">
    <div class=\"onlineField\"><label>Code de la partie</label><input id=\"onlineJoinCode\" maxlength=\"12\" placeholder=\"Entrez le code reçu\"></div>
    <div class=\"onlineActions\"><button id=\"onlineJoinRoom\" class=\"onlinePrimary\">Rejoindre</button><button class=\"onlineBack\" data-online-back>← Retour</button></div>
    <div class=\"onlineNotice\">La connexion au vrai serveur sera branchée à l’étape suivante. Cet écran prépare déjà le flux et l’interface.</div>
  </div>

  <div id=\"onlineLobbyScreen\" class=\"onlineScreen hidden\">
    <div class=\"onlineLobby\"><div class=\"onlineLobbyHead\"><div><b id=\"lobbyName\">Partie TRIBU</b><div id=\"lobbyMode\" class=\"onlineStatus\"></div></div><div class=\"onlineCode\" id=\"lobbyCode\">—</div></div>
      <div id=\"lobbyPlayers\"></div>
      <div class=\"onlineNotice\" id=\"lobbyNotice\">En attente des joueurs et des joueuses…</div>
      <div class=\"onlineReadyRow\"><button id=\"onlineReady\" class=\"onlineSecondary\">Prêt·e</button><button id=\"onlineLaunch\" class=\"onlinePrimary\" disabled>Lancer la partie</button></div>
    </div>
    <button class=\"onlineBack\" data-online-back>← Quitter le salon</button>
  </div>

  <!-- Sélecteurs historiques conservés pour le moteur local existant. -->
  <select id=\"gameMode\" hidden><option value=\"1v3\">1v3</option><option value=\"1v4\">1v4</option><option value=\"2v3\">2v3</option><option value=\"3h\">3h</option><option value=\"4h\">4h</option><option value=\"5h\">5h</option></select>
  <select id=\"victoryMode\" hidden><option value=\"3\">3</option><option value=\"4\">4</option><option value=\"5\">5</option></select>
  <button id=\"startBtn\" hidden>DÉMARRER LA PARTIE</button>
</div></section>"""
if old_start not in s: raise SystemExit('start html anchor missing')
s=s.replace(old_start,new_start,1)

old_wire="""audioLoadPrefs();audioWireControls();document.addEventListener('pointerdown',()=>audioMaybeWelcome(),{passive:true});
$('startBtn').onclick=()=>{$('start').classList.add('hidden');$('game').classList.remove('hidden');init()};"""
new_wire="""audioLoadPrefs();audioWireControls();document.addEventListener('pointerdown',()=>audioMaybeWelcome(),{passive:true});
const ONLINE_RANDOM_NAMES=['Aube-Rousse','Corne-de-Brume','Loup-Serein','Éclat-de-Silex','Rivière-Noire','Chêne-Ardent','Renard-d’Or','Lune-Fauve','Vent-du-Nord','Pierre-Claire'];
let onlineSelectedMode=null,onlineReadyState=false;
function onlinePseudo(){const input=$('onlinePseudo');let v=(input&&input.value||'').trim();if(!v){v=ONLINE_RANDOM_NAMES[Math.floor(Math.random()*ONLINE_RANDOM_NAMES.length)];if(input)input.value=v}return v}
function showOnlineScreen(id){document.querySelectorAll('.onlineScreen').forEach(x=>x.classList.add('hidden'));$(id).classList.remove('hidden')}
function launchLegacyMode(mode,victory=3){$('gameMode').value=mode;$('victoryMode').value=String(victory);$('start').classList.add('hidden');$('game').classList.remove('hidden');init()}
function onlineModeLabel(mode){return ({'2v3-online':'2 joueurs vs 3 bots','3v2-online':'3 joueurs vs 2 bots','3h':'3 joueurs','4h':'4 joueurs','5h':'5 joueurs'})[mode]||mode}
function onlineSeatCount(mode){return mode==='2v3-online'?2:mode==='3v2-online'?3:mode==='3h'?3:mode==='4h'?4:5}
function renderPrototypeLobby(){
 const seats=onlineSeatCount(onlineSelectedMode),name=onlinePseudo();
 $('lobbyName').textContent=($('onlineRoomName').value||'Partie TRIBU').trim();$('lobbyCode').textContent=($('onlineRoomCode').value||'TRIBU').trim().toUpperCase();$('lobbyMode').textContent=onlineModeLabel(onlineSelectedMode)+' — victoire à '+$('onlineVictory').value+' points';
 let h='<div class=\"onlinePlayerRow\"><span>'+name+' <small>(créateur)</small></span><span class=\"'+(onlineReadyState?'readyBadge':'waitingBadge')+'\">'+(onlineReadyState?'Prêt·e':'Pas prêt·e')+'</span></div>';
 for(let i=1;i<seats;i++)h+='<div class=\"onlinePlayerRow\"><span>Place '+(i+1)+'</span><span class=\"waitingBadge\">En attente</span></div>';
 $('lobbyPlayers').innerHTML=h;$('onlineLaunch').disabled=true;$('lobbyNotice').textContent='En attente des joueurs et des joueuses… Le lancement sera disponible quand toutes les places seront occupées et que tout le monde sera prêt.';
}
$('startBtn').onclick=()=>launchLegacyMode($('gameMode').value,+$('victoryMode').value||3);
$('onlineCreate').onclick=()=>{onlinePseudo();showOnlineScreen('onlineCreateScreen')};
$('onlineJoin').onclick=()=>{onlinePseudo();showOnlineScreen('onlineJoinScreen')};
$('localTestBtn').onclick=()=>{onlinePseudo();launchLegacyMode('2v3',3)};
document.querySelectorAll('[data-online-mode]').forEach(b=>b.onclick=()=>{onlineSelectedMode=b.dataset.onlineMode;if(onlineSelectedMode==='1v4'){launchLegacyMode('1v4',3);return}showOnlineScreen('onlineConfigScreen')});
document.querySelectorAll('[data-online-back]').forEach(b=>b.onclick=()=>showOnlineScreen('onlineHome'));
$('onlineCreateRoom').onclick=()=>{onlinePseudo();if(!$('onlineRoomCode').value.trim())$('onlineRoomCode').value='TRB-'+Math.floor(1000+Math.random()*9000);onlineReadyState=false;renderPrototypeLobby();showOnlineScreen('onlineLobbyScreen')};
$('onlineReady').onclick=()=>{onlineReadyState=!onlineReadyState;$('onlineReady').textContent=onlineReadyState?'Annuler prêt·e':'Prêt·e';renderPrototypeLobby()};
$('onlineJoinRoom').onclick=()=>{const code=$('onlineJoinCode').value.trim();if(!code){$('onlineJoinCode').focus();return}onlineSelectedMode='3h';$('onlineRoomName').value='Partie rejointe';$('onlineRoomCode').value=code;onlineReadyState=false;renderPrototypeLobby();showOnlineScreen('onlineLobbyScreen')};
$('onlineLaunch').onclick=()=>{};"""
if old_wire not in s: raise SystemExit('wire anchor missing')
s=s.replace(old_wire,new_wire,1)

p.write_text(s,encoding='utf-8')
