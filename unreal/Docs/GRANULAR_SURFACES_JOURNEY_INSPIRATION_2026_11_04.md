# TSTSS — Journey-inspired sand and snow art direction for Unreal (2026-11-04)

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
