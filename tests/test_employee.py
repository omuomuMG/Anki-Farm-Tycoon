import copy
import unittest
from unittest.mock import patch

from tests._bootstrap import import_target


employee_module = import_target("models.employee")
animal_type_module = import_target("models.animal_type")
Employee = employee_module.Employee
AnimalType = animal_type_module.AnimalType


def save_data(unlocked=()):
    names = ("PIG", "COW", "HORSE", "SHEEP")
    return {
        "breeds": {
            name: {"level": 0, "is_unlocked": name in unlocked}
            for name in names
        },
        "employees": {},
    }


class EmployeeTests(unittest.TestCase):
    def test_random_mode_only_offers_unlocked_animals(self):
        data = save_data(unlocked=("PIG", "SHEEP"))
        with (
            patch.object(employee_module.SaveManager, "load_game", return_value=data),
            patch.object(employee_module.random, "choice", side_effect=lambda choices: choices[-1]) as choose,
        ):
            selected = Employee("A", 0, 0).choose_animal_to_buy()

        self.assertEqual(selected, AnimalType.SHEEP)
        self.assertEqual(
            choose.call_args.args[0],
            [AnimalType.CHICKEN, AnimalType.PIG, AnimalType.SHEEP],
        )

    def test_random_mode_does_not_reseed_each_employee(self):
        data = save_data(unlocked=("PIG", "SHEEP"))
        choices = iter((AnimalType.PIG, AnimalType.SHEEP))
        with (
            patch.object(employee_module.SaveManager, "load_game", return_value=data),
            patch.object(employee_module.random, "choice", side_effect=lambda _items: next(choices)),
            patch.object(employee_module.random, "seed", side_effect=AssertionError("must not reseed")),
        ):
            first = Employee("A", 0, 0).choose_animal_to_buy()
            second = Employee("B", 1, 0).choose_animal_to_buy()

        self.assertEqual(first, AnimalType.PIG)
        self.assertEqual(second, AnimalType.SHEEP)

    def test_specific_mode_uses_each_employees_own_preference(self):
        data = save_data(unlocked=("PIG", "SHEEP"))
        pig_employee = Employee("A", 0, 0)
        sheep_employee = Employee("B", 1, 0)
        for employee in (pig_employee, sheep_employee):
            employee.buy_randomly = False
            employee.can_buy_chicken = False
            employee.can_buy_pig = False
            employee.can_buy_cow = False
            employee.can_buy_horse = False
            employee.can_buy_sheep = False
        pig_employee.can_buy_pig = True
        sheep_employee.can_buy_sheep = True

        with patch.object(employee_module.SaveManager, "load_game", return_value=data):
            self.assertEqual(pig_employee.choose_animal_to_buy(), AnimalType.PIG)
            self.assertEqual(sheep_employee.choose_animal_to_buy(), AnimalType.SHEEP)

    def test_preferences_are_saved_under_separate_employee_keys(self):
        class MemorySaveManager:
            data = save_data(unlocked=("PIG", "SHEEP"))

            @classmethod
            def load_game(cls):
                return copy.deepcopy(cls.data)

            @classmethod
            def save_game(cls, data):
                cls.data = copy.deepcopy(data)

        first = Employee("A", 0, 0)
        first.buy_randomly = False
        second = Employee("B", 1, 0)
        second.buy_randomly = False
        for employee in (first, second):
            employee.can_buy_chicken = False
            employee.can_buy_pig = False
            employee.can_buy_cow = False
            employee.can_buy_horse = False
            employee.can_buy_sheep = False
        first.can_buy_pig = True
        second.can_buy_sheep = True

        with patch.object(employee_module, "SaveManager", MemorySaveManager):
            first.save_preferences()
            second.save_preferences()

        employees = MemorySaveManager.data["employees"]
        self.assertTrue(employees["A"]["can_buy_pig"])
        self.assertFalse(employees["A"]["can_buy_sheep"])
        self.assertTrue(employees["B"]["can_buy_sheep"])
        self.assertFalse(employees["B"]["can_buy_pig"])

    def test_hire_cost_and_salary_are_bounded(self):
        self.assertEqual(Employee.calculate_hire_cost(0, 0), 0)
        self.assertEqual(Employee.calculate_hire_cost(1, 0), 400)
        employee = Employee("A", 0, 0)
        employee.level = employee.max_level
        self.assertEqual(employee.get_salary_rate(), 0)


if __name__ == "__main__":
    unittest.main()
