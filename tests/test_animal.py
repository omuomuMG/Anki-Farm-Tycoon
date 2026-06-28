import unittest
from unittest.mock import patch

from tests._bootstrap import import_target


animal_module = import_target("models.animal")
animal_type_module = import_target("models.animal_type")
Animal = animal_module.Animal
AnimalType = animal_type_module.AnimalType


class AnimalTests(unittest.TestCase):
    def test_growth_uses_boost_then_resets_it(self):
        animal = Animal(AnimalType.CHICKEN)
        animal.growth_boost = 3

        with patch.object(animal_module.random, "randint", return_value=2):
            animal.grow()

        self.assertEqual(animal.growth, 5)
        self.assertEqual(animal.growth_boost, 0)
        self.assertFalse(animal.is_dead)

    def test_growth_is_capped_and_marks_animal_dead(self):
        animal = Animal(AnimalType.CHICKEN)
        animal.growth = animal.max_growth - 1

        with patch.object(animal_module.random, "randint", return_value=4):
            animal.grow()

        self.assertEqual(animal.growth, animal.max_growth)
        self.assertTrue(animal.is_dead)

    def test_dead_animal_does_not_grow_or_produce(self):
        animal = Animal(AnimalType.COW)
        animal.is_dead = True
        animal.grow()

        self.assertEqual(animal.growth, 0)
        self.assertEqual(animal.produce(), 0)

    def test_chicken_and_cow_synergy_doubles_egg_value(self):
        chicken = Animal(AnimalType.CHICKEN)

        with (
            patch.object(animal_module.random, "random", return_value=0),
            patch.object(animal_module.random, "randint", return_value=5),
        ):
            production = chicken.produce(has_cow_nearby=True)

        self.assertEqual(production, 10)
        self.assertTrue(chicken.has_product)

    def test_sale_price_applies_growth_breed_and_fair_bonuses(self):
        pig = Animal(AnimalType.PIG, breed_level=2)
        pig.growth = 100
        self.assertEqual(pig.get_sale_price(fair_active=True), 618)

    def test_sheep_again_answers_increase_sale_price(self):
        sheep = Animal(AnimalType.SHEEP)
        sheep.growth = 50
        sheep.again_count = 2
        self.assertEqual(sheep.get_sale_price(), 825)

    def test_only_living_mature_animals_can_be_sold(self):
        animal = Animal(AnimalType.COW)
        animal.growth = 49
        self.assertFalse(animal.can_sell())
        animal.growth = 50
        self.assertTrue(animal.can_sell())
        animal.is_dead = True
        self.assertFalse(animal.can_sell())


if __name__ == "__main__":
    unittest.main()
