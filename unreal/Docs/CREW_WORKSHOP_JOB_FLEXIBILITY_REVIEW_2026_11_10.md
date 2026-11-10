# TSTSS — Crew roles, flexible jobs and workshop review slice

Status: DRAFT / PUBLIC-SAFE / UNMERGED / NO RUNTIME, ART OR SAVE AUTHORIZATION.
Source base: draft #742 at `dbd199609b91c11c633c8ce0a44ea7cd7d777528`.
Engine: Unreal 5.8.4. Do not implement forward development in Godot.

## Creator-approved rules respected

- **All five protagonists** retain native story/profession identity plus independently selectable, explicitly unlocked primary/secondary combat jobs. Existing `FTSTSSJobClassSystem::TrySelectJobs` remains the only reviewed job-selection guard; this change does not duplicate, weaken or bypass its fail-closed rules.
- Ender is Harmonic Resonance Engineer, harmonic-engine expert, Spirit-aligned, highest initial MAG/MP and second-lowest HP. The ship challenges his real expertise. Its anomalous instruments should be investigated, not diagnosed by fiat; apparent awareness remains ambiguous.
- Ionia remains Earth-aligned captain, owner and operational authority; her combat class is flexible.
- Lyra is Water-aligned, the second-strongest starting magic user with lowest HP, and a **default healer**, never a permanently locked healer. She may equip other admitted jobs.
- Reson is Fire-aligned **Armsmaster and ace pilot**; these are persistent aptitudes, not an exclusive warrior-job lock. Being an ace pilot does not transfer captaincy.
- Aepex is Air-aligned **gadgeteer/rogue**; upon later recruitment, he can design, construct and install upgrades for the Aureate Wake and party weapons/equipment. He complements Ender's harmonic analysis, and the captain retains vessel authority.
- These are public-safe roles only. Do not publish concealed modes, unlock sequences, private cinematic assets or spoilers.

## Source addition

`FTSTSSCrewWorkshopReview` is intentionally a **non-persistent, gameplay-adjacent model**. It introduces:
1. Immutable-by-call readout of Five Lights and personal aptitudes for the five known characters; every profile explicitly permits separately unlocked combat jobs.
2. Directly observed, Ender-initiated engine clues. Recording a clue asserts an observation occurred, **not** that the suggested explanation is true. No automatic ship powers or plot advancement.
3. A transactional Aepex workshop prototype: Aepex must be recruited; the safe workshop and exact upgrade are explicitly available; positive resources must be available; vessel upgrades need Ionia's authorization; harmonic-dependent work needs an Ender observation. Successful review transaction deducts shadow materials and records an upgrade receipt without creating real equipment or vessel capabilities.
4. Fail-closed denials for absent characters, unobserved clues, locked/DesignOnly upgrades, malformed or duplicated upgrade identities, invalid targets, insufficient materials, missing captain approval, missing harmonic evidence, and repeat installation.

Existing `TSTSS.Design.HybridCharacterJobs` automation covers all-five class switching and reviews these workshop boundaries. The new model is not Blueprint-exposed, has no runtime actor, does not edit `SaveGame`, DataTables, ship transforms, weapons, inventory or combat systems. Fixture `ReviewSelectable` is **not** creator approval or permission for production crafting.

## Next integration gates

- Source review and actual UE 5.8.4 C++ build/UHT and named native automation, plus all combat/job/save/roster regressions on the exact same SHA.
- Separate creator approval of final class catalog, default recommended starting jobs, crafting recipes/materials, upgrade effects, installation interactions and class menu UX.
- Wire a **single playable ordinary gear upgrade** to a safe workshop interaction after Aepex's recruitment, with inventory transaction, save/load, accessibility and denial tests. Use Ender + Aepex collaboration for an observation-dependent prototype after that.
- Implement the Ionia/Ender initial engine-room investigation as a separate story/cinematic slice, preserving First Wake recruitment chronology and rejecting invented readings as facts.
- Advanced crew-and-ship resonance and concealed form implementation remain restricted, separately gated and outside public source. No main merge or release.

Verification boundary: static/source-level review is not native Win64 or playable proof. Remote Unreal device availability must be independently checked before claiming execution.

## Creator canon correction — November 10, 2026

Ender's canonical native profession is now **Harmonic Resonance Engineer**, superseding the previously authored Rift Scholar identity. He retains four innate magical specialties **Aether, Resonance/Harmonic, Correspondence, and Lumen**, separate from his **Spirit** Five Lights affinity. **Rift Scholar** remains in the setting as the unnamed **Wise Woman's NPC profession**, not an explicitly unlocked or automatically playable class. Her exact magic, plot beats and first encounter remain open.

The guarded **FTSTSSJobClassSystem** native-profession contract and fixtures were revised as a follow-on source candidate. All five protagonists still retain their separately unlocked, swappable primary/secondary combat jobs. This is a source-level narrative identity correction, not an actual implemented Wise Woman actor, new spell or class-menu feature. Fresh same-head Unreal build and automation remain required.

## Creator-selected Ender vertical-slice primary class — November 10, 2026

The creator has selected **Resonator** for Ender's equipped primary combat job in the vertical slice. This is distinct from his fixed trade **Harmonic Resonance Engineer** and from the Wise Woman NPC's Rift Scholar profession.

The class includes a **complete eligible curriculum scope** across **Resonance/Harmonic, Correspondence, Psion/Psychic, and Synergy/combination** magic. Historical catalog shorthand ("Resonance + Technomancy") is superseded for this vertical-slice class. His four **innate** magic affinities remain **Aether, Resonance/Harmonic, Correspondence, Lumen**. Spirit remains his Five Lights story affiliation.

**Source slice:** `FTSTSSJobDefinitionRow::CurriculumFamilies` supplies authored curriculum family metadata without granting spells, school mastery or combat authority. The transient in-memory `TSTSS.Design.HybridJobTableReadback` fixture now checks all four Resonator families, rejects DesignOnly class selection even if nominally unlocked, and rejects unlearned Psychic spell use. It does not auto-equip a production default or create saved DataTables/Content assets.

**Next actual gameplay gates:** add creator-approved starting skills and explicit primary job assignment, executable class permission row, three-active combat and stable save/load; test C++/UHT in Unreal 5.8.4 at the current exact head. No silent job-lock, granted Psion mastery, global synergy permission, Shine changes, production merge or hidden vessel gate changes.

Authority: [Notion Resonator vertical-slice class contract](https://app.notion.com/p/414f5bad238b8114a732c153578fd190).

## Source-locked Resonator DataTable and selection boundary — 2026-11-10

Added `unreal/DataSource/Jobs/Resonator.vertical_slice.review.json` as the
authoring source for the creator-selected Ender primary combat job. It contains
exactly four curriculum families without starting abilities or innate-affinity
changes. The existing native `TSTSS.Design.HybridJobTableReadback` now loads
the exact on-disk JSON through the Unreal DataTable importer, checks a successful
**review-only** selection when explicitly unlocked, and proves denied paths for
missing unlock, unlearned Psychic ability, and revoked job approval. A Python
test is separately wired into engine-free GitHub CI and can detect JSON drift.

`ReviewSelectable` is not executable skill authorization. This does not add a
production DataTable Content asset, initialize the live character roster, create
a class menu or persist jobs/learned skills. The next gate is a fresh native UE
5.8.4 Editor build and exact-head automation, then explicitly authorized slice
initialization, combat permission and save/load with real rendered gameplay.
