# First Wake — Dialogue and State Migration Matrix (2026-10-27)

**Status: planning / source-verified legacy inventory, Godot port not executed.**
**Baseline examined:** `main:modules/first-wake-opening.js` legacy version 0.1.0, blob `37d59c4a6329a14535db21a89d43d6950a5ff74a`. Main still contains `SCENES[6].joinCharacterId === 'lyra'` and a validator rejecting Ionia in the early party. This is **historical code authority**, NOT permission to change the JS runtime; Godot 4.7.2/GDScript is the forward engine.

## Existing-to-new line map
| Old scene ID / example | Keep / rewrite / move | New destination |
|---|---|---|
| `arrival_horizon` — “Dawn gathers beneath a sea of clouds.” | KEEP scenic intent; revise ship description as still grounded, not already levitating. | FW-00 flyer / job search; introduce work and docks before hero ship |
| `ender_arrives` — “You said you could fix things.” | REWRITE as opening interview; preserve mutual respect and “honest uncertainty” sentiment. | FW-01 captain / provisional contract, Ionia first join |
| `dock_walk` — “Closed-route marks crowd the dock board.” | RETAIN optional atmospheric board, remove as primary mystery; player navigates to posted flyer and ship. | FW-00 and FW-01 |
| `berth_task` — heat-leaking berth / listing desk | SPLIT: early practical repair introduces limited spaces; completed living space after splashdown. | FW-02 and FW-11 |
| `talen_staying` — “Are you staying here now?” / model Wake | MOVE intact emotional function and block artwork; no Talen presence on risky maiden test flight. | FW-08 reunion / FW-11 home |
| `lyra_family` — “Galley lit again.” | MOVE domestic introduction to after splashdown; retain warm/dry humor with expanded personal agency. | FW-08 |
| `lyra_join` — “...Did you hear that?” / “But yes.” | MOVE motif to the joint investigation; event switches from initial join to post-splashdown Lyra recruitment, with dialogue gated on meeting her. | FW-08 and FW-09 |
| `ionia_practical` — “Wakeheart load just moved twelve percent.” | REWORK as Ionia/Ender preflight instrumentation and later postflight analysis. Keep the home-life practical concern. | FW-02, FW-05, FW-09 |
| `core_walk` — galley, conduit, stormlight | SPLIT preflight engine tour and later free-roam post-splashdown clue collection; never use old old party composition. | FW-02, FW-09 |
| `first_wake_card` — “AETHERWAKE / CHAPTER I — FIRST WAKE” | UPDATE displayed game title and anchor chapter card to first takeoff, subject to creator cinematic timing approval. Remove omniscient “crew becoming legible” reveal before the party forms. | FW-04 first flight |

## Pre-migration party state invariants
- Persistent roster identity and order remain: `ender | lyra | ionia | reson | aepex` (no schema reorder). Only *recruitment timing* changes.
- Before hiring: active party `[ender]`.
- On Ionia job offer acceptance: `[ender, ionia]` even if Ionia's production combat kit is unimplemented. Story-active never grants nonexistent magic or combat formulas.
- Until safe post-splashdown meeting: Lyra is *not* in the active party. Talen is NPC/non-playable.
- After Lyra recruitment: `[ender, ionia, lyra]` (storage order vs UI order and stable roster IDs separately verified).
- On reload/return: no duplicate join event or doubled rewards. Refusal/abort of unsafe engineering controls cannot progress the flight sequence.
- No changes to Reson/Aepex's later authored recruitment and no fake placeholder spell or skill grants.

## Expanded family dialogue candidates (post-splashdown, not yet accepted)
**The safe-reunion location remains an open design decision.** The following exchanges work at shore, sheltered dock or after waterborne recovery; physical placement must be chosen before implementation.

### Lyra and Ionia — the family under the ship
- LYRA: “You have spent nearly every day this year trying to bring her back. I need to know you're going to be there when the repairs are over.”
- IONIA: “I came back, didn't I?”
- LYRA: “On water.”
- IONIA: “She's always been good on water.”
- LYRA: “I know. Talen's already asking when he can put his things back in his corner.”
- IONIA: “When I can promise it's safe. That's not negotiable.”
- LYRA: “I wouldn't ask you to promise what you don't know. I am asking to be part of finding out.”
- IONIA: “Then help us figure out what she's telling us.”

### Lyra and Ender — beyond useful
- LYRA: “Ionia says you spotted the phase problem before she lost control.”
- ENDER: “I spotted that something was wrong. Those aren't quite the same.”
- LYRA: “Good distinction.”
- ENDER: “She gave me a job anyway.”
- LYRA: “She needed an engineer, not a person who pretends every problem comes with instructions.”
- ENDER: “I'm very good with instructions.”
- LYRA: “Then you may find the Wake a little challenging.”
- ENDER: “I've gathered that.”
- LYRA: “And for the record, I'm helping because I want this ship flying again, too. Not just because I'm Ionia's cousin.”

### Talen and the unfinished home
- TALEN: “Did the sea make the wings wet?”
- ENDER: “Very wet.”
- TALEN: “Do we have to dry them with towels?”
- ENDER: “I sincerely hope not. That would be a lot of towels.”
- TALEN: “I have one.”
- ENDER: “Then we're one towel closer.”
- LYRA: “Talen, you can show him the block ship after we finish unloading.”
- TALEN: “Mine has a bigger table. Because you said we need a table.”
- LYRA: “I said we need somewhere we can all sit.”
- TALEN: “That's what the table is for.”
*No Talen magical interpretation or predictive mechanism.*

### Ionia's quiet Denith recollection (optional)
- IONIA: “He taught me everything he could while we were flying. We always assumed there would be another overhaul.”
- ENDER: “Was there?”
- IONIA: “Not one where he was well enough to explain all of this. After he died, I had ten years of notes and no one to ask what the blank spaces meant.”
- ENDER: “Then we'll mark the spaces as unknown. We shouldn't mistake them for answers.”
- IONIA: “Denith would have approved of that.”
*This is newly authored dialogue, not verbatim historical speech or proof Denith intentionally concealed engineering secrets.*

## Integration checklist
1. Locate live `godot` Chapter I opening/dialogue/party files on the selected native branch, inspect identifiers and baseline SHA; rebase only after verifying dependency ancestry. Do not patch legacy JS.
2. Author mapping for all in-game lines actually displayed, not just early `SCENES` mirror. Confirm no outdated Lyra-first cinematic or quest hint remains reachable.
3. Migrate Ionia-first joins and Lyra-after-splashdown with explicit state transition and save migration; preserve known NPC/spoiler/child protections.
4. Add engineering mini-task, helm/engineering switching, real sea-state landing and a safe meeting-location transition. “Seaworthy” needs real water interaction evidence, not land touchdown test reuse.
5. Revalidate every playable/end-state route, optional talk branch, combat authority, clue order, subtitle, text-wrap/localization, reduced-motion mode, story replay and creator visual QA.
6. Record native 4.7.2 source/capture proof before describing gameplay as implemented. Keep known Windows installer security hold separate; no auto-merge or release.

## Authority/source
- [New Chapter I reboard](FIRST_WAKE_REVISED_OPENING_STORYBOARD_2026-10-27.md)
- [New candidate dialogue](FIRST_WAKE_REVISED_OPENING_DIALOGUE_2026-10-27.md)
- [Legacy runtime mirror on main](https://github.com/ndrorchestration/ToSailtheStarrySky-jrpg/blob/main/modules/first-wake-opening.js)
- [Old First Wake storyboard](https://app.notion.com/p/3e2f5bad238b81c99b51cfbce1bba583)
- [Canon/party/recruitment record](https://app.notion.com/p/3e0f5bad238b812bac52c594d1465c29)
