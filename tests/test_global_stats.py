import unittest

from tests._bootstrap import import_target


stats_module = import_target("models.global_status")
animal_type_module = import_target("models.animal_type")
GlobalStats = stats_module.GlobalStats
TRACKED_ANIMAL_TYPES = animal_type_module.TRACKED_ANIMAL_TYPES


class GlobalStatsTests(unittest.TestCase):
    def test_ten_answers_advance_one_day(self):
        stats = GlobalStats()
        for _ in range(9):
            stats.update_day_count()
        self.assertEqual(stats.current_day, 0)
        self.assertEqual(stats.answers_count, 9)

        stats.update_day_count()
        self.assertEqual(stats.current_day, 1)
        self.assertEqual(stats.answers_count, 0)
        self.assertEqual(stats.highest_day, 1)

    def test_money_record_never_decreases(self):
        stats = GlobalStats()
        stats.update_money_record(5000)
        stats.update_money_record(100)
        self.assertEqual(stats.highest_money, 5000)

    def test_serialization_round_trip_preserves_progress(self):
        stats = GlobalStats()
        stats.current_day = 7
        stats.answers_count = 3
        stats.total_animals_sold = 4
        stats.total_animals_sold_by_type["SHEEP"] = 2

        restored = GlobalStats.from_dict(stats.to_dict())

        self.assertEqual(restored.current_day, 7)
        self.assertEqual(restored.answers_count, 3)
        self.assertEqual(restored.total_animals_sold, 4)
        self.assertEqual(restored.total_animals_sold_by_type["SHEEP"], 2)

    def test_old_save_gets_defaults_for_new_animal_types(self):
        restored = GlobalStats.from_dict({"total_animals_sold_by_type": {"CHICKEN": 3}})
        for animal_type in TRACKED_ANIMAL_TYPES:
            expected = 3 if animal_type.name == "CHICKEN" else 0
            self.assertEqual(restored.total_animals_sold_by_type[animal_type.name], expected)


if __name__ == "__main__":
    unittest.main()
