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

## 2026-11-01 — Regression consolidation from other active agent branches

Added existing read-only-authored QA test source from independent draft [#671](https://github.com/ndrorchestration/ToSailtheStarrySky-jrpg/pull/671) at \`3dc716ddcce000373a79d504cf476c135b5916fa\`, and [#672](https://github.com/ndrorchestration/ToSailtheStarrySky-jrpg/pull/672) at \`b4dad1a01a696b910421f88b6ac308ffd19b7c40\`. These are copied tests (not merged PRs), and retain original noncanonical fixtures.

- \`TSTSS.CombatIntegration.DataContractCannotAutoAuthorize\`: verifies that level-derived proposed actions do not gain shipping approval or the separate learned/mastery/admission gate, and that failure preserves existing state.
- \`TSTSS.CombatIntegration.ProgressiveRecruitmentPartySize\`: verifies solo Ender → duo Ender/Ionia → trio Ender/Ionia/Lyra without phantom recruits or a fourth active member.
- Strengthened \`TSTSS.CombatData.NonExecutableSkillReconciliation\`: calls the actual guarded spell executor with a converted \`DesignOnly\` row, including an artificially learned and mastered review actor, and confirms action rejection plus unchanged outputs.

All three remain **native automation test source**, not a claim of native execution. \`Verify-Unreal.ps1\` requires their named results alongside the rest of the test inventory.

## 2026-11-01 — Bounded integer counter rollover hardening

The existing deterministic `FTSTSSCombatTurns::TryAction` implementation incremented signed `int32` `AcceptedActions` and `Round` without checking `MAX_int32`; an extremely long or deliberately restored malformed encounter state could otherwise overflow signed counters. A reversible, isolated change denies any action at maximum accepted-action count, and denies only those maximum-round actions that would advance the round. It preserves the output argument on rejection and allows max-round actions that do not wrap. The existing native `TSTSS.Combat.TurnOrderAndAtomicity` suite now includes positive no-wrap and negative max-round/max-action tests, avoiding new test inventory names. No gameplay tuning, save schema or character progression data is changed. **These are native test declarations, not evidence they ran in Unreal.**

## 2026-11-01 — Generic healing cannot resurrect knocked-out targets

`UTSTSSCombatRules::TryApplyAction` previously rejected damage targeting HP=0 but accepted ordinary healing on HP=0, potentially granting an unapproved resurrection through direct callers below `FTSTSSBattleSkillSystem`. The existing higher-level skill executor already denied such healing. This isolated core correction makes <b>all generic combat actions reject HP=0 targets</b> (including healing) while preserving outputs on rejection. The existing `TSTSS.Combat.RejectsInvalidActionsWithoutMutation` native test now checks the zero-HP heal denial and output/input preservation. This does not remove or implement an explicitly authored future resurrection mechanic; any such mechanic needs a separate approval and typed resolver. Unreal native execution remains unverified until exact-head UE 5.8.4 compilation and Editor tests.

## 2026-11-01 — Strict action-category/target enum validation

The authoring `ValidateActions` path previously did not reject cast/deserialized category/target values outside its declared enum schema. In `TryBuildAbilityData`, its target switch has no default, so an invalid target could silently retain an initialized default. `ETSTSSDataIssue::InvalidActionCategory` and `InvalidActionTarget` now cause source and shipping validation to fail rather than reinterpreting malformed input. Existing `TSTSS.CombatData.ActionDefinitions` test adds invalid category and target cases, including a catalog bridge rejection that preserves existing outputs. This remains a review-only validator and does not authorize gameplay magic, invent content, or claim native UE compilation.
