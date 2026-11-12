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

## 2026-11-12 continuation: safe intermediate footing and native-inventory reconciliation

- **Intermediate gameplay safety:** the existing review-only, non-shipping grounded-pawn rescue whitelist now includes `VS02_AureateInteriors` (Aureate Wake deck) and `VS05_DenithFuelShanty` (fuel-shanty platform). The five-point footing check, supported anchor, falling condition, 400 cm drop threshold, bounded teleport safety and no-story-mutation boundary remain unchanged. `VS03_FirstWakeSky` and `VS04_SplashdownSea` remain excluded; the physical 2.0-second flotation gate is untouched.
- **Native test strengthened (not executed at this new HEAD):** `TSTSS.FirstWake.ReviewDockReturnBoundaries` now contains two additional acceptance cases for the ship/shanty review maps, plus its existing sky/sea negative cases. `test_first_wake_v5_ship_bridge.py` checks the whitelist, negative exclusions and read-only J/K feedback.
- **Verification blocker repaired:** the registered `TSTSS.FirstWake.ReviewDockReturnBoundaries` test was missing from the current `Verify-Unreal.ps1` mandatory list. The live registry and its exact-count report validator, synthetic PowerShell fixtures, read-only readiness probe, and separate shore authorizer now require **36 distinct native names**. Historical integration manifest records that originally captured 35 names are preserved as *historical snapshots*, not evidence that 35 is today's full suite.
- **Legacy source assertion repaired:** consumed E-marker collision tests now validate the actual `IsAuthorizedReviewMilestoneWorld` helper, including editor-only scope, standalone PIE/Game, named review worlds, non-network mode, and rejection of unrelated V3/V4 worlds; the prior PIE-only expectation was stale after the bridge update.

### Current GitHub evidence before documentation-only follow-up

At code HEAD `8551c00925a50339f4b4b05f532b67ae7e6a7f41`:
- [Unreal source preflight — PASS](https://github.com/ndrorchestration/ToSailtheStarrySky-jrpg/actions/runs/43295682106): all **558** discovered Python source/contract tests passed; native registry preflight verified **36 names in 24 files**.
- [Unreal source inventory (engine-free) — PASS](https://github.com/ndrorchestration/ToSailtheStarrySky-jrpg/actions/runs/43295682051).
- [First Wake atmosphere source QA — PASS](https://github.com/ndrorchestration/ToSailtheStarrySky-jrpg/actions/runs/43295681960).
- [Aetherwake smoke workflow](https://github.com/ndrorchestration/ToSailtheStarrySky-jrpg/actions/runs/43295682350): check its result independently; do not assume success from source preflight.

**Authority: SOURCE VERIFIED ONLY for this child.** The 36-native-test inventory was *identified and checked for registration*, not executed in UE5.8.4 at the new source head. A prior two-native-test pass belongs to parent #816, not this branch. Remote device Neontic was offline for this session; full V5→ship→sky traversal, playability, final asset looks, audio, D3D performance/captures and physical flotation remain unverified. Keep this PR draft/unmerged.

### Native execution queue once Neontic reconnects

1. Bind source to exact new HEAD; verify idle Editor/UBT, 5 GiB+ build RAM, 6.5 GiB+ graphical RAM, 14 GiB+ disk and clean checkout.
2. UHT/UBT Win64 Editor rebuild and required native automation inventory; retain exact-head artifacts and failed receipts.
3. Play standalone New Game → V5 seven E milestones → J/K ship → J/K sky; assert engineering-mask continuity and no early launch; deliberately walk off the dock, ship deck and shanty platform to check bounded recovery without water authority.
4. Test physical splashdown using actual UE water/hull observation, at least 2.0 seconds of directly observed stable flotation; deny premature K to the fuel shanty and premature Lyra recruiting.
5. Capture D3D screenshots, assess actual readability, terrain/map boundaries, camera, materials, sound/music rights, and performance before any creator approval.
