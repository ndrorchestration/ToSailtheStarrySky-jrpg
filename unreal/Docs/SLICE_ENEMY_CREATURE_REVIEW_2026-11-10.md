# TSTSS Unreal 3D enemy roster — 15 review archetypes

**Current status:** 15 ARCHETYPES SOURCE-IMPLEMENTED / 30 DAMAGE-ONLY REVIEW ACTIONS / NATIVE UBT-UHT NOT VERIFIED (DISK BELOW GATE) / NO GALLERY MAP / VISUAL QA NOT TESTED / CANON PLACEMENT NOT APPROVED / DRAFT NO MERGE. Earlier native attempt was blocked by Live Coding; see historical receipt below.
**Engine:** Unreal Engine 5.8 project (UE 5.8.4 Windows validation required).
**Source of truth for current proposed review numbers:** `Public/Enemies/TSTSSSliceEnemyCatalog.h` and `Private/Enemies/TSTSSSliceEnemyCatalog.cpp`.
**Baseline:** main `f4e44544c3c7d7803a964cd1c9435dab8a8aff16`.

## Scope and lore
The existing historical `windShear` / **Harmonic Shear Elemental** is a known preexisting concept, but its *placement* in the revised Ender → Ionia → First Wake → sea landing → Lyra sequence is unresolved. The `aetherLeak` hazard ID is also a historical concept; its **Wisp** embodiment is a new provisional visual interpretation. **Dock Skitter** is an entirely new review-only enemy concept, not accepted canon. No protagonist gains a spell, no story beat or reward is added, and neither the historical Godot nor browser battle system is imported.

### Historical first three (retained as baseline)

| Review archetype | Archetype ID | HP | Resource | ATK | DEF | AGI | Review skills |
|---|---|---:|---:|---:|---:|---:|---|
| Harmonic Shear Elemental | windShear | 14 | 6 | 2 | 1 | 13 | Gale Force (power 2/cost 0), Shear Cut (power 3/cost 2/cooldown 1) |
| Aether Leak Wisp — proposed form | aetherLeak | 10 | 8 | 1 | 0 | 17 | Wisp Spark (power 1/cost 0), Wisp Surge (power 3/cost 3/cooldown 2) |
| Dock Skitter — proposed species | dockSkitterReview | 20 | 4 | 3 | 2 | 8 | Snap (power 2/cost 0), Lunge (power 4/cost 2/cooldown 2) |

These are balance **placeholders**, not final difficulty, canon stats or player-facing grants. All powers use the existing generic attack formula and resource pool. The historical Gale Force knockback effect is **not implemented** by these rows: the current turn system cannot resolve knockback. Animation/VFX cue names are metadata only, not Niagara, Control Rig, sound, collisions or hit detection.

### Expanded review balance snapshot (provisional)

These values mirror the C++ catalog at the expansion commit, but **C++ remains authoritative**. Named skills are damage-only single-target attacks; a thematic word does not implement an actual buff, status effect, poison, crowd control, or environmental behavior.

| Enemy | HP | Resource | ATK | DEF | AGI | Basic attack | Strong attack |
|---|---:|---:|---:|---:|---:|---|---|
| Quayside Cutpurse | 22 | 4 | 4 | 1 | 15 | Slash | Backstab |
| Quayside Slinger | 18 | 6 | 3 | 1 | 14 | Shot | Volley |
| Bandit Captain (leader) | 44 | 10 | 6 | 3 | 12 | Strike | Heavy Blow |
| Thornvine Creeper | 26 | 6 | 4 | 2 | 6 | Vine Lash | Thorn Burst |
| Sporecap Stalker | 19 | 9 | 2 | 1 | 9 | Spore Tap | Bloom Pulse |
| Root Sentinel | 48 | 7 | 5 | 5 | 4 | Root Bash | Bark Crush |
| Reef Eel | 20 | 9 | 3 | 0 | 18 | Tail Whip | Surge Bite |
| Tidefin Hunter | 30 | 6 | 5 | 2 | 15 | Fin Rake | Tide Lunge |
| Shellback Crab | 38 | 5 | 4 | 6 | 5 | Pincer Snap | Shell Slam |
| Cliff Lynx | 24 | 6 | 5 | 1 | 18 | Claw | Pounce |
| Bristleboar | 40 | 6 | 5 | 4 | 7 | Tusk | Charge |
| Night Glider | 17 | 10 | 3 | 0 | 20 | Wing Cut | Dive |

The bandits use different silhouettes for light melee, slinger, and high-health commander. Flora includes vine, mushroom, and rooted canopy forms. Aquatic species use eel, finned hunter, and crab-like carapace structures. The fauna set includes two terrestrial mammals and one flying/gliding animal. No biological taxonomy or habitat placement is canon-locked.

## Implemented technical boundaries
- `ATSTSSSliceEnemyActor` provides fifteen distinct provisional 3D engine-primitive silhouettes, contrasting accent points, light, editor-visible labels and inexpensive idle motion. Reduced-motion mode removes bobbing and turn oscillation. No imported/final skeletal meshes, materials or cinematic capture is claimed.
- `FTSTSSSliceEnemyCatalog::TryMakeReviewParticipant` supplies enemy combatants to **the existing** `UTSS_CombatTurnManager`. It validates instance identities, never gives them a player faction, and creates no encounter autonomously.
- `MakeReviewSkillTable(Outer)` defaults all thirty skill rows to `DesignOnly`. Only an explicit `MakeReviewSkillTable(Outer, true)` for a **non-shipping isolated review** marks the rows `ReviewExecutable`. This does not alter existing protagonist knowledge, battle math, skill admission or shipping game data.
- Shipping builds deny review participant construction and review-table creation, and hide any accidentally placed review actor.
- Three Editor automation tests cover registry uniqueness, exact HP/ability projection, invalid/impersonated IDs, design-only refusal through the actual manager, and one explicitly opted-in accepted enemy turn. They have **not run** at this new head.

## Native authoring / inspection path
1. In a **disposable** Unreal 5.8.4 review map, stage fifteen distinct `TSTSSSliceEnemyActor` C++ actors in the isolated gallery; each requires a unique `Kind` and `InstanceId`. The source gallery generator defines the five-by-three layout. These are constructed from built-in static meshes when an actor is placed. An earlier connection failure is historical; the current workstation is online, but the generated `.umap` remains absent because native verification is blocked by disk availability.
2. For mechanical isolated tests only, construct an explicit player roster and selected party members, call `TryMakeReviewParticipant` for enemies, set the manager's `SkillTable` to a table with explicitly reviewed admission, then call `InitializeEncounter`. Merely placing actors **does not start a fight**. For any true player battle, use the project's battle UI and existing skill/party authorization rather than coupling visuals to button presses.
3. Use the project's unchanged `Tools/Verify-Unreal.ps1` on a clean exact-head isolated checkout with available UE Editor toolchain. Inspect C++/UHT build, the three named enemy-native tests, all other registered tests and tracked-file cleanliness. Do not edit tracked Engine/Input INIs to satisfy the run.
4. Capture native Editor viewport or PIE front/side/three-quarter silhouettes, depth/scale against Ender and the Aureate Wake, reduced-motion parity, color/material parameter readback, shader and light behavior, frame timing, and visibility/readability before any production approval.

## Explicit unresolved tasks
- Connect authored 3D skeletal creature meshes, authored materials, Niagara, montages, sound cues and real combat resolution visuals; current shapes are **geometric review proxies**.
- Test the new C++ source with native UBT/UHT; static-source review cannot certify compilation.
- Make an isolated editor map and a player-command-selectable battle, then native PIE/replay/negative QA. No native gallery map or playable battle flow is claimed here.
- Approve encounter placement and whether each archetype belongs in the revised story, and reconcile old JS/Godot stats/labels without silently turning historical prototypes into canon.
- Check performance, lighting, camera blocking, colorblind-readable attacks, and reduced-motion presentation before raising visual quality status.

**Do not merge from a source-only result.** All production, creative, placement, native-validation and release gates remain separate.

## Windows source-locked attempt, November 10, 2026
On the isolated clean checkout `C:\\Users\\Admin\\work\\TSTSS-Slice-Enemies-20261110`, exact commit `ece4aa6b6b5920a5f976bcec2b2e7875f35d3214`, UnrealBuildTool started, but returned **exit code 6** with `Unable to build while Live Coding is active`. A separate Unreal Editor and LiveCodingConsole were subsequently observed on the workstation, so these sessions were not terminated or bypassed. This is a **BLOCKED build**, not native success and not evidence of a C++ compile defect. The checkout remained clean. The two tracked INI files' original read-only attributes were restored after the attempt. All native automation and visual QA remain untested; retry at the final PR head only when the machine is idle.

## Optional enemy-turn AI
`UTSTSSSliceEnemyReviewAI::TryActReviewEnemy` is a BlueprintCallable non-shipping helper. It checks exact instance/archetype state, chooses the lowest-HP living canonical protagonist (stable lexical tie-break), attempts the stronger attack, then a free basic action when denied or under-resourced. Every action goes through `UTSS_CombatTurnManager::SubmitCommand`—including skill admission, learned membership, cooldown, faction targeting and atomic HP effects. It cannot autonomously create encounters, grant player actions or mutate saves. A third native Editor test covers denial, archetype spoofing, stronger attack, turn ownership and resource fallback. **These are implementation/test definitions, not native pass claims.**

## Phase 2 — source-controlled Unreal enemy gallery authoring

Added `Tools/tstss_slice_enemy_gallery.py`, the explicit Editor runner
`Tools/run_tstss_slice_enemy_gallery.py`, and portable negative tests.
A *new* review map at `/Game/TSTSS/Review/SliceEnemyGallery_V0` is staged
only when the **actual UE 5.8.4 C++ module** has compiled and the disposable
`TSTSS-Slice-Enemies-20261110` worktree has the exact pinned clean head.

The script creates exactly three source-backed actors, neutral plinths,
separate readable captions, a neutral stage, a camera, and key/fill lights.
An explicit `RefreshReviewGeometry` C++ BlueprintCallable function ensures
that changing a kind in Editor Python regenerates the corresponding silhouette
rather than displaying the default vortex three times. The gallery **does
not** add the actors to First Wake, create actual enemy encounters, add
SaveGame records or edit a canonical map.

Portable plan/tests passing is not a generated `.umap`, not rendered 3D,
not a native test PASS, and not approval of art/lore/balance. The map remains
unmaterialized until the machine's separate Live Coding Editor session ends
and a new source-locked native build succeeds. Generated map is intentionally
untracked review evidence until inspected; do not add to main.

## Source-locked gallery admission launcher

Run the **source-only** plan checks with
`python unreal/Tools/tstss_slice_enemy_gallery.py --validate` and
`python -m unittest discover -s unreal/Tools -p test_tstss_slice_enemy_gallery.py -v`.
The runner and portable tests are also registered in the Unreal source-preflight
CI workflow, without falsely labeling source checks as UE gameplay proof.

To build **only after another Editor/Live Coding session has stopped**, use an
exact-head clean native Editor build receipt from `Verify-Unreal.ps1 -SkipTests`
and then `Invoke-SliceEnemyGalleryReview.ps1 -EngineRoot
'C:\Program Files\Epic Games\UE_5.8' -ExpectedHead '<full SHA>'`.
The launcher refuses foreign worktrees, changed HEADs, dirty source, existing
map, active Unreal Editor, insufficient RAM/disk, wrong UE patch, or missing
native build receipt before starting. It makes both tracked default INIs
temporarily read-only, restores attributes, and validates the new map SHA receipt.
Do not perform this launch in any other worktree.

## Provisional expanded wildlife and hostile humans — November 10, 2026

The original three remain preserved. Twelve *additional* archetypes are implemented as native C++ descriptor entries, each with two `SliceReview_` actions and eight procedural Unreal Engine primitive parts. The review roster now totals **15** and the strict enemy-only DataTable has **30** rows. No new persistent game assets were imported or canonized.

| Enemy family | Review members | Gameplay distinction |
|---|---|---|
| Bandits | Quayside Cutpurse, Quayside Slinger, Bandit Captain | agile melee, ranged-style attack, durable leader |
| Flora | Thornvine Creeper, Sporecap Stalker, Root Sentinel | constricting-looking plant, mobile mushroom, high-defense rooted guard |
| Aquatic | Reef Eel, Tidefin Hunter, Shellback Crab | high initiative swimmer, fast predator, heavy shell defense |
| Fauna | Cliff Lynx, Bristleboar, Night Glider | quick mammal, charging heavy mammal, evasive glider |

Each archetype has HP, resource, attack, defense, agility, family, proposed habitat and exactly two ability definitions. `BanditCaptain` is the only `bLeader=true` entry. The habitats are **ideas**, not Chapter I placements. Names and models are editable proxies pending worldbuilding approval. The existing mechanic currently processes all 30 actions as damage-style `JobArt` skills; *poison, spores, roots, currents, intimidation, ranged projectiles, team buffs, area damage, summoning, knockback and status effects are not implemented*. Actions do not confer a class/spell on party members.

`tstss_slice_enemy_gallery.py` now authors five gallery aisles, three enemies in each, with per-family review cameras, floor stages, labels, and low-resource point/directional lighting. It remains opt-in and still refuses dirty or foreign workspaces, overwrites, missing native build evidence, or an active editor session.

**Native build hold:** On Neontic the free disk measurement was roughly **9.09 GiB**, below the existing **14 GiB** gate, so no native build/gallery authoring will be attempted until resources recover; do not weaken the gate or delete another worker's files.

## Neutral encounter recipe bank (C++ source only)

Eight two-enemy encounter compositions can now be instantiated as detached roster data through `FTSTSSSliceEnemyCatalog::TryMakeReviewWave`. These are neutral **test fixtures**, not level spawns or creator-approved Chapter I encounters.

| Preset ID | Review-only opponents |
|---|---|
| `Review_HarborBanditPatrol` | Cutpurse + Slinger |
| `Review_HarborBanditCaptain` | Bandit Captain + Cutpurse |
| `Review_WoodlandSporeline` | Thornvine + Sporecap |
| `Review_WoodlandSentinel` | Root Sentinel + Thornvine |
| `Review_CoastalHunters` | Reef Eel + Tidefin Hunter |
| `Review_CoastalShellbacks` | Shellback Crab + Reef Eel |
| `Review_HighlandStalkers` | Cliff Lynx + Night Glider |
| `Review_HighlandBristle` | Bristleboar + Cliff Lynx |

Unknown preset IDs fail without changing output. Shipping builds deny this API. Callers must separately authorize the current player roster, encounter initialization, and skill admission in the existing combat turn manager. No quest, reward, SaveGame, world placement, faction override or player spell grant is introduced. The eight-preset positive and negative validation assertions live in the already-registered enemy catalog native automation and passed within the 32-test native UE automation suite at historical gallery commit `dc79a9dd6164f2ae631c1bd6ee051ea7a6f5c0c7`; the new battle console requires its own fresh exact-head verification.

## Phase 3 — opt-in playable enemy combat review bench

- New non-shipping `UTSTSSSliceEnemyReviewSession` orchestrates **the authoritative existing** `UTSS_CombatTurnManager`, `FTSTSSSliceEnemyCatalog::TryMakeReviewWave`, and `UTSTSSSliceEnemyReviewAI::TryActReviewEnemy`. It does not calculate damage independently, create SaveGames, alter First Wake, or grant production skills.
- The reviewer selects one of three **isolated scenario stages**: Ender only (F7), Ender and already-recruited Ionia (F8), and **explicitly after splashdown** Ender/Ionia/Lyra (F9). Stage selection is not a story advancement event; Reson and Aepex remain unavailable.
- Press J or K while the active turn belongs to a player to submit a temporary, non-shipping `SliceReview_PlayerStrike` at review enemy slot 1/2. This one synthetic sandbox-only row is added to a transient local table alongside the 30 catalog enemy rows. A player's attempts to use enemy-only abilities are denied by the existing learned-skill authority. Enemy turns use the already-tested AI adapter and manager, not a parallel resolver.
- `ATSTSSSliceEnemyReviewBattleConsole` is a 3D Unreal actor with a camera, world instruction sign, keyboard input and transient debug status overlay. It remains inactive unless explicitly placed in **a separate review map** and a scenario is started; shipping disables it.
- `unreal/Tools/tstss_slice_enemy_combat_sandbox.py` stages a new `/Game/TSTSS/Review/SliceEnemyCombatSandbox_V1` by loading the hashed native-verified original gallery map and adding **one** console actor, then saving under a *different* package path. The original gallery `.umap` SHA must remain unchanged. The generator refuses changed Git HEAD, dirty source, foreign worktrees, target overwrites and missing C++ actor class; the guarded launcher also requires UE 5.8.4, an exact native build receipt and sufficient resources.
- **Current evidence:** source-only staging plan and negative tests exist, but no generated V1 map, PIE interaction, D3D12 render capture, input simulation or cinematic art approval is claimed until separately executed. Historical original gallery passed native map and 32 automation checks at commit `dc79a9d...`, not at this new console head.
