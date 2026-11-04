# TSTSS Unreal — Hybrid Character Job/Class review contract

Status: REVIEW-ONLY / DRAFT / UNMERGED / NO GAMEPLAY AUTHORIZATION (2026-11-04).
Branch: review/ue58-hybrid-character-class-contract-20261104; stacked on native combat PR #685 at 813abdce5fd74ac32f685b9d6dbbee17d3863e7c.
Authority: [Notion: Magic Schools, Spell Trees & Job Classes](https://app.notion.com/p/3e0f5bad238b81a5acccdbf8bd4ef751); [Notion: Protagonist Roster](https://app.notion.com/p/3e0f5bad238b817b9ad4da4a2c0cb40f).

## Approved hybrid direction

- Each protagonist retains a permanent native profession/identity. Ender — Rift Scholar is currently the only approved named native profession; Ionia, Lyra, Reson and Aepex have open final class names.
- An explicitly unlocked primary combat job and optionally an explicitly unlocked secondary specialization may change, but never the native identity.
- Independent advancement axes: character level, job proficiency, magic-school mastery, weapon mastery and relationship development. Swapping a job cannot grant or erase experience, knowledge or mastery.
- Learned abilities are NOT automatically usable in every job. Primary-job access, explicitly permitted secondary-job access, and skill-by-skill off-job transfer have distinct gates. Exact job roster, secondary capacity, job XP accrual, off-job slot counts, passive transfers, spell lists and equipment rights remain open.
- Five Lights are story identities (Ender Spirit, Ionia Earth, Lyra Water, Reson Fire, Aepex Air), NOT forced magic schools or combat class selection. Preserve three active battle slots and recruitment order Ender → Ionia → Lyra → Reson → Aepex.
- No class change confers automatic spell knowledge, school mastery, equipment authorization, level gains, combat cues or relationship progression. Ender's staff is a fighting weapon, not a general spellcasting requirement.

## Implemented sources (review only)

| File | Function |
| --- | --- |
| Public/TSTSSJobClassSystem.h | UE 5.8 DataTable-ready class definition; DesignOnly default; separate volatile job state/skill policy |
| Private/TSTSSJobClassSystem.cpp | Guarded, transactional primary/secondary selection and learned-skill preview eligibility |
| Private/Tests/TSTSSJobClassSystemTests.cpp | TSTSS.Design.HybridCharacterJobs native automation test; denial and success cases |
| Tools/Verify-Unreal.ps1 | Requires the native job-class test in the strict automation evidence list |

Fixture IDs ReviewScholar, ReviewGuard, ReviewSeer and ReviewSigil are invented test data, NOT canonical or playable classes. ReviewSelectable means the job is allowed only in a disposable fixture; it does not mean CreatorApproved or runtime executable. No default DataTable, UPROPERTY SaveGame state, party change, UI widgets, spell rows, gameplay permission or active production actor is created. The class module never invokes the combat executor.

Epic's Unreal 5.8 [Data Driven Gameplay Elements](https://dev.epicgames.com/documentation/en-us/unreal-engine/data-driven-gameplay-elements-in-unreal-engine) documentation specifies FTableRowBase as the importer-supported DataTable row base.

## Design emphasis for later creator review (NOT final jobs)

| Character | Established role | Candidate emphasis |
| --- | --- | --- |
| Ender | Rift Scholar; analyst-controller | Pattern analysis, positional control and practical staff tools; highest starting MP and MAG |
| Ionia | captain-support | Tactical direction, positioning, navigation and ally protection; no invented spell school |
| Lyra | perceptive-support | Detection, stabilization and high-magic support; second MAG/MP, lowest HP |
| Reson | durable weapon specialist | Frontline defense and weapon techniques; loadout approvals separate |
| Aepex | technical specialist | Diagnostics, tactical devices and repair; Technomancy not automatically admitted |

Unsettled decisions: approved primary job names and starting assignments; native profession as an equippable job; job unlock/proficiency awards; exact secondary slot policy; learned Job Arts; permitted off-job slots; equipment rights; class selection UI and SaveGame migration.

## Verification gates

1. Run source checks on exact branch head: python unreal/Tools/check_unreal_test_inventory.py; python unreal/Tools/check_automation_registry.py; python unreal/Tools/test_automation_registry.py. These do not compile C++.
2. In an idle UE 5.8.4 workstation, use a clean isolated checkout to build Editor target and execute TSTSS.Design.HybridCharacterJobs, with full per-test JSON and unchanged git status.
3. Regression-run existing battle skill, data-reconciliation, party/recruitment and save automations. Native build and gameplay PASS cannot be inferred from source registration.
4. After explicit creator approval of actual job rows and ability permissions, add a disposable DataTable review, class UI, save migration and one playable three-active combat interaction, independently gated and reviewed.

The PR does NOT merge, release, activate Starbourne, authorize spells, alter art canon, approve provisional starting numeric stats, or modify any production gameplay or save asset.
