# Corruption — checkpoint 1 (2026-10-29)
Base: fc8ca7d12dbd4fbaab5346e550cba5b90752190b
Branch: corruption-integration. Do not merge or enable publicly before full integration and user trial.

Implemented locally in legacy engine:
- Explicit gameVersion, filtered expansion deck; stable existing card indexes.
- Independent second Portails card using existing placement/movement/recruitment; distinct token.
- Reciprocal same-card portal links, one building per region; Dragon stays on physical neighbors.
- Nine permanent randomly allocated NPC tribes after local setup: 2 humans, 1 ogre, 3 dwarves, 3 elves.
- NPC tokens behind units/buildings; expansion logo; base games omit these additions.

Validation:
- Browser with actual legacy functions: base deck, both portal placements, same-region refusal, independent links, recruitment, no Dragon teleport, isolated pair removal.
- NPC counts, no reroll, JSON round-trip, base game reset.
- No multiplayer, real tablet or complete expansion validation yet.
- All new public creation choices remain disabled. Local developer entry: launchLegacyMode('3h',5,'corruption').
- Browser check kept in original workspace work/corruption-integration/check-foundations.cjs (uses cached legacy assets).

Next:
1. Version propagation through room/server snapshots, six-player setup and faction selection.
2. Egnorax defense/cap/draw and Morcatt auction.
3. NPC alliances, Corruption, green loss selection.
4. Révoltes, heroes, clocks, bots passive-only, private/public views.
5. Full multiplayer regression, then user trial before main.
Rules: latest-decisions.json overrides older prose. Other per-card files contain validated texts.
Never modify historical backup branches or index_TRIBU_map_audio_cartes_fix.html.

## Checkpoint 2 — 2026-10-30
Version now propagates through room views, game views, legacy bootstrap, recovery capsules and canonical legacy snapshots. Missing version defaults to base for older games.
Corruption lobby capacity is six, behind server TRIBU_CORRUPTION_PREVIEW=1. Base six-seat requests and unknown versions are rejected.
Corruption launch remains explicitly blocked: sixth color, all setup paths and full faction rules are not ready.
Node options tests and real Socket.IO tests pass: base setup/bootstrap/recovery, six human connections, seventh refused, unfinished expansion launch refused. Foundation browser regression passes.
Next concrete work: six distinct color assets and full setup selection, new faction identifiers without replacing legacy indices 3/4, version-dependent deck generation on server. Then enable experimental launch only for complete mechanisms.

## Checkpoint 3 — setup visuals
User selected violet #a66bff. Added 15 optimized dice assets: Egnorax/Morcatt six colors, base factions violet. Local 6h setup has six players/colors and two new faction choices, info magnifiers and color routing. Base setup remains five colors/six portrait choices. Browser setup check passed; violet Egnorax inspected.
IMPORTANT: faction mechanics are NOT complete. Egnorax rounding/draw and Morcatt auctions remain pending. FACTIONS indices 5/6 reserved; legacy 3/4 aliases preserved. Full online setup still pending. Do not enable public selection/launch.

## Checkpoint 4 — Egnorax legacy rules
Rounded defendingUnits helper applied to battle creation, previews, NPC-destruction recomputation, bot estimates and Shadow defensive reinforcements (difference of rounded totals).
Unlimited cap handles zero owned regions without Infinity*0. Human start draw choice uses existing action confirmation, deck OR top two discard cards, one if only one, no discard option if empty. Bot currently uses normal deck.
Regional dice outside owner turn show rounded defense, own-turn/attacking unit counts unchanged.
Tests work/corruption-integration/check-egnorax.cjs pass defense odd/even, Yonkais regression, fortress 5 units=>13, reinforcement 5->6 adds zero defense, 6->7 adds one, draw cases, unlimited recruitment and display. Foundations browser test also passes.
Remaining: actual synchronized multiplayer scenarios, spectator unlimited-cap formatting, Morcatt auctions and full online setup. Do not enable public launch.
