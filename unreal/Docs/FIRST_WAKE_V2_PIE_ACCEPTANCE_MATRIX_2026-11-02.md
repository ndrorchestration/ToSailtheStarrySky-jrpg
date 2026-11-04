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

## November 3 — real-world position and marker scale admission prerequisite

The separate, read-only native Editor map checker now requires that
the **actual loaded milestone actor transforms**, spawn and traversal
floor agree (within 1 cm) with the authored Prelude blockout. It
checks actual marker proxy scales to prevent a larger collision target
from invalidating the claimed starting distance, measured floor
coverage for seven marker footprints and an initial nearest horizontal
flyer edge beyond 300 cm. This is a prerequisite for interpreting
P02/P03 movement/reach scenarios, not a substitute for the actual
E interaction, player-centered reach, occlusion/camera direction,
collision and UI acceptance criteria.

Source-side verification on Windows: 31/31 actual-checker behavior
cases, 8/8 admission checks and 37/37 synthetic native report
fixtures PASS at code SHA
`127667c48045f06f82f23d98faafe35eca3df6a3`.
**Actual Editor map inspection and P01–P13 keyboard PIE remain NOT
TESTED** while other Unreal Editor/Live Coding sessions are active.
No committed map, SaveGame, art or engine dependency was changed.


## November 3 — read-only persistent objective HUD review acceptance

A new **non-shipping, review-only** C++ `ATSTSSFirstWakeReviewHUD`
is selected by `ATSTSSGameMode` in non-shipping builds. It draws a
bounded translucent first-person-screen overlay (not in-world art),
the active `GetReviewObjectiveText()` from Ender's own
`UTSTSSFirstWakeState`, W/A/S/D/E/J/F5/F9 review controls, and an
explicit noncanonical Prelude disclaimer. It does not cache or
advance story state, inspect/save a player slot, alter combat,
recruit anyone, or unlock launch/sea contact/Splashdown.

The HUD uses the **existing Engine AHUD/Canvas APIs**; no UMG,
Slate, plugin or module dependency was added. It rejects very small
viewports rather than knowingly drawing a clipped panel and is
disabled in `UE_BUILD_SHIPPING` builds. Legacy transient debug
messages and J read-only recall remain available.

**Source proof, not in-engine proof:** At implementation revision
`4eaaa4246f86c4f5f81f406bb61e0f74c7f4709e`, GitHub
Unreal source preflight compiled and ran the **actual C++
`DrawHUD()` method** against controlled API stand-ins in both
non-shipping and shipping modes; all cases passed. The associated
five source-integration checks passed on Windows with clean Git
state. Installed UE5.8.4 header signatures were checked for
`DrawText`, `DrawRect`, fonts, Canvas clipping and GameMode's
HUDClass. **A native Unreal Editor build / PIE rendering of this
new HUD has NOT BEEN RUN** while unrelated Editor/Live Coding
sessions are active.

Add to **P01/P06/P09/P12** the observation that a persistent
objective matches the J cue after opening, ordered milestones,
story quickload and blocked premature Splashdown. Verify visual
contrast, readability and overlap at **1280×720 and 500 px wide**
as part of *actual PIE*, not from portable stand-ins.
The HUD does not convert any P01–P13 result from NOT TESTED
into PASS.

## November 3 — responsive engineering inspection HUD review

The non-shipping C++ `ATSTSSFirstWakeReviewHUD` now provides
three read-only Lift, Pressure and Reserve inspection indicators
directly from `UTSTSSFirstWakeState::GetInspectionMask()`.
An incomplete inspection appears muted and a completed inspection
uses a brighter indicator. A narrower review viewport uses shorter
control copy and disclaimer without adding a HUD plugin or changing
canonical art. If the player's existing state reports Chapter 1
Act 1, the **Prelude** overlay stops drawing rather than pretending
the Chapter 1 UI is implemented.

**Executed source evidence at `1f983d0c202ea0e52c5fd01725b3c436f4584bfa`:**
the hosted Unreal preflight extracted and compiled the **actual**
`DrawHUD()` method with C++ API doubles in development and shipping
modes. It verified a fresh 0/3 mask, a live 2/3 update and a 3/3
update, narrow viewport copy, absent/invalid state denial, Chapter
1 suppression and absence of the overlay in shipping. The **6/6
Windows HUD contract tests** also passed at the same exact SHA with
a clean tracked worktree.

**Still required in actual PIE:** verify all three indicator states
by inspecting stations in different orders, confirm the displayed
objective agrees with J and F9, test on at least 1280×720 and
500-pixel-wide review viewports for clipping/contrast, then confirm
the overlay does not misrepresent Splashdown as implemented. The
portable C++ checks cannot establish real UE font metrics, rendering,
line-of-sight, movement, keyboard input or the P01–P13 results.


## November 3 — MSVC proof of HUD method, real PIE visuals still required

The real C++ `DrawHUD()` method was extracted without rewriting its
body and compiled/executed under installed MSVC 2022 Build Tools
14.44 using minimal Engine API stand-ins at exact SHA
`64387804fb40cde97d20bb68e033ec57bf5cbfd2`.
**21/21 non-shipping behavior assertions** and **1/1 shipping
absence assertion passed**; clean detached Windows worktree.
This supplements the Linux hosted C++ source test and supports the
review-only HUD's intended objective/engineering lamp behavior.
It does **not** prove native Unreal rendering, on-screen font
clipping, contrast, visibility, actual SaveGame/PIE interactions or
P01–P13. The open Editor was minimized; no trustworthy
visual capture was obtained. Keep P01–P13 and both native visual
review resolutions (**1280×720 and 500 px wide**) as NOT TESTED
until observed and recorded in a real Editor play session.
