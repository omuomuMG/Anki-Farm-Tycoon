from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QPainter, QPixmap
from ..constants import RESOURCES_DIR
from ..models.animal_type import AnimalType

class ResourceManager:
    @staticmethod
    def _emoji_pixmap(emoji: str, size: int = 256) -> QPixmap:
        pixmap = QPixmap(size, size)
        pixmap.fill(Qt.GlobalColor.transparent)

        painter = QPainter(pixmap)
        font = QFont()
        font.setPointSize(int(size * 0.6))
        painter.setFont(font)
        painter.drawText(pixmap.rect(), Qt.AlignmentFlag.AlignCenter, emoji)
        painter.end()
        return pixmap

    @staticmethod
    def _load_pixmap(filename: str, fallback_emoji: str = "") -> QPixmap:
        path = RESOURCES_DIR / filename
        if path.exists():
            return QPixmap(str(path))
        if fallback_emoji:
            return ResourceManager._emoji_pixmap(fallback_emoji)
        return QPixmap(str(path))

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
                AnimalType.HORSE: QPixmap(str(horse_path)),
                AnimalType.SHEEP: ResourceManager._load_pixmap("sheep.png", AnimalType.SHEEP.emoji),
                AnimalType.UNICORN: ResourceManager._load_pixmap("unicorn.png", AnimalType.UNICORN.emoji),
            },
            'child_animals': {
                AnimalType.PIG: QPixmap(str(RESOURCES_DIR / "child_pig.png")),
                AnimalType.CHICKEN: QPixmap(str(RESOURCES_DIR / "child_chicken.png")),
                AnimalType.COW: QPixmap(str(RESOURCES_DIR / "child_cow.png")),
                AnimalType.HORSE: QPixmap(str(RESOURCES_DIR / "child_horse.png")),
                AnimalType.SHEEP: ResourceManager._load_pixmap("child_sheep.png", AnimalType.SHEEP.emoji),
                AnimalType.UNICORN: ResourceManager._load_pixmap("child_unicorn.png", AnimalType.UNICORN.emoji),
            },
            'products': {
                AnimalType.CHICKEN: QPixmap(str(RESOURCES_DIR / "egg.png")),
                AnimalType.COW: QPixmap(str(RESOURCES_DIR / "milk.png")),
                AnimalType.PIG:  QPixmap(str(RESOURCES_DIR / "pig_effect.svg")),
                AnimalType.SHEEP: ResourceManager._load_pixmap("wool.png", "🧶"),
            }
        }
        return resources
