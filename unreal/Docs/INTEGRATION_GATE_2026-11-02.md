# Unreal First Wake — combined authority/dependency review acceptance gate

**2026-11-03 isolated vertical-slice overlay:** The [joined review](FIRST_WAKE_VERTICAL_SLICE_JOINED_REVIEW_2026-11-03.md) selectively combines the quickload water-evidence fix and interaction-to-Splashdown C++ automation with this V2 Prelude review lineage. It raises the **required native registry to 26 tests** on that separate draft branch. The original 25/25 native receipts below remain true **only for their exact older SHAs**; this new joined head has no Unreal native/PIE approval. Protected main, original saves, review art and Starbourne gate remain unchanged.

**LATEST PINNED UE 5.8.4 NATIVE RESULT (2026-11-02):** Draft #713 commit `e3e3ff5f349c98b2051a18a5f0c3db6097af8040` **passed Win64 Editor compilation and 25/25 actual registered native automation tests**. The real JSON has 25 unique Success entries, 0 failed/NotRun; the isolated review worktree was clean after the run and `Verify-Unreal.ps1` exited 0. Report SHA-256 `243ad1eedaa344cd52dd4a3380e59cbef34fcfcd3e39c61cc1307195921733a5`. In this **disposable** checkout only, read-only attributes prevented Unreal from rewriting tracked `DefaultEngine.ini` and `DefaultInput.ini`. An earlier unprotected run's dirty-config/token evidence is still preserved, not erased. **This native receipt is only for the exact tested SHA; later documentation revisions require their own verification.** The **13 interactive PIE scenarios, genuine seawater/flotation, Splashdown, art approval, packaged installer and release are NOT TESTED/NOT AUTHORIZED**. See [exact-head gate](INTEGRATION_GATE_2026-11-02.md). No save schema, engine dependency, main-branch, art or Starbourne promotion occurred.


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
2. Compile Win64 Editor through `unreal/Tools/Verify-Unreal.ps1`
   with `-EngineRoot` and `-ExpectedHead` set to the **full exact 40-character
   SHA** of the isolated checkout. Require **25 distinct successful named
   native automation results**, including
   `TSTSS.FirstWake.ReviewObjectivesAreReadOnly`. Do not transfer #685's
   23/23 result or a source-registered 25-name list. Each run now writes its
   own ignored `Saved/MigrationEvidence/<SHA>-<UTC>-<nonce>/` folder with
   `head.txt`, `build.log`, `automation.log`, and `AutomationReport/index.json`.
   Previous failures and successes are **never deleted or overwritten** by
   the verifier; `-SkipTests` remains build-only and cannot certify 25/25.
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

## Repeat-run evidence protection — integrated review

The prior `Verify-Unreal.ps1` reused one report folder and deleted the
old automation result before another run. The integrated draft eliminates
that deletion. It checks full-length `-ExpectedHead` against actual
`git rev-parse HEAD` **before** creating an evidence directory; it
still requires a clean worktree, real Win64 Editor build, and 25
exact per-test successful native JSON entries. A per-run folder under
ignored `Saved/MigrationEvidence/` includes a UTC timestamp and random
nonce so repeated and failed attempts do not overwrite one another.
An evidence directory collision throws rather than reuses a prior run.
Do not share logs containing any generated local credentials.

**Source-only protection:** `unreal/Tools/test_native_evidence_safety.py`
checks exact SHA gating, log retention, unique paths and negative
mutations. This does **not** execute PowerShell, compile Unreal or
establish the performance of the new verifier on Windows. Its first
actual test must occur in a disposable, user-authorized checkout.

## Exact engine identification — integrated review addendum

The native verification script now reads the actual installed
`<EngineRoot>/Engine/Build/Build.version` **before starting** UBT or
creating a receipt. It must report **5.8.4** (`MajorVersion=5`,
`MinorVersion=8`, `PatchVersion=4`). Missing/unparseable metadata
or a different patch triggers **HOLD**, even if the project's
`EngineAssociation` is still `5.8`. A future legitimate patch change
requires deliberate review rather than silent acceptance.

GitHub hosted `Unreal source preflight` additionally uses the real
PowerShell parser, and exercises the native script against **synthetic**
wrong-version and wrong-SHA fixtures that must fail **before** launching
any executable or creating review evidence. These are genuine script
failure-path checks but **not** Windows UE build or playtest evidence.
All fixtures are temporary under the GitHub runner and cannot access
player SaveGame files.

## Native automation JSON receipt validation — no aggregate-only acceptance

The integrated native script now **calls** a separate source-controlled,
read-only PowerShell function in `unreal/Tools/Assert-NativeAutomationReport.ps1`.
It accepts a report only with all **25 unique required named tests**,
zero failed and zero not-run, well-formed nonnegative integer summary
counts, distinct per-test `fullTestPath` values, `Success` state for
all reported test entries, and agreement between the reported success
count and the number of actual successful entries. A missing name,
duplicate, contradictory aggregate or malformed JSON **fails closed**.
The validator does **not** grant PIE, character-art or release approval.

The companion `unreal/Tools/Test-NativeAutomationReportFixtures.ps1`
replays the **same actual validation function** in hosted PowerShell
against synthetic success and invalid-report variants (inflated counts,
missing/duplicate test names, skipped/failed entries, missing fields
and malformed JSON). All fixtures live in a temporary folder; **no
Unreal Engine process or SaveGame is opened**. This is a stronger check
of report-admission logic, not proof that UE5.8.4 emits the currently
expected JSON schema or that 25 native tests executed at this head.
Keep raw native JSON and logs if the real engine schema differs;
investigate rather than changing fields to manufacture acceptance.

## Story-only save overwrite protection — source-side review

The First Wake explorer can persist **story/inspection progress only**;
it has no authority to capture or modify a combat party roster. Its
`SaveFirstWake(Slot)` now checks the slot name, and when a SaveGame slot
already exists, requires that `UTSTSSPersistence::LoadProgress(Slot)`
returns a valid, supported, structurally valid payload with **no party
members**. Any unreadable, future-versioned, corrupt, or roster-bearing
existing save produces **false without calling SaveProgress**. When a
roster-free existing payload is valid, the method reuses the loaded object,
updating only its First Wake story fields and keeping other save fields
intact. An absent slot uses a fresh payload. This applies to explicit
`SaveFirstWake(Slot)` calls as well as normal/PIE quicksave routing.

The source check
`python3 unreal/Tools/check_first_wake_save_guard_compiled.py --self-test`
compiles the **actual production SaveFirstWake method** against API doubles
with in-memory fake slots and tests legitimate first/updated story saves,
preservation of future unrelated fields, denial of player roster/invalid
slots/corrupted or unreadable existing saves, and persistence failures. It
intentionally deletes the roster safeguard in a test copy and requires
that mutation to fail. This does **not** execute the Unreal SaveGame service
or guarantee atomic disk writes, multiplayer race freedom, or real keyboard
PIE behavior. Do not claim that player saves were migrated or modified.

**Native follow-up:** A user-authorized disposable Windows checkout
must separately check that direct Blueprint `SaveFirstWake` and F5
refuse a seeded roster-bearing or unreadable slot without byte changes;
preserve original hashes and never use actual player saves. Avoid
representing a positive source fixture as in-engine validation. If
native validation fails, keep PR #713 draft; inspect the engine record
without overwriting or deleting it.

## November 2 native Win64 exact-head receipt — partial, source custody blocked

An isolated detached worktree on authorized Windows workstation `neontic`
ran `unreal/Tools/Verify-Unreal.ps1` at exact source
`fd0b68c28e6289d45f8b8c70228631c24577a352`, using installed
Unreal Engine **5.8.4**, MSVC 14.44 and Windows SDK 10.0.26100.
**Native Win64 Editor compilation succeeded.** A second invocation of
the verifier actually launched native Editor automation and produced a
JSON report with **25 distinct tests marked Success**, zero failed and
zero not-run. The existing strict report parser accepted the contents,
but the verifier's final *source-custody* check **failed**, correctly
refusing to mark the total operation PASS.

Cause: Unreal itself rewrote tracked `unreal/Config/DefaultEngine.ini`
and `unreal/Config/DefaultInput.ini` in the isolated worktree during
automation. The first change included Android File Server host settings
and a generated local security token. These two changed files **remain
uncommitted in the isolated worktree for forensic review**. **Never
stage/publish their diffs, send the token to an external system, or
reset the evidence as a shortcut.** The clean tree check is intentionally
fail-closed. Retained local evidence is under
`C:\TSTSS_PR713_NativeReview_20261102\unreal\Saved\MigrationEvidence\`
with per-run `head.txt`, build/automation logs and JSON.

**Strict status:** `EDITOR_BUILD=PASS` at the pinned old SHA;
`NATIVE_AUTOMATION_REPORT=25_SUCCESS_ENTRIES`;
`NATIVE_25_ACCEPTANCE=HOLD_CONFIG_MUTATION`;
`PIE_P01_P13=NOT_TESTED`; `MAIN_MERGE=NOT_AUTHORIZED`.
This receipt does **not** transfer to later documentation commits.

**Smallest reversible native follow-up:** use a **fresh** isolated
checkout at the integration candidate's exact new SHA, record
pre-run hashes for the two tracked INI files, and experimentally
prevent engine-side rewrites only within that disposable checkout
(e.g. Windows read-only file attributes) while retaining Engine output
and all logs. Do not silence source-integrity checks or auto-discard
other modifications. The native report must again contain 25
unique successful tests and a pristine tracked tree *after* execution.
If read-only config prevents native execution, mark BLOCKED and
investigate; do not publish token-bearing defaults.

## Native Editor map-admission subgate (separate from 25 named automations)

The dedicated [native Prelude map and actor gate](FIRST_WAKE_NATIVE_MAP_ADMISSION_2026-11-02.md) now verifies a real loaded level, reflected milestone C++ actors, collision declarations and ordered read-only objectives using the Editor Python commandlet. Its hosted source checks and **8 Windows safety tests** passed, but the attempted native build at `a06f203902fcb1594e1b55e43d1ec9f27d9ed583` was **blocked** by active Unreal Live Coding. The new review script correctly refuses concurrent Editor activity before building, confirmed on Windows at `cfb88a9edf582b57ca95db1f731b68d79da3a22c`. The native **map/actor test has NOT RUN**, P01–P13 genuine PIE remains NOT TESTED, and previous 25/25 evidence belongs solely to its earlier exact SHA.


## Separate source-locked native map/actor acceptance gate (2026-11-02)

An opt-in [real Editor map verification lane](FIRST_WAKE_NATIVE_MAP_ADMISSION_2026-11-02.md)
now uses `Invoke-NativePreludeMapQA.ps1` with an explicit SHA,
`-PreflightOnly`, an exact-source successful `Verify-Unreal.ps1
-SkipTests` receipt (`verified-build.json`), and actual native
Python Editor map inspection. This prevents a log-only, unbuilt or
dirty checkout from being treated as playable evidence; it also refuses
to launch while another Unreal Editor or Live Coding session is active.
Hosted tests parse the actual PowerShell script and exercise negative
source mutations. **Real map loading is still NOT TESTED**; the
previously passed 25 native automations belong to their exact earlier
commit. P01–P13 PIE, water physics, Splashdown, character rendering,
ship production art and merge/release remain distinct held gates.

## Real map-checker behavior regression suite — November 3

`test_pr713_native_prelude_behavior.py` calls the exact read-only
`check_native()` function with deterministic in-memory Editor stand-ins.
All 23 valid/invalid scenarios passed on Windows and hosted CI at SHA
`2a9c03a5588ff4290211d9d315fe367690821a19`. The suite catches
incorrect milestone ordering, missing/misconfigured real-world actor
contracts, false visual water collision and premature Chapter 1 claims.
It is **source behavior verification**, not native Editor or player PIE
proof. The real map load remains blocked by concurrent Live Coding;
no other Editor process was stopped. Refer to the
[native map admission guide](FIRST_WAKE_NATIVE_MAP_ADMISSION_2026-11-02.md).

## Bounded native map-report validation — November 3

The integrated native map runner now requires an independent production
PowerShell validator, `Assert-NativePreludeMapReceipt.ps1`, to
approve every report field. A matching status and actor count alone
**cannot** pass. Its 32 synthetic positive/negative cases and the
14 launcher source-safety tests passed on Windows at source
`afac6d0eddaa9aa01a391d466d76557666fe6a9a`.
Hosted source preflight likewise succeeded, including six PowerShell
syntax checks. The validator checks exact source/map hashes, Unreal
version, all seven actor locations, objective and collision proofs,
input source mappings, distinct inspection bits, and explicit denials of
PIE, disk saves, water physics, art and Chapter 1 approval.

This is source/fixture evidence, **not** a real Unreal level inspection.
The live Editor/Live Coding sessions remain an independent idle-workstation
blocker for the commandlet. Genuine P01–P13 PIE and Splashdown remain held.
See [native map admission handoff](FIRST_WAKE_NATIVE_MAP_ADMISSION_2026-11-02.md).


## November 3 — persistent review objective HUD, no new dependencies

The integrated First Wake review GameMode now selects a non-shipping
`ATSTSSFirstWakeReviewHUD` whose `DrawHUD()` reads the current
objective from Ender's `UTSTSSFirstWakeState` each frame and
displays temporary Prelude controls/provenance. It has **no
authoritative story state of its own** and no new UMG/Slate/plugin,
SaveGame schema or engine version requirement. The render path is
compiled out for shipping builds; the overlay declines to render
on very small viewports rather than knowingly clip instructions.

A GitHub source-preflight lane compiles the **actual production
DrawHUD C++ method** using in-memory C++17 Engine API doubles
in both development and shipping configurations and requires that
the shipping path emit no review overlay. The UE header API
signatures were also checked on the authorized workstation;
five separate GameMode wiring / non-mutation integration tests
passed there. This is **not native Unreal rendering evidence**.
A real Win64 UE5.8.4 build and actual 1280×720/500 px PIE visual
inspection, objective synchronization, keyboard focus and
controller/accessibility review remain **NOT TESTED** at this
code head. Original earlier 25/25 Unreal automation receipt
remains source-pinned to its older head only. No art approval,
Chapter 1 completion or production release is conferred.

## November 3 — responsive source-derived engineering status on review HUD

In draft integration PR #713, `ATSTSSFirstWakeReviewHUD::DrawHUD()`
now derives both the current objective and the three station status
indicators **fresh each draw** from `UTSTSSFirstWakeState`.
The indicator bits are Lift `0x01`, Pressure `0x02`, Reserve
`0x04`; no status is cached or written. Narrow viewports use
compact guidance; the overlay refuses to appear for already-entered
Chapter 1 story states and stays absent in shipping builds. This
improves a real First Wake interaction review affordance without
changing production UI, SaveGame schemas, dependency/plugin versions
or canonical story events.

At code SHA `1f983d0c202ea0e52c5fd01725b3c436f4584bfa`,
the actual C++ function compiled against portable UE API stand-ins
for both development/shipping and **6/6 Windows source integration
tests passed**, with clean Git status. **Native UE 5.8.4
build/rendering for the changed HUD and all P01–P13 PIE
scenarios remain unverified.** The older actual 25/25 native
automation run belongs to its own exact prior SHA, not the
current HUD source. Do not merge/promote based on portable checks.
