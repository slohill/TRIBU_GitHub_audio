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
