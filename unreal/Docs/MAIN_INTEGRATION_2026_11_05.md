# Unreal development baseline integration — November 5, 2026

## Scope and authority

The creator explicitly requested: **Build and merge as much as you can.** This integration brings the existing, opt-in Unreal development foundation to `main`. It does not authorize a release, approve candidate art, change numerical character balance, or unlock Starbourne. Earlier documents describing this source as draft-only are dated evidence, not the current integration disposition. GitHub's integration PR remains authoritative for whether the merge has completed.

Source baseline: `main` at `725ecc5f56516466d46987fb04421f4decb5d5ef`.
Runtime candidate: title/opening PR [#776](https://github.com/ndrorchestration/ToSailtheStarrySky-jrpg/pull/776), exact source `4e57dc18a4d09c71309a529f33454cc1b99d81b8`.
The integration preserves that candidate's complete `unreal/Source`, project, configuration and map bytes. Additional changes are documentation, whitespace cleanup and enabling the existing Unreal source workflows on pushes to `main`.

## Included implementation

- Unreal C++ project and First Wake state, ordered milestone interaction, camera reach and review objectives.
- Combat turns, early-story party constraints, guarded skill/data contracts, passive hybrid class selection board and Ender equipment/combat review fixture.
- Versioned save validation and protected review save/load; F6 in PIE, F5 in standalone Game, F9 guarded restore. This is story/inspection persistence, not a complete player save system.
- Query-only traversable review markers and the committed seven-stop Prelude review map.
- Opt-in title screen, private-movie playback support, fallback interface and return to the loaded review scene.
- Source checks, portable C++ behavioral checks, 29-name native automation registry, native verification and map admission tools.
- Unreal-first documentation, creator Level 1 relative ranks, and the continuous realistic-cinematic visual quality criteria selectively carried from [#736](https://github.com/ndrorchestration/ToSailtheStarrySky-jrpg/pull/736). No checklist acceptance box is closed.

## Verification and its limits

At source `4e57dc18`, GitHub reported successful source preflight, source inventory and browser smoke. PR #776 records an exact-head UE 5.8.4 Win64 build, 29/29 native automation results and a D3D11 title-to-review-scene Enter interaction. Those are retained prior-run records; the offline workstation was not independently rerun during integration.

Executed in the integration Linux workspace:

- All 275 Python source tests passed, including after documentation/workflow integration.
- Both registry checkers passed: 29 unique native test names required.
- Eight portable C++ harnesses passed, covering objectives, PIE save protection, existing-save refusal, water-state rewind, physical adapter decisions, input bindings, review HUD and design-only combat refusal. Their mutation controls rejected the tested faults. API doubles are not Unreal physics, UHT or rendering evidence.
- Chapter polish checklist schema and relative Level 1 stat contract passed.
- Existing legacy contract checks are rerun separately; hosted browser smoke and workflow checks must pass on the integration PR before merge.

The Unreal workstation was offline on both available RDC connections. No new native executable, native screenshot or packaged game was produced in this integration session. The integration does not transfer an earlier exact-SHA native receipt to a new commit; it establishes unchanged native input bytes and reports that distinction.

## Remaining player-visible blockers

1. Default startup remains `/Engine/Maps/Entry`. The title review mode is explicitly selected; its New Game button dismisses the overlay, without creating a save, initializing a party or loading a production map.
2. The private title movie is intentionally absent from Git. A fresh clone uses the fallback. Playback over time, sound, mouse/gamepad and packaged media need native testing.
3. The last observed First Wake scene after Enter was nearly black, had six unbuilt-lighting warnings and mirrored review text. The warning also appeared over the title. Fix and capture these in Unreal before visual acceptance.
4. Complete continuous launch, physical sea landing and Splashdown are not accepted at this integration head. The separate #767/#773/#774/#775/#777/#779 physics/restore line is not folded in: its runtime differs and still needs a combined native replay.
5. Cross-session Continue, pawn position persistence and full party save integration remain unfinished. Existing saves must not be adopted or overwritten to bypass review protections.
6. Approved ship/character references still need finished in-engine asset integration, likeness/scale/lighting review and creator acceptance. Separate ship, character, harbor, sand and snow lookdev branches are not implicitly promoted by this baseline.

## Next implementation sequence

On the reconnected, idle Unreal workstation, use an isolated checkout of the merged revision and run the exact-head native verifier. Reconcile the separate splashdown/marker-restore fixes while preserving PIE F6 isolation; test save, advance, restore and reactivation with actual input. Then repair scene lighting and marker orientation, capture the native title-to-scene transition, and implement a real New Game/Continue flow with explicit slot ownership and party/location persistence. Keep the visual quality gate at the top of each playable review.
