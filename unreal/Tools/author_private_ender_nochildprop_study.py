"""UE5.8 private A/B: duplicate Manny-to-Ender retargeter and disable child root propagation.

NEVER changes original retargeter, clips, maps, gameplay or asset authority.
New ignored retargeter/clip binaries are NOT approved; measured spine pose
must pass independently. Requires clean source and exact host opt-in.
"""
import datetime
import hashlib
import json
import math
import os
from pathlib import Path
import subprocess
import traceback
import unreal

PROJECT = Path(unreal.Paths.project_dir()).resolve()
REPO = PROJECT.parent
ROOT = "/Game/TSTSS/Review/Characters/EnderRetarget_NONCANONICAL"
SOURCE = ROOT + "/MannequinWalkSources_PRIVATE"
OUTPUT = ROOT + "/DirectionalNoChildPropV1_PRIVATE"
ORIGINAL_RETARGET = ROOT + "/RTG_MannyToEnder_NONCANONICAL"
DUPLICATE_RETARGET = ROOT + "/RTG_MannyToEnder_NoChildPropV1_PRIVATE"
SUFFIX = "_EnderNoChildPropV1_PRIVATE"
SOURCE_MESH = "/Game/Characters/Mannequins/Meshes/SKM_Manny_Simple"
TARGET_MESH = ("/Game/ArtLookdev/Characters/"
               "Genesis9MergedFBXRigReview_20261109_NONCANONICAL/"
               "Genesis9_BaseShirtShorts_MergedRig_REVIEW")
CORRECTED_FORWARD = ROOT + "/Animations_SpineFixV1_PRIVATE/MF_Unarmed_Walk_Fwd_EnderSpineFixV1_PRIVATE"
CLIPS = {
 "MF_Unarmed_Walk_Bwd": (606821,"ae0c2ee1c1178fd1b9493f6c327e52d10a3d6bbde29eae54dcb07c13a27dcf46"),
 "MF_Unarmed_Walk_Left": (486552,"81500e4fcdd9ae9aa6433e652e67dea8f9dd9fa7b9ef1714e29f6ab0a1bb9d97"),
 "MF_Unarmed_Walk_Right": (491934,"f5922b4e632351353224b32f719af97e85512ab4f6553b15315cf14ad04f675f"),
}
REPORT = {"status":"NOT_STARTED","created":[],
          "normal_retargeter_modified":False,"original_sequences_modified":False,
          "default_gameplay_modified":False,"art_or_playback_accepted":False}


def require(cond,name):
 if not cond:raise RuntimeError("HOLD_ENDER_NO_CHILD_PROP_"+name)


def git(*args):
 r=subprocess.run(["git","-C",str(REPO),*args],capture_output=True,
                  text=True,timeout=20,check=True)
 return r.stdout.rstrip("\r\n")


def sha(p):
 return hashlib.sha256(p.read_bytes()).hexdigest()


def admitted():
 head=os.environ.get("TSTSS_NOCHILDPROP_EXPECTED_HEAD")
 receipt=os.environ.get("TSTSS_NOCHILDPROP_RECEIPT")
 require(head and len(head)==40 and git("rev-parse","HEAD")==head,"HEAD")
 require(os.getenv("TSTSS_PRIVATE_NOCHILDPROP_CREATE")=="1","OPT_IN")
 require(unreal.SystemLibrary.get_engine_version().startswith("5.8.4-"),"ENGINE")
 known={"unreal/Config/DefaultEngine.ini","unreal/Config/DefaultInput.ini"}
 drift=git("status","--porcelain").splitlines()
 require(all(line.startswith(" M ") and line[3:] in known for line in drift),
         "UNEXPECTED_EDITOR_SOURCE_DRIFT")
 target=Path(receipt).resolve() if receipt else None
 require(target is not None and
         (PROJECT/"Saved/MigrationEvidence").resolve() in target.parents and
         target.name=="native-result.json" and target.parent.is_dir() and
         not target.exists(),"RECEIPT")
 for name,(size,digest) in CLIPS.items():
  src=PROJECT/"Content"/SOURCE.replace("/Game/","")/(name+".uasset")
  require(src.is_file() and src.stat().st_size==size and sha(src)==digest,
          "SOURCE_HASH_"+name)
  require(isinstance(unreal.load_asset(SOURCE+"/"+name),unreal.AnimSequence),
          "SOURCE_ASSET_"+name)
  dest=PROJECT/"Content"/OUTPUT.replace("/Game/","")/(name+SUFFIX+".uasset")
  require(not dest.exists() and
          not unreal.EditorAssetLibrary.does_asset_exist(OUTPUT+"/"+name+SUFFIX),
          "OUTPUT_EXISTS_"+name)
  relative="unreal/Content"+OUTPUT.replace("/Game","")+"/"+name+SUFFIX+".uasset"
  require(subprocess.run(["git","-C",str(REPO),"check-ignore","--no-index","-q",relative],
                         timeout=20).returncode==0,"OUTPUT_NOT_IGNORED")
 existing=PROJECT/"Content"/DUPLICATE_RETARGET.replace("/Game/","")
 require(not existing.with_suffix(".uasset").exists() and
         not unreal.EditorAssetLibrary.does_asset_exist(DUPLICATE_RETARGET),
         "RETARGETER_EXISTS")
 return head,target


def spine_max_offset(seq):
 opts=unreal.AnimPoseEvaluationOptions()
 errs=[]
 for frac in (0,.1,.2,.3,.4,.5,.6,.7,.8,.9):
  pose=seq.get_anim_pose_at_time(float(seq.get_play_length())*frac,opts)
  p=pose.get_bone_pose("spine1",unreal.AnimPoseSpaces.LOCAL).translation
  q=pose.get_ref_bone_pose("spine1",unreal.AnimPoseSpaces.LOCAL).translation
  errs.append(math.sqrt((p.x-q.x)**2+(p.y-q.y)**2+(p.z-q.z)**2))
 return {"max_spine1_local_offset_cm":round(max(errs),3),
         "median_spine1_local_offset_cm":round(sorted(errs)[len(errs)//2],3),
         "ten_sample_local_offset_cm":[round(x,3) for x in errs]}


def run():
 head,out=admitted()
 REPORT["source_sha"]=head
 source_mesh=unreal.load_asset(SOURCE_MESH)
 target_mesh=unreal.load_asset(TARGET_MESH)
 original_rtg=unreal.load_asset(ORIGINAL_RETARGET)
 forward=unreal.load_asset(CORRECTED_FORWARD)
 require(isinstance(source_mesh,unreal.SkeletalMesh) and
         isinstance(target_mesh,unreal.SkeletalMesh) and
         isinstance(original_rtg,unreal.IKRetargeter) and
         isinstance(forward,unreal.AnimSequence),"PREEXISTING_ASSETS")
 target_skeleton=target_mesh.get_editor_property("skeleton")
 require(target_skeleton and
         forward.get_editor_property("skeleton")==target_skeleton,"TARGET_SKELETON")
 ref=spine_max_offset(forward)
 REPORT["corrected_forward_reference"]=ref
 require(ref["max_spine1_local_offset_cm"]<=5.0,"FORWARD_REFERENCE_DRIFT")
 # Must duplicate rather than mutate a shared IK retargeter/animation.
 copied=unreal.EditorAssetLibrary.duplicate_asset(ORIGINAL_RETARGET,DUPLICATE_RETARGET)
 require(isinstance(copied,unreal.IKRetargeter) and
         copied.get_path_name().startswith(ROOT+"/"),"DUPLICATED_RETARGETER")
 ctrl=unreal.IKRetargeterController.get_controller(copied)
 require(ctrl is not None and ctrl.get_num_retarget_ops()==5 and
         str(ctrl.get_op_name(3))=="Root Motion","EXACT_ROOT_MOTION_OP")
 op=ctrl.get_op_controller(3)
 settings=op.get_settings()
 require(bool(settings.get_editor_property("enabled")) and
         bool(settings.get_editor_property("propagate_to_non_retargeted_children")),
         "EXPECTED_ORIGINAL_CHILD_PROPAGATION")
 settings.set_editor_property("propagate_to_non_retargeted_children",False)
 op.set_settings(settings)
 check=ctrl.get_op_controller(3).get_settings()
 require(not bool(check.get_editor_property("propagate_to_non_retargeted_children")),
         "DISABLE_CHILD_PROPAGATION_NOT_APPLIED")
 require(unreal.EditorAssetLibrary.save_loaded_asset(copied,only_if_is_dirty=True),
         "NEW_PRIVATE_RETARGETER_SAVE")
 REPORT["retargeter_copy"]=DUPLICATE_RETARGET
 REPORT["only_retarget_change"]="Root Motion / propagate_to_non_retargeted_children True -> False"
 REPORT["status"]="RETARGETING_CHILD_PROPAGATION_STUDY_IN_PROGRESS"
 out.write_text(json.dumps(REPORT,indent=2),encoding="utf8")
 source_skeleton=source_mesh.get_editor_property("skeleton")
 data=[]
 for name in CLIPS:
  seq=unreal.load_asset(SOURCE+"/"+name)
  require(seq.get_editor_property("skeleton")==source_skeleton,"SOURCE_SKELETON_"+name)
  item=unreal.EditorAssetLibrary.find_asset_data(SOURCE+"/"+name)
  require(item and item.is_valid(),"SOURCE_DATA_"+name)
  data.append(item)
 inputs=unreal.IKRetargetBatchOperationInputs(
  assets_to_retarget=data,source_mesh=source_mesh,target_mesh=target_mesh,
  ik_retarget_asset=copied,target_path=OUTPUT,use_source_path=False,
  suffix=SUFFIX,include_referenced_assets=False,overwrite_existing_files=False)
 output_assets=unreal.IKRetargetBatchOperation.run_batch_retarget(inputs)
 require(len(output_assets)==3,"OUTPUT_COUNT")
 found=set()
 for item in output_assets:
  name=str(item.asset_name)
  require(name in {n+SUFFIX for n in CLIPS} and name not in found,
          "OUTPUT_NAME")
  object_path=str(item.package_name)+"."+name
  require(object_path.startswith(OUTPUT+"/"),"OUTPUT_NAMESPACE")
  seq=unreal.load_asset(object_path)
  require(isinstance(seq,unreal.AnimSequence) and
          seq.get_editor_property("skeleton")==target_skeleton,"OUTPUT_SKELETON")
  require(unreal.EditorAssetLibrary.save_loaded_asset(seq,only_if_is_dirty=True),
          "OUTPUT_SAVE_"+name)
  file=PROJECT/"Content"/OUTPUT.replace("/Game/","")/(name+".uasset")
  require(file.is_file() and file.stat().st_size>1000,"OUTPUT_MISSING_"+name)
  metrics=spine_max_offset(seq)
  REPORT["created"].append({
    "name":name,"sha256":sha(file),"bytes":file.stat().st_size,
    "root_motion_enabled":bool(seq.get_editor_property("enable_root_motion")),
    "duration_s":float(seq.get_play_length()),"spine_metrics":metrics,
    "spine_candidate_gate_pass":metrics["max_spine1_local_offset_cm"]<=10.0})
  found.add(name)
 require(len(found)==3,"OUTPUT_SET")
 REPORT["status"]=("SPINE_GEOMETRY_SCREEN_PASS_NOT_VISUAL" if
                   all(x["spine_candidate_gate_pass"] for x in REPORT["created"])
                   else "HOLD_SPINE_GEOMETRY_CHILDPROP_STUDY")


receipt=os.environ.get("TSTSS_NOCHILDPROP_RECEIPT")
try:run()
except BaseException:
 REPORT["status"]="HOLD_NOCHILDPROP_NATIVE_ERROR"
 REPORT["error"]=traceback.format_exc()[-5000:]
finally:
 REPORT["utc"]=datetime.datetime.now(datetime.timezone.utc).isoformat()
 if receipt and Path(receipt).parent.is_dir():
  Path(receipt).write_text(json.dumps(REPORT,indent=2),encoding="utf8")
 unreal.log("TSTSS_ENDER_NO_CHILDPROP_STUDY "+REPORT["status"])
 unreal.SystemLibrary.quit_editor()
