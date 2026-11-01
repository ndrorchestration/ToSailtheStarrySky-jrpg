# Unreal spell, magic, skill and weapon-technique vertical slice — draft

**Branch:** \`feat/unreal-combat-magic-weapon-techniques-slice\` (stacked on draft UE foundation PR #608, source baseline \`4b85f0d1d7b8870f09d72420871abf4553e3dfbf\`).
**Status:** implementation candidate; not merged or release authorized. Native Unreal build, Editor automation, playable capture, and artistic review are separate gates.

## Delivered in this bounded slice

- \`FTSTSSBattleSkillRow\` is a UDataTable-ready contract for explicit spell / weapon technique / job art identity, targeting, resource, power, cooldown, mastery, equipped weapon, VFX cue and animation cue.
- \`FTSTSSBattleSkillSystem\` executes admitted direct-damage/healing skills using the **existing** native faction/turn/transaction logic. Failures never alter combat state, cooldown state or emitted cues.
- Caster mastery and learned skill are *independent* checks. A character's narrative Light, plot resonance, innate affinity or the 260 design-only magic seeds never grant spells automatically.
- Weapon techniques demand explicit equipped weapon class and learned skill. Admission defaults to \`DesignOnly\`, including imported table rows.
- A successful action outputs presentation cue **IDs**; it does not claim authored Niagara emitters, animations, sound, materials, character rigging, in-game UI or playable integration.
- Editor automation fixture covers denied/unadmitted magic, learned + mastered spell, self-healing, missing weapon, action atomicity, and per-actor cooldown/recast.

## Admission boundary / canon

The old magic design registry distinguishes **11 elemental schools** and **15 non-elemental domains** (260 design seeds). None is auto-executable by presence in the catalog. Creator/authoring approval, cross-school prerequisites, progression, resource balance, status effects, field reactions and executable spell definitions must be reviewed explicitly before admitting further spells. Five Lights are character story affinities only; the currently established *innate magical* affinities are Ender's Aether, Resonance, Correspondence and Lumen, **without automatic rank or learned spells**. Do not assign Lyra/Ionia/Reson/Aepex new school mastery from their Light.

## Current mechanical limits (intentional fail-closed scope)

| Capability | State |
| --- | --- |
| Direct damage and healing with legal self/ally/enemy target | Review implementation |
| Resource costs, explicit learned skills and school rank | Review implementation |
| Weapon-class gate, actor-local cooldown, rejected-action atomicity | Review implementation |
| VFX / montage cue metadata | IDs only; no spawn or playback |
| Direct elemental visuals, environmental reactions, stuns, buffs, status, barriers, summons, AoE, multi-hit, multi-target, item effects | Not implemented; do not admit via this resolver |
| Cross-mastery rank + parent-school dependencies, synthesis, combination/triple arts, aiming, cast interruption, equipment stat formulas | Not implemented; keep design-only |
| Battle UI, character rigs/montages, save-version migration, production gameplay integration | Not implemented |
| All 260 historical design seeds usable in Unreal | **No** — registry remains design-only |

A \`CooldownActorTurns\` of 1 blocks the next action turn belonging to that actor; the actor must take a different admitted action before reusing the skill. **Every accepted turn must pass through this executor to keep actor-local cooldown counters accurate.** Do not wire it to a live battle or persistence until the one-authority turn route and versioned save schema are established. The native combat primitive underneath still allows generic heal-at-zero, so this new executor explicitly refuses healing knocked-out targets; resurrection needs a separately authored effect.

## Next reversible native verification

1. Open a **clean isolated checkout** of this branch in Unreal Engine 5.8.4 with matching VS game C++ toolchain.
2. Compile the Editor target and run \`Automation RunTests TSTSS.Combat.MagicAndWeaponTechniques\` plus \`TSTSS.Combat.AbilityAuthorization\` with full logs. These are proposed commands, **not passed results**.
3. Create a \`DataTable\` using \`FTSTSSBattleSkillRow\` with a single clearly labeled noncanonical review spell and an equally labeled staff technique; test default DesignOnly denial, then explicitly set ReviewExecutable for sandbox use only.
4. Capture three frames in isolated test level: cast wind-up, effect delivery, return to idle. Use placeholder emitters until approved VFX/rigs exist.
5. Measure equipment change, missing-masteries, exhausted MP, wrong target, mid-turn reentry, cooldown, knockout, victory, and save/reload across separate tests. Do not merge before passing native test evidence.

## Future production architecture

Follow a sequence of **ability registry → legal target preview → deterministic effect resolver → field state reactions → animation/VFX/audio cue routing → UI → save migration → character/monster integration → cinematic polish**. Assign spell ownership via learned-school mastery rather than jobs, while distinct weapon proficiency and Job Arts remain separately gated. Render specs and effects at three quality tiers (combat readability, boss cinematic, full cutscene) using the same canonical silhouettes and elemental semantics.

## Full 260-seed design catalog export

Run \`node unreal/Tools/export_magic_design_catalog.cjs --write\` then \`--check\` to obtain a deterministic \`unreal/DesignCatalog/ALL_MAGIC_SEEDS_DESIGN_ONLY.json\` manifest from the preserved source modules. The engine-free source-inventory workflow now checks this and uploads the generated manifest as a review artifact. It preserves all source IDs, ranks, domain proposal statuses, role/intent strings and explicit spell-level cross-mastery prerequisites. It deliberately leaves effect, targeting, numeric MP cost, VFX and animation assets **null** because those mechanics do not exist for all 260 seeds. Do not import it as an executable Unreal DataTable or treat an export PASS as editor/build/gameplay proof.
