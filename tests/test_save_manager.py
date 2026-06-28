import json
import io
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

from tests._bootstrap import import_target, set_profile_folder


save_manager_module = import_target("utils.save_manager")
SaveManager = save_manager_module.SaveManager


def game_state():
    return {
        "money": 2345,
        "previous_money": 2200,
        "unlocked_fields": 2,
        "easy_streak": 4,
        "unicorn_cooldown": 8,
        "unicorn_summoned_for_streak": True,
        "fair_active": True,
        "stats": {"CHICKEN": {"sold": 1, "dead": 0}},
        "fields": [[{"x": 0, "y": 0, "animal": None}]],
        "breeds": {"CHICKEN": {"level": 1, "is_unlocked": True}},
        "employees": {"A": {"name": "A", "x": 0, "y": 0}},
    }


class SaveManagerTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.profile = Path(self.temp_dir.name)
        (self.profile / "collection.media").mkdir()
        set_profile_folder(self.profile)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_game_state_round_trip(self):
        SaveManager.save_game(game_state())
        restored = SaveManager.load_game()

        self.assertEqual(restored["money"], 2345)
        self.assertEqual(restored["easy_streak"], 4)
        self.assertTrue(restored["fair_active"])
        self.assertEqual(restored["employees"]["A"]["name"], "A")

    def test_load_game_falls_back_to_legacy_location(self):
        legacy_state = {"money": 99}
        SaveManager.get_old_save_path().write_text(json.dumps(legacy_state), encoding="utf-8")
        with redirect_stdout(io.StringIO()):
            restored = SaveManager.load_game()
        self.assertEqual(restored, legacy_state)

    def test_settings_fill_missing_defaults(self):
        SaveManager.get_settings_path().write_text(
            json.dumps({"auto_start": True}),
            encoding="utf-8",
        )
        self.assertEqual(
            SaveManager.load_settings(),
            {"auto_start": True, "dock_widget": False},
        )

    def test_settings_round_trip_coerces_values_to_bool(self):
        SaveManager.save_settings({"auto_start": 1, "dock_widget": 0})
        self.assertEqual(
            SaveManager.load_settings(),
            {"auto_start": True, "dock_widget": False},
        )


if __name__ == "__main__":
    unittest.main()
