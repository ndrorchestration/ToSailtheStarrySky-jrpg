# First Wake — V2 native Prelude level and pending PIE verification

**Updated November 2, 2026.** A tracked seven-stop native
`/Game/TSTSS/Review/FirstWake_PreludeInteraction_V2` map is available
in the unmerged review stack [#694](https://github.com/ndrorchestration/ToSailtheStarrySky-jrpg/pull/694)
→ [#703](https://github.com/ndrorchestration/ToSailtheStarrySky-jrpg/pull/703)
→ [#704](https://github.com/ndrorchestration/ToSailtheStarrySky-jrpg/pull/704)
→ [#712](https://github.com/ndrorchestration/ToSailtheStarrySky-jrpg/pull/712).
The map's recorded SHA-256 is
`4c96f1fb28fe4af91b879977e473c20de32bd933f741a5384bb8403a00254b80`.
This is a **noncanonical review level**, not a fully playable or
accepted First Wake.

The explorer has third-person movement and camera input. Its E
interaction ray accounts for the **360 cm camera boom** while still
enforcing a **separate 300 cm pawn reach** and visibility test. J can
recall the read-only objective; F5/F9 use an isolated test slot in PIE,
protecting existing review saves from new-session overwrites. These
source-level features and portable C++ tests have passed hosted CI at
inspected #712 head `a1b07b64841c2cb6b735fdd66f2ecd6426cab016`,
but **native PIE input has not been verified on that head**.

**Actual scene scope:** Flyer, Ionia, boarding, three separate
engineering inspections and engineering signoff. The native V2 map
has no proven interactive launch, sea-contact or flotation sequence.
Treat the following older manual assembly notes as a reference only;
do **not** build a second redundant milestone map or insert synthetic
water/Chapter 1 markers to satisfy a test.

1. Compile Unreal 5.8 editor target and run the automation suite, recording the exact branch SHA.
2. Create a persistent coastal level in Unreal Editor, configure a PlayerStart on traversable collision, and verify the project's default TSTSSGameMode spawns TSTSSExplorerCharacter.
3. Place TSTSSMilestoneActor instances and give each a collidable StaticMesh. Assign the milestones in narrative order: flyer, hire Ionia, board, engineering, launch, sea contact, flotation, reserve inspection, berth return.
4. Early proof uses distinctly positioned objects; *do not call these objects the final characters, ship, or cinematic art*. Actual Ionia conversation, physically verified sea contact and launch animation require authored levels and new logic; the milestone actor is just a progression gate.
5. Validate camera tracing, blocked obstacles, ordered advancement, reset behavior, save/load state, and Windows input before claiming playable First Wake.
6. Replace proxy milestone triggers with game actions and real collision/physics/interaction evidence. Do not auto-award sea contact or flotation through a camera cut.
7. Import artistically approved character assets separately; verify hair silhouette, facial design, costume and materials via native renderer captures against approved references.

The earlier text-only milestone did not include a map, but the
later draft #694 **does include a committed V2 `.umap`**. Its exact
hash is separately checked by source QA. A native compiled editor and
fully exercised PIE run for current #712 remain pending; neither
stand-in art nor a seven-marker map proves the game's playable opening.

## October 30 preflight integration
Three interactions from the Godot #547 contract are now modeled in Unreal source as separate stations: Lift, Pressure, Reserve. Place three `ATSTSSMilestoneActor` instances with `bIsInspectionStation=true` and unique `InspectionStation` values. These must be accessible after boarding the Aureate Wake. An ordinary milestone actor with `Milestone=EngineeringChecked` will reject activation unless all three inspections have occurred. Duplicate inspections and early station calls are rejected. The inspection mask is persisted in `UTSTSSSaveGame` version 2, and restoring incomplete inspection evidence past engineering sign-off is rejected.

**Migration caveat:** version-1 Unreal saves are intentionally unsupported by this schema; no automatic conversion is implemented. Godot saves are not imported. The new station data are logic-only; authored meshes, text prompts, check feedback, engine animations and native testing remain open. Physics-verified sea contact/flotation from Godot #547 still require a separate Unreal implementation and must not be satisfied by generic milestone clicks.

## Exact next review operation (November 2, 2026)

Use [the 13-case PIE acceptance matrix](FIRST_WAKE_V2_PIE_ACCEPTANCE_MATRIX_2026-11-02.md)
and [Unreal test commands](UNREAL_TEST_COMMANDS.md), in a fresh isolated
checkout with no pre-existing test-save conflict. Require UHT, Editor
build, 25/25 named tests and P01–P13 actual keyboard evidence at one
exact SHA. Reconcile native input, collision, text and save reports
before doing any aesthetic work; preserve the map hash and clean tree.
A missing Windows workstation or an existing potentially valuable
save is a **BLOCKED**, not PASS and not permission to uninstall tools
or delete saves. Starbourne, ship water physics, cast approval and
Splashdown remain separate HOLD gates.
