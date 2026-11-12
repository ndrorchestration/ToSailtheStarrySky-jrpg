# First Wake V5 travel control discoverability — review-only source handoff

**Date:** 2026-11-12. **Scope:** An isolated review child of [draft #816](https://github.com/ndrorchestration/ToSailtheStarrySky-jrpg/pull/816), beginning at `cb092b71615b9d7608660f164d1c7611c693e44a`. This does not modify approved assets, production maps, scene ordering, story gate authority, SaveGame formats, party availability, or protected `main`.

## Implemented

- Existing, non-shipping First Wake Canvas HUD identifies **K: gated scene** (compact HUD: **K scene**) alongside WASD, E, J, F6, F9, and F7. The existing live objective and three inspection lamps are retained.
- **J** now presents the actual eligible destination package's short name after checking a standalone PIE/Editor Game World in the review package namespace; for V5, VS02, VS03, VS04, and VS05 it explicitly reports K locked when the current beat fails the existing gate. J performs no level travel or story mutation.
- **K** refusal now includes the current objective, making inspection, physical-water and reserve gate denials clearer to a player. It still calls the unchanged `QueueShore` authority before `OpenLevel` and cannot bypass physical flotation.
- Added a targeted source regression to `test_first_wake_v5_ship_bridge.py` for HUD control discoverability, namespace/network checks, route gate checks, and lack of story/SaveGame side effects in the J cue.

## Verification boundaries

Changes are **source-authored and unmerged**. Neontic's Remote Desktop Commander device was **offline at the time of this pass**. No UE5.8.4 UHT/UBT rebuild, native automation, PIE/standalone player test, audio check, screenshot, performance check, or visual approval has been performed for this child revision. Do not inherit #816's native PASS evidence as if it applies to this newer C++ edit.

**Next native acceptance:** with Neontic online, check exact child HEAD and host resource admission, compile Win64 Editor, run the original `TSTSS.FirstWake.ReviewObjectivesAreReadOnly` and `TSTSS.FirstWake.ReviewDockReturnBoundaries` tests, run source-side HUD compiled harness, then manually verify New Game → V5 E milestones → J/K → ship interior → J/K → sky, including denied K before engineering completion, correct no-early-launch state, safe footing, and live screenshots. The physical-water SeaContact/FlotationConfirmed two-second gate still requires native observation. No gameplay/cinematic or canon promotion until tested.

**Story constraints:** Only Ender and Ionia are available in the pre-splashdown segment. Lyra joins only after her later story recruitment. Reson and Aepex are unavailable in this slice. Starbourne remains fail-closed.
