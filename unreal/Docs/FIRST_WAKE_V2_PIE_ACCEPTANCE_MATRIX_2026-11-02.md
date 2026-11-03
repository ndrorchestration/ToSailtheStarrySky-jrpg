# First Wake V2 — UE 5.8.4 isolated PIE acceptance matrix

**LATEST PINNED UE 5.8.4 NATIVE RESULT (2026-11-02):** Draft #713 commit `e3e3ff5f349c98b2051a18a5f0c3db6097af8040` **passed Win64 Editor compilation and 25/25 actual registered native automation tests**. The real JSON has 25 unique Success entries, 0 failed/NotRun; the isolated review worktree was clean after the run and `Verify-Unreal.ps1` exited 0. Report SHA-256 `243ad1eedaa344cd52dd4a3380e59cbef34fcfcd3e39c61cc1307195921733a5`. In this **disposable** checkout only, read-only attributes prevented Unreal from rewriting tracked `DefaultEngine.ini` and `DefaultInput.ini`. An earlier unprotected run's dirty-config/token evidence is still preserved, not erased. **This native receipt is only for the exact tested SHA; later documentation revisions require their own verification.** The **13 interactive PIE scenarios, genuine seawater/flotation, Splashdown, art approval, packaged installer and release are NOT TESTED/NOT AUTHORIZED**. See [exact-head gate](INTEGRATION_GATE_2026-11-02.md). No save schema, engine dependency, main-branch, art or Starbourne promotion occurred.


**2026-11-02 · Review-only · Never report PASS without first-hand UE Editor evidence.**

## Scope and provenance

Review candidate: PR #712, stacked directly on #704, #703 and #694. The
currently tracked Prelude V2 map is
`/Game/TSTSS/Review/FirstWake_PreludeInteraction_V2`.
Only the seven early-harbor/engineering milestones are present; **launch,
water contact, stable flotation, Splashdown and Lyra recruitment are not
implemented in this review map**. Neither ship nor character blockouts are
production assets.

### Before opening Unreal

1. Use a fresh, named isolated Windows checkout of **exact PR #712 Git
   HEAD**. Record the full SHA in the review evidence. Do not use protected
   `main`, a player's real project checkout, or a shared sandbox.
2. Do not interfere with a parallel Unreal Editor/Live Coding build. Require
   installed UE **5.8.4** and normal supported Windows toolchain.
3. The isolated project must not contain a pre-existing
   `unreal/Saved/SaveGames/tstss_prelude_pie_quick.sav` before testing F5.
   The game itself refuses to adopt or overwrite a stale PIE slot.
   Any existing `first_wake_quick.sav` is a potentially valuable non-PIE
   player save; it must be left untouched. **Stop** if either slot's
   provenance is uncertain; never overwrite or delete a possibly valuable save.
4. Execute `unreal/Tools/Verify-Unreal.ps1` with an explicit `-EngineRoot`
   on the clean checkout; require complete success, 25 named UE automation
   results, exact HEAD and clean tracked tree. The earlier 23/23 and 13/13
   reports cannot be transferred to this revision.
5. Open `unreal/ToSailTheStarrySky.uproject` in the Editor and load
   `/Game/TSTSS/Review/FirstWake_PreludeInteraction_V2`. Use the Editor
   **Play In Editor** controls, not the uncooked standalone Game executable
   that previously failed during asset-registry startup. Confirm that a
   third-person player pawn exists and can be controlled.
6. Work from one clean PIE session per test scenario. When a scenario
   needs a reset, stop PIE and start a new session rather than altering
   map content or user saves. Never resave the committed V2 review map.

## Manual test matrix — do not mark as tested until executed in PIE

| ID | Setup/action | Expected outcome |
|---|---|---|
| P01 | Start clean PIE, then press J | Cue says `Find Ionia's flyer`; J alone does not advance story |
| P02 | From the original player start, aim at the distant flyer marker and press E | No milestone advancement while outside 300 cm pawn reach |
| P03 | Walk within 100–250 cm of the flyer marker, aim clearly at its visible collision mesh, press E | Flyer accepted; objective becomes `Speak with Captain Ionia` |
| P04 | Press E on the now-completed flyer again, still within range | No progression; temporary yellow `no progress` cue with existing objective |
| P05 | Start fresh PIE, pass the flyer **without** activating it, approach Ionia and press E | Out-of-order Ionia activation rejected; objective remains flyer |
| P06 | In a clean ordered run: flyer → Ionia → boarding; press J after each | Objectives advance in order, with no phantom new party member or magic unlock |
| P07 | While boarded, inspect Reserve before Lift/Pressure | Reserve accepted once; J still names the earliest incomplete inspection, Lift |
| P08 | Complete Lift and Pressure; press E on engineering signoff | Signoff accepted only when all three inspections are recorded; objective becomes launch preparation |
| P09 | In isolated clean slot only: after hiring Ionia press F5, board and inspect Lift, then press F9 | Reports actual save/load results. On successful load, story objective reverts to boarding; player world position does **not** rewind |
| P10 | Press E without hitting a marker, through an occluder, or outside reach | No progression or misleading 'marker rejected' cue for a miss; visibility/reach checks remain active |
| P11 | Inspect a station a second time | Rejected with no mask mutation and no premature engineering signoff |
| P12 | After engineering signoff in V2, inspect story state and try to progress to Splashdown using available review markers | No false `SeaContact`, `FlotationConfirmed` or Chapter 1 Act 1 completion |
| P13 | In a fresh PIE session with an **already existing** `tstss_prelude_pie_quick` save, press F5 and F9; preserve original bytes for comparison | F5 refuses to overwrite the pre-existing review save, F9 refuses to load it, and the external `first_wake_quick` player slot is never touched |

**Existing player-save safety extension:** Before any actual native
save test, ensure the disposable test profile contains **only**
review-created data; never copy genuine player saves into the
test directory. `SaveFirstWake(Slot)` is now source-gated against
overwriting any existing SaveGame with nonempty party data or
corrupt/unreadable metadata. A separate direct-call negative test for
that protection is still required in a disposable native environment.
Do not mark this as independently run by completing P09/P13 alone.
If the engine returns a different result, preserve original file
hashes and report BLOCKED rather than deleting or replacing the slot.

**Save-test safety:** P09 must use a disposable checkout with no pre-existing
PIE review slot. In PIE, F5/F9 now select `tstss_prelude_pie_quick`; the
pawn records ownership only after its first successful save in the
current session. Further F5 writes in the same session may update that
same review slot; new sessions with an existing review slot fail closed.
Non-PIE use still targets `first_wake_quick`. Never touch a player's
non-PIE save folder; discard review-only artifacts only after
preserving test results and proving this session created them.

**Accessibility/UX observations, not acceptance yet:** Record text legibility
at typical play resolution, contrast of green/red/yellow/cyan debug text,
whether the eight-second duration is sufficient, whether J works with a
controller (not currently established), and whether focus loss or layout
occlusion makes interactions difficult.

## Evidence template (fill from actual run; no defaults to PASS)

```text
SOURCE_HEAD=<exact git SHA>
UE_VERSION=<from installed Editor>
MAP_PACKAGE=/Game/TSTSS/Review/FirstWake_PreludeInteraction_V2
MAP_SHA256=<computed hash before/after>
CLEAN_TREE_BEFORE=<verified true/false>
NATIVE_WIN64_EDITOR_BUILD=NOT_TESTED|PASS|FAIL
NATIVE_AUTOMATION_25=NOT_TESTED|PASS|FAIL
PIE_PAWN_AND_CAMERA=NOT_TESTED|PASS|FAIL
PIE_WASD_MOUSE=NOT_TESTED|PASS|FAIL
PIE_E_AND_OCCLUSION=NOT_TESTED|PASS|FAIL
PIE_J_OBJECTIVE=NOT_TESTED|PASS|FAIL
PIE_F5_F9_STORY_SAVE=NOT_TESTED|PASS|FAIL
PIE_CHAPTER_BOUNDARY=NOT_TESTED|PASS|FAIL
CASE_RESULTS=P01:NOT_TESTED,...,P13:NOT_TESTED
STARTUP_LOG_PATH=<local review-only path or NONE>
SCREENSHOTS=<local review-only paths or NONE>
FAILED_CASE_EVIDENCE=<path(s) or NONE>
CLEAN_TREE_AFTER=<verified true/false>
REVIEWER=<actual operator, not AI inference>
CANON_ART_ACCEPTANCE=NOT_AUTHORIZED
MAIN_MERGE=NOT_AUTHORIZED
```

Do not infer a PIE PASS from source preflight, portable C++ tests,
successful build/link, static map authoring, a missing screenshot, or a
GitHub smoke workflow. Use failure logs and frames to isolate the smallest
next fix. If PIE is blocked by missing assets/build collision, record
**BLOCKED**, stop rather than uninstalling/upgrading software or terminating
someone else's Editor, and leave all game data untouched.

## Success criterion for this bounded review

A real Windows Editor build and full 25-test report pass at the exact
source, and a human operator executes P01–P13 on the isolated map with
logs, captured evidence and clean project provenance. This would establish
**a playable Prelude interaction review slice**, not a completed First Wake,
Splashdown, release, shipping build or cinematic acceptance.

## Native automation source-custody finding (2026-11-02)

An actual Win64 Unreal 5.8.4 Editor run at
`fd0b68c28e6289d45f8b8c70228631c24577a352`
compiled successfully and exported 25 distinct successful native
test entries, but clean-tree acceptance was **REJECTED** when Unreal
rewrote `unreal/Config/DefaultEngine.ini` and
`unreal/Config/DefaultInput.ini`. The first file contained a
host-generated Android File Server security token: preserve it as
private **uncommitted** evidence, never commit or copy its value.
This is a **native report observed**, not a verified clean end-to-end
pass and not a P01–P13 gameplay run. A fresh isolated test must
prevent config-file writes without changing the commit or weakening
the final custody gate. The original dirty worktree is retained.

## November 3 — source-level geometry for P02/P03, not PIE proof

Source authoring now rejects a flyer initially inside Ender's 300 cm
reach, an off-floor spawn, any marker footprint leaving the traversal
floor, invalid floor height or nonfinite dimensions. At the committed
plan's positions, the **closest horizontal flyer marker edge** is
**542.5 cm** from spawn, and all seven marker footprints fall on the
same continuous review floor. **13/13 source-only geometry negatives
and positives passed on Windows** (with 10/10 earlier authoring tests).
The **committed V2 `.umap` is unchanged**. This does not prove that
P02/P03 work with actual player movement, E camera traces, terrain
collision, occlusion or dynamic actors. Those specific interactive
cases remain NOT TESTED until recorded in real Editor PIE.
