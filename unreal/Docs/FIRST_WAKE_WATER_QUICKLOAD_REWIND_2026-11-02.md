# First Wake water landing — quickload restore-generation fix

**IMPLEMENTED, review-only; not native-verified.** This follow-up continues draft PR [#717](https://github.com/ndrorchestration/ToSailtheStarrySky-jrpg/pull/717), based on integrated draft PR [#713](https://github.com/ndrorchestration/ToSailtheStarrySky-jrpg/pull/713) at `52e13aedaa8bda900cece849b54eae570179c838`. Earlier native build and 25-test receipts do not transfer to the changed source.

## Defect and correction

`LoadFirstWake` restores the current `UTSTSSFirstWakeState` object in place. The water gate holds transient contact provenance and settling duration outside that story snapshot. A restore can therefore rewind to `Launched` or restore the same `SeaContact` beat while the gate still retains evidence from the later timeline.

`UTSTSSFirstWakeState::Restore` now advances a `Transient` runtime-only generation after a valid restore succeeds; invalid restore attempts leave it unchanged. The generation is not added to `UTSTSSSaveGame` or the persisted schema. `UTSTSSWaterLandingGate::Observe` remembers the generation it last saw and clears both contact provenance and settling duration when it changes. It then reacquires the existing ordered `SeaContact` milestone from an eligible physical sample. This handles same-beat as well as earlier-beat in-place restores; it does not synthesize water contact, bypass story transitions, or change the two-second stable-contact requirement.

## Executed source checks

`unreal/Tools/check_water_landing_rewind_compiled.py --self-test` compiles the actual production state/gate headers and implementations and both repository water automation test bodies with narrow Unreal API stand-ins. The updated run passed **310 assertions**, including same-object `Launched` rewind, same-beat `SeaContact` restore after 1.75 seconds of pre-load settling, rejected-restore generation stability, restored `SeaContact`, and 11 interrupted-rewind scenarios. Removing the restore-generation guard still compiles but fails the expected same-beat assertion. The hosted Unreal source-preflight workflow invokes this harness.

The local Unreal Tools Python suite passed **123 tests**; the source registry still contains **25 required native automation names** (registration is not execution). `git diff --check` passed. These results are source-level checks, not Unreal Engine execution.

## OPEN — native follow-up

In a separately authorized disposable UE 5.8.4 checkout at the exact candidate head, run the Win64 Editor build and all 25 named automation tests. The native `TSTSS.FirstWake.WaterLandingRestore` test must cover both `Launched` rewind and same-beat `SeaContact` restore.

A separate native fixture must use disposable story-only saves to restore both an earlier `Launched` snapshot and a `SeaContact` snapshot while the hull remains immersed. Verify contact reacquisition and two fresh stable seconds after each restore, dry/fast/interrupted-contact cases, actual save results, unchanged player-save hashes, and clean tracked source. Do not use genuine player saves. Native UHT/build, automation, real quickload/overlap behavior, and physical seawater acceptance remain **NOT TESTED for this change** in the Linux sandbox.

No merge, release, packaged-runtime, cinematic-art, or Chapter 1 completion approval is implied.

## Connected Windows MSVC source review — 2026-11-02

A separate, disposable Windows checkout at exact PR #717 head
`fc746719f7ccfee213e5dfb21dfdc632ae43158b` adds a narrow MSVC
fallback to `check_water_landing_rewind_compiled.py` (review-only child branch
`review/ue58-firstwake-water-msvc-20261102`). Using the installed VS 2022
Build Tools developer environment, `python -B
unreal/Tools/check_water_landing_rewind_compiled.py --self-test` compiled and
executed the production state/gate C++ and repository water-test bodies:
**310 assertions PASS**. The deliberately removed restore-generation guard
compiled and failed the exact expected same-beat regression assertion.
`python -B -m unittest discover -s unreal/Tools -p 'test_*.py'`
completed **123 tests PASS**; `git diff --check` passed.

This adds Windows source-level portability evidence only. The host's existing
Unreal Editor sessions were left running and no full native build, UHT,
automation suite, physical water behavior, PIE quickload, or player-save file
was exercised. The original #717 candidate remains draft/unmerged, and
no prior native result transfers to this child branch.
