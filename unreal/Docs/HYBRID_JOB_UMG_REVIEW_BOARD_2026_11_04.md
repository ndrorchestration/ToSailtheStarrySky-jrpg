# Unreal UMG hybrid-job review board — source-only pilot

Date: 2026-11-04. Status: DRAFT / NONCANONICAL / REVIEW ONLY / NOT PLAYABLE.

## Scope and authority

This is a child of draft #744 at `72d81bdf6aa6e0d8b8e1c9f5b0404d08e4b0f85b`, inheriting the exact verified job-catalog gate (#742) and guarded native verifier (#743). It changes no map, production actor, SaveGame schema, spell/weapon authorization, item inventory, class unlock progression or approved character lore.

The parent class system supplies a **deterministic validated view model**. A new `UTSTSSJobSelectionReviewWidget : UUserWidget` renders it as real UMG `UWidgetTree`, `UVerticalBox` and `UTextBlock` objects, without saved asset creation, UI routing or click actions.

The screen carries an explicit **JOB SELECTION - DESIGN REVIEW ONLY / NO GAMEPLAY** heading. Each row shows its noncanonical fixture display name and an explicit non-color-only status:
- `LOCKED: NOT UNLOCKED` for jobs not explicitly unlocked by this character.
- `LOCKED: NOT ADMITTED` for DesignOnly or otherwise prohibited jobs; their UMG text widget is disabled.
- `PRIMARY REVIEW` or `PRIMARY UNAVAILABLE`; `SECONDARY REVIEW` or `SECONDARY UNAVAILABLE` when selection is permitted only by existing transactional class guards.

The UMG tree is **passive**. It intentionally contains no buttons, selection events, gameplay callsites or battle-executor hooks. Rebuilding the tree validates all row identities and preserves the previous root on validation failure. The class may be instantiated by future isolated Editor review code but is NOT added to a level, viewport, UserWidget Blueprint or playable route here. Actual visible native GPU screenshot and PIE navigation have NOT been performed; verification of widget construction is not visual acceptance.

## Tests and provenance

The existing native `TSTSS.Design.HybridJobTableReadback` test now constructs a genuine transient widget tree from DesignOnly fixture rows, checks exact child types, explicit lock text and disabled `UTextBlock::GetIsEnabled()` flags; then tests primary/secondary review labels on explicitly unlocked temporary fixture rows. It also tests malformed/duplicate-row rejection without replacing the accepted UMG tree. This extends, but does not alter, the 25-test inventory.

Run `unreal/Tools/Verify-Unreal-ConfigGuard.ps1` from an exact pinned, clean, isolated UE 5.8.4 Windows checkout. The wrapper preserves tracked `.ini` hashes while the original strict verifier performs a native Editor build and all 25 required native tests. Source-only checks must not be conflated with native execution.

## Further gates

1. Complete native C++/UHT build and per-test JSON acceptance from this exact commit.
2. Create a disposable Editor review level/viewport only after explicit visual review needs and resource/watchdog gates are met. Do not promote blockout visuals or fixture jobs.
3. Request creator approval for the final four native profession names, actual job roster, spells and equipment rights, progression and saved data.
4. Integrate an actual interactive menu, player input, SaveGame and three-active combat only through separate guarded implementation and evidence.

Starbourne remains closed; production content, author-approved art and protected main remain untouched.
