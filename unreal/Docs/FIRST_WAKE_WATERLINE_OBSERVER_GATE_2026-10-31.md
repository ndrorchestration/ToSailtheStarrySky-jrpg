# First Wake — Waterline Contact Predicate and Alternate Observer Fail-Closed Gate

Date: 2026-10-31. Status: **DRAFT ENGINEERING PROOF — native Unreal 5.8 not compiled or run; no sea-landing acceptance**.

## Why this change exists

The current first-wake integration has two separate proposed water observation pathways: the main `ATSTSSWaterContactAdapter` and the ship's optional `UAureateWakeWaterObserverComponent`. The main adapter checks a physical hull below an authored water-volume top surface in addition to overlap, but the secondary observer previously passed **mere component overlap** directly into `UTSTSSWaterLandingGate::Observe`. A volume may overlap the hull without the hull crossing the waterline, which could advance `SeaContact` or prematurely switch the ship to Seaborne.

## Production code fix, without changing canon

- `UAureateWakeWaterObserverComponent::bEnableStoryWaterObservation` defaults to **false** and must be deliberately enabled only after native level wiring confirms a **single** authoritative water observer. This opt-in is not a runtime mutex or a claim the two systems can never both be enabled.
- When explicitly enabled and correctly connected, the observer reads **physical hull** and **water collision** component world-space bounds, requires real `IsOverlappingComponent`, rejects invalid or degenerate boxes, and only calls `LandingGate->Observe` with `bTouchingWater=true` when hull lower Z is strictly below water top Z. This is a conservative **axis-aligned bounds screening** of an authored collision volume, *not* wave, dynamic ocean surface, Chaos rigid-body penetration, or hydrostatic buoyancy.
- Existing `UTSTSSWaterLandingGate` retains sole authority to call `AdvanceWaterBeat`. Accepted story contact still precedes the visual `RequestForm(Seaborne)`. The main `ATSTSSWaterContactAdapter` and all canon/party, combat, saves and First Wake beats are unchanged.
- Invalid/absent samples reset the secondary observer's local stability accumulator; a disabled observer never touches the story or visual ship.

## Two independent executable C++ checks

1. `unreal/Source/ToSailTheStarrySky/Public/TSTSSWaterlineGeometry.h`: header-only, standard C++17 `HasMeasuredHullWaterlineIntersection` used directly in the actual Unreal observer. It rejects non-finite centers/extents, non-positive extents, bounds arithmetic overflow and hull overlap with no lower-bound waterline penetration.
2. `unreal/Tests/native_waterline_geometry_test.cpp`: **16 executable cases** compiled and run with a hosted real C++ compiler using that **same production header**. Tests overlap-only false contacts, actual penetration, tangent, finite/NaN/Infinity/overflow, and invalid extents.
3. `unreal/Source/ToSailTheStarrySky/Private/Tests/TSTSSWaterlineGeometryTests.cpp`: registered additional Unreal-native automation `TSTSS.FirstWake.WaterlineGeometry`, and `unreal/Tools/Verify-Unreal.ps1` updated to require it as part of engine-native verification. **Registered does not mean executed.**
4. Updated `unreal/Tests/check_aureate_water_observer_source.py` and `test_integrated_first_wake_ship_authority.py` to require explicit enablement, actual geometry screening and correct ordering before the water/story gate.

Run numeric C++ outside Unreal:

```bash
c++ -std=c++17 -O2 -Wall -Wextra -Werror -pedantic \
  -I unreal/Source/ToSailTheStarrySky/Public \
  unreal/Tests/native_waterline_geometry_test.cpp \
  -o /tmp/tstss-waterline-test
/tmp/tstss-waterline-test
```

GitHub's integrated review workflow compiles and runs this program before other source/asset gates. Preserve any failed job evidence; verify actual success against the exact commit.

## Still requiring real Unreal level acceptance

- Confirm UE5.8 Windows C++ build and native automation result.
- Wire exactly **one** observer to the ship story in an isolated test map; fail closed on a deliberate accidental double-wire. This cannot be certified through this source-level opt-in alone.
- Test large water volumes overlapping hull before waterline contact, surface tangent, wave reentry, high-speed splashdown, stationary flotation for 2 seconds, and save/restore without a false event.
- Use real measured hull/world-space velocity and an actual authored water physics/collision volume, never ocean presentation meshes or a cinematic cue.
- Capture native level contact traces, screenshots/video and scope of any experimental buoyancy; avoid promotion or installer change without owner approval.

Developer note: [Unreal Editor Actor Scripting API 5.8](https://dev.epicgames.com/documentation/en-us/unreal-engine/python-api/class/EditorActorSubsystem?application_version=5.8). The actual engine validation and game-art approval are outstanding.
