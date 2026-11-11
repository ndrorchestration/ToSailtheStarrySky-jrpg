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
