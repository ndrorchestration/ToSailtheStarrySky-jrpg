"""Source-only guard and mutation tests for Ender private native host runner.

Does not start an editor, read user files, modify .uassets, or build the game.
"""
import ast
from pathlib import Path
import unittest

HERE = Path(__file__).resolve().parent
HOST = (HERE / "run_ender_private_retarget_native.py").read_text(encoding="utf8")


class PrivateEnderNativeHostContracts(unittest.TestCase):
    def test_guarded_runner_parses_on_any_host(self):
        ast.parse(HOST)

    def test_explicit_mode_selection_no_implicit_ik_authoring(self):
        for s in (
            'choice = parser.add_mutually_exclusive_group(required=True)',
            'choice.add_argument("--audit", action="store_true")',
            'choice.add_argument("--create-rigs", action="store_true")',
            'os.environ.get("TSTSS_PRIVATE_IK_CREATE") == "1"',
            '"NO_EXPLICIT_CREATE_OPT_IN"',
        ):
            with self.subTest(s=s):
                self.assertIn(s, HOST)

    def test_user_owned_unreal_process_prevents_start(self):
        for s in (
            '"unrealeditor.exe"', '"unrealeditor-cmd.exe"',
            '"unrealbuildtool.exe"', '"livecodingconsole.exe"',
            '"shadercompileworker.exe"',
            'require(not ue_processes(), "OTHER_UNREAL_PROCESS_ACTIVE")',
        ):
            self.assertIn(s, HOST)
        self.assertNotIn("Get-Process | Stop-Process", HOST)

    def test_own_pid_only_is_stopped_at_safety_floor(self):
        self.assertIn('owned_child = subprocess.Popen(', HOST)
        self.assertIn('if owned_child.poll() is None:', HOST)
        self.assertIn('str(owned_child.pid)', HOST)
        self.assertIn('"taskkill", "/F", "/T", "/PID"', HOST)
        self.assertIn('RUNTIME_RAM_FLOOR_GIB = 2.5', HOST)
        self.assertIn('RUNTIME_DISK_FLOOR_GIB = 14.3', HOST)
        self.assertIn('STARTUP_RAM_GIB = 6.5', HOST)
        self.assertIn('STARTUP_DISK_GIB = 16.5', HOST)
        self.assertIn('ram_gib() >= STARTUP_RAM_GIB', HOST)
        self.assertIn('disk_gib() >= STARTUP_DISK_GIB', HOST)

    def test_readonly_protected_ini_restore_even_on_launch_failure(self):
        self.assertIn('PROJECT / "Config/DefaultEngine.ini"', HOST)
        self.assertIn('PROJECT / "Config/DefaultInput.ini"', HOST)
        self.assertIn('UPROJECT,', HOST)
        self.assertIn('prepared_readonly = []', HOST)
        self.assertIn('try:\n        # Keep permission changes inside', HOST)
        self.assertIn('prepared_readonly.append(path)', HOST)
        self.assertIn('for path in reversed(prepared_readonly):', HOST)
        self.assertIn('os.chmod(path, modes[path])', HOST)
        self.assertIn('receipt["protected_unchanged"]', HOST)
        self.assertIn('receipt["tracked_clean"]', HOST)
        self.assertIn('receipt["head_unchanged"]', HOST)
        for forbidden in ("git reset --hard", "git checkout --force",
                          "shutil.rmtree(", "os.remove("):
            self.assertNotIn(forbidden, HOST)

    def test_same_head_recent_native_audit_required_to_author(self):
        for s in (
            '"MISSING_PREVIOUS_AUDIT"',
            'data.get("source_head") == head',
            '"NATIVE_RETARGET_INPUTS_VALIDATED_NOT_RETARGETED"',
            'created.tzinfo is not None',
            '"PRIOR_AUDIT_STALE"',
            '"PRIVATE_OUTPUT_NOT_IGNORED"',
            '"REVIEW_RIG_ALREADY_PRESENT"',
        ):
            self.assertIn(s, HOST)

    def test_host_gate_has_real_resource_readings_and_run_id(self):
        self.assertIn('"status": "HOST_ADMITTED"', HOST)
        self.assertIn('"run_id": run_id', HOST)
        self.assertIn('"ram_start_gib": round(ram_gib(), 3)', HOST)
        self.assertIn('"disk_start_gib": round(disk_gib(), 3)', HOST)
        self.assertIn('env["TSTSS_PRIVATE_IK_RUN_ID"] = run_id', HOST)
        self.assertIn('env.pop("TSTSS_PRIVATE_IK_CREATE", None)', HOST)

    def test_private_batch_retarget_mode_requires_exact_reopen_and_no_files(self):
        for gate in (
            'choice.add_argument("--retarget-clips", action="store_true")',
            'os.environ.get("TSTSS_PRIVATE_ANIM_RETARGET") == "1"',
            '"NO_EXPLICIT_ANIMATION_OPT_IN"',
            '"RIG_REOPEN_OR_MOTION_HOLD_NOT_CURRENT"',
            '"RIG_REOPEN_AUDIT_STALE"',
            '"PRIVATE_ANIMATION_NOT_GIT_EXCLUDED"',
            '"PRIVATE_ANIMATION_ALREADY_EXISTS"',
            '"retarget-clips": "animation_candidate_receipt.json"',
            '"retarget-clips": "retarget_private_ender_locomotion_candidates.py"',
            '"retarget-clips":',
            'env.pop("TSTSS_PRIVATE_ANIM_RETARGET", None)',
            'receipt["clip_files_verified"] = clip_files_valid',
            'clip_files_valid,',
            '"PRIVATE_RETARGET_CLIP_CANDIDATES_CREATED_NOT_PLAYBACK_ACCEPTED"',
        ):
            with self.subTest(gate=gate):
                self.assertIn(gate, HOST)

    def test_no_stale_success_or_missing_ik_asset_success(self):
        self.assertIn('artifact.stat().st_mtime >= launched_at - 1.0', HOST)
        self.assertIn('receipt["native_report_fresh"]', HOST)
        self.assertIn('report.get("source_head") == head', HOST)
        self.assertIn('len(saved) == len(names)', HOST)
        self.assertIn('rig_files_valid', HOST)
        self.assertIn('report.get("status") == wanted_status', HOST)
        self.assertIn('"HOLD_NARROW_NATIVE_EVIDENCE"', HOST)
        self.assertIn('"art_approved": False', HOST)

    def test_negative_mutations_to_safety_gates_detectable(self):
        for required in (
            'require(not ue_processes(), "OTHER_UNREAL_PROCESS_ACTIVE")',
            'ram_gib() >= STARTUP_RAM_GIB',
            'disk_gib() >= STARTUP_DISK_GIB',
            'receipt["protected_unchanged"]',
            'receipt["native_report_fresh"]',
            'report.get("source_head") == head',
            'rig_files_valid',
        ):
            with self.subTest(required=required):
                self.assertIn(required, HOST)
                self.assertNotIn(
                    required,
                    HOST.replace(required, "/* removed guard */")
                    if HOST.count(required) == 1 else
                    HOST.replace(required, "/* removed guard */"),
                )


if __name__ == "__main__":
    unittest.main()
