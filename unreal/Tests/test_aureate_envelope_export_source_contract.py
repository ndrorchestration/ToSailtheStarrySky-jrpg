"""Source contracts for the Unreal envelope exporter and its host runner.

No Unreal needed: the exporter is executed against a minimal fake `unreal` module
so its record shape, read-only behaviour and refusals are tested on any machine.
This is NOT a native run; the first Neontic run is still OPEN.
"""
import ast
import hashlib
import importlib.util
import json
import math
import os
import sys
import tempfile
import types
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / "Tools"
sys.path.insert(0, str(TOOLS))
sys.path.insert(0, str(Path(__file__).resolve().parent))
EXPORTER = TOOLS / "export_aureate_envelopes_native.py"
RUNNER = TOOLS / "run_aureate_envelope_export_native.py"

import aureate_envelope_records as rec  # noqa: E402
import test_aureate_envelope_records as fx  # noqa: E402

FORBIDDEN_CALLS = {
    "save_current_level", "save_all_dirty_levels", "save_asset", "save_packages",
    "save_loaded_asset", "spawn_actor_from_class", "spawn_actor_from_object",
    "destroy_actor", "set_actor_location", "set_actor_label", "set_actor_transform",
    "set_actor_rotation", "set_actor_scale3d", "delete_asset", "rename_asset",
    "import_asset_tasks", "duplicate_asset", "new_level", "build_light_maps",
}


def calls_in(path):
    tree = ast.parse(path.read_text(encoding="utf8"))
    names = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            f = node.func
            names.add(f.attr if isinstance(f, ast.Attribute) else getattr(f, "id", ""))
    return names


class StaticContractTests(unittest.TestCase):
    def test_exporter_never_mutates_anything(self):
        self.assertFalse(calls_in(EXPORTER) & FORBIDDEN_CALLS)

    def test_exporter_has_required_gates(self):
        text = EXPORTER.read_text(encoding="utf8")
        for needle in ("Refusing to overwrite", "ALLOWED_MAP_PREFIX", "EXPECTED_ENGINE_PREFIX",
                       "Map file changed while exporting", "EXPORT_PASS_UNVERIFIED"):
            self.assertIn(needle, text)
        self.assertNotIn("Starbourne", text.replace("does not touch Starbourne content", ""))

    def test_exporter_does_not_import_converter_or_verifier(self):
        text = EXPORTER.read_text(encoding="utf8")
        self.assertNotIn("aureate_envelope_records", text.replace("aureate_envelope_records.py, which", ""))
        self.assertNotIn("import aureate_swept_clearance", text)

    def test_runner_gates_and_no_overwrite(self):
        text = RUNNER.read_text(encoding="utf8")
        for needle in ("MIN_RAM_GIB = 4.2", "MIN_DISK_GIB = 14", "-NullRHI", "refuse concurrency",
                       "Refusing to overwrite", "win32"):
            self.assertIn(needle, text)
        self.assertNotIn("shell=True", text)


def make_fake_unreal(snapshot, map_sha_holder):
    """Fake `unreal` that serves a SYNTHETIC snapshot back through the engine API."""
    u = types.ModuleType("unreal")
    u.logs = []
    u.log = u.logs.append

    class StaticMeshComponent:
        pass

    class Vec:
        def __init__(self, v):
            self.x, self.y, self.z = v

    class Quat:
        def __init__(self, wxyz):
            self.w, self.x, self.y, self.z = wxyz

    class Bounds:
        def __init__(self, origin, extent):
            self.origin, self.box_extent = Vec(origin), Vec(extent)

    class Mesh:
        def __init__(self, lb):
            self.lb = lb

        def get_bounds(self):
            return Bounds(self.lb["origin"], self.lb["extent"])

    class Comp(StaticMeshComponent):
        def __init__(self, lb):
            self.static_mesh = Mesh(lb)

    class Transform:
        def __init__(self, a):
            self.translation, self.rotation, self.scale3d = Vec(a["location"]), Quat(a["rotation_quat"]), Vec(a["scale"])

    class Actor:
        def __init__(self, a):
            self.a = a

        def get_components_by_class(self, cls):
            return [Comp(self.a["local_bounds"])]

        def get_actor_transform(self):
            return Transform(self.a)

        def get_actor_label(self):
            return self.a["label"]

        def get_actor_bounds(self, only_colliding):
            w = self.a["world_aabb"]
            return Vec(w["origin"]), Vec(w["extent"])

    actors = [Actor(a) for a in snapshot["actors"]]

    class Levels:
        loaded = []

        def load_level(self, path):
            self.loaded.append(path)
            return True

    levels = Levels()

    class Actors:
        def get_all_level_actors(self):
            return actors

    u.StaticMeshComponent = StaticMeshComponent
    u.LevelEditorSubsystem = Levels
    u.EditorActorSubsystem = Actors
    u.get_editor_subsystem = lambda cls: levels if cls is Levels else Actors()
    u.SystemLibrary = types.SimpleNamespace(get_engine_version=lambda: "5.8.4-fake")
    u.Paths = types.SimpleNamespace(project_dir=lambda: map_sha_holder["project_dir"])
    u.levels = levels
    return u


class FakeEditorExportTests(unittest.TestCase):
    def run_exporter(self, snapshot, env, content=b"umap-bytes"):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        project = Path(tmp.name)
        mapdir = project / "Content" / "TSTSS" / "Review"
        mapdir.mkdir(parents=True)
        (mapdir / "TestMap.umap").write_bytes(content)
        holder = {"project_dir": str(project) + os.sep}
        fake = make_fake_unreal(snapshot, holder)
        old = {k: os.environ.get(k) for k in env}
        os.environ.update(env)
        sys.modules["unreal"] = fake
        try:
            spec = importlib.util.spec_from_file_location("exporter_under_test", EXPORTER)
            module = importlib.util.module_from_spec(spec)
            try:
                spec.loader.exec_module(module)
                error = None
            except RuntimeError as exc:
                error = exc
        finally:
            sys.modules.pop("unreal", None)
            for k, v in old.items():
                if v is None:
                    os.environ.pop(k, None)
                else:
                    os.environ[k] = v
        return fake, project, error

    def env(self, out, form="Skybourne", game_map="/Game/TSTSS/Review/TestMap"):
        return {"TSTSS_ENVELOPE_MAP": game_map, "TSTSS_ENVELOPE_FORM": form,
                "TSTSS_ENVELOPE_OUT": str(out)}

    def test_export_feeds_converter_and_leaves_map_untouched(self):
        a, b = fx.pair()
        out_dir = tempfile.TemporaryDirectory()
        self.addCleanup(out_dir.cleanup)
        outs = []
        for snap in (a, b):
            out = Path(out_dir.name) / f"{snap['form']}.json"
            fake, project, error = self.run_exporter(snap, self.env(out, snap["form"]))
            self.assertIsNone(error)
            self.assertEqual(fake.levels.loaded, ["/Game/TSTSS/Review/TestMap"])
            outs.append(json.loads(out.read_text(encoding="utf8")))
            map_file = project / "Content" / "TSTSS" / "Review" / "TestMap.umap"
            self.assertEqual(outs[-1]["map_sha256"], hashlib.sha256(map_file.read_bytes()).hexdigest())
            self.assertEqual(outs[-1]["units"], "cm")
        # Same fake bytes -> same sha; real maps differ per form, so patch the second sha.
        outs[1]["map_sha256"] = "c" * 64
        cfg = rec.build_config(outs[0], outs[1], required_clearance=0.0)
        self.assertEqual(len(cfg["wings"]), 4)
        self.assertTrue(all(math.isfinite(x) for w in cfg["wings"] for x in w["pose_to"]["position"]))

    def test_refuses_overwrite(self):
        a, _ = fx.pair()
        with tempfile.TemporaryDirectory() as d:
            out = Path(d) / "exists.json"
            out.write_text("keep", encoding="utf8")
            _, _, error = self.run_exporter(a, self.env(out))
            self.assertIsNotNone(error)
            self.assertEqual(out.read_text(encoding="utf8"), "keep")

    def test_refuses_map_outside_review_folder_and_unlabelled_form(self):
        a, _ = fx.pair()
        with tempfile.TemporaryDirectory() as d:
            out = Path(d) / "x.json"
            _, _, error = self.run_exporter(a, self.env(out, game_map="/Game/Other/TestMap"))
            self.assertIsNotNone(error)
            self.assertFalse(out.exists())
            _, _, error = self.run_exporter(a, self.env(out, form=""))
            self.assertIsNotNone(error)
            self.assertFalse(out.exists())


class CombineRunnerTests(unittest.TestCase):
    def setUp(self):
        spec = importlib.util.spec_from_file_location("runner_under_test", RUNNER)
        self.runner = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(self.runner)
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.dir = Path(self.tmp.name)

    def write(self, name, obj):
        p = self.dir / name
        p.write_text(json.dumps(obj), encoding="utf8")
        return str(p)

    def combine(self, a, b, out="result.json", clearance="0"):
        return self.runner.main(["combine", "--from-snapshot", self.write("a.json", a),
                                 "--to-snapshot", self.write("b.json", b),
                                 "--clearance", clearance, "--out", str(self.dir / out)])

    def test_clear_exit_zero_and_result_written_once(self):
        a, b = fx.pair()
        self.assertEqual(self.combine(a, b), 0)
        data = json.loads((self.dir / "result.json").read_text(encoding="utf8"))
        self.assertEqual(data["result"]["verdict"], "CLEAR_UNDER_ENVELOPES")
        self.assertTrue(data["config"]["provisional"])
        with self.assertRaises(RuntimeError):
            self.runner.cmd_combine(types.SimpleNamespace(
                from_snapshot=str(self.dir / "a.json"), to_snapshot=str(self.dir / "b.json"),
                clearance=0.0, out=str(self.dir / "result.json")))

    def test_invalid_snapshot_fails_closed_without_result_file(self):
        a, b = fx.pair()
        a["actors"] = [x for x in a["actors"] if "FORE_PORT" not in x["label"]]
        self.assertEqual(self.combine(a, b, out="bad.json"), 1)
        self.assertFalse((self.dir / "bad.json").exists())

    def test_unreadable_file_fails_closed(self):
        code = self.runner.main(["combine", "--from-snapshot", str(self.dir / "nope.json"),
                                 "--to-snapshot", str(self.dir / "nope2.json"),
                                 "--out", str(self.dir / "o.json")])
        self.assertEqual(code, 1)

    def test_nonclear_verdict_exits_nonzero(self):
        a, b = fx.pair()
        for act in b["actors"]:
            if "FORE_PORT" in act["label"]:
                act["location"][1] = 0.0
                act["world_aabb"] = fx.world_aabb(act["location"], act["rotation_quat"], act["scale"],
                                                  act["local_bounds"]["origin"], act["local_bounds"]["extent"])
        self.assertEqual(self.combine(a, b, out="rej.json"), 1)

    def test_export_refuses_off_windows(self):
        if sys.platform == "win32":
            self.skipTest("Windows host")
        code = self.runner.main(["export", "--map", "/Game/TSTSS/Review/X", "--form", "Skybourne",
                                 "--out", str(self.dir / "s.json")])
        self.assertEqual(code, 2)


if __name__ == "__main__":
    unittest.main()
