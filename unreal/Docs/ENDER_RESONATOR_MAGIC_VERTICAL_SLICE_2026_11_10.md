# TSTSS — Ender Resonator magic: vertical-slice source implementation

**2026-11-10 | ISOLATED DEVELOPMENT CANDIDATE | NO MAIN MERGE | NO ART OR SHIPPING APPROVAL**

Authoring checkout: `feat/ue58-ender-magic-slice-20261110`.
Primary implementation: Unreal Engine **5.8.4**, not historical Godot.
This document must be read as an evidence boundary, not a claim that the spells
are already castable in the current First Wake playable map.

## Creator identity and admission gates

Ender's permanent profession is **Harmonic Resonance Engineer**. His selected
vertical-slice **combat job** is **Resonator**. Its full eligible curricula:
Resonance/Harmonic, Correspondence, Psychic/Psion and Synergy/Combination.
His innate magical specialties are separately Aether, Resonance/Harmonic,
Correspondence and Lumen. Five Lights **Spirit** is a narrative affiliation,
not an automatic spell unlock or synonym for the Resonator job.

The design rows in `DataSource/Magic/EnderResonator.vertical_slice.review.json`
all use `ReviewExecutable` **only for an explicitly learned, mastered, equipped,
isolated combat review**. This is intentionally NOT `CreatorApproved` for shipping,
not a default learned set, and not a blanket new class mastery grant. New numerical
power, MP and cooldown values are engineering proposals, pending creator balancing.
The existing `FTSTSSBattleSkillSystem::TryUseDataTable` must authorize a combat
transaction; learning and independent school mastery remain necessary. Psychic
curriculum eligibility **does not** grant Psychic mastery. Synergies require both
named school mastery gates. The current combat executor supports damage/healing,
not arbitrarily invented buffs, teleports, statuses, fields or world interaction.

## Authored review spell suite

| Spell | Family | Review action | 3D visual silhouette | Gate |
|---|---|---|---|---|
| Resonant Pulse | Resonance | enemy damage | expanding blue concentric harmonic rings | Resonance 1 |
| Tuning Lance | Resonance | enemy damage | traveling cyan spear core and harmonic rings | Resonance 2 |
| Echo Mend | Resonance | living ally heal | green restoring concentric pulse | Resonance 1 |
| Correspondence Thread | Correspondence | enemy damage | violet threaded orbit and target linkage | Correspondence 1 |
| Lattice Break | Correspondence | enemy damage | purple fractured impact rings | Correspondence 2 |
| Mind Ripple | Psychic/Psion | enemy damage | amber twisting psychic motes and ripple | Psychic 1, explicitly learned |
| Focus Harmonic | Psychic/Psion | self heal | golden compact focus orbit | Psychic 1, explicitly learned |
| Concordance Burst | Synergy | enemy damage | wide jade/cyan harmonic discharge | Resonance 2 + Correspondence 1 |
| Thought Chord | Synergy | enemy damage | rose-gold harmonic/psychic cross-phase burst | Resonance 2 + Psychic 1 |

Spell names, color coding and effect styles are review propositions, not final lore.
No unearned Aether or Lumen combat kit, Spirit-only school, advanced vessel feat,
ship unlock, Starbourne mechanic, or Wise Woman/Rift Scholar magic is implied.

## Runtime source and rendering

- `ATSTSSResonatorVfxActor`: genuine Unreal 3D actor, using instanced sphere
  meshes for 3 spatial rings (72 points), 32 orbiting motes, 1 energetic core,
  animated transforms and a colored local point light. Nine distinct parameterized
  spell-style mappings. Transient, bounded 2.15–2.45-second nonloop casts.
- `M_ResonatorGlow`: Unreal Editor Python asset-builder defines an additive,
  emissive shader with `Tint`/`Glow` parameters. BasicShapeMaterial is the
  degraded visual fallback until the shader is imported.
- `DT_EnderResonatorReview`: Editor generator imports the source-locked JSON as
  `FTSTSSBattleSkillRow` DataTable. No existing assets are overwritten.
- `L_EnderResonatorCueReview`: isolated **3 by 3** in-game PIE preview stage,
  one continuously looped VFX actor per candidate. It does not cast spells,
  spend MP, recruit characters, mutate savegames or modify First Wake levels.
- `SpawnFromAcceptedCue` is the C++ **post-success integration point**. The
  existing authorized combat action returns `FTSTSSBattleSkillCue` only on
  success. The renderer checks the exact Ender actor/skill/VFX mapping and
  never mutates combat state. A future runtime battle scene must invoke this
  point **only after** a true `TryUseDataTable` success with exact row and
  learned/mastered state. No current live caller is claimed.

### Build/import in the isolated checkout

1. Ensure no Unreal Editor, UnrealEditor-Cmd, Live Coding or another agent build
   is using the workstation. Require at least 5 GiB free RAM and 14 GiB free disk
   before running the repository's native verifier.
2. Commit the source candidate before `Verify-Unreal.ps1` to bind exact-head
   build and automation receipts.
3. Native compile: `powershell -File unreal/Tools/Verify-Unreal.ps1 -EngineRoot "C:\Program Files\Epic Games\UE_5.8" -ExpectedHead <full-40-char-SHA>`.
4. Only after a clean native build, run Unreal Editor Python script:
   `unreal/Tools/build_ender_resonator_preview.py` with the isolated
   `unreal/ToSailTheStarrySky.uproject`. Validate the DataTable importer, shader
   compile, review level save, native preview PIE and nine per-cue rendered captures.
5. Run `TSTSS.Magic.ResonatorCueContract`, existing
   `TSTSS.Combat.MagicAndWeaponTechniques`, full native automation, dedicated
   GPU frame-time budget and front/side/overhead cinematic screenshots.
6. Review effect contrast in daylight, night, rain, snow, fog, indoor lighting
   and with player/camera movement; check color-blind distinguishability,
   photosensitivity/bloom limits, platform scalability, spatial audio,
   mesh LOD, spell telegraph readability and screen-space UI collisions.
7. Only after approval: wire actual combat DataTable, separately authorized
   learnt and mastered starting loadout, actor caster/target transforms, staff
   cast animation montages and sound; prove active-party continuity and save/load.

## Validation and remaining blockers

Run engine-free tests:

```powershell
python unreal/Tools/test_ender_resonator_magic_source.py -v
python unreal/Tools/check_unreal_test_inventory.py
python unreal/Tools/check_automation_registry.py
python -m py_compile unreal/Tools/build_ender_resonator_preview.py
```

All nine targeted source-contract tests passed, as did the full 335-test
engine-free Python suite after updating the exact-count First Wake admission
regression from 29 to 30 named tests. Both source registry scripts passed. These are
**source-only** results. Native Editor compile, imported material and DataTable
assets, material shader validity, actual Niagara, montages, impact SFX, rendered
preview screenshots, interactive casting, multiplayer/save consistency, cinematic
acceptance and merged gameplay **are not yet established**. The renderer uses
native instanced geometry, not Niagara; a later Niagara replacement can preserve
the VFX cue IDs without re-authorizing spells. No claims of AAA visual approval
should be made before native review.
