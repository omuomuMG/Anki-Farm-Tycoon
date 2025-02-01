import json
from ..constants import ADDON_DIR
from ..models.animal_type import AnimalType

# utils/save_manager.py
import json
import os
from pathlib import Path


class SaveManager:
    @classmethod
    def save_game(cls, game_state):
        try:

            save_dir = Path(__file__).parent.parent
            save_path = save_dir / "game_save.json"


            serializable_state = {
                "money": game_state["money"],
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

            # JSONファイルに保存
            with open(save_path, 'w', encoding='utf-8') as f:
                json.dump(serializable_state, f, ensure_ascii=False, indent=2)
            print(f"Game saved successfully to {save_path}")

        except Exception as e:
            print(f"Error saving game: {e}")
            raise

    @classmethod
    def load_game(cls):
        """ゲームの状態を読み込む"""
        try:
            save_dir = Path(__file__).parent.parent
            save_path = save_dir / "game_save.json"

            if not save_path.exists():
                print("No save file found")
                return None

            with open(save_path, 'r', encoding='utf-8') as f:
                save_data = json.load(f)
            print(f"Game loaded successfully from {save_path}")
            return save_data

        except Exception as e:
            print(f"Error loading game: {e}")
            return None