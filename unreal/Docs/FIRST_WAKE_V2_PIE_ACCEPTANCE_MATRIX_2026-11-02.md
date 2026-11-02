# First Wake V2 — UE 5.8.4 isolated PIE acceptance matrix

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
3. The isolated project must not contain
   `unreal/Saved/SaveGames/first_wake_quick.sav` before running tests. If it
   exists, **stop**; never overwrite or delete a possibly valuable save.
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

**Save-test safety:** P09 must use a disposable checkout and a verified
absent review quicksave file. The game's F5 behavior is a normal quicksave,
which can overwrite an existing slot; this test does not authorize using a
player's save folder. Discard temporary *review-only* save artifacts only
after preserving the test result and confirming they were created during
this run.

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
CASE_RESULTS=P01:NOT_TESTED,...,P12:NOT_TESTED
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
source, and a human operator executes P01–P12 on the isolated map with
logs, captured evidence and clean project provenance. This would establish
**a playable Prelude interaction review slice**, not a completed First Wake,
Splashdown, release, shipping build or cinematic acceptance.
