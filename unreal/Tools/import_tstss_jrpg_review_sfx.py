#!/usr/bin/env python3
"""Guarded native SoundWave import of FOUR original TSTSS review-only WAVs.

Never edits any campaign map/music, changes audio licensing, merges content or
overwrites an existing Unreal SoundWave. --validate does not start Unreal.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess

ROOT_NAME="TSTSS-Slice-Enemies-20261110"
SOURCE_DIR=Path("Content/TSTSS/Review/AudioSource")
DEST_DIR=Path("Content/TSTSS/Review/Audio")
DEST_PACKAGE="/Game/TSTSS/Review/Audio"
HEAD_ENV="TSTSS_JRPG_REVIEW_AUDIO_EXPECTED_HEAD"
RECEIPT=Path("Saved/EnemyGalleryV3/audio-import-receipt.json")
HASHES={
 "SFX_EncounterSting":"4809d0ce3ab350c4fb067e8017810b3269fb2ec109527b6a7f9a9bd31d4d0d43",
 "SFX_VictoryFanfare":"7d6fb0822ff2ff97d6ca0edec4832692c880d65fcb6fb638563909f18b926929",
 "SFX_RewardReveal":"7bb0108bd11531fdc4af5c8a011509d6f013fc0d5c39d293523798198f9f0ed0",
 "SFX_ReturnWhoosh":"784435e9708c5a7777214136328f30a0d90566557f0a5a177c147d173a73d95a",
}
def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()
def plan():
    if len(HASHES)!=4 or not str(DEST_PACKAGE).startswith("/Game/TSTSS/Review/"):
        raise RuntimeError("HOLD: only four scoped original review cues allowed")
    return {"status":"SOURCE_PLAN_NOT_IMPORTED","expected_source_names":list(HASHES),
            "destination":DEST_PACKAGE,"original_review_sfx":True,
            "native_import_proven":False,"audio_playback_proven":False,
            "shipping_or_canon_status_changed":False}
def checked_project(project):
    project=project.resolve()
    repo=project.parent
    if project.name.lower()!="unreal" or repo.name!=ROOT_NAME:
        raise RuntimeError("HOLD: separate review worktree only")
    sha=os.environ.get(HEAD_ENV,"")
    if not re.fullmatch("[0-9a-fA-F]{40}",sha):
        raise RuntimeError("HOLD: exact full Git head missing")
    def git(*args):
        r=subprocess.run(["git","-C",str(repo),*args],
             text=True,capture_output=True,check=False,timeout=30)
        if r.returncode:
            raise RuntimeError("HOLD: git custody unavailable")
        return r.stdout.strip()
    if git("rev-parse","HEAD").lower()!=sha.lower():
        raise RuntimeError("HOLD: source drift")
    if git("status","--porcelain"):
        raise RuntimeError("HOLD: dirty worktree")
    if (project/RECEIPT).exists():
        raise RuntimeError("HOLD: audio import receipt already present")
    for name,expected in HASHES.items():
        wav=project/SOURCE_DIR/(name+".wav")
        asset=project/DEST_DIR/(name+".uasset")
        if not wav.is_file() or digest(wav)!=expected:
            raise RuntimeError("HOLD: source WAV digest drift: "+name)
        if asset.exists():
            raise RuntimeError("HOLD: refuse existing native audio asset: "+name)
    return project,sha.lower()
def build():
    result=plan()
    import unreal
    project,head=checked_project(Path(unreal.Paths.project_dir()))
    if unreal.EditorLoadingAndSavingUtils.get_dirty_map_packages():
        raise RuntimeError("HOLD: editor has unsaved map changes")
    task_list=[]
    for name in HASHES:
        package=DEST_PACKAGE+"/"+name
        if unreal.EditorAssetLibrary.does_asset_exist(package):
            raise RuntimeError("HOLD: native asset already registered: "+name)
        task=unreal.AssetImportTask()
        task.set_editor_property("filename",str(project/SOURCE_DIR/(name+".wav")))
        task.set_editor_property("destination_path",DEST_PACKAGE)
        task.set_editor_property("destination_name",name)
        task.set_editor_property("replace_existing",False)
        task.set_editor_property("automated",True)
        task.set_editor_property("save",True)
        task_list.append(task)
    unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks(task_list)
    saved={}
    for name,task in zip(HASHES,task_list):
        asset=unreal.EditorAssetLibrary.load_asset(DEST_PACKAGE+"/"+name)
        disk=project/DEST_DIR/(name+".uasset")
        if not asset or not isinstance(asset,unreal.SoundWave) or not disk.is_file():
            raise RuntimeError("HOLD: imported SoundWave missing: "+name)
        if not task.get_editor_property("imported_object_paths"):
            raise RuntimeError("HOLD: import task did not report asset: "+name)
        if digest(project/SOURCE_DIR/(name+".wav"))!=HASHES[name]:
            raise RuntimeError("HOLD: original audio altered by native import")
        saved[name]={"source_sha256":HASHES[name],
                     "native_asset_sha256":digest(disk),
                     "native_asset_package":DEST_PACKAGE+"/"+name,
                     "bytes":disk.stat().st_size}
    result.update(status="FOUR_NATIVE_SOUNDWAVES_IMPORTED_NOT_PIE_AUDIO_PLAYBACK",
                  exact_head=head,assets=saved,native_sound_waves=4)
    receipt=project/RECEIPT
    receipt.parent.mkdir(parents=True,exist_ok=True)
    with receipt.open("x",encoding="utf-8") as f:
        json.dump(result,f,indent=2)
        f.write("\n")
    unreal.log("TSTSS_FOUR_ORIGINAL_NATIVE_REVIEW_SFX_IMPORTED_NOT_PIE")
    return result

def main(args=None):
    parser=argparse.ArgumentParser(description=__doc__)
    group=parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--validate",action="store_true")
    group.add_argument("--build",action="store_true")
    opt=parser.parse_args(args)
    print(json.dumps(build() if opt.build else plan(),indent=2))

if __name__=="__main__":
    main()
