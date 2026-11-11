# First Wake P0-3 — launch-armed provisional hull gravity, review-only

**Issue:** #754 P0-3 physical launch and splashdown. **Source parent:** draft #763,
exact `baba204d403723886b5dc01357e48bbd12cbfe0d`. Separate source-only
worktree: `C:\TSTSS_LaunchChronology_20261104`.

## Why this is necessary

The existing opt-in `build_first_wake_splashdown_greybox.py` generated a
prototype hull with physics **already enabled** in the saved review map.
That hull could fall into the water volume before the real player interacted
with `LaunchMarker`. Later reaching `Launched` could then use an already
floating hull as contact evidence. This is a **source-level chronological
risk**, not a claim that a native UE water test reproduced it.

## Narrow, reversible change

- **Default-off** `ATSTSSWaterContactAdapter::bArmPrototypePhysicsOnLaunch`
  affects only explicitly opted-in noncanonical review worlds. Other maps
  retain their old water-adapter behavior and Story/SaveGame format.
- The authored greybox hull is initially **non-simulating, dry and movable**.
  Only an actual player-associated story with `HasStarted()` and an ordered
  beat at least `Launched` arms the hull for gravity and buoyancy.
- On story replacement, `Reset()` or `Restore()` generation change, the
  prototype resets to its original dry transform and resets the contact
  gate before any new physics sample. On a prelaunch beat, it stays dry.
- Real overlap with the tagged water volume, physical hull immersion,
  velocity, and the original two stable seconds remain required for
  `SeaContact` / `FlotationConfirmed`. No code grants them automatically.
- No new map is authored or saved by these source changes. The original
  V2 `.umap`, player saves, production gameplay/actors, locked Starbourne
  and human-approved art remain untouched.

## Tests executed and limits

- Full source suite: **252/252 PASS**.
- Source-only `--validate` greybox authoring plan: PASS; still reports
  `real_physics_verified=false`, `native_build_or_pie_tested=false`.
- `git diff --check`: PASS.
- On Neontic using installed Visual Studio MSVC, extraction of the **actual
  adapter `Tick` body** under C++ API doubles compiled and passed **16**
  assertions, including no prelaunch physics, launch arming and rewind
  reset. **5/5 safety mutations** were detected as failures, including
  intentionally bypassing the launch gate and skipping dry reset.
- This is **not** a native Unreal build, editor component binding,
  in-engine collision/overlap, rig, physical buoyancy or splashdown proof.

## Next native review (HOLD while another user Editor remains open)

1. Use new isolated `TSTSS_FirstWakeSplashdownSandbox_20261103` only,
   with exactly bound source head and original-map SHA. Never run the
   `--build` path on the user-owned working game.
2. Guard for no other Unreal/Live Coding process, >=6.5 GiB available
   physical RAM, >=14 GiB disk reserve, no existing SaveGames, clean tracked
   source and pristine protected config/map hashes. Do not terminate the
   existing user session to make room.
3. Compile current head in actual UE5.8.4 Win64, run native 29-test suite
   and add an explicit guarded source-to-private-map asset custody receipt.
4. Author the **new** review water lab exactly once; independently reload
   `.umap` and verify the hull starts dry and non-simulating, movable,
   `bArmPrototypePhysicsOnLaunch=true`, with tagged overlap-only water.
5. PIE negative path: remain before `Launched` long enough to prove hull
   stays dry; test Reset/Restore and stale contact. Record transforms and
   actual native physics state, not source assertions.
6. PIE positive path: authorize launch with real input; observe the hull's
   new gravity-driven water overlap, physical immersion, velocity settling
   and **>=2 continuous seconds** stable flotation. Verify progress to
   Chapter 1 Act 1 only from the physics gate, never from a marker.
7. Confirm actual disk save/restart/F5-F9 separately, and then begin
   cinematic ship, ocean and camera integration. No Lyra before splashdown.

**Current status: SOURCE REVIEW ONLY.** The game's 7/7-engineering-marker
review result is a separate verified milestone on #763. This patch does
not prove a completed physical launch, splashdown, flight or release.
