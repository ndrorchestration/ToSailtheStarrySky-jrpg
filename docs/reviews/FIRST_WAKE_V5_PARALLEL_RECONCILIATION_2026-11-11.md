# First Wake V5 — parallel work and dependency reconciliation (2026-11-11)

> Scope: current isolated review branch `review/ue58-opening-and-dock-rescue-20261111`, exact verified playable commit `f44b2bb1296cca888235433bd2adbf84f825e287`. This file is a **planning and source evidence record**, not a production merge, canon art approval, or integrated executable acceptance.

## What was actually demonstrated

V5's title map opens a real playable review map under `TSTSSGameMode` on Windows UE5.8.4/D3D11. Live W traverses the map, E on the first flyer marker advances `Find Ionia's flyer` to `Speak with Captain Ionia`, and walking off the review floor triggers `TSTSS_REVIEW_FALL_RETURN ... story_unchanged=1`. Native Editor build PASS at `31eb52266b719cfd968df15330029b5190d71a95`; 2 native `TSTSS.FirstWake.Review*` automation tests PASS at `53e2aff54b2f78e9f1aad1deeeaf22361d91f32e`; 63 focused source tests PASS before the last UI handoff fix and the focused input tests PASS afterward. Source code has not been merged into main. Full input/objective/fall evidence: [native playable report](FIRST_WAKE_V5_NATIVE_PLAYABILITY_EVIDENCE_2026-11-11.md). Neither the 7-stop prelude nor the 6-map story loop has been completed.

The V5 .umap has SHA256 `ff2b5c1423a370c4ac318b9b241088d8f20fec5eee993c998c2a5ed335cbb299`. The original V2 .umap SHA256 `4c96f1fb28fe4af91b879977e473c20de32bd933f741a5384bb8403a00254b80` is unchanged. V3 and V4 are deliberately retained as bad-look experiments with screenshots; they must not become gameplay or visual authority.

## Reconciliation order and ownership

| Workstream | Existing work | Admission into V5 | Potential conflict |
| --- | --- | --- | --- |
| Gameplay convergence | [#799](https://github.com/ndrorchestration/ToSailtheStarrySky-jrpg/pull/799), [#813](https://github.com/ndrorchestration/ToSailtheStarrySky-jrpg/pull/813) | **First**: select a source owner, compare against exact V5 behavior, compose only on disposable branch | `TSTSSExplorerCharacter`, input and menus, state/route tests |
| Six maps, scene travel | [#794](https://github.com/ndrorchestration/ToSailtheStarrySky-jrpg/pull/794), [#814](https://github.com/ndrorchestration/ToSailtheStarrySky-jrpg/pull/814) | Map assets and topology can be reused; test K gate and preserved state in each native map | overlay/world boundary and route-session ownership |
| Ionia → Lyra story | [#808](https://github.com/ndrorchestration/ToSailtheStarrySky-jrpg/pull/808) | Mandatory explicit post-physical-splashdown Lyra recruitment, no auto equip | roster/recruitment and equipment ownership |
| PBR/coastal art | [#801](https://github.com/ndrorchestration/ToSailtheStarrySky-jrpg/pull/801), [#807](https://github.com/ndrorchestration/ToSailtheStarrySky-jrpg/pull/807) | Reuse materials/layout after actual map/scale/collision A/B; GPU images from other World are not V5 evidence | material palettes, exposure, shoreline collision |
| Lighting/weather | [#796](https://github.com/ndrorchestration/ToSailtheStarrySky-jrpg/pull/796), [#798](https://github.com/ndrorchestration/ToSailtheStarrySky-jrpg/pull/798) | One sun/sky/fog/weather owner; preserve V5 illumination lessons, do not copy 1,500-lux as final balance | dynamic sun, SkyLight, exposure, fog, post-process |
| Audio/music | [#804](https://github.com/ndrorchestration/ToSailtheStarrySky-jrpg/pull/804) | Event names and QA sounds reusable; audible native integration and rights/mix still missing | audio subsystem, milestone actor, atmosphere owner |
| Optical presentation | [#815](https://github.com/ndrorchestration/ToSailtheStarrySky-jrpg/pull/815), [#811](https://github.com/ndrorchestration/ToSailtheStarrySky-jrpg/pull/811) | Camera receiver needs one explicit owner and native lens comparison; V5 already independently fixed positional Rotator bug | `Build.cs` CinematicCamera, controller/focus/PP arbitration |
| Ender pawn appearance | [#812](https://github.com/ndrorchestration/ToSailtheStarrySky-jrpg/pull/812) | Opt-in visual bridge only after creator-authorized art/rig/attachment QA | same `ExplorerCharacter` pawn touched by #814/#815 |
| Party equipment & menu | [#793](https://github.com/ndrorchestration/ToSailtheStarrySky-jrpg/pull/793) | Ender and Ionia start; Lyra only after gate, preserve V5 WASD/E/J and save/Continue keys | `DefaultInput.ini`, pawn, equipment interface |
| Spells, combat, enemies | [#810](https://github.com/ndrorchestration/ToSailtheStarrySky-jrpg/pull/810), [#791](https://github.com/ndrorchestration/ToSailtheStarrySky-jrpg/pull/791) | Centering and Resonant Pulse first; actual player-cast/MP/rounds and optional battle scene must be witnessed | skill/combat turn manager, sound, scene transition |

## Dependency reconciliation (no installers)

The checked-in `unreal/ToSailTheStarrySky.uproject`, `ToSailTheStarrySky.Build.cs`, `unreal/Tools/dependency_baseline.json`, and `first_wake_dependency_contract.json` currently agree on Unreal association **5.8**, workstation **5.8.4**, enabled **PythonScriptPlugin**, and public runtime modules Core, CoreUObject, Engine, InputCore, UMG, MediaAssets, SlateCore and AudioMixer. No extra plugin or package install was needed for the verified V5 route. Keep these exact declarations under their existing fail-closed drift test.

The **CinematicCamera** module used by optional #815 camera implementation is a *future proposed native dependency*, not a currently admitted module in V5; updating `Build.cs` or the strict dependency contract before adopting and testing #815 would produce false authority. No npm/NW.js, Daz, SpriteCook or music-license installation is authorized by this audit.

There are distinct **logical** dependencies: P0 map availability requires the corresponding 3D assets and safe collision; narrative travel requires Ionia + inspections and observed sea state; Lyra requires post-splashdown recruitment; environment/weather must have one director; focus must not override the gameplay camera/PP or readability; audio must not advance the authoritative story; equipment and spells must respect unlocked party/jobs. These dependencies are recorded in [machine-readable review frontier](../../unreal/DataSource/Integration/FirstWakeV5DependencyFrontier.review.json).

## Checks and blockers

- From the GitHub compare against current main at review time, the V5 branch is **150 commits ahead and 2 behind**, with **diverged** ancestry. The provider comparison supplied only its first 300 changed files: this is NOT an exhaustive all-file conflict calculation. Reported changed filenames from open PRs show direct `ExplorerCharacter.cpp` overlap for #812/#814/#815 and input/config overlap for #793; review file-level diff manually at exact heads before integration.
- A large existing #799/#813 convergence lineage already combines multiple workstreams, so do not cherry-pick #804/#810/#808 blindly and duplicate their source. Verify ancestry and target file hashes first.
- Engine-focus #815 has native Editor map/save/readback evidence, **not** player-facing bokeh approval; native D3D DOF side-by-side and performance are outstanding.
- #798 has an earlier separate exact-head native Win64 build, not a V5 integrated weather/sky scene. #804 audio has source and hosted checks, but corrected-head native audio/audible game playback were not established in the consulted record.
- Review machine at last direct check: ~**7.1 GiB free RAM**, **11.51 GiB free disk**. The established heavy-reconcile native admission requires **>=6.5 GiB RAM AND >=14 GiB disk**; **HOLD** further large Unreal authoring/combined build, even though V5's earlier isolated native work succeeded. Do not clear caches or terminate other workstreams just to override the guard.

## Smallest next safe integration

1. Record exact remote heads + relationship to V5 for #799, #813, #814, #808 and compare reviewed routing/actor files. Do not fetch or merge entire art histories just to answer a docs question.
2. On a new **isolated branch** choose one owner for input, one for First Wake story-state travel, one for dynamic atmosphere, one for cinematic post-processing and one for audio. Introduce explicit adapter contracts, no duplicated spawn/PP authority.
3. Re-run full source/negative contracts; on resource admission do one exact-head UBT/UHT Editor compile and all registered native automation tests. Preserve original clean V2/V5 maps and receipts.
4. Complete playable seven-step prelude → launch sky → physically verified sea landing → fuel → Lyra scene; then add equipment, magic, enemy gameplay and presentation by gates.
5. Only after source/native evidence, screenshots, audio rights and creator art review should any gameplay asset or feature be promoted. Main stays protected, Starbourne fail-closed, Reson and Aepex unavailable in First Wake.

**Disposition:** Dependencies and docs reconciled at review/planning level only. No new runtime integration, dependencies installed, native build, art approval, CI result, or merge is asserted by this document.
