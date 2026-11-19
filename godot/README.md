# Aetherwake — Godot 4.7.2 / GDScript migration feasibility pilot

**Status:** Isolated native-engine proof, **not** a complete migration, creator-accepted art, scene/canon rewrite, approved release, or evidence that production is now Godot.

## Objective

Move the *next technical vertical slice* off the legacy `p5.js / NW.js / JavaScript` implementation and evaluate a **purpose-built Godot 4 scene graph** with GDScript. Existing JavaScript sources remain a reference for story, save semantics and gameplay rules; no backwards-compatibility or save-data migration has been attempted.

This small opt-in Godot project contains a dock visual-grounding test, playable movement for Ender using `CharacterBody2D` and y-sorted actors, Ionia interaction at proximity, and a **distinct scene** for a trivial turn-based test arena. The numerical mock combat is **NOT** the actual Aetherwake encounter formula and must not be mistaken for an implemented migration. The dock terrain is **pilot geometry only** and does not authorize world route/canon changes.

## Run

Open `godot/project.godot` in **Godot 4.7.2 Standard (GDScript)** and press F6 or Play. Arrow keys move Ender; E interacts near Ionia; B opens the separate battle test; in that scene 1 strikes, 2 guards, R returns. No NW.js, npm or browser runtime is used.

```bash
Godot_v4.7.2-stable_linux.x86_64 --headless --path godot --editor --quit
Godot_v4.7.2-stable_linux.x86_64 --headless --path godot --script res://tests/smoke_test.gd
```

## Explicitly not delivered

- **Final art:** Actor silhouettes are drawn from primitive shapes, conspicuously not approved character sprites. The separate original Ionia SVG candidate on `art/ionia-original-v01-20261021` is **not automatically promoted**; its eye-color rendering and visual compliance must be reviewed against approved canon before use.
- **Gameplay:** No faithful migrated quest route, no inventory, no independent movement topology, no real stat/ability combat, no real assets/cutscenes/UI transitions, no multi-direction animation source, no save migration.
- **Release:** No Windows installer or export, signed admission, gameplay acceptance, third-party security review or changes to the Defender #293 hold.

## Migration gate

Compare this pilot against the existing `First Wake` contract. Establish: full play route and controls; matching authored map geometry/collision; Ender approved likeness; Ionia design/eye-color and original layered art; actual encounter mechanics in separate turn-based arenas; save/load parity and recovery; native-scale screenshots and tests; then a creator-approved engine-choice/production promotion. Keep the first Godot integration draft and the legacy production branch distinct until these gates pass.
