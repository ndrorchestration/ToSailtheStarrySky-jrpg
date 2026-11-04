# Aureate Wake V4 — coupled geodesic bridge and curved quarters native lookdev
## November 4 — two verified native bridge-camera diagnostics (LATEST)

After the full-scene Automation13, two **additional** registered UE5.8.4 D3D11 `Editor.Python` tests captured new 1280×720 frames from the **same unchanged** noncanonical coupled-habitation Skybourne review map.

| Evidence | Automation14: saved BRIDGE camera position | Automation15: transient camera-only reframe |
| --- | --- | --- |
| Real D3D11 native controller / engine exit | PASS / 0 | PASS / 0 |
| PNG SHA-256 | `55d1ec97e77c563af2f31f8f53c6c1c88fbb6b7747e6aeff71047e138ad52d88` | `64c6a83fe2a8361b0585c2952073c98eb480d1691fbf7d7aba474031d8dff1fb` |
| Near-black pixels | 2.2413% | 0.3994% |
| Nearly white pixels | 0.9466% | 0.7029% |
| Saved review-map SHA preserved | PASS | PASS |
| Visual approval | **HOLD** | **HOLD** |

Automation14 uses the original review map's named `V4_NONCANONICAL_CAMERA_BRIDGE` role. Its native image makes the brass triangular geodesic struts and cyan translucent shell legible, but **a large foreground leaf wing occludes much of the dome**. Automation15 uses the **same camera actor only transiently**, setting the unsaved review eye position to **(610, -20, 295) cm**, target **(185, 0, 130) cm**. This puts the dome closer to center but wings still crowd the left and right edges. **Neither composition is accepted as a cinematic bridge shot.** The filenames retain the inherited `ThreeQuarter_REVIEW.png` suffix; the **native receipt's `camera_label=V4_NONCANONICAL_CAMERA_BRIDGE` and temporary camera metadata are authoritative**.

All 14/15 native and host receipts independently agree on PNG hashes, dimensions, successful named-controller execution, absence of production changes, Starbourne still locked, and source map SHA-256 unchanged at `14e896f532e898836c98d51b3acf33936faf7c43f907b0d0fa20f9cac4ca4362`. The 15 temporary camera was not saved to the map. Both tests created unique temporary skydome review materials in the **disposable sandbox only**; they did not promote materials to production or approve a real sky.

Private original-pixel side-by-side:
`C:\tmp\TSTSS_AureateCinematicV4_Native_20261103\SkybourneV4_BridgeViews_Default_vs_Temporary_PRIVATE_20261104.png`,
SHA-256 `cd69cf53e4c048442313250160f2327318c2ec4accac2f3d2ea29e931bc14b4b`, with adjacent JSON provenance. The source pixels are unchanged except for side-by-side layout/title text.

**Source provenance:** registered local scripts now copied to PR review source with their independent, non-overwriting attempt paths. The images and binary maps remain **private** on the workstation; these outputs were not generated from a clean exact-head GitHub checkout. Local V4 engine-free `unittest` group now **60/60 PASS** including 3 new camera/capture safety tests. Workflow results of this updated GitHub head must be checked separately; source CI cannot confer native visual approval.

**Visual/engineering HOLD:** no crew-scale signoff, glass pressure validation, full wing-root vs dome swept clearance, physics, bridge/quarters docking collar clearance, actual #705 sky physical atmosphere, canonical pose, creator shot approval, production integration or Starbourne player unlock. The next targeted lookdev should test a camera not blocked by the authored fore wing and separately investigate wing root/dome interference; avoid unrestricted camera/pose changes and four-form GPU rollout.

**Evidence date:** November 4, 2026. **Authority:** NONCANONICAL / DISPOSABLE UE5.8.4 SANDBOX / REVIEW-ONLY.
**Parent review:** PR #732. **Important:** Native GLB binaries, .umap, PNG and receipts below were generated on the authorized Windows workstation. The native executions used these source files locally in a dirty review checkout and **are not exact-head clean-tree Unreal verification**; committing their source here enables independent future reproduction without promoting art.

## Reversible geometry delivered
- Deterministic `build_aureate_v4_habitation_lookdev.py` uses the already-reviewed `build_aureate_body_review.py` GLB encoder and true tessellated geodesic dome, plus a new curved lofted quarters body with brass ribs and unsealed blue window insets.
- Two separately importable, 3-material-slot GLBs generated with stable bytes in `C:\tmp\TSTSS_AureateCinematicV4_Native_20261103\CoupledHabitationLookdev_20261104`:
  - `AureateWake_CoupledBridge_Geodesic_REVIEW.glb` SHA-256 `a3a136ced79b61fc5608e37ac0f3e6d275fdb1e4644c3c3dca95d9588fd66506`;
  - `AureateWake_CurvedLivingQuarters_REVIEW.glb` SHA-256 `69ac5e3b4b7899ccc542b391ae39c38d500026b854dd918cf446db1b329797d0`.
- These are **design-study centimeters**, not approved engineering dimensions. Reference central pivot (40,0,72) cm; bridge mesh actor origin (170,0,133) cm; separate living-quarters mesh actor origin (0,0,0) cm. The geodesic bridge sits over a curved section of the quarters. No crew-size/cabin-clearance or pressure seal proof.

## Native asset intake: PASS
One resource-guarded, `-NullRHI` **Unreal 5.8.4** import succeeded in the *existing disposable* `AureateCinematicV4Sandbox` project. Both imported as one UE StaticMesh each, preserving three independent material slots:
- Bridge native bounding-box half-extents about (96.385,57.398,62.945) cm;
- Quarters half-extents about (224.111,61.250,25.102) cm.
Native receipt `coupled_habitation_native_import_20261104.json`; host receipt `coupled_habitation_native_host_20261104.json` reports `NATIVE_HABITATION_IMPORT_PASS` and engine exit 0. Import destination `/Game/TSTSS/Review/ShipArt/CoupledHabitation_20261104`. These `.uasset` review binaries remain local to the sandbox; their existence is not author approval.

## Fresh review map, common-parent pivot: PASS
A *new* map `/Game/TSTSS/Review/Scenes/AureateV4_Skybourne_CoupledHabitation_20261104` was staged and saved without duplicating or modifying original review maps. It has **15 native review actors**, including four correctly rooted imported 280 cm leaf-wing components and four matching camera roles. Two habitation meshes share `V4_NONCANONICAL_COUPLED_HABITATION_PIVOT_REVIEW`.

In native NullRHI, the pivot was yawed **17.5 degrees**, moved both bridge and quarters, held their child-to-child separation constant from **215.84485168750263** to **215.84485168750257** cm, then restored both children to original positions and saved at rest. This does **not** verify continuous swept clearance, rotational limits, bridge cabin pressure/gravity or production ship animation.

Map SHA-256 `14e896f532e898836c98d51b3acf33936faf7c43f907b0d0fa20f9cac4ca4362`. Source receipt `native_coupled_habitation_stage_20261104.json`; host `native_coupled_habitation_stage_host_20261104.json`; native stage engine exit 0.

### Independent saved-map integrity
These five earlier .umap SHA-256s were asserted before/after the native stage and independently rechecked by the capture:
- Skybourne original `16bb93fb9bdd2a4e1559864df908122094fe8a641b4a1481f2935d64ba184c40`
- Seabourne original `b0b0587783197b2eff4a3e820fb49a52ac70edbbc9519a8cdbceee470edc955a`
- Submersible original `815e235aae6abef0e9a816bd8c9d01a13b4441bd81538763d2424e799e925f35`
- Starbourne static-only original `953bb2aaca0db194bdd871229cdb13245c59ceab19cf0f8cbc44a802c01e0e00`
- Skybourne authored-leaf reference `93b0940c75bcd0269d0d20dbf55aaf2bfad3c2f903f82d4daf835797be220e95`

## Real GPU capture: PASS, cinematic acceptance: HOLD
`Editor.Python.AureateCinematicV4Sandbox.test_aureate_v4_habitation_automation13` completed in UE5.8.4 D3D11, engine exit 0 and named-test controller Success. Real **1280×720** PNG SHA-256 **`e6383c588be1d2aecc0c11679e44b1f59844491726216865ab0a8f5695ee7cad`**, 1,109,295 bytes, source map SHA unchanged. Native proof records 15 review actors, both exact imported habitation StaticMeshes, parent attachment, and four authored 280 cm leaf wings. Host start/end free RAM ~7.95/7.93 GiB, well above 6.5 GiB launch requirement. The default screenshot warning means *no approved image ground truth*, not failure of the native capture.
Private PNG: `C:\tmp\TSTSS_AureateCinematicV4_Native_20261103\SkybourneV4HabitationGPU_20261104_Automation13\Skybourne_V4_UE584_D3D11_ThreeQuarter_REVIEW.png`.

A private, source-pixel-preserving, side-by-side review against the prior authored-wing blockout (Automation12) is saved at:
`C:\tmp\TSTSS_AureateCinematicV4_Native_20261103\SkybourneV4_LeafOnly_vs_CoupledHabitation_PRIVATE_20261104.png`, SHA-256 **`c4863a839a6343c235050f2676fee6e7349a1387c8ffa494c4703d9c6bcbf20e`**. The adjacent JSON record rechecks both screenshots and map hashes; original pixel arrays were pasted unchanged. In the new frame, faceted gold dome edges, transparent tinted glazing and continuous ivory cabin curvature are plainly legible; the previous sphere/cuboid placeholders are no longer the habitation silhouette. Near-black pixels were 0.1934% before and 0.1398% after, but these fractions are engineering diagnostics, **not artistic scores**. White clipping increased from 0.0065% to 0.3102%, indicating highlights merit inspection.

## Local source verification and boundaries
- Model build + byte-for-byte regeneration: PASS. Existing GLB generator base source matches the GitHub PR branch exactly.
- **57/57** local `test_aureate_v4_*.py` tests PASS, including **5/5** new deterministic geometry/safety tests; the previous 52 still pass.
- The special-purpose native stage and screenshot scripts contain absolute private Windows sandbox paths, unique output names and pre-existing-receipt refusal. These are **reproduction recipes for the authorized review workstation**, not portable production gameplay tools.
- No production C++ actor was changed, no SaveGame or original four form scene modified, no art approved, no merge, no Starbourne player/story unlock or release. The only Unreal assets saved are **new, noncanonical review GLBs imported into the disposable sandbox, a new review map, and disposable sky-test materials**.
- **#705 D3D12 physically rendered sky remains independent HOLD.** Automation13 reused the bright, camera-centered two-sided nonphysical review skydome from the earlier D3D11 diagnostics; a blue background is not physical atmosphere or lighting approval.

## Next gated iteration
1. Compare the native frame side by side with approved Aureate Wake reference for **credible human-scale glass dome, canopy curve and believable attachment to the forward deck**; do not infer a scale from the image alone.
2. Review bridge/quarters docking collar and shared-pivot axis, room clearance, visible wing-root separation and scale checks, then commission one fresh native capture from an isolated successor review map only.
3. Validate physically coherent sky (#705), glass material/readability, true atmospheric depth, collisions during the full transformation path, pressure envelope and gameplay save/load separately before any production promotion.

**Decision:** Native mesh intake PASS; coupled pivot PASS; single preview D3D11 render PASS; cinematic visual approval, continuous swept physics, habitat pressure ratings, full four-form integration and release all HOLD.
