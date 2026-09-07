from pathlib import Path

p = Path('index.html')
s = p.read_text(encoding='utf-8')

def rep(old, new, label):
    global s
    if old not in s:
        raise SystemExit(f'Motif introuvable: {label}')
    s = s.replace(old, new, 1)

rep(
".setupPanel h3{margin:0 0 7px;font-size:16px}\n.setupChoices{display:flex;flex-wrap:wrap;gap:7px;justify-content:center;margin-top:8px}",
".setupPanel h3{margin:0 0 12px;font-size:16px;line-height:1.25}\n#setupText{display:block;margin:0 0 12px;line-height:1.35}\n.setupChoices{display:flex;flex-wrap:wrap;gap:7px;justify-content:center;margin-top:8px}",
"espacement installation"
)

rep(
"BASE_COLORS.forEach((color,i)=>{if(state.setup.usedColors.includes(color))return;const b=document.createElement('button');b.className='setupColorBtn';b.dataset.color=color;b.textContent=COLOR_NAMES[i];b.style.borderColor=color;b.style.color=color;b.onclick=()=>{box.querySelectorAll('.setupColorBtn').forEach(x=>x.classList.remove('selected'));b.classList.add('selected');box.dataset.color=color;onlineSetupIdentityReady(box)}});",
"BASE_COLORS.forEach((color,i)=>{if(state.setup.usedColors.includes(color))return;const b=document.createElement('button');b.className='setupColorBtn';b.dataset.color=color;b.textContent=COLOR_NAMES[i];b.style.borderColor=color;b.style.color=color;b.onclick=()=>{box.querySelectorAll('.setupColorBtn').forEach(x=>x.classList.remove('selected'));b.classList.add('selected');box.dataset.color=color;onlineSetupIdentityReady(box)};box.appendChild(b)});",
"boutons couleurs"
)

rep(
"$('setupText').innerHTML='Province <b>'+me.province+'</b> — choisissez <b>2 régions parmi les 4 régions non hostiles</b>.<br>Sélection : <b>'+onlineSetupSelectedRegions.length+'/2</b>';\n   const ok=document.createElement('button');ok.textContent='Valider les 2 régions';ok.disabled=onlineSetupSelectedRegions.length!==2;ok.onclick=()=>onlineAck('setupRegions',{regions:onlineSetupSelectedRegions.slice()}).catch(onlineError);box.appendChild(ok);",
"$('setupText').innerHTML='Province <b>'+me.province+'</b> — cliquez directement sur la carte pour installer vos unités dans <b>2 régions parmi les 4 régions non hostiles</b>.<br>Sélection : <b>'+onlineSetupSelectedRegions.length+'/2</b>';\n   const ok=document.createElement('button');ok.textContent='Valider le placement';ok.disabled=onlineSetupSelectedRegions.length!==2;ok.onclick=()=>onlineAck('setupRegions',{regions:onlineSetupSelectedRegions.slice()}).catch(onlineError);box.appendChild(ok);\n   const restart=document.createElement('button');restart.textContent='Recommencer le placement';restart.disabled=onlineSetupSelectedRegions.length===0;restart.onclick=()=>{onlineSetupSelectedRegions=[];renderOnlineAuthoritativeSetup(state)};box.appendChild(restart);",
"validation et recommencement placement"
)

p.write_text(s, encoding='utf-8')
