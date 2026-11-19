# Aetherwake — Hybrid Job and Character-Identity Contract v0.1

**Status:** IMPLEMENTED DESIGN CONTRACT / NOT RUNTIME-INTEGRATED / NO JOB CATALOG ADMITTED

**Source authority:** Aetherwake creator decision, 2026-10-07; Notion Magic Codex, Ender Innate Spell Trees, Magic Schools/Spell Trees/Job Classes, Cross-School Magic & Combination Arts, and Ender's Character Dossier. The repo implementation is authoritative for executable behavior.

## Approved principles

- A character retains permanent identity regardless of equipped combat role. Ender's formal native profession is **Rift Scholar** (not "Rift Scholar + Dreamwright").
- Primary combat job and secondary specialization are independently swappable once **explicitly admitted**.
- Character level, school mastery, learned spells, job proficiency, future weapon proficiency, and party relationship progress are independent axes. No job change resets any of these.
- Ender's four established innate magical affinities are Aether, Resonance/Harmonic, Correspondence, and Lumen. They do not confer automatic mastery or spells. Ender may potentially study all recognized ordinary schools, subject to eligibility; Dreaming and Commons/Mycelial access are exceptional, not freely unlocked jobs or schools.
- Ender's starting **fighting staff** is a physical two-ended weapon; magic is **not** dependent on wielding it. Staff mechanics and magic progression must not be collapsed into the job contract.
- Ender's personal strengths for narrative/animation direction: observation, discernment, cooperation, creative problem-solving, optimism, insight, originality, humor, strong heart. No numerical buffs or gameplay status are inferred by this contract.
- Staff fighting direction: efficient grounded strikes, practical reversals and thrusts, flowing footwork when useful; research Okinawan bo, Chinese gunshu, and Indian silambam as movement references without claiming unverified technique fidelity.
- Visual direction: realistic cinematic portraits, expressive Star Ocean-inspired 2.5D gameplay sprites with more grounded proportions/material detail; character-specific animation should grow with mastery.

## Bounded implementation

modules/job-progression.js is a **pure UMD design/evaluation module**:
- createProfile binds the unchangeable nativeJob to modules/character-canon.js; other characters' unset native jobs remain null rather than invented.
- The two equipped slots start empty; only explicitly provided **admitted** registry entries with slot-specific permissions may be selected. Candidate/unknown job IDs fail closed.
- The same job cannot occupy both slots, and a secondary cannot be equipped without a primary.
- Job ranks 1–5 are stored separately and advance by one validated transaction only. This model does **not** grant XP, teacher access, job unlocks or live proficiency.
- Technique checks distinguish native/character ownership, job-bound use, and **explicitly allowed cross-job transfer**. Learning an ability does not imply unconditional cross-job use. No transfer to an unlisted target.
- Magic/weapon/party techniques are deliberately **not authorized** by the job evaluator; their own domains must validate them.
- All outputs remain DESIGN_ONLY_NOT_RUNTIME_AUTHORIZED (and technique checks explicitly return executable:false).

No real job catalog, cross-job permissions, job skill definitions, acquisition requirements, resource costs, stat growth, secondary weapon permissions, or mastered skill slots have been frozen. The test registry uses **test-* fixture IDs only**.

## Compatibility / non-authority

- Do not load this new module into index.html, combat, roster/session persistence, equipment, saves, or release packaging yet.
- Do not interpret the design-only evaluator as a combat command or job-selector UI.
- Existing character-magic-profile, magic-study, magic-spell-access, character canon, and route tests remain unchanged.
- docs/MAGIC_SYSTEM.md and existing Notion canon still govern school definitions; this file does not overwrite any magic taxonomy or resource ontology.
- Preserve Arete vs Aether vs Echoes distinction and avoid generic one-pool spellcasting.
- Job proficiencies and skill transfer need explicit source-owned admission and player usability balancing before runtime wiring.

## Next reversible advancement gates

1. Creator approval of **specific job catalog entries**, candidate availability, and inheritance capacity (number/type of off-job abilities).
2. Typed job and ability registries with ownership, admission, equipment permissions, skill prerequisites, and relevant source links.
3. Independent prototype of job unlock/experience, cross-job eligibility, and visual equipment variants.
4. Player-facing selection preview behind opt-in flag, with input/controller/accessibility contract, no existing save mutation.
5. Exact-head full route/combat tests, save migration verification, and human playable feedback before default integration.

**Verification:** node tests/job-progression-contract.test.js; no runtime admission or visual/acceptance PASS is implied.
