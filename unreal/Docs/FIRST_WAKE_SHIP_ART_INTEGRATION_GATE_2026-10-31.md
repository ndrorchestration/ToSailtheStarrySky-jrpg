# TSTSS Unreal — First Wake + Aureate Wake + Authored 3D Art Integration Gate

Date: 2026-10-31. State: **ISOLATED REVIEW BRANCH / SOURCE-VERIFIED ONLY / NOT NATIVE-BUILT / NOT APPROVED FOR MAIN OR RELEASE**.

## Exact source authority and integration method

Created branch `integration/unreal-first-wake-ship-art-reconcile-20261031` from **current Unreal foundation** `3a8461a025ec3ee91b422a54fe58b6731ce7f595` (draft PR #608), not from the older Godot or ship branch. Preserved every foundation C++/config file, including `TSTSSFirstWakeState`, `TSTSSWaterLandingGate`, `TSTSSWaterContactAdapter`, `TSTSSCombatAbilities`, `TSTSSPersistence` and `DefaultInput.ini`. This is a real git-tree integration from exact source blob SHAs, not a simulation of a merge.

43 original paths reconciled atomically from:

- Ship/water observer + selected engineering docs/scripts from [draft PR #629](https://github.com/ndrorchestration/ToSailtheStarrySky-jrpg/pull/629), source `6c8a2502cee98727523f9247129c0b21387eadee` — **16 paths**, including fixed `AureateWakeWaterObserverComponent.cpp`, its source checker and dependency contract.
- Authored wing/GLB + root-pivot pose + four ship root supports + isolated First Wake review map scripts / asset safety + QA from [draft PR #631](https://github.com/ndrorchestration/ToSailtheStarrySky-jrpg/pull/631), source `a0be9dec82514d6c45314c0ff7d54a3f7356f96b` — **26 paths**, including the more recent four-support `AAureateWakePreviewActor`.
- `unreal/.gitignore` additive privacy-preserving review art exclusions — **1 path**, keeping the foundation's existing UE build cache ignores.

The earlier art branch's `AureateWakeWaterObserverComponent.cpp` and `check_aureate_water_observer_source.py` are **explicitly rejected**, because the former could request Seaborne visual state merely on `bTouchingWater` without first checking accepted water-contact story progression. Selected PR #629 version uses physical-body velocity where simulated and checks `bContactAccepted && bTouchingWater` after the story water gate. This is safer, but still requires native collision proof.

Do **not** replace the foundation `TSTSSFirstWakeState` with the stale copy from the art branch. The current foundation rejects generic `AdvanceTo(SeaContact/FlotationConfirmed)`, requires all engineering inspections and validates save/restore inspection masks.

## Integrated source check

Workflow: [`.github/workflows/unreal-integrated-first-wake-source.yml`](../../.github/workflows/unreal-integrated-first-wake-source.yml). It tests all offline unit suites together, checks the physical observer/story coupling, ensures the declared C++ automation suite is present in the Windows verifier, runs the isolated coastal review-map specification, regenerates corrected meter-scale wing and support GLBs and validates their non-destructive importer manifests, then screens normal wing transformations against the actual GLB geometry. Outputs an artifact containing the two review-only GLBs and numeric clearance JSON.

Additional regression:
- [`test_integrated_first_wake_ship_authority.py`](../Tests/test_integrated_first_wake_ship_authority.py): story milestones and engineering prerequisites, accepted-contact before visual landing, 4 wings / 4 supports / 2 hydrofoils, isolated non-destructive art imports, Orbiter fail-closed and no ship preview story authority.
- [`check_aureate_preview_source.py`](../Tests/check_aureate_preview_source.py) scoped its Submersible-visibility test to *wing* components. The old blanket exclusion of every `SetVisibility(false)` was incompatible with intentionally hidden optional **support** components.

The first integrated workflow run `41191917278` executed 77 offline unit tests and initially failed on a formatting-sensitive test assertion: `replace_existing\x27, False` versus a zero-space form. Source importers themselves still had `replace_existing=False`, the intended fail-closed safety control. The integration test was fixed to normalize whitespace, retaining the check. This first failure is preserved as evidence.

## Native production gates — all still pending

1. Confirm the development host has Unreal Engine **5.8**, Windows C++ build tools, the Python Editor Script Plugin and native scene test infrastructure. Native build of `ToSailTheStarrySkyEditor`, then execute `unreal/Tools/Verify-Unreal.ps1`. Source-only checks and hosted Python do **not** establish C++ compilation, engine test execution or frames.
2. Import the corrected wing and root support GLBs into two *separate*, empty review folders via their manual, guarded importers; verify meters-to-centimeters, actual import transforms, materials/tangents, PBR opacity and light response. Imported assets remain **noncanonical**.
3. Build the isolated First Wake coastal review map; wire a **single** authoritative hull/water-contact observation path for that trial. Do not activate both `ATSTSSWaterContactAdapter` and `UAureateWakeWaterObserverComponent` for the same hull/story until there is a tested ownership contract. A water-volume overlap alone cannot be a SeaContact milestone; verify actual hull/waterline intersection and physical velocity.
4. In the isolated actor preview, expect exactly **4 wings, 4 supports and 2 hydrofoils**. Test all three normal forms and six directed transitions with actual StaticMesh assets; inspect hull root mount geometry, collisions, brackets, forward geodesic bridge, long-range silhouette and performance. Wing root support length-scaling can distort its brass collars and requires cinematic review. True continuous-time collision and structural load tests remain open.
5. Hidden Orbiter/Moon Bridge preview remains default-off and the authored-wing interpolation route remains disabled due to prior witnessed proxy intersections. Do not imply final physics or story unlock from the four-form review enum.
6. Capture genuine UE engine screenshots/video, frame timing and test logs bound to **exact git SHA**. Have creator judge visuals against approved October 30 character/ship reference, then seek separate decisions for engine, narrative, visual and build acceptance.
7. Do **not** merge to protected main, modify Godot First Wake, change Windows installer, publish art or deploy without explicit creator approval. Original PR #608/#629/#631 remain independent draft audit evidence.

## Known project risks

**Source divergence:** new foundation changes while review branches move. Keep integration branch pinned and rebase/reconcile explicitly before native build; do not overwrite newer story, combat and save files.

**Multiple physical observation routes:** only one should be assigned story authority in any native scene until an integration test proves safe handoff/mutual exclusion.

**Engine-native quality:** procedural GLB geometry and source check passes are not artistic acceptance, real-time optical effects, animations or player-visible feature admission.

**Asset provenance:** candidate wing/support meshes are authored review lookdev, not final producer-approved objects; older v1 100× oversized wing GLB is permanently retired for import.


## Explicit editor-only ship art binding (review scene only)

This branch additionally provides [`unreal/Tools/bind_first_wake_review_ship_art.py`](../Tools/bind_first_wake_review_ship_art.py) and [`unreal/Tests/test_bind_first_wake_review_ship_art.py`](../Tests/test_bind_first_wake_review_ship_art.py). The aim is to get the actual corrected wing/support meshes onto the existing Aureate Wake C++ ship actor in the **isolated benchmark map**, rather than relying on source code and standalone GLBs alone. This is a human-reviewed editing convenience, not a game integration or engine execution result.

**Prerequisites (not yet verified here):** UE 5.8 Windows C++ project compiles; both separate review-only GLB importers have been run manually and each produces a valid StaticMesh; the isolated `/Game/TSTSS/Review/FirstWake_Benchmark_V1` map exists and is open in Unreal Editor, with a single `TSTSS_REVIEW_AureateWake` actor from the compiled `AAureateWakePreviewActor` class.

Review the exact imported asset paths in the Content Browser. Example **read-only** preflight, outside Unreal:

```powershell
py -3.11 unreal/Tools/bind_first_wake_review_ship_art.py --inspect --wing-asset "/Game/TSTSS/Review/ShipArt/WingCandidateV2/AureateWake_Wing_Lookdev" --root-support-asset "/Game/TSTSS/Review/ShipArt/RootSupportCandidateV1/AureateWake_RootSupport_Lookdev"
```

Only if the actual imported asset names match those paths, run the identical script with `--bind-in-editor` rather than `--inspect`, inside **Unreal Editor Python**, with the same two asset arguments. The editor function refuses any other world, duplicate or missing actor, non-StaticMesh, pre-existing authored art assignment, transitioning/non-Skyborne form, or enabled Orbiter. It then attaches reviewed wing and support assets to this one actor, enables its root-pivot pose mode, and calls the existing `refresh_wing_meshes()` and `refresh_root_supports()` C++ methods. On setter/refresh failures it attempts to restore the original asset properties.

**Never auto-save:** this function does not create/spawn/destroy actors, open/save levels, import new assets, alter gameplay or perform actor form requests. The editor's map is intentionally left dirty and must be reviewed visually by the creator before any manual review-map save. Do not run it against a playable level.

Source API references: [Epic UE 5.8 EditorActorSubsystem](https://dev.epicgames.com/documentation/en-us/unreal-engine/python-api/class/EditorActorSubsystem?application_version=5.8) and [Epic Python Editor scripting](https://dev.epicgames.com/documentation/unreal-engine/scripting-the-unreal-editor-using-python).

**Verification boundary:** mocked Python tests prove guard logic only. Unreal Editor import, reflection of properties/functions, actual compilation, live binding and resulting image are NOT VERIFIED on a native machine.


## Hydrofoil review regression carried forward

Ported the bounded visibility correction from PR #635 at `90932ad322589ff4eddae4ff1b5d0ba103fc7856` onto integration baseline `8b3cc4d6c8327487cd0d9e0f4081e0f30facfd60`. Only the RequestForm foil visibility statement changes: foils stay visible during deployment/retraction on routes involving Seaborne and hidden on other routes. Existing authored mesh selection, four supports, water/story authority and fail-closed authored Orbiter route are retained.

Added the 12-route native BasicShapes mechanics test from #635 and required its exact name in Verify-Unreal.ps1. This native test uses default cube mode, not imported-art poses. Run the ordinary native verifier; a missing or skipped ship test must prevent PASS.

Adapted the isolated g++ RequestForm probe for the integrated class and 48 route/mode cases: cube preview permitted, authored mesh present, authored mesh missing, and cube Orbiter permission disabled. Rejected requests must preserve foil visibility, source form and empty transition arrays. Before correction: 12 failing cases; afterward: 48/48 passed locally. The probe executes the actual method with boundary substitutes and does not test Unreal types, transforms, assets, physics or rendered visibility. CI now runs it alongside existing integrated suites.

Windows Unreal compilation, native automation, authored-wing visuals and artist acceptance remain NOT VERIFIED. #635 and #610 are preserved, main and Godot untouched. Roll back this integration increment as one commit if necessary.
