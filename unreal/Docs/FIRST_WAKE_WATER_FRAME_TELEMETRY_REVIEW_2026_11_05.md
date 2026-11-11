# First Wake physical landing — opt-in per-frame evidence review

**Stacked on draft [#773](https://github.com/ndrorchestration/ToSailtheStarrySky-jrpg/pull/773) at parent `d0d9d5b235e0e4f70ee033f78be87a31239ff15c`.**
This is a **review-only measurement tool**, not new gameplay or released physics.

## Why

The prior exact-head actual D3D11 PIE accepted all 10 First Wake review
milestones and reached the post-flotation story objective. Story code and a
two-second landing gate support that result, but it did not produce **direct
per-frame measurements** of actual tagged water overlap, physical hull
submersion, vertical velocity or uninterrupted stability. The next P0 gate
requires measurements, not another summary based only on an objective.

## Controls and data

An **editor-only, default-OFF** CVar is available in the exact-head Unreal
Editor process, for use only with the disposable `FirstWake_LaunchWaterGreybox_V1`
map and its `bArmPrototypePhysicsOnLaunch=true` actor:

`tstss.FirstWake.WaterTrace 1`

Use Unreal's in-Editor console or a protected Editor launch with the console
command configured. Set it to `0` to disable if still playing. The CVar
never enters shipping code. Before launch it records up to **30 dry samples**
at a maximum of once per second: editor world-time, story start/beat,
physics OFF, hull Z, stable timer zero and story generation.

After real player launch, it records at most **6000 native physics frames**
with `TSTSS_WATER_REVIEW_SAMPLE phase=PHYSICS`, containing world time,
delta, hull center/bottom Z, tagged-water surface Z, actual overlap,
immersion, submersion fraction, physical vertical speed, stable timer,
story beat before/after, physics enabled and restore generation.
Observations occur **after** the unchanged `Gate->Observe` call.
The logger cannot grant progress, change collision, alter forces, turn
on physics, write saves or unlock a ship configuration.

## Fail-closed acceptance of a *new native* run

1. Use a NEW disposable exact-head source worktree with a separately
   hash-verified NEW review map and Win64 native module binaries.
   Never overwrite saved native screenshots/reports or protected production
   maps/configuration. Require 6.5 GiB physical free RAM, 14 GiB disk
   reserve and no other Unreal Editor/Live Coding process.
2. Verify this head with real Unreal Engine 5.8.4 Windows Editor build and
   29 native automated checks. Source-only or API-double tests cannot count.
3. Enable the CVar BEFORE real PIE starts, capture prelaunch dry frames and
   all postlaunch physical frames in an independent, uniquely named native
   Editor log. Run actual W/E game input through engineering, launch,
   flotation and empty-reserve inspection. Do not teleport or drive state
   artificially.
4. In a separate read-only validation, invoke
   `python unreal/Tools/verify_first_wake_water_frame_trace.py
   --checkout <isolated-worktree> --log <native.log>
   --map <review.umap> --head <40hex> --map-sha256 <sha256>
   --out <unique-ignored-Saved-receipt.json>`.
   No output overwrite is allowed. It must observe real PIE login,
   dry/sim-disabled prelaunch samples, a **unique** native
   SeaContact(5)->FlotationConfirmed(6) transition, and at least
   two *continuous* seconds of measured tagged overlap, hull immersion,
   speed within 25 cm/s, finite 0–0.25s frames and unbroken world-time
   sampling of a single restore generation.
5. Prove additional negative controls separately: prelaunch never falls,
   jumping state order/false volume cannot count, SaveGame restore invalidates
   old contact, and a no-water scenario cannot advance to Flotation.
   Preserve original receipt when a check fails.
6. Document both strengths and limitations. This still does not establish
   a player-controlled Aureate Wake flight, final cinematic ocean physics,
   approved art, disk restart or release.

**No live PIE trace receipt has yet passed merely by introducing these
source files.** The synthetic parser tests are named synthetic and MUST
NOT be promoted as physical evidence.
