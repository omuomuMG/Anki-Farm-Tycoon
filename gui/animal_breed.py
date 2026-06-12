from ..models.animal_type import AnimalType


class AnimalBreed:
    def __init__(self, animal_type: AnimalType):
        self.animal_type = animal_type
        self.level = 0
        self.is_unlocked = animal_type == AnimalType.CHICKEN
        self.max_level = 0 if animal_type in (AnimalType.HORSE, AnimalType.UNICORN) else 20

    def get_unlock_cost(self) -> int:
        costs = {
            AnimalType.PIG: 1000,
            AnimalType.COW: 2000,
            AnimalType.HORSE: 5000,
            AnimalType.CHICKEN: 0,
            AnimalType.SHEEP: 1500,
        }
        return costs.get(self.animal_type, 0)

    def get_upgrade_cost(self) -> int:
        base_cost = {
            AnimalType.PIG: 800,
            AnimalType.CHICKEN: 500,
            AnimalType.COW: 1500,
            AnimalType.HORSE: 0,
            AnimalType.SHEEP: 1000,
        }
        return int(base_cost[self.animal_type] * (1.5 ** self.level))

    def get_production_chance(self) -> float:
        if self.animal_type in (AnimalType.HORSE, AnimalType.UNICORN):
            return 0.0
        base_chance = {
            AnimalType.PIG: 0.01,
            AnimalType.CHICKEN: 0.10,
            AnimalType.COW: 0.02,
            AnimalType.SHEEP: 0.05,
        }
        level_bonus = self.level * 0.01
        return base_chance[self.animal_type] + level_bonus
