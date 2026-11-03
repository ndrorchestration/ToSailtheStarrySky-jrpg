# First Wake water landing — quickload rewind fix

**IMPLEMENTED, review-only; not native-verified.** This change is based on integrated draft PR [#713](https://github.com/ndrorchestration/ToSailtheStarrySky-jrpg/pull/713) at `52e13aedaa8bda900cece849b54eae570179c838`. It continues the existing Unreal Engine 5.8.4 project. Prior native build and 25-test receipts do not transfer to this changed source.

## Defect and correction

`LoadFirstWake` restores the current story object in place. After the water gate records `SeaContact`, loading a `Launched` snapshot can rewind that same object without changing the story pointer watched by `ATSTSSWaterContactAdapter`. The gate retained its old `bContactRecorded` flag and settling duration. While the hull remained immersed, later samples tried to advance directly from `Launched` to `FlotationConfirmed`, which the ordered story correctly refused. Progress remained stuck until contact was lost or the gate otherwise reset.

`UTSTSSWaterLandingGate::Observe` now discards contact and settling evidence when it sees a previously recorded contact paired with a story rewound to `Launched`. An eligible new water observation can reacquire `SeaContact` in the same call. Flotation still requires a full two seconds of fresh stable samples. Dry observations, excessive vertical speed and invalid samples retain their existing rejection/reset behavior. No story transition is bypassed.

This fixes gate bookkeeping; it does not create water overlap, real buoyancy or a playable flight scene. The seven-stop Prelude V2 review map has no flight or water section, so this is not evidence that its manual P01–P13 scenarios were executed.

## Executed source checks

The new `unreal/Tools/check_water_landing_rewind_compiled.py --self-test` compiles the actual production state/gate headers and implementations and both existing repository water automation test bodies with narrow Unreal API stand-ins. It passed **285 assertions**, including same-object rewind with continuous contact, rejection of incomplete restore data, exact two-second fresh stability, restored SeaContact, and 11 interrupted-rewind scenarios. Removing the new guard still compiles but fails the expected `Rewind immediately reacquires SeaContact` behavioral assertion. Hosted source preflight now runs this harness.

The local pre-existing Python source suite passed **123 tests**. Existing compiled objective (16 cases), F5/F9 (12 cases), save overwrite protection (10 cases) and DesignOnly combat adapter (22 assertions) checks also passed. Required native registration remains **25 names**, unchanged; registration is not execution. Dependency declaration and design-only relative stat gates passed. No engine, package, plugin, lockfile, save schema, approved art, recruitment canon, Starbourne gate or protected-main change was made.

## OPEN — native follow-up

In a separately authorized disposable UE 5.8.4 checkout at this candidate's exact head, run the native Win64 Editor build and all 25 named automation tests. The extended `TSTSS.FirstWake.WaterLandingRestore` test must pass in the actual engine. Keep source custody and per-run evidence retention checks intact.

A separate native physics fixture must then save a disposable story-only slot at `Launched`, establish actual hull/water contact, load that save while the hull remains immersed, and demonstrate contact reacquisition and two fresh stable seconds before flotation. Verify dry, fast-moving and interrupted-contact cases, actual save results, unchanged player-save hashes and clean tracked source. Do not use genuine player saves. Native UHT/build, automation, actual quickload/overlap behavior and physical seawater acceptance remain **NOT TESTED for this change** in the Linux sandbox.

No merge, release, packaged-runtime, cinematic-art or Chapter 1 completion approval is implied.
