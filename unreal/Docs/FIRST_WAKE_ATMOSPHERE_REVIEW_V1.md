# First Wake atmosphere and weather — Unreal 5.8.4 review V1 (2026-11-10)

**Status: IMPLEMENTED SOURCE CANDIDATE / NATIVE AND ART ACCEPTANCE HOLD.**
**Authority:** Creator's [First Wake master matrix](https://app.notion.com/p/3ecf5bad238b8103b313f79ea816a9b5), VS-D04/D05/D07; [Chapter One quality checklist](../../docs/CHAPTER_ONE_HIGH_QUALITY_POLISH_CHECKLIST_2026-10-28.md), CH1-18/19. The [First Wake shot plan](../DataSource/Cinematics/FirstWakeShotPlan.review.json) is a *proposed* cinematic shot contract, not an approved frame.

## Delivered in this isolated branch

- New runtime, Blueprint-callable `ATSTSSAtmosphereDirector` actor owns the primary sun, secondary moon, physically based SkyAtmosphere, sky fill, volumetric-cloud component, volumetric height fog, translucent procedural star/aurora dome, and camera-local rain and snow instance renderers.
- Seven mutually exclusive precipitation/weather presets: **Clear, CoastalMist, Rain, Storm, Snow, Blizzard, AuroralVeil**. Profiles are rendering only, with independent 24-hour clock control.
- Day-to-night controls: `RequestTimeOfDay(Hour, Seconds)` and `RequestWeather(Preset, Seconds)`. Smooth-step crossfade is interruptible and shortest-arc midnight-safe. In-game passage of time is **not** silently accelerated or determined by story progress.
- Storm mood depends on darker sky, fog scattering and cool light; there is **no automatic strobing lightning**. Cloud layer thickness, sunlight attenuation, fog density and moving precipitation vary with the weather profile.
- Night uses original procedural star points and teal/blue auroral curtain, gated by actual night factor. Aurora is a visible lookdev veil, *not* permission to open any navigation lane or celestial story gate.
- Rain and snow instance positions are deterministic, camera-local, collisionless and purely visual. These are bounded no-texture **preview emitters**, not a Niagara-quality production rain volume. Footprints, puddles, water-state/sea-contact and accumulation remain separate.
- `SetReducedMotion` snaps pending transitions, freezes star/aurora modulation, disables camera-local precipitation and halts preview cycling. `SetLowQuality` removes volumetric cloud expense and lowers precipitation instance work without changing game logic.
- Five one-click Editor presets plus an **opt-in review-map autoplay cycle** for daylight, coastal golden hour, storm dusk, snow night and aurora night. Do not enable autoplay on story/playable production scenes.
- Opt-in Unreal Editor Python script creates 3 original procedural materials and duplicates the existing First Wake Prelude *review* map into `/Game/TSTSS/Review/Atmosphere_V1/M_FirstWakeAtmosphereReview`. The source map is not edited. In the copied map only, its two historical placeholder light actors are removed so there is exactly one light authority. The native C++ director is placed, with a built-in UE EngineSky volumetric-cloud material.
- Strict preflight refuses occupied review destination, dirty Editor changes, missing source map, unavailable compiled actor, or missing EngineSky cloud asset. No deletion/overwrite fallback.
- Engine-free test file exercises 9 positive/negative cases. One native C++ Editor automation test covers seven profile bounds, precipitation exclusivity, shortest-arc midnight and clamped blending.

## Preview usage

From the worktree root:

```powershell
python unreal/Tools/build_first_wake_atmosphere_review.py --validate
python -m unittest discover -s unreal/Tools -p test_first_wake_atmosphere_review.py -v
```

**Native admission only after physical RAM >= 6.5 GiB, C: free >= 14 GiB, and no competing Editor/game build.**

1. Run UE 5.8.4 `Build.bat ToSailTheStarrySkyEditor Win64 Development -Project=<worktree>/unreal/ToSailTheStarrySky.uproject -NoXGE -MaxParallelActions=2`; log exact exit and source SHA. Don't build against the parallel workers' active project directories.
2. With a clean editor and freshly built module, run `UnrealEditor-Cmd.exe <uproject> -d3d11 -ExecutePythonScript="<worktree>/unreal/Tools/build_first_wake_atmosphere_review.py --build"`. Review Editor log and material compiler errors; a positive process exit alone does not establish shader validity.
3. Require a saved duplicate `.umap` and `Saved/AtmosphereReviewV1/staging_receipt.json`. Test native automation `TSTSS.Atmosphere.PresetsAndNightContinuity` plus existing First Wake suite on that exact compiled head.
4. Load review-only atmosphere map, run PIE from the real Ender proxy and observe a full weather preview loop. Capture fixed camera and motion video for golden hour, blue hour, night, rain, storm, snow, aurora, and the transition midpoints. Compare to the original source review map at matched camera pose/time; record exposure and RHI. Inspect sky visibility through bridge glass, horizon curvature, sea specular continuity and character interaction signage.
5. Compare effects with low-quality and reduced-motion toggles; measure frame times/VRAM and watch shimmer, translucency sort order, moon direction, fog distance, cloud depth and emitter pop. Preserve native image/video hashes and creator acceptance separately.

**Native compile, shader compilation, map staging, GPU captures, PIE route and visual approval must be reported individually.** None is implied by source QA. Creator review required before any material, weather palette, image or timeline becomes approved production art.

## Provisional shot lookdev, not story canon

| First Wake beat | Optional review look | Status |
|---|---|---|
| Harbor flyer / first encounter | CoastalMist, 17:00 local look, warm sun and salt haze | PROPOSAL |
| Engineering / bridge | Inherit exterior grade through skylights; interior brass/teal practicals independent | PROPOSAL |
| First ascent / open sky | Clear, bright atmospheric scattering and layered cloud banks | PROPOSAL |
| Abnormal phase drift | Storm/dusk lighting and rising obscuration, without implying a new meteorological cause | PROPOSAL |
| Controlled sea landing | Rain/spray-readable profile; no effect is permitted to prove water contact | PROPOSAL |
| Shoreline aftermath | Calm readable coastal grade and gentle weather transition | PROPOSAL |
| Snow / blizzard | Optional high-latitude biome/material review ONLY; not a new mandatory opening beat | NOT IN FIRST WAKE ROUTE |
| Auroral veil | Celestial aesthetic/sky-lane look only; Starbourne gate remains locked | PROPOSAL |

## Independent acceptance constraints

- **VS-D04:** source-only candidate until real cloud/light/fog/exposure render is observed and compared; no black sky, opaque star dome, double sun or washed-out HUD.
- **VS-D05:** candidate atmospheric and precipitation VFX, no gameplay effect or physical-world truth; no false ocean collision, ship repairs, spell, affinity, or quest permissions.
- **VS-D07:** remains OPEN until exact-head real D3D GPU capture, matched side-by-side visual review and creator acceptance.
- **CH1-18:** sand/snow *surface* optical look is controlled by the existing Journey-inspired review document/PR #753. Falling snow is not accumulated ground snow, and no copyrighted texture or reference asset has been imported.
- **Accessibility:** no automatic lightning flashes; avoid compulsory time-of-day skips, preserve readable silhouettes and UI; reduced motion and low tier must be independently checked.
- **Collaboration:** branch is isolated, stacked on cinematic handoff #790 and does not merge #638/#753/other concurrent map branches. Integration must reconcile all source/asset owners first and may require rebase/cherry-pick, not map copying.

## Explicitly not delivered

No packaged playable sky/weather level, stable 60fps GPU evidence, asset approval, Niagara production precipitation, physically correct lightning/thunder, snow footprints/accumulation, soundscape/audio cues, replicated weather, global planet-time system, biome-based seasonal simulation, or authored wet-material interaction. No production map, default game mode, objectives, SaveGame, combat, recruitment order, real water contact, or Starbourne path was changed.
