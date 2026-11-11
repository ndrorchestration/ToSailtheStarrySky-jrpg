# P0-3 consumed splashdown review marker collision — review-only

## Exact source and scope
Stacked on [draft PR #767](https://github.com/ndrorchestration/ToSailtheStarrySky-jrpg/pull/767)
at parent `0cd94702ec517d85be0d6ca5fe51855959e09fe9`.
Isolated worktree: `C:\TSTSS_P0ConsumedMarkerFix_20261105`.

The previous exact-parent UE5.8.4 D3D11 PIE session accepted all 10 review
milestones, but after real launch an E press was *denied* by a previously
consumed `TSTSS_SPLASHDOWN_GREYBOX_LaunchMarker`. Unlike original
`TSTSS_PRELUDE_REVIEW_` markers, new splashdown markers did not release
their visibility and pawn collision. The reviewer could continue only by
walking around the consumed launch marker.

## Minimal bounded fix
`ATSTSSMilestoneActor::TryActivate` now accepts either **explicitly
review-only** actor-label namespace inside the existing conditional. Only
AFTER `State->InspectStation` or `State->AdvanceTo` succeeds, only
`WITH_EDITOR`, only `WorldType == PIE`, and only if the native mesh is
valid, it changes just `ECC_Visibility` and `ECC_Pawn` responses to
`ECR_Ignore`. All failed/out-of-order encounters remain solid; production
labels, non-PIE worlds, physics water contact, SaveGame schema, protected
maps and the four ship forms are unchanged. No blanket
`SetCollisionEnabled(NoCollision)` is permitted.

## Acceptance gates
1. Python source tests must confirm both names under ONE PIE-only gate
   and collision changes happen only after story acceptance.
2. The existing native First Wake interaction automation must spawn actual
   transient PIE-world milestone actors. Verify accepted review LaunchMarker
   ignores both channels, rejected out-of-order LaunchMarker keeps blocking,
   and an accepted nonreview actor keeps blocking.
3. Bind Windows Unreal 5.8.4 native C++ compile and 29-test automation
   results to a new exact source SHA. Never reuse #767 parent SHA results.
4. In a NEW disposable exact-head map session, prove real keyboard W/E
   launch then E at the *consumed* marker does not deny via the old cube,
   and the next EmptyReserve marker is reachable without lateral detour.
   Check camera hit actor, pawn reach, original map/config bytes, and a
   fresh renderer screenshot. Source tests alone do not prove this step.
5. Record native outcome and limitations before proposing merge. No
   production art acceptance, disk persistence, starbourne unlock,
   physical-water time-series proof or release implied.

Source-only result recorded separately from native run. Do not load or
overwrite the previous `FirstWake_LaunchWaterGreybox_V1.umap` proof map.
