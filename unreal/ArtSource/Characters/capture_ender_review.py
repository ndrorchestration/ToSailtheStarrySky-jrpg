"""Review-only Ender screenshot runner for a *running* UE 5.8.4 Editor.

The screenshot task needs subsequent Editor ticks. Run from the Python console
or Tools > Execute Python Script, NOT with -ExecutePythonScript (which exits on
script completion). No production project, image, or asset is changed.

Run without Unreal: python capture_ender_review.py --self-test
"""
import hashlib
import json
import re
import struct
import sys
import time
import traceback
import zlib
from pathlib import Path

SOURCE_SHA = "d516f68b49301cd04ae17c58eeeb2ca318b5f9b6a42f300be773fb62a7a3d6f2"
MESH_PATH = "/Game/ArtLookdev/Characters/Ender/Ender/StaticMeshes/Ender.Ender"
LEVEL_PATH = "/Game/EnderReviewScene_63dbfac"
RECEIPT_NAME = "ender_63dbfac_native_20261101.json"
ACTOR_LABEL = "Ender_STATIC_CANDIDATE_NOT_CANON"
# Viewpoint names are provisional, not verified anatomical directions.
CAMERAS = ("front_plus_x", "side_plus_y", "rear_minus_x", "threequarter")
RESOLUTION = (800, 600)


def require(condition, message):
    if not condition:
        raise ValueError(message)


def valid_session(value):
    require(bool(re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_-]{0,39}", value)),
            "Unsafe capture session label")
    return value


def validate_project_root(root):
    root = Path(root).resolve()
    require(root.name.startswith("TSTSS-Cast643-UEImport-Sandbox-"),
            "Review capture refuses non-isolated project")
    require((root / "Cast643Review.uproject").is_file(),
            "Missing exact isolated Cast643Review.uproject")
    return root


def verify_import_receipt(record):
    require(record.get("status") == "IMPORT_PASS_REVIEW_PENDING",
            "Prior native import was not successful")
    require(record.get("kind") == "STATIC_LOOKDEV_ONLY", "Not a static review import")
    require(record.get("requested") == "Ender", "Prior import is not Ender-only")
    require(len(record.get("imported", [])) == 1, "Unexpected imported actor count")
    mesh = record["imported"][0]
    require(mesh.get("sha256") == SOURCE_SHA, "Ender source bytes differ")
    require(mesh.get("mesh") == MESH_PATH, "Wrong Unreal asset path")
    xyz = mesh.get("bounds_cm", [])
    require(len(xyz) == 3 and 150 <= xyz[2] <= 230 and
            xyz[2] > 1.5 * max(xyz[0], xyz[1]), "Unreal Z-up extent gate")
    return xyz


def inspect_png(path, expected_size=RESOLUTION):
    """Validate PNG chunks/CRC and pixels' dimensions, not visual fidelity."""
    data = Path(path).read_bytes()
    require(data[:8] == b"\x89PNG\r\n\x1a\n", "Missing PNG signature")
    index = 8
    size = None
    image_chunks = 0
    ended = False
    while index + 12 <= len(data):
        length = struct.unpack_from(">I", data, index)[0]
        kind = data[index+4:index+8]
        end = index + 12 + length
        require(end <= len(data), "PNG chunk exceeds file")
        blob = data[index+8:index+8+length]
        stored = struct.unpack_from(">I", data, index+8+length)[0]
        require((zlib.crc32(kind + blob) & 0xffffffff) == stored,
                "PNG chunk CRC mismatch")
        if kind == b"IHDR":
            require(size is None and len(blob) == 13, "Invalid PNG header")
            size = struct.unpack_from(">II", blob, 0)
        if kind == b"IDAT":
            image_chunks += 1
        index = end
        if kind == b"IEND":
            ended = True
            break
    require(ended and index == len(data) and image_chunks > 0, "Incomplete PNG")
    require(size == expected_size, "Unexpected screenshot resolution")
    return {"bytes": len(data), "width": size[0], "height": size[1],
            "sha256": hashlib.sha256(data).hexdigest(),
            "png_crc_valid": True, "visual_acceptance": "NOT_ESTABLISHED"}


def run_self_test():
    import tempfile
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp) / "TSTSS-Cast643-UEImport-Sandbox-QA"
        root.mkdir()
        (root / "Cast643Review.uproject").write_text("{}")
        require(validate_project_root(root) == root.resolve(), "Review root self-test")
        for bad in ("../escape", "", "bad spaces", "a"*41):
            try:
                valid_session(bad)
            except ValueError:
                pass
            else:
                raise AssertionError("Unsafe session accepted: " + repr(bad))
        for other in (Path(tmp), root / "nested"):
            try:
                validate_project_root(other)
            except ValueError:
                pass
            else:
                raise AssertionError("Non-review project accepted")
        good = {"status": "IMPORT_PASS_REVIEW_PENDING",
                "kind": "STATIC_LOOKDEV_ONLY", "requested": "Ender",
                "imported": [{"sha256": SOURCE_SHA, "mesh": MESH_PATH,
                              "bounds_cm": [56.316, 31.6, 185.8]}]}
        verify_import_receipt(good)
        for field, value in (("sha256", "not-the-source"),
                             ("mesh", "/Game/Playable/Ender"),
                             ("bounds_cm", [185.8, 31.6, 56.316])):
            broken = json.loads(json.dumps(good))
            broken["imported"][0][field] = value
            try:
                verify_import_receipt(broken)
            except ValueError:
                pass
            else:
                raise AssertionError("Invalid import receipt accepted")
        def chunk(kind, payload):
            return (struct.pack(">I", len(payload)) + kind + payload +
                    struct.pack(">I", zlib.crc32(kind + payload) & 0xffffffff))
        tiny = (b"\x89PNG\r\n\x1a\n" +
                chunk(b"IHDR", struct.pack(">IIBBBBB", 1, 1, 8, 2, 0, 0, 0)) +
                chunk(b"IDAT", zlib.compress(b"\x00\xff\x00\x00")) +
                chunk(b"IEND", b""))
        path = root / "test.png"
        path.write_bytes(tiny)
        require(inspect_png(path, (1, 1))["png_crc_valid"], "PNG self-test")
        damaged = bytearray(tiny)
        damaged[-5] ^= 1
        path.write_bytes(damaged)
        try:
            inspect_png(path, (1, 1))
        except ValueError:
            pass
        else:
            raise AssertionError("Damaged PNG accepted")
    print("CAST_NATIVE_CAPTURE_POLICY_PASS (engine-free, no screenshots)")


def main_unreal():
    import builtins
    import unreal
    root = validate_project_root(unreal.Paths.project_dir())
    valid_session("Ender")
    require("5.8.4" in unreal.SystemLibrary.get_engine_version(),
            "Review requires Unreal 5.8.4")
    source_receipt = root / "Saved" / "CharacterLookdev" / RECEIPT_NAME
    xyz = verify_import_receipt(json.loads(source_receipt.read_text(encoding="utf-8")))
    require(unreal.EditorAssetLibrary.does_asset_exist(MESH_PATH),
            "Imported Ender asset missing")
    loaded = unreal.EditorAssetLibrary.load_asset(MESH_PATH)
    require(isinstance(loaded, unreal.StaticMesh), "Not a static mesh")
    require(unreal.EditorAssetLibrary.does_asset_exist(LEVEL_PATH),
            "Review-only level not present: create it in isolated sandbox first")
    require(not getattr(builtins, "_tstss_capture643_active", False),
            "A capture is already running in this Editor")
    require(hasattr(unreal, "register_slate_post_tick_callback"),
            "Unreal Slate post-tick callback unavailable")
    level = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
    require(level.load_level(LEVEL_PATH), "Could not load review-only level")
    actors = unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors()
    subjects = [a for a in actors if a.get_actor_label() == ACTOR_LABEL]
    require(len(subjects) == 1, "Expected one isolated Ender lookdev actor")
    component = subjects[0].get_editor_property("static_mesh_component")
    require(component.get_editor_property("static_mesh").get_path_name() == MESH_PATH,
            "Review actor references wrong mesh")
    cameras = {a.get_actor_label().removeprefix("ReviewCamera_"): a
               for a in actors if isinstance(a, unreal.CameraActor) and
               a.get_actor_label().startswith("ReviewCamera_")}
    require(set(cameras) == set(CAMERAS), "Unexpected camera labels or count")

    out = root / "Saved" / "CharacterLookdev" / "NativeCaptures" / "ender643_review01"
    require(not out.exists(), "Capture destination already exists; never overwrite")
    out.mkdir(parents=True)
    result = {"kind": "STATIC_LOOKDEV_NATIVE_CAPTURE", "status": "IN_PROGRESS",
              "source_sha256": SOURCE_SHA, "imported_bounds_cm": xyz,
              "engine": unreal.SystemLibrary.get_engine_version(),
              "level": LEVEL_PATH, "mesh": MESH_PATH, "views": [],
              "visual_acceptance": "NOT_ESTABLISHED", "render_quality": "UNREVIEWED"}
    receipt = out / "capture_receipt.json"

    def save():
        receipt.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")

    save()
    class CaptureRunner:
        def __init__(self):
            self.index = 0
            self.task = None
            self.frame = 0
            self.start = time.monotonic()
            self.completed_at = None
            self.handle = None

        def close(self, status, error=None):
            result["status"] = status
            if error is not None:
                result["error"] = str(error)
            save()
            if self.handle is not None:
                unreal.unregister_slate_post_tick_callback(self.handle)
            builtins._tstss_capture643_active = False
            builtins._tstss_capture643_runner = None
            unreal.log("TSTSS_ENDER_CAPTURE " + status + " " + str(receipt))

        def tick(self, delta):
            try:
                self.frame += 1
                if time.monotonic() - self.start > 240:
                    self.close("TIMED_OUT")
                    return
                if self.frame < 10:
                    return
                if self.task is None:
                    name = CAMERAS[self.index]
                    filename = out / (name + ".png")
                    self.task = unreal.AutomationLibrary.take_high_res_screenshot(
                        RESOLUTION[0], RESOLUTION[1], str(filename),
                        camera=cameras[name], delay=0.0, force_game_view=True)
                    require(self.task and self.task.is_valid_task(),
                            "Unreal screenshot task invalid: " + name)
                    self.completed_at = None
                    unreal.log("TSTSS_CAPTURE_REQUESTED " + name)
                    return
                if not self.task.is_task_done():
                    return
                name = CAMERAS[self.index]
                filename = out / (name + ".png")
                try:
                    evidence = inspect_png(filename)
                except (OSError, ValueError):
                    # Let async screenshot writes flush after task completion.
                    if self.completed_at is None:
                        self.completed_at = self.frame
                    if self.frame - self.completed_at < 90:
                        return
                    raise
                result["views"].append({"camera": name, "file": filename.name,
                                        **evidence})
                save()
                self.index += 1
                self.task = None
                if self.index == len(CAMERAS):
                    self.close("CAPTURE_FILES_PRESENT_UNREVIEWED")
            except Exception:
                unreal.log_error("TSTSS_ENDER_CAPTURE_ERROR " + traceback.format_exc())
                self.close("FAILED", traceback.format_exc())

    runner = CaptureRunner()
    builtins._tstss_capture643_active = True
    builtins._tstss_capture643_runner = runner
    try:
        runner.handle = unreal.register_slate_post_tick_callback(runner.tick)
    except Exception:
        builtins._tstss_capture643_active = False
        builtins._tstss_capture643_runner = None
        result["status"] = "FAILED_TO_REGISTER_TICK"
        result["error"] = traceback.format_exc()
        save()
        raise
    unreal.log("TSTSS_ENDER_CAPTURE_ARMED " + str(out))


if __name__ == "__main__":
    if "--self-test" in sys.argv:
        run_self_test()
    else:
        main_unreal()
