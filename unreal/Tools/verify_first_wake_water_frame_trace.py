"""Fail-closed validator of actual opt-in First Wake PIE water-frame samples.

Not a simulator and not a native test; consumes original Unreal Editor log.
It never changes source, maps or SaveGames. A source test using synthetic log
fixtures cannot establish gameplay or physical water contact.
"""
import argparse
import hashlib
import json
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

def analyze(text):
    if "PIE: Server logged in" not in text:
        raise ValueError("no real native PIE login")
    samples=parse_samples(text)
    dry=[x for x in samples if x["phase"]=="DRY"]
    physical=[x for x in samples if x["phase"]=="PHYSICS"]
    if not dry or len(dry)>30 or not physical or len(physical)>6000:
        raise ValueError("dry/physics bounded samples missing or excessive")
    if not any(x.get("sim")=="0" and float(x.get("stable_sec","-1"))==0 for x in dry):
        raise ValueError("no genuine dry, nonsimulating prelaunch frame")
    for x in physical:
        if any(k not in x for k in NEEDED):
            raise ValueError("incomplete actual physical sample")
    transitions=[i for i,x in enumerate(physical)
                 if x["beat_before"]=="5" and x["beat_after"]=="6"]
    if len(transitions)!=1:
        raise ValueError("exactly one real sea-contact-to-flotation transition required")
    i=transitions[0]
    if float(physical[i]["stable_sec"]) < 2.0:
        raise ValueError("native flotation transition lacks stable gate time")
    generation=physical[i]["restore_gen"]
    previous=None
    duration=0.0
    used=0
    for x in reversed(physical[:i+1]):
        dt=float(x["dt"])
        t=float(x["world_sec"])
        good=(x["sim"]=="1" and x["tagged_overlap"]=="1"
              and x["immersed"]=="1" and x["restore_gen"]==generation
              and abs(float(x["vertical_speed_cm_s"]))<=25.0
              and float(x["stable_sec"])>0
              and 0<dt<=0.25)
        if not good:
            break
        if previous is not None:
            gap=previous-t
            if not 0<gap<=0.25:
                break
        previous=t
        used+=1
        duration+=dt
        if duration>=2.0:
            break
    if duration < 2.0:
        raise ValueError("incomplete or discontinuous measured two-second contact window")
    return {
        "status":"DIRECT_NATIVE_WATER_FLOTATION_TIMESERIES_PASS",
        "dry_samples":len(dry),
        "physical_samples":len(physical),
        "window_samples":used,
        "window_seconds_sum_dt":round(duration,4),
        "transition_world_seconds":float(physical[i]["world_sec"]),
        "stable_seconds_at_transition":float(physical[i]["stable_sec"]),
        "restore_generation":generation,
        "strict_tagged_immersion":True,
        "max_abs_vertical_velocity_cm_s":25,
        "authorizes_cinematic_shot":False,
        "authorizes_player_flight":False,
        "proves_disk_restart":False,
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
