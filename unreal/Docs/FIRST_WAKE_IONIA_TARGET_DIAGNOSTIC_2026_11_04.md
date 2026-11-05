# First Wake P0-1 — opt-in interaction targeting diagnostic (review only)

## Scope and authority

This change is stacked on draft #756 at `fc5f3c78f569ab783ce02f9f7751135e17cb1214`.
It diagnoses GitHub issue #757: the Flyer E interaction succeeded on NEONTIC,
but Ionia hiring did not advance in the observed PIE session. The cause is
**not yet established**. It does **not** resolve the player-story blocker,
alter interaction range (300 cm), revise the camera boom (360 cm), change
`ECC_Visibility`, change the state machine, disable collision, patch art,
modify saves, merge code into main, or unlock Starbourne.

## Source change

`ATSTSSExplorerCharacter::Interact` preserves the existing single camera
visibility ray, the separate pawn-to-impact reach gate, and the exact
`Milestone->TryActivate` call. A default-off, nonshipping console variable
enables one diagnostic line after an actual E key press:

```text
tstss.FirstWake.InteractionTrace 1
```

Then interact with the next marker in a strictly disposable, source-and-map
guarded review scene. The native Unreal log line begins
`TSTSS_FIRST_WAKE_INTERACTION_DIAG`. It reports:

- `outcome`: `trace_disabled`, `visibility_miss`,
  `visibility_hit_non_milestone`, `outside_pawn_reach`,
  `story_or_repeat_rejected`, or `accepted`.
- Pawn and camera XYZ, camera forward vector, blocking hit actor/component,
  impact point, pawn-to-hit distance, max reach, before/after story beat.

A rejected story beat is *not* evidence of an occluder; an occluder is *not*
evidence of insufficient reach. A named hit actor can distinguish an old
Flyer marker from the `IoniaHiring` marker. Logs do not grant progression.

To turn tracing off again:
```text
tstss.FirstWake.InteractionTrace 0
```

## Required acceptance steps (not executed by this source-only change)

1. Leave the currently open user gameplay Editor entirely untouched. Do not
   build, hot-reload, restart, capture, or inject input into that session.
2. When no other Unreal Editor/Live Coding is active, use a fresh review
   sandbox with a **new guarded launcher**. Check current exact source SHA,
   protected config, old map and imported-asset hashes, no preexisting saves,
   6.5 GiB **physical** free RAM and 14 GiB disk reserve. Preserve the
   original protected `.umap`, binaries, evidence and saved games.
3. Run exact-head UE 5.8.4 Win64 build and native test suite; preserve
   command, runtime, JSON results, hashes and failures. Do not infer native
   proof from Python source tests.
4. Run one genuine D3D11 PIE session, capture per-press telemetry for
   `FlyerDiscovery -> IoniaHiring -> AureateBoarding`, plus a deliberate
   out-of-reach and blocked-object negative case. Inspect real screenshots
   and native log; bind all receipts to the source SHA and map digest.
5. If the ray hits the *wrong* actor or an occluder, inspect actual map
   collision and camera orientation before changing it. If the right actor
   is outside range, verify pawn/impact XYZ and distances before fixing
   placement. If in reach but state-rejected, inspect the beat and
   `TryActivate` path. **Do not weaken reach or story order to hide a miss.**
6. Only then create a separate minimally scoped *fix* and demonstrate the
   actual uninterrupted route in PIE, not just a successful source test.

## Current verification boundary

Source/test checks may run without opening a second resource-heavy Unreal
instance. No native build, newly instrumented PIE, finished Ionia hiring,
boarding, physical splashdown, UI/art approval, or ship collision proof is
claimed by this diagnostic-only branch. Starbourne remains locked.
