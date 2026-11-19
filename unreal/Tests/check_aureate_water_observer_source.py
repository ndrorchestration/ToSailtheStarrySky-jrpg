#!/usr/bin/env python3
"""Fast source-structure guard, not an Unreal runtime/compile test."""
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
observer=(ROOT/"Source/ToSailTheStarrySky/Private/AureateWakeWaterObserverComponent.cpp").read_text()
ship=(ROOT/"Source/ToSailTheStarrySky/Private/AureateWakePreviewActor.cpp").read_text()
checks={
    "physics overlap sampled": "IsOverlappingComponent(WaterCollision)" in observer,
    "physical velocity sampled": "GetPhysicsLinearVelocity()" in observer and "GetComponentVelocity()" in observer and "IsSimulatingPhysics()" in observer,
    "nonfinite samples rejected": "FMath::IsFinite(VerticalSpeed)" in observer,
    "stale gate resets": observer.count("LandingGate->Reset()")>=3,
    "story gate evaluated before visual request": observer.find("LandingGate->Observe(")<observer.find("VisualShip->RequestForm("),
    "Seaborne requires accepted contact": "bContactAccepted && bTouchingWater" in observer and "AcceptedBeat == ETSTSSFirstWakeBeat::SeaContact" in observer,
    "preview does not advance story": "AdvanceTo(" not in ship,
    "preview preserves four wings": "Index < 4" in ship,
    "Orbiter remains gated": "bAllowOrbiterPreview" in ship,
}
for label,passed in checks.items():
    print(("PASS" if passed else "FAIL")+": "+label)
if not all(checks.values()):
    raise SystemExit(1)
print("SOURCE CONTRACT ONLY — Unreal compilation, actual overlap, flotation, and rendering unverified")
