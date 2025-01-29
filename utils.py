import json
import os
import random
import sys
from enum import Enum
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QPainter, QColor, QPixmap, QFont
from PyQt6.QtWidgets import QApplication, QWidget, QMessageBox
from aqt import mw, gui_hooks
from aqt.utils import showInfo
from PyQt6.QtWidgets import QMenu
from PyQt6.QtGui import QCursor

def get_addon_dir():
    return os.path.dirname(os.path.abspath(__file__))

class AnimalType(Enum):
    PIG = ("Pig", 150, "🐷")
    CHICKEN = ("Chicken", 80, "🐔")
    COW = ("Cow", 300, "🐮")
    EMPTY = ("Empty", 0, "")

    def __init__(self, label, price, emoji):
        self._label = label
        self._price = price
        self._emoji = emoji

    @property
    def label(self):
        return self._label

    @property
    def price(self):
        return self._price

    @property
    def emoji(self):
        return self._emoji

class Animal:
    def __init__(self, animal_type: AnimalType):
        self.animal_type = animal_type
        self.growth = 0
        self.max_growth = 150
        self.is_dead = False
        self.has_product = False

    def produce(self) -> int:
        """Generate products (eggs/milk) and return earnings"""
        if self.is_dead:
            return 0

        if self.animal_type == AnimalType.CHICKEN:
            # Chicken egg production (10% chance)
            if random.random() < 0.10:
                self.has_product = True
                return random.randint(5, 10)

        elif self.animal_type == AnimalType.COW:
            # Cow milk production (2% chance)
            if random.random() < 0.02:
                self.has_product = True
                return 50

        return 0

    def grow(self):
        if not self.is_dead:
            # 動物タイプごとに異なる成長率
            growth_rates = {
                AnimalType.CHICKEN: 7,
                AnimalType.PIG: 5,
                AnimalType.COW: 3
            }
            growth_rate = growth_rates[self.animal_type]
            self.growth = min(self.growth + growth_rate, self.max_growth)
            if self.growth >= self.max_growth:
                self.is_dead = True

    def get_sale_price(self):
        if self.is_dead:
            return 0
        growth_multiplier = 1 + (self.growth / 100)
        return int(self.animal_type.price * growth_multiplier)

    def can_sell(self):
        return not self.is_dead and self.growth >= 50

    def get_cleanup_cost(self):
        return int(self.animal_type.price * 0.5)

class Field:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.animal = None

    def add_animal(self, animal: Animal):
        if self.animal is None:
            self.animal = animal
            return True
        return False

    def remove_animal(self):
        animal = self.animal
        self.animal = None
        return animal


class GameWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.save_file_path = os.path.join(get_addon_dir(), "game_save.json")

        # Basic settings
        self.cell_size = 100
        self.current_animal_type = AnimalType.PIG
        self.selected_animal_type = None

        # Set window size
        stats_panel_width = 250
        window_width = stats_panel_width + (self.cell_size * 4)
        window_height = self.cell_size * 4
        self.setGeometry(100, 100, window_width, window_height)
        self.setWindowTitle("Ranch")

        # Load game data and images
        self.load_game()
        self.load_images()

        # Set up Anki hook
        gui_hooks.reviewer_did_answer_card.append(self.called)

    def _initialize_new_game(self):
        """Initialize new game"""
        self.money = 1000
        self.unlocked_fields = 1
        self.stats = {
            AnimalType.PIG: {"sold": 0, "dead": 0},
            AnimalType.CHICKEN: {"sold": 0, "dead": 0},
            AnimalType.COW: {"sold": 0, "dead": 0}
        }
        self.fields = []
        for y in range(4):
            row = []
            for x in range(4):
                row.append(Field(x, y))
            self.fields.append(row)

    def load_images(self):
        """Load image resources"""
        addon_dir = get_addon_dir()
        resources_dir = os.path.join(addon_dir, "Resources")

        # Field tile images
        self.tile_image = QPixmap(os.path.join(resources_dir, "maptile_sogen_01.svg"))
        self.locked_tile_image = QPixmap(os.path.join(resources_dir, "maptile_sogen_hana_01.svg"))
        self.stats_bg_image = QPixmap(os.path.join(resources_dir, "maptile_sogen_01.svg"))
        self.grave_image = QPixmap(os.path.join(resources_dir, "grave.svg"))

        # Animal images
        self.animal_images = {
            AnimalType.PIG: QPixmap(os.path.join(resources_dir, "buta.svg")),
            AnimalType.CHICKEN: QPixmap(os.path.join(resources_dir, "niwatori_male.svg")),
            AnimalType.COW: QPixmap(os.path.join(resources_dir, "ushi_red_tsuno.svg"))
        }

        # Product images
        self.product_images = {
            AnimalType.CHICKEN: QPixmap(os.path.join(resources_dir, "egg.svg")),
            AnimalType.COW: QPixmap(os.path.join(resources_dir, "milk.svg"))
        }

    def save_game(self):
        """Save game state to JSON file"""
        save_data = {
            "money": self.money,
            "unlocked_fields": self.unlocked_fields,
            "stats": {
                animal_type.name: stats
                for animal_type, stats in self.stats.items()
                if animal_type != AnimalType.EMPTY
            },
            "fields": [
                [
                    {
                        "x": field.x,
                        "y": field.y,
                        "animal": {
                            "type": field.animal.animal_type.name,
                            "growth": field.animal.growth,
                            "is_dead": field.animal.is_dead,
                            "has_product": field.animal.has_product,
                            "max_growth": field.animal.max_growth
                        } if field.animal else None
                    }
                    for field in row
                ]
                for row in self.fields
            ]
        }

        try:
            with open(self.save_file_path, 'w', encoding='utf-8') as f:
                json.dump(save_data, f, ensure_ascii=False, indent=2)
            print(f"Game saved: {self.save_file_path}")
        except Exception as e:
            print(f"Failed to save game: {e}")

    def load_game(self):
        """Load game state from JSON file"""
        try:
            if os.path.exists(self.save_file_path):
                print(f"Loading save data: {self.save_file_path}")
                with open(self.save_file_path, 'r', encoding='utf-8') as f:
                    save_data = json.load(f)

                # Load basic data
                self.money = save_data.get("money", 1000)
                self.unlocked_fields = save_data.get("unlocked_fields", 1)

                # Load statistics
                saved_stats = save_data.get("stats", {})
                self.stats = {}
                for animal_type in AnimalType:
                    if animal_type != AnimalType.EMPTY:
                        self.stats[animal_type] = saved_stats.get(
                            animal_type.name,
                            {"sold": 0, "dead": 0}
                        )

                # Load fields
                self.fields = []
                saved_fields = save_data.get("fields", [])

                for y in range(4):
                    field_row = []
                    for x in range(4):
                        if y < len(saved_fields) and x < len(saved_fields[y]):
                            field_data = saved_fields[y][x]
                            field = Field(field_data["x"], field_data["y"])

                            animal_data = field_data.get("animal")
                            if animal_data:
                                animal_type = AnimalType[animal_data["type"]]
                                animal = Animal(animal_type)
                                animal.growth = animal_data["growth"]
                                animal.is_dead = animal_data["is_dead"]
                                animal.has_product = animal_data["has_product"]
                                animal.max_growth = animal_data["max_growth"]
                                field.animal = animal
                        else:
                            field = Field(x, y)
                        field_row.append(field)
                    self.fields.append(field_row)

            else:
                print("No save data found, starting new game")
                self._initialize_new_game()

        except Exception as e:
            print(f"Failed to load save data: {e}")
            self._initialize_new_game()

    def show_animal_selection_dialog(self):
        menu = QMenu(self)
        for animal_type in AnimalType:
            if animal_type != AnimalType.EMPTY:
                action = menu.addAction(
                    f"{animal_type.emoji} {animal_type.label} ({animal_type.price} coins)")
                action.setData(animal_type)

        action = menu.exec(QCursor.pos())
        if action:
            return action.data()
        return None

    def try_cleanup_dead_animal(self, field):
        if not field.animal or not field.animal.is_dead:
            return

        cleanup_cost = field.animal.get_cleanup_cost()
        animal_type = field.animal.animal_type
        reply = QMessageBox.question(
            self,
            'Clean up dead animal',
            f'Do you want to clean up this dead {animal_type.label} for {cleanup_cost} coins?',
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            if self.money >= cleanup_cost:
                self.money -= cleanup_cost
                self.stats[animal_type]["dead"] += 1
                field.remove_animal()
                self.update()
                self.save_game()
            else:
                QMessageBox.warning(self, "Cannot Clean",
                                    f"Not enough money!\nRequired: {cleanup_cost} coins")

    def can_unlock_field(self):
        return self.unlocked_fields < 16

    def try_unlock_field(self):
        if not self.can_unlock_field():
            QMessageBox.warning(self, "Cannot Buy", "No more plots available!")
            return False

        price = self.get_field_price()
        if self.money < price:
            QMessageBox.warning(self, "Cannot Buy",
                                f"Not enough money!\nRequired: {price} coins")
            return False

        reply = QMessageBox.question(
            self,
            'Buy Plot',
            f'Do you want to buy a new plot for {price} coins?',
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            self.money -= price
            self.unlocked_fields += 1
            self.update()
            self.save_game()
            return True
        return False

    def get_field_price(self):
        base_price = 500
        return int(base_price * (1.5 ** (self.unlocked_fields - 1)))

    def try_sell_animal(self, field):
        if not field.animal:
            return

        if not field.animal.can_sell():
            QMessageBox.warning(self, "Cannot Sell",
                                "This animal cannot be sold yet.\nGrowth must be 50% or higher.")
            return

        price = field.animal.get_sale_price()
        animal_type = field.animal.animal_type
        reply = QMessageBox.question(
            self,
            'Sell Animal',
            f'Do you want to sell this {animal_type.label} for {price} coins?',
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            self.money += price
            self.stats[animal_type]["sold"] += 1
            field.remove_animal()
            self.update()
            self.save_game()

    def paintEvent(self, event):
        painter = QPainter(self)

        # Stats panel width
        stats_panel_width = 250
        field_height = self.cell_size * 4

        # Draw wooden background for stats panel
        painter.drawPixmap(
            0, 0, stats_panel_width, self.height(),
            self.stats_bg_image
        )

        # Add semi-transparent overlay
        painter.fillRect(
            0, 0, stats_panel_width, self.height(),
            QColor(255, 255, 255, 100)
        )

        # Display money
        painter.setPen(QColor(0, 0, 0))
        font = painter.font()
        font.setPointSize(19)
        font.setBold(True)
        painter.setFont(font)
        painter.drawText(10, 20, f"Money: {self.money} coins")

        # Display statistics
        y_pos = 40
        font.setPointSize(14)
        painter.setFont(font)
        painter.drawText(10, y_pos, "Statistics:")
        y_pos += 15

        font.setBold(False)
        painter.setFont(font)
        for animal_type in [AnimalType.PIG, AnimalType.CHICKEN, AnimalType.COW]:
            stats = self.stats[animal_type]

            # Draw shadow
            painter.setPen(QColor(0, 0, 0, 100))
            painter.drawText(
                11,
                y_pos + 1,
                f"{animal_type.emoji} {animal_type.label}: "
                f"Sold: {stats['sold']}, "
                f"Dead: {stats['dead']}"
            )

            # Draw main text
            painter.setPen(QColor(0, 0, 0))
            painter.drawText(
                10,
                y_pos,
                f"{animal_type.emoji} {animal_type.label}: "
                f"Sold: {stats['sold']}, "
                f"Dead: {stats['dead']}"
            )
            y_pos += 25

        # Display next plot price
        if self.can_unlock_field():
            next_price = self.get_field_price()
            y_pos += 10
            painter.drawText(10, y_pos, "Next Plot Price:")
            y_pos += 20
            painter.drawText(10, y_pos, f"{next_price} coins")

        # Draw game field
        field_start_x = stats_panel_width

        # Draw fields
        for y in range(4):
            for x in range(4):
                field = self.fields[y][x]
                field_number = y * 4 + x + 1

                pos_x = field_start_x + (x * self.cell_size)
                pos_y = y * self.cell_size

                if field_number <= self.unlocked_fields:
                    # Draw unlocked tile
                    painter.drawPixmap(
                        pos_x,
                        pos_y,
                        self.cell_size,
                        self.cell_size,
                        self.tile_image
                    )

                    if field.animal:
                        # 動物の描画部分を修正
                        if field.animal:
                            if field.animal.is_dead:
                                # 死亡した動物の場合、お墓を表示
                                grave_size = min(self.cell_size - 20, self.grave_image.width())
                                painter.drawPixmap(
                                    pos_x + (self.cell_size - grave_size) // 2,
                                    pos_y + (self.cell_size - grave_size) // 2,
                                    grave_size,
                                    grave_size,
                                    self.grave_image
                                )
                                # 死亡テキストを表示（赤色で）
                                painter.setPen(QColor(255, 0, 0))
                                painter.drawText(
                                    pos_x,
                                    pos_y + self.cell_size - 5,
                                    f"Dead ({field.animal.animal_type.label})"
                                )
                            else:
                                # 生きている動物の通常表示
                                animal_image = self.animal_images[field.animal.animal_type]
                                animal_size = min(self.cell_size - 10, animal_image.width())
                                painter.drawPixmap(
                                    pos_x + (self.cell_size - animal_size) // 2,
                                    pos_y + (self.cell_size - animal_size) // 2,
                                    animal_size,
                                    animal_size,
                                    animal_image
                                )

                                # 生産物の表示（既存のコード）
                                if field.animal.has_product and field.animal.animal_type in [
                                    AnimalType.CHICKEN, AnimalType.COW
                                ]:
                                    product_image = self.product_images[field.animal.animal_type]
                                    product_size = min(self.cell_size // 4, product_image.width())
                                    painter.drawPixmap(
                                        pos_x + self.cell_size - product_size - 5,
                                        pos_y + self.cell_size - product_size - 5,
                                        product_size,
                                        product_size,
                                        product_image
                                    )

                                # 成長率表示（生きている動物のみ）
                                painter.setBrush(Qt.BrushStyle.NoBrush)
                                growth_text = f"{field.animal.growth}%"
                                if field.animal.can_sell():
                                    growth_text += f" (Value: {field.animal.get_sale_price()} coins)"
                                painter.setPen(QColor(0, 0, 0))
                                painter.drawText(
                                    pos_x,
                                    pos_y + self.cell_size - 5,
                                    growth_text
                                )
                else:
                    # Draw locked tile
                    painter.drawPixmap(
                        pos_x,
                        pos_y,
                        self.cell_size,
                        self.cell_size,
                        self.locked_tile_image
                    )

                    font = painter.font()
                    font.setPointSize(24)
                    painter.setFont(font)
                    painter.drawText(
                        pos_x + self.cell_size // 2 - 20,
                        pos_y + self.cell_size // 2 + 10,
                        "🔒"
                    )

    def mousePressEvent(self, event):
        stats_panel_width = 250
        adjusted_x = event.position().x() - stats_panel_width
        x = int(adjusted_x // self.cell_size)
        y = int(event.position().y() // self.cell_size)

        if 0 <= x < 4 and 0 <= y < 4:
            field_number = y * 4 + x + 1

            if field_number > self.unlocked_fields:
                self.try_unlock_field()
                return

            field = self.fields[y][x]
            if event.button() == Qt.MouseButton.LeftButton:
                if field.animal is None:
                    selected_type = self.show_animal_selection_dialog()
                    if selected_type:
                        purchase_price = selected_type.price
                        if self.money >= purchase_price:
                            field.add_animal(Animal(selected_type))
                            self.money -= purchase_price
                            self.update()
                            self.save_game()
                        else:
                            QMessageBox.warning(self, "Cannot Buy",
                                                f"Not enough money!\nRequired: {purchase_price} coins")
            elif event.button() == Qt.MouseButton.RightButton:
                if field.animal:
                    if field.animal.is_dead:
                        self.try_cleanup_dead_animal(field)
                    else:
                        self.try_sell_animal(field)

    def called(self, reviewer, card, ease):
        bonus_multiplier = 1.0
        if ease > 2:
            bonus_multiplier = 1.2

        total_production = 0
        for row in self.fields:
            for field in row:
                if field.animal:
                    field.animal.grow()
                    production = field.animal.produce() * bonus_multiplier
                    total_production += production

        if total_production > 0:
            self.money += total_production

        self.update()
        self.save_game()


def game_window():
    mw.myWidget = widget = GameWidget()
    widget.show()


