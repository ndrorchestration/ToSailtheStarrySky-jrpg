# First Wake native level assembly — not yet tested in editor

> **V2 review-map update — November 1, 2026.** [Draft #694](https://github.com/ndrorchestration/ToSailtheStarrySky-jrpg/pull/694) now tracks a **real** V2 Prelude `.umap` (56,053 bytes; SHA-256 `4c96f1fb28fe4af91b879977e473c20de32bd933f741a5384bb8403a00254b80`) with seven native milestone/engineering stations. A seven-actor V2 milestone-order verification was observed in a review sandbox, but **keyboard-driven PIE walking, E interaction and F5/F9 keypress save/load are not accepted**. [Draft #703](https://github.com/ndrorchestration/ToSailtheStarrySky-jrpg/pull/703) provides separate V2 map/provenance and native persistence QA source; its exact-head native execution remains open.

> **E-interaction defect and correction:** native camera spring arm `360 cm` exceeds the original camera-origin interaction ray `300 cm`, so a legitimate target directly ahead could be outside the ray. [Draft #704](https://github.com/ndrorchestration/ToSailtheStarrySky-jrpg/pull/704) extends the ray to camera→pawn distance plus 300 cm **without increasing pawn-to-target reach**, registers test #24, and source-checks it. Its Game-target native build succeeded on the C++ ancestor, but raw un-packaged startup crashed; do not claim a live playable interaction.

**Level-review sequence for V2:** verify actual `/Game/TSTSS/Review/FirstWake_PreludeInteraction_V2` map and hash in its own checkout; confirm floor blocks, visual sea has NoCollision and story actor count exactly seven. Then test physical keyboard movement/camera, E activation at reachable vs unreachable distances with obstruction, F5/F9 restoration, and stable objective feedback in PIE. Do not award `SeaContact`, `FlotationConfirmed`, Lyra recruitment or Chapter 1 Act 1 from a stage prop. [Dependency and evidence register](DEPENDENCY_AND_EVIDENCE_REGISTER_2026-11-01.md).

### Archived initial setup text

The original instructions below describe the pre-map stage and are preserved as a historical checklist.


The C++ project now provides an explorer pawn with spring-arm follow camera, keyboard movement and camera mouse axes. Press E to line-trace from the camera to a milestone actor within 300 Unreal units. An interaction advances only its exact next ordered beat.

1. Compile Unreal 5.8 editor target and run the automation suite, recording the exact branch SHA.
2. Create a persistent coastal level in Unreal Editor, configure a PlayerStart on traversable collision, and verify the project's default TSTSSGameMode spawns TSTSSExplorerCharacter.
3. Place TSTSSMilestoneActor instances and give each a collidable StaticMesh. Assign the milestones in narrative order: flyer, hire Ionia, board, engineering, launch, sea contact, flotation, reserve inspection, berth return.
4. Early proof uses distinctly positioned objects; *do not call these objects the final characters, ship, or cinematic art*. Actual Ionia conversation, physically verified sea contact and launch animation require authored levels and new logic; the milestone actor is just a progression gate.
5. Validate camera tracing, blocked obstacles, ordered advancement, reset behavior, save/load state, and Windows input before claiming playable First Wake.
6. Replace proxy milestone triggers with game actions and real collision/physics/interaction evidence. Do not auto-award sea contact or flotation through a camera cut.
7. Import artistically approved character assets separately; verify hair silhouette, facial design, costume and materials via native renderer captures against approved references.

No maps, characters, meshes or binaries have been committed by this text-only milestone. Native compile and gameplay verification are outstanding.

## October 30 preflight integration
Three interactions from the Godot #547 contract are now modeled in Unreal source as separate stations: Lift, Pressure, Reserve. Place three `ATSTSSMilestoneActor` instances with `bIsInspectionStation=true` and unique `InspectionStation` values. These must be accessible after boarding the Aureate Wake. An ordinary milestone actor with `Milestone=EngineeringChecked` will reject activation unless all three inspections have occurred. Duplicate inspections and early station calls are rejected. The inspection mask is persisted in `UTSTSSSaveGame` version 2, and restoring incomplete inspection evidence past engineering sign-off is rejected.

**Migration caveat:** version-1 Unreal saves are intentionally unsupported by this schema; no automatic conversion is implemented. Godot saves are not imported. The new station data are logic-only; authored meshes, text prompts, check feedback, engine animations and native testing remain open. Physics-verified sea contact/flotation from Godot #547 still require a separate Unreal implementation and must not be satisfied by generic milestone clicks.
