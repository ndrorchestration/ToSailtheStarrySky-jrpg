# Aureate Wake — body/primitive review visibility precedence (2026-11-01)

**Draft-only reversible Unreal 5.8.4 source review. Native C++/UHT, Editor tests, GLB import and D3D12 renders are NOT established for this candidate.**

## Defect found

In parent [PR #680](https://github.com/ndrorchestration/ToSailtheStarrySky-jrpg/pull/680) at exact tested source head `b397a683c9c83d2ba14da6f34205adb415091aec`, the actor tracks both requested `bUseHullSilhouetteReview` and actual `bBodyReviewApplied` after a validated hull+bridge mesh pair has been installed. The original `UpdateHullSilhouetteVisibility()` made the *request flag* alone control visibility. Changing that flag in the editor **after** body application could turn off the applied hull/bridge and show the primitive sections, despite `RefreshBodyReviewMeshes()` correctly rejecting the conflicting request.

This breaks the visual representation/actual applied-state correspondence, and the root-support anchor computation separately followed the raw toggle. The problem is an observed **source-level state defect**, not a proven screenshot or Unreal runtime defect.

## Minimal mitigation

- Add a tiny pure C++ predicate `ShouldShowPrimitiveHullStudy(requested, applied)` returning `requested && !applied`.
- Apply this single rule to the hull, bridge, four primitive sections, 40 geodesic-study frame bars, optional canopy shell and four wing-root anchoring calculations.
- A previously applied authored body stays visible, even when an editor user requests an incompatible primitive study; the already existing `RefreshBodyReviewMeshes()` still rejects conflicts and does not mutate mesh assignments. An explicit successful body rollback restores the original fallback mesh geometry; only then can a requested primitive review become visible.
- Do **not** change gameplay, form transition timing, 4 wings, 4 root mounts, 2 hydrofoils, 2 hydrofoil struts, combat, First Wake, save state, or Orbiter authorization.

## Tests and acceptance

- Native `TSTSS.Ship.PreviewFormsAndOrbiterHold` source now checks the four-state truth table: neither requested/applied, requested only, applied only, and both.
- Existing hull and root-support source tests were updated for the coherent visibility predicate.
- New `unreal/Tests/check_aureate_preview_visibility_cpp.py` extracts the **real predicate from the actor header**, compiles it with an available host C++ compiler and evaluates all four cases. It also verifies that both the rendering-visibility path and root-anchor geometry path actually use the tested predicate. It is wired into the hosted Unreal source preflight workflow.
- Host C++ extraction is not native Unreal C++ or a physical/cinematic artifact; native UE 5.8.4 Editor/UHT compile and `Automation RunTests TSTSS` at this exact branch, plus genuine D3D12 visual comparison of state transitions, remain mandatory.
- The source test **must fail closed** if no host compiler is available or if the extracted method/production use is absent.

**Review boundaries:** parent [PR #680](https://github.com/ndrorchestration/ToSailtheStarrySky-jrpg/pull/680); creator-approved ship art [PR #668](https://github.com/ndrorchestration/ToSailtheStarrySky-jrpg/pull/668); current project status in [Notion](https://app.notion.com/p/40bf5bad238b81e3a3b0e0cbfa61ec6d). No merge, release, art approval or Orbiter unlock.
