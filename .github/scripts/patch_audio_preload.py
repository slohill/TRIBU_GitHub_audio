from pathlib import Path
import re

p = Path('index.html')
s = p.read_text(encoding='utf-8')

if 'function preloadOfficialCardArt()' not in s:
    anchor = 'const FACTION_PORTRAITS='
    if anchor not in s:
        raise SystemExit('preload anchor missing')
    preload = """function preloadOfficialCardArt(){
 Object.values(OFFICIAL_CARD_ART).forEach(src=>{const img=new Image();img.decoding='async';img.src=src});
}
preloadOfficialCardArt();

const FACTION_PORTRAITS="""
    s = s.replace(anchor, preload, 1)

s, n = re.subn(r'^\s*battle:\s*["\']assets/audio/battle\.mp3["\'],\s*$', '', s, count=1, flags=re.M)
if n != 1 and 'assets/audio/battle.mp3' in s:
    raise SystemExit('battle source removal failed')

start = s.find('function audioBattleBegin(){')
end = s.find('\nfunction audioBattleEnd(){', start)
if start < 0 or end < 0:
    raise SystemExit('audioBattleBegin block missing')
s = s[:start] + """function audioBattleBegin(){
 audioBattleCue();
 if(audioBattleActive)return;
 audioBattleActive=true;
 audioMode='ambient';
}""" + s[end:]

start = s.find('function audioBattleEnd(){')
end = s.find('\nfunction audioSetMusic(', start)
if start < 0 or end < 0:
    raise SystemExit('audioBattleEnd block missing')
s = s[:start] + """function audioBattleEnd(){
 if(!audioBattleActive)return;
 audioBattleActive=false;
 audioMode='ambient';
}""" + s[end:]

s = re.sub(r"\n\s*if\(audioBattleActive\)\{const b=audioTrack\('battle'\);.*?return\}\n", '\n', s, count=1)
s = s.replace("a.onended=()=>{if(audioMode!=='ambient'||audioBattleActive)return;", "a.onended=()=>{if(audioMode!=='ambient')return;", 1)

if 'assets/audio/battle.mp3' in s:
    raise SystemExit('battle.mp3 reference still present')
if "audioTrack('battle')" in s:
    raise SystemExit('battle track reference still present')
if "if(audioMode!=='ambient'||audioBattleActive)return" in s:
    raise SystemExit('ambient still blocked during battle')
if 'function preloadOfficialCardArt()' not in s:
    raise SystemExit('card preload missing')

p.write_text(s, encoding='utf-8')
