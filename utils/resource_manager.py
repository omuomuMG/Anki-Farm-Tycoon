from PyQt6.QtGui import QPixmap
from ..constants import RESOURCES_DIR
from ..models.animal_type import AnimalType

class ResourceManager:
    @staticmethod
    def load_all_resources():
        resources = {
            'tile': QPixmap(str(RESOURCES_DIR / "maptile_sogen_01.svg")),
            'locked_tile': QPixmap(str(RESOURCES_DIR / "maptile_sogen_hana_01.svg")),
            'stats_bg': QPixmap(str(RESOURCES_DIR / "maptile_sogen_01.svg")),
            'grave': QPixmap(str(RESOURCES_DIR / "grave.svg")),
            'animals': {
                AnimalType.PIG: QPixmap(str(RESOURCES_DIR / "buta.svg")),
                AnimalType.CHICKEN: QPixmap(str(RESOURCES_DIR / "niwatori_male.svg")),
                AnimalType.COW: QPixmap(str(RESOURCES_DIR / "ushi_red_tsuno.svg"))
            },
            'products': {
                AnimalType.CHICKEN: QPixmap(str(RESOURCES_DIR / "egg.svg")),
                AnimalType.COW: QPixmap(str(RESOURCES_DIR / "milk.svg")),
                AnimalType.PIG:  QPixmap(str(RESOURCES_DIR / "pig_effect.svg"))
            }
        }
        return resources