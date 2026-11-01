# Ender sculpt/hair study V1 — native Unreal 5.8.4 review evidence

**Date:** 2026-11-01
**Branch:** `review/unreal-ender-fidelity-sculpt-v1-20261101` (review only; stacked on #651)
**Status:** Engine-free source geometry PASS; actual UE5.8.4 StaticMesh import PASS; disposable .umap staging PASS; two D3D11 screenshots PASS integrity/legibility; **visual fidelity and creator approval NOT ESTABLISHED**.

## Why this exists

The canonical cast artwork approved on October 30 is a far more developed cinematic direction than the current procedural Unreal blockouts. This V1 is an incremental, reversible sculpt study, focused **only on Ender**. It does not pretend to be the approved art or a fully realistic character. It preserves original Godot gameplay, the five original candidate GLBs, all existing Unreal assets and the original native five-cast review map.

## What actually changed

- Reshaped Ender's smooth head into a narrowed jaw and more deliberate chin/cheek/forehead profile.
- Separate nose bridge, nose tip and nostril shapes; improved upper/lower lip contours.
- Upper and lower eyelid curves, arched eyebrows and inner ear study details.
- Swapped the plastic-looking solid hair dome for a layered undercap and multiple variable-radius forehead, nape and sideburn strands.
- Added proper goggle rim rings and side straps, plus garment collar/stitch/dart details.
- Preserved the established two-ended staff, centered grip wrap and brass ferrules. Equipment and relative height canon unchanged.
- **Important:** green hair remains a *temporary existing-color placeholder* while conflicting approved individual vs group hair references remain unresolved. This file does **not** resolve the conflict.

## Native/source evidence

| Gate | Result | Basis |
|---|---|---|
| Immutable source pilot GLB | PASS | `FidelityCandidates/EnderV1/Ender_ender_face_hair_v1.glb`; SHA-256 `3fc37924bb457dfe3b62877ca8709efb693a1c1c73251cf6f5dcfbe012babd38` |
| Source polygon/normal audit | PASS | 17,398 triangles, 135 named parts, 32 material sections; strict local face/normal consistency; 4 steep face triangles given localized facet normals |
| Regression tests | PASS | Five engine-free tests (deterministic rebuild, immutable output, tampering rejection, baseline original SHA, detail parts) |
| UE5.8 native import | PASS | `5.8.4-58902052+++UE5+Release-5.8` in disposable Windows `CastAllSandbox`; one saved native StaticMesh, approx 185.8 cm staff-inclusive imported extent |
| Native review map | PASS | `/Game/ArtLookdev/ReviewMaps/TSTSS_EnderFaceHairV1_Review` in disposable project only |
| Native D3D11 render | PASS | `Editor.Python.CastAllSandbox.test_ender_fidelity_v1` automation SUCCESS; two actual 1280×720 PNGs; no raster rotation |
| Independent image QA | PASS | distinct PNG SHA-256, CRC/IDAT/dimensions, nonblank content (~9.38% front, 8.16% 3/4 visible pixel fraction), no visual acceptance claim |
| Canonical character model | **NOT APPROVED** | Procedural static mesh, no rig/animation, no high-fidelity likeness; owner comparison/signoff required |

## Actual native screenshots (unfinished geometry)

- [Native front — V1 study](ReviewCaptures/2026-11-01/EnderFidelityV1/Ender_v1_front.png)
- [Native three-quarter — V1 study](ReviewCaptures/2026-11-01/EnderFidelityV1/Ender_v1_three_quarter.png)

These look deliberately sculpted more than the earlier blockout but remain visibly low-fidelity compared to the creator-approved cinematic artwork. They must not be used as marketing or approved character art.

## Geometry QA design

The unchanged baseline `check_cast_geometry.py` assumes every primitive part is geometrically convex and uses a single part-center heuristic for outward faces. Curved strand and garment tube meshes are naturally nonconvex; it would be inappropriate to weaken the baseline checker. A dedicated `verify_ender_fidelity_v1.py` checks source hash, glTF BIN/accessor ranges, normals, face winding, nonzero face areas, section/material consistency, and named-part boundaries for arbitrary curved pieces. This can reject defects the broad convexity test cannot characterize correctly. The tiny number of locally ambiguous jaw triangles are split to preserve surface-facing normals rather than flipping face winding.

## Reproduce and review

1. `python build_ender_fidelity_v1.py --output <fresh-private-or-throwaway-folder>`; compare output SHA and receipt to this checked-in pilot. It refuses overwrite.
2. `python verify_ender_fidelity_v1.py <fresh-folder>`, then run `python -m unittest -v test_ender_fidelity_v1`. No extra third-party Python dependencies.
3. Import to a **disposable Unreal 5.8.4** project only using `intake_ender_fidelity_v1.py`, verify SHA in native intake receipt.
4. Run `stage_ender_fidelity_v1.py` in NullRHI, and `capture_ender_fidelity_v1.py` using the opt-in Python Automation Test plugin and native D3D11 for front and three-quarter.
5. Use `verify_ender_native_captures.py` (Pillow, GPU-review host only) to check genuine PNG artifacts. Reproduce without overwriting existing receipts/map/PNG outputs.
6. Perform expert art comparison with creator-approved source images; **do not substitute** generic visual-bible metadata or this sculpt for the accepted personal character art.

## Next production steps

Priority is now **actual sculpt/likeness**, not more environment/prototype code: richer age-appropriate face anatomy and eye topology, physically plausible hair cards/curves, cloth topology, natural proportion anatomy and true hand/staff grip. Then Ionia's long curly blonde hair and face, Lyra red hair and face, followed by Reson and Aepex. Introduce skeletal meshes, retargeting and animation only after the silhouette passes creator visual review. Track in [expert issue #649](https://github.com/ndrorchestration/ToSailtheStarrySky-jrpg/issues/649).

The Five Lights, party order, and **Reson > Aepex > Ender > Ionia > Lyra** height ranking remain authoritative. All merges/releases/production-art promotions remain held.

## Cross-platform source-byte reproducibility boundary (verified CI failure)

The first Ubuntu 24.04 hosted run on this PR exposed a genuine cross-host difference: source regeneration produced SHA-256 `b513360ac2ea9f9f15758b2af75e057a46a6a623fbf07d67a8aeb46bf692da40` versus the canonical, Windows-generated pilot SHA-256 `3fc37924bb457dfe3b62877ca8709efb693a1c1c73251cf6f5dcfbe012babd38`. Runtime trigonometric float rounding is a plausible cause, but is **not independently proven** as the exact source of every differing byte.

We therefore do **not** claim cross-platform bit-for-bit regeneration. The checked-in canonical GLB is checked against its receipt and exact SHA, and the generator is tested for same-host determinism and matching source-geometry section counts. Both representations are strictly noncanonical lookdev only. Any later cross-OS asset pipeline should introduce explicit numeric quantization and prove exact reproducibility before assigning a shared cross-platform SHA.
