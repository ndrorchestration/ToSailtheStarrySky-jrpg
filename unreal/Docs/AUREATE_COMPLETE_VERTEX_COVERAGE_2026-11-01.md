# Aureate Wake GLB clearance — complete vertex coverage requirement

**2026-11-01 · Unreal 5.8.4 workstream · REVIEW ONLY · ENGINE-FREE QA**

## Defect corrected

The existing `audit_aureate_wing_clearance.py` treated a requested per-primitive vertex budget as a *subsampling* limit. When primitive vertex counts exceeded that budget, the auditor omitted interior indices while still using sampled minima/maxima as a purported conservative wing bounding box. Such an AABB can be **too small** when an omitted vertex is extremal, so clearance results could wrongly pass.

This review branch makes the input policy **all positions or hold**. Each GLB primitive must have at least one position, and a position count at or below the declared maximum; every position is read. Counts exceeding the upper bound reject before calculating clearance. Accessor stride, declared view length, finite values and binary bounds are also checked. This change makes spatial coverage of the *given mesh* complete, but does not grant continuous motion clearance.

## Source implementation

- `unreal/Tools/audit_aureate_wing_clearance.py`: removes strided/partial position sampling; accepts legacy `--samples-per-primitive` for compatibility and introduces the accurate alias `--max-vertices-per-primitive` (default 20,000, allowed 100–50,000; still all-or-hold). Each budget is a **hard upper limit**, not authorization to estimate bounds from a subset. The JSON receipt adds `vertex_coverage: COMPLETE_POSITION_ACCESSORS_WITHIN_BUDGET`.
- `unreal/Tools/test_aureate_full_vertex_coverage.py`: seven engine-free synthetic GLB cases for complete enumeration including an extremal vertex; partial-over-budget refusal; empty accessor refusal; truncated declared position-view refusal; short stride refusal; nonfinite coordinates; unreasonable requested budget.
- `.github/workflows/unreal-source-preflight.yml`: executes these cases without Unreal, in addition to source registration and ship review-state checks.

## C++ ↔ offline pose parity contract

Added `unreal/Tools/test_aureate_pose_source_parity.py` and wired it into source-preflight CI. The offline GLB clearance entrypoint now imports its fail-closed `assert_pose_parity` check. It freezes the entire normalized (comments/whitespace ignored) C++ `RootPivotedWingPose` method. Any substantive pose change rejects old offline clearance evidence until independent C++/Python geometry reconciliation is explicitly reviewed. The checker also compares Python's four wing poses across Skyborne, Seaborne and Submersible (12 endpoints) and injects five deliberate negative mutations (root offset, Seaborne Z, Skyborne rotation, Submersible scale and Orbiter root) to exercise refusal.

This is an intentionally conservative <b>source synchronization gate</b>. It is not a mathematical proof that the independent Python transform, FRotator conventions, imported mesh axes, or runtime physics perfectly match Unreal; these must still be checked natively. Updating the pinned snapshot merely because a build fails is forbidden; review the actual change and revise the Python pose model and tests first.

## Review-only glTF scene-graph and accessor admission

The clearance auditor formerly read mesh-local positions without checking whether the imported scene applied a translation, rotation, scale, skin, animation, morph target or GLB extension. Such data can change rendered positions while leaving the offline AABB unchanged. The auditor now **refuses** anything other than the deterministic generator's single scene, single node, single mesh and untransformed/unskinned geometry; it does not silently ignore transforms. It also refuses sparse or normalized POSITION accessors, verifies each decoded position is within its declared buffer view, and recomputes each primitive's actual min/max to reject missing, nonfinite or mismatched declared extrema (tolerance 0.0001 glTF meter). This is conservative for review: alternative legitimate GLBs must be explicitly modeled and approved before the auditor can clear them.

The standard-library `test_aureate_full_vertex_coverage.py` suite now covers the canonical untransformed fixture and negative scene mutations (translation, rotation, scale, matrix, nested/duplicated nodes, skinning, animations, glTF extensions, morphs, sparse positions, additional meshes) and accessor metadata mismatches. The CI preflight executes the entire suite. **Engine-free PASS does not establish native Unreal Interchange transform handling, a rendered silhouette or swept collision safety.** The imported GLB's SHA and an actual Unreal mesh bounds review are still required.

## Authored-wing generator size gate — November 1 continuation

The actual procedural wing generator contains **292 membrane positions, 14,770 venation positions and 78 hinge positions** (15,140 total). The inherited 3,000-vertex default did not fit the wing's venation primitive after full-coverage validation replaced partial sampling; the auditor would hold the legitimate generated GLB even when its geometry was unchanged. The source now defaults to 20,000 vertices per primitive, retaining the 50,000 hard upper bound, no vertex subsampling, and the existing manifest/source-parity/scene-graph/bounds/Orbiter holds.

The engine-free fixture suite now calls `author_aureate_wing_glb.build()` and runs the **actual deterministic generated GLB bytes** through `read_vertices` at the default limit, verifying all three primitive counts against the generator's own manifest. This is stronger than relying only on synthetic fixture meshes, but is **not an actual Unreal import, visual acceptance, or execution of the six-route clearance screen**; the separate end-to-end clearance audit (with SHA-256 manifest and C++ source at a pinned head) is still required.

## Actual generated GLB: six ordinary routes, 126 sampled poses

`test_aureate_full_vertex_coverage.py` now uses the deterministic generator to obtain the **real authored review wing GLB**, reads all 15,140 positions, and runs the existing geometric auditor at its default **20 time intervals per directed transition**. The six directed Skyborne/Seaborne/Submersible transitions therefore cover **126 sampled configurations**, four wing instances per configuration, against the provisional hull/bridge AABBs and the other wings. A clearance below the existing 10-cm screen threshold fails CI. This supplements the synthetic malformed-GLB fixtures and exact-source C++ pose guard.

**Interpretation:** A passing engine-free fixture means the current deterministic procedural geometry does not trigger the auditor's sampled proxy-AABB overlap criteria at those 126 samples. It does NOT mean real GLB importer transforms or materials are verified, that every time between samples is safe, that the brackets and support spars are structural, or that the canonical vessel model is physically/cinematically approved. Direct authored-wing Orbiter transitions remain rejected, not screened.

## Provenance and evidence limits

- Exact parent is draft PR #660 at `5bbbfa8301396b58ca04538e66c4a43734eaadc3`, itself stacked on the native-tested foundation and ordinary-form review PRs.
- **No native Unreal Editor build, import, physical collision, swept-volume proof or renderer pass is claimed for this branch.** A complete vertex set supports a stronger *discrete-time* screen only; between-time crossings and true hull/wing intersections remain possible.
- All authored wing mesh admission, permanent bridge/hull geometry, structural root connections, Seaborne hydrodynamics, Submersible pressure hardware, and final cinematic art remain separate approval gates.
- Four wings, five protagonist canon, the First Wake narrative and the Orbiter hold are unchanged. No protected merge or release.

## Next verification

1. Run the Python source-preflight workflow at the exact head and check every test's reported result; do not inherit previous-head green checks.
2. Re-run the corrected wing GLB/manifests through `audit_aureate_wing_clearance.py` with the original source C++ and header; record the exact GLB SHA, complete per-primitive counts, and time-sample clearance minima.
3. In a clean native UE 5.8.4 worktree, build and run both required ship automation tests from PR #660.
4. Produce a true post-strut Seaborne image and a separate swept-volume motion study before claiming clearance or creator visual acceptance.
