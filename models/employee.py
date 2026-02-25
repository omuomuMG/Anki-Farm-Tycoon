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
        self.max_level = 11
        self.enabled = True
        self.total_earnings = 0
        self.total_sales = 0

        self.can_buy_chicken = True
        self.can_buy_pig = True
        self.can_buy_cow = True
        self.can_buy_horse = True
        self.buy_randomly = True

    @staticmethod
    def calculate_hire_cost(x: int, y: int) -> int:
        # First employee is free
        if y == 0 and x == 0:
            return 0
        position = y * GRID_SIZE + x
        base_cost = 100
        return int(base_cost + (300 * position))

    def get_salary_rate(self) -> float:
        base_rate = 0.3
        level_reduction = 0.03
        return max(0, base_rate - (self.level - 1) * level_reduction)

    def get_upgrade_cost(self) -> int:
        return 1000 + self.level * 100

    def should_sell_animal(self, animal) -> bool:
        if not animal or animal.is_dead:
            return False
        optimal_growth = 50 + (self.level * 5)
        return animal.growth >= optimal_growth

    def choose_animal_to_buy(self) -> AnimalType:
        """Return which animal type this employee should buy"""
        save_data = SaveManager.load_game()

        pig = save_data["breeds"].get(
            "PIG", {"level": 0, "is_unlocked": False}
        )
        cow = save_data["breeds"].get(
            "COW", {"level": 0, "is_unlocked": False}
        )
        horse = save_data["breeds"].get(
            "HORSE", {"level": 0, "is_unlocked": False}
        )

        if self.buy_randomly:
            choices = []
            choices.append(AnimalType.CHICKEN)

            if pig["is_unlocked"]:
                choices.append(AnimalType.PIG)

            if cow["is_unlocked"]:
                choices.append(AnimalType.COW)

            if horse["is_unlocked"]:
                choices.append(AnimalType.HORSE)

            import time
            random.seed(int(time.time()))

            if len(choices) == 1:
                choice = choices[0]
            else:
                index = random.randint(0, len(choices) - 1)
                choice = choices[index]
            return choice

        # if self.buy_randomly is False
        if self.can_buy_pig and pig["is_unlocked"]:
            return AnimalType.PIG

        if self.can_buy_cow and cow["is_unlocked"]:
            return AnimalType.COW

        if self.can_buy_horse and horse["is_unlocked"]:
            return AnimalType.HORSE

        if self.can_buy_chicken:
            return AnimalType.CHICKEN

        return AnimalType.CHICKEN

    def update_buying_preferences(self, chicken: bool, pig: bool, cow: bool, horse: bool = False):
        """Update which animals this employee can buy"""
        self.can_buy_chicken = chicken
        self.can_buy_pig = pig
        self.can_buy_cow = cow
        self.can_buy_horse = horse

        # Save the updated preferences
        self.save_preferences()

    def save_preferences(self):
        """Save employee preferences to the save file"""
        save_data = SaveManager.load_game()

        if "employees" not in save_data:
            save_data["employees"] = {}

        employee_id = self.name

        if employee_id in save_data["employees"]:
            save_data["employees"][employee_id].update({
                "can_buy_chicken": self.can_buy_chicken,
                "can_buy_pig": self.can_buy_pig,
                "can_buy_cow": self.can_buy_cow,
                "can_buy_horse": self.can_buy_horse,
                "buy_randomly": self.buy_randomly
            })
        else:
            save_data["employees"][employee_id] = {
                "name": self.name,
                "x": self.x,
                "y": self.y,
                "level": self.level,
                "enabled": self.enabled,
                "total_earnings": self.total_earnings,
                "total_sales": self.total_sales,
                "can_buy_chicken": self.can_buy_chicken,
                "can_buy_pig": self.can_buy_pig,
                "can_buy_cow": self.can_buy_cow,
                "can_buy_horse": self.can_buy_horse,
                "buy_randomly": self.buy_randomly
            }

        SaveManager.save_game(save_data)

    def load_preferences(self):
        """Load employee preferences from the save file"""
        save_data = SaveManager.load_game()

        if "employees" not in save_data:
            return

        employee_id = self.name

        if employee_id in save_data["employees"]:
            emp_data = save_data["employees"][employee_id]

            self.level = emp_data.get("level", self.level)
            self.enabled = emp_data.get("enabled", self.enabled)
            self.total_earnings = emp_data.get("total_earnings", self.total_earnings)
            self.total_sales = emp_data.get("total_sales", self.total_sales)

            self.buy_randomly = emp_data.get("buy_randomly", True)

            if not self.buy_randomly:
                self.can_buy_chicken = emp_data.get("can_buy_chicken", False)
                self.can_buy_pig = emp_data.get("can_buy_pig", False)
                self.can_buy_cow = emp_data.get("can_buy_cow", False)
                self.can_buy_horse = emp_data.get("can_buy_horse", False)
            else:
                self.can_buy_chicken = False
                self.can_buy_pig = False
                self.can_buy_cow = False
                self.can_buy_horse = False


__all__ = ["Employee"]
