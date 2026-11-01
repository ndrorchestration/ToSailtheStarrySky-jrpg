# Aureate Wake — approved-reference body intake on the single four-mount actor

**2026-11-01 | Unreal Engine 5.8.4 | Draft, source-only until native verification**

This review candidate starts at exact [PR #669](https://github.com/ndrorchestration/ToSailtheStarrySky-jrpg/pull/669) head `fa718fdf4609f2db32cb8984149d9c4f0ed7bfa5`. It selectively ports the *behavioral contract* of the allowlisted body slots from [PR #668](https://github.com/ndrorchestration/ToSailtheStarrySky-jrpg/pull/668) at `b1d1fc52449efdff14de6d127cd8a16cca155537` without copying that branch's independent `WingRootSupports` rig or overwriting newer actor geometry.

The creator-approved ship art reference remains the original four-configuration image (1536×1024; SHA-256 `03e3d500d8998a1377502f5ea28da79cf3eaf3854ece833d7ac25b4e0b268e13`). **Approval of that picture does not approve a new Unreal mesh.** The reference calls for a long ivory/white pointed hull, brass/gold accents, blue surfaces, translucent iridescent dragonfly wings, open front deck and panoramic geodesic bridge.

## Implemented on this candidate (NOT a finished ship)

- Adds `bUseAuthoredBodyReview`, default `false`, and optional `AuthoredHullReviewMesh` and `AuthoredBridgeDomeReviewMesh` slots. Separate `bBodyReviewApplied` state prevents an editor-facing checkbox from being confused with a successfully applied mesh pair.
- `RefreshBodyReviewMeshes()` rejects incomplete pairs, an active form transition, Orbiter, missing wing/mount/foil components, or simultaneous `bUseHullSilhouetteReview`. Both meshes must be loaded from *exact* review-only prefixes `/Game/TSTSS/Review/ShipArt/HullCandidateV1/` and `/Game/TSTSS/Review/ShipArt/BridgeDomeCandidateV1/`. **No mesh replacement occurs before both validations pass.** The method returns false outside UE Editor builds.
- With validated assets, replaces the two original box placeholders for visual study only. No collision, buoyancy, mass, engine tuning, First Wake narrative, save state, or production-art promotion is introduced.
- Turning off the requested mode restores both exact original cube meshes and transforms. The 4-section curved profile study remains a separate default-off alternative; both review modes cannot be enabled together.
- Keeps precisely four `WingRootMounts` (also the optional +X authored 100cm GLB support adapter from #669), two `HydrofoilStruts`, four dragonfly wings and two hydrofoils. The separate #668 four-component `WingRootSupports` implementation is deliberately NOT imported.
- `RequestForm` rejects routes into/out of Orbiter if either visual review mode is requested or if a previously authorized body candidate is still applied, even when `bAllowOrbiterPreview` is manually enabled.

## Tests staged

- Native automation extends existing `TSTSS.Ship.PreviewFormsAndOrbiterHold` with default-disabled check; empty and invalid asset rejection; both original meshes unchanged after failure; mutually exclusive review modes; reset; and Orbiter hold even when the preview toggle is forced true.
- Host-run `unreal/Tests/test_aureate_body_integration.py` supplies **12 source contracts** for opt-in, atomicity/provenance, fail-closed package execution, component cardinality and native test coverage.
- GitHub's Unreal source preflight workflow executes the source contracts. These **are not equivalent to Unreal C++/UHT compilation or rendered QA**.

## Native acceptance still required

1. Isolated exact-head Windows UE 5.8.4 Editor build with single compile worker; retain compiler/UBT output and exact SHA.
2. Headless full `Automation RunTests TSTSS` including the single ship test; report test count, identity, exit code and JSON receipt.
3. Generate or import authored **noncanonical** hull and geodesic bridge candidate meshes only to the two allowlisted review folders; verify original source images, imported orientation, dimensions and material provenance.
4. Inspect four-angle real GPU Skyborne, Seaborne and Submersible captures with full body and a deliberately null/invalid body assignment. Test fallback meshes/positions pixel/camera consistently and verify the two new hydrofoil struts visually.
5. Analyze 6 ordinary directed form transitions for swept clearances, deck/bridge obstructions and the prior wing-root mounting gap. An image or discrete pose set is not continuous collision proof.
6. Obtain creator artistic acceptance only after the model is demonstrably faithful to the approved drawing. Keep Orbiter held and preserve the hidden lunar reveal gate.

**Current workstation:** authorized `neontic` is offline, so native compilation, importer execution, GPU captures, artistic review and release readiness are NOT established at this head. No protected merges, launch or public deployment.

[Cross-branch Notion checkpoint](https://app.notion.com/p/40bf5bad238b81e3a3b0e0cbfa61ec6d) • [Approved-art branch reconciliation](https://github.com/ndrorchestration/ToSailtheStarrySky-jrpg/blob/fa718fdf4609f2db32cb8984149d9c4f0ed7bfa5/unreal/Docs/AUREATE_APPROVED_ART_BRANCH_RECONCILIATION_2026-11-01.md).
