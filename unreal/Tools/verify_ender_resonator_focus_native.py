#!/usr/bin/env python3
"""Second-process, non-overwriting, read-only UE5.8.4 focus-map readback.

Source preflight is pure Python; '--native' must be run by Unreal
Editor-Cmd.exe -run=pythonscript with TSTSS_FOCUS_READBACK_EXACT_HEAD.
No maps or assets are saved, relabeled, imported or modified.
"""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import re
import subprocess

ROOT=Path(__file__).resolve().parents[2]
PROJECT=ROOT/"unreal"
MANIFEST=PROJECT/"Docs/Evidence/ender_resonator_focus_native_assets_20261111.json"
ENV="TSTSS_FOCUS_READBACK_EXACT_HEAD"
STATUS="INDEPENDENT_UE58_FOCUS_MAP_READBACK_PASS_NOT_PIE"

def git(*args):
    r=subprocess.run(["git","-C",str(ROOT),*args],
        capture_output=True,text=True,timeout=30,check=True)
    return r.stdout.strip()

def exact_sha(sha):
    return isinstance(sha,str) and bool(re.fullmatch(r"[0-9a-f]{40}",sha))

def verify_sources(project=PROJECT, manifest=MANIFEST, require_exact_head=False):
    """Prove committed binary scope, history and no active source edits.

    Independent of the original one-off importer Saved receipt, so the
    review works on a fresh clone without relying on local author state.
    """
    project=Path(project).resolve()
    # Portable source-only verification may run in any actual Git worktree.
    # Native readback retains the dedicated-worktree and exact-head lock below.
    if project.name!="unreal" or not (project.parent/".git").exists():
        raise RuntimeError("HOLD: source check requires isolated review worktree")
    data=json.loads(Path(manifest).read_text(encoding="utf8"))
    if (data.get("schema")!="tstss.resonator-focus-native-review.v1" or
        data.get("unreal_version")!="5.8.4" or
        not exact_sha(data.get("asset_commit")) or
        data.get("map_package")!="/Game/TSTSS/Review/ResonatorFocus/L_EnderCenteringPulseReview" or
        data.get("data_table_package")!="/Game/TSTSS/Review/ResonatorFocus/DT_EnderResonatorFocusReview" or
        data.get("executable_spells")!=["Ender_Centering","Ender_ResonantPulse"] or
        data.get("other_magic_status")!="DesignOnly / Correspondence ON HOLD"):
        raise RuntimeError("HOLD: focus identity or authority manifest drift")
    if (len(data.get("assets",{}))!=4 or len(data.get("source_wav",{}))!=2 or
        set(data["assets"])!={"L_EnderCenteringPulseReview.umap",
                              "DT_EnderResonatorFocusReview.uasset",
                              "Audio/SFX_Centering.uasset",
                              "Audio/SFX_ResonantPulse.uasset"} or
        set(data["source_wav"])!={"AudioSource/SFX_Centering.wav",
                                  "AudioSource/SFX_ResonantPulse.wav"}):
        raise RuntimeError("HOLD: source or imported asset inventory drift")
    root=project/"Content/TSTSS/Review/ResonatorFocus"
    for relative,digest in {**data["assets"],**data["source_wav"]}.items():
        if not re.fullmatch(r"[a-f0-9]{64}",digest):
            raise RuntimeError("HOLD: invalid pinned SHA256")
        f=root/relative
        if not f.is_file() or hashlib.sha256(f.read_bytes()).hexdigest()!=digest:
            raise RuntimeError("HOLD: committed asset bytes mismatch: "+relative)
    source=json.loads((project/"DataSource/Magic/EnderResonator.vertical_slice.review.json").read_text(encoding="utf8"))
    if len(source)!=10 or {r["SkillId"] for r in source if r["Admission"]=="ReviewExecutable"}!=set(data["executable_spells"]):
        raise RuntimeError("HOLD: live source spell admission drift")
    if require_exact_head:
        expected=os.environ.get(ENV,"")
        current=git("rev-parse","HEAD")
        if not exact_sha(expected) or expected!=current:
            raise RuntimeError("HOLD: native readback needs unchanged explicit HEAD")
        if project.parent.name!="TSTSS_CenteringPulse_20261111":
            raise RuntimeError("HOLD: wrong isolated review worktree for native readback")
        if git("status","--porcelain","-uall"):
            raise RuntimeError("HOLD: changed project source during native readback")
        subprocess.run(["git","-C",str(ROOT),"merge-base","--is-ancestor",
                        data["asset_commit"],current],
                       timeout=30,check=True)
    return data

def native_readback():
    import unreal as u
    if not u.SystemLibrary.get_engine_version().startswith("5.8.4"):
        raise RuntimeError("HOLD: requires Unreal 5.8.4")
    project=Path(u.Paths.project_dir()).resolve()
    if project!=PROJECT.resolve():
        raise RuntimeError("HOLD: unexpected UE project")
    data=verify_sources(require_exact_head=True)
    if (u.EditorLoadingAndSavingUtils.get_dirty_map_packages() or
        u.EditorLoadingAndSavingUtils.get_dirty_content_packages()):
        raise RuntimeError("HOLD: existing unsaved changes")
    base="/Game/TSTSS/Review/ResonatorFocus"
    table=u.EditorAssetLibrary.load_asset(data["data_table_package"])
    if not table or not isinstance(table,u.DataTable):
        raise RuntimeError("HOLD: DataTable cannot reopen as native DataTable")
    names={str(n) for n in u.DataTableFunctionLibrary.get_data_table_row_names(table)}
    if len(names)!=10 or not set(data["executable_spells"]).issubset(names):
        raise RuntimeError("HOLD: DataTable exact row count/required names mismatch")
    for skill in data["executable_spells"]:
        if skill not in names:
            raise RuntimeError("HOLD: missing required focus skill")
    for name in ("SFX_Centering","SFX_ResonantPulse"):
        sound=u.EditorAssetLibrary.load_asset(base+"/Audio/"+name)
        if not isinstance(sound,u.SoundWave):
            raise RuntimeError("HOLD: original native SoundWave cannot reopen")
    world=u.EditorLoadingAndSavingUtils.load_map(data["map_package"])
    if world is None:
        raise RuntimeError("HOLD: native focus map cannot reopen")
    actors=list(u.get_editor_subsystem(u.EditorActorSubsystem).get_all_level_actors())
    review=[actor for actor in actors
            if actor.get_class().get_name()=="TSTSSResonatorFocusReviewActor"]
    if len(review)!=1:
        raise RuntimeError("HOLD: expected one actor of native review type")
    focus=review[0]
    if focus.get_actor_label()!="REVIEW ONLY - Ender Centering and Resonant Pulse":
        raise RuntimeError("HOLD: saved review actor label mismatch")
    if "TSTSSReviewOnly" not in {str(t) for t in focus.get_editor_property("tags")}:
        raise RuntimeError("HOLD: scene lost mandatory review-only tag")
    def required_enabled(stem):
        for prop in (stem,"b_"+stem):
            try:
                state=focus.get_editor_property(prop)
            except Exception:
                continue
            if state is not True:
                raise RuntimeError("HOLD: required review flag was disabled: "+prop)
            return prop
        raise RuntimeError("HOLD: required native review flag missing: "+stem)
    focus_prop=required_enabled("enable_focus_review")
    ionia_prop=required_enabled("ionia_recruited_for_review")
    result={
        "status":STATUS,
        "head":git("rev-parse","HEAD"),
        "asset_origin_commit":data["asset_commit"],
        "engine":"5.8.4",
        "map":data["map_package"],
        "native_actor_count":len(actors),
        "focus_actor_count":len(review),
        "review_flags":[focus_prop,ionia_prop],
        "native_skill_rows":len(names),
        "imported_native_soundwaves":2,
        "source_and_asset_hashes_verified":True,
        "rendered_gpu_frames_verified":False,
        "live_player_input_verified":False,
        "speaker_audio_verified":False,
        "campaign_integration_verified":False
    }
    destination=project/"Saved/ResonatorFocus"/(
        "native-independent-readback-"+result["head"][:12]+".json")
    destination.parent.mkdir(parents=True,exist_ok=True)
    with destination.open("x",encoding="utf8") as handle:
        json.dump(result,handle,indent=2)
        handle.write("\n")
    u.log("TSTSS_RESONATOR_FOCUS_INDEPENDENT_NATIVE_READBACK_PASS_NOT_PIE")
    return result

if __name__=="__main__":
    native_readback()
