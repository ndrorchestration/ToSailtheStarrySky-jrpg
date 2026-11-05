# Unreal combat — progressive recruitment versus three-active party QA

Date: 2026-11-01. **Status: native test authored / source CI pending / UE 5.8.4 execution NOT VERIFIED.**
Draft only, stacked exclusively on [PR #671](https://github.com/ndrorchestration/ToSailtheStarrySky-jrpg/pull/671) and inherited #666/#662/#665. No runtime modifications, art admission, merge or release.

## Problem identified during multi-track reconciliation

The canonical early story sequence recruits **Ender → Ionia → Lyra → Reson → Aepex**. In the opening, the crew legitimately contains one, then two, then three protagonists. The Unreal `UTSS_CombatTurnManager::InitializeEncounter` correctly supports **1–3 explicitly selected living active players**, without falsely auto-recruiting absent party members. However `FTSTSSCombatData::ValidateActiveParty` validates **exactly three**, representing the standard full-party battle data contract. These are different purposes and must not be conflated.

This branch does not force three active members before Lyra joins, and does not weaken the three-slot full-party validator. That distinction is explicitly tested, not silently “resolved” by changing runtime rules. An empty enemy group remains invalid; no battle content, combat magic, skill admission, stat number, resource, or equipment is newly granted.

## New native Unreal test

`TSTSS.CombatIntegration.ProgressiveRecruitmentPartySize`, in `TSTSSProgressivePartyIntegrationTests.cpp`, checks:

- a legitimate data validator rejects one- or two-member arrays and accepts an exactly-three array;
- with only Ender recruited, the turn manager admits a one-player review encounter and creates **no phantom bench members**;
- with Ender and Ionia recruited, an encounter admits two, but selecting unrecruited Lyra fails;
- after Lyra joins, exactly three active members can be used, with no fourth or fifth auto-recruited;
- selecting four fails without changing an uninitialized encounter's phase.

All fixtures use noncanonical temporary player/enemy stats, no ability DataTable and no starter spells or Five Lights combat powers. They do **not** establish that the game's first-story scene presently spawns a battle, or that native source compiles.

The full native verification script `unreal/Tools/Verify-Unreal.ps1` now requires this new named test. Exact-head test-name registry checks must also pass before native execution.

## Evidence and boundaries

- Source-level registration and GitHub Actions source inventory: inspect exact PR head after commit.
- **Native UE 5.8.4 UHT/C++ build and Editor automation: NOT RUN** while authorized Windows `neontic` remains offline.
- First Wake player-facing encounter balance, save/load party persistence, recruited/benched UI, event sequencing, battle presentation and full-party starting-state semantics remain separate integration gates.
- Do not mix #665's level-eligible **proposed** action catalog into #662's explicitly authorized `ReviewExecutable` combat executor; the Five Lights remain narrative identity, not automatic spell entitlement.
- Project retains **three active party slots maximum** and five canonical protagonists. Preserve stat hierarchy, storyline, user-approved visuals, Orbiter gate, and Godot legacy build.

The smallest next verified native slice is an exact-head isolated Unreal 5.8.4 Windows Editor build and execution of both `TSTSS.CombatIntegration.ProgressiveRecruitmentPartySize` and `TSTSS.CombatIntegration.DataContractCannotAutoAuthorize`, recording per-test receipts, before adapting any production First Wake encounter.
