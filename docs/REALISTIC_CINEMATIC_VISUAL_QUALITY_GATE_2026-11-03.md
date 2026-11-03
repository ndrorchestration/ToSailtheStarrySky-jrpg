# P0 — Realistic-Cinematic Visual Quality Gate (Unreal)

**Established creator quality definitions (2026-11-03):** Realism = **believable scale, curvature, and lighting**. Cinematic presentation = **intentional framing, atmospheric depth, and readable visual contrast**. The goal is sustained, stunning, realistic-cinematic rendered visuals in *To Sail the Starry Sky* (TSTSS); beautiful imagery must also work during actual player control.

**Priority:** This is the **first cross-disciplinary development checklist gate**, applying to new characters, ships, interiors, environments, globe/atmosphere, weather, combat/VFX, UI, trailers and cinematics. Quality improvements should proceed in small, reversible Unreal Engine review slices. This document is an acceptance plan, **not proof of implemented quality or new creator art approval**.

**Current engine/authority:** Creator declared Unreal the active development engine on 2026-10-31. Older main-branch Godot 4.7.2 material remains historical evidence and may have separate playable acceptance; it does **not** demonstrate native Unreal visual fidelity. Public-safe checklist only. Do not expose restricted celestial reveals.

## P0 visual gate: always evaluate these separately

- [ ] **RCV-01 SCALE** — A documented, consistent centimeter-based scale sheet covers protagonist stature ordering (Reson > Aepex > Ender > Ionia > Lyra; exact heights pending), door/bunk/staff/console hand reach, four wing roots and ship hull/quarters/bridge. In UE compare a human proxy in the same native camera, log bounding-box dimensions and eliminate conspicuous scale jumps. Working ship or planet dimensions are provisional, not canon.
- [ ] **RCV-02 CURVATURE** — At close range, hull, glass geodesic dome, foils, wing veins, roof and fuselage transitions have continuous, purposeful silhouettes without proxy-cube joins or unnatural faceting. At planetary scale, independently review real horizon occlusion and local curvature across low/high altitudes; never flatten a vast globe into a nearby panorama. Use consistent geometry/LOD normals across transitions.
- [ ] **RCV-03 LIGHTING** — A reproducible UE scene has motivated key/fill/rim or sky/environment illumination; consistent shadow contact, physically coherent emissives/reflections, legible glass, and stable exposure moving indoors/outdoors. Capture at least one day/dusk and one low-light test. Reject clipped highlights, crush-black characters, glowing materials with no bounce and all-neon wash.
- [ ] **RCV-04 FRAMING** — Each benchmark uses locked camera transform, FOV, subject placement and safe framing. Provide a hero/wide view plus gameplay-eye view; intentional focal hierarchy from main subject to setting; no framing that hides wing roots, foils, bridge/quarters rotation or story-critical action.
- [ ] **RCV-05 ATMOSPHERE** — Foreground, play plane, midground and far field separate visually through haze/aerial perspective, weather/cloud density, depth and scale-appropriate falloff. Review ocean-waterline and distance cues, terrain horizon, fog clipping, sky blackouts; VFX must not conceal traversal.
- [ ] **RCV-06 CONTRAST** — At native game presentation size and a 50% reduction, the character/ship silhouette, interactive prompts, combat targets and narrative focal object remain distinguishable from their backgrounds. Validate grayscale/color-vision-safe contrast and avoid overbloom, white-on-white, underwater murk or excessively thin UI/wing details.
- [ ] **RCV-07 MATERIALS AND MOTION** — Authored PBR material response for wood/brass/glass, cloth/skin/hair, wing iridescence, water/ice and ship metamaterials; test roughness/metallic/normal consistency, temporal ghosting, movement/readability and distinct silhouettes through transformations. Review test material is not production art.
- [ ] **RCV-08 PLAYABLE AND PERFORMANCE** — Compare the hero render with a captured in-play view on an explicitly named Windows GPU/render path, engine version, resolution, quality settings and representative camera motion. Record frame pacing, memory headroom, shader artifacts, LOD/pop-in and level transitions. Target thresholds are to be established from baseline measurements, not asserted here.
- [ ] **RCV-09 HUMAN ART REVIEW** — Side-by-side matched-camera comparison against creator-approved source references, with dated written reviewer observations. Only the creator may accept canonical likeness, signature Aureate design, character faces/hair, palette or new lore-specific visual identity. Separate creative approval from technical pass.

## Evidence and admission rules

For **each** reviewed scene or asset: record repository, branch/commit SHA; Unreal build; renderer (e.g. D3D11/D3D12 and feature configuration); native level/map and source asset SHA; camera pose/FOV, exposure and light rig; capture dimensions and image SHA-256; pixel/content sanity check; a marked-up or written comparison to approved references; visual/accessibility/performance reviewer disposition; and unresolved issues.

**Admission stages:** DRAFT/PROPOSAL -> SOURCE-CHECKED -> NATIVE-ASSET-LOADED -> NATIVE-IMAGE-CAPTURED -> VISUALLY-REVIEWED -> CREATOR-ACCEPTED -> GAMEPLAY/QUALITY-ACCEPTED -> MERGE/RELEASE-AUTHORIZED. One stage never implies the next. Screenshot queued, process exit 0, NullRHI/map audit, CI source success or a previously captured version **do not** substitute for current-head native GPU image proof. Evidence must be from the same asset and commit lineage being assessed.

### Initial fixed camera review matrix (proposed)

| Scene | Shots | Critical read |
| --- | --- | --- |
| Aureate Wake shared hull | Side and three-quarter wide; human-scale deck/dome close-up | Coherent vessel dimensions, four wings, actual dome and recognizable silhouette; surface/contact light |
| Skybourne | Wide silhouette + wing-root macro + playable flight POV | Four dragonfly wings, iridescence in motion, atmospheric flight and horizon |
| Seabourne | Side/low waterline + foil/strut close-up | Hydrofoil attachment, water contact, reflected daylight, readable wakes/spray |
| Submersible | Three-quarter wide + folded-wing/pressure seam close-up | Slightly visible tucked wings, dark-water contrast, practical lighting and depth |
| Starbourne | Private developer-only static cardinal sail views | Four equal radial light/solar sails, shared vessel lineage, restrained gleam; no player unlock, reveals, gate changes |
| Bridge + living quarters | Human-scale interior, forward dome, pivot before/after | Coherent coupled movement and livability; clearance/physics separately proven |
| Ender / five protagonists | Front/profile/rear/three-quarter + face/hand close-up | Reference likeness, proper scale, believable fabrics/hair, human expression and staff grip |
| First Wake dock, launch, splashdown, berth and repair | Wide establishing + in-control gameplay + dialogue close | Art/story continuity, atmosphere, ocean scale, readable cues and camera continuity |
| Globe, weather and biome pilot | Low/high-altitude paired horizons + weather extremes | Correct horizon-limited visibility, curved world, depth layers and no clipping |
| Combat + magic | Playable battle wide + effect peak + reaction shot | Silhouette/target readability while preserving physical lighting and tone |

## Existing evidence as of 2026-11-03 (not new verification)

- [Aureate V4 PR #732](https://github.com/ndrorchestration/ToSailtheStarrySky-jrpg/pull/732): draft/unmerged, four-map native read-only integrity and temporary bridge/quarters coupled pivot reported at head `c182cea3def0440999fe5e271efa2ebbb8461c59`. V4 D3D11 screenshot attempt ended **REQUESTED_NOT_YET_DONE** without PNG; current-head cinematic render, realistic hull/dome, continuous clearance, materials and creator approval **HOLD**. Later PR changes require new exact-head verification.
- [Aureate ordinary modes PR #656](https://github.com/ndrorchestration/ToSailtheStarrySky-jrpg/pull/656): native D3D12 Seaborne/Submersible previews are **pre-strut**; post-strut foil placement **UNVERIFIED**; placeholder hull/dome/sky; Starbourne gate remains closed.
- [Ender cast lookdev PR #643](https://github.com/ndrorchestration/ToSailtheStarrySky-jrpg/pull/643): four-angle calibrated native D3D11 captures reported for earlier review07 source; current-head native rerender and reference-accurate sculpt/rig/face/hair, grip, materials, gameplay integration and creator acceptance remain **OPEN**. Character hair reference conflict requires creator resolution.
- [Atmospheric-sky draft #705](https://github.com/ndrorchestration/ToSailtheStarrySky-jrpg/pull/705) has a reported black-sky visual hold, not a validated atmospheric solution; independently validate exact-head state.
- Previous [visual benchmark scene](../../docs/VISUAL_BENCHMARK_SCENE.md) and [world/ship visual direction](../../docs/WORLD_SHIP_VISUAL_DIRECTION.md) define earlier art ambitions, not current Unreal acceptance or approved final proportions.

## Fastest safe milestone / recurring loop

1. **First:** on #732's isolated Windows UE 5.8.4 review sandbox, capture **one** actual Skybourne V4 D3D11/D3D12 native GPU PNG after memory/resource preflight, using a named Editor automation controller that waits for capture completion and checks dimensions/pixels/hash. No screenshot = HOLD.
2. Compare that exact asset/image with creator-approved vessel reference: scale proxy, four-wing silhouette, geodesic dome/quarters relation, curvature, lighting, atmospheric separation and 50% thumbnail. Write a punch-list with screenshot annotations; keep V4 lookdev unapproved until human review.
3. Reuse identical camera/light rig to capture Seabourne/Submersible and developer-only Starbourne; review specific mechanical silhouettes without opening Starbourne access.
4. Apply same criteria to Ender close-up (face/hair/fabric/staff grip) and a playable First Wake environment shot. Select one small improvement per scene, rerender, compare, test, record.
5. Every subsequent visual-bearing PR must state which RCV IDs are impacted, include `before/after` capture evidence or an explicit **NOT CAPTURED / REVIEW PENDING** waiver, and preserve story, combat, physics, saves and release gates.

**Review cadence:** Each affected PR before human visual acceptance; consolidate unresolved RCV issues at each weekly development audit. This quality gate remains P0 throughout production, but does not supersede safety-critical physics, story-gate or build-security holds. Record exact technical evidence; never infer visual quality from code tests.

**Ownership:** Creators accept character, ship and world art; rendering/lighting reviewers assess native technical picture; UX/accessibility testers inspect real gameplay readability; QA/producers enforce evidence and regression gates. No automatic approvals.