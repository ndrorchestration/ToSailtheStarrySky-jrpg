# First Wake — cinematic open-water postflight visual slice (review only)

**Date:** 2026-10-28  
**Source parent:** draft PR #551, exact `4da9e450e91adbdc9216f650e3fda2c1acf3c0f2`, ultimately stacked on #547's Godot default-first-flight source.  
**Status:** IMPLEMENTED as a reversible source-level visual candidate. **No merge, art approval, production certification or public release.**

## Why this is the priority

The real revised First Wake playable sequence goes from a source-derived 3D Aureate Wake/physical 2D splashdown into a very flat, drawn-rectangle shipboard inspection scene. This abrupt downgrade is the most obvious visual discontinuity in the integrated path. Address it **in the real playable Godot scene** before widening the art backlog.

## Added source-native rendering, independent of plot

- Original procedural stormbreak sky with multiscale cloud shading, warm horizon scattering approximation and a bounded sun halo. All done in a `canvas_item` GPU shader.
- Independently animated original deep-to-shallow ocean shader with three spatial wave frequencies and restrained reflected sun-path glints. **M** toggles the visual ocean motion off/on without affecting the physics or story; there is no new weather simulation or gameplay clock.
- New original maritime geometry: timber planks with grain highlights, metal seams, fasteners, brass rail and structural spars, ocean-facing shipboard furniture, an illuminated harmonic reserve console whose state changes only after the existing dialogue is actually completed.
- Top and bottom high-contrast cinematic panel beds keep all real current dialogue, movement, story, checkpoint and accessibility controls intact.
- Deck remains **the same fictional local open-water, post-splashdown shipboard location**; no shore, world navigation, tow, future flight or hidden ship mode is implied. Actor movement bounds, positions and interaction distance are unchanged.
- All drawing/lighting helpers are presentation nodes: no `Area2D`, `RigidBody2D`, colliders, party roster, character art replacement, inventory, save schema, fuel-solution authority, or stage mutation.

## Exact source changes

- `godot/shaders/first_wake_cinematic_sky.gdshader`
- `godot/shaders/first_wake_cinematic_sea.gdshader`
- `godot/scripts/first_wake_cinematic_seascape.gd`
- `godot/scripts/first_wake_cinematic_deck_architecture.gd`
- `godot/scripts/first_wake_postflight_game.gd` now attaches the environment as actual background to live Ender/Ionia and exposes reversible still-water option.
- Dedicated independent native shader/motion test and live renderer screenshot test from **actual** playable opening → engineering → warning → RigidBody2D/Area2D splashdown → reserve dialogue, checked in both official workflows.

## Evidence gates and limitations

1. Headless native Godot 4.7.2 **must** parse/import and pass `TSTSS_FIRST_WAKE_CINEMATIC_DECK_PASS`, plus inherited `TSTSS_FIRST_WAKE_GAME_ENTRY_PASS` and all regressions.
2. Real Godot Compatibility GL on the official rendering job **must** pass `TSTSS_CINEMATIC_DECK_CAPTURE_PASS`. Three actual 960x640 frames: uninspected console, player-inspected console and still-water mode. Console pixel delta must change. Runner-only PNG/hash evidence is not a downloadable build or artistic signoff.
3. **OPEN**: actual screenshot examination, light/color grading by an artist, source-locked character assets, authentic environmental texture maps, physically correct 3D deck, source-locked vessel material parity, effects profiling on target PC, reduced-motion player study, multi-resolution HUD legibility, uncoached full gameplay and opening-to-postflight continuity review.
4. **BLOCKED**: public downloadable installer and final release. Parent #551 functional installer work is tested but its independent Windows Defender realtime-on security gate is not green; this branch neither changes nor bypasses it.

This work demonstrates a **production-oriented visual pipeline** (shader + parametric scenic art + genuine game admission + playable state-reaction + image captures), **not** that procedural graphics alone meet final cinematic standards. Next visual milestone: produce and review actual 960x640 frame samples; then material/lighting/character continuity across dock → engineering → flight → deck, before considering any art promotion.
