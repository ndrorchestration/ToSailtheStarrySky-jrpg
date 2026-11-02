# Aureate Wake V2 — isolated brass support tube variant (NOT approved art)

**2026-11-01 · Unreal 5.8.4 cross-lane geometry hypothesis · review-only · Orbiter HOLD**

## Purpose

The [126-pose, full-geometry brass-support gate in draft #696](https://github.com/ndrorchestration/ToSailtheStarrySky-jrpg/pull/696) identified frequent proximity of four authored wing hinges and venation ribs to the V2 white-gold hull's root-support tubes. That test is source-only, static per-time-sample and limited to the four brass support tubes. There is no creator-approved, mechanically validated root connection yet; the fact that supports and wing hinges appear near each other does **not** establish that they are attached, load-bearing or safe.

This draft explores the **smallest isolated trim geometry hypothesis**, never changing original V2 source, wing pivots, approved visual reference, Unreal Editor assets or Orbiter gate. A candidate with more geometric space may look unsupported or sever a mechanical connection; approval is **NOT** implied.

## Controlled generation and immutable inputs

- V2 original source: [draft #679](https://github.com/ndrorchestration/ToSailtheStarrySky-jrpg/pull/679) at `cc58d518ca397158df27be366e4dc506a84497c9`. The generator's two Python source files are independently SHA-pinned in `prepare_aureate_v2_support_variant.py`.
- Original hull GLB SHA-256: `efed53b0b1847646d675bb2efe30dbb9af1aaeafb3cbf2e2ef314bb697cb2388`.
- Experimental hull GLB SHA-256: `3e57722d962ecc834c292748673c37c6d372a6fbf2f3fe50d18b0b80180c23dd`.
- Glass bridge GLB SHA-256: `b9a5e43ad6759f4f06e1d3634c80c74616307d267de5f3330b04382cf9e822d1`, **identical** before/after.
- Wing actor and deterministic authored GLB remain pinned to draft #687 source head `b43303e0afe2150d5a1956023194d9ee5abb4b2e` and wing asset SHA-256 `04d7f9461b4cb4475ea98d5e3f7699b68f272f5646362ad7aef0d222ad92ec73`.
- Only the **single** original generator source line
  `trim.tube((x,side*72,23),(x,side*107,35),2.2)`
  becomes, **in a separate copied source tree**, 
  `trim.tube((x,side*72,21),(x,side*101,31),1.6)`.
  The support tube becomes shorter, lower and slimmer. No source/GLB is overwritten; candidate source is generated in a *fresh* output folder with an independent recipe receipt.
- This file is a **noncanonical lookdev test**. A proposed root attachment design still requires authored bracket/hinge geometry and artist/structural review.

## Verified Skyborne endpoint surface screen

All four wing meshes were inspected with the existing exact triangle-surface algorithm against the four tubes in the baseline and trial hull GLBs at Skyborne t0.

| Root | Baseline hinge-to-support | Candidate hinge-to-support | Baseline venation within 10 cm | Trial venation within 10 cm |
|---|---:|---:|---|---|
| Forward negative-Y | 3.8029 cm | 8.4673 cm | No | No |
| Forward positive-Y | 3.8029 cm | 8.4673 cm | No | No |
| Aft negative-Y | 3.5752 cm | 8.2164 cm | Yes | No |
| Aft positive-Y | 3.5752 cm | 8.2164 cm | Yes | No |

**Critical interpretation:** larger hinge-to-tube distance is **not automatically desirable**: if no socket/strut bridges the new gap, the wing could look detached or be physically unsupported. Candidate venation had **no triangle pairs inside the 10-cm query window** at t0; that is not a global surface-distance measurement.

## Verified full-route targeted support screen

From the exact Windows source checkout `ed3ae7619435bd544eb51891ac4200708222e6d1`, with Python 3.14 and NumPy, the trial was screened against all four brass support tubes: **six directed ordinary routes × 21 discrete time samples × four wings = 504 wing–time observations**, separated into hinge and venation. The baseline comparison is the independently vetted previous #696 receipt with fixed source/GLB checksums and original 164 venation / 256 hinge under-threshold observations.

| Directed route | Original venation | Trial venation | Original hinge | Trial hinge |
|---|---:|---:|---:|---:|
| Skyborne → Seaborne | 2 | 0 | 24 | 14 |
| Skyborne → Submersible | 58 | 18 | 68 | **72** |
| Seaborne → Skyborne | 2 | 0 | 24 | 14 |
| Seaborne → Submersible | 22 | 14 | 36 | 32 |
| Submersible → Skyborne | 58 | 18 | 68 | **72** |
| Submersible → Seaborne | 22 | 14 | 36 | 32 |
| **Total** | **164/504** | **64/504** | **256/504** | **236/504** |

**Observed outcome:** 100 fewer venation under-threshold wing–time observations (approximately 61% reduction), but only 20 fewer hinge observations (approximately 8% reduction). Trial hinge proximity **increases** on the Skyborne↔Submersible routes. This is useful for deciding where to shape the support, but does not justify adopting this specific trial mesh.

**The trial remains HOLD**: `HOLD_EXPERIMENT_NOT_STRUCTURALLY_OR_ARTISTICALLY_ACCEPTED`. Each count is the number of wing–time categories with at least one actual sub-10cm triangle-pair witness, not unique defects, collision penetrations or a continuous-time safety verdict. First-witness distances are not global minima.

## Evidence and next engineering step

- Source helper: `unreal/Tools/prepare_aureate_v2_support_variant.py`; source-bound comparison `unreal/Tools/compare_aureate_v2_support_variant.py`; mutation/authority tests `unreal/Tools/test_aureate_support_variant_guard.py`.
- Windows isolated review checkout: `C:\TSTSS_Unreal_Ship697_SupportVariant_20261101`. Original + experimental GLBs and source receipts: `C:\TSTSS_Review\PR697_SupportVariant_20261101`. Original generator and asset repositories are unchanged.
- The receipt `trial_full_126pose_vs_original.json` was written by PowerShell (which may use BOM-marked UTF-16), and its reader now supports only explicitly identifiable UTF-8/UTF-16 BOM cases *while still requiring all original SHAs/source heads and baseline observation totals*.
- Source tests are hosted in GitHub preflight; the numerical full-route test requires NumPy and ran on Windows. A successful source CI result never substitutes for native Unreal Editor import/physics.
- **Recommended next reversible slice:** design an actual dedicated hinge socket/bracket first, with explicit allowed contact interfaces, then adjust only nearby venation clearance *without shortening or destabilizing the support's load path*. Compare at all six trajectories and continuous swept motion, import into a separate Unreal preview, capture Skyborne/Seaborne/Submersible with hydrofoils/struts and request creator approval before any production promotion.

Do not merge review PRs, move wing pivots, unlock Orbiter, change canon or claim this trial is now the canonical Aureate Wake hull.
