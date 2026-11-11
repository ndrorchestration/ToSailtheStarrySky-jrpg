"""Cinematic-only developer-sign suppression, never milestone deletion.

NO level save, no collision/milestone change, no actual 3D material edits.
Safe only inside an isolated native camera-review process after exact 115-
or 200-actor World and required story marker identities have been verified.
The original review signs remain visible in regular gameplay by default.
"""
from __future__ import annotations
MILESTONES=("FlyerDiscovery","IoniaHiring","AureateBoarding",
            "LiftStation","PressureStation","ReserveStation",
            "EngineeringApproval")
SIGN_PREFIX="TSTSS_PRELUDE_REVIEW_SIGN_"
MILESTONE_PREFIX="TSTSS_PRELUDE_REVIEW_"

def sign_inventory(labels):
    if len(set(labels))!=len(labels):
        raise RuntimeError("HOLD: duplicate scene actor identity")
    expected={SIGN_PREFIX+s for s in MILESTONES}
    seen={s for s in labels if s.startswith(SIGN_PREFIX)}
    if seen!=expected:
        raise RuntimeError("HOLD: missing or unreviewed cinematic developer sign")
    for stop in MILESTONES:
        if labels.count(MILESTONE_PREFIX+stop)!=1:
            raise RuntimeError("HOLD: real interaction milestone missing "+stop)
    return tuple(SIGN_PREFIX+s for s in MILESTONES)

def suppress_transient_only(actor_list,unreal):
    labels=[a.get_actor_label() for a in actor_list]
    expected=sign_inventory(labels)
    signs={a.get_actor_label():a for a in actor_list
           if a.get_actor_label().startswith(SIGN_PREFIX)}
    for name in expected:
        if not isinstance(signs[name],unreal.TextRenderActor):
            raise RuntimeError("HOLD: developer sign is not a native TextRenderActor")
    # Never hide/destroy seven gameplay marker actors or change any collision.
    milestones={MILESTONE_PREFIX+s for s in MILESTONES}
    if any(bool(a.get_editor_property("hidden")) for a in actor_list
           if a.get_actor_label() in milestones):
        raise RuntimeError("HOLD: interaction marker already hidden")
    for name in expected:
        signs[name].set_actor_hidden_in_game(True)
    if any(not bool(signs[name].get_editor_property("hidden")) for name in expected):
        raise RuntimeError("HOLD: native sign visibility toggle unverified")
    return {"status":"ONLY_SEVEN_DEV_SIGNS_HIDDEN_TRANSIENT_FOR_CAPTURE",
            "sign_labels":list(expected),"interaction_actors_hidden":0,
            "map_saved":False,"gameplay_signs_deleted":False,
            "runtime_pie_verified":False}
