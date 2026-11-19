# Sea landing admission contract

The UE bootstrap currently prevents `ATSTSSMilestoneActor::TryActivate` from granting `SeaContact` or `FlotationConfirmed` via a generic E interaction. This was already present when inspected; do not duplicate that fix or claim it as newly implemented here.

The existing `UTSTSSFirstWakeState::AdvanceTo` still advances beats when called directly. Therefore this guard is not an authoritative proof of collision or buoyancy. Only a future physics event adapter, with actual ocean/vessel overlap, stable flotation sampling, and native Unreal negative tests, may establish landing evidence. The editor setup text that previously suggested placing generic sea-contact/flotation milestone actors is historical and must not be followed.

Reuse the Godot #547 landing contract and #600 story binding as specifications, not as native UE evidence. First compile the UE 5.8 bootstrap, then implement water contact using physics scene overlap and sustained stability, and capture an uninterrupted native launch-to-water-to-berth run.

Acceptance: no sea-contact or flotation from E interactions; no water-contact on a flying vessel; no flotation without sustained physically measured stability; resets upon exiting water; exact-head UE automation and captured gameplay. Keep these gates OPEN until native evidence exists.
