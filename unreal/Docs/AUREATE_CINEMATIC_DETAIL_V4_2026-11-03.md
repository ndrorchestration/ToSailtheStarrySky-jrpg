# Aureate Wake — Cinematic Detail V4 (review-only, November 3, 2026)
**Four-form native scene assembly follow-up:** Separate full UE5.8.4 Editor NullRHI reviews have now genuinely saved **4/4** noncanonical ship layouts, with Skybourne 18, Seabourne 20, Submersible 15 and developer-only Starbourne 14 actors. [Four-map exact SHA evidence](AUREATE_V4_ALL_FOUR_NATIVE_REVIEW_MAPS_2026_11_03.md). This supersedes earlier statements that only the Skybourne scene was assembled, but **does not lift** the D3D11 GPU capture HOLD, geodesic pivot/quarters engineering, continuous clearance or visual art signoff. The fourth mode is privately developable but not a player unlock.

**Same-day second native update:** A genuine UE5.8.4 full Editor pilot and one-form Skybourne scene staging now **PASS**, after the earlier headless actor-spawn failure. The new review level contains 18 actors with four wing identities and four comparison cameras; its raw proof is [here](AUREATE_V4_NATIVE_SKYBOURNE_SCENE_EVIDENCE_2026_11_03.md). Native GPU capture remains **HOLD** (no PNG); memory observations caused a stricter 6.5 GiB free-RAM GPU gate. This does not approve the hull/bridge proportion or validate any physical transform.


**Review pipeline follow-up (same day):** The new [dependency/acceleration register](AUREATE_V4_DEPENDENCIES_AND_ACCELERATION_2026_11_03.md) links V4 assets to the one-hull/four-wing source plan, independent bridge and foil tracks, UE Python Editor dependencies, native import and the stage hold. [Deterministic scene-plan builder](../Tools/author_aureate_v4_review_scene_plan.py) emits a non-mutating four-form JSON with common vessel identity and camera ROLES, not scene actors or PNGs. [Epic's full Editor Python method](https://dev.epicgames.com/documentation/unreal-engine/scripting-the-unreal-editor-using-python) is the next one-actor test route; a safety preflight refused launch because RAM headroom was below 4.2 GiB. No native full Editor actor pass or cinematic render is claimed.


**Native status supersession — November 3:** Genuine UE 5.8.4 NullRHI import and five StaticMesh/four-material-slot readbacks **PASSED** with exit 0, 0 errors, 0 warnings in the isolated sandbox. The separate four-form native scene staging attempt **FAILED at its first actor spawn**, with zero completed maps and no new render. This supersedes older pre-import descriptions below; see AUREATE_CINEMATIC_V4_NATIVE_IMPORT_EVIDENCE_2026_11_03.md. No production art promotion, game actor integration, or Starbourne story unlock.


**Authority:** Creator-approved original four-form illustration (PNG SHA-256 03e3d500d8998a1377502f5ea28da79cf3eaf3854ece833d7ac25b4e0b268e13) remains the visual source. This procedural V4 pack is **NONCANONICAL review-only**. Actual material fidelity, native UE import, cinematography and creator model signoff remain NOT ESTABLISHED.

## Lineage and authority

- Stacked on the draft four-form naming/UV review #699, exact head 909ac42eb7c8823dcdf58c2d67de79e04c888620. It does not integrate separate bridge pivot #702/#706, hydrofoil route #695/#724 or atmosphere #705.
- Forward-development engine: Unreal Engine 5.8.4, notwithstanding stale historical root text in this draft ancestry. No Godot work is resumed.
- Existing serialized enum identifiers remain Skyborne, Seaborne, Submersible, Orbiter. Player-facing canonical names remain **Skybourne, Seabourne, Submersible, Starbourne**.
- Starbourne/Orbiter remains story-gated and fail-closed. Its static radial-sail motif is not a request to unlock the ship.

## Reusable ship accessories

| Candidate | Review attachment | Artistic purpose | Nonclaim |
| --- | --- | --- | --- |
| SharedExteriorTrim | 1 ship root, all forms | Ivory enamel lines, brass chines, observation ports, aft nacelle collars, deck trim | Not an approved hull or crew-scale model |
| SkybourneWingFiligree | Existing four wing roots, 4 instances | Branching gold veins, cyan traces, pearl tip/root | No fifth wing, aerodynamic model or approved membrane |
| SeabourneHydrofoilDetail | Existing two foils, 2 instances | Gold edges, marine joint ornament and foil accents | No hydrodynamics, load path, wake or buoyancy |
| SubmersibleLightRail | 1 ship root | Blue underwater light guides and stern accents | Not pressure-safe hardware or functional illumination |
| StarbourneSailMotif | 4 identical static developer-only copies | Golden ribbed, cyan luminous sail detail across four cardinal directions | No runtime sail, transition, save or story unlock |

**Technical:** stdlib Python only. All geometry in UE centimetres, +X forward / +Z up, exported as glTF 2.0 meters / Y up. Per-triangle dominant-face UV projection prevents degenerate UV bases on side faces. Four explicit PBR material sections per GLB. Generated binaries and receipt stay out of Git. Manifest pins the original approved art SHA, five asset hashes and locked-form authority.

## Offline source verification

From repository root:

    python -m unittest discover -s unreal/Tests -p test_aureate_cinematic_v4.py -v
    python -m unittest discover -s unreal/Tests -p test_import_aureate_cinematic_v4.py -v
    python unreal/ArtSource/ShipReview/build_aureate_cinematic_v4.py --output-dir <unused-output> --build
    python unreal/ArtSource/ShipReview/build_aureate_cinematic_v4.py --output-dir <same-output> --verify
    python unreal/Tools/import_aureate_cinematic_v4_review.py --source-dir <same-output> --check

Never overwrite a changed output file or import into an occupied Unreal destination. Candidate GLBs generated outside the repository; none promoted to production.

## Native UE 5.8.4 admission sequence (import PASS, staging and rendering HOLD)

1. Create a NEW disposable Unreal project named AureateCinematicV4Sandbox. Its project description must contain AUREATE_CINEMATIC_V4_REVIEW_ONLY and EngineAssociation must be 5.8 or 5.8.4. Enable built-in Python Editor / Interchange; no installs or live game project access.
2. In this isolated project only, run import_aureate_cinematic_v4_review.py with --source-dir and --import-review. Exactly five preflighted StaticMeshes must be imported to /Game/TSTSS/Review/ShipArt/CinematicV4 without replacing prior assets. This stage does NOT save maps, mutate actors or trigger form transitions. If a partial import fails, discard the disposable project; native writes are not transactional.
3. Validate importer logs, asset bounds, axis orientation, pivot transforms, tangent warnings, four material slots each, and source hashes. Do not call source-only tests a native UE build.
4. Create a SECOND isolated visual-comparison map, place the shared details on the one ship, wing lace on the existing four wing components, foil ornaments only on the two marine foils, and light rails on the shared submersible body. Place the four identical Starbourne sail studies in a separate **static private scene only** with zero runtime RequestForm calls.
5. Capture native D3D12 1920x1080 matched-angle three-quarter, top, side and bridge/hinge closeups for Skybourne, Seabourne and Submersible. Clearly label Starbourne as a locked static development study. Require readable gold and cyan details, true glass transparency, no black sky, believable wing-to-hull proportions and water/underwater atmospheres.
6. Audit actual continuous swept clearances across all six directed ordinary transition routes with the reviewed hull/wing/support/foil and coupled bridge+quarters; a sampled 126-pose screen is not continuous collision proof. The separate #706 bridge pivot requires its own exact-head native compile/test.
7. Resolve the independent #705 BLACK-SKY native visual HOLD with actual warmup/screenshot proof before claiming cinematic atmospheric completion. Obtain creator visual and crew-scale acceptance before any production merge or asset promotion.

## Explicit holds

Native import/render, cinematic likeness, physic simulation, underwater pressure seals, waterline contact, Starbourne movement/unlock, production actor attachment, cross-branch integration, merge and release remain unverified or unauthorized. No modification to protected main, original approved art, existing asset folders, or gameplay authority.
