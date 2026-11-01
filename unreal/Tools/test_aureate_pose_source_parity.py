#!/usr/bin/env python3
"""Fail closed when the Unreal root-pivot review pose diverges from the offline audit.

An intentionally explicit, reviewed source snapshot is more conservative than
accepting a few constants: ANY expression change requires independent review
of the matching Python clearance model. Whitespace/comment-only edits are ignored.
This source guard is NOT equivalent to running the Unreal implementation.
"""
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
CPP = ROOT / "Source/ToSailTheStarrySky/Private/AureateWakePreviewActor.cpp"
SIGNATURE = "FTransform AAureateWakePreviewActor::RootPivotedWingPose("
EXPECTED_CPP_SOURCE = "constboolbForward=WingIndex<2;constfloatSide=WingIndex%2==0?-1.f:1.f;constfloatRootX=bForward?155.f:-180.f;constfloatRootY=Side*112.f;FVectorPosition(RootX,RootY,48.f);FRotatorRotation;FVectorScale(1.f,1.f,1.f);switch(Form){caseEAureateWakeForm::Skyborne:Rotation=FRotator(0.f,Side*(bForward?80.f:100.f),Side*7.f);break;caseEAureateWakeForm::Seaborne:Position.Z=82.f;Rotation=FRotator(32.f,Side*(bForward?75.f:105.f),Side*50.f);Scale=FVector(.94f,.82f,1.f);break;caseEAureateWakeForm::Submersible:Position.Z=16.f;Rotation=FRotator(0.f,Side*(bForward?23.f:157.f),Side*72.f);Scale=FVector(.78f,.38f,.95f);break;caseEAureateWakeForm::Orbiter:Scale=FVector(1.f,1.f,1.f);if(WingIndex==0){Position=FVector(0.f,0.f,130.f);Rotation=FRotator(90.f,0.f,0.f);}elseif(WingIndex==1){Position=FVector(0.f,0.f,-130.f);Rotation=FRotator(-90.f,0.f,0.f);}elseif(WingIndex==2){Position=FVector(0.f,-130.f,0.f);Rotation=FRotator(0.f,-90.f,0.f);}else{Position=FVector(0.f,130.f,0.f);Rotation=FRotator(0.f,90.f,0.f);}break;}returnFTransform(Rotation,Position,Scale);"


def extract_cpp_method(source: str) -> str:
    if source.count(SIGNATURE) != 1:
        raise ValueError("RootPivotedWingPose is absent or ambiguous")
    begin = source.index("{", source.index(SIGNATURE))
    depth = 0
    for position in range(begin, len(source)):
        if source[position] == "{":
            depth += 1
        elif source[position] == "}":
            depth -= 1
            if depth == 0:
                return source[begin + 1:position]
    raise ValueError("RootPivotedWingPose braces are unbalanced")


def normalize(source: str) -> str:
    return re.sub(r"\s+", "", re.sub(r"//[^\r\n]*", "", source))


def assert_pose_parity(source: str) -> None:
    observed = normalize(extract_cpp_method(source))
    if observed != EXPECTED_CPP_SOURCE:
        raise ValueError(
            "C++ root-pivot wing poses diverged from reviewed offline audit; "
            "update/independently validate pose matrix before clearing GLB intake"
        )


def test_auditor_pose_matrix():
    # Import only in the executable self-test path; the clearance auditor
    # imports assert_pose_parity without importing itself recursively.
    from audit_aureate_wing_clearance import pose
    forms = ("Skyborne", "Seaborne", "Submersible")
    verified = 0
    for form in forms:
        for index in range(4):
            front = index < 2
            side = -1 if index % 2 == 0 else 1
            xyz, angles, scale = pose(form, index)
            expected_x = 155. if front else -180.
            expected_y = side * 112.
            expected_z = {"Skyborne": 48., "Seaborne": 82.,
                          "Submersible": 16.}[form]
            expected_angles = {
                "Skyborne": (0., side * (80. if front else 100.), side * 7.),
                "Seaborne": (32., side * (75. if front else 105.), side * 50.),
                "Submersible": (0., side * (23. if front else 157.), side * 72.),
            }[form]
            expected_scale = {
                "Skyborne": (1., 1., 1.),
                "Seaborne": (.94, .82, 1.),
                "Submersible": (.78, .38, .95),
            }[form]
            if (xyz != (expected_x, expected_y, expected_z)
                or angles != expected_angles or scale != expected_scale):
                raise ValueError(f"Offline pose matrix drift: {form} wing {index}")
            verified += 1
    return verified


def self_test():
    current = CPP.read_text(encoding="utf-8")
    assert_pose_parity(current)
    mutants = (
        ("const float RootY = Side * 112.f;",
         "const float RootY = Side * 114.f;"),
        ("Position.Z = 82.f;", "Position.Z = 84.f;"),
        ("Rotation = FRotator(0.f, Side * (bForward ? 80.f : 100.f), Side * 7.f);",
         "Rotation = FRotator(0.f, Side * (bForward ? 90.f : 100.f), Side * 7.f);"),
        ("Scale = FVector(.78f, .38f, .95f);",
         "Scale = FVector(.78f, .48f, .95f);"),
        ("Position = FVector(0.f, 130.f, 0.f);",
         "Position = FVector(0.f, 140.f, 0.f);"),
    )
    for number, (old, new) in enumerate(mutants, 1):
        if current.count(old) != 1:
            raise ValueError(f"Mutation fixture {number} is no longer unique")
        try:
            assert_pose_parity(current.replace(old, new, 1))
        except ValueError:
            pass
        else:
            raise ValueError(f"Source pose mutation {number} was not rejected")
    # A comment-only change must not trigger a review hold.
    commented = current.replace(
        "FTransform AAureateWakePreviewActor::RootPivotedWingPose(",
        "// Offline parity guard: whitespace/comment differences permitted.\n"
        "FTransform AAureateWakePreviewActor::RootPivotedWingPose(", 1)
    assert_pose_parity(commented)
    checked = test_auditor_pose_matrix()
    if checked != 12:
        raise ValueError("Incomplete reviewed Python pose matrix")
    print(f"PASS: exact normalized C++ pose contract; {checked} Python endpoints; "
          f"{len(mutants)} mutation negatives")
    print("ENGINE-FREE source parity only; not Unreal native or continuous collision")


if __name__ == "__main__":
    try:
        self_test()
    except (ValueError, OSError) as exc:
        print("FAIL: " + str(exc), file=sys.stderr)
        raise SystemExit(1)
