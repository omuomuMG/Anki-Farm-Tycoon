import json
import os
from pathlib import Path
from aqt import mw
from ..constants import VERSION


class SaveManager:
    @classmethod
    def get_save_path(cls):
        profile_dir = Path(mw.pm.profileFolder())
        save_path = profile_dir / "collection.media/_anki_farm_tycoon_save.json"
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
