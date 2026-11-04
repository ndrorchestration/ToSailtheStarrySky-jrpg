# Ender equipment-to-combat vertical-slice seam — review only

Date: 2026-11-04. Authority: **NONCANONICAL, DRAFT, UNMERGED, NOT PLAYER-PLAYABLE**. Base: PR #741 exact head `0952c949dca2d91d472ef27d6f26d6aa4ee972c1` (25/25 actual UE 5.8.4 Editor automation and DataTable test PASS on that older head).

## One isolated integration proof

The new `FTSTSSReviewEquipment` has an **in-memory caller-provided instance ledger** and actor loadout with three slots (weapon, armor, accessory). It neither grants items nor writes `.uasset`, source game content, `SaveGame`, or character equipment. `TryEquip` validates ownership/slot/bounds/conservation and swaps atomically; attempts to steal an Ionia item, repeat a slot equip, duplicate a reference, or forge a weapon fail closed. `TryProjectAtBattleStart` creates a **one-time fresh combat roster** from immutable base stats plus validated item bonuses. It replaces any caller's claimed equipped weapon class with the *actual* owned staff evidence and leaves learned knowledge and mastery unchanged.

A single native Editor automation test `TSTSS.CombatIntegration.EnderGearSpellBattleReview` composes:
1. Ender baseline → test-owned `Staff` (+3 attack) and review vest (+4 defense); a fabricated staff claim without equipment is denied.
2. `ReviewStaffStrike` weapon-legal physical attack, then enemy counterattack mitigated by equipped armor through the actual existing `FTSTSSCombatRules` damage formula.
3. `ReviewStaffArc` equipment-gated technique with cost and animation cue ID, followed by an enemy turn.
4. `ReviewLumenPulse` learned + explicit `Lumen` rank-1 + **ReviewExecutable** spell, with resource cost and VFX cue ID.
5. Distinct negative checks for DesignOnly spell, missing mastery, foreign gear, wrong slot, unchanged output on rejected actions and job-policy preview denial.

All fixture numbers, item names and spells are **test-only**. Ender's innate Lumen affinity does not award school mastery. His Rift Scholar native profession persists independently of optional combat jobs. Five Lights remain narrative affinities only. Generic `Attack` continues to power the **review spell's** resolved damage; this is **not an approved MAG equation or MP economy**.

## Acceptance stages

- **Source-level:** new suite named once in `Verify-Unreal.ps1`, audit declared names bidirectionally and run existing engine-free source checks.
- **Native Unreal:** clean isolated checkout at the exact new branch head, UBT/UHT Editor build, run **all 26 native TSTSS automation cases** and capture full exported JSON with 26 Success/0 Failed/0 NotRun. Prevent unrelated Editor/Live Coding conflicts and preserve exact-head clean-tree integrity.
- **Presentation:** **NOT IMPLEMENTED**. The cue IDs are metadata only: no Niagara systems, animation montages, equipment sockets or usable combat menu.
- **Gameplay:** **NOT IMPLEMENTED**. No enemy encounter world map, real user commands, 3D battle arena, validated 3-active party, persistent items/shops/loot, job unlocks, stat balancing or versioned save. This is a behavioral vertical-slice *seam*, not a playable battle.
- **Authority:** no production asset, real equipment, approved spells, class roster, character stat chart, main merge or Starbourne player unlock.

## Next smallest step

After native compilation and full review-regression success, add one opt-in disposable **combat arena Actor/UMG UI** that routes player-selected actions to the same transactional skill executor. Make one actual staff attack, technique and spell visible with appropriate animation and effects, then test gamepad, restart and lost-item prevention. Keep creator approval and production integration as separate gates.
