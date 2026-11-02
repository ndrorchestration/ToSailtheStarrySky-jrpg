# Unreal First Wake — combined authority/dependency review acceptance gate

**November 2, 2026 · Draft [integration PR #713](https://github.com/ndrorchestration/ToSailtheStarrySky-jrpg/pull/713) · NOT MERGED · NOT PLAYABLE-CERTIFIED.**

## What was actually brought together

This is a **single bounded composition**, not a Git merge of all the parallel
drafts. The PR is based on [#712](https://github.com/ndrorchestration/ToSailtheStarrySky-jrpg/pull/712)
and inherits its existing review ancestry: #704 (camera and separate 300 cm
pawn reach) → #703 (independent V2 save/map QA) → #694 (seven-stop tracked V2
review map) → earlier C++ foundations. No sibling ship-art/combat-branch
history was grafted in.

| Source | Exact inspected head | Files selectively carried into this review | Distinct authority |
|---|---|---|---|
| [#657](https://github.com/ndrorchestration/ToSailtheStarrySky-jrpg/pull/657) | `0a03ea92999445bc0b5d78202fdbf0a5192945b3` | Root `AGENTS.md`, `README.md`, character/art authority and Level 1 relative stat contract + design-only JS validator and negative tests | Current Unreal-first creator decision; NO numeric stat authorization or art promotion |
| [#711](https://github.com/ndrorchestration/ToSailtheStarrySky-jrpg/pull/711) | `4e4a40aed34c0ff6789ce4a69ca757f75139fee2` | Dependency/evidence register, manifest baseline, independent source checker, reconciliation/source negative controls | Historical cross-PR evidence; branch-specific plugin baseline, not release |
| [#712](https://github.com/ndrorchestration/ToSailtheStarrySky-jrpg/pull/712) | `36f64849c17d16e700a0f93f2ba3dec7dd49e84c` | All existing First Wake review source, V2 map ancestry, objective and PIE save logic, stronger dependency contract, documentation | Current integration test target, still draft and native unverified |

**Focused reconciliation:** The copied Level 1 rank-design JSON once said to
verify Godot's native HP implementation. The integrated **review copy only**
now says to verify Unreal Engine 5.8 instead. The creator's approved strict
relative inequalities and their lack of approved numeric values did not change.
This wording correction was not pushed back to #657.

The #711 register is retained as the dated **narrative index** to its other
branches and holds, while #712's
`unreal/Tools/first_wake_dependency_contract.json` plus
`check_first_wake_dependency_contract.py` remain the **stricter active
machine-readable review gate**. #711's
`dependency_baseline.json` and `check_dependency_contract.py` are still
run as an independent **legacy comparator**. Their shared engine family,
enabled plugin, target configuration, native modules and historical npm
manifest versions must agree. Neither authorizes an actual install.

## Mandatory source-only gate

Run from repository root on the **exact candidate commit**:

```bash
python3 unreal/Tools/check_first_wake_dependency_contract.py
python3 -m unittest discover -s unreal/Tools -p 'test_first_wake_dependency_contract.py' -v
python3 unreal/Tools/check_dependency_contract.py
python3 -m unittest discover -s unreal/Tools -p 'test_dependency_contract.py' -v
python3 -m unittest discover -s unreal/Tools -p 'test_dependency_register_reconciliation.py' -v
node tests/level-one-stat-ranks.test.js
python3 unreal/Tools/check_integrated_review_contract.py
python3 -m unittest discover -s unreal/Tools -p 'test_integrated_review_contract.py' -v
```

The hosted `.github/workflows/unreal-source-preflight.yml` runs these
checks **in addition to** the prior First Wake and combat source/portable-C++
gates. Negative controls reject wrong engine authority, unreviewed stat
numbers, roster/rank changes, cross-baseline plugin/target drift, historical
npm drift, incomplete P01–P13 and unauthorized native/release claims. A
registered Unreal test is *not* a result from UnrealEditor.

## Windows Unreal gate — HOLD until the workstation is available

In a **new isolated checkout** of PR #713's exact SHA, with a voluntarily
idle Windows UE 5.8.4 Editor and disposable SaveGame context:

1. Record current Git HEAD and clean tracked tree, UE build tool path/version,
   any actual plugin availability and exact engine installation.
2. Compile Win64 Editor through `unreal/Tools/Verify-Unreal.ps1` and obtain
   **25 distinct successful named native automation results**, including
   `TSTSS.FirstWake.ReviewObjectivesAreReadOnly`. Do not transfer #685's
   23/23 result or a source-registered 25-name list.
3. Open `/Game/TSTSS/Review/FirstWake_PreludeInteraction_V2` in PIE and
   execute the documented [P01–P13 protocol](FIRST_WAKE_V2_PIE_ACCEPTANCE_MATRIX_2026-11-02.md).
   Verify E visibility/reach, J objective recall, story order and F5/F9 actual
   save-slot isolation, including an already existing review-slot negative.
4. Capture full native automation JSON, Editor/gameplay logs, actual screenshots,
   source SHA, V2 map hash before/after, unchanged player save hashes and a
   final clean tracked tree. An interrupted test is **BLOCKED**, not a PASS.
5. Release/render and physical sea-water/Splashdown acceptance are separate
   independent future gates. No synthetic click can manufacture flotation
   or Chapter 1 Act 1. No Starbourne/Orbiter unlock.

## Integration permissions and open risks

- **Not authorized:** protected-main merge, sibling PR auto-merge,
  real package/SDK/plugin upgrade, user save deletion, production asset
  acceptance, combat affinity→spell auto-unlock, packaged installer or
  release/public announcement.
- **No dependency updates were performed.** Engine family `5.8`,
  `PythonScriptPlugin` explicitly enabled, V7/UE5.8 targets, four built-in
  engine modules and legacy npm lockfile remain unchanged.
- **Branch conflicts resolved here:** root AGENTS/README engine direction
  superseded, Five Lights/party/cast stats linked without inventing numeric
  balance, #711's cross-branch dependencies reconciled with #712's stricter
  contract, First Wake native/milestone evidence kept separate from source CI.
- **Still open:** native compilation and interactive PIE, actual save replay,
  game-ready 3D faces/rigs, controlled bridge/hull transforms, strut render
  fidelity, continuous collision, fully playable launch/water arc and
  Splashdown physics.

The composed branch is a **reviewable next candidate**, not a new canonical
production engine build or approval to close the source PRs.
