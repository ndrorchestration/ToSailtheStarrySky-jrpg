# Aureate Wake UE 5.8 Four-Form Geometry Preview

**Not playable / native build not yet verified.** A deliberate test-actor implementation staged against draft Unreal bootstrap PR #608, not the Godot release.

- Spawn `AAureateWakePreviewActor` in a dedicated test level (or Blueprint derived from this actor).
- `RequestForm(Skyborne/Seaborne/Submersible)` moves four persistent mesh components toward deterministic target poses over `TransitionSeconds`.
- `RequestForm(Orbiter)` fails unless `bAllowOrbiterPreview` is deliberately enabled **for isolated demonstration only**. Real story gates need their own future authority.
- Exactly four equal-scale Orbiter wing meshes arrange along +Z/-Z/-Y/+Y with an unchanged forward-facing (+X) bridge/hull.
- Hydrofoils extend only in Seaborne; submerged wings remain visibly folded.
- This geometric study uses engine cube shapes, not approved model art. The current geometry does not guarantee hinge fidelity, real solar-panel/light-sail materials, hull sealing, collision-safe articulation, flotation, pressure physics or orbital travel.
- Next: compile UE 5.8 with Windows C++ toolchain, instantiate actor, capture all four forms and transition sequence, check mesh counts, positions, transformations, materials, and approval against Visual Bible. Preserve protected main.

Suggested manual smoke: instantiate actor; assert 4 wings & 2 hydrofoils; request Sea and advance >2.5 s; observe two foils; request Submersible and inspect four visible tucked panels; confirm Orbiter blocked by default; set opt-in true and request Orbiter; confirm four equally scaled sails at cardinal directions with forward bridge.
