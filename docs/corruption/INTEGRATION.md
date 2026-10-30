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

## Checkpoint 5 — Morcatt auction state engine (not yet connected to gameplay)
assets/corruption-auction.js implements serializable preparation, prices, round ordering, 30-second deadline, revision-checked bids/pass, immediate payments/card award, unsold discard/penalty, final nonnegative harvest and bot 3/10 caps. Same-name portal copies counted together for singleton policy.
Six Node tests pass: preparation/launch, rebids/pass reset, stale simultaneous offer, deadlines/payment once, budgets, no buyer/empty deck, JSON restore, bots.
NOT DONE: UI in Morcatt Commerce row, map notice, actual server-authoritative auction event handlers, harvesting bridge to offerGoldGain, card-activation guards while allowing previews/proposals, bot scheduling. Module deliberately not loaded in index yet. Next work is these connections before claiming Morcatt playable.

## Checkpoint 6 — local Morcatt harvest UI
Loaded auction engine and new corruption-auction-ui.js. Harvest reveals via legacy drawOneToPool, shared Commerce panel, editable prices/no preparation timer, launch, bid/pass, 30s display, sequential settlement, bots, final offerGoldGain bridge. Card entry guards block activation/purchases while zoom/show/proposals remain available. Local browser test checks sale/payment/gold reaction and accessible zoom/Commerce; Egnorax regression passes.
Online harvest explicitly returns an integration message: authoritative auction actions and multi-device sync remain TODO. Price changes currently use onchange; live cross-client updates pending. Do not unlock online Corruption.

## Checkpoint 7 — authoritative auction actions
Server corruption-auction-sync.js owns price/start/bid/pass, revisions, deadlines and bot actions. Socket actor taken from authenticated room membership. Active-auction legacy commits only merge Commerce proposals, preserving balances, cards and auction state; execution of exchanges rejected.
Online UI sends actions and displays server snapshots; server ticks even if seller disconnects. Finished auction owner/driver bridges to existing gold reaction. Initial harvest still enters through legacy snapshot.
Real Socket.IO test with test-only fixture passes concurrent bids, stale rejection, single payment/award, old snapshot overwrite resistance. Local browser auction regression passes.
TODO before release: full multi-browser harvest-to-Embuscade and reconnect tests; initialize/finish handoff races; server-clock offset for display; spectator public summaries; six-player/faction online setup. Public launch still locked.
Test fixture creates temporary server copy; test-only event is never included in production server.
