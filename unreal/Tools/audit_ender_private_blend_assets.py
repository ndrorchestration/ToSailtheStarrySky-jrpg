"""Native Unreal 5.8.4 read-only verification of Ender's local private AnimBP/BlendSpace.

Launch only by a guarded host with:
  TSTSS_ENDER_AUDIT_EXPECTED_HEAD=<40-digit sha>
  TSTSS_ENDER_AUDIT_RECEIPT=<NEW path under project/Saved/MigrationEvidence>
No animation, map, source, configuration or native asset writes are authorized.
This checks asset custody/graph topology, NOT gameplay/visual quality or licensing.
"""
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import unreal

ROOT = "/Game/TSTSS/Review/Characters/EnderRetarget_NONCANONICAL"
BLEND = ROOT + "/BlendReview_PRIVATE/BS_EnderIdleWalkRun_V1_NONCANONICAL"
ABP = ROOT + "/BlendReview_PRIVATE/ABP_EnderIdleWalkRun_V1_PRIVATE"
CLIPS = [
    (ROOT + "/Animations/MM_Idle_EnderPreview_NONCANONICAL", 0.0),
    (ROOT + "/Animations_SpineFixV1_PRIVATE/MF_Unarmed_Walk_Fwd_EnderSpineFixV1_PRIVATE", 260.0),
    (ROOT + "/Animations_SpineFixV1_PRIVATE/MF_Unarmed_Jog_Fwd_EnderSpineFixV1_PRIVATE", 600.0),
]
EXPECTED_GRAPH_LINKS = [
    ("AnimGraph", "AnimGraphNode_BlendSpacePlayer", "Pose", "AnimGraphNode_Root", "Result"),
    ("AnimGraph", "K2Node_VariableGet", "SpeedCmS", "AnimGraphNode_BlendSpacePlayer", "X"),
    ("EventGraph", "K2Node_CallFunction", "ReturnValue", "K2Node_CallFunction", "self"),
    ("EventGraph", "K2Node_Event", "then", "K2Node_VariableSet", "execute"),
]


def need(condition, token):
    if not condition:
        raise RuntimeError("HOLD_ENDER_ASSET_AUDIT_" + token)


def pin(node, name, output):
    pins = node.list_output_pins() if output else node.list_input_pins()
    matches = [p for p in pins if str(unreal.BlueprintGraphPinLibrary.get_pin_name(p)) == name]
    need(len(matches) == 1, "PIN_" + name)
    return matches[0]


def linked(source, destination):
    return any(unreal.BlueprintGraphPinLibrary.is_same_native_pin(source, p)
               for p in unreal.BlueprintGraphPinLibrary.list_connected_pins(destination))


def inspect_graphs(bp, blend):
    anim = unreal.BlueprintEditorLibrary.find_graph(bp, "AnimGraph")
    event = unreal.BlueprintEditorLibrary.find_event_graph(bp)
    need(anim is not None and event is not None, "GRAPHS_MISSING")
    ag = unreal.BlueprintGraphEditor.get_graph_editor(anim)
    eg = unreal.BlueprintGraphEditor.get_graph_editor(event)
    an = list(ag.list_all_nodes())
    en = list(eg.list_all_nodes())
    need(len(an) == 3 and len(en) == 5, "TOPOLOGY_COUNT")
    def one(nodes, klass, title=None):
        found = [n for n in nodes if isinstance(n, getattr(unreal, klass))
                 and (title is None or n.get_node_title() == title)]
        need(len(found) == 1, "NODE_" + klass + (title or ""))
        return found[0]
    player = one(an, "AnimGraphNode_BlendSpacePlayer")
    need(player.get_editor_property("node").get_editor_property("blend_space") == blend, "PLAYER_ASSET")
    root = one(an, "AnimGraphNode_Root")
    getter = one(an, "K2Node_VariableGet")
    update = one(en, "K2Node_Event")
    owner = one(en, "K2Node_CallFunction", "TryGetPawnOwner")
    velocity = one(en, "K2Node_CallFunction", "GetVelocity")
    length = one(en, "K2Node_CallFunction", "Vector Length XY")
    setter = one(en, "K2Node_VariableSet")
    connections = [
        (pin(player, "Pose", True), pin(root, "Result", False), "POSE_OUTPUT"),
        (pin(getter, "SpeedCmS", True), pin(player, "X", False), "SPEED_INPUT"),
        (pin(owner, "ReturnValue", True), pin(velocity, "self", False), "OWNER_VELOCITY"),
        (pin(velocity, "ReturnValue", True), pin(length, "A", False), "VELOCITY_XY"),
        (pin(length, "ReturnValue", True), pin(setter, "SpeedCmS", False), "XY_SPEED_SET"),
        (pin(update, "then", True), pin(setter, "execute", False), "UPDATE_EXEC"),
    ]
    for source, destination, name in connections:
        need(linked(source, destination), "LINK_" + name)
    need(not list(ag.list_nodes_with_errors()) and not list(eg.list_nodes_with_errors()),
         "GRAPH_NODES_WITH_ERRORS")
    klass = unreal.BlueprintEditorLibrary.generated_class(bp)
    need(klass is not None and klass.get_name() == "ABP_EnderIdleWalkRun_V1_PRIVATE_C",
         "GENERATED_CLASS")
    cdo = unreal.get_default_object(klass)
    need(cdo.get_editor_property("root_motion_mode") == unreal.RootMotionMode.IGNORE_ROOT_MOTION,
         "ROOT_MOTION_MODE")
    return [name for _, _, name in connections]


def audit():
    project = Path(unreal.Paths.project_dir()).resolve()
    repository = project.parent
    envhead = os.environ.get("TSTSS_ENDER_AUDIT_EXPECTED_HEAD", "")
    need(re.fullmatch(r"[a-f0-9]{40}", envhead) is not None, "SHA_REQUIRED")
    current = subprocess.run(["git", "-C", str(repository), "rev-parse", "HEAD"],
                             capture_output=True, text=True, check=True).stdout.strip()
    need(current == envhead, "WRONG_COMMIT")
    # Guarded PowerShell host proves clean exact HEAD before launch and after exit.
    # Editor startup may modify only two allowlisted Unreal Config defaults;
    # host verifies and restores those exact paths after process exit.
    need(unreal.SystemLibrary.get_engine_version().startswith("5.8.4-"), "ENGINE_VERSION")

    path = os.environ.get("TSTSS_ENDER_AUDIT_RECEIPT")
    need(bool(path), "EVIDENCE_DESTINATION_REQUIRED")
    output = Path(path).resolve()
    root = (project / "Saved" / "MigrationEvidence").resolve()
    need(root in output.parents, "RECEIPT_OUTSIDE_EVIDENCE")
    need(output.suffix == ".json" and output.parent.is_dir() and not output.exists(),
         "RECEIPT_NOT_NEW")

    mesh = unreal.EditorAssetLibrary.load_asset(BLEND)
    bp = unreal.EditorAssetLibrary.load_asset(ABP)
    need(isinstance(mesh, unreal.BlendSpace1D), "BLEND_MISSING")
    need(isinstance(bp, unreal.AnimBlueprint), "ANIMBP_MISSING")
    clips = []
    for object_path, speed in CLIPS:
        anim = unreal.EditorAssetLibrary.load_asset(object_path)
        need(isinstance(anim, unreal.AnimSequence), "INPUT_CLIP_MISSING")
        clips.append(anim)
    skeleton = clips[0].get_editor_property("skeleton")
    need(skeleton is not None and all(x.get_editor_property("skeleton") == skeleton for x in clips),
         "CLIP_SKELETON_MISMATCH")
    need(mesh.get_editor_property("skeleton") == skeleton or
         mesh.get_editor_property("target_skeleton") == skeleton, "BLEND_SKELETON")
    need(bp.get_editor_property("target_skeleton") == skeleton, "ANIMBP_SKELETON")
    samples = list(mesh.get_editor_property("sample_data"))
    need(len(samples) == 3, "BLEND_SAMPLE_COUNT")
    for index, ((_, expected_speed), clip) in enumerate(zip(CLIPS, clips)):
        item = samples[index]
        need(item.get_editor_property("animation") == clip, "SAMPLE_CLIP")
        need(abs(item.get_editor_property("sample_value").x - expected_speed) < .01,
             "SAMPLE_SPEED")
        need(abs(item.get_editor_property("rate_scale") - 1.0) < .001, "SAMPLE_RATE")
    links = inspect_graphs(bp, mesh)

    asset_files = [
        project / "Content/TSTSS/Review/Characters/EnderRetarget_NONCANONICAL/BlendReview_PRIVATE/BS_EnderIdleWalkRun_V1_NONCANONICAL.uasset",
        project / "Content/TSTSS/Review/Characters/EnderRetarget_NONCANONICAL/BlendReview_PRIVATE/ABP_EnderIdleWalkRun_V1_PRIVATE.uasset",
    ]
    inventory = []
    for filename in asset_files:
        need(filename.is_file() and filename.stat().st_size > 1024, "PRIVATE_BINARY_MISSING")
        relative = filename.relative_to(repository).as_posix()
        ignored = subprocess.run(["git", "-C", str(repository), "check-ignore", "-q",
                                  "--no-index", relative]).returncode == 0
        need(ignored, "PRIVATE_BINARY_NOT_IGNORED")
        inventory.append({"relative_path": relative,
                          "sha256": hashlib.sha256(filename.read_bytes()).hexdigest(),
                          "bytes": filename.stat().st_size})
    receipt = {
        "status": "EXACT_HEAD_NATIVE_PRIVATE_ASSET_AUDIT_PASS",
        "source_sha": envhead,
        "engine": unreal.SystemLibrary.get_engine_version(),
        "private_assets": inventory,
        "skeleton": skeleton.get_path_name(),
        "clips": [{"path": path, "speed_cm_s": speed} for path, speed in CLIPS],
        "verified_graph_links": links,
        "runtime_sample_cache": "NOT_CHECKED_ASSET_REQUIRES_PRIVATE_RESAMPLED_RUNTIME",
        "scene_visual_art_or_licensing_acceptance": "NOT_ESTABLISHED",
        "assets_modified_by_audit": False
    }
    output.write_text(json.dumps(receipt, indent=2), encoding="utf8")
    unreal.log("TSTSS_ENDER_PRIVATE_BLEND_ASSET_AUDIT_PASS " + str(output))


audit()
