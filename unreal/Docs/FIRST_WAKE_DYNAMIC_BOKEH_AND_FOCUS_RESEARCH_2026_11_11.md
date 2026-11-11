# First Wake — world-driven bokeh, depth, and cinematic-focus research v0.1

**Status:** DESIGN + DATA PREFLIGHT ONLY; NOT CONNECTED TO RUNTIME; NOT NATIVE-VERIFIED; NOT ART-APPROVED.
**Date:** 2026-11-11.
**Base evidence:** draft PR #813 at `76268b8975ec3ce7b7644b6223c09d4889b658a2`; do not treat this as merged gameplay. This is intentionally an isolated stacked review branch. Do not modify an existing map, save, Story/SeaContact/Flotation state, cinematics owned by other drafts, or Starbourne gates.

**Adjacent authorities:** `docs/REALISTIC_CINEMATIC_VISUAL_QUALITY_GATE_2026-11-03.md` (RCV-03/04/05/06/08), `docs/WORLD_SHIP_VISUAL_DIRECTION.md`, `unreal/Docs/FIRST_WAKE_PLAYABLE_LEVEL_SETUP.md`, and draft PRs #796 (lighting), #798 (atmosphere), #811 (camera rotation fix), #813 (playable convergence), #814 (gated traversal). Existing `docs/VISUAL_BIBLE.md` has historical Godot/pixel presentation constraints and is not authorization to override Unreal 5.8.4 implementation or ship naming.

## Decision

Use **three physically motivated, independently controllable layers**:

1. **Optical focus / bokeh:** filmback, focal length, f-stop, actual camera-to-subject distance; aperture shape defines out-of-focus highlights. Prefer Unreal Cine Camera Actor manual or actor-tracked focus in authored shots. Do not force depth-of-field on the main traversal camera.
2. **Medium / distance:** real depth bands, parallax, terrain occlusion, physically motivated height fog, clouds, scattering, precipitation, spray, and sky illumination. Atmospheric extinction is not optical defocus. Apply this to day/night and biome state.
3. **Luminous signature:** restrained HDR practical/emissive sources, bloom, optional lens flare, aurora/stellar shaders. A source may glow while its geometric point/core remains sharp. Bloom, halation, diffraction and anamorphic streaks are not bokeh; author and cost them separately.

Bokeh is a **narrative punctuation mark, not a substitute for distance geometry**. Keep broad environmental views legible and reserve pronounced bokeh for staged close-ups, discovery and meaningful attention shifts. No ubiquitous fake star orbs; avoid blanket blurring of distant geometry, camera-speed-driven random pumping, overbloom, and UI blur.

### Optical accuracy notes and corrections

- Star distances are effectively infinity, **not automatically sharp when focusing a nearby subject**. Under a real large-aperture long-lens close-up, infinity points can be strongly defocused. A wide deep-focus shot focused near hyperfocal/infinity renders stars nearly pointlike. Decide deliberately, and treat an artificial in-focus sky plate as a stylization if used over a shallow-focus character.
- Small f-stop number means large aperture and **more** possible defocus; f/5.6 or f/8 generally deepens focus relative to f/2.8 for the same framing. Changes in lens/filmback/framing also matter; there is no universal aperture that guarantees near and far sharpness.
- A `1/3 foreground, 2/3 background` DOF rule is not generally reliable. Use focus-plane/CoC or Epic's DOF layers preview in the actual shot instead.
- In air, scattering increases with particles/conditions and path length, so distant lights/horizons lose contrast; **rain does not mechanically increase optical bokeh**. Wet glass, droplets, spray and reflection can alter appearance, but remain separate effects.
- Vacuum has no local aerial perspective, but this slice predominantly uses coastal/cloud environments, not unlocked interstellar travel.

## Dynamic world-driver contract

**World state > camera intent > safety priority > rendering.**

- Inputs already present/available in game or authoring context: named story beat; controllable gameplay/cutscene camera; player/actor/camera positions; visible target transform; camera movement; wind/altitude/time-of-day/cloud cover/weather; light-emitter positions/brightness; waterline and safe traversal geometry; reduced-motion and graphics tier.
- A target must be visible, important, stable for an acquisition interval, and **authorized by the scene** before focus can switch. Never use unrestricted tick-by-tick reticle raycast auto-focus to hunt through props/occluders.
- Maintain a hold of at least 0.5 s on a recently lost target, with approx 40 cm target-distance hysteresis and a smoothed focus ramp. These are initial review tunables, **not measurements**.
- Authored shot: choose subject, then pick focal length and aperture, then focus distance and transition timing. In `DIALOGUE`, focus on speaker eye socket, not pelvis/root; the other speaker and title/HUD overlays remain readable.
- Player navigation, ledges, interacting, camera rotation, combat, emergency splashdown, and accessibility take priority over spectacle. Disable or greatly limit gameplay DOF; no violent focus pumps as hazards approach.
- Weather drives the lighting, scattering and surfaces; not an arbitrary defocus coefficient. Aurora adds luminous veil and atmospheric sky behavior, not faux blurred stars.
- Separate visual-only camera automation from canonical events. A camera cut cannot award a milestone, satisfy physics sea contact, infer flotation, grant a party member, or unlock ship modes. Starbourne remains fail-closed. Only Ender, Ionia and post-splashdown Lyra can be playable during this slice; no default Reson/Aepex loadouts.

### Proposed director states

```
GAMEPLAY_EXPLORATION -> [objective, line of sight, author trigger] -> INSPECT
GAMEPLAY_EXPLORATION -> [safe dialogue transition]             -> DIALOGUE
INSPECT/DIALOGUE     -> [scripted cue and valid subject]       -> REVEAL
REVEAL               -> [player-control restore]              -> GAMEPLAY_EXPLORATION
ANY                  -> [combat, fast traversal, hazard]       -> CLARITY_OVERRIDE
ANY                  -> [reduced motion / DOF disabled]        -> CLARITY_OVERRIDE
CLARITY_OVERRIDE     -> [safe return, stable target]           -> GAMEPLAY_EXPLORATION
```

Priority (high to low): player accessibility / HUD and collision legibility / actual gameplay action / story-authorized camera / scenic bokeh. Hold focus rather than recalculating on every momentary occlusion. Exposure and blur must be stable under temporal anti-aliasing.

**Illustrative runtime policy (not implemented by the review JSON):**

```text
if reduced_motion or accessibility_disable_dof:
    disable_cinematic_dof_and_focus_racks()
elif gameplay_is_active and (moving_fast or in_combat or near_ledge):
    use_deep_focus_or_disable_dof()
elif scripted_camera and authoritative_scene_beat:
    target = resolve_authorized_focus_actor()
    if target_is_visible_and_stable(target):
        blend_focus_manual_or_tracking(target, scene_profile)
else:
    preserve_stable_focus_and_low_blur()
world_weather_and_lighting_systems_render_independently()
```

## First Wake shot treatment (review-only)

The nine profiles in `../DataSource/Cinematics/FirstWakeFocusProfiles.review.json` are **proposed parameters** on a 36x24 mm filmback, **not verified native values**.

| Shot | Story purpose | Bokeh / focus judgment |
|---|---|---|
| FW01 Dock establish | Humans small against the world | 28 mm, f/5.6; parallax + mist; minimal DOF, keep dock edges readable |
| FW02 Ionia dialogue | Establish mutual trust | 50 mm, f/2.8; tracked eyes; warm practical-lantern defocus in rear |
| FW03 Engine inspection | Ender's real skill and curiosity | 65 mm, f/2.8; slow rack from gauge to physical engine component |
| FW04 Engine awakening | Ambiguous response from the ship | 50 mm, f/4; light and mechanism animation motivate focus reveal |
| FW05 First Wake liftoff | Vast scale and vertical motion | 24 mm, f/5.6; stable deep frame, cloud layers, foreground ship |
| FW06 Splashdown | Danger, physical impact | 35 mm, f/8; near-zero defocus, horizon and sea-contact evidence visible |
| FW07 Shore exploration | Re-establish player agency | 28 mm, f/5.6; clear traversal, realistic mist and wet highlights |
| FW08 Lyra introduction | Human stakes after splashdown | 50 mm, f/3.5; faces sharp, nearby lamps soften, no early recruitment |
| FW09 Night-sky wonder | Establish future longing, not Starbourne | 24 mm, f/5.6; focus far/infinity, crisp stars, soft independently controlled bloom |

Filmback, f-stop and focal lengths are **starting looks**. If the render reveals excessive blur/aliasing, revise with screenshot comparisons and frame-time profiling. Scene subject distance is measured in centimeters in UE.

## Artistically distinctive TSTSS looks

**The living engine:** close shot of Ender's hands and worn brass resonance controls. The engine's practical teal/silver lights form modest out-of-focus discs while the point of mechanical contact stays crisp. Only after a *real, authored* physical engine response do light/reflections and the next focal target change. Keep the possible ship awareness ambiguous.

**The human-scale bridge:** Ionia is sharply framed against cool blue dome glass, distant wet harbor lights become gentle ovals; do not claim this is physical anamorphic optics unless the corresponding lens behavior is intentionally simulated.

**The awakening horizon:** as the deck climbs, do not blur cloud sea to imply distance. Show actual layered cloud motion, parallax, terrain silhouettes and volumetric scattering. Reserve a brief cinematic rack to the distant horizon if the player is not steering.

**The storm:** rain on surfaces and a few lens droplets only in *authored* storm shots. Sea-surface impact should remain sharp and physically readable; less bokeh under high hazard. A bright flash with restrained bloom and exposure recovery can supply drama without obscuring cause and effect.

**Quiet celestial awe:** stop gameplay camera movement, keep star texture core nearly point-like in a wide shot, add restrained sky luminescence and cloud separation. A close-up with nearby foreground may artistically show star bokeh if the physical camera focus warrants it. No hidden moon bridge or Starbourne gameplay admission.

## Unreal 5.8.4 implementation handoff

1. **No direct staging in this PR.** It authors JSON and source validation only; source maps, existing `Content/` assets, and shared worktree remain untouched.
2. On an isolated workstation checkout, add an opt-in review camera sequence/Blueprint or Cine Camera Actor in a **new duplicate map under** `/Game/TSTSS/Review/DynamicFocus_V1`. Fail closed if occupied, if the source level is missing, or if unsaved Editor changes exist.
3. Configure a Cine Camera Actor filmback/lens. For per-shot DOF, use **Manual** focus in centimeters or **Tracking** for actor references. Expose focus smoothing/debug plane to review. Do not confuse look-at camera rotation with optical tracking; preserve PR #811 camera-rotation fix.
4. For cinematic vs gameplay: only blend from scripted focus to normal player camera after restoring input, collision and gameplay visibility. Implement focus director in runtime C++/Blueprint **after** agreeing on owner and integration base; never let an editor Python staging utility pose as runtime integration.
5. Reuse draft #798 sky/weather and #796 lighting when integrated, without duplicating their owned Post Process Volumes or changing their source heads. Effects should be scoped to camera/volume and composited predictably; avoid double-authoring exposure/bloom.
6. Validate both native screenshots and gameplay: full resolution, 50% downscale, DOF on/off, clear/mist/rain/storm, daylight/dusk/night, reduced-motion, Ender/Ionia/Lyra introduction timing, fast camera turns, dock edge traversal, interaction HUD, and actual sea contact.
7. Profile **GPU cost** using native `stat gpu`, `profilegpu` or Unreal Insights where available at the exact head, hardware and resolution. Define a frame-time budget only after baseline; if DOF causes unstable frame time or temporal artifacts, degrade to circular blur in scripted sequences or disable DOF in gameplay.

### Evidence and admission

- Preflight: `python unreal/Tools/validate_first_wake_focus_profiles.py --self-test`.
- Required for any playable claim: committed integration implementation + native UE 5.8.4 editor build + actual PIE camera transitions + visual captures + DOF-on/off comparisons + device/config, exact commit and source/scene hashes.
- Required for visual approval: creator side-by-side comparisons of hero shots and **in-play** views; protect RCV-03 lighting, RCV-04 framing, RCV-05 atmosphere, RCV-06 contrast, RCV-08 gameplay/performance.
- Reject false positives: JSON parse or source-only script success != material authored, level built, runtime activated, native test passed, or artistic approval.
- Follow all project gate policy; do not merge or propagate global camera settings from this document.

## Research basis

- Epic UE 5.8 cinematic DOF: https://dev.epicgames.com/documentation/en-us/unreal-engine/cinematic-depth-of-field-in-unreal-engine
- Epic UE 5.8 cinematic camera controls: https://dev.epicgames.com/documentation/en-us/unreal-engine/cinematic-cameras-in-unreal-engine
- Epic UE 5.8 post-processing, including bloom: https://dev.epicgames.com/documentation/en-us/unreal-engine/post-process-effects-in-unreal-engine
- Panavision optical engineering on anamorphic bokeh: https://www.panavision.com/highlights/highlights-detail/the-five-pillars-of-anamorphic-bokeh
- B&H depth-of-field fundamentals: https://www.bhphotovideo.com/explora/photography/tips-and-solutions/depth-field-part-1
- Fujifilm focus pulls and narrative timing: https://www.fujifilm-x.com/en-us/stories/pulling-focus-with-your-x-series-camera/
- Filmmakers Academy storytelling grammar: https://www.filmmakersacademy.com/depth-field-character-story/

These sources support the optical/filmmaking mechanisms. The TSTSS profiles, specific timings and blur limits are **new design hypotheses requiring native review**, not empirically validated presets.
