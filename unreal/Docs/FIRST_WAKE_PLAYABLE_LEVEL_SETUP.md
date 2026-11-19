# First Wake native level assembly — not yet tested in editor

The C++ project now provides an explorer pawn with spring-arm follow camera, keyboard movement and camera mouse axes. Press E to line-trace from the camera to a milestone actor within 300 Unreal units. An interaction advances only its exact next ordered beat.

1. Compile Unreal 5.8 editor target and run the automation suite, recording the exact branch SHA.
2. Create a persistent coastal level in Unreal Editor, configure a PlayerStart on traversable collision, and verify the project's default TSTSSGameMode spawns TSTSSExplorerCharacter.
3. Place TSTSSMilestoneActor instances and give each a collidable StaticMesh. Assign the **manually interactable** milestones in narrative order: flyer, hire Ionia, board, engineering, launch, reserve inspection and berth return. **Do not place generic interaction actors for SeaContact or FlotationConfirmed.** Those beats require a separately implemented, validated physics-backed water/ship evidence adapter; until then the complete First Wake route is NOT playable in Unreal.
4. Early proof uses distinctly positioned objects; *do not call these objects the final characters, ship, or cinematic art*. Actual Ionia conversation, physically verified sea contact and launch animation require authored levels and new logic; the milestone actor is just a progression gate.
5. Validate camera tracing, blocked obstacles, ordered advancement, reset behavior, save/load state, and Windows input before claiming playable First Wake.
6. Replace proxy milestone triggers with game actions and real collision/physics/interaction evidence. Do not auto-award sea contact or flotation through a camera cut.
7. Import artistically approved character assets separately; verify hair silhouette, facial design, costume and materials via native renderer captures against approved references.

No maps, characters, meshes or binaries have been committed by this text-only milestone. Native compile and gameplay verification are outstanding.

## October 30 preflight integration
Three interactions from the Godot #547 contract are now modeled in Unreal source as separate stations: Lift, Pressure, Reserve. Place three `ATSTSSMilestoneActor` instances with `bIsInspectionStation=true` and unique `InspectionStation` values. These must be accessible after boarding the Aureate Wake. An ordinary milestone actor with `Milestone=EngineeringChecked` will reject activation unless all three inspections have occurred. Duplicate inspections and early station calls are rejected. The inspection mask is persisted in `UTSTSSSaveGame` version 2, and restoring incomplete inspection evidence past engineering sign-off is rejected.

**Migration caveat:** version-1 Unreal saves are intentionally unsupported by this schema; no automatic conversion is implemented. Godot saves are not imported. The new station data are logic-only; authored meshes, text prompts, check feedback, engine animations and native testing remain open. Physics-verified sea contact/flotation from Godot #547 still require a separate Unreal implementation and must not be satisfied by generic milestone clicks.
