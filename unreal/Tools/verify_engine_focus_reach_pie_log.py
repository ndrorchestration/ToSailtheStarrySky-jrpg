"""Fail-closed parser for a future *real* Unreal 5.8.4 PIE E-K-O-WASD-C log.

Synthetic unit fixtures verify the parser ONLY. A passing real logfile is
not camera-frame proof, a physical-key proof, final focus restoration
confirmation, or creator approval. Review worktree and native DLL custody
must be independently checked.
"""
from __future__ import annotations
import argparse
import datetime as dt
import json
import math
import re
from pathlib import Path

PREFIX="LogTemp: Display: "
STAMP=re.compile(r"^\[(\d{4}\.\d{2}\.\d{2}-\d{2}\.\d{2}\.\d{2}):(\d{3})\]\[\d+\]")
KV=re.compile(r"([A-Za-z_]+)=([^\s]+)")
EXPECTED_E=(
    "FlyerDiscovery","IoniaHiring","AureateBoarding",
    "LiftStation","PressureStation","ReserveStation","EngineeringApproval",
)
EVENTS={
 "E":"TSTSS_PIE_REVIEW_E_ACCEPT",
 "K":"TSTSS_FIRSTWAKE_REVIEW_SCENE_TRAVEL_QUEUED_NO_RECRUITMENT",
 "O":"TSTSS_FIRSTWAKE_OPTICAL_REVIEW_QUEUED_NO_STORY_ADVANCE",
 "ARRIVAL":"TSTSS_FIRSTWAKE_REVIEW_SCENE_ARRIVAL_STORY_RESTORED_NO_RECRUITMENT",
 "RANGE":"TSTSS_PIE_GAMEPLAY_ENGINE_FOCUS_RANGE",
 "ENTER":"TSTSS_PIE_GAMEPLAY_ENGINE_FOCUS_ENTER",
 "RESTORE":"TSTSS_PIE_GAMEPLAY_ENGINE_FOCUS_RESTORE_AUDIT",
 "RESTORE_MARKER":"TSTSS_PIE_GAMEPLAY_ENGINE_FOCUS_RESTORE",
}
REQUIRED_WORLD_GAUGE=(-250.,-250.,270.)
MAX_DISTANCE_CM=450.

def parse_events(raw:str):
    results=[]
    for i,line in enumerate(raw.splitlines()):
        m=STAMP.match(line)
        if not m or PREFIX not in line:
            continue
        message=line.split(PREFIX,1)[1]
        name=next((k for k,v in EVENTS.items()
                   if message.startswith(v+" ") or message==v),None)
        if name is None:
            continue
        timestamp=dt.datetime.strptime(m.group(1),"%Y.%m.%d-%H.%M.%S")
        timestamp=timestamp.replace(microsecond=int(m.group(2))*1000)
        results.append({"kind":name,"ts":timestamp,"line":i+1,
                        "kv":dict(KV.findall(message)),"message":message})
    return results

def demand(condition,why):
    if not condition:raise ValueError("HOLD: "+why)

def finite_float(v,label):
    try: x=float(v)
    except (TypeError,ValueError):raise ValueError("HOLD: invalid "+label) from None
    demand(math.isfinite(x),"nonfinite "+label)
    return x

def validated(events):
    def exactly(kind,n):
        hits=[x for x in events if x["kind"]==kind]
        demand(len(hits)==n,f"expected {n} {kind} event(s), got {len(hits)}")
        return hits
    es=exactly("E",7)
    targets=[x["kv"].get("target","") for x in es]
    expected=(["TSTSS_PRELUDE_REVIEW_"+label for label in EXPECTED_E[:3]] +
              ["TSTSS_ENGINEROOM_REVIEW_"+label for label in EXPECTED_E[3:]])
    demand(targets==expected,"seven earned E objective sequence differs")
    k=exactly("K",1)[0]
    o=exactly("O",1)[0]
    arrivals=exactly("ARRIVAL",2)
    demand("VS02_AureateInteriors" in k["message"],"K did not load original ship")
    demand("M_EnginePresentationReview" in o["message"],"O did not load optical copy")
    demand([x["kv"].get("beat") for x in arrivals]==["2","3"],
           "ship arrival must preserve boarded beat=2, optical arrival engineering beat=3")
    entered=exactly("ENTER",1)[0]
    restored=exactly("RESTORE",1)[0]
    restoremarkers=exactly("RESTORE_MARKER",1)[0]
    ranges=[x for x in events if x["kind"]=="RANGE"]
    demand(len(ranges)>=1,"missing real native gauge-distance sample")
    preceding=[x for x in ranges if x["ts"]<=entered["ts"]]
    demand(preceding,"no native gauge sample preceding camera entry")
    sample=preceding[-1]
    ordered=[*es[:3],k,arrivals[0],*es[3:],o,arrivals[1],sample,entered,restored,restoremarkers]
    demand(all(a["ts"]<b["ts"] for a,b in zip(ordered,ordered[1:])),
           "event sequence/order/camera restoration invalid")
    demand([x["ts"] for x in es]==sorted(x["ts"] for x in es),
           "E interactions reversed or duplicate timestamps")
    kv=sample["kv"]
    demand(kv.get("limit_cm")=="450.0","C proximity threshold was modified")
    demand(kv.get("gauge_count")=="1" and kv.get("sky_count")=="1",
           "one real native LIFT + sky owner not established")
    pawn=[finite_float(kv.get(c),c) for c in ("pawn_x","pawn_y","pawn_z")]
    gauge=[finite_float(kv.get(c),c) for c in ("gauge_x","gauge_y","gauge_z")]
    for have,want in zip(gauge,REQUIRED_WORLD_GAUGE):
        demand(abs(have-want)<=1.0,"native LIFT gauge moved from authored location")
    dist=math.dist(pawn,gauge)
    read_dist=finite_float(kv.get("distance_cm"),"distance_cm")
    demand(abs(dist-read_dist)<=1.5,"logged range contradicts 3D pawn/gauge positions")
    demand(dist<=MAX_DISTANCE_CM,"C cut entered outside unchanged 450cm range")
    ekv=entered["kv"]
    demand(ekv.get("move_ignored")=="1" and ekv.get("look_ignored")=="1",
           "preview did not claim required input locks")
    focus=finite_float(ekv.get("focus_cm"),"focus_cm")
    demand(65.<=focus<=12000.,"impossible native focus distance")
    demand(abs(focus-math.sqrt(380.**2+650.**2+260.**2))<1.0,
           "native lens/camera focus offset drift")
    demand(ekv.get("preview_limit_s")=="4.0","4-second limit changed")
    demand(abs(finite_float(ekv.get("gauge_distance_cm"),"gauge_distance_cm")-read_dist)<=1.,
           "entry logged a different gauge distance than the sample")
    rkv=restored["kv"]
    elapsed=finite_float(rkv.get("elapsed_s"),"elapsed_s")
    delta=(restored["ts"]-entered["ts"]).total_seconds()
    demand(3.70<=delta<=5.20 and 3.70<=elapsed<=5.20,
           "four-second auto return missing or outside bounds")
    demand(abs(delta-elapsed)<=0.50,"wall-time and engine elapsed-time disagree")
    demand(rkv.get("controller_valid")=="1","restoration lost live controller")
    demand(rkv.get("move_ignored")=="0" and rkv.get("look_ignored")=="0",
           "PIE movement or look input still locked")
    return {
        "status":"PIE_LOG_CONTRACT_PASS_STILL_NEEDS_REAL_INPUT_AND_NATIVE_CUSTODY",
        "seven_earned_interactions":True,
        "board_then_shipboard_inspections_then_optical_o":True,
        "real_lift_actor_and_sky_owner_count":1,
        "pawn_cm":pawn,"gauge_cm":gauge,
        "distance_cm":round(dist,2),
        "native_focus_cm":round(focus,2),
        "preview_return_wall_s":round(delta,3),
        "preview_return_engine_elapsed_s":round(elapsed,3),
        "input_unlock_observed_in_native_log":True,
        "view_target_blend_completed_after_0_3s":False,
        "actual_physical_wasd_independently_observed":False,
        "actual_gpu_bokeh_approved":False,
        "creator_visual_approved":False,
        "canonical_story_save_mutated":False,
    }

def verify(text:str):
    return validated(parse_events(text))

if __name__=="__main__":
    arg=argparse.ArgumentParser()
    arg.add_argument("unreal_log",type=Path)
    arg.add_argument("--receipt",type=Path)
    args=arg.parse_args()
    result=verify(args.unreal_log.read_text(encoding="utf-8",errors="replace"))
    if args.receipt:
        args.receipt.parent.mkdir(parents=True,exist_ok=True)
        with args.receipt.open("x",encoding="utf-8") as stream:
            json.dump(result,stream,indent=2)
    print(json.dumps(result,indent=2))
