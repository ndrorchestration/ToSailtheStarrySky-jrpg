#!/usr/bin/env python3
"""Read-only source contract checks. NOT a replacement for UE compiler or renderer tests."""
from pathlib import Path
import re
root = Path(__file__).resolve().parents[1]
source = (root / "Source/ToSailTheStarrySky/Private/AureateWakePreviewActor.cpp").read_text()
header = (root / "Source/ToSailTheStarrySky/Public/AureateWakePreviewActor.h").read_text()
checks = {
    "four persistent wings": 'Index < 4' in source and 'DragonflyWing_%d' in source,
    "two hydrofoils": 'Index < 2' in source and 'Hydrofoil_%d' in source,
    "seaborne foil deployment": 'Form == EAureateWakeForm::Seaborne' in source,
    "submersible wing visibility": 'case EAureateWakeForm::Submersible:' in source and 'Wings[Index]->SetRelativeTransform(WingPoseForMesh(Form, Index))' in source and not re.search(r'\b(?:Wing|Wings\[[^\]]+\])\s*->\s*SetVisibility\(\s*false\s*\)', source),
    "four additional *supports*, not wings": 'WingRootSupports.Add(Support);' in source and 'Wings.Add(Wing);' in source and 'GetRootSupportCount()' in header,
    "orbiter access gate": 'bAllowOrbiterPreview = false' in header and '!bAllowOrbiterPreview' in source,
    "cardinal orbiter offsets": all(fragment in source for fragment in ['FVector(0, 0, 315)', 'FVector(0, 0, -315)', 'FVector(0, -315, 0)', 'FVector(0, 315, 0)']),
    "vertical sails pitched": 'FRotator(90.f, 0.f, 0.f)' in source,
    "equal orbiter sail scales": 'Scale = FVector(2.5f, 1.7f, 0.055f)' in source,
    "bridge not transformed in Tick": 'ForwardBridge->SetRelativeTransform' not in source,
    "reject invalid enum": 'static_cast<int32>(RequestedForm)' in source,
}
for name, success in checks.items():
    print(f'{"PASS" if success else "FAIL"}: {name}')
if not all(checks.values()):
    raise SystemExit(1)
print("Source contracts passed. UE compile/render NOT verified.")
