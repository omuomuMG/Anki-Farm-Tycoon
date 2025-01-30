import json
from ..constants import ADDON_DIR
from ..models.animal_type import AnimalType

class SaveManager:
    SAVE_FILE = ADDON_DIR / "game_save.json"

    @classmethod
    def save_game(cls, game_state):
        try:
            save_data = {
                "money": game_state["money"],
                "unlocked_fields": game_state["unlocked_fields"],
                "stats": {
                    animal_type.name: stats
                    for animal_type, stats in game_state["stats"].items()
                    if animal_type != AnimalType.EMPTY
                },
                "fields": [
                    [
                        {
                            "x": field.x,
                            "y": field.y,
                            "animal": {
                                "type": field.animal.animal_type.name,
                                "growth": field.animal.growth,
                                "is_dead": field.animal.is_dead,
                                "has_product": field.animal.has_product,
                                "max_growth": field.animal.max_growth
                            } if field.animal else None
                        }
                        for field in row
                    ]
                    for row in game_state["fields"]
                ]
            }

            cls.SAVE_FILE.parent.mkdir(parents=True, exist_ok=True)

            with open(cls.SAVE_FILE, 'w', encoding='utf-8') as f:
                json.dump(save_data, f, ensure_ascii=False, indent=2)
            print(f"Game saved successfully to {cls.SAVE_FILE}")
        except Exception as e:
            print(f"Error saving game: {e}")

    @classmethod
    def load_game(cls):
        try:
            if not cls.SAVE_FILE.exists():
                print("No save file found, starting new game")
                return None

            if cls.SAVE_FILE.stat().st_size == 0:
                print("Save file is empty, starting new game")
                return None

            with open(cls.SAVE_FILE, 'r', encoding='utf-8') as f:
                try:
                    save_data = json.load(f)
                    print("Save data loaded successfully")
                    return save_data
                except json.JSONDecodeError as e:
                    print(f"Error decoding save file: {e}")
                    backup_path = cls.SAVE_FILE.with_suffix('.json.backup')
                    cls.SAVE_FILE.rename(backup_path)
                    print(f"Corrupted save file backed up to {backup_path}")
                    return None
        except Exception as e:
            print(f"Error loading save file: {e}")
            return None