# Prelude → Chapter 1, Act 1: Splashdown boundary

**Story authority:** October 27 Ionia-first First Wake reboard, superseding historical Lyra-first opening. **Creator directive:** Splashdown opens Chapter 1, Act 1. Implementation candidate on isolated Unreal draft PR #608; not a native-tested build or visual approval.

## Continuity
1. Intro / Prelude: Ender seeks paid work; discovers Captain Ionia's harmonic-engine repair flyer; is hired; Ionia joins first.
2. Prelude: board Aureate Wake, inspect lift/phase, pressure/containment and reserve, sign off safe test.
3. Prelude: first flight is a genuine brief success; phase drift, containment strain and reserve depletion develop; Ionia commands an ocean landing.
4. Transition: real water contact **plus sustained flotation** recorded as `ETSTSSFirstWakeBeat::FlotationConfirmed`. This exact milestone completes the Prelude and starts **Chapter 1 — Act 1: Splashdown**.
5. Chapter 1, Act 1: inspect remaining reserves, establish safety/recovery and the seaworthy route, reunite with Lyra and noncombat Talen, then recruit Lyra second. Later: evidence collection and *unconfirmed* fuel theory. No instant fuel solution, no early Lyra aboard the flight.

## Source contract
- Existing numeric enum values and save schema version 2 remain unchanged. `UTSTSSFirstWakeState::IsPreludeComplete()` and `IsChapterOneActOne()` derive from the existing beat, requiring a started story and `FlotationConfirmed` or later.
- `SeaContact` alone does **not** start Chapter 1. Generic milestone interactions cannot create sea-contact or flotation evidence; the physics landing gate owns that transition.
- `EmptyReserveInspected` and `ReturnedToBerth` are *Chapter 1 recovery milestones*, even though they remain within the historical enum for backward compatibility.
- Restoring a valid v2 save at or beyond `FlotationConfirmed` exposes Chapter 1; reset/new game returns to Prelude. No retroactive rewrite of historical Godot/Unreal save payloads.
- Title card, level travel, crew/family, shoreline geography, native water physics and cinematic assets remain independent, unverified acceptance tasks.

## Native review gates
- First Wake ordered milestone test and chapter-boundary regression PASS at exact clean Win64 Unreal head.
- Full physical overlap, sustained float, no-collision/unstable-contact negative tests.
- PIE scene journey Ender → Ionia → launch → splashdown → Chapter 1 with readable HUD/title and player control restoration.
- Confirm save/load across precontact, sea contact and post-flotation; no premature Lyra, no superseded Lyra-first chapter flags; compare against approved cast and ship art.
- Do not merge/release until source, gameplay, cinematic render and Windows security acceptance are independently established.

Reference: https://app.notion.com/p/406f5bad238b81bcbacbeeb372e8fd77 and https://github.com/ndrorchestration/ToSailtheStarrySky-jrpg/pull/547
