# First Wake — Unified Cinematic Experience Coordination (review design v0.1)

**Status:** DESIGN / CROSS-PR SOURCE CONTRACT ONLY — NOT RUNTIME-WIRED, NOT NATIVE-RENDERED, NOT ART-APPROVED.  
**Date:** 2026-11-11. **Engine target:** Unreal Engine 5.8.4.  
**Location:** stacked draft PR #815 on unmerged First Wake P0 convergence PR #813; no production merge or scene promotion.

## Decision: a thin coordinator, not one giant replacement director

The first step toward cohesion is a *single declarative scene-intent layer* sitting **above** existing gameplay state and **below** the engine-specific presentation owners. Its role is to determine *when and why* a treatment should appear. It **must not own** story progression, physics, atmospheric simulation, lighting actor spawning, audio playback, spell casting or SaveGames.

A presentation snapshot is read-only and assembled from existing authoritative systems:

```text
Truth / authority (read only)          Artistic intent (review data)
 Story phase + allowed crew            Nine focus shots (#815)
 Map + actual collision/physics        Eleven lighting look candidates (#796)
 Time/season/weather (#798)            Audio/foley intent (not yet bound)
 Actor positions/visible interests     Shot framing + dramatic emphasis
 Real sound sources, magic events      Accessibility and performance caps
                \                         /
                  Presentation Snapshot
                           |
                 Safety / Priority Resolver
                           |
             Cinematic Experience Coordinator
                    (intent only)
                           |
         +---------------+---------+--------------+
         |               |         |              |
      Focus/DOF      World light   Audio owner    Authorized
       Camera         + weather    + mixing      VFX presentation
       (#815)         (#798 with   (not yet      (Ender spell cue;
                       #796 look    validated)    no spell authority)
                       presets)
         |
   QA telemetry, exact-head screenshot comparisons, frame timing
```

**Single-writer rule:** only one integrated owner applies each rendering control. `#796` is a *look parameter library* to reconcile into `#798` world atmosphere/lighting ownership; it must not independently spawn competing sun, SkyLight, fog or PP actors in gameplay. `#815` owns only authored camera focus intent and optical study. The final post-process/exposure owner remains to be selected explicitly during integration; no branch may assume it can freely introduce another full-screen unbound PostProcessVolume. UE assigns priority and blend weights to overlapping post-process volumes; equal priorities have undefined precedence.

### Data and implementation split

- **Declarative input:** `unreal/DataSource/Cinematics/FirstWakePresentationBindings.review.json` (nine focus shot IDs, six existing map IDs, references to original #796 lighting look identifiers and #798 weather modes, semantic sound intentions, story prerequisites and safety gates).
- **Existing focused optical profiles:** `FirstWakeFocusProfiles.review.json` for lenses/f-stop/focus.
- **Source-only gate:** `python unreal/Tools/validate_first_wake_presentation_bindings.py --self-test`.
- **Future runtime proposal:** a small `UGameInstanceSubsystem` or view-layer component that *reads* an immutable `FPresentationSnapshot`, resolves one `FPresentationIntent`, and forwards intents to existing owner components. Using a subsystem is a recommendation, **not** a completed class or native test. Avoid a global tick that spawns actors or traverses every scene object; cache named interest anchors and update only on significant state changes.
- **No circular effects:** presentation sends no commands to world progression. For example, the camera may respond to genuine `SeaContact` after physics established it, but never grant `SeaContact`, `Launched`, `FlotationConfirmed` or `LyraRecruited`.

## Priority, blending, and compositional grammar

Arbitration (highest to lowest):

1. **Accessibility and safety:** reduced-motion / DOF-off options, stable exposure, subtitles and interaction text, high-contrast hazards, ledge and ocean boundaries.
2. **Actual gameplay:** navigation, engineering interactions, enemy target readability, active movement and combat. Disallow focus hunting or shallow focus on high-speed gameplay.
3. **Authorized authored beat:** dialogue, hand/gauge inspection, ship response, viewpoint reveal or cinematic cut (only with proper state gate).
4. **World conditions:** time, weather, celestial visibility, altitude, terrain/occlusion, lamps and material wetness.
5. **Stylistic accent:** gentle practical bokeh, contained bloom, soft focus transition, chromatic effects; remove first under load.

Default visual stack: **world base** (time/weather) → **location** (biome/materials/lighting anchors) → **shot intention** (subject/lens/framing) → **accessibility & safety override**. Gameplay can override shot intention without altering the world. Never fake spatial distance with screen-wide blur; use world geometry, parallax, atmosphere, scale and occlusion. Treat star optics physically: distant stars may defocus in near-focus close-ups, while wide infinity-focus landscapes preserve crisp points plus separately controlled bloom.

**Suggested coordinator inputs (all read-only, availability must be confirmed):**

`story_phase_authoritative`, `map_id`, `camera_pose`, `active_focus_target`, `player_traversal_mode`, `camera_visibility`, `weather_mode`, `time_of_day`, `cloud_cover`, `altitude`, `wind`, `wetness`, `spell_event_authorized`, `physical_sea_contact`, `accessibility_reduced_motion`, `graphics_tier`.

**Proposed outputs:** `camera_focus_intent`, `exposure_look_intent`, `soundscape_mix_intent`, `authorized_visual_cue_intent`, and `qa_explanation`. These are presentation-only proposals. No new spell IDs, voice lines, actual audio event bindings, or production look assets are asserted by the JSON.

Focus transitions should be keyed to named story/interest anchors rather than an arbitrary periodic autofocus ray. Acquire stable targets, apply hysteresis and short hold on target loss, release on scene/interaction exit. Camera movement must not disorient player exploration. For visual review, compare the same lens/exposure/transform with DOF enabled and disabled.

## Cross-PR boundaries and known conflicts

| Source | Responsibility | Integration constraint |
|---|---|---|
| #813 P0 playable convergence | Player interaction, approved story progression, real sea/roster constraints | Read-only inputs; no camera-induced milestones |
| #814 six-map route review | Actual gated traversal/collision, ledge protection | No bokeh that hides off-map hazards |
| #796 lighting | Eleven look parameter candidates | Feed single lighting/atmosphere owner, not another duplicate sun/fog |
| #798 atmosphere | Day/night sky, seven weather modes, fog/clouds | Physical world response is primary; no arbitrary bokeh increase from rain |
| #815 cinematic bokeh | Nine shots, focus profile, isolated A/B map tooling | Only presentation. Editor prototype is not runtime controller |
| #804 audio draft | Intended event bank and audio route | No exact audio event IDs or audible success claimed in this integration |
| #810 Ender Centering / Resonant Pulse | Gameplay-authorized spell and preview VFX | No cast/resource changes from visual intensity |
| Character, ship, material drafts | Render sources / approved visual authority | Prototype lens targets are not creator-approved likenesses |

**Unresolved present gap:** There is no matched shore-night look within #796's eleven source presets. `FW09_NightSky_Wonder` intentionally has no lighting-look binding and must remain blocked from an invented mapped night shot. Existing harbor-night look must not be silently treated as a shore-night look.

Another present issue: legacy #796/#798 map-staging scripts use `EditorAssetLibrary.duplicate_asset` on a UWorld. A neighboring native integration observed a real unsafe duplication path; use the proven **two-process Save Map As** strategy in a fresh, disposable worktree, with source map hashes before and after. Do not wholesale reuse old staging scripts.

## Cinematic continuity examples

**Engine inspection (Ender):** authentic `ENGINE_INSPECTION` beat → engineering practical warm lighting from reconciled look → lens isolates Ender's hands and resonator gauge; real harmonic-machine hum grows from the audio owner → authorized inspection outcome reveals a physical response → focus may move *after* that event. Nothing in focus logic awards completion or asserts ship consciousness.

**Ionia hiring:** dialog gate → dusk harbor light from world clock → foreground rope and lantern parallax → actor-eye focus on Ionia/Ender in authored close-up → environmental ambience lowers beneath intelligible dialogue, if audio owner truly binds a mix → return to gameplay camera with readable pier/interaction cues.

**Emergency landing:** real physical trajectory and splash contact → atmosphere and sea spray respond to scene state → camera reverts to deep focus and horizon visibility → waterline, collision and two-second flotation evidence remain visible; avoid stylized focus pulses that fake the critical sea-contact event.

**Lyra introduction:** post-splashdown narrative gate only → shore-aftermath light, gentle ocean sound and restrained background bokeh → Lyra with Talen framed for human connection → *separate real dialogue/recruitment* controls whether Lyra becomes a party member. Reson/Aepex remain unavailable.

**Quiet stars:** full-story-legal night view, no Starbourne admission → near-infinity focus + restrained star bloom + world cloud/aurora visibility and distant wind → camera holds still long enough to establish scale; do not force "space travel" spectacle before the story unlocks it.

## Optimized production sequence: fewer redundant edits

1. **Now: contract only** — pin refs, names, owners, all nine mappings, 11 cross-system adversarial tests. Keep PR #815 draft. The contract is allowed to reference separate unmerged branches but **cannot assert they are integrated**.
2. **Reconcile the overlapping lighting/weather PP authorship** into a single draft composition base. Resolve actual C++/Blueprint APIs and source-test ownership before native compile. Keep story/physics/save code under its current owners.
3. **One safe native Harbor A/B** at exact SHA after RAM/disk gates, two Editor sessions, no duplicate UWorld asset copy; collect same-scene wide, shallow-focus, no-DOF captures. Compare exposure, skin placeholder limitation, depth and 50%-scale legibility. Avoid duplicating this into all six maps prematurely.
4. **One true connected narrative beat** (prefer engine inspection) in PIE: event -> presentation snapshot -> target focus, light look and sound intent -> return to gameplay. Observe genuine gameplay outcome independently of shot.
5. **Only then scale** to liftoff/splashdown, where safety outranks spectacle, and later to Lyra and optional celestial awe; profile GPU/CPU/memory on Neontic and measure weather/day/night variants.
6. **Approval gates** — exact source head, native Win64 Editor compile, automated + adversarial tests, actual PIE traces, screenshot/audio evidence, baseline and altered frame timings, reduced-motion and DOF-off checks, creator side-by-side review. No main merge based on source checks.

### Evidence vocabulary

- `DESIGN` or `SOURCE_VALIDATED` = declared contract and offline checks only.
- `NATIVE_MAP_SAVED` = a new map file and receipt only, **not** player integration.
- `PIE_TESTED` = on-device game behavior at exact head.
- `VISUALLY_REVIEWED` = user inspected native screenshots/clips.
- `CREATOR_APPROVED` = explicit design approval.
- `MERGED` = only after authorized merge.
- The workstation host gate last reported ~7.13 GiB free RAM, **13.26 GiB free disk** against 6.5/14.0 GiB review requirements; the native stage correctly returned `HOLD: LOW_DISK` and no map was written.

## Technical support

- Unreal Engine 5.8 cinematic camera focus (manual/tracking/disable and smoothing): https://dev.epicgames.com/documentation/en-us/unreal-engine/cinematic-cameras-in-unreal-engine
- Unreal Engine 5.8 Post Process Volume priority and blend radius: https://dev.epicgames.com/documentation/en-us/unreal-engine/post-process-effects-in-unreal-engine
- Unreal Engine 5.8 Post Process Material blendable priority: https://dev.epicgames.com/documentation/unreal-engine/post-process-materials-in-unreal-engine
- Unreal Engine 5.8 Audio Modulation overview: https://dev.epicgames.com/documentation/en-us/unreal-engine/audio-modulation-overview-in-unreal-engine
  - Audio Modulation is optional/disabled by default: **do not assume it is enabled or integrated**. Existing owned audio bank and native compile must be reconciled first.

**No unverified assertion in this document should be promoted to a gameplay or scientific fact by a downstream tool.**
