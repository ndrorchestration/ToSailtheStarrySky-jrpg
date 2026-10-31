# Aureate Wake → First Wake native integration boundary (2026-10-30)

**Status: dependency mapping and admission design only.** This document does not wire an Unreal level, execute physics, merge PRs, or authorize content.

## Verified source dependencies
- [Unreal bootstrap PR #608](https://github.com/ndrorchestration/ToSailtheStarrySky-jrpg/pull/608): `UTSTSSFirstWakeState`, `UTSTSSWaterLandingGate`, `UTSTSSPersistence`, combat rules/turn authority.
- [Ship geometry PR #610](https://github.com/ndrorchestration/ToSailtheStarrySky-jrpg/pull/610): `AAureateWakePreviewActor`, four wing components, two hydrofoils, optional Orbiter preview gate and material blend.
- [Canon PR #611](https://github.com/ndrorchestration/ToSailtheStarrySky-jrpg/pull/611): Ionia Captain, Reson Ace pilot, Ender/Aepex pairing, approved visual-reference boundaries.
- [Narrative PR #425](https://github.com/ndrorchestration/ToSailtheStarrySky-jrpg/pull/425), [Godot hiring PR #430](https://github.com/ndrorchestration/ToSailtheStarrySky-jrpg/pull/430), [splashdown PR #447](https://github.com/ndrorchestration/ToSailtheStarrySky-jrpg/pull/447): sources of sequence and observable test cases, **not code to merge directly**.
- [Godot combat PR #601](https://github.com/ndrorchestration/ToSailtheStarrySky-jrpg/pull/601): atomicity and rejection invariants; Unreal already has distinct transactional implementations.

## Ship-state / story-state isolation
| Player-visible event | Ship preview | Story authority | Rule |
| --- | --- | --- | --- |
| Flyer and Ionia hiring | Skyborne stationary | First Wake interaction | No ship form request can advance hiring |
| Boarding / checks | Skyborne | Authored player interactions | No automatic progression from rendering |
| Launch | Skyborne | Verified departure event | Animation alone cannot authorize Launched |
| Hull touches water | Transition to Seaborne may be requested for presentation | **UTSTSSWaterLandingGate** from physical hull/water observations | Form state must never emit SeaContact |
| Stable flotation | Seaborne visually stable | Gate requires observed water overlap and stable vertical speed over time | No arbitrary timer on visual tween |
| Reserve inspection | Seaborne | Player-driven inspection | No speculative fuel mechanics |
| Lyra/Talen introduction | Following splashdown | Narrative authority | No premature scene/recruitment |
| Submersible or Orbiter | Separate gated previews | Later, independent progression | Not unlocked by Chapter I |

## Proposed adapter (not yet coded)
A future `UAureateWakeStoryBridge` should **observe** vessel mode and current story stage without mutating either as a side effect. Only trusted authored collision/physics observer may invoke `UTSTSSWaterLandingGate::Observe`. Emit form-complete camera/audio feedback only after an accepted actor mode change. Do not place `bAllowOrbiterPreview` on player options in production; an editor-only debug actor can expose it.

## Ship-specific acceptance checks
1. On First Wake test map, intentionally request Seaborne in midair; assert `SeaContact` and `FlotationConfirmed` remain false.
2. Contact event without stable vertical motion must never confirm flotation; overlap loss resets timer.
3. After a genuine physics-derived flotation pass, the player can inspect depleted reserve without recruiting Lyra early.
4. Four dragonfly wings remain visible; Seaborne has hydrofoils; Submersible stows but does not erase wings; Orbiter has four equal radial sails and forward bridge.
5. Ship model must not be confused with the distinct larger Frigate-class **Dragonfly**. Avoid changing old lore text without separate review.
6. Persist ship *presentation mode* separately from story/progression state, with explicit save versioning and validation.

## Admission restrictions
The candidate work is not merged; no Windows UE 5.8 compilation, Editor playback, vessel-water collision integration, shader render, save/load, or creator art acceptance has been observed. Do not mark First Wake integrated until native evidence exists at a pinned commit.
