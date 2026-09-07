from pathlib import Path

path = Path('server/server.js')
text = path.read_text(encoding='utf-8')

replacements = [
    ("    canHarvest: game.phase === 'start' && ownTurn,\n    canRecruit: game.phase === 'start' && ownTurn,",
     "    canHarvest: false,\n    canRecruit: false,"),
    ("function finishSetupIfReady(game) {\n  if (game.players.some",
     "function finishSetupIfReady(game) {\n  if (game.phase !== 'setup') return false;\n  if (game.players.some"),
    ("  const participants = shuffle(humans.concat(bots), rng);",
     "  const participants = shuffle(humans, rng).concat(bots);")
]

for old, new in replacements:
    if old in text:
        text = text.replace(old, new, 1)
    elif new not in text:
        raise SystemExit(f'Expected server block not found: {old[:60]}')

path.write_text(text, encoding='utf-8')
