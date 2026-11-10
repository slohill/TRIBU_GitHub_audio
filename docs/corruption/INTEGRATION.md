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

## Checkpoint 28 — shared hero lifecycle foundation
New corruption-heroes.js implements own-play placement/return, one hero, explicit replacement confirmation with stale instance protection, return old hero to hand, deployment identity and next-owner-turn readiness. Passive readiness survives serialization and ends immediately when hero instance leaves play. Active ability usage recorded per epoch; bots cannot activate/return. Guide activePhase start exception supported. Existing engine caller must normalize inPlayUID and enforce mandatory-action locks before mutations.
Seven Node tests PASS: phase/base gates, next owner timing, once-per-turn, replacement confirmation/stale instance, use-return-repose delay, removal invalidates readiness, bots/passives, JSON use persistence, Guide start phase.
NOT LOADED OR PLAYABLE: no hero registry/deck/UI hooks yet, no individual abilities. Next wire common engine lifecycle and first hero abilities before enabling cards in deck. Main unchanged.

## Checkpoint 29 — local hero lifecycle UI
Loaded hero module. Human hand entry prepares deployment, replacement uses existing Agent modal with explicit cancel/confirm and revalidates instance. Return button in hero explanation; own play/mandatory lock/game-over/online guards. Agent UID normalization retained. Owner advanceTurn marks next-turn readiness, dormant title grayed until then; repose resets. Existing Assassin type matching recognizes Agent — Heros, object theft excludes them.
check-hero-ui.cjs PASS with synthetic count0 hero fixtures: placement/dormancy, cancel/confirm, next owner turn, return/repose, assassination eligibility/no in-play theft, phase/online/mandatory/stale guards. Existing alliance card and Revolts Oracle/bot browser regressions PASS.
Real hero cards still NOT REGISTERED: individual abilities/art and bot placement need integration before enabling in deck. Online remains gated. Main unchanged.

## Checkpoint 30 — Defenseuse local abilities
Registered one Defenseuse du peuple after existing extension cards, shared server catalog order, optimized prepared WebP and prescribed named ability text. Union dynamically adds2 to land defender battlePower only when exactly1 stationed unit; never multiplied by faction or applied at sea/outgoing groups. Givre de guerre for ready Griffes-Blanches overrides city/climate terrain, reuses recruitment/building legality, adds snow layer above Sundo desert below dice. Removing instance immediately disables queries. Bots place a hero when none in play and use next-turn passives, no replacement/return/active.
check-defenseuse.cjs PASS timing, Canicule/Sundo precedence, recruitment2, Sundo placement refusal, 1->2 units dynamic bonus, Yonkai3+2 pluscity10, sea exclusion, halo order, return/removal, bots, base/tutorial exclusion. Hero unit/UI and Revolts human-roll regressions PASS. Foundation extension deck count now base+17; Oracle9.
Local first real hero playable. Four heroes remaining, online authoritative extension pending. Public main unchanged.

## Checkpoint 31 — Guide Ancestrale local abilities
One Guide registered with prepared optimized art and prescribed named text. Holder start-turn red Divination button explains then opens private ordering of top3; reset/keep/confirm, once-per-turn through lifecycle. Start actions/other card entry blocked while mandatory ordering; modal cannot cancel after revealing. Short deck preserves remaining1/2 then shuffles all others including active Oracle, clears its persistent climate/Revolts effect. Confirmation writes reverse order for pop-based deck, updates next preview. Bots use passives only per latest decisions (superseding older auto-Divination spec).
Yonkai Culture dynamically subtracts target buildingDefense (cities/fortresses/walls) from defender battlePower including Shadow, leaves regional visuals intact, disappears with hero.
check-guide.cjs PASS real double-click UI/order, lock/close refusal, consumed button, short-deck nine unique IDs/active clear, Yonkaï+Shadow cancellation, other faction/removal restoration. Defenseuse, Revolts Oracle/bots, foundations regressions PASS; extension TRIBU deck base+18.
Three heroes remain (Golem/Haute/Guilde); authoritative multiplayer extension pending. Public main unchanged.

## Checkpoint 32 — Haute Noblesse local abilities
Registered one Haute noblesse with optimized art/named zoom text. Mercantile uses hero once-per-epoch own-play gate, rolls d6 and offers2X via existing gold engine/sound. Captured Revolts token survives Embuscade in gold metadata and hero assassination; queued only after payout, drains after Dragon/mandatory notices finish. Passive Morcatt immunity filters eligible Ambushers and revalidates play, excludes Corruption targets, suppresses active Revolts target at next owner turn/activation. Removal immediately disables Embuscade/Corruption protection; no retroactive die trigger. Bots passives only.
check-noblesse.cjs PASS delayed activation/once, forced4=8 gold, Embuscade recipient, actual Assassin after roll retains gain, Revolts after payout, delayed immunity and loss, gold44->Dragon0 and destruction before Revolts choice. Guide and Corruption theft regressions PASS. Deck expectation base+19.
Remaining heroes Golem/Guilde; verify broader battle/gold interruption cases and online authoritative flow before public release. Main unchanged.

## Checkpoint 33 — Guilde de l'ombre local abilities
Registered Guild with optimized art and named text. Furie once per own play: roll then opponent hand target4/5 or Agent/Hero6, corresponding thief/assassin/fail sounds, no target consumes use, captured3/4 Revolts after effect. Pending action retained independently of agent modal so actual Assassin interruption/removal of Guild does not erase rolled action. Original pause ownership restored after selection/Revolts.
Colony: ready Egnorax can reserve units on one empty non-NPC land excluding committed origins; neutral ownership/troops untouched until beginPlay confirms; translucent preview/highlight. Normal cost, no faction cap. Reset clears choice/refunds via legacy snapshot; loss of hero during recruitment resets all through existing helper; contested extra region refunds its reservation only. Empty building transfers through legacy helper, portal retained.
check-guild.cjs PASS actual Assassin after roll followed by theft and Revolts, roll6 elimination/once, provisional2 on neutral region/second region refusal, reset, confirmation ownership, hero loss full reset, enemy occupation selective refund, committed source exclusion. Haute Noblesse regression PASS. Deck expectation base+20.
Remaining Golem, broader integration/authoritative multiplayer. Main unchanged.


## Checkpoint 34 — Golem local abilities (2026-11-06)
Golem added as one optimized WebP card. Violence uses next-own-play readiness and once-per-turn lifecycle, excludes own/adjacent land including strict portal pairs, rolls before selecting one land origin, allows exact stationed/committed group losses and black UI. Existing mandatory casualty engine handles consequences; captured 3/4 resolves Revolts after losses. Reptone passive recruits on sea Z for 1 Gold up to 3 units with normal cap and recruitment reset.
Checks PASS: check-golem.cjs (readiness, once, 4 losses, black chips, subsequent Revolts, capped sea recruitment/reset), corruption-golem.test.js (adjacency, groups, reset, stale selection), check-revolts-losses.cjs, check-guild.cjs, check-foundations.cjs (base deck unchanged, extension base+21).
Still local preview only: full multiplayer hero authority and expanded simultaneous battle/Gold interruption testing remain before release. Main untouched.

Additional checks PASS: check-golem-battles.cjs (mixed origins, outgoing battle cancellation, NPC15, empty conquest, stale/replay); check-golem-gold.cjs (Gold pause across Golem and Revolts, resume after both).


## Checkpoint 35 — Online hero lifecycle (2026-11-06)
Server corruptionHeroAction validates authenticated actor, exact legacy revision, own play phase, mandatory locks, hero instance and confirmation. Shared lifecycle module handles placement/replacement/return; no duplicate rules engine. Client flushes pending changes, prevents duplicate submission, applies canonical response; replacement preview remains private and cancellable. Cards stay dormant until next owner turn.
Checks PASS: corruption-hero-sync.test.js (actor/revision/once, delayed readiness, replacement confirmation/UID, return, mandatory/base guards), check-heroes-online-browser.cjs (two real sockets/browser pages, placement, private cancel/replacement, page reload recovery, wrong actor/stale return rejection, synchronized return), check-hero-ui.cjs local regression.
Scope: only hero lifecycle is newly enabled in legacy online preview. Active abilities and Golem/Guild recruitment passives remain locally gated; multiplayer integration is NOT complete. Main/public release unchanged.


## Checkpoint 36 — Guide Divination online (2026-11-06)
Shared corruption-guide module handles preparation, short-deck recycling and reorder in local and server paths. Server validates owner/start phase/readiness/once-per-turn, serializes each selected position/reset/confirmation and retains pending state through reload. Legacy snapshots cannot overwrite a pending Divination; Commerce proposals remain mergeable, completed trades rejected. Holder-only chooser UI restored after state recovery; next Oracle updated after confirmation. Short decks preserve remaining top cards and recycle all others including active Oracle; climate and Revolts are cleared.
Checks PASS: corruption-guide-sync.test.js (order/actor/replay, short deck9/active removal, proposal-only merge), corruption-hero-sync.test.js, check-guide.cjs local regression, check-guide-online-browser.cjs (two browsers, double-click, holder-only overlay, partial selection reload, final order/preview, once), check-heroes-online-browser.cjs regression.
Scope: Guide active ability newly enabled in online preview. Legacy transport still sends full game snapshots to players; privacy verified here concerns displayed UI, not a redesigned secret-data protocol. Other hero active abilities and Golem/Guild recruitment passives remain to integrate online. Main unchanged.


## Checkpoint 37 — Haute Noblesse online (2026-11-06)
Server owns Doigté mercantile roll and once-per-turn consumption. Shared gold-reaction-state creates the existing legacy 10-second gain; no new payout engine. Embuscade, Assassin after activation, battle suspension, Dragon threshold and gold sound retain legacy resolution. Captured Revolts token waits until gain/Dragon resolution. Ready Morcatt suppresses active targeted Revolts before capture.
Noblesse-triggered Revolts can now resolve through legacy online actor ownership: only roller begins/chooses, instruction/announcement stages restore on reload using stored deadlines, viewers receive notices, selection has no timeout, existing casualty engine applies losses. Other Revolts roll sources remain gated online until their integrations.
Checks PASS: corruption-noblesse-sync.test.js (readiness/once/server roll, battle pause metadata, post-death gain, Morcatt immunity), existing Guide/lifecycle server tests; check-noblesse-online-browser.cjs (two browsers roll4/8Gold, Embuscade18Gold, subsequent Revolts, reload during selection, one loss, shared completion); check-noblesse.cjs legacy Assassin/Dragon/immunity; check-guide-online-browser.cjs and check-foundations.cjs regressions. Real-device audio audibility and broad simultaneous battle/network stress testing remain for release validation.
Scope: Haute Noblesse active ability enabled in online preview; Guild/Golem active powers and recruitment passives still pending. Main/public site unchanged.


## Checkpoint 38 — Guild online and Colony recruitment (2026-11-06)
Furie server-owned roll/once and target resolution use shared corruption-guild mechanics. UID revalidation for Agent/Hero elimination; random theft server-side without public card name; fail/thief/assassin events emitted via existing synchronized sound stream. Pending roll survives hero loss; completion stays actor-owned, then resolves captured Revolts before resuming paused timers. Holder-only choices restore after reload.
Colony passive enabled on legacy online recruitment path: provisional one neutral land region, reset/confirmation preserved. Incoming hero removal overrides dirty recruitment display preservation; resulting full reset is republished canonically instead of remaining only a local render mutation.
Checks PASS: corruption-guild-sync.test.js (roll6 UID/replay/hero death, theft/no target, fail1/2/3 and Revolts, sound metadata), check-guild.cjs local regression; check-guild-online-browser.cjs two browsers (private reload choice, roll4 theft/sound, Revolts, provisional/reset/commit colony, simulated incoming hero removal resets and server snapshot reflects reset); check-noblesse-online-browser.cjs and Noblesse unit regressions. Real-device sound audibility and broader concurrency testing remain release checks.
Main/public unchanged. Golem online active/recruitment integration remains next.


## Checkpoint 39 — Golem online and Fire Sea recruitment (2026-11-06)
Server owns roll, once-per-turn consumption, provisional grouped selection/reset and exact validation before authorizing the legacy casualty engine. Shared Golem topology uses actual client map DATA and strict portal pairing. No eligible targets consumes neither die nor ability. Pending Golem state is protected from ordinary legacy snapshots except Commerce proposals; authorized holder publishes the legacy result with the operation receipt. Full battle consequences remain in the legacy engine, not reimplemented server-side.
Online partial selections restore after reload; black chips/links retained; captured Revolts follows losses with Gold remaining paused until both complete. Ready Reptone Golem sea recruitment enabled on legacy synchronization path, cap and reset preserved.
Checks PASS: corruption-golem-sync.test.js (grouped selection, portal exclusion/no use, reset/stale/replay validation, authorized owner), corruption-golem.test.js; check-golem-online-browser.cjs two browsers (partial reload, 4 losses + Revolts, Gold pause/resume, capped sea recruitment/reset); check-golem.cjs, check-golem-battles.cjs (multi-origin battle/NPC15/capture), check-guild-online-browser.cjs regression.
Main/public unchanged. Remaining work is global Corruption integration audit, especially online alliance/Oracle roll sources, bots, simultaneous battles and release validation; hero hookups alone do not mean the whole extension is ready.


## Checkpoint 40 — Global audit and real online Oracle activation (2026-11-06)
See AUDIT-2026-11-06.md for scope, evidence and remaining online gates. 47 unit tests plus seven integration scenarios pass. Fixed actual Oracle activation/replacement not updating Revolts online; new two-browser test activates the Oracle through activateOracle rather than injecting active state, then verifies hero/Embuscade/Revolts and replacement. Alliances, Corruption theft, Elf/Ogre powers, legacy roll capture and bot hero placement remain gated online and block release. Main unchanged.


## Checkpoint 41 — Online alliances and replacement losses (2026-11-09)
Shared alliance placement now maintains inPlay UID alignment in local and online paths. Server validates actor/phase/card/revision, discards the previous alliance once, opens a per-origin five-unit loss plan and persists every manual choice/reset. Existing Golem authorization/legacy casualty handoff extended to alliance plans; unrelated snapshots cannot overwrite pending selections, Commerce proposals remain possible. Empty regions, NPC buildings, battles and decimation use unchanged legacy loss resolution.
Checks PASS: corruption-alliance-sync.test.js (replacement, one stationed plus four committed losses, independent automatic region loss, stale/actor/base rejection), alliance and Golem unit suites (13 total); check-alliances-online-browser.cjs (two browsers, first placement/replacement, single discard, five manual plus three automatic losses, partial reload, NPC fortress recovery, UID alignment), check-alliance-cards.cjs local UI regression, check-golem-online-browser.cjs regression.
Alliances can now be placed/replaced online. Corruption theft, Elf fleeing and Ogre active ability remain gated; no claim of complete extension readiness. Main/public unchanged.


## Checkpoint 42 — Corruption theft online (2026-11-09)
Shared theft module now validates target alliance identity, removes the tactic/cost5 exactly once and moves the stolen alliance to the thief hand. Server owns open/cancel/resolve; opening/cancel has no public journal entry or debit, and pauses are preserved. Ready Morcatt Haute Noblesse immune. Captured target UID revalidated. Dwarf pending harvest updated using the same helper as local play, including gains already intercepted by Embuscade; previously credited balances unchanged.
Victim owns the persisted per-origin loss selection even outside their turn. Bot victims get deterministic server-selected losses and the initiating human resolves legacy consequences, preventing a bot-input deadlock. Private target UI restores after reload and closes on canonical resolution/cancel.
Checks PASS: corruption-theft-sync.test.js (cancel/atomicity/UID/immunity/insufficient Gold/pending gain/nonactive victim/bot resolver), all server unit tests; check-corruption-online-browser.cjs two browsers (outside-turn play, cancel, private reload,5Gold,14-to4 intercepted harvest, victim5/automatic3 losses, PNJ fortress, final payout9), check-corruption-bot-online.cjs automatic completion, check-corruption-card.cjs local regression, check-alliances-online-browser.cjs regression.
Main/public unchanged. Remaining online integrations: Elf fleeing, Ogre power/cascade ownership, remaining Revolts sources and bot hero placement, followed by full release audit.


## Checkpoint 43 — Elf flight and Ogre power online (2026-11-09)
Elf destination eligibility is shared with the server, including strict matching Portal pairs. Defender choice/destination survives reload; server validates actor, revision and destination before authorizing the unchanged legacy transfer/capture/battle-stack resolution. Authorized completion uses a receipt so unrelated snapshots cannot overwrite it. Battle clocks remain suspended during the Elf choice.
Ogre die and once-per-player-turn consumption are server-owned; roll3/4 captures Revolts before battle completion. Legacy battle resolution queues adjacent land losses. Each human owner selects their affected group through the existing server-authorized loss protocol; successive owners receive the canonical state. Bots resolve losses automatically, preserving the preceding human completion receipt. Cascade handoffs retain paused Gold until completion.
Checks PASS: all57 server unit tests; check-battle-alliances-online-browser.cjs (two browsers: Elf choice/reload/invalid target/capture, Ogre roll6/once/owner loss handoff); check-battle-alliances-bot-online.cjs (same plus automatic bot loss); check-elf-flight.cjs, check-elf-nested.cjs, check-ogres.cjs, check-ogre-cascade.cjs local battle regressions; check-corruption-online-browser.cjs and check-golem-online-browser.cjs regressions; check-foundations.cjs.
Scope: Elf/Ogre integrations enabled in Corruption online preview. Nested battle/cascade coverage above is local; a complete six-player online session and tablet/audio checks still remain. Legacy Voleur/Assassin/Oracle roll capture and online bot hero placement are the next integration gates. Main/public site unchanged.


## Checkpoint 44 — Legacy rolls and bot heroes online (2026-11-09)
Enabled existing Revolts capture for the authenticated legacy actor or the current bot driver, never while applying a remote snapshot. Assassin now persists the captured roll with its resolved effect before opening Revolts, including outside the actor turn. Pending Revolts prevents premature Gold resumption. Thief and Oracle reuse their existing post-effect hooks; Oracle advances once only after mandatory losses and announcement.
Online bot driver handles instruction/selection/announcement continuation and can recover it after reload. Bot opening actions are recorded once per turn in Corruption; a newly triggered Revolts interrupts movement immediately without replaying recruitment/cards afterward. Online bots can place one hero and retain it, using the existing delayed passive lifecycle; active hero powers and return-to-hand remain disabled for bots.
Checks PASS: check-legacy-rolls-online-browser.cjs with two browsers and one bot (human Thief4, Assassin4 outside turn during Taxe Gold pause, Oracle4/double call/one turn advance; bot hero placement/dormancy/no active use; bot Thief via botAdvance blocks movement, reload restores pending notice; bot Assassin and Oracle auto-losses); check-revolts-rolls.cjs and check-revolts-oracle-bots.cjs local regression; all57 server unit tests; Noblesse, Golem and Elf/Ogre online browser regressions.
Main/public unchanged. Remaining release work: audit actual UI card entry points, complete multiplayer scenarios with six players and nested battles, reconnection/concurrent actions, then tablet/audio validation. These targeted tests do not establish a bug-free release. Legacy roll ownership still uses the existing trusted-client snapshot architecture, not a new server game engine.


## Checkpoint 45 — Real card gestures and six-client scenario (2026-11-09)
UI audit found Corruption hand activation still gated online despite its working engine hook. Enabled it for legacy online; battle hand rendering now keeps its dedicated theft action instead of replacing it with an ordinary battle tactic. Excluded Corruption from the generic pre-action recruitment/Gold wrapper so its own validated opening owns the pause context and cancel resumes Gold correctly.
Hand action gestures now reserve long press for enlargement (including locked cards); first/second click remains explanation/action. Heroes now use this explanation-first hand gesture too. Start-phase action buttons retain direct long-press activation. Zoom uses prescribed card text, not temporary alliance replacement warnings; explanation previews render line breaks as text rather than literal HTML tags. Asset cache version updated.
Checks PASS: check-corruption-card-clicks-online.cjs reproduces old UI failure then verifies real first/second click, cancel/no debit/Gold resume, reload, target button, losses and payout; check-battle-corruption-clicks-online.cjs theft during Elf choice cancels fleeing, costs5 once and leaves defender3+fortress10; check-six-card-clicks-online.cjs same harvest/Embuscade/Corruption/loss/payout scenario across six connected browser views with matching final state. check-card-gestures.cjs covers fourteen hand cards (five heroes, four alliances, Corruption, four base action cards), lens/long press/no accidental play, prescribed zoom text and hero pose/return. Alliance UI, hero lifecycle, base foundations and six-player setup regressions pass.
This is a six-client targeted scenario, not a completed six-player match. Full mixed-action matches, adverse network conditions and tablet/audio remain release checks. Main/public unchanged.


## Checkpoint 46 — Six turns, reconnect, stale packets and touch (2026-11-10)
Added a scripted six-browser match using real UI draws, five hero placements, Dragon movement and Oracle rolls through a complete round, then purchase of the winning point. The fixture starts player0 at2VP/35Gold and fixes rolls to2; it deliberately does not model an organic full mixed-action match. Actual socket disconnect/resume and page reload preserve the ongoing turn; hero passives activate next owner turn, the winner and balances agree across six views.
Reproduced a delayed old snapshot rewinding a spectator/player view to the previous turn. onlineLegacyApply now ignores lower revisions before touching UI, units, timers or sound state. Same-revision recovery remains permitted. The captured-old-packet regression fails before the fix and passes afterward. An initial uninstrumented six-turn run timed out on an Oracle button; subsequent instrumented runs passed; no causal claim that the stale-packet guard explains that initial timeout.
Touch emulation exposed synthetic compatibility clicks landing on the newly opened backdrop after a long press, closing the zoom immediately. Click suppression now lasts through the delayed compatibility click and resets on a new pointer gesture; regular hand, in-play and Commerce holds opt in. Hand lenses open on click rather than pointerup. Cache version updated. Real-device Safari/iPad audio is not validated by this emulation.
Checks PASS: check-six-turns-online.cjs; check-auction-online-browser.cjs (disconnect/reload during auction, clock, sales, Embuscade); check-tablet-gestures.cjs (820x1180/touch,14 lenses+holds, no card use, map swipe scrolls, hero controls); check-card-gestures.cjs desktop and check-battle-corruption-clicks-online.cjs; all57 server tests. Main/public unchanged. Remaining: organic mixed-action/end-to-end battle coverage, adverse network stress and real tablet/audio acceptance.


## Checkpoint 47 — Ogre/Revolts/Corruption battle chain (2026-11-10)
Added check-ogre-corruption-chain-online.cjs: two real browser views, Ogre activated through its in-play title, fixed server roll4, Revolts resolves before the battle ends, defender plays Corruption through actual hand/target buttons, attacker chooses five Ogre-region losses, bonus falls12 to8 and use stays consumed. Battle resolves through the legacy engine: defender2 removes two attacking units, six survivors conquer; adjacent land units remain3/3 because Corruption canceled the blast. No production rule change needed.
Checks PASS: new chained online scenario; check-legacy-rolls-online-browser.cjs (human/bot rolls, delayed Gold and reconnect); check-ogre-cascade.cjs (local nested battles, owner choices, one discard/loss, Gold stays paused through final owner); check-golem-gold.cjs (local Golem/Revolts/Gold, recruitment cap/reset).
Resume from branch corruption-integration, code head918a5a4b31b7bb5f9b5af9c16000d98b0b1f1f0a before this documentation-only checkpoint. Main remainsfc8ca7d12dbd4fbaab5346e550cba5b90752190b. Local browser harnesses are in work/corruption-integration; run from workspace root, sequentially (online ports8791/8792; local8795), with NODE_PATH=work/spectator-build/server/node_modules.
Next focused test: reproduce the nested Ogre cascade online (current cascade coverage is local), including ownership handoff and Gold resumption; then broader mixed-action matches. Real iPad/Safari sound remains unverified; headless Chromium touch tests are not audio acceptance. Do not publish or merge main on the strength of these targeted tests alone.
