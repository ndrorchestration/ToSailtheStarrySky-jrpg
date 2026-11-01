# Aureate Wake GLB clearance — complete vertex coverage requirement

**2026-11-01 · Unreal 5.8.4 workstream · REVIEW ONLY · ENGINE-FREE QA**

## Defect corrected

The existing `audit_aureate_wing_clearance.py` treated a requested per-primitive vertex budget as a *subsampling* limit. When primitive vertex counts exceeded that budget, the auditor omitted interior indices while still using sampled minima/maxima as a purported conservative wing bounding box. Such an AABB can be **too small** when an omitted vertex is extremal, so clearance results could wrongly pass.

This review branch makes the input policy **all positions or hold**. Each GLB primitive must have at least one position, and a position count at or below the declared maximum; every position is read. Counts exceeding the upper bound reject before calculating clearance. Accessor stride, declared view length, finite values and binary bounds are also checked. This change makes spatial coverage of the *given mesh* complete, but does not grant continuous motion clearance.

## Source implementation

- `unreal/Tools/audit_aureate_wing_clearance.py`: removes strided/partial position sampling; accepts legacy `--samples-per-primitive` for compatibility and introduces the accurate alias `--max-vertices-per-primitive` (default 3,000, allowed 100–50,000). Each budget is a **hard upper limit**, not authorization to estimate bounds from a subset. The JSON receipt adds `vertex_coverage: COMPLETE_POSITION_ACCESSORS_WITHIN_BUDGET`.
- `unreal/Tools/test_aureate_full_vertex_coverage.py`: seven engine-free synthetic GLB cases for complete enumeration including an extremal vertex; partial-over-budget refusal; empty accessor refusal; truncated declared position-view refusal; short stride refusal; nonfinite coordinates; unreasonable requested budget.
- `.github/workflows/unreal-source-preflight.yml`: executes these cases without Unreal, in addition to source registration and ship review-state checks.

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
