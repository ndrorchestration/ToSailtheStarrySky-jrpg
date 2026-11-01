# Aureate Wake V2 body × authored-wing cross-lane gate

**Review only · 2026-11-01 · source-controlled, fail-closed conservative AABB**

## Why this exists

The original 126-pose, all-15,140-vertex wing audit in [draft #687](https://github.com/ndrorchestration/ToSailtheStarrySky-jrpg/pull/687) establishes **19.94 cm** minimum separation against the *old simple hull/bridge boxes*. That clearance cannot be inherited by the distinct V2 white/gold hull and blue-geodesic bridge in [draft #679](https://github.com/ndrorchestration/ToSailtheStarrySky-jrpg/pull/679).

Pinned source inputs:
- Wing actor and audit **parent head**: `b43303e0afe2150d5a1956023194d9ee5abb4b2e`
- Wing GLB SHA-256: `04d7f9461b4cb4475ea98d5e3f7699b68f272f5646362ad7aef0d222ad92ec73`
- V2 generator **head**: `cc58d518ca397158df27be366e4dc506a84497c9`
- V2 white/gold hull GLB: `efed53b0b1847646d675bb2efe30dbb9af1aaeafb3cbf2e2ef314bb697cb2388`
- V2 blue-glass bridge GLB: `b9a5e43ad6759f4f06e1d3634c80c74616307d267de5f3330b04382cf9e822d1`

## Implementation

`unreal/Tools/audit_aureate_v2_crosslane_envelope.py` verifies the V2 manifest's noncanonical authority, approved-image provenance, checksum entries and exact **independently pinned** SHA-256 values, validates the actual GLB bytes, checks actor C++ pose contract and bridge placement, loads **all positions** and screens the four wing meshes against each V2 object's full geometry-derived AABB at twenty time intervals per directed ordinary-form transition. Orbiter stays hard held.

The whole-object AABB is a deliberately conservative broad phase. It can flag harmless empty regions, mounting contacts, or false intersections. **HOLD means the accurate, per-triangle narrow-phase + authored-support review must happen; it does not establish a physical intersection.**

Return semantics: exit **0** means *only a conservative AABB screen completed without triggering its 10 cm threshold*; exit **2** means review HOLD requiring more precise work; exit **3** means invalid source or provenance (fail-closed). Every receipt lists pinned source heads, asset digests, vertex counts, V2 world bounds, review status and limitations.

## Actual Windows cross-lane receipt

On authorized `neontic`, the two V2 GLBs were regenerated and verified byte-identical at the PR #679 head. Native Unreal 5.8.4 earlier imported and rendered these two assets in **four 1920×1080 D3D11 asset-only screenshots**, whose receipt is at `C:\TSTSS_Unreal_V2NativeQA_20261101\NativeArtReviewSandbox\Saved\ReviewReceipts\native_images_qa_receipt.json`. These are *not* the complete four-wing ship, D3D12 post-strut captures, or final model approval.

The actual cross-lane broad phase returned **exit 2 / HOLD**:
- Skyborne → Seaborne **t = 0.000**, wing/full-V2-hull AABB separation **approximately 0.104 cm**, below the **10 cm** review threshold.
- Wing/V2-bridge world AABB gap at that sampled configuration **approximately 37.57 cm**.
- V2 hull local bounds (cm) about X ±399, Y ±107.71, Z −41..37.08; the dome in the actor is translated by (240, 0, 95) cm.
- Wing primitive positions: 292 + 14,770 + 78; hull: 720 + 4,704 + 426; bridge: 504 + 14,976 + 36.
- Local receipt: `C:\TSTSS_Review\PR679_exacthead_cross_geometry_20261101\pr689_pinned_sha_crosshead_receipt.json`; worktree stays clean.

`unreal/Tools/test_aureate_v2_crosslane_envelope.py` covers required provenance, immutable source hashes (including a fully rewritten asset + manifest), bounds/translation, simulated clear and HOLD, and minimum sampling. GitHub engine-free preflight runs these tests. No native C++ source/gameplay or approved art is changed by this PR.

## Triangle-level narrow phase at Skyborne t0 — later verification

**Additional review code:** `unreal/Tools/aureate_indexed_triangles.py` reads and validates complete indexed triangle faces from the three pinned GLBs; `unreal/Tools/aureate_triangle_narrowphase.py` computes exact finite segment-to-segment, point-to-triangle and segment-through-triangle distances, after a conservative per-triangle AABB candidate filter. It uses standard-library Python only; it does not modify meshes, downsample vertices or grant physics authority. `--narrow-phase-skyborne` on the cross-lane CLI adds a narrow-phase report **only at Skyborne → Seaborne t=0**. The earlier broad-phase HOLD and exit 2 stay in force.

**Real mesh endpoint surface minima (cm):**

| Wing root (index) | All hull triangle pairs | Excluding ONLY hypothesized wing-hinge to brass support-tube pairs | Interpretation |
| --- | ---: | ---: | --- |
| Forward negative-Y (0) | 3.8029 | 10.0025 | Other pairs just beyond 10 cm |
| Forward positive-Y (1) | 3.8029 | 10.0515 | Other pairs beyond 10 cm |
| Aft negative-Y (2) | 3.5752 | **9.9646** | Other pair STILL within 10 cm |
| Aft positive-Y (3) | 3.5752 | **9.9745** | Other pair STILL within 10 cm |

The most proximal triangle pairs are the **wing hinge section** (wing triangle indices 29,280–29,423) and one of the **first four hull brass root-support tubes** (hull triangle indices 240–367; 32 per tube). These ranges are derived from the frozen deterministic source topology and are **hypothesized intended joint contacts**, not an authorized contact exemption. The second column omits only pairs where *both* triangle membership conditions match. The original, unfiltered all-triangle test remains authoritative. In the second pass the aft wing's other venation triangles (for example wing triangle 14,933) are still within 10 cm of a brass support detail (hull triangle 324 or 356), so an exemption for hinge/support tube pairs would **not** fully clear the ship.

The bridge generated GLB's full triangle AABBs are more than 10 cm away at this one endpoint; there were no candidate bridge pairs within threshold in that pass. This does **not** establish clearance along other ordinary-form poses or during movement.

The source fixture suite covers explicit triangle piercing, coplanar overlap, separated triangles, degeneracy, segment closest points, intended-pair diagnostic exclusion, and seeded brute-force cross-checks of AABB pruning. The Windows checkout passed **14/14 triangle tests and 9/9 cross-lane admission tests** at source head `d4b50716bddadf8a8e626b81e07375601dac5438`. The earlier actual full-input endpoint receipt was captured at source head `e5ef577df804fe2fc4ca5c503b2eaf70f0f4be9c`; the later edits are naming, limits wording, regression hardening and documentation, not geometry changes. Re-run exact final head to bind a fresh receipt.

**Important limits:** The exact triangle proximity test identifies geometric surface separation at one time sample only. It is not continuous swept collision, no native engine collision query or optical model approval, and the four brass support tubes have not been formally accepted as safe or pressure-bearing attachments. Do not mark the V2 assembly PASS or reduce the review threshold.

## Unresolved approval gates

1. Implement or independently run **triangle-level or appropriate convex narrow-phase clearance**, treating the intended wing joint/attachment separately from accidental body penetration; preserve 20+ temporal intervals and separately investigate *continuous* swept collision.
2. Render **fully assembled four-wing Skyborne, Seaborne (hydrofoils), Submersible (partially folded wings)** with matching cameras, correct V2 imported hull/bridge, proper struts and materials. Record exact Unreal branch/asset IDs, capture hashes and D3D12 proof.
3. Resolve visual silhouette: actual asset-only contact sheet presently reads as a low, long platform with an aft-positioned geodesic dome; compare against the approved original four-form illustration rather than assuming lookdev equals finished art.
4. Obtain creator review before any 3D asset promotion. Orbiter direct interpolation remains rejected. No merge/release/public deployment.

**The required next result is a narrower review of apparent hull/wing proximity—not loosening the threshold, silently shifting the wing pivots, or claiming the new hull is safe.**
