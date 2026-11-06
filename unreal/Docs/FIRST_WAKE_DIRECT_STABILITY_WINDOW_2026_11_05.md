# First Wake: directly observed water stability interval (review candidate)

Parent development integration: draft [#781](https://github.com/ndrorchestration/ToSailtheStarrySky-jrpg/pull/781), exact base `58ff9752a0729b1527d7a8bfbcdbfb36f3b68bee`. This is a separate, draft-only water-timing correction; no protected-main, approval, release or production SaveGame change.

## Measured failure of the earlier proof claim

The saved UE 5.8.4 D3D11 PIE trace at historical source `83cd089f54cc5c1a3f16d80036b9bf64bd3d1152` has a native gate timer **2.0312 s** on the SeaContact → FlotationConfirmed transition, but the strict independent pre-transition validator finds only **1.9943 s of directly observed, consecutive qualifying frames**. A preceding sample had a vertical speed of **25.231 cm/s**, above the 25 cm/s limit. A first newly qualifying sample cannot grant the unobserved previous frame's delta. Do not round either value, relax the timing threshold, or substitute 58.8689 s post-transition for pre-transition evidence.

## Source change

The water gate now treats the first stable/immersed qualifying frame as the **start** of a witnessed window and assigns zero observed elapsed time. Each subsequent consecutive qualifying frame contributes only its own valid `DeltaSeconds`. No story transition occurs until at least **2.0 observed seconds** have elapsed between qualifying samples.

- A dry contact gap, out-of-range delta, nonfinite speed, >25 cm/s vertical motion, Restore generation change, or full Reset invalidates the first-sample anchor and elapsed observed timer.
- Original authority remains intact: only the native water gate can advance SeaContact/FlotationConfirmed. An interaction marker never can.
- This fix does not assert that the exact game-world clock matches every input delta; native per-frame timestamp/delta consistency still requires the independent validator.
- No change to buoyancy force, water volume, approved hull/wing geometry, cinematic renderer, save schema, game-menu control, party, Lyra recruitment or locked Starbourne.

## Verification requirements (fail closed)

1. Run the full Python/source suite, production-source extracted portable C++ rewind harness with negative mutations, and input/adapter behavioral harnesses at the **exact new head**, preserving outputs.
2. On NEONTIC, require free physical RAM >=6.5 GiB and C: free disk >=14 GiB **before** starting one native Editor/UBT/GPU workload. Do not bypass the Windows lock screen, kill another user's app or reset host-generated config without custody.
3. Same-head Unreal Engine 5.8.4 native Win64 Editor build and **29/29 automation tests**, especially WaterLandingRestore, WaterLandingNegativePaths, InteractionToSplashdown and restoration/collision assertions.
4. Isolated exact-head real D3D11 PIE, with opt-in water telemetry, hash-verified review map, actual W/E ten-stop traversal, `F6` (PIE) save → advance → `F9` restore → replay. Record original physical time series and a strict *pre-transition* qualifying window >=2.0 elapsed world seconds, without interpolation.
5. Confirm separate post-flotation stability, no stale contact after rewind, preserved config bytes, zero unexpected saves, and independent source/map/log/receipt hashes. Native validation of this correction remains **NOT ESTABLISHED** until executed.

A native Editor sandbox at #781's parent source was launched on NEONTIC after resource admission, but Windows was at the lock screen; no actual PIE/player-input pass was possible, the review Editor closed gracefully, and disk headroom later fell below the reserve. Do not transfer #779's F5 replay or #781's prior 29/29 native receipt to this new commit.

**Disposition: DRAFT / REVIEW ONLY — no merge or direct two-second acceptance claim before exact-head native evidence.**
