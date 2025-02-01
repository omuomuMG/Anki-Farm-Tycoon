import json
import random

from PyQt6.QtWidgets import QWidget, QMenu, QMessageBox, QPushButton
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPainter, QColor, QCursor, QFont
from aqt import gui_hooks

from .employee_management_window import EmployeeManagementWindow
from ..models.emploee import Employee
from .animal_breed import AnimalBreed
from .shop_window import ShopWindow
from .statistics_window import StatisticsWindow
from ..models.global_status import GlobalStats
from ..models.animal import Animal
from ..models.animal_type import AnimalType
from ..models.field import Field
from ..utils.resource_manager import ResourceManager
from ..utils.save_manager import SaveManager
from ..gui.paint_handler import PaintHandler
from ..constants import (
    CELL_SIZE, STATS_PANEL_WIDTH, GRID_SIZE,
    INITIAL_MONEY, BASE_FIELD_PRICE, FIELD_PRICE_MULTIPLIER, ADDON_DIR
)


class GameWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        # Set window properties
        window_width = STATS_PANEL_WIDTH + (CELL_SIZE * GRID_SIZE)
        window_height = CELL_SIZE * GRID_SIZE
        self.setGeometry(100, 100, window_width, window_height)
        self.setWindowTitle("Anki Ranch")


        self.breeds = {
            AnimalType.PIG: AnimalBreed(AnimalType.PIG),
            AnimalType.CHICKEN: AnimalBreed(AnimalType.CHICKEN),
            AnimalType.COW: AnimalBreed(AnimalType.COW)
        }

        self.employees = {}
        self.load_game()

        # Load resources
        self.resources = ResourceManager.load_all_resources()

        # Initialize paint handler
        self.paint_handler = PaintHandler()

        gui_hooks.reviewer_did_answer_card.append(self.called)


        self.global_stats = GlobalStats()
        self.load_global_stats()

        self.shop_button = QPushButton("Shop", self)
        self.shop_button.clicked.connect(self.show_shop)
        self.shop_button.setStyleSheet("""
                QPushButton {
                    background-color: #4CAF50;
                    color: white;
                    border: none;
                    padding: 5px;
                    border-radius: 3px;
                }
                QPushButton:hover {
                    background-color: #45a049;
                }
            """)

        self.employee_button = QPushButton("Employees", self)
        self.employee_button.clicked.connect(self.show_employee_management)
        self.employee_button.setStyleSheet("""
                QPushButton {
                    background-color: #9b59b6;
                    color: white;
                    border: none;
                    padding: 5px;
                    border-radius: 3px;
                }
                QPushButton:hover {
                    background-color: #8e44ad;
                }
            """)

        # ResetButton
        self.reset_button = QPushButton("Reset Game", self)
        self.reset_button.clicked.connect(self.reset_game)
        self.reset_button.setStyleSheet("""
            QPushButton {
                background-color: #ff6b6b;
                color: white;
                border: none;
                padding: 5px;
                border-radius: 3px;
            }
            QPushButton:hover {
                background-color: #ff5252;
            }
        """)

        # StatisticsButton
        self.stats_button = QPushButton("Global Statistics", self)
        self.stats_button.clicked.connect(self.show_statistics)
        self.stats_button.setStyleSheet("""
            QPushButton {
                background-color: #4a90e2;
                color: white;
                border: none;
                padding: 5px;
                border-radius: 3px;
            }
            QPushButton:hover {
                background-color: #357abd;
            }
        """)

    def show_employee_management(self):
        """従業員管理ウィンドウを表示"""
        employee_window = EmployeeManagementWindow(self)
        employee_window.exec()

    def get_field_by_position(self, position: int):
        """位置番号からフィールドを取得"""
        y = position // GRID_SIZE
        x = position % GRID_SIZE

        if 0 <= y < len(self.fields) and 0 <= x < len(self.fields[y]):
            return self.fields[y][x]
        return None

    def update_employees(self):
        """従業員の行動を更新"""
        for employee in self.employees.values():
            if not employee.enabled:
                continue

            field = self.get_field_by_position(employee.position)
            if not field:
                continue

            # 動物がいない場合は購入
            if not field.animal:
                animal_type = employee.choose_animal_to_buy()
                if self.money >= animal_type.price:
                    self.money -= animal_type.price
                    field.add_animal(Animal(animal_type, breed_level=self.breeds[animal_type].level))

            # 動物を売却するか判断
            elif employee.should_sell_animal(field.animal):
                price = field.animal.get_sale_price()
                salary = int(price * employee.get_salary_rate())
                self.money += (price - salary)
                employee.total_earnings += salary
                employee.total_sales += 1

                # 統計情報を更新
                animal_type = field.animal.animal_type
                self.stats[animal_type]["sold"] += 1
                self.global_stats.total_animals_sold += 1
                self.global_stats.total_money_earned += price
                self.global_stats.total_animals_sold_by_type[animal_type.name] += 1

                field.remove_animal()
                self.save_game()
                self.save_global_stats()


    def hire_employee(self, position: int) -> bool:
        """新しい従業員を雇用"""
        if position in self.employees:
            return False

        # 新しい従業員を作成（A, B, C...の順で名前を付ける）
        name = chr(65 + len(self.employees))
        employee = Employee(name=name, position=position)
        self.employees[position] = employee
        return True

    def upgrade_employee(self, employee: Employee):
        """従業員をレベルアップ"""
        if employee.level >= employee.max_level:
            return False

        cost = employee.get_upgrade_cost()
        if self.money >= cost:
            self.money -= cost
            employee.level += 1
            self.save_game()
            return True
        return False

    def toggle_employee(self, employee: Employee):
        """従業員の有効/無効を切り替え"""
        employee.enabled = not employee.enabled
        self.save_game()

    def show_shop(self):
        """ショップウィンドウを表示"""
        shop_window = ShopWindow(self)
        shop_window.exec()

    def show_statistics(self):
        """Show statistics window"""
        stats_window = StatisticsWindow(self.global_stats, self)
        stats_window.exec()

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
                        breed_level = self.breeds[animal_type].level
                        animal = Animal(animal_type, breed_level=breed_level)
                        animal.growth = animal_data["growth"]
                        animal.is_dead = animal_data["is_dead"]
                        animal.has_product = animal_data["has_product"]
                        animal.max_growth = animal_data["max_growth"]
                        field.animal = animal
                else:
                    field = Field(x, y)
                row.append(field)
                self.fields.append(row)

        breeds_data = save_data.get("breeds", {})
        for animal_type in AnimalType:
            if animal_type != AnimalType.EMPTY:
                breed_data = breeds_data.get(animal_type.name, {})
                self.breeds[animal_type].level = breed_data.get("level", 0)
                self.breeds[animal_type].is_unlocked = breed_data.get("is_unlocked", animal_type == AnimalType.CHICKEN)

        employees_data = save_data.get("employees", {})
        for pos_str, emp_data in employees_data.items():
            pos = int(pos_str)
            employee = Employee(emp_data["name"], pos)
            employee.level = emp_data["level"]
            employee.enabled = emp_data["enabled"]
            employee.total_earnings = emp_data["total_earnings"]
            employee.total_sales = emp_data["total_sales"]
            self.employees[pos] = employee

    def save_game(self):
        game_state = {
            "money": self.money,
            "unlocked_fields": self.unlocked_fields,
            "stats": {
                animal_type.name: stats  # AnimalTypeの名前をキーとして使用
                for animal_type, stats in self.stats.items()
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
            ],
            "breeds": {
                animal_type.name: {
                    "level": breed.level,
                    "is_unlocked": breed.is_unlocked
                }
                for animal_type, breed in self.breeds.items()
                if animal_type != AnimalType.EMPTY
            },
            # 従業員情報を追加
            "employees": {
                str(pos): {  # 位置を文字列に変換してキーとして使用
                    "name": emp.name,
                    "level": emp.level,
                    "enabled": emp.enabled,
                    "total_earnings": emp.total_earnings,
                    "total_sales": emp.total_sales,
                    "position": emp.position
                }
                for pos, emp in self.employees.items()
            }
        }
        SaveManager.save_game(game_state)


    def show_animal_selection_dialog(self):
        menu = QMenu(self)
        for animal_type in AnimalType:
            if animal_type != AnimalType.EMPTY:
                if self.breeds[animal_type].is_unlocked:
                    action = menu.addAction(
                        f"{animal_type.emoji} {animal_type.label} ({animal_type.price} coins)")
                    action.setData(animal_type)
                else:
                    action = menu.addAction(
                        f"{animal_type.emoji} {animal_type.label} (Locked)")
                    action.setEnabled(False)

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

            self.global_stats.total_animals_sold += 1
            self.global_stats.total_money_earned += price
            self.global_stats.total_animals_sold_by_type[animal_type.name] += 1
            field.remove_animal()
            self.update()
            self.save_game()
            self.save_global_stats()

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

    def check_game_over(self):
        if self.money < min(animal_type.price for animal_type in AnimalType
                          if animal_type != AnimalType.EMPTY):
            has_living_animals = any(
                field.animal and not field.animal.is_dead
                for row in self.fields
                for field in row
            )
            if not has_living_animals:
                self.show_game_over()

    def show_game_over(self):
        msg = QMessageBox(self)
        msg.setWindowTitle("Game Over")
        msg.setText("You've run out of money and have no living animals!")
        msg.setInformativeText(
            f"Total animals sold: {self.global_stats.total_animals_sold}\n"
            f"Total money earned: {self.global_stats.total_money_earned}\n"
            f"Highest money achieved: {self.global_stats.highest_money}\n"
            f"Days survived: {self.global_stats.current_day}\n"
            f"Highest day reached: {self.global_stats.highest_day}\n"
            "\nWould you like to reset the game?"
        )
        msg.setStandardButtons(QMessageBox.StandardButton.Yes |
                               QMessageBox.StandardButton.No)

        if msg.exec() == QMessageBox.StandardButton.Yes:
            self.reset_game()
        else:
            self.close()

    def reset_game(self):
        self.save_global_stats()
        self.money = INITIAL_MONEY
        self.unlocked_fields = 1
        self.fields = []
        for y in range(GRID_SIZE):
            row = []
            for x in range(GRID_SIZE):
                row.append(Field(x, y))
            self.fields.append(row)

        self.global_stats.current_day = 0
        self.global_stats.answers_count = 0
        self.update()
        self.save_game()
        self.initialize_new_game()

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

        painter.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        painter.drawText(10, 120, f"Day: {self.global_stats.current_day}")


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

            if field_number in self.employees:
                employee = self.employees[field_number]
                if employee.enabled:
                    painter.drawPixmap(
                        pos_x + self.cell_size - 20,
                        pos_y,
                        20,
                        20,
                        self.resources['employee_icon']
                    )

            self.shop_button.setGeometry(10, self.height() - 160, 100, 30)  # ShopButton
            self.employee_button.setGeometry(10, self.height() - 120, 100, 30)
            self.stats_button.setGeometry(10, self.height() - 80, 100, 30)  # StatisticsButton
            self.reset_button.setGeometry(10, self.height() - 40, 100, 30)  # ResetButton


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
                            breed_level = self.breeds[selected_type].level
                            field.add_animal(Animal(selected_type, breed_level=breed_level))
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
        pig_products = []
        for row in self.fields:
            for field in row:
                if (field.animal and
                        field.animal.animal_type == AnimalType.PIG and
                        field.animal.has_product):
                    pig_products.append(field)

        boosted_animals = []
        for pig_field in pig_products:
            available_animals = []
            for row in self.fields:
                for field in row:
                    if (field.animal and
                            not field.animal.is_dead and
                            field != pig_field):
                        available_animals.append(field)

            if available_animals:
                target_field = random.choice(available_animals)
                boost_amount = random.randint(3, 7)
                target_field.animal.growth_boost = boost_amount
                boosted_animals.append((target_field, boost_amount))

        total_production = 0
        for row in self.fields:
            for field in row:
                if field.animal:
                    if field.animal.growth >= field.animal.max_growth and not field.animal.is_dead:
                        self.global_stats.total_animals_died_by_type[field.animal.animal_type.name] += 1

                    field.animal.grow()
                    print(f"Animal growth: {field.animal.growth}%")


                    field.animal.has_product = False
                    production = field.animal.produce()
                    if production > 0:
                        total_production += production
                        print(f"Production: {production} coins")

        if total_production > 0:
            self.money += total_production
            self.global_stats.total_money_earned += total_production



        self.global_stats.update_money_record(self.money)
        self.global_stats.update_day_count()

        # ゲームオーバーチェック
        self.check_game_over()
        self.update_employees()

        self.update()
        self.save_game()
        self.save_global_stats()

    def save_global_stats(self):
        try:
            with open(ADDON_DIR / "global_stats.json", 'w') as f:
                json.dump(self.global_stats.to_dict(), f)
        except Exception as e:
            print(f"Error saving global stats: {e}")

    def load_global_stats(self):
        try:
            stats_file = ADDON_DIR / "global_stats.json"
            if stats_file.exists():
                with open(stats_file, 'r') as f:
                    data = json.load(f)
                    self.global_stats = GlobalStats.from_dict(data)
            else:
                self.global_stats = GlobalStats()
        except Exception as e:
            print(f"Error loading global stats: {e}")
            self.global_stats = GlobalStats()

