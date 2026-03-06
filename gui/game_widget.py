import datetime
import json
import random
import copy

from PyQt6.QtWidgets import (QMenu, QMessageBox, QPushButton, QLabel, QWidget,
                             QVBoxLayout, QHBoxLayout, QFrame, QSizePolicy, QGridLayout)
from PyQt6.QtCore import Qt, QUrl, QTimer
from PyQt6.QtGui import QPainter, QColor, QCursor, QFont, QDesktopServices
from aqt import gui_hooks, mw

from ..models.employee import Employee
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
from .leaderboard import LeaderBoardWindow, get_user_data, update_user_data
from ..constants import (
    GRID_SIZE, INITIAL_MONEY, VERSION
)
from pathlib import Path

# use QWidget 
class GameWidget(QWidget):
    def __init__(self, parent=None):
        QWidget.__init__(self, parent)
        self.parent = parent
        
        # Set window properties
        self.setMinimumWidth(380)
        self.setMaximumWidth(500)
        self.setMinimumHeight(500)
        
        # 初始化数据
        self.breeds = {
            AnimalType.PIG: AnimalBreed(AnimalType.PIG),
            AnimalType.CHICKEN: AnimalBreed(AnimalType.CHICKEN),
            AnimalType.COW: AnimalBreed(AnimalType.COW),
            AnimalType.HORSE: AnimalBreed(AnimalType.HORSE)
        }
        
        self.employees = {}
        self.load_game()
        self.resources = ResourceManager.load_all_resources()
        self.paint_handler = PaintHandler()
        
        gui_hooks.reviewer_did_answer_card.append(self.called)

        self.global_stats = GlobalStats()
        self.load_global_stats()
        
        self.last_unlock_click_time = 0
        self.double_click_threshold = 500
        
        # 游戏区域参数
        self.game_offset_x = 0
        self.game_offset_y = 0
        self.cell_size = 60
        
        self.setup_ui()

    def setup_ui(self):
        """Create UI layout（创建 UI 布局）"""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(5, 5, 5, 5)
        main_layout.setSpacing(5)
        
        # === Statistics Panel（统计面板） ===
        stats_frame = QFrame()
        stats_frame.setStyleSheet("background-color: #FFF8DC; border-radius: 5px;")
        stats_frame.setFixedHeight(120)
        
        stats_layout = QVBoxLayout(stats_frame)
        stats_layout.setContentsMargins(10, 3, 10, 3)

        self.money_label = QLabel(f"Money: {self.money} coins")
        self.money_label.setStyleSheet("font-size: 13px; font-weight: bold; margin: 0px;")
        stats_layout.addWidget(self.money_label)

        self.day_label = QLabel(f"Day: {self.global_stats.current_day}")
        self.day_label.setStyleSheet("font-size: 11px; margin: 0px;")
        stats_layout.addWidget(self.day_label)
        
        # Statistical information（统计信息）
        stats_grid = QGridLayout()
        
        stats_grid.setContentsMargins(0, 0, 0, 0)  # 移除边距
        self.stat_labels = {}
        animals = [AnimalType.PIG, AnimalType.CHICKEN, AnimalType.COW, AnimalType.HORSE]
        for i, animal_type in enumerate(animals):
            row = i // 2  # 0, 0, 1, 1
            col = i % 2  # 0, 1, 0, 1
            label = QLabel(f"{animal_type.emoji} {animal_type.label}: Sold 0, Dead 0")
            label.setStyleSheet("font-size: 10px;")
            self.stat_labels[animal_type] = label
            stats_grid.addWidget(label, row, col)
        stats_layout.addLayout(stats_grid)
        
        main_layout.addWidget(stats_frame)
        
        # === 游戏区域 ===
        self.game_widget = QWidget()
        self.game_widget.setMinimumHeight(300)

        main_layout.addWidget(self.game_widget, stretch=1)
        
        # 关键：绑定绘制和鼠标事件到 game_widget
        self.game_widget.paintEvent = self.draw_game_area
        self.game_widget.mousePressEvent = self.handle_game_click

        # ========== Money 显示（带收益提示）==============
        money_row = QHBoxLayout()
        self.money_label = QLabel(f"Money: {self.money} coins")
        self.money_label.setStyleSheet("font-size: 13px; font-weight: bold; margin: 0px;")

        # Profit prompt label (green/red)
        self.money_change_label = QLabel("")
        self.money_change_label.setStyleSheet("""
            QLabel {
                color: #27ae60;
                font-size: 11px;
                font-weight: bold;
                margin-left: 5px;
            }
        """)
        money_row.addWidget(self.money_label)
        money_row.addWidget(self.money_change_label)
        money_row.addStretch()
        stats_layout.addLayout(money_row)

        # === Button panel 按钮面板 ===
        controls_frame = QFrame()
        controls_frame.setFixedHeight(220)  # 固定高度确保显示完整
        controls_frame.setStyleSheet("background-color: #f0f0f0; border-radius: 5px;")
        controls_layout = QVBoxLayout(controls_frame)
        controls_layout.setSpacing(5)
        controls_layout.setContentsMargins(8, 8, 8, 8)
        
        btn_style = """
            QPushButton {
                background-color: #A0522D;
                color: white;
                border: none;
                padding: 5px;
                border-radius: 4px;
                font-size: 11px;
                min-height: 26px;
            }
            QPushButton:hover { background-color: #cb6838; }
        """
        
        # Button row
        for texts, callbacks in [
            (["🐾 Shop", "👨‍🌾 Employee"], [self.show_shop, self.show_employee_management]),
            (["👑 Leader", "⭐ GitHub"], [self.show_leaderboard, 
                lambda: QDesktopServices.openUrl(QUrl("https://github.com/omuomuMG/Anki-Farm-Tycoon"))]),
            (["📈 Stats", "👍 Rate"], [self.show_statistics,
                lambda: QDesktopServices.openUrl(QUrl("https://ankiweb.net/shared/review/20342773"))]),
            (["🔄 Reset", "📗 Help"], [self.reset_game,
                lambda: QDesktopServices.openUrl(QUrl("https://github.com/omuomuMG/Anki-Farm-Tycoon/blob/master/Instruction.md"))]),
        ]:
            row = QHBoxLayout()
            for text, callback in zip(texts, callbacks):
                btn = QPushButton(text)
                btn.setStyleSheet(btn_style)
                btn.clicked.connect(callback)
                row.addWidget(btn)
            controls_layout.addLayout(row)
        
        # coffee_btn
        coffee_btn = QPushButton("☕ Buy me a coffee")
        coffee_btn.setStyleSheet(btn_style)
        coffee_btn.clicked.connect(lambda: QDesktopServices.openUrl(QUrl("https://buymeacoffee.com/omuomumg")))
        controls_layout.addWidget(coffee_btn)
        
        main_layout.addWidget(controls_frame)
        self.update_stat_labels()

    def show_money_change(self, amount, source=""):
        """显示金钱变化提示"""
        if amount == 0:
            return

        # Set text and color
        if amount > 0:
            text = f"+{amount}"
            color = "#27ae60"  # 绿色
        else:
            text = f"{amount}"
            color = "#e74c3c"  # 红色

        if source:
            text += f" ({source})"

        self.money_change_label.setText(text)
        self.money_change_label.setStyleSheet(f"""
            QLabel {{
                color: {color};
                font-size: 11px;
                font-weight: bold;
                margin-left: 5px;
            }}
        """)

        # 2秒后清除
        QTimer.singleShot(50, lambda: self.money_change_label.setText(""))

    def update_money_display(self, change=0, source=""):
        """更新金钱显示"""
        self.money_label.setText(f"Money: {self.money} coins")
        if change != 0:
            self.show_money_change(change, source)

    def update_stat_labels(self):
        """Updated statistics"""
        self.money_label.setText(f"Money: {self.money} coins")
        self.day_label.setText(f"Day: {self.global_stats.current_day}")
        for animal_type in [AnimalType.PIG, AnimalType.CHICKEN, AnimalType.COW, AnimalType.HORSE]:
            stat = self.stats[animal_type]
            self.stat_labels[animal_type].setText(
                 f"{animal_type.emoji} {animal_type.label}: Sold {stat['sold']}, Dead {stat['dead']}"
            )

    def draw_game_area(self, event):
        """绘制游戏区域 """
        painter = QPainter(self.game_widget)
        
        # 获取 game_widget 的实际尺寸
        widget_width = self.game_widget.width()
        widget_height = self.game_widget.height()
        
        # 计算格子大小（适应窗口）
        self.cell_size = min(widget_width // GRID_SIZE, widget_height // GRID_SIZE)
        self.cell_size = max(50, min(self.cell_size, 80))  # 限制范围
        
        # 计算居中偏移
        grid_width = self.cell_size * GRID_SIZE
        grid_height = self.cell_size * GRID_SIZE
        self.game_offset_x = (widget_width - grid_width) // 2
        self.game_offset_y = (widget_height - grid_height) // 2
        
        # 绘制每个格子
        for y in range(GRID_SIZE):
            for x in range(GRID_SIZE):
                field = self.fields[y][x]
                field_number = y * GRID_SIZE + x + 1
                
                # 关键：使用相对于 game_widget 的坐标
                pos_x = self.game_offset_x + (x * self.cell_size)
                pos_y = self.game_offset_y + (y * self.cell_size)

                # Draw field background
                if field_number <= self.unlocked_fields:
                    # 绘制地面
                    painter.drawPixmap(
                        pos_x, pos_y, 
                        self.cell_size, self.cell_size,
                        self.resources['tile']
                    )
                    # Draw field contents (animal, growth, etc.) 绘制动物
                    self.draw_field_content(painter, field, pos_x, pos_y)
                else:
                    # Draw locked field 绘制锁定格子
                    painter.drawPixmap(
                        pos_x, pos_y,
                        self.cell_size, self.cell_size,
                        self.resources['locked_tile']
                    )
                    # Draw lock icon 绘制锁
                    painter.setPen(QColor(0,0,0))
                    painter.drawText(
                        pos_x + self.cell_size//2 - 10,
                        pos_y + self.cell_size//2 + 5,
                        "🔒"
                    )

    def draw_field_content(self, painter, field, pos_x, pos_y):
        """绘制格子内容（动物等）"""
        if not field.animal:
            return
            
        animal = field.animal
        cell_size = self.cell_size
        
        if animal.is_dead:
            # 绘制坟墓
            grave_size = min(cell_size - 10, 40)
            painter.drawPixmap(
                pos_x + (cell_size - grave_size)//2,
                pos_y + (cell_size - grave_size)//2,
                grave_size, grave_size,
                self.resources['grave']
            )
        else:
            # 绘制动物
            animal_type = animal.animal_type
            animal_img = self.resources['animals'][animal_type]
            
            # 判断是否幼年
            is_child = animal.growth < 50
            if is_child and animal_type in self.resources.get('child_animals', {}):
                child_img = self.resources['child_animals'][animal_type]
                if not child_img.isNull():
                    animal_img = child_img
            
            # 计算绘制大小
            img_size = min(cell_size - 15, 50)
            painter.drawPixmap(
                pos_x + (cell_size - img_size)//2,
                pos_y + 5,
                img_size, img_size,
                animal_img
            )
            
            # 绘制成长度文字
            painter.setPen(QColor(0,0,0))
            font = painter.font()
            font.setPointSize(8)
            painter.setFont(font)
            
            growth_text = f"{int(animal.growth)}%"
            if animal.can_sell():
                growth_text += f" ${animal.get_sale_price()}"
            
            painter.drawText(
                pos_x + 3,
                pos_y + cell_size - 3,
                growth_text
            )
            
            # 绘制产物
            if animal.has_product:
                product_img = self.resources['products'].get(animal_type)
                if product_img:
                    p_size = cell_size // 3
                    painter.drawPixmap(
                        pos_x + cell_size - p_size - 2,
                        pos_y + cell_size - p_size - 2,
                        p_size, p_size,
                        product_img
                    )



    def buy_animal(self, x, y):
        """购买动物"""
        field = self.fields[y][x]
        selected_type = self.show_animal_selection_dialog()
        if selected_type:
            if self.money >= selected_type.price:
                self.money -= selected_type.price
                breed_level = self.breeds[selected_type].level
                field.add_animal(Animal(selected_type, breed_level=breed_level))
                self.save_game()
                self.update()
                self.update_stat_labels()
                # 显示花费
                self.update_money_display(-selected_type.price, f"buy {selected_type.label}")
            else:
                QMessageBox.warning(self, "Cannot Buy", 
                    f"Not enough money! Need {selected_type.price} coins")

    def show_animal_selection_dialog(self):
        """显示动物选择菜单"""
        menu = QMenu(self)
        for animal_type in AnimalType:
            if animal_type != AnimalType.EMPTY:
                breed = self.breeds[animal_type]
                if breed.is_unlocked:
                    action = menu.addAction(
                        f"{animal_type.emoji} {animal_type.label} ({animal_type.price} coins)")
                    action.setData(animal_type)
                else:
                    action = menu.addAction(
                        f"{animal_type.emoji} {animal_type.label} (Locked - {breed.get_unlock_cost()} coins)")
                    action.setEnabled(False)
        
        action = menu.exec(QCursor.pos())
        return action.data() if action else None





    def show_shop(self):
        shop_window = ShopWindow(self)
        shop_window.exec()

    def show_employee_management(self):
        from .employee_management_window import EmployeeManagementWindow
        employee_window = EmployeeManagementWindow(self)
        employee_window.exec()

    def show_statistics(self):
        stats_window = StatisticsWindow(self.global_stats, self)
        stats_window.exec()





    def show_temp_message(self, text, color_type="blue"):
        """通用临时消息显示"""
        colors = {
            "red": "#e74c3c",
            "blue": "#3498db",
            "orange": "#f39c12",
            "green": "#27ae60"
        }
        color = colors.get(color_type, "#3498db")

        msg = QLabel(text, self.game_widget)
        msg.setStyleSheet(f"""
            QLabel {{
                background-color: {color};
                color: white;
                padding: 8px 12px;
                border-radius: 4px;
                font-size: 12px;
                font-weight: bold;
            }}
        """)
        msg.adjustSize()

        # 确保不超出边界
        x = max(10, (self.game_widget.width() - msg.width()) // 2)
        y = 10
        msg.move(x, y)
        msg.show()
        msg.raise_()

        QTimer.singleShot(2000, msg.deleteLater)

    def try_unlock_field(self):
        """尝试解锁新土地 - 修复提示"""
        import time
        current_time = int(time.time() * 1000)

        cost = 500 + (self.unlocked_fields * 200)

        if self.money < cost:
            self.show_temp_message(f"Need {cost} coins!", "red")
            return

        if current_time - self.last_unlock_click_time < self.double_click_threshold:
            self.money -= cost
            self.unlocked_fields += 1
            self.save_game()
            self.update_stat_labels()
            self.update()
            self.last_unlock_click_time = 0

            # 显示花费（负数表示支出）
            self.update_money_display(-cost, "unlock land")
            self.show_temp_message(f"New land unlocked!", "blue")

            self.show_temp_message(f"New land! Cost: {cost}", "blue")
        else:
            self.last_unlock_click_time = current_time
            self.show_temp_message(f"Double-click to unlock ({cost})", "orange")


    # 数据加载保存方法（保持原逻辑）
    def load_game(self):
        save_data = SaveManager.load_game()
        if save_data:
            self.load_saved_game(save_data)
        else:
            self.initialize_new_game()

    def initialize_new_game(self):
        self.money = INITIAL_MONEY
        self.unlocked_fields = 1
        self.stats = {
            AnimalType.PIG: {"sold": 0, "dead": 0},
            AnimalType.CHICKEN: {"sold": 0, "dead": 0},
            AnimalType.COW: {"sold": 0, "dead": 0},
            AnimalType.HORSE: {"sold": 0, "dead": 0}
        }
        self.employees = {}
        
        for breed in self.breeds.values():
            breed.level = 0
            breed.is_unlocked = (breed.animal_type == AnimalType.CHICKEN)
        
        self.fields = [[Field(x, y) for x in range(GRID_SIZE)] for y in range(GRID_SIZE)]
        self.save_game()

    def load_saved_game(self, save_data):
        self.money = save_data.get("money", INITIAL_MONEY)
        self.unlocked_fields = save_data.get("unlocked_fields", 1)
        
        self.stats = {}
        for animal_type in AnimalType:
            if animal_type != AnimalType.EMPTY:
                self.stats[animal_type] = save_data.get("stats", {}).get(
                    animal_type.name, {"sold": 0, "dead": 0}
                )
        
        self.fields = []
        saved_fields = save_data.get("fields", [])
        for y in range(GRID_SIZE):
            row = []
            for x in range(GRID_SIZE):
                field = Field(x, y)
                if y < len(saved_fields) and x < len(saved_fields[y]):
                    field_data = saved_fields[y][x]
                    if field_data.get("animal"):
                        animal_data = field_data["animal"]
                        animal_type = AnimalType[animal_data["type"]]
                        animal = Animal(animal_type, breed_level=self.breeds[animal_type].level)
                        animal.growth = animal_data.get("growth", 0)
                        animal.is_dead = animal_data.get("is_dead", False)
                        animal.has_product = animal_data.get("has_product", False)
                        field.animal = animal
                row.append(field)
            self.fields.append(row)
        
        # 加载 breeds
        breeds_data = save_data.get("breeds", {})
        for animal_type in AnimalType:
            if animal_type != AnimalType.EMPTY:
                breed_data = breeds_data.get(animal_type.name, {})
                self.breeds[animal_type].level = breed_data.get("level", 0)
                self.breeds[animal_type].is_unlocked = breed_data.get(
                    "is_unlocked", animal_type == AnimalType.CHICKEN
                )

    def save_game(self):
        game_state = {
            "Version": VERSION,
            "money": self.money,
            "previous_money": getattr(self, 'previous_money', self.money),  # 添加这行
            "unlocked_fields": self.unlocked_fields,
            "stats": {k.name: v for k, v in self.stats.items()},
            "fields": [[{
                "x": f.x, "y": f.y,
                "animal": {
                    "type": f.animal.animal_type.name,
                    "growth": f.animal.growth,
                    "is_dead": f.animal.is_dead,
                    "has_product": f.animal.has_product,
                } if f.animal else None
            } for f in row] for row in self.fields],
            "breeds": {
                k.name: {"level": v.level, "is_unlocked": v.is_unlocked}
                for k, v in self.breeds.items() if k != AnimalType.EMPTY
            },
            "employees": {}
        }
        SaveManager.save_game(game_state)







    def update_employees(self):
        """更新员工自动操作"""
        for employee in self.employees.values():
            if not employee.enabled:
                continue
            
            field = self.get_field_by_employee(employee)
            if not field:
                continue
            
            if not field.animal:
                # 购买动物
                animal_type = employee.choose_animal_to_buy()
                if self.money >= animal_type.price:
                    self.money -= animal_type.price
                    field.add_animal(Animal(animal_type, breed_level=self.breeds[animal_type].level))
            elif field.animal and employee.should_sell_animal(field.animal):
                # 出售动物
                price = field.animal.get_sale_price()
                salary = int(price * employee.get_salary_rate())
                self.money += (price - salary)
                employee.total_earnings += price
                employee.total_sales += 1
                
                animal_type = field.animal.animal_type
                self.stats[animal_type]["sold"] += 1
                self.global_stats.total_animals_sold += 1
                self.global_stats.total_money_earned += price
                
                field.remove_animal()
                self.save_game()

    def get_field_by_employee(self, employee):
        if 0 <= employee.y < len(self.fields) and 0 <= employee.x < len(self.fields[employee.y]):
            return self.fields[employee.y][employee.x]
        return None

    def reset_game(self):
        """重置游戏"""
        reply = QMessageBox.question(self, 'Reset Game',
                                     'Are you sure you want to reset? Global stats will be kept.',
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)

        if reply == QMessageBox.StandardButton.Yes:
            self.initialize_new_game()

    def handle_game_click(self, event):
        """Handle clicks on the game area 处理游戏区域点击 """
        # Get the click position (relative to the game_widget)
        click_x = int(event.position().x())
        click_y = int(event.position().y())

        # Check if it is within the game grid 检查是否在游戏网格内
        grid_width = self.cell_size * GRID_SIZE
        grid_height = self.cell_size * GRID_SIZE

        if (click_x < self.game_offset_x or
                click_x >= self.game_offset_x + grid_width or
                click_y < self.game_offset_y or
                click_y >= self.game_offset_y + grid_height):
            return  # 点击在网格外

        # Calculate grid coordinates 计算格子坐标
        relative_x = click_x - self.game_offset_x
        relative_y = click_y - self.game_offset_y
        grid_x = relative_x // self.cell_size
        grid_y = relative_y // self.cell_size

        # 边界检查
        if not (0 <= grid_x < GRID_SIZE and 0 <= grid_y < GRID_SIZE):
            return

        field_number = grid_y * GRID_SIZE + grid_x + 1

        # 处理点击逻辑
        if field_number > self.unlocked_fields:
            self.try_unlock_field()
            return

        field = self.fields[grid_y][grid_x]

        if event.button() == Qt.MouseButton.LeftButton:
            if field.animal is None:
                self.buy_animal(grid_x, grid_y)
            else:
                # Left-click on an existing animal to sell it (if it is sellable)
                if field.animal.can_sell():
                    self.sell_animal_directly(field)
                else:
                    self.show_cannot_sell_message(field.animal)

        elif event.button() == Qt.MouseButton.RightButton:
            if field.animal:
                self.sell_animal_directly(field)

        self.update()
        self.update_stat_labels()

    # 其他方法（sell_animal_directly, show_shop 等）保持不变...
    def sell_animal_directly(self, field):
        """直接出售动物"""
        if not field.animal or not field.animal.can_sell():
            return

        animal = field.animal
        price = animal.get_sale_price()
        animal_type = animal.animal_type

        # 更新统计
        self.stats[animal_type]["sold"] += 1
        self.global_stats.total_animals_sold += 1
        self.global_stats.total_money_earned += price
        self.global_stats.total_animals_sold_by_type[animal_type.name] += 1

        # 移除动物，增加金钱
        field.remove_animal()
        self.money += price

        self.save_game()
        self.save_global_stats()
        self.update_stat_labels()

        # 显示出售提示
        self.update_money_display(price, f"sold {animal_type.label}")

        # 显示提示
        self.show_sale_message(animal_type.label, price)

    def show_sale_message(self, animal_name, price):
        """显示出售提示"""
        msg = QLabel(f"Sold {animal_name} for {price} coins!", self.game_widget)
        msg.setStyleSheet("""
            QLabel {
                background-color: #27ae60;
                color: white;
                padding: 8px;
                border-radius: 4px;
                font-weight: bold;
            }
        """)
        msg.adjustSize()

        x = (self.game_widget.width() - msg.width()) // 2
        y = 10
        msg.move(x, y)
        msg.show()
        msg.raise_()
        QTimer.singleShot(2000, msg.deleteLater)

    def show_cannot_sell_message(self, animal):
        """显示不能出售提示"""
        msg = QLabel(f"Need 50% growth! Now: {int(animal.growth)}%", self.game_widget)
        msg.setStyleSheet("""
            QLabel {
                background-color: #e74c3c;
                color: white;
                padding: 8px;
                border-radius: 4px;
                font-weight: bold;
            }
        """)
        msg.adjustSize()  # 自动调整大小

        # 显示在游戏区域顶部中央
        x = (self.game_widget.width() - msg.width()) // 2
        y = 10
        msg.move(x, y)
        msg.show()
        msg.raise_()  # 确保在最上层
        QTimer.singleShot(2000, msg.deleteLater)

    def called(self, reviewer, card, ease):
        """Anki 卡片回答回调"""
        # 记录之前金钱
        old_money = self.money

        # 猪的特殊效果
        pig_boosts = []
        for row in self.fields:
            for field in row:
                if (field.animal and field.animal.animal_type == AnimalType.PIG
                        and field.animal.has_product):
                    # 随机加速其他动物
                    for target_row in self.fields:
                        for target in target_row:
                            if target.animal and target != field and not target.animal.is_dead:
                                if random.random() < 0.3:
                                    boost = random.randint(3, 7)
                                    target.animal.growth_boost = boost
                                    pig_boosts.append((target, boost))

        # 所有动物成长
        total_production = 0
        production_sources = []  # 记录产物来源

        for row in self.fields:
            for field in row:
                if field.animal:
                    if field.animal.growth >= field.animal.max_growth and not field.animal.is_dead:
                        field.animal.is_dead = True
                        self.stats[field.animal.animal_type]["dead"] += 1
                        self.global_stats.total_animals_died_by_type[field.animal.animal_type.name] += 1
                    else:
                        field.animal.grow()
                        production = field.animal.produce()
                        if production > 0:
                            total_production += production
                            self.global_stats.total_animals_production_by_type[field.animal.animal_type.name] += 1

                            # 记录产物类型
                            animal_name = field.animal.animal_type.label
                            production_sources.append((animal_name, production))

                    # 死亡动物随机移除
                    if field.animal.is_dead:
                        remove_probability = random.randint(0, 15)
                        if remove_probability == 0:
                            self.stats[field.animal.animal_type]["dead"] += 1
                            self.global_stats.total_animals_died_by_type[field.animal.animal_type.name] = \
                            self.stats[field.animal.animal_type]["dead"]
                            field.remove_animal()

        # 产物收益
        if total_production > 0:
            self.money += total_production
            self.global_stats.total_money_earned += total_production

            # 显示产物提示（合并显示）
            if len(production_sources) <= 2:
                source_text = ", ".join([f"{name}+{val}" for name, val in production_sources])
            else:
                source_text = f"{len(production_sources)} items"
            self.update_money_display(total_production, source_text)

        # 随机奖励
        bonus = random.randint(0, 2)
        if bonus > 0:
            self.money += bonus
            self.global_stats.total_money_earned += bonus
            # 延迟显示，避免覆盖产物提示
            QTimer.singleShot(50, lambda b=bonus: self.update_money_display(b, "bonus"))

        self.global_stats.update_money_record(self.money)
        self.global_stats.update_day_count()

        self.update_employees()
        self.save_game()
        self.save_global_stats()
        self.update()
        self.update_stat_labels()

        # 如果没有产物和奖励，显示学习完成
        if total_production == 0 and bonus == 0:
            self.update_money_display(0, "study")

    def save_global_stats(self):
        try:
            profile_dir = Path(mw.pm.profileFolder())
            save_path = profile_dir / "collection.media/_anki_farm_tycoon_global_stats.json"
            with open(save_path, 'w') as f:
                json.dump(self.global_stats.to_dict(), f)
        except Exception as e:
            print(f"Error saving global stats: {e}")

    def load_global_stats(self):
        try:
            profile_dir = Path(mw.pm.profileFolder())
            save_path = profile_dir / "collection.media/_anki_farm_tycoon_global_stats.json"
            if not save_path.exists():
                save_path = profile_dir / "anki_farm_tycoon_global_stats.json"

            if save_path.exists():
                with open(save_path, 'r') as f:
                    self.global_stats = GlobalStats.from_dict(json.load(f))
            else:
                self.global_stats = GlobalStats()
        except Exception as e:
            print(f"Error loading global stats: {e}")
            self.global_stats = GlobalStats()

    def show_leaderboard(self):
        leaderboard_data = get_user_data()
        leaderboard_window = LeaderBoardWindow(leaderboard_data, self)
        leaderboard_window.exec()
