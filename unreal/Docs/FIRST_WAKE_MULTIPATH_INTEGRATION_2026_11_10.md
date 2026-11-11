# First Wake — multi-path Unreal integration candidate (2026-11-10)

**State: source/asset integration candidate only. NOT native-accepted, playable, art-approved, merged into protected main, or releasable.** Source of truth for this candidate: `unreal/DataSource/Integration/FirstWakeMultipath.review.json`. Historic upstream PR commits there identify exactly what was imported, not current status of those evolving PRs.

## What has been integrated in the isolated review worktree

- #792 — water contact, pretransition flotation, E interactions, F6 save/F9 load, F7 preview/confirm prelaunch Continue. **New live #792 head `ab69db6abd06fab35a0ab105f8c3b3539699c9cb`** was separately merged after the initial integration candidate: it adds a source-validated 10-shot runtime beat/engineering/water handoff contract, not a runtime LevelSequence or actual gameplay integration.
- #790 — 10-shot cinematic requirements and story chronology.
- #796 — 11 independently authorable lighting looks and source tests.
- #794 — six UE 5.8.4 review maps and ten native material assets with prior map-readback evidence.
- #795 — 22 deterministic GLB environment/ship object prefabs (additive source snapshot, rather than importing unrelated historical #766 ancestry).
- #793 — 14 original three-character GLB equipment meshes, imported review assets, QA gallery and fail-closed equipment stage contract.
- #797 — nine proposed Ender Resonator spell rows, native C++ review VFX actor, source-gated cue selection and isolated authoring script.
- #798 — C++ sun/moon, weather, atmosphere, fog, cloud and precipitation review director and authoring script.
- #791 — three 3D enemy review silhouettes, guarded encounter/AI and six candidate abilities (additive source snapshot only, rather than importing unrelated main ancestry).

All import paths remain in the review namespace. Original PRs remain open/draft. The object and enemy snapshot file content was copied from the exact source commits shown in the machine manifest. Nothing in this branch automatically promotes ReviewSelectable/ReviewExecutable to CreatorApproved, adds mastery or abilities to Ender, recruits Lyra before splashdown, or opens Starbourne.

## Critical integration reconciliation

- Distinct native automation names from parallel paths were united into an exact **35-test** registry; previously hardcoded counts from individual 29–32-name tracks were reconciled in the PowerShell assertion/negative-fixture scripts, native-readiness guards, and source-admission tests. Do **not** relax these checks or accept stale 30-name reports.
- Both magic and equipment source-preflight path triggers are preserved. Source-only tests confirm duplicate names, missing proof, forged automation totals and unsafe native admission are rejected.
- Gameplay controls: PIE F6 quicksave, F9 session quickload, F7 twice only for prelaunch Continue; standalone F5 quicksave. Shift+F5 in PIE must never be used as a save shortcut. Water landing requires directly observed >=2.0 s pretransition flotation.
- The first two party members are Ender and Captain Ionia. Lyra joins only after splashdown. Reson and Aepex are excluded from this slice, not from broader game canon.
- The 6 native review maps, equipment gallery, spell VFX comparison scene and sky/lighting preview scripts are **separate review assets and authoring paths**. They have not been connected into a single gameplay map or shown to function together; do not call this a completed vertical slice.

## Ordered next native gates

1. Close other Editor/Live Coding sessions without interrupting their owners. Confirm clean exact commit, >=5.0 GiB physical RAM, >=14 GiB disk.
2. Native UE 5.8.4 Win64 UHT/C++ Editor build and all **35 distinct named Editor automations** on this exact commit. No existing native receipt transfers across merge commits.
3. Under >=6.5 GiB physical RAM with no competing GPU/Editor session, author a disposable review level and verify imported map/material/prop/equipment assets and spawned atmosphere, lighting, spell and enemy actors against the **combined** project binaries.
4. Record source and built asset hashes, map readback, real Lit D3D captures, visual fidelity, screenshot comparisons, performance, sound/animation and failure paths. A source script or generated static proxy is not a verified cinematic result.
5. Execute two real player-driven Prelude to splashdown PIE runs, with E, F6, F7, F9 and negative tests, water stability and chapter transition. Audit chronology and unlocked-skill guards, then seek creator visual approval.

**NEONTIC safety hold during source integration:** Unreal Editor + LiveCodingConsole were active. Native build/Editor/PIE was deliberately not started, and no existing game worktree/session/config/save was overwritten.

## Cross-path source gate

`python -m unittest discover -s unreal/Tools -p "test_*.py"`

`powershell -NoProfile -ExecutionPolicy Bypass -File unreal/Tools/Test-NativeAutomationReportFixtures.ps1`

The `test_first_wake_multipath_review.py` guard additionally verifies all nine lane sources, registered native-test inventory, 6 maps, 22 GLBs, 14 equipment GLBs, player order, input isolation and strictly unapproved evidence states, with negative mutation tests.


## 2026-11-10 continuation — isolated integrated shore probe

**Implementation staged in source, Unreal Editor execution NOT RUN.**
The additive plan `unreal/Tools/stage_first_wake_multipath_shore.py --plan` verifies the actual six-map receipt, SHA-256 of the saved VS06 shore map, all 22 original object GLB sources, 14 three-party static equipment GLBs, and all nine Ender VFX cues. No user process is launched by `--plan`.

When native C++ modules are actually built at this **exact integrated commit**, the guarded native launcher can generate one separate review scene:

`/Game/TSTSS/Review/MultipathV1/L_VS06_ShoreMagicEnemyGear_Review`

It duplicates VS06 instead of changing it, creates an isolated folder per GLB import, imports all 22 source prop meshes, displays eight curated prop actors and three non-equipped equipment props (Ender staff, Ionia saber, Lyra water focus), spawns three distinct enemy visual proxies, nine independent *review-only* Ender cue loops, the native atmosphere director, a camera, and a conspicuous review-only warning. It replaces only known duplicate-owned sky/sun/fog actors inside the **duplicate map**, disables added actor collision, and verifies counts, identities, source-map hash and config hashes. This is an additive visual *showcase*, not an encounter, cast, runtime map transition, native animation, story/authority progression, gameplay proof or finished cinematic.

### Fail-closed exact-head execution sequence (not yet executed)

1. Ensure the user's existing Unreal Editor and Live Coding sessions are closed **without terminating or interfering with them**. Confirm 5 GiB free physical RAM minimum for native build and 14 GiB free disk, and that the isolated integration branch has a clean full 40-character HEAD.
2. Run existing `unreal/Tools/Verify-Unreal.ps1` with `-EngineRoot "C:\Program Files\Epic Games\UE_5.8" -ExpectedHead "<current 40-hex integration SHA>"`. A successful full native build **and all 35** registered UE native tests now produce `Saved/MigrationEvidence/<unique>/verified-native.json` (with report digest, head and explicit PIE/visual NOT_TESTED). Build-only `-SkipTests` does not satisfy this gate.
3. Read-only host check: `python unreal/Tools/run_first_wake_multipath_native.py --check --expected-head <same SHA>`. It must return `HOST_PREFLIGHT_PASS_NO_UNREAL_LAUNCH`. It explicitly rejects active Editor/LiveCoding processes, missing exact-head native receipt, fewer than **6.5 GiB physical RAM**, fewer than 14 GiB disk, dirty/rebased HEAD, existing saves or an occupied output.
4. Explicit host-only stage: `python unreal/Tools/run_first_wake_multipath_native.py --stage --expected-head <same SHA>`. Exactly one own, capped, low-priority UE headless NullRHI child is launched; no foreign process is killed. The stage writes separate `Saved/MultipathV1/` evidence and refuses to overwrite previous receipts.
5. If the map was successfully saved and its map hash verified, perform independent Editor readback, Lit D3D camera review, actor/visibility/layout checks, performance, combat admission review, real controlled Prelude PIE, input/sea/save checks, and creator art approval. **NullRHI output is not a rendered GPU image or proof that the sequence is playable.**

**Partial-failure semantics:** A failed native import may leave new unapproved assets inside its unique review namespace. The workflow intentionally refuses a second overwrite attempt; inspect the failed run and use a fresh disposable namespace/worktree for remediation rather than silently deleting evidence or assets.

**Source-only QA:** `python -m unittest discover -s unreal/Tools -p "test_first_wake_multipath_shore.py"` checks the map/GLB/gear hashes, no automatic grants, exact native receipt binding, stale/forged receipt denial, no implicit Unreal launch, conflict-free map destination, unique actor counts, and fail-closed process/resource boundaries.

## 2026-11-10 native UBT compile trial: failed at `bb6855e27475`

The first exact-head UE 5.8.4 native Win64 Editor build was attempted on an idle workstation. The build report is retained under `unreal/Saved/MigrationEvidence/bb6855e27475-20261111T042648861Z-212b5bbf/build.log`. **Result: FAILED**, before any Editor automation tests.

Three compiler diagnostics reduced to two source defects:
- `TSTSSMilestoneActor.h` duplicated the declaration `ReconcileReviewCollisionAfterRestore` within the same class (C2535).
- `TSTSSExplorerCharacter.cpp` compared the First Wake beat to nonexistent `bPendingReviewContinueBeat` rather than its actual `PendingReviewContinueBeat` member (C2065, cascading C2737).

Smallest reversible source repairs have been applied ONLY on this integration branch, with one new test `test_native_compile_regression_restore_and_f7_confirmation` in `test_first_wake_multipath_review.py`. Source-only regression: **438/438 PASS**. These repairs do not prove that the next native build passes. The failed exact-head evidence stays in place and must not be promoted as native acceptance.

Disk reserve after initial UBT compile: 14.1 GiB. Existing `unreal/Intermediate` (~2.48 GiB) is preserved for the incremental retry; no shared build/cache or other agent session was deleted or terminated.

## Native verifier cross-agent race safeguard (source-only)

During the second native attempt, `Build.bat` was already held by an independently launched Unreal build and a separate `UnrealEditor.exe` appeared after the initial preflight. Our waiting verifier process was stopped, not the other agent's processes. This revealed a concurrency boundary: a preflight at entry does **not** prove that native automation is safe after a long compile or lock wait.

`Verify-Unreal.ps1` now calls `Assert-TSTSSNativeSessionStillSafe` **immediately before the build** and **after the build, before build-only evidence or a second UnrealEditor-Cmd launch**. The gate checks active Editor/LiveCoding, 5 GiB free physical RAM, 14 GiB free C: disk, exact HEAD and clean source. It does not globally reserve Unreal, and cannot prevent another actor starting after the check; outside operators must coordinate concurrent native sessions.

At this point C: free disk was 9.09 GiB. Only the failed multipath integration checkout's disposable `unreal/Intermediate` (2.48 GiB) was deleted, after verifying no process referenced the isolated worktree and its original negative native build log persisted. Disk free increased to 11.57 GiB but is **still BELOW 14 GiB**. No other agent assets, caches, worktrees, active Editor, user saves or production maps were modified. **Native build/PIE remains BLOCKED** until resource gates genuinely pass. The additional verifier source guard is a safety repair, not a native test pass.

## 2026-11-10 additional concurrency finding: UnrealBuildTool queue

During exact-head retry at `de0a6a185fae0c5c17300762d288fa753f39a203`, native verification again encountered `Build.bat is already running`. A separate agent had started `UnrealBuildTool.dll` for its **Lyra staging** checkout. Only this integration verifier's *waiting* terminal was canceled; the outside build and its child processes were left untouched. **No native build or 35-test result was produced on this retry.**

The existing preflight only detected UnrealEditor and LiveCodingConsole, which did not exclude active command-line UBT builds. `Verify-Unreal.ps1` now also performs a Windows process-query gate for active `Build.bat` / `UnrealBuildTool` **before** its initial build admission and at its later safety rechecks. This prevents intentionally entering the global wait queue when an existing build is visible. It still cannot provide a machine-wide atomic lock: each separately controlled agent must cooperate to avoid races.

Neontic disk free recovered to ~18 GiB through concurrent activity without further cleanup from this integration session. Because other TSTSS native validation was active at the time, our review-native work remained safely held. No shared cache was deleted, no external compiler/Editor session was terminated, and all source/head/authority boundaries remain unchanged.

## 2026-11-10 native receipt consumer parity and visual-stage concurrency

The secondary visual-stage receipt checker in `run_first_wake_multipath_native.py` now requires the same complete per-test semantics as `Assert-NativeAutomationReport.ps1`: 35 distinct required native paths, all rows valid and successful, **exact equality** between the succeeded summary and the per-test list, no failed/not-run rows, and full same-head receipt/report checksum custody. Engine-free synthetic tests explicitly reject inflated successes, invented failed/blank rows and falsified totals even if a synthetic report hash was updated to match; these are tests of refusal logic, **not native build evidence**.

The guarded scene launcher now separately probes for competing `Build.bat` or `UnrealBuildTool` via read-only Windows process inspection before starting its own Unreal Editor child, in addition to its existing Editor/LiveCoding/RAM/disk/exact-head checks. It records no other process's command line. Ambiguous/failed process inspection is an explicit HOLD, not an implied idle state. These source hardenings preserve the existing review-only art and progression restrictions. No native 3D scene was authored on this head.

## 2026-11-10 native 35/35 report rejected for mutated tracked config

Unreal 5.8.4 execution on exact head `fd1a07742b384100abefba7029012d09517f4492` produced a real `AutomationReport/index.json` with 35 succeeded / 0 failed / 0 notRun and 35 unique per-test `Success` entries. The verifier nevertheless **correctly refused acceptance** because the commandlet rewrote two tracked source files: `unreal/Config/DefaultEngine.ini` (plugin-generated editor settings, including transient local fields) and `unreal/Config/DefaultInput.ini` (engine-exported normalization/default input bindings). The run has **no `verified-native.json`** and cannot be called exact-head clean native PASS. Full negative evidence is retained in the ignored `Saved/MigrationEvidence/fd1a07742b38-20261111T050557220Z-d0de6e9c` directory, without publishing or copying transient config values.

After confirming the two files were the entire tracked diff and no native process still used this dedicated review checkout, the files were restored **only in this isolated worktree** from the precise committed contents. No production, other-agent, user-save or shared configurations were touched.

The native verifier now records each tracked config's SHA-256 and read-only state, makes both configs read-only **only while the editor automation child is running**, restores their original attributes in `finally`, and rejects any hash drift even if Unreal itself returns success. This is a source-level prevention measure, pending actual same-head native validation. It neither alters expected input controls nor approves visuals, PIE or a release.

## Independent shoreline native map readback (new source-only gate)

Added `unreal/Tools/verify_first_wake_multipath_shore.py` as an independently executable **read-only** checker for the proposed combined scene. Its `--plan` path operates without Unreal and verifies 26 deterministic review actor labels and expected actor classes: one coastal atmosphere actor, eight original props, three non-equipped party gear props, three enemy-only silhouettes, nine Ender cue visualization actors, one review camera, and one unapproved-art warning.

Its `--native` path remains **NOT RUN / NOT ACCEPTED**. Only after exact-head native-stage receipt exists, it independently reopens `/Game/TSTSS/Review/MultipathV1/L_VS06_ShoreMagicEnemyGear_Review`, compares saved-world actor identity, class and collision against the expected source list, verifies staged map and original map SHA-256 and actor totals, and writes an isolated, non-overwriting `Saved/MultipathV1/shore_independent_readback.json` with `pie_verified=false`, `gpu_render_verified=false`, `creator_approved=false`. It cannot spawn actors, save maps, grant spells, change equipment, create encounters or approve gameplay/art.

The separate engine-free `test_first_wake_multipath_readback.py` provides synthetic negative checks for missing/malformed/stale native stage receipts, false creator/PIE approvals, changed map hashes, and actor-count disagreement. No native map readback, playable encounter, render or visual approval has occurred.

## 2026-11-11 exact-head native success and scene-stage failure

**At exact source HEAD `3e5cd3eab6c7832266ad4209f4349470605bd0b3`**, `Verify-Unreal.ps1` returned zero and emitted real acceptance `unreal/Saved/MigrationEvidence/3e5cd3eab6c7-20261111T120841557Z-55fc135a/verified-native.json`, bound to the matching report digest `83061518c6bfa7cbe99889a0f3832305b05fcf89e20837ec2cfcddc5d0efc092`: UE 5.8.4 Win64 Editor build SUCCESS, **35 succeeded / 0 failed / 0 notRun**, all 35 distinct test entries `Success`; checkout and tracked configs clean. **This is real native automation success at that exact historical head**, not proof of an integrated playable map or later commits.

The first guarded native shore stage was **HOLD**, not accepted. Preflight and exact-head native receipt check passed with ~19.81 GiB disk and 6.75 GiB RAM; Unreal Editor launched but the Python stage stopped at `HOLD: C++ native enemy enum is not reflected`. The stage attempted the C++ spelling `unreal.ETSTSSSliceEnemyKind`. Unreal's reflected Python naming removes the leading enum `E`; the source-only fix now explicitly resolves `unreal.TSTSSSliceEnemyKind`, checks all three distinct `HARMONIC_SHEAR`, `AETHER_LEAK_WISP`, and `DOCK_SKITTER` values, and fails closed if any value is unavailable. This fix is **source tested only** pending another native stage.

The failed stage produced **no map/content namespace** and no stage receipt; tracked source and original VS06 map hash stayed unchanged. The three failed child/host evidence files (`shore_host_receipt.json`, `shore_unreal.log`, `shore_stdout.log`) were SHA-256 checked and moved, without overwriting, to `unreal/Saved/MultipathV1/Attempts/3e5cd3eab6c7_failed_python_enum_25208/`. This permits a distinct later native attempt while preserving exact historical failure evidence. A new source commit still requires full **new exact-head native build+35 actual tests** and fresh admissibility before a further stage. No PIE, native scene readback, D3D Lit screenshot or visual approval occurred.

## 2026-11-11 follow-up stage: real embedded-Python import boundary

A second guarded native stage at `65d8e3313df5a833e4750492161d1e53b498267c` passed the exact-head UE 5.8.4 native build/35-automation receipt, all read-only source/asset prechecks, and the repaired C++ enum reflection check. The next failure was **`ModuleNotFoundError: No module named 'build_ender_resonator_preview'`**: UE's `-ExecutePythonScript` does not guarantee the invoking script's sibling Tools folder is in `sys.path`. No map or material namespace was authored; tracked source, default configs and original shore map remained unchanged. The three failed host/editor/stdout evidence files were independently SHA-256 checked and archived without replacement into `Saved/MultipathV1/Attempts/65d8e3313df5_failed_material_import_38916/`.

**Source repair:** the integrated stage now loads the specific source-locked Ender material helper from an absolute `unreal/Tools/build_ender_resonator_preview.py` path using `importlib.util.spec_from_file_location`, verifies the import spec, and executes only its explicit `make_material()` function, not the helper's `__main__` map/DataTable authoring. The original standalone C++ VFX renderer references `M_ResonatorGlow` at runtime, with a generic Engine fallback; review material is still required for full creative VFX review. Review boolean properties now use a checked, fail-closed setter that attempts both native Unreal Python b-prefix spellings and confirms the intended value, never silently skipping no-autoplay, reduced-motion or cue-loop settings.

These corrections are **source-only** until the next exact-head native build/35-test receipt and subsequent staged world readback. Existing failed-attempt history is immutable and preserved.

## 2026-11-11 fatal Unreal duplicated-world GC and two-process remedy

The third staged attempt on exact native-verified source HEAD `7c60e1eb4e3284fda4ea84de2b691ea8193da86a` successfully authored `/Game/TSTSS/Magic/M_ResonatorGlow` and **220** imported modular-prop `.uasset` objects, then **CRASHED** at `UnrealEd/EditorServer.cpp:2544`: `World Memory Leaks: 2 leaks objects and packages`. The Editor log identifies `EditorLoadingAndSavingUtils.LoadMap` trying to load the new duplicate immediately after `EditorAssetLibrary.duplicate_asset`; duplicate target world and package had standalone garbage-collection references. It produced **NO saved `.umap`, no native-stage receipt and no valid gameplay/art proof**. The original VS06 map SHA-256 remained `316299925275785494d1ec7b082f20007fa0f889f50ce59ea1c7e977ef942726`; no tracked source/config file changed.

The `221` partial review-only assets (including the one emissive material) and all three failure logs/receipts were moved out of `Content` into the ignored, immutable-in-practice `Saved/MultipathV1/Attempts/7c60e1eb4e32_editor_world_leak_18520/`, then indexed by relative path, size and SHA-256 in `archival_manifest.json`. Archive verification passed; the integration checkout became clean again. Existing approved party equipment/source maps and other agent sessions were not modified.

The stage has been redesigned as a **two-process native review pipeline** (the two processes execute serially, not concurrently). In process **prepare**, the original source shore level is loaded in Unreal and **saved as** a distinct destination map via `EditorLoadingAndSavingUtils.save_map(source_world, DEST_MAP)` instead of duplicating a `UWorld` through `EditorAssetLibrary`. This is consistent with documented Unreal level-duplication GC failures (Epic UE-177376, UE-109253) and avoids a Level Blueprint redirect hazard. The prepare process imports the 22 original GLBs into independent namespaces, materializes the review material, validates source/config hashes, and writes a non-overwriting first-phase receipt only after the separate `.umap` exists. The process then **fully exits**; no UWorld pointer can cross the process boundary.

In a new process **compose**, the host verifies the exact-head prepare receipt and map hash, checks for other Editor/UBT processes and >=6.5 GiB physical RAM and >=14 GiB free disk, then opens the prepared map and projects 26 source-locked noncanonical review actors. Final native scene receipt and 3D map save occur only if the actual save, actor counts, config/source hashes, and log sentinels succeed. Any first-phase failure prevents compose and preserves partial evidence. A separate independent readback remains necessary after this step; PIE, GPU Lit capture, story/party gameplay and creator approval are **NOT TESTED**.

This new source route has passed engine-free QA only and **requires a new exact-head UE 5.8.4 Win64 build plus 35 native automations** before either process may be run. No review scene exists at this new source head yet.

## 2026-11-11 native-review map package — source-locked handoff

The historical source head `a7244775e64208be21f04320cc7fe20703704979` passed **35/35 real UE 5.8.4 Win64 native automations**, produced a fresh `VS06` shoreline review copy through the isolated two-process `prepare → compose` path, and passed an independent **fresh-process native map reopen/readback**. Accepted review receipts remain under ignored `Saved/MigrationEvidence/a7244775e642-20261111T144831776Z-0dd10928/` and `Saved/MultipathV1/`. The rejected first independent readback due to tracked Engine/Input configuration rewrites was not promoted; after reverting only the two generated config changes, an independent native readback verified 43 saved actors and 26 source-locked review-only objects and preserved original VS06 SHA.

For team review, exactly **222 locally generated native UE files** are captured in this draft branch: 221 `.uasset` plus one `.umap`, total **15,283,468 bytes**. SHA-256 for each file and canonical content-tree digest `70a5eeebc8169ae8f04d6c89a96153c94fa65b7ccd323cb22e2c04b24509c88d` are recorded in `Docs/Evidence/firstwake_multipath_native_scene_snapshot_20261111.json`, validated by `Tools/verify_first_wake_multipath_asset_snapshot.py --check` and its negative tests. Review map digest: `fec410d08244ec5ac71965af2df98434411591aa8a280dfefe8ea038ae50357f`. Original shore map digest remains `316299925275785494d1ec7b082f20007fa0f889f50ce59ea1c7e977ef942726`.

**Critical authority distinction:** native stage and readback evidence applies to the historical generating commit **a724477**, and the new GitHub commit carrying the assets is a **different head** requiring its own revalidation for new claims. The handoff is review-only, unmerged and not a playable encounter. The 3 gear props are not automatically equipped. Magic cues are review visuals, not authorized player-cast skills. The three enemy silhouettes are not live combat encounters. No PIE/player-control proof, GPU Lit screenshot, cinematic/AAA visual approval, progression approval, or Starbourne unlock is established. Native authoring uses a new destination and fails if it already exists: do **not** rerun the prepare phase on a checkout containing these committed assets. Instead use the independent read-only map-opening review gate, or a fresh disposable checkout for replay.
