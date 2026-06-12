import random
from .animal_type import AnimalType
from ..constants import (
    MAX_GROWTH, GROWTH_RATE,
    CHICKEN_PRODUCTION_CHANCE, COW_PRODUCTION_CHANCE,
    CHICKEN_MIN_PRODUCTION, CHICKEN_MAX_PRODUCTION,
    COW_PRODUCTION_VALUE, PIG_PRODUCTION_CHANCE,
    CHICKEN_GROWTH_RANGE, PIG_GROWTH_RANGE, COW_GROWTH_RANGE, HORSE_GROWTH_RANGE,
    PIG_SALE_BONUS_PER_LEVEL,
    SHEEP_GROWTH_RANGE, SHEEP_PRODUCTION_CHANCE, SHEEP_AGAIN_BONUS_PER_CARD,
    UNICORN_GROWTH_RANGE,
    CHICKEN_COW_SYNERGY_MULTIPLIER,
    RANDOM_EVENT_FAIR_MULTIPLIER,
)

class Animal:
    def __init__(self, animal_type: AnimalType, breed_level: int = 0):
        self.animal_type = animal_type
        self.growth = 0
        self.growth_boost = 0
        self.max_growth = MAX_GROWTH
        self.is_dead = False
        self.death_processed = False
        self.has_product = False
        self.breed_level = breed_level
        # Sheep: tracks "Again" cards answered while this Sheep is alive
        self.again_count = 0

    def get_production_chance(self) -> float:
        """calculate production chance"""
        if self.animal_type in (AnimalType.HORSE, AnimalType.UNICORN):
            return 0.0

        base_chance = {
            AnimalType.PIG: PIG_PRODUCTION_CHANCE,
            AnimalType.CHICKEN: CHICKEN_PRODUCTION_CHANCE,
            AnimalType.COW: COW_PRODUCTION_CHANCE,
            AnimalType.SHEEP: SHEEP_PRODUCTION_CHANCE,
        }.get(self.animal_type, 0)

        level_bonus = self.breed_level * 0.01
        return base_chance + level_bonus

    def get_growth_range(self):
        return {
            AnimalType.CHICKEN: CHICKEN_GROWTH_RANGE,
            AnimalType.PIG: PIG_GROWTH_RANGE,
            AnimalType.COW: COW_GROWTH_RANGE,
            AnimalType.HORSE: HORSE_GROWTH_RANGE,
            AnimalType.SHEEP: SHEEP_GROWTH_RANGE,
            AnimalType.UNICORN: UNICORN_GROWTH_RANGE,
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

    def produce(self, has_cow_nearby: bool = False) -> int:
        if self.is_dead:
            return 0

        if random.random() < self.get_production_chance():
            self.has_product = True
            if self.animal_type == AnimalType.CHICKEN:
                base = random.randint(CHICKEN_MIN_PRODUCTION, CHICKEN_MAX_PRODUCTION)
                # Sinergia: dobra o valor do ovo se houver uma vaca no campo
                if has_cow_nearby:
                    base *= CHICKEN_COW_SYNERGY_MULTIPLIER
                return base
            elif self.animal_type == AnimalType.COW:
                return COW_PRODUCTION_VALUE
            elif self.animal_type == AnimalType.PIG:
                self.grow()
                return 1
            elif self.animal_type == AnimalType.SHEEP:
                return 20
            elif self.animal_type == AnimalType.HORSE:
                return 0
            elif self.animal_type == AnimalType.UNICORN:
                return 0
        return 0

    def get_sale_price(self, fair_active: bool = False):
        if self.is_dead:
            return 0
        growth_multiplier = 1 + (self.growth / 100)
        sale_price = self.animal_type.price * growth_multiplier

        if self.animal_type == AnimalType.PIG and self.breed_level > 0:
            sale_price *= (1 + (self.breed_level * PIG_SALE_BONUS_PER_LEVEL))

        # Sheep: bonus for "Again" cards answered while this Sheep is alive
        if self.animal_type == AnimalType.SHEEP and self.again_count > 0:
            again_bonus = 1 + (self.again_count * SHEEP_AGAIN_BONUS_PER_CARD)
            sale_price *= again_bonus

        # Unicorn: sale price scales with caller's easy streak (passed externally)
        # The streak multiplier is applied in game_widget when selling

        if fair_active:
            sale_price *= RANDOM_EVENT_FAIR_MULTIPLIER

        return int(sale_price)

    def can_sell(self):
        return not self.is_dead and self.growth >= 50
