# Hybrid class-selection view model (Unreal review-only)

Date: 2026-11-04. Status: draft, not gameplay, not canonical job assignment.

## Context

This child is based on the independently native-verified strict config guard (#743), catalog integrity gate (#742), DataTable readback (#741), and core hybrid job contract (#740). The existing canonical combat executor, SaveGame model, three-active-party limit and First Wake recruitment remain unchanged.

## Implemented review projection

`FTSTSSJobClassSystem::TryBuildJobSelectionPreviewForReview` accepts the volatile in-memory protagonist loadout and a validated `UDataTable` catalog. It produces stable sorted rows with:
- Job ID and nonempty imported display name;
- whether that specific character explicitly unlocked the job;
- whether the existing transactional `TrySelectJobs` permits primary selection;
- whether the existing selected primary job permits each candidate in the secondary slot.

The projection uses **the same** underlying selection guard rather than reimplementing skill/identity permissions. When the current character identity, profession, level or catalog is invalid it returns failure **without** replacing prior preview output. Secondary preview is disabled until the current primary is valid and distinct; a job is never implicitly unlocked by being present in a table.

This is a plain C++/FText data view model, not a UMG widget, live game UI, equipment-grant, spell catalog or production authorization. `ReviewSelectable` is an opt-in fixture only; `DesignOnly` entries remain disabled even when unlocked.

## Dedicated test extension

Existing `TSTSS.Design.HybridJobTableReadback` covers: sorted disabled DesignOnly rows; explicit fixture review primary/secondary selectability; duplicate primary/secondary rejection; unknown-character refusal; malformed-row atomic failure; no learned-skill grant. It shares and preserves earlier DataTable import/strict-row-integrity proofs. Full 25 native test suite must pass from the exact clean committed source, not from docs.

## Next held gates

Creator approval for final four native profession names, job roster, job unlocks and job passives; test-only preview to a truly isolated UMG menu; explicit executable skill/equipment rights; save-version migration; full PIE/visual and real combat acceptance. None is authorized by this change.
