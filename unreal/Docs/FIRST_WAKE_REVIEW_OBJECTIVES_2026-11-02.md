# First Wake — read-only review objectives for the Unreal vertical slice

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
