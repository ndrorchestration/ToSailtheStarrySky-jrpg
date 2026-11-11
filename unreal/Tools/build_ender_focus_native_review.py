#!/usr/bin/env python3
"""Fail-closed native UE5 review: import 2 original sounds, 10-row DataTable,
and author one isolated playable Centering/Resonant Pulse battle map.
No main story map edits. No overwrite. NULLRHI import is not PIE proof.
"""
from pathlib import Path
import hashlib
import json
import os
import subprocess

PACKAGE="/Game/TSTSS/Review/ResonatorFocus"
MAP=PACKAGE+"/L_EnderCenteringPulseReview"
TABLE=PACKAGE+"/DT_EnderResonatorFocusReview"
SOUNDS=("SFX_Centering","SFX_ResonantPulse")
ENV_HEAD="TSTSS_FOCUS_EXPECTED_HEAD"

def source_preflight(project):
    project=Path(project).resolve()
    if project.name!="unreal" or project.parent.name!="TSTSS_CenteringPulse_20261111":
        raise RuntimeError("HOLD: only isolated focus worktree")
    head=os.environ.get(ENV_HEAD,"")
    if len(head)!=40 or any(c not in "0123456789abcdef" for c in head.lower()):
        raise RuntimeError("HOLD: exact commit not provided")
    def git(*args):
        r=subprocess.run(["git","-C",str(project.parent),*args],
            capture_output=True,text=True,timeout=30,check=True)
        return r.stdout.strip()
    if git("rev-parse","HEAD")!=head:
        raise RuntimeError("HOLD: source revision changed")
    if git("status","--porcelain"):
        raise RuntimeError("HOLD: uncommitted source")
    source=project/"DataSource/Magic/EnderResonator.vertical_slice.review.json"
    rows=json.loads(source.read_text(encoding="utf-8"))
    admitted={r["SkillId"] for r in rows if r["Admission"]=="ReviewExecutable"}
    if len(rows)!=10 or admitted!={"Ender_Centering","Ender_ResonantPulse"}:
        raise RuntimeError("HOLD: source permission drift")
    for name in SOUNDS:
        wav=project/"Content/TSTSS/Review/ResonatorFocus/AudioSource"/(name+".wav")
        uasset=project/"Content/TSTSS/Review/ResonatorFocus/Audio"/(name+".uasset")
        if not wav.is_file() or uasset.exists():
            raise RuntimeError("HOLD: audio source missing or target exists: "+name)
    for name in ("DT_EnderResonatorFocusReview.uasset",
                 "L_EnderCenteringPulseReview.umap"):
        if (project/"Content/TSTSS/Review/ResonatorFocus"/name).exists():
            raise RuntimeError("HOLD: target already exists: "+name)
    return head,source

def generate():
    import unreal
    project=Path(unreal.Paths.project_dir()).resolve()
    head,source=source_preflight(project)
    for name in SOUNDS:
        if unreal.EditorAssetLibrary.does_asset_exist(PACKAGE+"/Audio/"+name):
            raise RuntimeError("HOLD: existing SoundWave")
    if unreal.EditorAssetLibrary.does_asset_exist(MAP) or unreal.EditorAssetLibrary.does_asset_exist(TABLE):
        raise RuntimeError("HOLD: existing DataTable/map")
    unreal.EditorAssetLibrary.make_directory(PACKAGE)
    unreal.EditorAssetLibrary.make_directory(PACKAGE+"/Audio")
    tasks=[]
    for name in SOUNDS:
        task=unreal.AssetImportTask()
        task.set_editor_property("filename",
            str(project/"Content/TSTSS/Review/ResonatorFocus/AudioSource"/(name+".wav")))
        task.set_editor_property("destination_path",PACKAGE+"/Audio")
        task.set_editor_property("destination_name",name)
        task.set_editor_property("replace_existing",False)
        task.set_editor_property("automated",True)
        task.set_editor_property("save",True)
        tasks.append(task)
    unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks(tasks)
    for name in SOUNDS:
        sound=unreal.EditorAssetLibrary.load_asset(PACKAGE+"/Audio/"+name)
        if not sound or not isinstance(sound,unreal.SoundWave):
            raise RuntimeError("HOLD: SoundWave missing: "+name)
    row_struct=unreal.load_object(None,"/Script/ToSailTheStarrySky.TSTSSBattleSkillRow")
    if not row_struct: raise RuntimeError("HOLD: native battle row missing")
    factory=unreal.DataTableFactory()
    configured=False
    for key in ("struct","row_struct"):
        try:
            factory.set_editor_property(key,row_struct)
            configured=True
            break
        except Exception:
            continue
    if not configured: raise RuntimeError("HOLD: DataTable row struct missing")
    table=unreal.AssetToolsHelpers.get_asset_tools().create_asset(
        "DT_EnderResonatorFocusReview",PACKAGE,unreal.DataTable,factory)
    if not table: raise RuntimeError("HOLD: cannot author DataTable")
    if not unreal.DataTableFunctionLibrary.fill_data_table_from_json_file(table,str(source)):
        raise RuntimeError("HOLD: source catalog DataTable JSON admission failed")
    if not unreal.EditorAssetLibrary.save_loaded_asset(table):
        raise RuntimeError("HOLD: DataTable save failed")

    review_cls=unreal.load_class(None,
        "/Script/ToSailTheStarrySky.TSTSSResonatorFocusReviewActor")
    if not review_cls: raise RuntimeError("HOLD: C++ review actor unavailable")
    if not unreal.EditorLevelLibrary.new_level(MAP):
        raise RuntimeError("HOLD: cannot create focus map")
    actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    actor=actors.spawn_actor_from_class(
        review_cls,unreal.Vector(0,0,100),unreal.Rotator(0,0,0))
    if not actor: raise RuntimeError("HOLD: review actor spawn failed")
    actor.set_actor_label("REVIEW ONLY - Ender Centering and Resonant Pulse")
    actor.set_editor_property("tags",[unreal.Name("TSTSSReviewOnly")])
    actor.set_editor_property("b_enable_focus_review",True)
    actor.set_editor_property("b_ionia_recruited_for_review",True)
    if not unreal.EditorLevelLibrary.save_current_level():
        raise RuntimeError("HOLD: native review map save failed")
    target=project/"Content/TSTSS/Review/ResonatorFocus"
    files={
        "L_EnderCenteringPulseReview.umap":target/"L_EnderCenteringPulseReview.umap",
        "DT_EnderResonatorFocusReview.uasset":target/"DT_EnderResonatorFocusReview.uasset",
        "SFX_Centering.uasset":target/"Audio/SFX_Centering.uasset",
        "SFX_ResonantPulse.uasset":target/"Audio/SFX_ResonantPulse.uasset"
    }
    for name,file in files.items():
        if not file.is_file(): raise RuntimeError("HOLD: missing native file "+name)
    receipt={
        "status":"FOUR_NATIVE_FOCUS_ASSETS_WRITTEN_NOT_PIE_REVIEWED",
        "head":head,"engine":"5.8.4",
        "assets":{name:{"bytes":file.stat().st_size,
            "sha256":hashlib.sha256(file.read_bytes()).hexdigest()}
            for name,file in files.items()},
        "executable_spells":["Ender_Centering","Ender_ResonantPulse"],
        "correspondence":"DESIGN_ONLY_HOLD",
        "pie_keyboard":"NOT_VERIFIED","gpu_screenshot":"NOT_VERIFIED",
        "real_audio":"NOT_VERIFIED","main_merged":False}
    out=project/"Saved/ResonatorFocus/native-authoring.json"
    out.parent.mkdir(parents=True,exist_ok=True)
    with out.open("x",encoding="utf-8") as f:
        json.dump(receipt,f,indent=2)
        f.write("\n")
    unreal.log("TSTSS_CENTERING_PULSE_NATIVE_CONTENT_WRITTEN_NOT_PIE_PROVEN")
    return receipt
if __name__=="__main__":generate()
