#!/usr/bin/env python3
"""Advisory source-bound hydrofoil strut geometry review (NO Unreal runtime).

Parse a pinned C++ review actor's exact literal transforms and safeguards, then
calculate endpoint alignment only in UE centimeters. Not 3D collision, geometry
clearance, source-independent implementation proof or artist signoff.
"""
import argparse
import hashlib
import json
import math
import re
from pathlib import Path

PINNED_SOURCE_HEAD = "77ee249f8a0d734eab165dcafcd16870f12f07a7"
PINNED_BLOB_SHA1 = "27733525db404b0458db53bd1f5af1b0edad7f2c"
SOURCE_PATH = "unreal/Source/ToSailTheStarrySky/Private/AureateWakePreviewActor.cpp"

def git_blob_sha(raw):
    return hashlib.sha1(b"blob " + str(len(raw)).encode("ascii") + b"\0" + raw).hexdigest()

def body(text, start, end):
    a = text.find(start)
    b = text.find(end, a + len(start)) if a >= 0 else -1
    if a < 0 or b < 0:
        raise ValueError("review method boundary missing")
    return text[a:b]

def must_have(text, patterns):
    for label, pattern in patterns.items():
        if not re.search(pattern, text, re.DOTALL):
            raise ValueError("missing/modified source invariant: " + label)

def audit_semantics(text):
    foil = body(text, "FTransform AAureateWakePreviewActor::FoilPose(",
                "FTransform AAureateWakePreviewActor::Interpolate(")
    strut = body(text, "void AAureateWakePreviewActor::UpdateHydrofoilStruts()",
                 "void AAureateWakePreviewActor::SnapToForm(")
    snap = body(text, "void AAureateWakePreviewActor::SnapToForm(",
                "bool AAureateWakePreviewActor::RequestForm(")
    request = body(text, "bool AAureateWakePreviewActor::RequestForm(",
                   "bool AAureateWakePreviewActor::FinishOrdinaryPreviewTransitionForReview(")
    tick = body(text, "void AAureateWakePreviewActor::Tick(", "\n}") + "\n}"
    must_have(foil, {
        "foil-side": r"FoilIndex\s*==\s*0\s*\?\s*-1\.f\s*:\s*1\.f",
        "seaborne-only": r"bDeployed\s*=\s*Form\s*==\s*EAureateWakeForm::Seaborne",
        "foil-position": r"FVector\(\s*0\s*,\s*Side\s*\*\s*80\.f\s*,\s*bDeployed\s*\?\s*-140\.f\s*:\s*-45\.f\s*\)",
        "foil-proxy-scale": r"FVector\(\s*2\.1f\s*,\s*0\.75f\s*,\s*0\.10f\s*\)",
    })
    must_have(strut, {
        "two-source-components": r"Index\s*<\s*HydrofoilStruts\.Num\(\)",
        "foil-exists-and-visible": r"Hydrofoils\.IsValidIndex\(Index\).*?!Hydrofoils\[Index\]->IsVisible\(\)",
        "absent-foil-hides-strut": r"Strut->SetVisibility\(false\)",
        "strut-side": r"Index\s*==\s*0\s*\?\s*-1\.f\s*:\s*1\.f",
        "hull-anchor": r"FVector\s+HullAnchor\(\s*0\.f\s*,\s*Side\s*\*\s*60\.f\s*,\s*-30\.f\s*\)",
        "span-difference": r"Span\s*=\s*FoilPosition\s*-\s*HullAnchor",
        "midpoint": r"SetRelativeLocation\(\s*\(HullAnchor\s*\+\s*FoilPosition\)\s*\*\s*\.5f\s*\)",
        "x-axis-align": r"SetRelativeRotation\(\s*Span\.ToOrientationQuat\(\)\s*\)",
        "unit-length-scale": r"SetRelativeScale3D\(\s*FVector\(\s*Length\s*/\s*100\.f\s*,\s*\.12f\s*,\s*\.12f\s*\)\s*\)",
        "nonzero-span-hides": r"SetVisibility\(Length\s*>\s*KINDA_SMALL_NUMBER\)",
    })
    must_have(snap, {
        "snap-foils-visible-only-seaborne": r"Hydrofoils\[Index\]->SetVisibility\(Form\s*==\s*EAureateWakeForm::Seaborne\)",
        "snap-updates-struts": r"UpdateHydrofoilStruts\(\)",
    })
    must_have(request, {
        "transition-foils-visible": r"Hydrofoils\[Index\]->SetVisibility\(true\)",
        "authored-orbiter-refused": r"bUseRootPivotedWingPose\s*&&\s*\(RequestedForm\s*==\s*EAureateWakeForm::Orbiter\s*\|\|\s*CurrentForm\s*==\s*EAureateWakeForm::Orbiter\)",
        "orbiter-review-gate": r"RequestedForm\s*==\s*EAureateWakeForm::Orbiter\s*&&\s*!bAllowOrbiterPreview",
    })
    must_have(tick, {"transition-updates-struts": r"UpdateHydrofoilStruts\(\)"})
    # The provisional hull uses Unreal's 100cm basic cube, with scale y=1.5
    # and z=.65. Its +/- 75cm and +/- 32.5cm are review assumptions, not art.
    results = []
    for side in (-1, 1):
        hull = (0.0, side * 60.0, -30.0)
        foil_point = (0.0, side * 80.0, -140.0)
        span = tuple(f - h for h, f in zip(hull, foil_point))
        length = math.sqrt(sum(x*x for x in span))
        midpoint = tuple((h+f)/2 for h,f in zip(hull, foil_point))
        assert length > 0
        assert abs(midpoint[2] + 85.0) < 1e-9
        results.append({
            "side": "port_negative_y" if side == -1 else "starboard_positive_y",
            "hull_anchor_cm": list(hull),
            "foil_center_cm": list(foil_point),
            "strut_center_cm": list(midpoint),
            "strut_span_cm": round(length, 6),
            "strut_x_scale": round(length / 100, 6),
            "hull_anchor_within_basic_cube_proxy_yz": (
                abs(hull[1]) <= 75 and abs(hull[2]) <= 32.5),
            "support_endpoints_aligned_to_declared_centers": True,
        })
    return {
        "source_head": PINNED_SOURCE_HEAD,
        "source_path": SOURCE_PATH,
        "evidence_class": "PINNED_SOURCE_LITERAL_AND_PROXY_ENDPOINT_ARITHMETIC_ONLY",
        "seaborne": results,
        "hydrofoil_strut_count_from_constructor": "NEEDS_NATIVE_CHECK",
        "observed_ue_mesh_bounds": "NOT_OBSERVED",
        "continuous_motion_collision": "NOT_VERIFIED",
        "struts_visible_in_native_d3d12": "NOT_VERIFIED",
        "art_authority": "NOT_APPROVED",
        "orbiter": "FAIL_CLOSED_SOURCE_GUARDS_PRESENT",
    }

def check_pinned_file(raw):
    # Windows Git may materialize a text blob with CRLF (core.autocrlf=true).
    # Accept ONLY exact LF byte identity or canonical CRLF->LF conversion.
    # Reject stray CR and content modifications, preserving the raw digest.
    original = raw
    line_endings = "EXACT_LF"
    if b"\r" in raw:
        if b"\r" in raw.replace(b"\r\n", b""):
            raise ValueError("mixed or unsupported CR line endings")
        raw = raw.replace(b"\r\n", b"\n")
        line_endings = "GIT_WINDOWS_CRLF_NORMALIZED"
    blob = git_blob_sha(raw)
    if blob != PINNED_BLOB_SHA1:
        raise ValueError("source blob is not the pinned PR #656 actor; refuse to extrapolate")
    return dict(audit_semantics(raw.decode("utf-8")),
                source_blob_sha1=blob,
                local_source_raw_sha256=hashlib.sha256(original).hexdigest(),
                local_line_endings=line_endings)

def self_test():
    # Isolate the source grammar and math using a tiny synthetic C++ excerpt,
    # not a real native mesh or source-verification substitute.
    sample = """FTransform AAureateWakePreviewActor::FoilPose(
FoilIndex == 0 ? -1.f : 1.f;
bDeployed = Form == EAureateWakeForm::Seaborne;
FVector(0, Side * 80.f, bDeployed ? -140.f : -45.f);
FVector(2.1f, 0.75f, 0.10f);
FTransform AAureateWakePreviewActor::Interpolate(
void AAureateWakePreviewActor::UpdateHydrofoilStruts()
Index < HydrofoilStruts.Num()
Hydrofoils.IsValidIndex(Index) || !Hydrofoils[Index]->IsVisible()
Strut->SetVisibility(false);
Index == 0 ? -1.f : 1.f;
const FVector HullAnchor(0.f, Side * 60.f, -30.f);
Span = FoilPosition - HullAnchor;
Strut->SetRelativeLocation((HullAnchor + FoilPosition) * .5f);
Strut->SetRelativeRotation(Span.ToOrientationQuat());
Strut->SetRelativeScale3D(FVector(Length / 100.f, .12f, .12f));
Strut->SetVisibility(Length > KINDA_SMALL_NUMBER);
void AAureateWakePreviewActor::SnapToForm(
Hydrofoils[Index]->SetVisibility(Form == EAureateWakeForm::Seaborne);
UpdateHydrofoilStruts();
bool AAureateWakePreviewActor::RequestForm(
Hydrofoils[Index]->SetVisibility(true);
(bUseRootPivotedWingPose && (RequestedForm == EAureateWakeForm::Orbiter || CurrentForm == EAureateWakeForm::Orbiter))
(RequestedForm == EAureateWakeForm::Orbiter && !bAllowOrbiterPreview)
bool AAureateWakePreviewActor::FinishOrdinaryPreviewTransitionForReview(
void AAureateWakePreviewActor::Tick(
UpdateHydrofoilStruts();
}
"""
    result = audit_semantics(sample)
    assert len(result["seaborne"]) == 2
    assert all(x["hull_anchor_within_basic_cube_proxy_yz"] for x in result["seaborne"])
    assert abs(result["seaborne"][0]["strut_span_cm"] - 111.803399) < 1e-5
    variants = [
        sample.replace("Side * 60.f", "Side * 90.f"),
        sample.replace("Length / 100.f", "Length / 80.f"),
        sample.replace("Span.ToOrientationQuat()", "Span.ToOrientationRotator()"),
        sample.replace("Hydrofoils[Index]->IsVisible()", "Hydrofoils[Index]->WasRecentlyRendered()"),
        sample.replace("UpdateHydrofoilStruts();", "", 1),
        sample.replace("!bAllowOrbiterPreview", "false"),
        sample.replace("bDeployed ? -140.f", "bDeployed ? -110.f"),
        sample.replace("Strut->SetVisibility(false)", "Strut->SetVisibility(true)"),
    ]
    for variant in variants:
        try:
            audit_semantics(variant)
        except ValueError:
            continue
        raise AssertionError("synthetic geometry/authorization mutant accepted")
    try:
        check_pinned_file(sample.encode("utf-8"))
    except ValueError:
        pass
    else:
        raise AssertionError("unpinned test source accepted as real PR")
    crlf_fixture = b"one\r\ntwo\r\n"
    assert git_blob_sha(crlf_fixture.replace(b"\r\n", b"\n")) == git_blob_sha(b"one\ntwo\n")
    mixed = crlf_fixture + b"stray\rno"
    assert b"\r" in mixed.replace(b"\r\n", b"")
    print("PASS: synthetic two-sided math, 8 source mutations, pin rejection, CRLF normalization controls")

def main():
    p = argparse.ArgumentParser()
    p.add_argument("actor_cpp", nargs="?")
    p.add_argument("--self-test", action="store_true")
    a = p.parse_args()
    if a.self_test:
        self_test()
        return
    if not a.actor_cpp:
        p.error("exact pinned PR #656 C++ file required")
    try:
        result = check_pinned_file(Path(a.actor_cpp).read_bytes())
    except (ValueError, OSError) as exc:
        print(json.dumps({"status":"NOT_VERIFIED", "reason":str(exc)}))
        raise SystemExit(1)
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    main()
