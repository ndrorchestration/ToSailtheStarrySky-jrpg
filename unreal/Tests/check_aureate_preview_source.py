#!/usr/bin/env python3
"""Read-only source contract tests; NOT Unreal compile, rendering or art approval."""
from pathlib import Path

root = Path(__file__).resolve().parents[1]
source = (root / "Source/ToSailTheStarrySky/Private/AureateWakePreviewActor.cpp").read_text()
header = (root / "Source/ToSailTheStarrySky/Public/AureateWakePreviewActor.h").read_text()
generator = (root / "Tools/generate_aureate_wing.py").read_text()
checks = {
    "four persistent wings": "Index < 4" in source and "DragonflyWing_%d" in source,
    "two hydrofoils": "Index < 2" in source and "Hydrofoil_%d" in source,
    "seaborne foil deployment": "Form == EAureateWakeForm::Seaborne" in source,
    "submersible wing visibility": "Wings[Index]->SetVisibility(false)" not in source,
    "orbiter access gate": "bAllowOrbiterPreview = false" in header and "!bAllowOrbiterPreview" in source,
    "root-mounted wing geometry": "The mesh origin is the HINGE" in source
        and "Position = FVector(bForwardWing ? 155.f : -165.f, Side * 72.f, 45.f)" in source,
    "orbiter four hinge mounts": all(v in source for v in
        ("FVector(0, 0, 50)", "FVector(0, 0, -50)", "FVector(0, -78, 0)", "FVector(0, 78, 0)")),
    "orbiter all four radial rotations": all(v in source for v in
        ("FRotator(90.f, 0.f, 0.f)", "FRotator(-90.f, 0.f, 0.f)",
         "FRotator(0.f, -90.f, 0.f)", "FRotator(0.f, 90.f, 0.f)")),
    "equal orbiter sail scale": "Scale = FVector(3.6f, 1.15f, 1.f)" in source,
    "forward bridge not rotated": "ForwardBridge->SetRelativeTransform" not in source,
    "reject invalid enum": "static_cast<int32>(RequestedForm)" in source,
    "artist wing mesh binding": "TObjectPtr<UStaticMesh> AuthoredWingMesh" in header
        and "RefreshWingMeshes();" in source,
    "dynamic shader hookup": "TObjectPtr<UMaterialInterface> WingMaterial" in header
        and "OrbiterSailBlend" in source and "RefreshWingMaterials();" in source,
    "source asset generator": "class OBJ" in generator and "gold_spars" in generator,
    "no malformed literal backslash-newline": r"\n        Wings.Num()" not in source,
}
for name, passed in checks.items():
    print(f'{"PASS" if passed else "FAIL"}: {name}')
if not all(checks.values()):
    raise SystemExit(1)
print("Source checks passed; Unreal native compilation, editor import and render remain UNVERIFIED.")
