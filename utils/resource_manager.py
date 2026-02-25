from PyQt6.QtGui import QPixmap
from ..constants import RESOURCES_DIR
from ..models.animal_type import AnimalType

class ResourceManager:
    @staticmethod
    def load_all_resources():
        horse_path = RESOURCES_DIR / "horse.png"
        if not horse_path.exists():
            horse_path = RESOURCES_DIR / "hource.png"

        resources = {
            'tile': QPixmap(str(RESOURCES_DIR / "ground.png")),
            'locked_tile': QPixmap(str(RESOURCES_DIR / "tile_flower.png")),
            'stats_bg': QPixmap(str(RESOURCES_DIR / "menu3.png")),
            'grave': QPixmap(str(RESOURCES_DIR / "grave.png")),
            'employee_icon': QPixmap(str(RESOURCES_DIR / "farmer.png")),
            'animals': {
                AnimalType.PIG: QPixmap(str(RESOURCES_DIR / "pig.png")),
                AnimalType.CHICKEN: QPixmap(str(RESOURCES_DIR / "chicken.png")),
                AnimalType.COW: QPixmap(str(RESOURCES_DIR / "cow.png")),
                AnimalType.HORSE: QPixmap(str(horse_path))
            },
            'products': {
                AnimalType.CHICKEN: QPixmap(str(RESOURCES_DIR / "egg.png")),
                AnimalType.COW: QPixmap(str(RESOURCES_DIR / "milk.png")),
                AnimalType.PIG:  QPixmap(str(RESOURCES_DIR / "pig_effect.svg"))
            }
        }
        return resources
