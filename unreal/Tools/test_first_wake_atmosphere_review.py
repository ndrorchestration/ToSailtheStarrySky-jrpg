"""Engine-free, fail-closed boundaries for review-only UE atmosphere staging."""
import importlib.util
import pathlib
import unittest

TOOL = pathlib.Path(__file__).with_name("build_first_wake_atmosphere_review.py")
spec = importlib.util.spec_from_file_location("first_wake_atmosphere", TOOL)
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)


class EditorAssets:
    occupied = False
    source_available = True

    @classmethod
    def does_directory_exist(cls, path):
        return cls.occupied

    @classmethod
    def does_asset_exist(cls, path):
        return cls.source_available


class EditorLoading:
    dirty_map = []
    dirty_content = []

    @classmethod
    def get_dirty_map_packages(cls):
        return cls.dirty_map

    @classmethod
    def get_dirty_content_packages(cls):
        return cls.dirty_content


class MockUnreal:
    EditorAssetLibrary = EditorAssets
    EditorLoadingAndSavingUtils = EditorLoading

    @staticmethod
    def load_class(parent, path):
        return "compiled_class" if path == m.NATIVE_CLASS else None

    @staticmethod
    def load_asset(path):
        return "native_cloud" if path == m.CLOUD_ASSET else None


class AtmosphereBoundaryTests(unittest.TestCase):
    def setUp(self):
        EditorAssets.occupied = False
        EditorAssets.source_available = True
        EditorLoading.dirty_map = []
        EditorLoading.dirty_content = []

    def test_contract_manifest(self):
        result = m.validate()
        self.assertEqual(len(result["weather_modes"]), 7)
        self.assertEqual(result["native_stage"], "NOT_RUN")
        self.assertTrue(result["review_map"].startswith("/Game/TSTSS/Review/"))
        self.assertNotEqual(result["source_map"], result["review_map"])
        self.assertEqual(len(result["shader_sha256"]), 64)

    def test_native_dependencies_accepted(self):
        self.assertEqual(m.preflight(MockUnreal), ("compiled_class", "native_cloud"))

    def test_existing_review_assets_fail_closed(self):
        EditorAssets.occupied = True
        with self.assertRaisesRegex(RuntimeError, "occupied"):
            m.preflight(MockUnreal)

    def test_unsaved_map_fails_closed(self):
        EditorLoading.dirty_map = ["other_author_work"]
        with self.assertRaisesRegex(RuntimeError, "unsaved map"):
            m.preflight(MockUnreal)

    def test_unsaved_content_fails_closed(self):
        EditorLoading.dirty_content = ["other_author_asset"]
        with self.assertRaisesRegex(RuntimeError, "unsaved content"):
            m.preflight(MockUnreal)

    def test_missing_source_map_fails_closed(self):
        EditorAssets.source_available = False
        with self.assertRaisesRegex(RuntimeError, "source First Wake"):
            m.preflight(MockUnreal)

    def test_compiled_actor_required(self):
        class MissingActor(MockUnreal):
            @staticmethod
            def load_class(parent, path):
                return None
        with self.assertRaisesRegex(RuntimeError, "Compiled"):
            m.preflight(MissingActor)

    def test_cloud_material_required(self):
        class MissingCloud(MockUnreal):
            @staticmethod
            def load_asset(path):
                return None
        with self.assertRaisesRegex(RuntimeError, "volumetric cloud"):
            m.preflight(MissingCloud)

    def test_no_runtime_story_or_save_mutations_in_builder(self):
        source = TOOL.read_text(encoding="utf-8")
        for forbidden in ("open_level(", "save_game_to_slot(", "delete_asset(SOURCE_MAP"):
            self.assertNotIn(forbidden, source)
        self.assertIn("duplicate_asset(SOURCE_MAP, MAP)", source)
        self.assertIn("save_map(world, MAP)", source)


if __name__ == "__main__":
    unittest.main()
