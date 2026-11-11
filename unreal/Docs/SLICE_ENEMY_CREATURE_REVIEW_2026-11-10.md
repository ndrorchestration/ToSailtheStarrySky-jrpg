# TSTSS Unreal 3D slice enemy roster — initial implementation

**Status:** SOURCE IMPLEMENTED / DRAFT / NATIVE UBT/UHT BLOCKED BY ACTIVE LIVE CODING / VISUAL QA NOT TESTED / STORY PLACEMENT NOT APPROVED / NO MERGE.
**Engine:** Unreal Engine 5.8 project (UE 5.8.4 Windows validation required).
**Source of truth for current proposed review numbers:** `Public/Enemies/TSTSSSliceEnemyCatalog.h` and `Private/Enemies/TSTSSSliceEnemyCatalog.cpp`.
**Baseline:** main `f4e44544c3c7d7803a964cd1c9435dab8a8aff16`.

## Scope and lore
The existing historical `windShear` / **Harmonic Shear Elemental** is a known preexisting concept, but its *placement* in the revised Ender → Ionia → First Wake → sea landing → Lyra sequence is unresolved. The `aetherLeak` hazard ID is also a historical concept; its **Wisp** embodiment is a new provisional visual interpretation. **Dock Skitter** is an entirely new review-only enemy concept, not accepted canon. No protagonist gains a spell, no story beat or reward is added, and neither the historical Godot nor browser battle system is imported.

| Review archetype | Archetype ID | HP | Resource | ATK | DEF | AGI | Review skills |
|---|---|---:|---:|---:|---:|---:|---|
| Harmonic Shear Elemental | windShear | 14 | 6 | 2 | 1 | 13 | Gale Force (power 2/cost 0), Shear Cut (power 3/cost 2/cooldown 1) |
| Aether Leak Wisp — proposed form | aetherLeak | 10 | 8 | 1 | 0 | 17 | Wisp Spark (power 1/cost 0), Wisp Surge (power 3/cost 3/cooldown 2) |
| Dock Skitter — proposed species | dockSkitterReview | 20 | 4 | 3 | 2 | 8 | Snap (power 2/cost 0), Lunge (power 4/cost 2/cooldown 2) |

These are balance **placeholders**, not final difficulty, canon stats or player-facing grants. All powers use the existing generic attack formula and resource pool. The historical Gale Force knockback effect is **not implemented** by these rows: the current turn system cannot resolve knockback. Animation/VFX cue names are metadata only, not Niagara, Control Rig, sound, collisions or hit detection.

## Implemented technical boundaries
- `ATSTSSSliceEnemyActor` provides three distinct 3D engine-primitive silhouettes, contrasting accent points, light, editor-visible labels and inexpensive idle motion. Reduced-motion mode removes bobbing and turn oscillation. No imported/final skeletal meshes, materials or cinematic capture is claimed.
- `FTSTSSSliceEnemyCatalog::TryMakeReviewParticipant` supplies enemy combatants to **the existing** `UTSS_CombatTurnManager`. It validates instance identities, never gives them a player faction, and creates no encounter autonomously.
- `MakeReviewSkillTable(Outer)` defaults every one of six skill rows to `DesignOnly`. Only an explicit `MakeReviewSkillTable(Outer, true)` for a **non-shipping isolated review** marks the rows `ReviewExecutable`. This does not alter existing protagonist knowledge, battle math, skill admission or shipping game data.
- Shipping builds deny review participant construction and review-table creation, and hide any accidentally placed review actor.
- Two Editor automation tests cover registry uniqueness, exact HP/ability projection, invalid/impersonated IDs, design-only refusal through the actual manager, and one explicitly opted-in accepted enemy turn. They have **not run** at this new head.

## Native authoring / inspection path
1. In a **disposable** Unreal 5.8.4 review map, place three `TSTSSSliceEnemyActor` C++ actors; choose a different `Kind` and `InstanceId` for each (e.g. `Shear_01`, `Wisp_01`, `Skitter_01`). These are constructed from built-in static meshes when an actor is placed. The connected Neontic workstation was offline when this source increment was authored, so no `.umap` or `.uasset` was generated.
2. For mechanical isolated tests only, construct an explicit player roster and selected party members, call `TryMakeReviewParticipant` for enemies, set the manager's `SkillTable` to a table with explicitly reviewed admission, then call `InitializeEncounter`. Merely placing actors **does not start a fight**. For any true player battle, use the project's battle UI and existing skill/party authorization rather than coupling visuals to button presses.
3. Use the project's unchanged `Tools/Verify-Unreal.ps1` on a clean exact-head isolated checkout with available UE Editor toolchain. Inspect C++/UHT build, the two named new tests, all old tests and tracked-file cleanliness. Do not edit tracked Engine/Input INIs to satisfy the run.
4. Capture native Editor viewport or PIE front/side/three-quarter silhouettes, depth/scale against Ender and the Aureate Wake, reduced-motion parity, color/material parameter readback, shader and light behavior, frame timing, and visibility/readability before any production approval.

## Explicit unresolved tasks
- Connect authored 3D skeletal creature meshes, authored materials, Niagara, montages, sound cues and real combat resolution visuals; current shapes are **geometric review proxies**.
- Test the new C++ source with native UBT/UHT; static-source review cannot certify compilation.
- Make an isolated editor map and a player-command-selectable battle, then native PIE/replay/negative QA. No such map or flow is claimed here.
- Approve encounter placement and whether each archetype belongs in the revised story, and reconcile old JS/Godot stats/labels without silently turning historical prototypes into canon.
- Check performance, lighting, camera blocking, colorblind-readable attacks, and reduced-motion presentation before raising visual quality status.

**Do not merge from a source-only result.** All production, creative, placement, native-validation and release gates remain separate.

## Windows source-locked attempt, November 10, 2026
On the isolated clean checkout `C:\\Users\\Admin\\work\\TSTSS-Slice-Enemies-20261110`, exact commit `ece4aa6b6b5920a5f976bcec2b2e7875f35d3214`, UnrealBuildTool started, but returned **exit code 6** with `Unable to build while Live Coding is active`. A separate Unreal Editor and LiveCodingConsole were subsequently observed on the workstation, so these sessions were not terminated or bypassed. This is a **BLOCKED build**, not native success and not evidence of a C++ compile defect. The checkout remained clean. The two tracked INI files' original read-only attributes were restored after the attempt. All native automation and visual QA remain untested; retry at the final PR head only when the machine is idle.

## Optional enemy-turn AI
`UTSTSSSliceEnemyReviewAI::TryActReviewEnemy` is a BlueprintCallable non-shipping helper. It checks exact instance/archetype state, chooses the lowest-HP living canonical protagonist (stable lexical tie-break), attempts the stronger attack, then a free basic action when denied or under-resourced. Every action goes through `UTSS_CombatTurnManager::SubmitCommand`—including skill admission, learned membership, cooldown, faction targeting and atomic HP effects. It cannot autonomously create encounters, grant player actions or mutate saves. A third native Editor test covers denial, archetype spoofing, stronger attack, turn ownership and resource fallback. **These are implementation/test definitions, not native pass claims.**
