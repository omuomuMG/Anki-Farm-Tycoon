from ..constants import INITIAL_MONEY


class GlobalStats:
    def __init__(self):
        self.total_animals_sold = 0
        self.total_animals_dead = 0
        self.total_money_earned = INITIAL_MONEY
        self.highest_money = 0
        self.highest_day = 0
        self.current_day = 0
        self.answers_count = 0

        # 動物タイプごとの統計を追加
        self.total_animals_sold_by_type = {
            'PIG': 0,
            'CHICKEN': 0,
            'COW': 0
        }
        self.total_animals_died_by_type = {
            'PIG': 0,
            'CHICKEN': 0,
            'COW': 0
        }

    def update_money_record(self, current_money: int):
        self.highest_money = max(self.highest_money, current_money)

    def update_day_count(self):
        self.answers_count += 1
        if self.answers_count >= 10: # 10ans => 1day
            self.current_day += 1
            self.answers_count = 0
            self.highest_day = max(self.highest_day, self.current_day)

    def to_dict(self):
        return {
            "total_animals_sold": self.total_animals_sold,
            "total_animals_dead": self.total_animals_dead,
            "total_money_earned": self.total_money_earned,
            "highest_money": self.highest_money,
            "highest_day": self.highest_day,
            "current_day": self.current_day,
            "answers_count": self.answers_count,
            "total_animals_sold_by_type": self.total_animals_sold_by_type,
            "total_animals_died_by_type": self.total_animals_died_by_type
        }

    @classmethod
    def from_dict(cls, data: dict):
        stats = cls()
        stats.total_animals_sold = data.get("total_animals_sold", 0)
        stats.total_animals_dead = data.get("total_animals_dead", 0)
        stats.total_money_earned = data.get("total_money_earned", 0)
        stats.highest_money = data.get("highest_money", 0)
        stats.highest_day = data.get("highest_day", 0)
        stats.current_day = data.get("current_day", 0)
        stats.answers_count = data.get("answers_count", 0)
        stats.total_animals_sold_by_type = data.get("total_animals_sold_by_type", {
            'PIG': 0, 'CHICKEN': 0, 'COW': 0
        })
        stats.total_animals_died_by_type = data.get("total_animals_died_by_type", {
            'PIG': 0, 'CHICKEN': 0, 'COW': 0
        })
        return stats