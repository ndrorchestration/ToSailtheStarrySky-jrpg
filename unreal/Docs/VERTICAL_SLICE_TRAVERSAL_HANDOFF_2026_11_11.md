# First Wake — PIE-only six-scene traversal handoff (source candidate)

**Status:** source-authored candidate, not a native Unreal build, saved traversal map, player test or cinematic approval.

**Parent:** [environment map draft #794](https://github.com/ndrorchestration/ToSailtheStarrySky-jrpg/pull/794), based on the original six native review maps (hashes in `unreal/Docs/Evidence/vertical_slice_map_authoring_20261110.json`). The original maps must remain immutable.

## Runtime additions

- `UTSTSSReviewRouteSession`: session-memory-only `UGameInstanceSubsystem`; refuses non-PIE worlds, arbitrary current/target map names and out-of-sequence transitions. Each request is bound to the exact source stage and only the next destination.
- `ATSTSSReviewRouteGate`: explicit E/visibility-ray interaction only, using Ender's existing 300 cm pawn-distance verification. An overlap or actor BeginPlay never progresses the story. Serialized solid collision is reconfigured at BeginPlay to keep the route walkable.
- `ATSTSSExplorerCharacter`: preserves existing movement, interaction, F5/F6/F9 ownership; adds a second hit target type for route gates and a one-shot destination-bound `UTSTSSFirstWakeState::Restore` when a freshly spawned pawn arrives. Snapshot includes **only** started=true, First Wake beat and three-bit inspection mask. No party, ship position, inventory or SaveGame mutation.

## Explicit route admission

| From | To | Required real beat |
|---|---|---|
| Denith Harbor | Aureate interiors | BoardedAureateWake (or existing EngineeringChecked state with 3 inspected stations) |
| Aureate interiors | First Wake sky review corridor | Launched, with all 3 inspections |
| Sky review corridor | Physical water lab | Launched, with all 3 inspections |
| Physical water lab | Denith fuel shanty | FlotationConfirmed by native hull-water observation, with all 3 inspections |
| Fuel shanty | Splashdown shore | EmptyReserveInspected after flotation, with all 3 inspections |

There is no exit from the final shore review map. Unstarted, out-of-order and unknown stages are denied; dry hull contact, generic markers, and the transition code cannot forge SeaContact or FlotationConfirmed. This is not full playable skyflight, global streaming, cross-session Continue, Lyra recruitment, or Starbourne authorization.

## Additive stage authoring

`unreal/Tools/build_vertical_slice_traversal_overlays.py` creates **six separate new** `...TraversalReviewV1.umap` copies under `/Game/TSTSS/Review/VerticalSliceTraversal`. It deliberately refuses overwrite, dirty branch, incorrect expected HEAD, mutable base map hashes, or missing native route class.

New review additions, when the Unreal editor eventually builds this source:

- Denith: explicit gated boarding passage, visual prompt and edge barriers.
- Ship: real inspection/engineering/launch marker actors in place of inert instrument props, clear prompts, four outer containment rails.
- Sky: explicit *walkable review corridor* and camera context; no claim of physical airborne traversal.
- Sea: dry player observation catwalk **above** water surface, authentic native water adapter still responsible for flotation, guarded post-contact passage.
- Shanty: post-contact reserve inspection marker, pier approach gap, shore access.
- Shore: on-foot safe terrain and end-of-review cue, no premature party additions.

The collision review barriers are specifically intended to prevent Ender walking off unfinished platforms as previously observed in playtests. They are not final level architecture or a substitute for shoreline/ship navigation design.

## Tests and outstanding QA

Source: `py -3 -m unittest discover -s unreal/Tools -p 'test_*.py' -q`; schema/route specific `test_vertical_slice_route_contracts.py`; native automation additions were made inside the **existing** `TSTSS.FirstWake.InteractionToSplashdown` registered test to avoid silently increasing the required registry from 29. Existing water authority and save contract tests remain unchanged.

Once resource admission permits, compile current-source UE 5.8.4 module, stage new traversal maps **once**, reopen and verify package manifests/collision actors, perform actual PIE keyboard E interactions over all five transitions, observe stable water contact for >=2 real seconds before flotation, reject invalid/foreign states, run 29 native automations and authentic GPU captures, and only then seek visual and gameplay approval. A source-only test or NullRHI map readback does not establish complete gameplay.
