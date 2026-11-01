#!/usr/bin/env python3
"""Fail-closed, engine-free source guard for Aureate Wake review hydrofoil visibility.

This checker asserts reviewed C++ source contracts and mutates the source to
prove the guard detects representative regressions. It is NOT UE compilation,
native automation, mechanical clearance or a render.
"""
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
ACTOR = ROOT / "Source/ToSailTheStarrySky/Private/AureateWakePreviewActor.cpp"
TEST = ROOT / "Source/ToSailTheStarrySky/Private/Tests/AureateWakePreviewNativeTests.cpp"


def body(source: str, signature: str) -> str:
    if source.count(signature) != 1:
        raise ValueError(f"Missing or duplicated method: {signature}")
    start = source.index("{", source.index(signature))
    depth = 0
    for index in range(start, len(source)):
        if source[index] == "{":
            depth += 1
        elif source[index] == "}":
            depth -= 1
            if depth == 0:
                return source[start + 1:index]
    raise ValueError(f"Unclosed method: {signature}")


def require(pattern: str, source: str, label: str) -> None:
    if not re.search(pattern, source, flags=re.DOTALL):
        raise ValueError(label)


def verify(actor: str, native_test: str) -> None:
    request = body(actor, "bool AAureateWakePreviewActor::RequestForm(")
    snap = body(actor, "void AAureateWakePreviewActor::SnapToForm(")
    tick = body(actor, "void AAureateWakePreviewActor::Tick(")
    supports = body(actor, "void AAureateWakePreviewActor::UpdateHydrofoilStruts(")
    routes = body(native_test, "bool FTSTSSAureateSixRouteSupportReviewTest::RunTest(")

    # Do not inadvertently display hydrofoils during an ordinary-form route
    # that neither starts nor ends at Seaborne.
    require(
        r"const\s+bool\s+bReviewFoilsInMotion\s*=\s*"
        r"CurrentForm\s*==\s*EAureateWakeForm::Seaborne\s*\|\|\s*"
        r"RequestedForm\s*==\s*EAureateWakeForm::Seaborne\s*;",
        request, "Seaborne-only transition predicate missing")
    require(
        r"Hydrofoils\[Index\]->SetVisibility\(bReviewFoilsInMotion\)",
        request, "Hydrofoil visibility is not guarded by Seaborne endpoints")
    require(
        r"bUseRootPivotedWingPose\s*&&\s*"
        r"\(RequestedForm\s*==\s*EAureateWakeForm::Orbiter\s*\|\|\s*"
        r"CurrentForm\s*==\s*EAureateWakeForm::Orbiter\)",
        request, "Authored-wing Orbiter safety hold removed")
    for name in ("UpdateWingRootMounts();", "UpdateHydrofoilStruts();"):
        if name not in request or request.index(name) < request.index("bTransitioning = true;"):
            raise ValueError(f"Immediate review support update missing: {name}")

    require(r"Hydrofoils\[Index\]->SetVisibility\(\s*"
            r"Form\s*==\s*EAureateWakeForm::Seaborne\s*\)",
            snap, "Terminal form should only display Seaborne hydrofoils")
    require(r"UpdateHydrofoilStruts\(\s*\)", snap,
            "Terminal support visibility refresh missing")
    require(r"UpdateHydrofoilStruts\(\s*\)", tick,
            "Mid-transition support update missing")
    require(r"!Hydrofoils\[Index\]->IsVisible\(\)", supports,
            "Support visibility must follow foil visibility")
    require(r"Strut->SetVisibility\(false\)", supports,
            "Missing hidden-support path")

    # Test must cover all 3*2 directed ordinary routes, with both transition
    # endpoints, midpoint and end-state assertions and a continuing Orbiter hold.
    require(r"EAureateWakeForm::Skyborne\s*,\s*"
            r"EAureateWakeForm::Seaborne\s*,\s*"
            r"EAureateWakeForm::Submersible", routes,
            "Ordinary form test matrix incomplete")
    require(r"if\s*\(Start\s*==\s*Target\)\s*continue\s*;", routes,
            "Test no longer excludes same-form routes")
    require(r"RoutesCompleted\s*,\s*6\s*\)", routes,
            "Six directed routes not asserted")
    require(r"const\s+bool\s+bFoilsExpected\s*=\s*"
            r"Start\s*==\s*EAureateWakeForm::Seaborne\s*\|\|\s*"
            r"Target\s*==\s*EAureateWakeForm::Seaborne", routes,
            "Test does not model both Seaborne endpoints")
    for assertion in (
        "Foil starts visible only for a Seaborne route",
        "Strut follows foil on the same transition frame",
        "Hydrofoil visibility at route midpoint",
        "Hydrofoil strut visibility at route midpoint",
        "Terminal hydrofoil visible only in Seaborne",
        "Terminal support strut visible only in Seaborne",
        "Orbiter blocked at ordinary destination",
    ):
        if assertion not in routes:
            raise ValueError(f"Required native review assertion absent: {assertion}")


def replace_one(source: str, old: str, new: str) -> str:
    if source.count(old) != 1:
        raise ValueError(f"Could not uniquely locate mutation target: {old}")
    return source.replace(old, new)


def main() -> int:
    actor = ACTOR.read_text(encoding="utf-8")
    native_test = TEST.read_text(encoding="utf-8")
    verify(actor, native_test)
    mutants = [
        (replace_one(actor,
                     "Hydrofoils[Index]->SetVisibility(bReviewFoilsInMotion)",
                     "Hydrofoils[Index]->SetVisibility(true)"), native_test),
        (replace_one(actor,
                     "RequestedForm == EAureateWakeForm::Seaborne;",
                     "RequestedForm == EAureateWakeForm::Skyborne;"), native_test),
        (replace_one(actor, "Form == EAureateWakeForm::Seaborne);",
                     "Form != EAureateWakeForm::Orbiter);"), native_test),
        (actor, replace_one(native_test, "RoutesCompleted, 6)", "RoutesCompleted, 4)")),
        (actor, replace_one(native_test,
                            "Hydrofoil visibility at route midpoint",
                            "Hydrofoil visibility (missing midpoint assertion)")),
    ]
    for index, (changed_actor, changed_test) in enumerate(mutants, start=1):
        try:
            verify(changed_actor, changed_test)
        except ValueError:
            continue
        raise ValueError(f"Regression mutation {index} passed unexpectedly")
    print("PASS: Seaborne-only foil and support source contract plus 5 negative mutants")
    print("Source-only; no native Unreal execution, collision proof or render")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, ValueError) as error:
        print(f"FAIL: {error}", file=sys.stderr)
        raise SystemExit(1)
