import random
from .animal_type import AnimalType
from ..constants import (
    MAX_GROWTH, GROWTH_RATE,
    CHICKEN_PRODUCTION_CHANCE, COW_PRODUCTION_CHANCE,
    CHICKEN_MIN_PRODUCTION, CHICKEN_MAX_PRODUCTION,
    COW_PRODUCTION_VALUE, PIG_PRODUCTION_CHANCE,
    CHICKEN_GROWTH_RANGE, PIG_GROWTH_RANGE, COW_GROWTH_RANGE,
    PIG_SALE_BONUS_PER_LEVEL
)

class Animal:
    def __init__(self, animal_type: AnimalType, breed_level: int = 0):
        self.animal_type = animal_type
        self.growth = 0
        self.growth_boost = 0
        self.max_growth = MAX_GROWTH
        self.is_dead = False
        self.has_product = False
        self.breed_level = breed_level

    def get_production_chance(self) -> float:
        """calculate production chance"""
        base_chance = {
            AnimalType.PIG: PIG_PRODUCTION_CHANCE,
            AnimalType.CHICKEN: CHICKEN_PRODUCTION_CHANCE,
            AnimalType.COW: COW_PRODUCTION_CHANCE
        }.get(self.animal_type, 0)

        # レベルごとに1%ずつ上昇
        level_bonus = self.breed_level * 0.01
        return base_chance + level_bonus

    def get_growth_range(self):
        return {
            AnimalType.CHICKEN: CHICKEN_GROWTH_RANGE,
            AnimalType.PIG: PIG_GROWTH_RANGE,
            AnimalType.COW: COW_GROWTH_RANGE
        }.get(self.animal_type, (0, GROWTH_RATE))

    def grow(self):
        """Handle animal growth"""
        if not self.is_dead:
            growth_min, growth_max = self.get_growth_range()
            growth_increment = random.randint(growth_min, growth_max) + self.growth_boost
            self.growth = min(self.growth + growth_increment, self.max_growth)
            self.growth_boost = 0
            if self.growth >= self.max_growth:
                self.is_dead = True

    def produce(self) -> int:
        if self.is_dead:
            return 0

        if random.random() < self.get_production_chance():
            self.has_product = True
            if self.animal_type == AnimalType.CHICKEN:
                return random.randint(5, 10)
            elif self.animal_type == AnimalType.COW:
                return 50
            elif self.animal_type == AnimalType.PIG:
                self.grow()
                return 1
        return 0

    def get_sale_price(self):
        if self.is_dead:
            return 0
        growth_multiplier = 1 + (self.growth / 100)
        sale_price = self.animal_type.price * growth_multiplier

        if self.animal_type == AnimalType.PIG and self.breed_level > 0:
            sale_price *= (1 + (self.breed_level * PIG_SALE_BONUS_PER_LEVEL))

        return int(sale_price)

    def can_sell(self):
        return not self.is_dead and self.growth >= 50
