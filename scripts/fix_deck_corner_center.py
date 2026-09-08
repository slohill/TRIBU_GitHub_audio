from pathlib import Path
p=Path('index.html');s=p.read_text()
old=".deckCorner{position:absolute;left:8px;top:8px;z-index:58;display:flex;gap:5px;height:8.33%;max-height:46px;min-height:29px}"
new=".deckCorner{position:absolute;left:50%;right:auto;top:8px;transform:translateX(-50%);z-index:58;display:flex;gap:5px;height:8.33%;max-height:46px;min-height:29px}"
assert old in s
s=s.replace(old,new,1)
# Remove the ineffective guessed selector block added previously.
old2="/* vOnline UI: pioche/défausse recentrées pour libérer la zone U */\n#map .deckZone,#map .deckArea,#map .drawDiscard,#map .piles,#map .cardPiles{left:50%!important;right:auto!important;transform:translateX(-50%)!important;top:1.5%!important;display:flex!important;gap:8px!important;flex-direction:row!important}\n"
if old2 in s:s=s.replace(old2,"/* vOnline UI: Pioche / Défausse utilisent directement .deckCorner, centrée en haut. */\n",1)
p.write_text(s)
