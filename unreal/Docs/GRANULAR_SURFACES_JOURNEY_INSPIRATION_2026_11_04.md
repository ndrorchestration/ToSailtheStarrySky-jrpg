# TSTSS — Journey-inspired sand and snow art direction for Unreal (2026-11-04)

## November 4 — TWO actual native UE5.8.4 attempts (latest evidence; FAIL-CLOSED)

**Separate original private sandbox projects; no playable/prod content modified.** Source is commit `3c9ad4ede1c88987485a37fd0aae82c6be6b2524` for attempt 02, with an isolated clean review checkout and **11/11 engine-free tests PASS**. All six hosted exact-head GitHub source workflows completed **SUCCESS**. Those tests do not validate a native GPU frame.

| Evidence boundary | Attempt 01 | Attempt 02 |
| --- | --- | --- |
| Private Windows project | `C:\tmp\TSTSS_GranularV2_Native_20261104\GranularV2Sandbox` | `C:\tmp\TSTSS_GranularV2_Native_20261104_02\GranularV2Sandbox` |
| Exact source commit | `758af9b0bad079dd8556d472dd7c8d09928f8621` | `3c9ad4ede1c88987485a37fd0aae82c6be6b2524` |
| UE5.8.4 D3D11 native result | `NATIVE_MATERIAL_BUILD_HOLD`: material graph connection failed before compiler | Internal Python receipt `NATIVE_TWO_SURFACE_MATERIAL_BUILD_PASS`: compiler error arrays reported clean and both material instances plus map were saved |
| Windows Unreal Editor **process** exit | **0**, but source receipt failed | **3221225477 (0xC0000005, access violation)** near/after UE shutdown; **strict G1 overall HOLD**, not success |
| Actual screenshots/performance | **NONE / NOT RUN** | **NONE / NOT RUN** |
| Evidence preservation | Original logs and failure receipts retained | Original native/host receipts, full log and five assets retained |

Attempt 02 **independently enumerated and SHA-256 rehashed** all five physical files in its disposable project:
- `GranularReview.umap` `2bee9a7ec491522527ad240bb5645613c3b4e59f47f80bc24083ee96ac79a8f7`
- `M_SilkenDune.uasset` `a031feccc0b0147c1c1e85632426492667d3e6c530239065a60aa9731f6d5539`
- `MI_SilkenDune.uasset` `8cfe6d2f480036efa17554085fa5c00fbb72e3bc29dc7c0e2c96de6babac206e`
- `M_WindCrustSnow.uasset` `13c9dbcc8cd80ed89c6fd00a4f5a95ad8d1e422fc07747af815961a0edf5c872`
- `MI_WindCrustSnow.uasset` `e5f4e3755d069d13ff1f1f6ed8826b69b10dff9512808c658b42d4230510c70b`

This establishes that the UE Editor Python graph builder advanced from a first-pin error to **writing both native material/material-instance assets and a review map**, with no compiler errors returned by the synchronous `recompile_material` calls. It **does not** prove that those materials display correctly, survive an independent Unreal reopen, render on the GPU, or pass a clean process shutdown. In fact the abnormal exit is a blocker even though `LogExit: Exiting.` appears in the tail of the log. Do **not** infer a known crash cause or retry the occupied attempt paths. The source input hash was checked at startup; the second native host log SHA-256 is `0dfda89a8701269d4bf176cc55008089fe7e8c4425152df85276506991309e8e`.

**Next smallest safe gate:** read-only engine AssetRegistry and material-graph readback from a separate, clean *third* reviewer project or a snapshot of the generated review project; identify the `0xC0000005` shutdown if repeatable, and only then attempt **one** review screenshot with defined light direction, exposure, full provenance and pixel QA. Do not approve source-only manifests, assume this exit is harmless, or merge draft PRs. Production weather, globe material blending, footprints, snowfall wind transport, canonical terrain and Starbourne remain untouched.

---

**CREATOR DIRECTION — ADOPTED:** The experiential sand and snow presentation of *Journey* (thatgamecompany, 2012) is the **primary artistic/technical inspiration** for sand and snow in *To Sail the Starry Sky*. This is an art-direction constraint, not a request to recreate proprietary code, sample assets, copy its world layout, or clone character designs. The TSTSS visual target remains *original premium cinematic science fantasy*: believable planetary curvature, scale, lighting, atmospheric depth, readable contrast, environmental storytelling, and an emotionally resonant world.

**Source authority:** user's direct design decision on November 4, 2026. This page **does not** declare an exact implementation of *Journey*'s technology, approved TSTSS assets, canon geography, implemented footsteps, weather simulation or a tested Unreal renderer.

## Source-backed interpretation — distinguish history from proposals

John Edwards' publicly described GDC 2013 [Sand Rendering in Journey](https://www.gdcvault.com/play/1018864/Sand-Rendering-in) and SIGGRAPH 2012 [Dynamic Sand Simulation and Rendering in Journey](https://advances.realtimerendering.com/s2012/) focus on dune response, footprint/trail physics, and conveying sparkling granular surfaces without brute-force individual grains. Thatgamecompany's [2012 interview](https://www.pushsquare.com/news/2012/02/interview_thatgamecompany_journey) frames the result as "impressionistic realism": interactive, surreal, and emotionally convincing rather than simply physically measured. A secondary independent [technical breakdown](https://www.alanzucconi.com/2019/10/08/journey-sand-shader-1/) discusses ripple normals, tonal contrast, broad ocean-like specular, grazing-angle silhouette and sparse glitter as interpreted rendering ingredients.

**For snow:** use the *observed* in-game mountain ascent—wind-stretched shapes, muted cool gradients, drifting snow and persistent traversal tracks—as the visual reference. **We have NOT verified *Journey*'s proprietary snow shader algorithm** and must not imply that snow uses the same sand equations.

## TSTSS original material target

| Material | Intended emotional quality | Candidate optical and interaction layers | Status |
| --- | --- | --- | --- |
| Silken Dune | Warm, fluid, luminous, welcoming but vast | Large smooth dune geometry; wind-shaped **normal** ripple, high-contrast sun-readable diffuse, original broad grazing specular; rare view/light-gated **filtered microglints**; traversed sand trails, kicked grains and wind haze as *separate future effects* | Source concept and prototype, not native-render accepted |
| Wind-Crust Snow | Quiet, crystalline, ancient, becoming harsh under a blizzard | Powder/packed crust roughness blend; wind-aligned fine normals; restrained bright crystal response, cool diffuse and soft shadow depth; exposed hard edges, accumulating/drifting snow and readable footprints as *separate future effects* | Source concept and prototype, not native-render accepted |

The surface should look different at sunset, high noon, blue hour and in motion while retaining legibility. Sand must feel **silken, not oily/wet plastic**; snow must feel **powdery/crystalline, not polished ice or white paint**. Create original palette variants for TSTSS biomes; do not borrow *Journey*'s signature architecture, characters, game geography, soundtrack, textures or other expressive assets.

## Engineering layering — original UE5.8.4 renderer, not an engine fork

1. **One material family:** two opt-in material instances within `/Game/TSTSS/Review/EvocativeGranular_V2`. Candidate source `unreal/Tools/granular_surface_review_v2.py` outputs new original HLSL for albedo/roughness, analytic tangent normal perturbation, and sun-gated bounded artistically adjusted sheen/glints. This is **source-authored, not Unreal-compiled** until a native receipt exists. Sun direction is a fixed *review parameter* and **must** be connected to the single authoritative world sun before any production use.
2. **Wind and environmental condition owner:** use one authoritative biome/weather controller. Sand maps only to selected arid/coastal exposed ground; snow maps only to snowpack/appropriate frozen terrain. Do **not** infer falling snow from biome temperature or moisture. Wind drives directional ripple, drift material and future Niagara only once across a local tangent frame; cloud/light transitions derive from one game world time source.
3. **Interactions as separate systems:** local trails/footprints/boarding paths and sliding/surfing feedback require a surface deformation or decal/virtual texture system with valid collision, lifetime, LOD and network/save limits. Shader normals alone do **not** change terrain geometry, navigation, footsteps or friction. Start with reversible surface interaction trails in a disposable map—not an automatic world-globe deformation engine.
4. **Scalability and accessibility:** high/medium/low sparkle density and lighting; distance/derivative filtering to avoid temporal crawling or glitter flicker. Reduced-motion mode must reduce moving grains and visual strobing, not suppress essential traversal tracks. Fall back to ordinary readable albedo/roughness on low-end GPUs; single sun/haze/precipitation owner, bounded overdraw and Niagara rates.
5. **World integration:** local curvature, pole and cube-tile transitions use world-space/tangent basis and deterministic per-patch seeds. Validate cross-seam normals, footprints and wind direction before integrating into a planetary globe. The V2 **flat-review UV shader does not solve globe seams**.

## Exact review acceptance — no automatic art promotion

- **G0 / Source:** deterministic `--validate`, original code only, noncanonical review path, no automatic merge, overwrites or gameplay/save/ship edits. Engine-free regression tests recorded.
- **G1 / Native Unreal:** isolated UE5.8.4 Editor run compiles all material HLSL; imported instances read back, native saved review map and source/exact-head receipt. Compile errors or warnings requiring manual intervention fail closed.
- **G2 / Matched light/camera captures:** at least three matched cameras (macro ground, walking-height, wide dune/crest) under fixed noon/golden-hour/blue-hour lights for both snow and sand, baseline/V2 A/B. Record screenshot SHA-256, verified material/mesh, render path, camera and exposure. No resemblance claim from source code alone.
- **G3 / Motion and interactions:** recorded camera pan and wind-lift sample; inspect aliasing, glare, color-band shadows and low/reduced-motion. Later test procedural footprints, trail persistence and gameplay friction separately.
- **G4 / Performance:** target Intel Iris Xe workstation plus representative Windows desktop GPU. Record frame time, compilation stalls, GPU memory and visual fallback. No speculative FPS claims.
- **G5 / Creator acceptance:** side-by-side creator review of *feeling*, visual uniqueness, environment narration and 2.5D legibility. Only the creator approves resulting sand/snow style or canon world locations.

## Existing parallel work to preserve

- Earlier procedural Unreal source [draft #638](https://github.com/ndrorchestration/ToSailtheStarrySky-jrpg/pull/638) includes seven independent sand/snow/wet/weather cards; source tests passed, but **actual native Unreal material compilation and capture are not established**.
- Existing Godot sand/snow optic trials and the more detailed [material promotion ledger](https://github.com/ndrorchestration/ToSailtheStarrySky-jrpg/blob/main/docs/design/PERCEPTUAL_BIOME_MATERIAL_PROMOTION_2026-10-27.md) remain useful references, not the active engine or accepted materials. Preserve explicit one-weather-controller, biome/precipitation separation and low-quality parity.
- **This V2 branch is stacked on draft #638 as a disposable source review**, does not modify the old V1 shader graph, and is not production content. Avoid registering candidate effects as gameplay spells, and do not change First Wake, Ender, the Aureate Wake, game saves, accepted character art, or Starbourne gates.

**Decision status:** Journey-*inspired* visual direction accepted; original V2 shader-source implementation candidate; **native render, geometry interaction, environmental integration and artistic approval remain HOLD**.

## First real UE5.8.4 material build — preserved failed preflight (November 4)

A **private** D3D11 Unreal 5.8.4 full-Editor test ran from the exact source commit `758af9b0bad079dd8556d472dd7c8d09928f8621` in `C:\tmp\TSTSS_GranularV2_Native_20261104\GranularV2Sandbox`, a newly created module-free, explicitly noncanonical review project. Resource preflight: **8.91 GiB free RAM and 29.75 GiB disk**, no competing Editor. The spawned Editor exited 0, but **the native material creation did not succeed**: `MaterialEditingLibrary.connect_material_expressions(color, "", rgb, "Input")` returned false, and the guarded source raised `Could not connect material node: color`. **No native HLSL shader compile, material-save success, map or GPU frame is established.**

The native failure was preserved rather than retried at an occupied destination: `native_granular_v2_receipt.json` and `host_granular_v2_receipt.json` are next to private full-Editor log `granular_v2_native_editor.log` (SHA-256 `b0e6c332c830eb77f33f4ee0165304c710195609f815bbacfc9daf2fe6e9cce4`). No production assets or project maps changed and no Starbourne action occurred. Note that the exit code 0 **does not override the native receipt's explicit HOLD**.

**Bounded source correction:** use an empty `to_input_name` for the ComponentMask's first input. The official UE 5.8 [Connect Material Expressions](https://dev.epicgames.com/documentation/unreal-engine/BlueprintAPI/MaterialEditing/ConnectMaterialExpressions?lang=en-US) API specifically documents that an empty target input selects the first pin. Add an engine-free regression guard. This is a source fix, **not yet new native success** until a *new uniquely named* private sandbox compiles both materials and saves the review map, with independent SHA/readback. Older V1 sources are left intact.
