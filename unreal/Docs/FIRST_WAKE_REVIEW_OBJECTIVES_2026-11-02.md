# First Wake — read-only review objectives for the Unreal vertical slice

**LATEST PINNED UE 5.8.4 NATIVE RESULT (2026-11-02):** Draft #713 commit `e3e3ff5f349c98b2051a18a5f0c3db6097af8040` **passed Win64 Editor compilation and 25/25 actual registered native automation tests**. The real JSON has 25 unique Success entries, 0 failed/NotRun; the isolated review worktree was clean after the run and `Verify-Unreal.ps1` exited 0. Report SHA-256 `243ad1eedaa344cd52dd4a3380e59cbef34fcfcd3e39c61cc1307195921733a5`. In this **disposable** checkout only, read-only attributes prevented Unreal from rewriting tracked `DefaultEngine.ini` and `DefaultInput.ini`. An earlier unprotected run's dirty-config/token evidence is still preserved, not erased. **This native receipt is only for the exact tested SHA; later documentation revisions require their own verification.** The **13 interactive PIE scenarios, genuine seawater/flotation, Splashdown, art approval, packaged installer and release are NOT TESTED/NOT AUTHORIZED**. See [exact-head gate](INTEGRATION_GATE_2026-11-02.md). No save schema, engine dependency, main-branch, art or Starbourne promotion occurred.


**2026-11-02 · Draft, noncanonical review UX · UE 5.8.4.**

## Narrow runtime change

This branch stacks on the exact source head of First Wake camera-reach draft #704
(`d0dc6b44c4c0b90c1caa543de5026daff0012d79`). It adds
`UTSTSSFirstWakeState::GetReviewObjectiveText()` as a **BlueprintPure**,
read-only string derived from existing `bStarted`, `CurrentBeat` and
`InspectionMask` values. It does not introduce new save fields, change any
milestone order, authorize ship physics, change party recruitment, or grant abilities.

The nine existing beats each have a short provisional objective. While boarded,
the view picks the next unchecked lift/pressure/reserve inspection using the
existing bit mask. Different inspection orders remain valid; the objective is
guidance, not a forced new progression gate. Read-only queries leave state intact.

In non-shipping builds only, the native explorer temporarily displays the
review objective (8 seconds) at BeginPlay, after a **successful** E milestone,
and after a **successful** F9 quickload. F5 and F9 now also display explicit
success or failure feedback based on their actual save/load return values.
The successful messages disclose that the review save covers **story state
only** and does not preserve Ender's world position. Failed operations never
claim persistence. Messages are disabled in shipping builds. This is a **debug-screen cue**, not a final
approved quest HUD, localization, dialogue system or cinematic UI. Blueprints
can read the objective independently of the debug rendering.

## Verification

- `python3 -m unittest discover -s unreal/Tools -p 'test_first_wake_objective_review.py' -v`
  checks source read-only behavior, every beat, masks, guard calls,
  save/load-result feedback and native test registration, **not execution in Unreal**.
- `python3 unreal/Tools/check_automation_registry.py` checks one new required
  native test is registered.
- `TSTSS.FirstWake.ReviewObjectivesAreReadOnly` exercises unstarted,
  flyer/hiring/boarding, inspection-completion, launch, restored water beats,
  terminal and reset states. It must be run via the exact-head UE 5.8.4 Editor
  verification gate, not inferred from prior 23/23 or 13/13 reports.

## Holds / next admission steps

1. On a voluntarily idle Windows Unreal Editor, obtain a clean source-locked
   native Game/Editor build and all required per-test Editor automation entries.
   Do not stop other concurrent editor sessions to force the test.
2. Open the isolated V2 Prelude map in PIE; walk to the flyer, Ionia,
   ship boarding and engineering stations, observe objective cues, and verify
   that E respects the pawn-centered 300 cm limit and occlusion.
3. Verify F5/F9 at the **player input** layer, including cue refresh on a
   successful load and unchanged state after failed input. Existing source
   wiring and lower-level SaveGame receipts do not prove keyboard operation.
4. Investigate bare un-packaged Game startup/asset-registry failure separately.
   The raw executable crash is not a successful packaged game or a reason to
   bypass PIE validation.
5. Keep sky/sea lookdev, character meshes, ship transformation, Splashdown
   physics and Starbourne progression on their independent review gates.

No protected-main merge, production art acceptance, installer or public
release is approved by this branch.

## 2026-11-02 continuation: truthful F5/F9 feedback

The same draft PR adds conditional F5/F9 success/failure messages rather
than introducing another competing branch. F5 confirms saving only when
`SaveFirstWake` returned true; F9 refreshes the objective only when
`LoadFirstWake` returned true. Both actions report failure on false.
The messages explicitly distinguish story-state persistence from player
position, which remains unchanged on load and is not stored on save.
No story beat, actor position, SaveGame schema or save slot was changed.

Additional engine-free source checks cover the success/failure control flow.
No native UE test was executed by this continuation, and the suite remains
25 required registered native tests. Player-level F5/F9 behavior is still
pending independent PIE verification.

## 2026-11-02 continuation — J objective recall and compiled behavior

The temporary on-screen review cue can be recalled with **J**, even after its
eight-second display has expired. This is a read-only convenience action:
the handler only reads `FirstWakeState`, never advances a milestone,
mutates inspection evidence, changes save data, or grants progression.
The default action mapping is explicit in `Config/DefaultInput.ini`.
The transient label now hints `[J to recall]`. This is not a production
journal, visual HUD or accessibility acceptance.

The new host-side `Tools/check_first_wake_objective_compiled.py --self-test`
extracts the **actual** `GetReviewObjectiveText()` C++ implementation,
compiles it with a C++17 compiler against minimal type stand-ins, and tests
16 started/unstarted/inspection/launch/water/invalid-state cases. Each
asserts objective text, stable repeated reads and no state mutation. A
single mutated objective string must produce a failing run, proving the
probe detects semantic drift. GitHub source preflight runs this experiment.

**Limit:** Compiling this real function body with API stand-ins does not
compile Unreal HeaderTool reflection, native module dependencies, input
binding behavior in PIE, screen rendering, or native automation. All 25
registered native test cases and the manual E/J/F5/F9 playtest remain on
HOLD until an isolated UE5.8.4 Windows run passes at this exact head.

## 2026-11-02 continuation — rejected marker interaction feedback

An in-reach marker that **rejects** `TryActivate(FirstWakeState)` now shows
a temporary yellow review hint that no progress occurred and repeats the
current read-only objective. The message does not guess whether the cause
was a wrong story order, a repeated inspection, or another legitimate
refusal. It is emitted **only after a real camera visibility hit, an
`ATSTSSMilestoneActor` match and successful pawn-centered range check**.
No claim of interaction is made for missing hits or out-of-range markers.
All debug text remains outside shipping builds.

Source tests verify the gate order, denial branch, absence of story
mutation and shipping exclusion; no PIE interaction or visual capture
has yet run at this exact head. This keeps the review progression
transparent during keyboard playtesting without altering canon, physics
or the save format.

## 2026-11-02 continuation — PIE save isolation

F5/F9 now use separate slots by engine world type: in **Play In Editor**
(`EWorldType::PIE`) they use `tstss_prelude_pie_quick`; outside PIE they
continue using the original `first_wake_quick`.

A transient per-pawn ownership flag is set only after a successful first
PIE write. A new PIE session refuses to overwrite an already existing
review slot and refuses to load any review slot it did not itself
successfully save. In both cases a non-shipping diagnostic explains the
hold. Repeated saves **within the same PIE session** remain possible.

No player save is migrated, deleted or overwritten by this update.
No serialized schema, story beat, ship physics or game art is changed.
The independent source verifier enforces the new routing; the PIE test
matrix now adds **P13** for a stale-slot negative test.

These controls have passed no native UE5.8.4 runtime test at the new
source revision; actual write/load behavior is still an explicit hold.

## 2026-11-02 continuation — compiled F5/F9 handler behavior

Source-only code-inspection tests do not establish that `QuickSave()` and
`QuickLoad()` actually make the intended calls. The new standalone
`unreal/Tools/check_first_wake_pie_save_compiled.py --self-test` extracts
those **exact existing C++ method bodies** and compiles them against
small in-memory API stand-ins (no modifications to game methods).
It executes 12 behavioral assertions for PIE save refusal, stale-save
load refusal, failed save, successful current-session save and rewrite,
successful/failed current-session load, new-session isolation, and
non-PIE compatibility. A deliberately unsafe mutation that disables the
existing pre-save collision check must fail the same executable test.
The script writes to temporary compiler files only, never to actual
Unreal SaveGame slots, and uses no native engine dependencies.

The hosted Unreal source-preflight workflow now runs the compiled probe.
A passing result proves these C++ method bodies behave as expected **under
the test stand-ins**, not that Unreal's engine SaveGame service or PIE
runtime follows the same behavior. Exact-source native Windows UE 5.8.4
validation and real keyboard playtesting remain required and unclaimed.

## November 2, 2026 — Preserve existing party saves on story-only F5

A native `UTSTSSSaveGame` payload can contain valid `PartyRoster`
data, but the First Wake review pawn does **not** manage that party.
Previously `SaveFirstWake` always allocated a fresh, roster-empty
save object. Saving to an existing `first_wake_quick` slot could
therefore silently discard a roster. The method now **refuses writes**
to an existing save when the file is unsupported, corrupted, unreadable
or contains a nonempty `PartyRoster`. A valid existing roster-free
save can be updated by reusing the loaded object, preserving fields
outside the First Wake story snapshot.

The direct C++ source method is compiled/exercised against in-memory
stand-ins by `check_first_wake_save_guard_compiled.py --self-test`,
including a negative mutation that removes the roster protection.
The test uses no actual disk SaveGame or Windows Unreal service. Native
PIE evidence, 25 named automations and external save hash verification
remain pending. This safeguard does **not** authorize party recruitment
or an automatic combat roster synchronized from narrative story state.
