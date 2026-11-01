#!/usr/bin/env python3
"""Derive public-safe ordinal claims from measurements; NOT canon approval.

This adapter accepts native-claimed data as assertions, not authenticated evidence.
All synthetic data is strictly labelled synthetic. Missing/tied values -> UNKNOWN.
"""
import argparse
import json
import math
import re
from pathlib import Path

NAMES = ("Reson", "Aepex", "Ender", "Ionia", "Lyra")
SHIP_KEYS = (
    "skyborne_wings", "seaborne_hydrofoils",
    "submersible_folded_wings_visible", "orbiter_request_permitted",
)
MEASUREMENT_KEYS = ("height_cm", "starting_mp", "starting_hp", "ship")
KINDS = {"synthetic", "native_receipt", "not_observed"}

def ranked(measurements, *, descending):
    if not isinstance(measurements, dict) or set(measurements) != set(NAMES):
        return None
    values = []
    for name in NAMES:
        value = measurements[name]
        if type(value) not in (int, float) or not math.isfinite(value) or value <= 0:
            return None
        values.append(value)
    if len(set(values)) != len(NAMES):
        return None  # Ties do not determine an exact order.
    return sorted(NAMES, key=lambda n: measurements[n], reverse=descending)

def derive(receipt):
    if not isinstance(receipt, dict) or receipt.get("schema_version") != 1:
        raise ValueError("expected schema_version=1 object")
    kind = receipt.get("source_kind")
    if kind not in KINDS:
        raise ValueError("unsupported source_kind")
    raw = receipt.get("measurements")
    if not isinstance(raw, dict) or set(raw) - set(MEASUREMENT_KEYS):
        raise ValueError("unknown or malformed measurement keys")
    if kind == "not_observed" and raw:
        raise ValueError("not_observed must have empty measurements")
    if kind == "native_receipt":
        sha = receipt.get("source_sha", "")
        if not isinstance(sha, str) or not re.fullmatch(r"[a-f0-9]{40}", sha):
            raise ValueError("native receipt requires exact git source SHA")
        if not isinstance(receipt.get("evidence_location"), str) or not receipt["evidence_location"].strip():
            raise ValueError("native receipt requires evidence_location")
    observations = {}
    height = ranked(raw.get("height_cm"), descending=True)
    if height is not None:
        observations["height_order"] = height
    mp = ranked(raw.get("starting_mp"), descending=True)
    if mp is not None:
        observations["starting_mp_top_two"] = mp[:2]
    hp = ranked(raw.get("starting_hp"), descending=False)
    if hp is not None:
        observations["starting_hp_bottom_two"] = hp[:2]
    ship = raw.get("ship")
    if ship is not None:
        if not isinstance(ship, dict) or set(ship) - set(SHIP_KEYS):
            raise ValueError("ship observations must use allowed keys")
        for key in SHIP_KEYS:
            if key not in ship:
                continue
            v = ship[key]
            if key in ("skyborne_wings", "seaborne_hydrofoils"):
                if type(v) is not int or v < 0:
                    raise ValueError("invalid ship component count")
            elif type(v) is not bool:
                raise ValueError("visibility / gate observations must be boolean")
            observations[key] = v
    return {
        "schema_version": 1,
        "source_kind": kind,
        "observations": observations,
        **({k: receipt[k] for k in ("source_sha", "evidence_location")}
           if kind == "native_receipt" else {}),
    }

def self_test():
    # Arbitrary numbers are synthetic test data, NEVER approved canonical stats.
    base = {"schema_version": 1, "source_kind": "synthetic", "measurements": {
        "height_cm": dict(zip(NAMES, (190, 182, 176, 168, 160))),
        "starting_mp": {"Ender": 60, "Lyra": 50, "Ionia": 30, "Reson": 10, "Aepex": 20},
        "starting_hp": {"Lyra": 40, "Ender": 50, "Ionia": 60, "Reson": 90, "Aepex": 80},
        "ship": {"skyborne_wings": 4, "seaborne_hydrofoils": 2,
                 "submersible_folded_wings_visible": True,
                 "orbiter_request_permitted": False},
    }}
    result = derive(base)["observations"]
    assert result["height_order"] == list(NAMES)
    assert result["starting_mp_top_two"] == ["Ender", "Lyra"]
    assert result["starting_hp_bottom_two"] == ["Lyra", "Ender"]
    assert len(result) == 7
    tie = json.loads(json.dumps(base))
    tie["measurements"]["height_cm"]["Lyra"] = 168
    assert "height_order" not in derive(tie)["observations"]
    missing = json.loads(json.dumps(base))
    del missing["measurements"]["starting_hp"]["Lyra"]
    assert "starting_hp_bottom_two" not in derive(missing)["observations"]
    for field, value in (("starting_hp", {"Lyra": float("nan")}),
                         ("height_cm", {"Lyra": True})):
        test = json.loads(json.dumps(base))
        test["measurements"][field].update(value)
        assert (field == "starting_hp_bottom_two" or "height_order" not in derive(test)["observations"])
    invalid = json.loads(json.dumps(base))
    invalid["measurements"]["ship"]["orbiter_request_permitted"] = "false"
    try:
        derive(invalid)
    except ValueError:
        pass
    else:
        raise AssertionError("string boolean accepted")
    assert derive({"schema_version":1,"source_kind":"not_observed","measurements":{}})["observations"] == {}
    print("PASS: synthetic derivation, tie/missing/invalid-value controls, no-observation UNKNOWN")

def main():
    p = argparse.ArgumentParser()
    p.add_argument("measurement_file", nargs="?")
    p.add_argument("--self-test", action="store_true")
    args = p.parse_args()
    if args.self_test:
        self_test()
        return
    if not args.measurement_file:
        p.error("measurement_file required")
    print(json.dumps(derive(json.loads(Path(args.measurement_file).read_text(encoding="utf-8"))),
                     indent=2))

if __name__ == "__main__":
    main()
