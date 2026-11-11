# First Wake physical water witness: post-transition versus pre-transition

**Parent review code:** [draft PR #774](https://github.com/ndrorchestration/ToSailtheStarrySky-jrpg/pull/774), Unreal 5.8.4 source `83cd089f54cc5c1a3f16d80036b9bf64bd3d1152`.

## Actual retained evidence
From the disposable D3D11 Play In Editor review log
`C:\TSTSS_WaterTracePIE_20261105\TSTSS_FirstWakeSplashdownSandbox_20261103\unreal\Saved\WaterTracePIE\water-frame-real-walk-20261105-v2.log`,
SHA-256 `8f11b0dce22fcb35fb99d88627de11003f77504417734e090f3e4400a78db9e8`:
- Prelaunch physics disabled: 30 native dry frames, `sim=0`.
- 1,775 real hull-water physics frames, explicit editor trace CVar enabled.
- The original gate reported `stable_sec=2.0312` at precisely one
  `SeaContact(5)->FlotationConfirmed(6)` native frame at world 232.0485 s.
- A separate strict **pre-transition** replay observed only 1.9943 s
  between its first fully qualifying sample and that transition. The
  earlier sample was too fast (25.231 cm/s). Thus the independent
  **pre-transition two-second** claim remains **HOLD**.
- Independent direct-sample diagnostic found one continuous
  post-transition segment from 232.0485 s through 290.9174 s:
  58.8689 elapsed world seconds with valid tagged-water overlap,
  actual hull immersion, native simulation and vertical speed within
  25 cm/s, without a missing/inconsistent frame gap.

## New validator scope and tests
`unreal/Tools/verify_first_wake_postflotation_stability.py` independently
checks exactly one native story flotation transition, CVar enabled, actual
PIE player login and **all 10 ordered native player interactions**.
It then checks actual contiguous physical frames **starting from the
first fully qualifying sampled flotation-transition endpoint**, and
requires at least two measured world-clock seconds *after* that boundary,
with each frame's `dt` agreeing within measurement rounding, one
restore generation, tagged water overlap, immersion, hull below surface,
submersion >0.01, physical simulation and |velocity| <=25 cm/s.

The validator explicitly preserves the separate pre-transition result.
**Post-flotation stability proof must never be presented as direct proof
that every fraction of the game's *pre*-transition two-second gate was
sampled.** Native gate report and post-event physical stability are
independently valuable, but not interchangeable.

Test fixtures are synthetic positive and negative guards only, not
real game evidence. A verification result is grounded only when the
validator's exact Git head, the **separate** capture Git head, original
saved review map SHA, unmodified UE native log SHA, and no-overwrite
result receipt all agree.

## Still out of scope
No player-piloted Aureate Wake flight, cinematographic splashdown,
approved ship/character/ocean visuals, full disk save/restart/Continue,
or production integration is claimed. Existing maps and saves remain
unchanged, all candidate PRs draft/unmerged; Starbourne locked.

The dedicated strict PRE-transition evidence gate remains open and
requires revised **future native observations** or a genuine extra
sampling interval rather than retrospective smoothing, rounding, or
lowering the two-second threshold.
