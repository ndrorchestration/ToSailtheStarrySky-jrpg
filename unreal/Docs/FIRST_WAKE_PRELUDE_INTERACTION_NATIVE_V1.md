# First Wake Prelude — isolated Unreal 5.8 interaction level

**Scope:** review-only, playable-input candidate, not accepted chapter gameplay. **Parent:** PR #685 native-verified combat branch `813abdce5fd74ac32f685b9d6dbbee17d3863e7c`.

## Why this slice

The existing Unreal project had a native explorer pawn, W/A/S/D + camera input, E interaction trace, F5/F9 quick save/load, versioned First Wake story state, milestone actors and three engineering checks. It had **no committed level** where those systems could be experienced together.

`unreal/Tools/build_first_wake_prelude_interaction.py` authors an explicitly named **new** `.umap` in a uniquely named isolated Windows checkout. It places actual compiled `ATSTSSMilestoneActor` instances rather than fake completion calls, a collision floor, a `PlayerStart`, sign actors, visual-only harbor/sea primitives, a review camera and sky lighting. The global GameMode already uses `ATSTSSExplorerCharacter`; no production runtime C++ is modified.

## Ordered station sequence

**Flyer discovered → Ionia hiring marker → boarding marker → three separate Lift/Pressure/Reserve inspections → Engineering Checked.** The ordering and duplicate/out-of-sequence rejection are enforced by the existing native First Wake state. Each marker is a primitive and must not be mistaken for approved Ionia, Ender, the ship or a cutscene. There is no actual conversation, recruitment roster write, or voiced character in this prototype. Ender alone is the implicit POV.

## Strict safety limits

- **No `Launched`, `SeaContact`, or `FlotationConfirmed` activation:** the sea visual is a noncolliding plane; only the actual native water/physics observer may advance sea beats. Therefore this stage remains in the Prelude, not Chapter 1 Act 1 Splashdown.
- **No Lyra, Talen, Reson or Aepex preflight spawns**; no Orbiter reveal, no Five Lights combat abilities.
- **No startup map switch.** The saved map lives at `/Game/TSTSS/Review/FirstWake_PreludeInteraction_V1` and does not replace an existing map. The source builder refuses dirty maps, overwritten review map or project folders outside `C:\TSTSS_FirstWakePreludeSandbox_20261101\unreal`.
- Meshes are **Unreal BasicShapes review stand-ins**, not final cinematic assets, authored hull or concept-art match. Props are not physically authoritative.

## Native Windows reproduction and completion gates

1. Prepare a clean isolated checkout of the draft review branch into **exactly** `C:\TSTSS_FirstWakePreludeSandbox_20261101`. Confirm exact SHA, clean tracked worktree, Engine 5.8.4 and installed MSVC. Never stage in a production checkout.
2. Run `python unreal/Tools/build_first_wake_prelude_interaction.py --validate` and `python -m unittest discover -s unreal/Tools -p test_first_wake_prelude_interaction.py -v`. These are only source checks.
3. Compile `ToSailTheStarrySkyEditor Win64 Development` for the isolated `unreal/ToSailTheStarrySky.uproject`. Use the already-proven UE5.8 target settings. Keep parallel editor sessions untouched.
4. Enable **Python Editor Script Plugin** for the disposable review project. Execute `build_first_wake_prelude_interaction.py --build` inside UE Editor via a tiny isolated `-ExecutePythonScript` wrapper, with `sys.argv` set explicitly. Verify actual saved `.umap` SHA receipt at `Saved/PreludeInteractionV1/native_staging_receipt.json`. Do not infer map creation from a log line.
5. Open the map in Unreal Editor and Play in Editor: confirm **real** explorer pawn and PlayerStart, move/camera, E line trace/range, milestone rejection/acceptance, all three inspections, quick-save F5/quick-load F9, obstacle collision, and no ability to fake sea-water progression. Record actual editor play evidence/screenshot. Native C++ unit tests are not a substitute for the final hands-on experience.
6. Real 1280×720 D3D11 screenshots, performance and visual assessments belong to separate approval gates. A `.umap` file and spawn receipt do not prove playable navigation.

A generated binary `.umap` may be reviewed in the draft PR only after current-head generated-asset verification and separate owner art approval; source design is not a production scene or guarantee of artistic fidelity.

**Status:** source authoring implementation exists; native staging/PIE/renders must be independently run and documented. Owner controls canon, merges, public releases, and production art promotion.
