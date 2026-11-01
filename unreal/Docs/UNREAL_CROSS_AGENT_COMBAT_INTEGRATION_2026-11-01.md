# Cross-agent Unreal combat integration review — November 1, 2026

**Stack:** foundation #608 → magic/weapon permission executor #662 → initiative/component #666 → **this draft**, with the additive validator/data contract copied from independent Claude draft #665 at head \`a0be01ed280279e3a650d4c8f5d9f051ef6f4a00\`. Copying source into this isolated review branch is **not** merging #665 or accepting its fixture values into main.

## Integration mechanics

- Preserve the original #665 \`FTSTSSCombatData\` validators for five protagonists, Five Lights as narrative tags, Level 1 HP/MP/MAG relative ordering, user-specified level-gated learned-set calculation, and source provenance.
- Preserve #662 \`FTSTSSBattleSkillSystem\` execution: requires explicit learned, mastery, equipment, admission and actor-local cooldown checks; prohibits accidental spells from narrative affinity and data export.
- Preserve #666 \`UTSS_CombatTurnManager\`: only one turn executor, explicit 1–3 active party selection, deterministic speed initiative, legally executed skill rows.
- **New guarded bridge** \`FTSTSSCombatSkillReconciliation::TryPrepareDesignOnly\` converts only compatible Spell/WeaponTechnique authoring metadata (identity/power/cost/healing/target) into \`FTSTSSBattleSkillRow\` with permanent \`DesignOnly\` admission at this stage. Even a row marked \`CreatorApproved\` by the #665 schema is never automatically executable. It does **not** claim per-character learned/mastery authorization, infer school from Five Lights, infer equipped weapon, or emit fabricated FX assets. Unknown/generic categories and malformed input fail atomically.
- All new/ported native automation test declarations are required in \`Verify-Unreal.ps1\`. Source-only CI checks registration and legacy smoke; only native UE 5.8.4 verifies C++ and editor reflection.

## Explicit unresolved contract differences

1. **Party count:** #665 \`ValidateActiveParty\` requires EXACTLY THREE, while #666 supports 1–3 to handle recruitment (Ender → Ionia → Lyra). Do not change the former silently; treat it as a later fully populated selection gate, and keep early encounters 1–3 pending authored chapter-integration review.
2. **Action ownership and school:** #665 \`Learners + UnlockLevel\` is not enough to satisfy #662's learned school, mastery rank, equipped-weapon requirement, or gameplay admission.
3. **Stats and economy:** #665 \`StartMagic\` and \`StartMaxMP\` are not wired into #666's generic Combatant Resource/Attack, and no creator-approved numeric baselines exist. Do not equate the resource pool to canonical MP or port the legacy JS HP values.
4. **Category map:** #665 Attack/Support are not automatically the JobArt category in #662; require explicit authored classification or separate resolvers.
5. **Provenance:** \`CreatorApproved\` (data ownership/provenance) and \`ReviewExecutable\` (isolated mechanic opt-in) remain distinct gates, neither sufficient alone for shipping.

## Required verification

1. Read exact-source branch SHA, run both hosted Unreal source preflight/inventory plus generic smoke; report FAIL if any regression, and no false native pass.
2. Isolated UE 5.8.4 Win64 Editor compile + UnrealHeaderTool + exact report of all \`TSTSS.Combat*\` tests, including \`TSTSS.CombatData.NonExecutableSkillReconciliation\`.
3. Import DataTables using each separate row type; verify Blueprint shapes and absence of automatic spell learning.
4. Independently test underfunded/wrong target, weapon swapping, status/knockout, initiative ties, 1-/2-/3-member recruitment boundaries, reserve save continuity and terminal victory/defeat.
5. Real renderer VFX/montage and cinematic captures are outside this source-only slice. Do not merge or release until independently accepted.
