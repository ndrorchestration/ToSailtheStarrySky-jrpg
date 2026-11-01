# Aureate Wake — Opt-in hull silhouette and geodesic-frame study (UE 5.8)

**Status: SOURCE-SIDE REVIEW CANDIDATE; NATIVE BUILD/RENDER NOT YET VERIFIED.**
Based on draft PR #656 at exact head `61e02fd2fbdcd5ae59078867b5f37f54d6e52a17`.
No merge, release, production art promotion, ship-physics change or narrative unlock is implied.

## What this changes

- Adds `bUseHullSilhouetteReview`, **false by default**. The already compiled original rectangular hull and forward bridge remain the default visual. When opted in, both are hidden in favor of four review-only geometric sections: an overlapping curved mid-hull, a tapered bow, a tapered stern, and an open foredeck.
- Provides a forward bridge **triangulated frame study**, built from 40 short, named cube-beam components around two elliptical rings and a raised apex (8 segments x 5 beams). This is *geodesic-inspired proxy geometry*, not a mathematically exact frequency-defined geodesic dome or certified pressure vessel.
- Adds `OptionalCanopyGlassMaterial`. The separate spherical glazing envelope remains **hidden unless an artist supplies an actual material**; no stock opaque sphere is represented as finished glass.
- Exposes `RefreshHullSilhouetteReview()` for reversible editor lookdev and updates wing-root visual anchor approximations to account for the narrower elliptical hull. Root brackets and hydrofoil struts remain **visual proxies**, independent of any authored review asset from PR #631.
- Makes `FinishOrdinaryPreviewTransitionForReview()` return false in non-editor builds via `#if WITH_EDITOR`. This is an editor convenience, not an alternate gameplay or narrative form authority.

## Boundaries

The study adds no collision to the new sections or frame pieces; it changes no save format, combat rules, First Wake milestones, sea landing, or character data. The existing four dragonfly wings, two hydrofoils, and Orbiter failure gate remain intact. The optional hull profile does **not** imply structural continuity, correct membrane clearance, hull pressure resistance, water displacement or seaworthiness. It is not an art acceptance.

The separate PR #631 offers an authored, material-rich 100 cm wing-root support GLB. Its four-support model and the existing four bracket components must be **reconciled**, not blindly combined into eight root supports. No source or asset from #631 was merged in this change.

## Source checks completed

Eight static checks were evaluated against the exact GitHub branch contents: default-off, four hull sections, 40 deterministic ribs, no collision, material-gated canopy shell, original four-wing cardinality, Orbiter hold, and packaged review-method fail-closed. All eight source predicates passed.

A matching Python source contract file (`unreal/Tests/test_aureate_hull_canopy_source.py`) and added Unreal-native actor assertions are committed. **Neither the Python suite nor native C++ tests has been executed in the new branch yet**: Remote Desktop Commander disconnected before native verification could begin. Prior PR #656 native 13/13 and wing source 31/31 results apply to that older head only.

## Next verification procedure (review worktree only)

1. Create an isolated worktree from this branch, leaving any concurrent Unreal editor session and previous evidence directories unchanged.
2. Run `python -m unittest discover -s unreal/Tests -p test_aureate_hull_canopy_source.py -v` and the existing four wing source suites.
3. Run `Build.bat ToSailTheStarrySkyEditor Win64 Development -Project=<isolated-path>/unreal/ToSailTheStarrySky.uproject -WaitMutex -NoHotReloadFromIDE -MaxParallelActions=1` using the installed Unreal 5.8.4 compiler and SDK; record exact output and exit code.
4. Run headless `Automation RunTests TSTSS`; inspect exported JSON counts, not only process exit. Verify four silhouette sections and forty frame components are constructed, original preview remains default, and Orbiter remains inaccessible.
5. Using an isolated Unreal Editor scene, enable the silhouette flag, supply **only explicitly noncanonical** review materials and render a real D3D12 screenshot for Skyborne, Seaborne and Submersible at consistent camera angles. Compare the new profile against the approved artistic direction. Save exact source/import provenance, warnings and image hashes.
6. Check the 28 cm root mount issue and six ordinary directed form transitions for interference across real geometry before approving any visual replacement. Do not claim continuous collision proof from discrete samples.

## Release/acceptance gate

Native compiler: **NOT RUN**. New native automation: **NOT RUN**. New in-engine GLB/material import: **NOT RUN**. New hull/canopy render: **NOT RUN**. Collision proof and creator visual approval: **NOT ESTABLISHED**. Orbiter: **LOCKED**.
