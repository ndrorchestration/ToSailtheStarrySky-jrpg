# First Wake — Cinematic Lighting Review v0.1 (2026-11-10)

**Status:** Isolated Unreal lighting implementation candidate. No image, native map, full player run, performance number, or visual/art acceptance is implied by a source-test pass.

**Base:** Draft First Wake cinematic plan PR #790, head a91068891e5792ea584301c2b65975b22e954e94. Own worktree: C:\TSTSS_Lighting_20261110. **This branch is stacked on #790, not a merge of #788 and #789.** New source file names only, no shared map edits. Approved creator canon and ship/character assets remain authoritative; no unapproved models, lunar gates or spell unlocks.

## What this implements

- Eleven separately selectable lighting **looks** spanning harbor day/dusk, engineering, bridge, ascent, aurora, phase drift, storm descent, sea contact, shore aftermath, and an optional night-legibility stress test (not a canon story beat), encoded with directional key, movable SkyLight fill, SkyAtmosphere, ExponentialHeightFog, practical PointLight, and bounded post-process exposure bias.
- UE Editor staging duplicates existing V2 First Wake review map into unique /Game/TSTSS/Review/Lighting/FirstWake_<name>_Lighting_V1 maps; it removes exactly two original noncinematic light placeholders **only in the duplicate**, requests no precomputed lighting, authors dynamic actors and saves native map hashes/receipts. It refuses to overwrite existing destinations or receipts.
- Static source validation, malformed-profile negative tests, nonfinite/overbright/fog bounds, story-order protection, fail-closed source map and dedicated-worktree guard.
- The shot plan is **not** the final canon palette; scene anchors remain temporary BasicShapes blockout. Day/night interpolation, real weather and ocean physics are owned by independent integration lanes and are explicitly **not implemented** by this lookdev generator.

## Safe commands (in this isolated worktree)

Source-only:
    python unreal/Tools/tstss_lighting_review.py --validate
    python -m unittest unreal/Tools/test_tstss_lighting_review.py -v

Native stage requires dedicated worktree, a working UE 5.8.4 Editor Python environment, >6.5 GiB available physical RAM and >14 GiB free C:, no other UE Editor running, source-locked compiled project assets, clean map, and new output names. Example invocation from Unreal Python with imported module:
    import tstss_lighting_review as lighting
    lighting.stage_native("harbor_day")

Load the resulting map in a disposable Editor session. **Do not run** against a production/other artist map. Do not assume successful staging proves the rendered sky, physical sea, dynamic shadows, cloud/volumetric effect, framed scene, or exposure; verify each independently with native D3D captures.

## Expert panel QA lenses (same-assistant, not independent agents)

1. **Cinematic art direction:** Hero face/ship silhouette and motivated key/fill/rim; no crushed blacks or blown brass.
2. **Rendering engineer:** Movable light mobility, SkyAtmosphere binding, Skylight capture, no unbuilt-lighting warnings; UE version compatibility and proper exposure.
3. **Environmental realism:** Day/dusk/storm light, fog depth falloff and sky-water horizon alignment, not generic neon or black-sky.
4. **Gameplay UX/accessibility:** Legible E/J prompts, footpath and gauges at player camera, grayscale and half-size preview.
5. **Narrative/continuity:** Ionia before Lyra; no advanced Five Lights power, false buoyancy evidence, or Starbourne reveal.
6. **Performance:** Measure GPU milliseconds, average/low frame time, shader compilation/memory, Skylight realtime-capture cost and dynamic shadow budgets on Neontic.
7. **Adversarial QA:** Reject same destination, dirty editor, wrong project, missing source/map/classes, invalid values, duplicate names, absent output and receipts.
8. **Production/integration:** Integrate lighting only after #788/#789 conflict reconciliation and against exact-head shot sequence; creator retains art approval.

## Native image acceptance: all remain open until observed

- Capture **locked camera** same scene in day, dusk, low light, storm and bridge/engineering interior; side by side with creator source. At least one actual controlled player view per location.
- Report Unreal build, Git HEAD, map hash, renderer, GPU, image SHA/dimensions, no near-black or clipped region around face/ship, 50% downsample and grayscale cues, stable exposure moving interior/exterior, shadows/contact and atmospheric depth.
- Verify fog/cloud/sky/water response, aurora silhouette, storm flashes, emergency lighting, reflective metals and legible HUD while moving; test low-spec quality settings and no-flicker transitions.
- Confirm actual absence of "Lighting needs to be rebuilt" warnings and black sky; unbuilt-lighting issue is *not* resolved merely because bForceNoPrecomputedLighting was requested.
- Never count sea contact, stable 2.0-second flotation, saved gameplay state or story beat completed from a lighting change.

**Authority:** Notion First Wake Master Acceptance Matrix VS-D04 and VS-D07; docs/REALISTIC_CINEMATIC_VISUAL_QUALITY_GATE_2026-11-03.md RCV-03/05/06/08/09. All visual and release status **HOLD** pending exact-head native captures, review and creator approval.
