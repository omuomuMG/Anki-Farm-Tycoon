import random
from .animal_type import AnimalType

class Employee:

    def __init__(self, name: str, position: int):
        self.name = name
        self.position = position
        self.level = 1
        self.max_level = 10
        self.enabled = True
        self.total_earnings = 0
        self.total_sales = 0

    @staticmethod
    def calculate_hire_cost(position: int) -> int:
        base_cost = 2000
        return int(base_cost * (1.5 ** position))



    def get_salary_rate(self) -> float:
        base_rate = 0.5  # 50%から開始
        level_reduction = 0.03  # レベルごとに3%減少
        return max(0.1, base_rate - (self.level - 1) * level_reduction)

    def get_upgrade_cost(self) -> int:
        return 1000 * self.level * 2

    def get_hire_cost(self) -> int:
        return 2000 * (self.position + 1)

    def should_sell_animal(self, animal) -> bool:
        if not animal or animal.is_dead:
            return False
        optimal_growth = 50 + (self.level * 5)  # レベルごとに5%上乗せ
        return animal.growth >= optimal_growth

    def choose_animal_to_buy(self) -> AnimalType:
        choices = [AnimalType.CHICKEN] * (11 - self.level)  # レベルが上がるほど選択率減少
        choices += [AnimalType.PIG] * self.level
        choices += [AnimalType.COW] * (self.level // 2)
        return random.choice(choices)