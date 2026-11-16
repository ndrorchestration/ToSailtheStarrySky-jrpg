# First Wake C-key reach telemetry — source-only diagnostics

**Date:** 2026-11-15
**Status:** REVIEW-ONLY / SOURCE-TESTED / NATIVE UE BUILD & ACTUAL C-KEY PIE NOT TESTED
**Source parent:** draft PR #841 `eb9211ec053398153238721099bc6c09894308cc`, itself stacked on draft PR #838. No merges or game asset changes.

## Problem and why this matters

The earned V5 route has actual native evidence for seven E interactions, K transfer to the Aureate Wake VS02 map and O transfer into the optional optical review copy. Its C attempt failed with a generic "stand near LIFT" HUD warning. The original authored player start occupies the large BridgeDeck solid cube; parent PR #841 provides a conservative source-only route proposal to a spot within the actual 450 cm LIFT proximity gate. However, the old native log did not record player world XYZ, gauge XYZ, measured distance or which scene/ownership gate rejected the attempt. A later capsule component *relative* location must not be mistaken for pawn world position.

## What this branch actually implements

Only the existing editor-only `ATSTSSExplorerCharacter::ToggleEngineFocusPreview()` and `RestoreEngineFocusPreview()` acquire passive `UE_LOG(LogTemp, Display, ...)` diagnostics. The code still checks `World->WorldType == EWorldType::PIE`, the exact original LIFT name, unique atmosphere owner, unchanged C-key radius 450cm, actual engineering story/weather authorization, camera/view owner, existing movement/look ownership and borrowed cinematic coordinator before a camera may be created.

- `TSTSS_PIE_GAMEPLAY_ENGINE_FOCUS_RANGE` logs true **pawn actor world XYZ**, real LIFT gauge world XYZ, measured 3D distance, 450cm limit, LIFT actor count and atmosphere owner count for each eligible C attempt.
- `TSTSS_PIE_GAMEPLAY_ENGINE_FOCUS_GATE` differentiates controller/input ownership, invalid instrument/range, another cinematic owner and story/weather access. It does not grant authorization or move the pawn.
- `TSTSS_PIE_GAMEPLAY_ENGINE_FOCUS_ENTER` retains the known marker and adds focus distance, current instrument distance, a four-second expiry and two input-lock observations *after* they are set.
- `TSTSS_PIE_GAMEPLAY_ENGINE_FOCUS_RESTORE_AUDIT` logs engine elapsed time, immediate movement/look ignore state and current camera target at restore time. Because Unreal blends the view back for 0.3s, immediate pawn camera ownership is **not** final camera verification. The existing `TSTSS_PIE_GAMEPLAY_ENGINE_FOCUS_RESTORE` marker is preserved.

The editor-only diagnostic is passive: no SaveGame write, 3D teleport, actor spawn, player input remapping, camera exposure change, multiplayer scene authority, actual combat/spell change, approved art or story advancement. The No-PIE return and C-only user action are unchanged. It will still require a native C++ build against UE 5.8.4; source tests are not compilation proof.

## Verification and limitations

`unreal/Tools/verify_engine_focus_reach_pie_log.py` parses real Unreal timestamped `LogTemp` records and requires:
- Seven ordered real `TSTSS_PIE_REVIEW_E_ACCEPT` targets.
- K to original VS02, engineering beat 3 arrival, O to nonshipping optical map, engineering beat 3 restored.
- Logged real LIFT at (−250,−250,270) cm, exactly one gauge and one sky owner, and consistent 3D pawn-to-gauge distance ≤450cm.
- One native C enter after the range check; correct original 65mm/f2.8 framing distance ~796.6cm; movement and look ignored on entering.
- One return after approximately four seconds with native elapsed and wall time agreeing, active controller and unlocked movement/look. The parser expressly leaves actual physical WASD, final camera blend and GPU bokeh proof marked FALSE.

Synthetic mutation tests reject changed actors, spoofed distances, over-range location, shifted optics/limit, duplicate acceptance, wrong story beats, wrong map travel, early/manual returns and leaked input locks. A real historical failed native PIE log from PR #838 was run against this parser and correctly returned `HOLD: expected 1 ENTER event(s), got 0`. **This is a negative result, not native success.**

## Native acceptance remains HOLD

Neontic's separate PR #838 UnrealEditor PID 19268 and LiveCodingConsole PID 7176 were still active on 2026-11-15 around 21:23 ET, and free physical RAM was ~3.99 GiB (< 6.5 GiB native threshold). This branch does not terminate or use the other owner's live session. The engine-resident fixed BridgeDeck remains unapplied, original VS02 SHA256 `a97fbb057cb87c0e35fe95195ca06c30de1a5cc60158bf31a657f738b22a9d69`, existing optical copy SHA256 `06f006b42d54a990ffefa5903bda0d24e34259a424c1f6bee4a51a29f0766223`.

After safety admission, implement the one-actor nonshipping bridge fix in PR #841 with independent native map readback; then native compile and run actual PIE E→K→O→WASD→C, record the real 4-second camera return, verify physical player input and native D3D11/D3D12 Lit scene captures. The parser's positive synthetic tests must never be represented as a passed real keyboard, native build, bokeh, accessibility, or creator approval gate.

Preserve Starbourne fail-closed, post-splashdown Seabourne plot lock, Ender/Ionia/Lyra slice availability, and the ship's first-journey story authority.
