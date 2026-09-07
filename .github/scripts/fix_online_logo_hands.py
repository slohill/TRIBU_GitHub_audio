from pathlib import Path
import base64, re

p=Path('index.html')
s=p.read_text(encoding='utf-8')

# 1) En Online, plusieurs humains ne doivent jamais être traités comme du hot-seat local.
old="function isHotseatMode(){return !!G&&humanPlayers().length>1}"
new="function isHotseatMode(){return !!G&&!G.online&&humanPlayers().length>1}"
if old not in s:
    raise SystemExit('isHotseatMode anchor missing')
s=s.replace(old,new,1)

# 2) Chaque navigateur Online regarde et agit depuis SON siège, pas depuis le joueur actif.
old="""function localViewer(){
 if(isHotseatMode()&&Number.isInteger(hotseatViewerOverride)&&G.players[hotseatViewerOverride]&&!G.players[hotseatViewerOverride].bot)return hotseatViewerOverride;"""
new="""function localViewer(){
 if(G&&G.online&&Number.isInteger(G.online.myPlayerIndex)&&G.online.myPlayerIndex>=0&&G.players[G.online.myPlayerIndex])return G.online.myPlayerIndex;
 if(isHotseatMode()&&Number.isInteger(hotseatViewerOverride)&&G.players[hotseatViewerOverride]&&!G.players[hotseatViewerOverride].bot)return hotseatViewerOverride;"""
if old not in s:
    raise SystemExit('localViewer anchor missing')
s=s.replace(old,new,1)

# 3) Sort le logo embarqué de l'énorme data URI pour en faire un vrai asset web.
# Cela évite les problèmes de rendu/cache liés à l'image inline sur l'écran d'accueil.
m=re.search(r'<img class="onlineBrandLogo" src="data:image/(webp|png);base64,([A-Za-z0-9+/=]+)" alt="([^"]*)">',s)
if not m:
    # Le patch reste idempotent si l'asset est déjà référencé.
    if 'class="onlineBrandLogo" src="assets/tribu-title.webp"' not in s:
        raise SystemExit('online logo data URI anchor missing')
else:
    ext=m.group(1)
    data=base64.b64decode(m.group(2))
    out=Path('assets/tribu-title.webp' if ext=='webp' else 'assets/tribu-title.png')
    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_bytes(data)
    replacement=f'<img class="onlineBrandLogo" src="{out.as_posix()}" alt="{m.group(3)}">'
    s=s[:m.start()]+replacement+s[m.end():]

# Ajoute une version de cache explicite pour forcer le navigateur à prendre le logo corrigé.
s=s.replace('src="assets/tribu-title.webp" alt=', 'src="assets/tribu-title.webp?v=1" alt=', 1)

p.write_text(s,encoding='utf-8')
