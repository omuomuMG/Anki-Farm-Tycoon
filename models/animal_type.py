from enum import Enum

class AnimalType(Enum):
    PIG = ("Pig", 150, "🐷")
    CHICKEN = ("Chicken", 80, "🐔")
    COW = ("Cow", 300, "🐮")
    HORSE = ("Horse", 1200, "🐎")
    SHEEP = ("Sheep", 500, "🐑")
    UNICORN = ("Unicorn", 3000, "🦄")
    EMPTY = ("Empty", 0, "")

    def __init__(self, label, price, emoji):
        self._label = label
        self._price = price
        self._emoji = emoji

    @property
    def label(self):
        return self._label

    @property
    def price(self):
        return self._price

    @property
    def emoji(self):
        return self._emoji


PURCHASABLE_ANIMAL_TYPES = (
    AnimalType.CHICKEN,
    AnimalType.PIG,
    AnimalType.COW,
    AnimalType.HORSE,
    AnimalType.SHEEP,
)

TRACKED_ANIMAL_TYPES = (
    AnimalType.PIG,
    AnimalType.CHICKEN,
    AnimalType.COW,
    AnimalType.HORSE,
    AnimalType.SHEEP,
    AnimalType.UNICORN,
)
