"""Fail-closed validator of actual opt-in First Wake PIE water-frame samples.

Not a simulator and not a native test; consumes original Unreal Editor log.
It never changes source, maps or SaveGames. A source test using synthetic log
fixtures cannot establish gameplay or physical water contact.
"""
import argparse
import hashlib
import json
import math
from pathlib import Path
import subprocess

PREFIX = "TSTSS_WATER_REVIEW_SAMPLE "
NEEDED = ("world_sec","dt","hull_z_cm","water_surface_z_cm",
          "tagged_overlap","immersed","submersion",
          "vertical_speed_cm_s","stable_sec","beat_before",
          "beat_after","sim","restore_gen")

def digest(path):
    h=hashlib.sha256()
    with Path(path).open("rb") as f:
        for chunk in iter(lambda:f.read(1024*1024),b""):
            h.update(chunk)
    return h.hexdigest()

def parse_samples(text):
    samples=[]
    for line in text.splitlines():
        if PREFIX not in line:
            continue
        attrs={}
        for token in line.split(PREFIX,1)[1].split():
            if "=" not in token:
                continue
            k,v=token.split("=",1)
            if k in attrs:
                raise ValueError("duplicate log field: "+k)
            attrs[k]=v
        if attrs.get("phase") not in ("DRY","PHYSICS"):
            raise ValueError("unexpected water trace phase")
        samples.append(attrs)
    return samples

def _finite(sample, field):
    """A sampled physics number must not be NaN, infinite, or malformed."""
    try:
        value = float(sample[field])
    except (KeyError, ValueError, TypeError, OverflowError) as exc:
        raise ValueError("invalid physical sample number: " + field) from exc
    if not math.isfinite(value):
        raise ValueError("nonfinite physical sample number: " + field)
    return value


def analyze(text):
    if "PIE: Server logged in" not in text:
        raise ValueError("no real native PIE login")
    samples = parse_samples(text)
    dry = [x for x in samples if x["phase"] == "DRY"]
    physical = [x for x in samples if x["phase"] == "PHYSICS"]
    if not dry or len(dry) > 30 or not physical or len(physical) > 6000:
        raise ValueError("dry/physics bounded samples missing or excessive")
    if not any(x.get("sim") == "0" and
               _finite(x, "stable_sec") == 0.0 and
               _finite(x, "world_sec") >= 0.0 for x in dry):
        raise ValueError("no genuine dry, nonsimulating prelaunch frame")

    numeric = ("world_sec", "dt", "hull_z_cm", "hull_bottom_z_cm",
               "water_surface_z_cm", "submersion", "vertical_speed_cm_s",
               "stable_sec")
    for sample in physical:
        if any(k not in sample for k in (*NEEDED, "hull_bottom_z_cm")):
            raise ValueError("incomplete actual physical sample")
        for key in numeric:
            _finite(sample, key)

    transitions = [i for i, x in enumerate(physical)
                   if x["beat_before"] == "5" and x["beat_after"] == "6"]
    if len(transitions) != 1:
        raise ValueError("exactly one real sea-contact-to-flotation transition required")
    i = transitions[0]
    native_stable = _finite(physical[i], "stable_sec")
    if native_stable < 2.0:
        raise ValueError("native flotation transition lacks stable gate time")

    # Walk BACKWARD from the actual transition. The newest sample is an
    # observation, not a duration: never count its dt without a verified prior
    # qualifying sample. A valid later sample's dt must match its world-clock
    # interval from the immediately preceding qualifying sample.
    generation = physical[i]["restore_gen"]
    later = None
    elapsed_world = 0.0
    elapsed_dt = 0.0
    used = 0
    observed = []  # Most-recent first; never synthesize missing frames.
    for sample in reversed(physical[:i + 1]):
        speed = _finite(sample, "vertical_speed_cm_s")
        dt = _finite(sample, "dt")
        now = _finite(sample, "world_sec")
        stable = _finite(sample, "stable_sec")
        surface = _finite(sample, "water_surface_z_cm")
        bottom = _finite(sample, "hull_bottom_z_cm")
        submersion = _finite(sample, "submersion")
        # During a witnessed window, genuine samples either hold SeaContact
        # (5 -> 5), make the *single* flotation transition (5 -> 6), or
        # begin contact (Launched 4 -> SeaContact 5, zero credited time).
        # Other story beats must never masquerade as settled water frames.
        contact_entry = (sample["beat_before"] == "4"
                         and sample["beat_after"] == "5"
                         and abs(stable) <= 0.005)
        at_contact = (sample["beat_before"] == "5"
                      and sample["beat_after"] in ("5", "6"))
        good = ((contact_entry or at_contact)
                and sample["sim"] == "1"
                and sample["tagged_overlap"] == "1"
                and sample["immersed"] == "1"
                and sample["restore_gen"] == generation
                and abs(speed) <= 25.0 and 0 < dt <= 0.25
                and stable >= 0.0 and 0.01 < submersion <= 1.0
                and bottom < surface)
        if not good:
            break
        if later is not None:
            later_world, later_dt, later_stable = later
            interval = later_world - now
            # Two world observations and the LATER frame's reported dt must
            # agree. Time gaps, duplicate frames and downwards clock jumps
            # cannot create false evidence.
            tolerance = max(0.002, later_dt * 0.15)
            if (not 0 < interval <= 0.25 or
                    abs(interval - later_dt) > tolerance or
                    stable > later_stable + tolerance):
                break
            elapsed_world += interval
            elapsed_dt += later_dt
        later = (now, dt, stable)
        observed.append((dt, stable))
        used += 1
        if contact_entry:
            # This frame can anchor the window, but no earlier Launched
            # frames may be imported as stable SeaContact evidence.
            break

    # Both the independently observed world clock and reported frame deltas
    # must demonstrate the full two seconds. A first frame contributes ZERO
    # elapsed time; this deliberately rejects the historical 1.9943s trace.
    if elapsed_world < 2.0 or elapsed_dt < 2.0:
        raise ValueError("incomplete or discontinuous measured two-second contact window")
    if native_stable > elapsed_world + 0.005:
        raise ValueError("native stable timer exceeds directly observed window")

    # A two-second timespan alone does not prove the production gate counted
    # those frames. Compare the counter advance against each LATER frame dt;
    # a forged jump at the transition used to pass the elapsed-time check.
    for (later_dt, later_stable), (_, earlier_stable) in zip(
            observed, observed[1:]):
        tolerance = max(0.002, later_dt * 0.15)
        if abs((later_stable - earlier_stable) - later_dt) > tolerance:
            raise ValueError("native stable timer progression disagrees with observed frames")

    return {
        "status": "DIRECT_NATIVE_WATER_FLOTATION_TIMESERIES_PASS",
        "dry_samples": len(dry),
        "physical_samples": len(physical),
        "window_samples": used,
        "window_seconds_elapsed_world": round(elapsed_world, 4),
        "window_seconds_sum_dt": round(elapsed_dt, 4),
        "transition_world_seconds": _finite(physical[i], "world_sec"),
        "stable_seconds_at_transition": native_stable,
        "restore_generation": generation,
        "strict_tagged_immersion": True,
        "max_abs_vertical_velocity_cm_s": 25,
        "authorizes_cinematic_shot": False,
        "authorizes_player_flight": False,
        "proves_disk_restart": False,
    }

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--log",type=Path,required=True)
    p.add_argument("--checkout",type=Path,required=True)
    p.add_argument("--map",type=Path,required=True)
    p.add_argument("--head",required=True)
    p.add_argument("--map-sha256",required=True)
    p.add_argument("--out",type=Path,required=True)
    a=p.parse_args()
    if a.out.exists():
        raise FileExistsError("never overwrite a prior native telemetry receipt")
    head=subprocess.check_output(["git","-C",str(a.checkout),"rev-parse","HEAD"],text=True).strip()
    if head != a.head:
        raise ValueError("exact source commit mismatch")
    if digest(a.map)!=a.map_sha256:
        raise ValueError("saved native map SHA mismatch")
    text=a.log.read_text(encoding="utf-8",errors="replace")
    result=analyze(text)
    result.update(head=head,map_sha256=a.map_sha256,log_sha256=digest(a.log),
                  source="REAL_NATIVE_PIE_LOG_NOT_SYNTHETIC")
    with a.out.open("x",encoding="utf-8") as f:
        json.dump(result,f,indent=2,sort_keys=True)
    print(result["status"]+" "+str(a.out))

if __name__=="__main__":
    main()
