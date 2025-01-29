from PyQt6.QtWidgets import QWidget, QMenu, QMessageBox
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPainter, QColor, QCursor
from aqt import gui_hooks

from ..models.animal import Animal
from ..models.animal_type import AnimalType
from ..models.field import Field
from ..utils.resource_manager import ResourceManager
from ..utils.save_manager import SaveManager
from ..gui.paint_handler import PaintHandler
from ..constants import (
    CELL_SIZE, STATS_PANEL_WIDTH, GRID_SIZE,
    INITIAL_MONEY, BASE_FIELD_PRICE, FIELD_PRICE_MULTIPLIER
)


class GameWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        # Set window properties
        window_width = STATS_PANEL_WIDTH + (CELL_SIZE * GRID_SIZE)
        window_height = CELL_SIZE * GRID_SIZE
        self.setGeometry(100, 100, window_width, window_height)
        self.setWindowTitle("Ranch")

        # Initialize game state
        self.load_game()

        # Load resources
        self.resources = ResourceManager.load_all_resources()

        # Initialize paint handler
        self.paint_handler = PaintHandler()

        gui_hooks.reviewer_did_answer_card.append(self.called)

    def load_game(self):
        """Load or initialize game state"""
        save_data = SaveManager.load_game()

        if save_data:
            self.load_saved_game(save_data)
        else:
            self.initialize_new_game()

    def initialize_new_game(self):
        """Initialize a new game state"""
        self.money = INITIAL_MONEY
        self.unlocked_fields = 1
        self.stats = {
            AnimalType.PIG: {"sold": 0, "cleaned": 0},
            AnimalType.CHICKEN: {"sold": 0, "cleaned": 0},
            AnimalType.COW: {"sold": 0, "cleaned": 0}
        }

        # Initialize fields
        self.fields = []
        for y in range(GRID_SIZE):
            row = []
            for x in range(GRID_SIZE):
                row.append(Field(x, y))
            self.fields.append(row)

    def load_saved_game(self, save_data):
        """Load game state from save data"""
        self.money = save_data["money"]
        self.unlocked_fields = save_data["unlocked_fields"]

        # Load statistics
        self.stats = {}
        for animal_type in AnimalType:
            if animal_type != AnimalType.EMPTY:
                self.stats[animal_type] = save_data["stats"].get(
                    animal_type.name, {"sold": 0, "cleaned": 0}
                )

        # Load fields
        self.fields = []
        saved_fields = save_data["fields"]

        for y in range(GRID_SIZE):
            row = []
            for x in range(GRID_SIZE):
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
                row.append(field)
            self.fields.append(row)

    def save_game(self):
        """Save current game state"""
        game_state = {
            "money": self.money,
            "unlocked_fields": self.unlocked_fields,
            "stats": self.stats,
            "fields": self.fields
        }
        SaveManager.save_game(game_state)

    def show_animal_selection_dialog(self):
        """Show dialog for animal selection"""
        menu = QMenu(self)
        for animal_type in AnimalType:
            if animal_type != AnimalType.EMPTY:
                action = menu.addAction(
                    f"{animal_type.emoji} {animal_type.label} ({animal_type.price} coins)")
                action.setData(animal_type)

        action = menu.exec(QCursor.pos())
        return action.data() if action else None

    def try_cleanup_dead_animal(self, field):
        """Handle dead animal cleanup"""
        if not field.animal or not field.animal.is_dead:
            return

        cleanup_cost = field.animal.get_cleanup_cost()
        animal_type = field.animal.animal_type

        reply = QMessageBox.question(
            self,
            'Remove grave',
            f'Do you want to say goodbye to {animal_type.label} and remove grave for {cleanup_cost} coins?',
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            if self.money >= cleanup_cost:
                self.money -= cleanup_cost
                self.stats[animal_type]["cleaned"] += 1
                field.remove_animal()
                self.update()
                self.save_game()
            else:
                QMessageBox.warning(
                    self,
                    "Cannot remove grave",
                    f"Not enough money!\nRequired: {cleanup_cost} coins"
                )

    def try_sell_animal(self, field):
        """Handle animal selling"""
        if not field.animal or not field.animal.can_sell():
            QMessageBox.warning(
                self,
                "Cannot Sell",
                "This animal cannot be sold yet.\nGrowth must be 50% or higher."
            )
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

    def get_field_price(self):
        """Calculate price for next field"""
        return int(BASE_FIELD_PRICE * (FIELD_PRICE_MULTIPLIER ** (self.unlocked_fields - 1)))

    def can_unlock_field(self):
        """Check if more fields can be unlocked"""
        return self.unlocked_fields < (GRID_SIZE * GRID_SIZE)

    def try_unlock_field(self):
        """Handle field unlocking"""
        if not self.can_unlock_field():
            QMessageBox.warning(self, "Cannot Buy", "No more plots available!")
            return False

        price = self.get_field_price()
        if self.money < price:
            QMessageBox.warning(
                self,
                "Cannot Buy",
                f"Not enough money!\nRequired: {price} coins"
            )
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

    def paintEvent(self, event):
        """Handle paint event"""
        painter = QPainter(self)

        # Draw stats background
        painter.drawPixmap(
            0, 0, STATS_PANEL_WIDTH, self.height(),
            self.resources['stats_bg']
        )

        # Add overlay
        painter.fillRect(
            0, 0, STATS_PANEL_WIDTH, self.height(),
            QColor(255, 255, 255, 100)
        )

        # Draw statistics
        self.paint_handler.draw_statistics(painter, self.stats, self.money)


        # Draw fields
        for y in range(GRID_SIZE):
            for x in range(GRID_SIZE):
                field = self.fields[y][x]
                field_number = y * GRID_SIZE + x + 1
                pos_x = STATS_PANEL_WIDTH + (x * CELL_SIZE)
                pos_y = y * CELL_SIZE

                # Draw field background
                if field_number <= self.unlocked_fields:
                    painter.drawPixmap(
                        pos_x, pos_y, CELL_SIZE, CELL_SIZE,
                        self.resources['tile']
                    )
                    # Draw field contents (animal, growth, etc.)
                    self.paint_handler.draw_field(
                        painter, field, self.resources, pos_x, pos_y
                    )
                else:
                    # Draw locked field
                    painter.drawPixmap(
                        pos_x, pos_y, CELL_SIZE, CELL_SIZE,
                        self.resources['locked_tile']
                    )
                    # Draw lock icon
                    font = painter.font()
                    font.setPointSize(24)
                    painter.setFont(font)
                    painter.drawText(
                        pos_x + CELL_SIZE // 2 - 20,
                        pos_y + CELL_SIZE // 2 + 10,
                        "🔒"
                    )

    def mousePressEvent(self, event):
        """Handle mouse press events"""
        adjusted_x = event.position().x() - STATS_PANEL_WIDTH
        x = int(adjusted_x // CELL_SIZE)
        y = int(event.position().y() // CELL_SIZE)

        if 0 <= x < GRID_SIZE and 0 <= y < GRID_SIZE:
            field_number = y * GRID_SIZE + x + 1

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
                            QMessageBox.warning(
                                self,
                                "Cannot Buy",
                                f"Not enough money!\nRequired: {purchase_price} coins"
                            )
            elif event.button() == Qt.MouseButton.RightButton:
                if field.animal:
                    if field.animal.is_dead:
                        self.try_cleanup_dead_animal(field)
                    else:
                        self.try_sell_animal(field)

    def called(self, reviewer, card, ease):
        """Handle Anki card review events"""
        print("Card answered, updating animals...")

        total_production = 0
        for row in self.fields:
            for field in row:
                if field.animal and not field.animal.is_dead:
                    field.animal.grow()
                    print(f"Animal growth: {field.animal.growth}%")


                    field.animal.has_product = False
                    production = field.animal.produce()
                    if production > 0:
                        total_production += production
                        print(f"Production: {production} coins")

        if total_production > 0:
            self.money += total_production

        self.update()
        self.save_game()