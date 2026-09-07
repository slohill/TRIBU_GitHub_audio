from pathlib import Path
import base64,re

s=Path('index.html').read_text(encoding='utf-8')

old="function isHotseatMode(){return !!G&&humanPlayers().length>1}"
new="function isHotseatMode(){return !!G&&!G.online&&humanPlayers().length>1}"
if old in s:
    s=s.replace(old,new,1)
elif new not in s:
    raise SystemExit('isHotseatMode anchor missing')

old_lv="""function localViewer(){
 if(isHotseatMode()&&Number.isInteger(hotseatViewerOverride)&&G.players[hotseatViewerOverride]&&!G.players[hotseatViewerOverride].bot)return hotseatViewerOverride;"""
new_lv="""function localViewer(){
 if(G&&G.online&&Number.isInteger(G.online.myPlayerIndex)&&G.online.myPlayerIndex>=0&&G.players[G.online.myPlayerIndex])return G.online.myPlayerIndex;
 if(isHotseatMode()&&Number.isInteger(hotseatViewerOverride)&&G.players[hotseatViewerOverride]&&!G.players[hotseatViewerOverride].bot)return hotseatViewerOverride;"""
if old_lv in s:
    s=s.replace(old_lv,new_lv,1)
elif new_lv not in s:
    raise SystemExit('localViewer anchor missing')

logo_b64=''.join(Path(f'.github/tmp/logo.b64.{i}').read_text().strip() for i in range(4))
logo=base64.b64decode(logo_b64,validate=True)
out=Path('assets/tribu-title.webp'); out.write_bytes(logo)

pat=r'(<img class="onlineBrandLogo" src=")[^"]+(" alt="Tribu — Conquest of Myrmigate">)'
s,n=re.subn(pat,r'\1assets/tribu-title.webp?v=2\2',s,count=1)
if n!=1:
    raise SystemExit('online logo img anchor missing')

Path('index.html').write_text(s,encoding='utf-8')
