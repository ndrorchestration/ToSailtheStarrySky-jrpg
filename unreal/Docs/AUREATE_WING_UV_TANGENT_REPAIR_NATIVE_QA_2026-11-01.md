# Aureate Wake — Wing tangent-space UV repair, 2026-11-01

**UE 5.8.4 source review only until native import verified.** This draft stack begins at [PR #692](https://github.com/ndrorchestration/ToSailtheStarrySky-jrpg/pull/692) head `75da1c9da22f3081977237c5ea54cbe26bb53a6a`, retaining the native 13/13 ship test and three D3D12 screenshot receipts **only for the earlier tested asset version**. No merge, story, physics, approved art, or Orbiter gate change is authorized here.

## Reproduced geometry defect

The first native import of the noncanonical wing `AureateWake_Wing_Lookdev.glb` emitted **"some nearly zero bi-normals"** in Unreal's Interchange/StaticMesh log. The source contains 29,424 triangles across three materials. A complete Python per-face audit of the original version measured:

| Surface | Faces | Degenerate UV-area faces | Zero geometric area |
| --- | ---: | ---: | ---: |
| veined membrane | 580 | 292 | 0 |
| golden ribs | 28,700 | 1,470 | 0 |
| brass root hinge | 144 | 36 | 0 |
| **Total** | **29,424** | **1,798** | **0** |

The membrane's closed front/back shell used identical UVs for both layers, collapsing every edge-wall/cap UV Jacobian. Tube and hinge cap centers also lay on the same UV line as the rim vertices. Valid manifold geometry was *not* enough to establish usable tangent-space coordinates.

## Narrow source repair

In `unreal/Tools/author_aureate_wing_glb.py`:
- Back layer UVs now shift +0.015 in U and +1 in V, separating front/back edge-wall and end-cap parameterization while preserving unchanged physical vertex positions, triangles, root orientation, authored 280cm scale, three materials and transparency rules.
- Tube cap UV centers now use distinct U values outside rim U=0/1; hinge cap centers use V outside their V=0/1 rim lines.
- The deterministic GLB bytes and SHA-256 necessarily change. **Never overwrite the earlier asset or pretend previous imported image approval applies.** A fresh review import path is required.
- `unreal/Tests/test_aureate_wing_uv_tangents.py` exhaustively checks **all 29,424 triangles** for nonzero UV and geometric areas, plus fixed shell UV offset. Added to hosted Unreal source preflight CI.

## First local source verification

Isolated checkout `C:\Users\Admin\work\TSTSS-UE58-WingUVNative-20261101` at `645ea53f7d09e18b246e2b360add8d8a92958010`:
- New UV/geometry audit: 4/4 PASS.
- Existing wing source geometry suite: 9/9 PASS.
- Existing wing guarded importer suite: 7/7 PASS.
- Deterministic revised wing GLB, PNG and manifest generated successfully in a new folder `C:\Users\Admin\work\TSTSS-UE58-WingUVGenerated-20261101`, without overwriting the prior wing.
- Native UE Editor/UHT build, Interchange reimport, log-warning comparison and captured rendering must have independent exact-head evidence before this source review can be considered a native fix.

## Native acceptance procedure

1. Compile the exact current review head in an isolated UE 5.8.4 Editor worktree, with one compile worker; record UHT and compiler receipt.
2. Verify source hash from the newly generated manifest, preflight against existing `import_aureate_wing_review.py`, and import to a **new** `/Game/TSTSS/Review/ShipArt/WingUVRepairCandidateV3` folder with overwrite disabled. Compare native StaticMesh dimensions, material slots, normal/tangent warning logs against the old import.
3. If all warnings disappear, keep the revised StaticMesh strictly noncanonical. Test all four wings with the approved-reference hull in a **new** private three-form scene before creator review.
4. No approval of hydrofoil clearance, physical join strength, water simulation, full wing cinematic size, continuous swept collision or lunar Orbiter is inferred.

**Separate parallel visual pipeline:** [PR #693](https://github.com/ndrorchestration/ToSailtheStarrySky-jrpg/pull/693) proposes distinct V3 fairings/bridge interior; do not blindly combine its separate V2 asset actor with this native four-mount ship review.
