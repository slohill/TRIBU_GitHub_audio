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

## Checkpoint 8 — 2026-11-02 end-to-end auction verification
Two real browser pages + local Socket.IO server pass full harvest -> shared preparation prices -> disconnect/reload/resume buyer -> start -> sale -> final harvest reaction -> Embuscade -> payout. One owned region (2 Or) + sale (3) - unsold (1) = 4; buyer pays 3 then intercepts 4, seller unchanged.
Added serverTime on legacy stream/request/auction responses and monotonic browser clock projection. Artificial +120s client wall-clock skew does not corrupt auction display.
Test: work/corruption-integration/check-auction-online-browser.cjs. Production launch remains locked. Test fixture only changes room version after ordinary base setup, does not enable real production extension.
Remaining: seller disconnect at final payout and bot handoff, spectator public summaries, full six-player online setup/factions, alliance and hero integrations. No changes published to main.

## Checkpoint 9 — six-player online setup (preview only)
Server version-aware colors/portraits/capacity: violet + E_A faction5 and M_A faction6 only in Corruption; base indices 3/4 remain unchanged client-side. Both setupComplete and setupIdentity/setupRegions routes validate availability. Bots choose from version-specific remaining options.
Corruption setup launch allowed only with BOTH TRIBU_CORRUPTION_PREVIEW=1 and TRIBU_CORRUPTION_SETUP_PREVIEW=1. Normal/default launch stays blocked; public selector disabled.
Server initializes permanent NPC allocation once after all placements, copies allocation flag into legacy bootstrap, adds independent second portal to version deck. All six clients receive identical board/deck state.
check-six-online.cjs PASS six actual sockets, duplicate refusal, two setup routes, versioned factions/colors, NPC counts and portal count; base setup regression. Existing launch gate and two-browser Morcatt reconnect/Embuscade tests PASS.
Next: alliance cards and peaceful conquest, Corruption loss selection, remaining Oracle/heroes; spectator summaries and full bot game checks still pending.

## Faction portraits
Egnorax A/B and Morcatt A/B supplied BMPs optimized q90 WebP at 3000x3000. Both variants registered client/server. Info lenses checked; full Morcatt explanation restored. Commit d81d1419276113c7ea810e77d4ab5cb445c5f7b7.

## Checkpoint 10 — shared alliance loss planning
assets/corruption-alliances.js provides alliance lookup, peaceful NPC target eligibility including buildings, tribe-owned bonus queries and immutable loss selection plans. Plan includes stationed and all committed groups per original region; required min(5,total), auto-select <=5, choose/reset for >5. Validate rejects stale troop counts and forged choices before any engine mutation.
Seven Node scenario tests PASS: user example 1 stationed +4 committed, two battles, separate quota per region, emptied committed origin, opponent exclusion, stale/forged selection, building conquest and immediate bonus loss without alliance.
NOT YET CONNECTED: module not loaded by index; card play/replacement/theft, green map links, final loss application and battle/NPC reconciliation remain next. Do not claim alliances playable.

## Checkpoint 11 — legacy loss application
Shared alliance module is now loaded; applyAllianceLossPlan validates all choices before mutation and uses existing building/NPC and destroyed-battle helpers. Updates committed origin moves and attack totals, preserves unrelated battles, removes old defender cards when NPCs return while keeping attacker cards. Rejects duplicate application and stale/forged routing. No automatic gameplay entry point yet: alliance card play, mandatory selection UI/green links, pause/sync ownership and post-resolution rendering remain to connect.
Verified real browser legacy scenarios: 1 stationed +4 committed, second battle survives, no-attacker cancellation/discard, NPC fortress defense15 / bare NPC5, stale plan has zero mutation. Eight unit tests plus existing foundation and Egnorax browser checks pass.
Main unchanged. Public Corruption remains locked. Next: mandatory loss UI and card replacement/Corruption theft flow; do not claim alliance gameplay complete.

## Checkpoint 12 — mandatory loss view component
assets/corruption-alliance-loss-ui.js provides mount/destroy with explicit per-origin stationed/attacking dice and green source links, right-column counters, reset and OK gated by exact quotas. Other viewers see waiting state and disabled picks. Picks are provisional; controller callback owns actual application. ResizeObserver updates links on responsive map resize; cleanup removes all overlays/listeners. Existing engine/render is not overridden by this component.
Browser check-alliance-loss-ui.cjs PASS actual clicks: 1 stationed +4 attackers, independent second battle, reset, no premature confirm, other viewer read-only, resize to 768x1024, cleanup. Preview saved locally as alliance-loss-ui-preview.png.
NOT YET WIRED into automatic gameplay. Next controller must handle mandatory pause/card guards, preserve zoom/show/proposals, bot choices, online authoritative submission and stale-plan refresh; then connect replacement/theft. Component is intentionally not loaded by index until controller integration. Main unchanged.

## Checkpoint 13 — local mandatory loss controller
Loss UI is now loaded and rendered by legacy render. beginAllianceLossSelection creates G.allianceLoss, pauses battle/gold/paid-draw, blocks gameplay entry points and exchange execution while preserving show/proposals/zoom. OK applies the validated loss bridge, closes resolved battles and resumes eligible timers. Bots choose valid groups and confirm automatically. Existing auto-resume safety was attempting to restart paused gold during selection; resume helpers now respect loss lock.
Real browser controller test PASS: provisional five picks do not mutate board until OK, 8->3 troops, gold frozen then resumed10s, Tax/Oracle/recruit blocked, zoom/commerce accessible, bot7->2, base and online entry rejected. Loss bridge/foundations/Egnorax regression PASS.
Scope: local controller tested through explicit entry; cards not yet registered/wired. Online entry explicitly refuses until authoritative action/sync implemented. Next: card replacement/theft call sites, alliance card registration/bonuses, authoritative online loss submission and interruption recovery. No public deployment.

## Checkpoint 14 — alliance cards and local replacement
Shared idempotent registry appends alliances after second portal with 3 dwarves/3 humans/4 elves/1 ogre, same order client/server. Optimized existing WebP artwork copied and wired to official art and zoom text. Base/tutorial deck filtering preserved.
Local human play-phase hand action: first click explanation, second play; replacing discards old alliance and enters mandatory loss controller. One alliance stays in play; picks provisional until OK. Online card play remains gated. Real browser check-alliance-cards.cjs PASS counts, two-click interaction, dwarf->human replacement, five losses, zoom text/art and base exclusion; unit/controller regressions PASS.
INCOMPLETE abilities: peaceful conquest only has predicate, not movement call sites; dwarf harvest and human attack queries not wired; elf flee and ogre die not implemented. Corruption theft and authoritative online losses pending. Thus extension remains private/locked, not release-ready.

## Checkpoint 15 — peaceful conquest, dwarf harvest, human attacks
Normal movement recognizes allied NPCs as peaceful and transfers surviving city/fortress via legacy helper; Shadow uses same alliance predicate. Enemy-owned regions remain hostile. Human bonus is computed dynamically in battlePower attack only, including Shadow; losing region/alliance removes corresponding bonus.
Dwarf harvest metadata records original owner/regions and non-dwarf base; preserved by Embuscade and checked on render/payout, including stacked gold reactions. Revocation affects pending gain only, not already paid gold. Morcatt auction carries metadata; sales/unsold are combined before zero floor, including after bonus removal.
Real browser check-alliance-bonuses.cjs PASS fortress/Shadow peaceful conquest, enemy exclusion, human 6->5->4 attack, unchanged defense, dwarf harvest7/Embuscade/removal2/payout2, Morcatt pending4->0 with three unsold. Card replacement, auction UI and foundations regressions PASS. Foundation test updated from +1 portal to +12 cards (portal+11 alliances), checks per-tribe counts.
Remaining: Elf flee, Ogre active power, Corruption theft, online authoritative loss controller, heroes/Oracle. Public release stays locked.

## Checkpoint 16 — local Corruption theft
Registered four tactical Corruption copies with optimized artwork and zoom description. Same hand explanation/second-click gesture; target modal shows opponent alliances. No card/gold consumption or journal leak before selection; close cancels. On valid target, deduct5, discard Corruption, move enemy alliance to actor hand, enter victim loss selection. Local hotseat switches viewer to victim. Pause ownership transfers from targeting to losses so gold remains paused until OK; dwarf pending metadata refreshes even after Embuscade.
check-corruption-card.cjs PASS opening/cancel, cost/card once, victim 8->3 chosen troops, pending intercepted dwarf gain7->2, gold resumes10, insufficient gold and replay rejected. Alliance bonus/foundation regressions PASS; expected expansion deck now +16.
Remaining: online authoritative controller, Haute Noblesse immunity when hero integrated, full decimation/turn continuation edge cases after mandatory losses, Elf flee/Ogre power. Corruption is local preview only; public extension still locked.

## Checkpoint 17 — decimation after alliance losses
Mandatory loss confirmation now invokes legacy checkDecimations, removes decimated players from pending battle priority orders and preserves engaged survivors. Active decimation defers turn end until current battle/gold/paid-draw/priority/Oracle/Dragon resolutions finish; epoch/player guard prevents a stale end from affecting a later turn. Existing advanceTurn handles the actual transition.
check-alliance-decimation.cjs PASS: active last troops lost -> assets discarded and next turn once; pending gold survives, pays then advances; inactive victim does not change active player; surviving committed troops prevent decimation. Corruption/card-controller regression checks PASS.
Next: Elf flight and Ogre active power, then authoritative online losses/theft and hero/Oracle integration. Main unchanged.

## Checkpoint 18 — local Elf flight
Battle opening offers eligible human defender Fuir/Defendre in right column; choice pauses reaction timer, Fuir highlights destinations and map click commits. Eligible if Elf alliance + controlled Elf region; own/empty land and allied Elf NPC allowed, enemy/non-Elf NPC excluded, sea destinations allowed, portal adjacency uses existing strict pair helper. All defending units relocate together; attacker captures source and surviving building with all attacking units, no epic reward; used battle cards discarded through existing helper, parent Shadow battle restored via existing destroyed-battle finalizer.
Removing alliance before commit cancels flight; Corruption remains playable during decision. Bots currently always defend. Online entry stays disabled pending authoritative actions.
check-elf-flight.cjs PASS full-unit flight/Elf NPC conquest/building transfer/no epic, invalid target rejection, removal cancellation, actual Corruption during choice -> losses -> NPC defense5, valid portal pair accepted/mixed pair rejected, bot no-block. Corruption, decimation and foundations regression PASS.
Remaining verification: full sea-origin and nested Shadow-flight browser scenarios, multi-browser authoritative sync; Ogre ability and heroes/Oracle. Main unchanged.

## Checkpoint 19 — maritime/nested flight validation
Fixed receiving garrison reconciliation when Elf flight reinforces a suspended battle destination: refresh defender/hostile status and actual/faction-adjusted defense plus existing building, including sea fleet defense for same defender. Parent battle cards/time remain unchanged; no new battle resolution is invented.
check-elf-nested.cjs PASS sea-origin flight preserving unrelated third-party fleet, nested Shadow flight back to parent (9s, original attack card preserved, child card discarded once), destination 2+4 units/fortress =>16defense; real browser clicks Fuir then C2 relocate4 and remove controls. check-elf-flight.cjs regression PASS including actual Corruption and paired portals.
Remaining next: Ogre active ability, authoritative online extension actions, Oracle/heroes. Main unchanged.

## Checkpoint 20 — local Ogre ability and owner-chosen collateral
User clarified: when adjacent origin has stationed and committed units, its owner chooses which group loses one. Extended shared loss planner with Ogre per-region quota1, reused UI/controller and sequential per-owner queue; bots resolve choices automatically. Land regions only, ordinary adjacency helper includes valid portal links.
Ogre in-play active uses d6 once per turnEpoch, attacker only (Shadow allowed), requires Ogre alliance+region. Battle-only dynamic bonus; loss of alliance/control cancels bonus/blast, use stays consumed. Normal battle completion queues adjacent losses after completed attackers have left engaged origins. Destroyed-battle finalizer also supports blast. Existing two-click in-play activation reused; die result in journal/battle breakdown. Online activation gated.
check-ogres.cjs PASS +4 on4units=8, repeat refused, next epoch available, Shadow eligibility, own/enemy/third-party lands lose1 after battle, sea untouched, alliance removal cancels while use consumed, owner can remove committed unit instead of stationed. Alliance unit/Corruption/Elf-nested regressions PASS.
Pending: hook Ogre 3/4 into Re voltes once Oracle implemented; full battle-destruction/decimation/stacked-blast and real online tests; hero mechanics. Bots do not proactively roll Ogre yet. Public extension remains locked.

## Checkpoint 21 — interrupted Ogre battle cascade
Queued Ogre blasts survive recursive battle finalization without overwriting a mandatory loss choice. Queue drains only between completed owner selections; turn-end waits for it. ResolveBattle/startReactionWindow/advancePriority explicitly refuse during mandatory losses, protecting against stale callbacks.
check-ogre-cascade.cjs PASS child+parent battles destroyed together, parent's valid Ogre blast retained once, card stacks discarded once, sequential two-owner selection, gold remains paused through first choice and resumes10 only after final, repeat finalizer/stale resolve refused. Ogre, decimation and Elf-nested regression PASS.
Next: Oracle Re voltes including Ogre roll3/4 integration; online authoritative extension flow and heroes remain. Public main unchanged.

## Checkpoint 22 — Revolts timing/selection foundation
New shared corruption-revolts.js models activation generation, capture of eligible3/4 before original action, after-action enqueue/dedup, replacement/reactivation cancellation and future immunity suppression. Provisional selection covers stationed land, sea fleets and all committed origin groups; exactly one origin, optional1or2 units, reset, stale validation; no board mutation.
Six Node tests in server/test/corruption-revolts.test.js PASS: no retroactivity/double trigger, original action timing, replaced active/suppressed oracle, split two battle groups, seas/self-target support, empty origin committed survivors, no targets and stale choices. Event deduplication also survives serialized state and prototype-like identifiers. All 14 Revolts/alliance unit tests pass on resume.
NOT YET LOADED OR PLAYABLE: Oracle registry/deck/image, activation hooks, roll capture call sites, selection UI/red halos/links, actual casualty bridge and notices remain. Do not claim Revolts implemented in gameplay. Next integrate this module with legacy carefully, including sea casualties and NPC defense restoration.
Main unchanged.

## Checkpoint 23 — Revolts selection view
The existing mandatory casualty view accepts an explicit revolts mode, selecting by roll actor rather than victim. Red source lines sit underneath dice, red halos identify eligible groups, one or two losses from a single origin are provisional, sea fleets supported, reset and OK in side panel; other viewers wait without interactive selection. Default alliance/Ogre behavior preserved.
New portable server/test/corruption-revolts-ui.cjs browser check PASS real clicks: actor/victim distinction, two separate engaged groups, one-loss confirmation, two-loss limit, cross-origin rejection, sea selection, reset, observer and responsive geometry/cleanup. Existing alliance UI and legacy mandatory controller browser checks also PASS.
Still not added to Oracle deck: do not permit drawing a card whose effect is not connected. Next: casualty application bridge (sea + NPC restoration), mandatory controller and notices, then Oracle/roll hooks and optimized card registration. No public deployment; main unchanged.

## Checkpoint 24 — Revolts legacy casualty bridge
Loaded pure Revolts module and added local-only applyRevoltLossPlan. Shared validated casualty command application with alliance losses, preserving their behavior. Handles selected sea fleets only, movement allowances, committed origins/attack totals, defensive recomputation and stale/replay rejection. Extracted existing destroyed-battle finalization into settleDestroyedBattle so removing the last defender captures empty non-NPC land/sea without destroying unrelated attackers originating there. Original NPC returns5/15 and retains attacker cards; defender cards discarded once.
check-revolts-losses.cjs PASS mixed stationed/committed loss, independent second battle, NPC fortress15, empty capture preserving outgoing troops, partial sea defense, third-party fleet preserved, stale/replay rejection. Existing alliance-loss and Ogre-cascade browser regressions PASS.
Next: mandatory resolution controller/notices and timer ownership, Oracle registry/roll hooks. Revolts still absent from deck and not playable through normal gameplay. Public main unchanged.

## Checkpoint 25 — local Revolts mandatory controller
Explicit beginRevoltSelection(actor,target) uses shared mandatory lock and pause ownership. Ten-second instruction notice (skip dismisses instructions only), unlimited selection, actor-only confirmation, five-second post-loss Oracle notice/sound while lock remains, then existing decimation/battle/Ogre/timer continuation. Bots choose up to2 units from one origin. Cards/gameplay blocked while zoom/commerce show workflow remains accessible. Stale plans regenerated; empty refreshed target exits safely. Oracle notice customization defaults preserve prior callers and uses textContent for names.
check-revolts-controller.cjs PASS actual UI pick/confirm: victim cannot confirm, loss provisional then once, gold paused until final notice ends then10s, instructions10/announcement5, zoom/commerce, bot continuation. Alliance mandatory controller regression PASS.
Not automatically triggered yet: Oracle registration/deck/optimized art and eligible roll hooks remain. Online entry gated. Public main unchanged.

## Checkpoint 26 — human action roll hooks
Added captureRevoltRoll/resolveRevoltAfterAction, activation generation reset on actual Oracle activation/replacement and Divination full discard. Human Ogre, Thief3/4 and Assassin rolls capture eligibility before effect and start mandatory reaction after effect. Ogre battle remains live; Assassin removes/discards target before reaction; failed Thief result closes agent overlay before selection. Online remains gated.
check-revolts-rolls.cjs PASS actual forced4 Ogre/Thief/Assassin paths with fixture-activated Revolts: applied Ogre+4 before choice, battle survives resolution, one target loss, Assassin terminal discard before reaction, old token rejected after Oracle replacement. Existing Ogre regression PASS.
Still not in deck: Oracle roll/end-turn continuation, bot roll paths and movement storm-roll interaction need wiring/verification before card registration/art. Full online and hero integration remain pending. Main unchanged.

## Checkpoint 27 — local Revolts card and remaining roll paths
Oracle3/4 defers turn completion until mandatory losses and announcement finish; epoch guard prevents duplicate transition. Bot Thief/Assassin capture before effects and resolve afterward, bot Oracle uses same path. Added one local Corruption Oracle copy, deck helper shared by initial deal and full Divination reshuffle, base/tutorial exclude it. Registered optimized art and prescribed zoom text; owner dice red pulse while active, reduced-motion fallback. Replacement clears effect. Storm die cannot coincide with active Revolts because they are mutually exclusive active Oracles.
Browser checks PASS: Oracle waits then advances once, bot Oracle/Thief/Assassin, actual card activation/replacement, one copy/base/tutorial isolation, red owner dice and art served. Foundations regression PASS.
Local preview now draws Revolts. Online authoritative extension integration remains gated/pending; heroes not yet implemented. Need broader interruption/decimation and six-player integration verification before public release. Main unchanged.
