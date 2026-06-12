import json
import os
from pathlib import Path
from aqt import mw
from ..constants import VERSION


class SaveManager:
    DEFAULT_SETTINGS = {
        "auto_start": False,
        "dock_widget": False,
    }

    @classmethod
    def get_save_path(cls):
        profile_dir = Path(mw.pm.profileFolder())
        save_path = profile_dir / "collection.media/_anki_farm_tycoon_save.json"
        return save_path

    @classmethod
    def get_settings_path(cls):
        profile_dir = Path(mw.pm.profileFolder())
        save_path = profile_dir / "collection.media/_anki_farm_tycoon_settings.json"
        return save_path

    # Save location for version 1.0.0
    @classmethod
    def get_old_save_path(cls):
        profile_dir = Path(mw.pm.profileFolder())
        save_path = profile_dir / "anki_farm_tycoon_save.json"
        return save_path

    @classmethod
    def save_game(cls, game_state):
        try:
            save_path = cls.get_save_path()

            serializable_state = {
                "Version": VERSION,
                "money": game_state["money"],
                "previous_money": game_state["previous_money"],
                "unlocked_fields": game_state["unlocked_fields"],
                "easy_streak": game_state.get("easy_streak", 0),
                "unicorn_cooldown": game_state.get("unicorn_cooldown", 0),
                "unicorn_summoned_for_streak": game_state.get("unicorn_summoned_for_streak", False),
                "fair_active": game_state.get("fair_active", False),
                "stats": game_state["stats"],
                "fields": [
                    [
                        {
                            "x": field["x"],
                            "y": field["y"],
                            "animal": field["animal"]
                        }
                        for field in row
                    ]
                    for row in game_state["fields"]
                ],
                "breeds": game_state["breeds"],
                "employees": game_state["employees"]
            }

            with open(save_path, 'w', encoding='utf-8') as f:
                json.dump(serializable_state, f, ensure_ascii=False, indent=2)

        except Exception as e:
            print(f"Error saving game: {e}")
            raise

    @classmethod
    def load_game(cls):
        """load game state"""
        try:
            save_path = cls.get_save_path()

            if not save_path.exists():
                print("No save file found at collection.media folder")
                save_path = cls.get_old_save_path()
                if not save_path.exists():
                    print("No save file found at profile folder")
                    return None

            with open(save_path, 'r', encoding='utf-8') as f:
                save_data = json.load(f)
            return save_data

        except Exception as e:
            print(f"Error loading game: {e}")
            return None

    @classmethod
    def load_settings(cls):
        """Load addon settings, filling missing keys with defaults."""
        settings = cls.DEFAULT_SETTINGS.copy()
        try:
            settings_path = cls.get_settings_path()
            if settings_path.exists():
                with open(settings_path, 'r', encoding='utf-8') as f:
                    saved_settings = json.load(f)
                    if isinstance(saved_settings, dict):
                        settings.update({
                            key: bool(saved_settings.get(key, default_value))
                            for key, default_value in cls.DEFAULT_SETTINGS.items()
                        })
        except Exception as e:
            print(f"Error loading settings: {e}")
        return settings

    @classmethod
    def save_settings(cls, settings):
        """Save addon settings."""
        try:
            settings_path = cls.get_settings_path()
            settings_path.parent.mkdir(parents=True, exist_ok=True)
            serializable_settings = cls.DEFAULT_SETTINGS.copy()
            serializable_settings.update({
                key: bool(settings.get(key, default_value))
                for key, default_value in cls.DEFAULT_SETTINGS.items()
            })

            with open(settings_path, 'w', encoding='utf-8') as f:
                json.dump(serializable_settings, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Error saving settings: {e}")
            raise
