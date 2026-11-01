# Aureate Wake — Authored root-support adapter integration (2026-11-01)

**REVIEW ONLY • NONCANONICAL • NATIVE BUILD/RENDER UNVERIFIED**

This stacked source candidate begins at draft PR #661 exact head `d443c68df7fd8f36a8a7ecafb9cb5b0162362c8d` and selectively incorporates the root-support art generator, import preflight, and tests from draft PR #631 exact head `a0be9dec82514d6c45314c0ff7d54a3f7356f96b`.

## Implementation decisions

The previously integrated actor already exposes four noncanonical `WingRootMounts` components. PR #631's actor variant separately adds four `WingRootSupports`. Combining the actor versions wholesale would create eight visible support elements, duplicate visual/animation authority and reintroduce older code. **This adapter adds zero components.**

- `AuthoredRootSupportMesh` is optional, null by default. The engine's original Cube remains the fallback visual support.
- `RefreshRootSupportReview()` deliberately reuses `UpdateWingRootMounts()`; the existing snap and interpolation routines continue to own all four transforms.
- The authored asset is exactly 100 cm long along *local +X*, rooted at the *inboard* end. When explicitly selected with a reviewed authored wing and root-pivot pose, a support's location is the hull-side anchor and its scale becomes `(span/100, 1, 1)`. This differs from the centered Cube stand-in, which stays centered between the hull and wing and uses `(span/100, .09, .09)`.
- Support visibility requires the existing four-wing authored review setting and a non-Orbiter transition. The optional support mesh alone cannot enable a wing or unlock any mode.
- Opt-in curved-hull silhouette from PR #661 uses the provisional ±56 cm local anchoring study; fallback hull uses ±72 cm. Neither is a verified mechanical load path.
- The imported GLB is review-only; importer checks name, SHA-256, 100 cm in meters, materials and luminous details and refuses overwrite of occupied review destinations.
- No changes to combat, story, First Wake, water-contact authority, physics, saving, release or canonical art.

## Source evidence and limits

- Source GLB generator and importer were copied without alteration from PR #631 and their donor Git blob identifiers are recorded by the commit history.
- Source tests have been adapted to assert reuse of the existing *four* `WingRootMounts` rather than expecting PR #631's separate four-element rig.
- The complete native C++ preview automation adds checks that the support property defaults to null, an optional review placeholder does not increase wing/mount counts, and authored-wing Orbiter movement remains refused.
- GitHub workflow includes the hull/canopy source contract test plus root-support GLB generator/import tests; CI evidence is required for this exact branch. A hosted PASS is **not** an Unreal native compile.

## Acceptance gates

1. Hosted source tests for generator (10 cases), importer (8 cases), optional hull contracts and Unreal automation registry.
2. A clean **UE 5.8.4** Editor Win64 compile at the exact branch head, followed by headless `Automation RunTests TSTSS` with per-test JSON results.
3. Import review support GLB to `/Game/TSTSS/Review/ShipArt/RootSupportCandidateV1` in isolated Editor, without replacing approved assets. Confirm 1 meter local X with correct origin, 3 material sections, and compatibility with four existing bracket components.
4. Capture native D3D12 screenshots of Skyborne, Seaborne and Submersible with and without the mesh; verify all four mount attachments and two hydrofoil struts. Document material fidelity and any lighting artifacts.
5. Test all six ordinary form transitions against actual geometry across the full movement interval. Geometric sampling alone is not continuous swept collision proof.
6. Do not unlock Orbiter, promote art, merge into protected branches, publish a build, or declare complete ship fidelity without explicit creator review.

**Machine status:** Remote Desktop Commander was offline during this source integration. Native build, import, render, collision and creator art approval are **not established** for this new branch.
