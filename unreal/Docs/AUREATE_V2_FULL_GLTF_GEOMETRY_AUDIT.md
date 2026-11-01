# Aureate Wake V2 — full glTF binary geometry review gate

**Scope:** independent source-only QA for the approved-direction, but **noncanonical and unapproved**, ivory/gold hull and blue-glass bridge candidates in draft PR #679. This gate does **not** edit those GLBs, change actors/levels, install Unreal, or authorize Orbiter.

## Motivation

The existing V2 intake checked source hashes, manifest provenance and accessor min/max values **advertised inside glTF JSON**. A malformed GLB could falsify those claims while containing unbounded, degenerate, badly oriented or nonfinite coordinates. GitHub review must check the **real BIN bytes and all triangles**, not trust only metadata.

New source script: `unreal/ArtSource/ShipReview/audit_aureate_v2_glb_geometry.py`.

Run after generating the unchanged V2 candidates:

```powershell
python unreal/ArtSource/ShipReview/build_aureate_fidelity_v2.py --build --output-dir unreal/Saved/AureateApprovedDirectionV2
python unreal/ArtSource/ShipReview/audit_aureate_v2_glb_geometry.py --folder unreal/Saved/AureateApprovedDirectionV2
python -m unittest discover -s unreal/Tests -p test_aureate_v2_full_binary_geometry.py -v
```

## Acceptance scope

The V2 review importer now requires this independent complete geometry audit as part of `inspect()`; direct calls to `import_in_editor()` revalidate the source bytes and geometry and require the matching completed preflight receipt **before any native Editor asset write**. A forged/stale receipt fails closed. This is a mandatory precondition, not an optional QA command.

The audit checks GLB JSON/BIN chunk sizes, buffer-view/accessor containment and alignment, all POSITION/NORMAL/TEXCOORD_0 samples, actual XYZ minima/maxima against advertised claims, finite coordinates, triangle index ranges, repeated indices, degenerate faces, normalized normals and agreement with winding, and review-scale dimensions in glTF Y-up metres. It forbids unexpected node transformations, changed provenance and unsupported material/primitive configuration. Exact deterministic manifest and SHA proof is required first.

Regression tests inject corruption into actual binary values, accessor metadata, NaN positions/normals/UVs, out-of-range/repeated/flipped indices, reversed normals, added node scale and broken length. **Every triangle and every position buffer is checked**, not a spatial subsample.

## Authority limits

- Passing is a **geometry integrity gate**, not proof of watertight pressure hull, detailed mesh topology, continuous collision/transform clearance, material fidelity or deck walkability.
- Meshes remain a **procedural study**, not the approved 3D ship. Creator-approved image stays `Aureate Wake_ Four Configurations.png`, SHA-256 `03e3d500d8998a1377502f5ea28da79cf3eaf3854ece833d7ac25b4e0b268e13`.
- Native UE5.8 import, asset binding, new screenshots and shader behavior are NOT established while `neontic` remains offline. Do not infer images from passing binary checks.
- Earlier V1 outputs and V2 generator/importer are unchanged. Orbiter and Moon Bridge remain story-locked.
- Keep QA draft-only, with no main merge, gameplay promotion or public release.
