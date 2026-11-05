# Cross-PR Unreal integration review — 2026-10-30

Status: **PLANNED / NO CROSS-PR MERGE / NO NATIVE ACCEPTANCE**.

## Exact source snapshots reviewed
- Unreal foundation PR #608, head `44be5bb34157efa746f49bd9694d12a13536b4b4` (draft, base main).
- Godot combat PR #601, head `c6c969685e86a9879bf8ab23d3fe3c34928cbc98` (draft, based on revised Godot First Wake branch).
- SpriteCook reference PR #609, head `3f808b477346d6ed8c261a954b8962be98558e7f` (draft, base main).
- Aureate Wake geometry PR #610, head `d2da85d6930a356b578988b02879812020855251` (draft, stacked on `feat/unreal-5-8-migration-foundation`).

These are review snapshots, not permanent heads. Reinspect before any cherry-pick, merge or release decision.

## What can be pulled forward

| Source | Reusable contract / content | Integration action | Acceptance gate |
| --- | --- | --- | --- |
| #601 | Pure combat transaction and duplicate/invalid identity rejection; actor-target atomicity, knockout skip, round rollover; learned-ability and faction preflight | Mirror finite behavioral fixtures in UE automation tests; translate algorithms, do not copy GDScript | Win64 UE 5.8 native compile and exact-head automated tests; review parity where combat formulas differ |
| #609 | Three SpriteCook 1024x1024 art-direction sheets and importer plan | Recover originals by stable asset ID, checksum and record license; place in reference-only UE asset paths; reject unverified slicing | Authoritative originals, provenance, visual inspection and UE import/render evidence |
| #610 | Four-form dragonfly ship actor, visible folded submersible wings, Seaborne hydrofoils, Orbiter preview opt-in; procedural wings and venation tools | Keep stacked preview isolated; verify it builds atop actual #608 head; run its source checks and inspect native meshes/materials | Engine compile, actor transitions, native renderer capture, creator approval |
| Existing #608 | Combat rules/turns/abilities, First Wake state, SaveGame, exploration character, native verification script | Stabilize as the integration base, preserve its tests and verify exact-head before moving external code | Windows build, automation JSON evidence, play-in-editor and rendering separately |

## Recommended order

1. **Do not merge into main.** Preserve Godot as the playable fallback and both approved cast art and vessel design canon.
2. Run `unreal/Tools/Verify-Unreal.ps1` on a connected Windows machine with UE 5.8 and a clean checkout. Capture build log, automation JSON, commit SHA and exit codes. The present environment cannot supply a native UE verification receipt.
3. Compare #601's tests against UE's existing `TSTSS.Combat.*` tests. Add only missing negative or boundary fixtures; explicitly document the differing formulas (UE Attack/Defense versus Godot power-only primitive) before claiming parity.
4. Treat #610 as a stacked preview. Rebase or restack only after checking current heads and conflicts. No Orbiter story permission is granted by the preview switch.
5. Integrate #609 originals as traceable reference assets, *not* rigged character models, finished Niagara effects, or production shaders.
6. Prepare a renderer-enabled standalone UE test level to review ship transitions and battle presentation. Require human visual acceptance; NullRHI never proves cinematic fidelity.

## Nonclaims and protected state

No UE compile, native automation, 3D asset import, ship physics, visual acceptance, gameplay encounter, Windows installer or release approval is established here. Five Lights are plot affinities; they do not automatically grant magic. Chapter I Ionia-first opening and the missing Lyra/Talen shoreline reunion/salvage beats remain protected. No existing PR was merged or closed by this documentation-only integration review.

## Follow-up regression pulled forward

The UE turn-order test now mirrors two additional Godot #601 scenarios: sole surviving actor round rollover and duplicate participant rejection on battle initialization, including preservation of the prior output on rejection. This is **test source only, not proof of Unreal compilation or test pass**. The fixture also demonstrates that the current turn primitive has no battle-victory/encounter termination authority: a surviving actor can continue acting when opponents are incapacitated. Before playable battle integration, add an explicit encounter lifecycle gate that determines when turns terminate. Preserve draft status and native verification gates.

## 2026-10-30 follow-up — isolated encounter lifecycle gate

- Added `FTSTSSEncounterGate` (public header and C++ implementation) above the existing transactional turn primitive. It evaluates an explicitly provided two-faction roster as `Invalid`, `Ongoing`, `Victory`, `Defeat`, or `Draw`, and prevents further actions once the encounter is terminal. Its failure path preserves the output argument.
- Added `TSTSS.Combat.EncounterCompletion` automation source covering a lethal action, subsequent-action rejection, unchanged original state, defeat, simultaneous incapacitation, and missing-faction refusal.
- **Not an encounter spawner or party/recruitment authorization system.** Faction data is caller-supplied; canonical encounter eligibility, rewards, retreats, animations, save/resume semantics and level exit remain unimplemented. All native Unreal build/test evidence remains pending.
- Cross-PR pull assessment is unchanged: #601 supplies behavioral fixtures, #610 supplies an isolated stacked ship visual preview, #609 supplies provenance-bound concept art references. None was merged, and #609/#610 content was not copied into #608.
- Required native test: `TSTSS.Combat.EncounterCompletion`, alongside all existing `TSTSS.Combat.*` tests in a clean UE 5.8 Win64 editor build, retaining exact-head reports.

## Additional pull-in review — October 31, 2026

Latest inspected snapshots: #608 `822f76fc9f57b7b58f3abe5a584966ca2ba1e142`, #610 `1e567b2b22e74e7d7bbb86bc1b8a0ddd9b6f478c`, #609 `3f808b477346d6ed8c261a954b8962be98558e7f`, #601 `c6c969685e86a9879bf8ab23d3fe3c34928cbc98`. Source references may advance.

The existing `UPSTREAM_INTEGRATION_AUDIT_2026-10-30.md` already inventories First Wake milestone/physics, Chapter I gates, approved art, save continuity and installer lessons: do not duplicate or silently import those branches. The immediate low-risk code pull-in was an encounter-state validation alignment with `FTSTSSCombatTurns::IsValid`: reject negative attack/defense before encounter evaluation or action commit. Added negative-value and nonmutation automation fixtures. **These are source changes only; Unreal 5.8 compilation and test execution are still required.**

Remaining high-value integration gaps: (1) route every ability use through the encounter termination authority, not directly through a lower-level turn primitive in playable scenes; (2) verify native build/test evidence; (3) review #610's ship preview after restacking against the current #608 head; (4) recover licensed #609 reference originals before UE asset import. No merges or production render approvals.

## October 31 ability/encounter integration

The Unreal `FTSTSSCombatAbilities::TryUse` interface now requires explicit party and opponent faction IDs and delegates approved actions to `FTSTSSEncounterGate::TryAction`, rather than directly to `FTSTSSCombatTurns::TryAction`. This closes the identified post-victory ability bypass for callers using this adapter; it is **not** a guarantee that other future/direct turn callers cannot bypass the encounter layer. A regression test refuses a learned ability after victory and preserves the prior output.

Cross-PR candidates remain: Godot #601 for additional behavior vectors (not scripts), #610 ship preview under its stacked branch, #609 provenance-bound concept references, and the existing upstream First Wake/installer audit. No art or ship assets were imported or merged in this pass. Native UE 5.8 compilation, exact-head automation output and player-facing interaction remain unverified.
