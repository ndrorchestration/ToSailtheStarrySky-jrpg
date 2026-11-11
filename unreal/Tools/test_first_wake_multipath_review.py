"""Fail-closed source-only reconciliation of independent First Wake review lanes.

This does NOT perform an Unreal build, execute PIE, or approve cinematics.
"""
import copy
import json
import re
import unittest
from pathlib import Path

UNREAL = Path(__file__).resolve().parents[1]
MANIFEST = UNREAL / "DataSource/Integration/FirstWakeMultipath.review.json"
EXPECTED_TRACKS = {
    "gameplay", "cinematics", "lighting", "maps", "objects", "equipment",
    "magic", "atmosphere", "enemies",
}
ENEMY_NAMES = {
    "TSTSS.Slice.Enemies.RegistryAndAdmission",
    "TSTSS.Slice.Enemies.RealTurnManagerBoundary",
    "TSTSS.Slice.Enemies.AuthorizedAIAndFallback",
}

def validate(data):
    errors = []
    auth = (
        "pie_verified", "gpu_approved", "creator_approved", "merged_to_main",
        "release_authorized",
    )
    if data.get("schema") != "tstss.firstwake.multipath.v1":
        errors.append("schema")
    if data.get("engine") != "UE 5.8.4" or data.get("integration_scope") != "REVIEW_ONLY":
        errors.append("engine-or-scope")
    if data.get("native_at_integrated_head") != "NOT_TESTED":
        errors.append("native-overclaim")
    if any(data.get(k) is not False for k in auth):
        errors.append("authority-overclaim")
    if data.get("pre_splashdown_party") != ["Ender", "Ionia"]:
        errors.append("pre-splashdown-chronology")
    if data.get("post_splashdown_first_recruit") != "Lyra":
        errors.append("lyra-chronology")
    if data.get("disallowed_slice_party") != ["Reson", "Aepex"]:
        errors.append("future-cast-boundary")
    if data.get("restricted_ship_form") != "Starbourne":
        errors.append("starbourne-boundary")
    if data.get("min_pretransition_observed_flotation_seconds", 0) < 2.0:
        errors.append("observed-water-gate")
    keys = data.get("keys") or {}
    if keys != {
        "pie_save": "F6", "pie_load": "F9",
        "prelaunch_continue": "F7", "standalone_save": "F5",
    } or len(set(keys.values())) != 4:
        errors.append("input-ownership")
    resources = data.get("resources") or {}
    if resources.get("native_free_ram_gib", 0) < 5 or resources.get("graphics_free_ram_gib", 0) < 6.5:
        errors.append("physical-ram-gate")
    if resources.get("min_free_disk_gib", 0) < 14 or resources.get("forbid_parallel_unreal_editor_or_live_coding") is not True:
        errors.append("native-process-disk-gate")
    handoff = data.get("convergence_handoff_update") or {}
    if (handoff.get("pr") != 792 or
        handoff.get("head_sha") != "ab69db6abd06fab35a0ab105f8c3b3539699c9cb" or
        handoff.get("source_review_only") is not True or
        handoff.get("key_file") != "unreal/DataSource/Cinematics/FirstWakeRuntimeShotHandoffs.review.json" or
        not (UNREAL.parent / str(handoff.get("key_file", ""))).is_file()):
        errors.append("convergence-handoff-binding")
    probe = data.get("shore_review_probe") or {}
    if (probe.get("package") != "/Game/TSTSS/Review/MultipathV1/L_VS06_ShoreMagicEnemyGear_Review"
            or probe.get("source_map") != "/Game/TSTSS/Review/VerticalSlice/VS06_SplashdownShore"
            or probe.get("requires_verified_exact_head_35_native_tests") is not True
            or probe.get("independent_native_readback") != "unreal/Tools/verify_first_wake_multipath_shore.py"
            or any(probe.get(k) is not False for k in ("native_staged", "independent_readback_established", "pie_verified", "creator_approved"))
            or any(not (UNREAL.parent / str(probe.get(k, ""))).is_file()
                   for k in ("compositor", "host_gate", "independent_native_readback"))):
        errors.append("shore-probe-authority-or-source")
    tracks = data.get("source_tracks") or []
    if len(tracks) != len(EXPECTED_TRACKS) or {x.get("id") for x in tracks} != EXPECTED_TRACKS:
        errors.append("track-coverage")
    if len({x.get("pr") for x in tracks}) != len(tracks):
        errors.append("duplicate-pr")
    for track in tracks:
        if not re.fullmatch("[0-9a-f]{40}", str(track.get("source_sha", ""))):
            errors.append("invalid-source-sha")
        rel = str(track.get("key_file", ""))
        if not rel.startswith("unreal/") or ".." in Path(rel).parts:
            errors.append("unsafe-source-path")
        elif not (UNREAL.parent / rel).is_file():
            errors.append("missing-source-file")
    preflight = (UNREAL.parent / ".github/workflows/unreal-source-preflight.yml").read_text(encoding="utf-8")
    for glob in (
        "unreal/DataSource/**", "unreal/Content/TSTSS/Review/VerticalSlice/**",
        "unreal/ArtSource/VerticalSliceObjectsV1/**",
        "unreal/ArtSource/PartyEquipment/**",
        "unreal/Content/TSTSS/Review/PartyEquipment/**",
    ):
        if ("'" + glob + "'") not in preflight:
            errors.append("source-preflight-trigger-coverage")
    registry = (UNREAL / "Tools/Verify-Unreal.ps1").read_text(encoding="utf-8")
    names = re.findall(r"^\s*'(TSTSS\.[^']+)'", registry, re.M)
    if data.get("required_native_names") != 35 or len(names) != 35 or len(set(names)) != 35:
        errors.append("native-registration-count")
    if not ENEMY_NAMES.issubset(set(names)):
        errors.append("enemy-native-registration")
    if len(list((UNREAL / "ArtSource/VerticalSliceObjectsV1").glob("*.glb"))) != 22:
        errors.append("object-source-count")
    if len(list((UNREAL / "ArtSource/PartyEquipment/Generated").glob("*.glb"))) != 14:
        errors.append("equipment-source-count")
    if len(list((UNREAL / "Content/TSTSS/Review/VerticalSlice").glob("VS*.umap"))) != 6:
        errors.append("map-count")
    return errors


class CrossPathReviewContract(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = json.loads(MANIFEST.read_text(encoding="utf-8"))

    def test_all_nine_lanes_and_native_registry(self):
        self.assertEqual([], validate(self.data))

    def test_refuses_another_agent_build_before_wait_mutex_queue(self):
        source = (UNREAL / "Tools/Verify-Unreal.ps1").read_text(encoding="utf-8")
        self.assertIn("function Assert-NoOtherUnrealBuild", source)
        self.assertIn("Assert-NoOtherUnrealBuild -Phase 'initial'", source)
        self.assertIn("Assert-NoOtherUnrealBuild -Phase $Phase", source)
        self.assertIn("UnrealBuildTool", source)
        self.assertIn("Build\\.bat", source)
        self.assertIn("Get-CimInstance Win32_Process", source)
        self.assertIn("already active", source)
        self.assertLess(source.index("Assert-NoOtherUnrealBuild -Phase 'initial'"),
                        source.index("& $BuildTool ToSailTheStarrySkyEditor"))
        workflow = (UNREAL.parent / ".github/workflows/unreal-source-preflight.yml").read_text(encoding="utf-8")
        self.assertIn("run: ./unreal/Tools/Test-NativeBuildOverlapFixtures.ps1", workflow)
        self.assertIn("7 PowerShell verification scripts parse", workflow)
        self.assertTrue((UNREAL / "Tools/Test-NativeBuildOverlapFixtures.ps1").is_file())

    def test_native_automation_protects_tracked_unreal_configs(self):
        verifier = (UNREAL / "Tools/Verify-Unreal.ps1").read_text(encoding="utf-8")
        self.assertIn("Config/DefaultEngine.ini", verifier)
        self.assertIn("Config/DefaultInput.ini", verifier)
        self.assertIn("$ConfigGuards = @()", verifier)
        self.assertIn("OldReadOnly = $File.IsReadOnly", verifier)
        self.assertIn("BeforeSha256 = (Get-FileHash", verifier)
        self.assertIn(".IsReadOnly = $true", verifier)
        self.assertIn(".IsReadOnly = $Guard.OldReadOnly", verifier)
        self.assertIn("finally {", verifier)
        self.assertIn("if ($After -ne $Guard.BeforeSha256)", verifier)
        self.assertIn("Tracked Unreal source config changed", verifier)
        self.assertLess(verifier.index(".IsReadOnly = $true"),
                        verifier.index("& $EditorCmd $Project -unattended"))
        self.assertLess(verifier.index("& $EditorCmd $Project -unattended"),
                        verifier.index(".IsReadOnly = $Guard.OldReadOnly"))

    def test_native_build_rechecks_race_and_disk_before_automation(self):
        # A second Editor/UBT lane started after the initial admission on
        # 2026-11-10; no build-only/source pass may bypass this second gate.
        source = (UNREAL / "Tools/Verify-Unreal.ps1").read_text(encoding="utf-8")
        self.assertIn("function Assert-TSTSSNativeSessionStillSafe", source)
        self.assertIn("Assert-TSTSSNativeSessionStillSafe -Phase 'immediately-before-build'", source)
        self.assertIn("Assert-TSTSSNativeSessionStillSafe -Phase 'after-build-before-native-tests'", source)
        self.assertLess(source.index("Assert-TSTSSNativeSessionStillSafe -Phase 'after-build-before-native-tests'"),
                        source.index("if ($SkipTests)"))
        self.assertIn("$CurrentDisk.Free -lt (14 * 1GB)", source)
        self.assertIn("$CurrentFreeKiB -lt 5242880", source)
        self.assertIn("$NowHead -ne $GitHead", source)
        self.assertIn("$Dirty.Count -gt 0", source)

    def test_native_compile_regression_restore_and_f7_confirmation(self):
        # Exact errors witnessed by UE 5.8.4 UBT at bb6855e (not merely
        # theoretical lint rules). Keep the restored public declaration unique.
        milestone = (UNREAL / "Source/ToSailTheStarrySky/Public/TSTSSMilestoneActor.h").read_text(encoding="utf-8")
        explorer_h = (UNREAL / "Source/ToSailTheStarrySky/Public/TSTSSExplorerCharacter.h").read_text(encoding="utf-8")
        explorer_cpp = (UNREAL / "Source/ToSailTheStarrySky/Private/TSTSSExplorerCharacter.cpp").read_text(encoding="utf-8")
        self.assertEqual(1, milestone.count(
            "void ReconcileReviewCollisionAfterRestore(const UTSTSSFirstWakeState* State);"))
        self.assertEqual(1, explorer_h.count(
            "ETSTSSFirstWakeBeat PendingReviewContinueBeat ="))
        self.assertRegex(explorer_cpp, r"GetCurrentBeat\(\)\s*==\s*PendingReviewContinueBeat\s*&&")
        self.assertRegex(explorer_cpp, r"PendingReviewContinueBeat\s*=\s*FirstWakeState->GetCurrentBeat\(\);")
        self.assertNotIn("bPendingReviewContinueBeat", explorer_cpp)

    def test_cannot_claim_approval_or_native_success(self):
        for field in ("pie_verified", "gpu_approved", "creator_approved",
                      "merged_to_main", "release_authorized"):
            changed = copy.deepcopy(self.data)
            changed[field] = True
            self.assertIn("authority-overclaim", validate(changed))
        changed = copy.deepcopy(self.data)
        changed["native_at_integrated_head"] = "PASS"
        self.assertIn("native-overclaim", validate(changed))

    def test_deny_unearned_progression_and_input_collision(self):
        changed = copy.deepcopy(self.data)
        changed["pre_splashdown_party"].append("Lyra")
        self.assertIn("pre-splashdown-chronology", validate(changed))
        changed = copy.deepcopy(self.data)
        changed["keys"]["prelaunch_continue"] = "F6"
        self.assertIn("input-ownership", validate(changed))
        changed = copy.deepcopy(self.data)
        changed["min_pretransition_observed_flotation_seconds"] = 1.9
        self.assertIn("observed-water-gate", validate(changed))

    def test_fail_closed_when_lane_missing_or_resource_gate_weakens(self):
        changed = copy.deepcopy(self.data)
        changed["convergence_handoff_update"]["source_review_only"] = False
        self.assertIn("convergence-handoff-binding", validate(changed))
        changed = copy.deepcopy(self.data)
        changed["shore_review_probe"]["native_staged"] = True
        self.assertIn("shore-probe-authority-or-source", validate(changed))
        changed = copy.deepcopy(self.data)
        changed["source_tracks"].pop()
        self.assertIn("track-coverage", validate(changed))
        changed = copy.deepcopy(self.data)
        changed["resources"]["native_free_ram_gib"] = 4.0
        self.assertIn("physical-ram-gate", validate(changed))
        changed = copy.deepcopy(self.data)
        changed["resources"]["forbid_parallel_unreal_editor_or_live_coding"] = False
        self.assertIn("native-process-disk-gate", validate(changed))


if __name__ == "__main__":
    unittest.main()
