import random
from ..constants import GRID_SIZE
from ..utils.save_manager import SaveManager
from .animal_type import AnimalType

class Employee:
    def __init__(self, name: str, x: int, y: int):
        self.name = name
        self.x = x
        self.y = y
        self.level = 1
        self.max_level = 10
        self.enabled = True
        self.total_earnings = 0
        self.total_sales = 0

    @staticmethod
    def calculate_hire_cost(x: int, y: int) -> int:
        # First employee is free
        if y == 0 and x == 0:
            return 0
        position = y * GRID_SIZE + x
        base_cost = 2000
        return int(base_cost + (300 * position))


    def get_salary_rate(self) -> float:
            base_rate = 0.3
            level_reduction = 0.03
            return max(0.1, base_rate - (self.level - 1) * level_reduction)

    def get_upgrade_cost(self) -> int:
        return 1000 + self.level * 100

    def should_sell_animal(self, animal) -> bool:
        if not animal or animal.is_dead:
            return False
        optimal_growth = 50 + (self.level * 5)
        return animal.growth >= optimal_growth

    def choose_animal_to_buy(self) -> AnimalType:
        save_data = SaveManager.load_game()

        pig = save_data["breeds"].get(
            "PIG", {"level": 0, "is_unlocked": False}
        )

        cow = save_data["breeds"].get(
            "COW", {"level": 0, "is_unlocked": False}
        )

        choices = [AnimalType.CHICKEN] * self.level

        if pig["is_unlocked"]:
            choices += [AnimalType.PIG] * self.level

        if cow["is_unlocked"]:
            choices += [AnimalType.COW] * self.level

        return random.choice(choices)

