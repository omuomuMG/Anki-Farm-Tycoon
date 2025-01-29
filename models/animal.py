import random
from .animal_type import AnimalType
from ..constants import (
    MAX_GROWTH, GROWTH_RATE,
    CHICKEN_PRODUCTION_CHANCE, COW_PRODUCTION_CHANCE,
    CHICKEN_MIN_PRODUCTION, CHICKEN_MAX_PRODUCTION,
    COW_PRODUCTION_VALUE
)

class Animal:
    def __init__(self, animal_type: AnimalType):
        self.animal_type = animal_type
        self.growth = 0
        self.max_growth = MAX_GROWTH
        self.is_dead = False
        self.has_product = False

    def grow(self):
        """Handle animal growth"""
        if not self.is_dead:
            growth_increment = random.randint(0,3)
            self.growth = min(self.growth + growth_increment, self.max_growth)
            print(f"Growing animal: {self.growth}%")

            if self.growth >= self.max_growth:
                self.is_dead = True
                print("Animal died due to max growth")

    def produce(self) -> int:
        if self.is_dead:
            return 0

        if self.animal_type == AnimalType.CHICKEN:
            if random.random() < CHICKEN_PRODUCTION_CHANCE:
                self.has_product = True
                return random.randint(CHICKEN_MIN_PRODUCTION, CHICKEN_MAX_PRODUCTION)
        elif self.animal_type == AnimalType.COW:
            if random.random() < COW_PRODUCTION_CHANCE:
                self.has_product = True
                return COW_PRODUCTION_VALUE
        return 0

    def get_sale_price(self):
        if self.is_dead:
            return 0
        growth_multiplier = 1 + (self.growth / 100)
        return int(self.animal_type.price * growth_multiplier)

    def can_sell(self):
        return not self.is_dead and self.growth >= 50

    def get_cleanup_cost(self):
        return int(self.animal_type.price * 0.5)