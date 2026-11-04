"""Source-only safety/route checks for a not-yet-run full Unreal Editor actor pilot."""
from pathlib import Path
import ast
import unittest

ROOT=Path(__file__).resolve().parents[1]
TOOLS=ROOT/"Tools"


class FullEditorActorPilotSourceTests(unittest.TestCase):
    def source(self,name):
        path=TOOLS/name
        text=path.read_text(encoding="utf8")
        ast.parse(text,filename=str(path))
        return text

    def test_pilot_is_new_disposable_project(self):
        s=self.source("aureate_v4_full_editor_actor_probe.py")
        self.assertIn("AureateActorPilot",s)
        self.assertIn("AUREATE_ONE_ACTOR_PILOT_ONLY",s)
        self.assertIn("Paths.project_dir()",s)
        self.assertIn("if lib.does_asset_exist(LEVEL)",s)
        self.assertIn("NATIVE_FULL_EDITOR_ONE_ACTOR_AND_MAP_SAVE_PASS",s)

    def test_actor_creation_is_real_editor_and_one_map(self):
        s=self.source("aureate_v4_full_editor_actor_probe.py")
        self.assertIn("unreal.EditorActorSubsystem",s)
        self.assertIn("spawn_actor_from_class(unreal.StaticMeshActor",s)
        self.assertIn("level.save_current_level()",s)
        self.assertIn("len(found)!=1",s)
        self.assertIn("hashlib.sha256(mapfile.read_bytes())",s)

    def test_runner_uses_full_editor_not_headless_commandlet(self):
        s=self.source("run_aureate_v4_full_editor_actor_probe.py")
        self.assertIn("-ExecutePythonScript=",s)
        self.assertNotIn("-run=pythonscript",s)
        self.assertIn("EditorScriptingUtilities",s)
        self.assertIn("PythonScriptPlugin",s)
        self.assertIn("AureateActorPilot.uproject",s)

    def test_resource_gate_before_any_project_creation(self):
        s=self.source("run_aureate_v4_full_editor_actor_probe.py")
        self.assertLess(s.index("if free_ram()<4.2"),s.index("ROOT.mkdir()"))
        self.assertLess(s.index("shutil.disk_usage(ROOT.parent).free<14*1024**3"),
                        s.index("ROOT.mkdir()"))
        self.assertIn("if ROOT.exists():raise FileExistsError",s)
        self.assertIn("UnrealEditor-Cmd.exe",s)
        self.assertIn("MAX_SECONDS=180",s)

    def test_no_unrelated_session_kill_or_gameplay_promotion(self):
        for name in ("aureate_v4_full_editor_actor_probe.py",
                     "run_aureate_v4_full_editor_actor_probe.py"):
            s=self.source(name)
            for bad in ("taskkill /im", "Stop-Process", "request_form(", "OrbiterRequest",
                        "git push origin main", "subprocess.run(['taskkill'", "ResetLevel("):
                self.assertNotIn(bad,s)
        runner=self.source("run_aureate_v4_full_editor_actor_probe.py")
        self.assertIn("proc.terminate()",runner)
        self.assertIn("proc.kill()",runner)
        pilot=self.source("aureate_v4_full_editor_actor_probe.py")
        self.assertIn("story_starbourne_player_unlock",pilot)
        self.assertIn("production_map_modified",pilot)


if __name__=="__main__":
    unittest.main()
