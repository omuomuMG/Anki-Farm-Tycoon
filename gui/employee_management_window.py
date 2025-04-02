from PyQt6.QtWidgets import (QVBoxLayout, QHBoxLayout, QLabel,
                             QPushButton, QGridLayout, QFrame, QScrollArea,
                             QWidget, QMessageBox, QComboBox, QGroupBox, QRadioButton)
from PyQt6.QtCore import Qt

from ..constants import GRID_SIZE
from .base_window import BaseWindow
from ..models.emploee import Employee


class EmployeeManagementWindow(BaseWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Employee Management")
        self.setMinimumWidth(400)
        self.setMinimumHeight(500)

    def setup_ui(self):
        self.main_layout = QVBoxLayout()
        self.setLayout(self.main_layout)


        title = QLabel("👥 Employee Management")
        title.setStyleSheet("font-size: 16px; font-weight: bold; margin: 10px;")
        self.main_layout.addWidget(title)

        self.money_label = QLabel(f"Money: {self.parent.money} coins")
        self.money_label.setStyleSheet("font-size: 14px; color: grey; margin: 5px;")
        self.main_layout.addWidget(self.money_label)


        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        self.content_widget = QWidget()
        self.content_layout = QVBoxLayout(self.content_widget)


        self.update_display()

        scroll.setWidget(self.content_widget)
        self.main_layout.addWidget(scroll)

        close_btn = QPushButton("Close")
        close_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                padding: 8px;
                border-radius: 4px;
                min-width: 80px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        self.register_button(close_btn, self.close)
        self.main_layout.addWidget(close_btn)

    def create_employee_frame(self, x: int, y: int):
        """従業員情報または雇用枠のフレームを作成"""
        frame = QFrame()
        frame.setFrameStyle(QFrame.Shape.Box | QFrame.Shadow.Raised)
        frame.setStyleSheet("""
            QFrame {
                background-color: #ffffff;
                border: 1px solid #bdc3c7;
                border-radius: 5px;
                margin: 5px;
                padding: 10px;
            }
        """)

        layout = QVBoxLayout()


        employee = None
        for emp in self.parent.employees.values():
            if emp.x == x and emp.y == y:
                employee = emp
                break

        if employee:  # 既存の従業員の場合
            header = QLabel(f"👨‍💼 Employee {employee.name}")
            header.setStyleSheet("font-size: 14px; font-weight: bold; color: #2c3e50;")
            layout.addWidget(header)

            info_layout = QGridLayout()
            level_text = QLabel(f"Level: {employee.level}/{employee.max_level}")
            level_text.setStyleSheet("font-weight: bold; color: #2c3e50;")
            info_layout.addWidget(level_text)

            salary_rate_text = QLabel(f"Salary Rate: {employee.get_salary_rate() * 100:.1f}%")
            salary_rate_text.setStyleSheet("font-weight: bold; color: #2c3e50;")
            info_layout.addWidget(salary_rate_text)

            total_sales_text = QLabel(f"Total Sales: {employee.total_sales}")
            total_sales_text.setStyleSheet("font-weight: bold; color: #2c3e50;")
            info_layout.addWidget(total_sales_text)

            total_earnings_text = QLabel(f"Total Earnings: {employee.total_earnings} coins")
            total_earnings_text.setStyleSheet("font-weight: bold; color: #2c3e50;")
            info_layout.addWidget(total_earnings_text)
            layout.addLayout(info_layout)
            
            # Add animal buying preferences section
            preferences_group = QGroupBox("Animal Buying Preference")
            preferences_layout = QVBoxLayout()
            
            # radio buttons for random and specific mode
            random_mode_radio = QRadioButton("Random (buy any available animal)")
            specific_mode_radio = QRadioButton("Specific animal type")
            
            # Set the radio button states based on employee preferences
            random_mode_radio.setChecked(employee.buy_randomly)
            specific_mode_radio.setChecked(not employee.buy_randomly)
            
    
            mode_layout = QVBoxLayout()
            mode_layout.addWidget(random_mode_radio)
            mode_layout.addWidget(specific_mode_radio)
            preferences_layout.addLayout(mode_layout)
            
            # Create dropdown for animal type selection
            animal_dropdown = QComboBox()
            animal_dropdown.addItem("Chicken", "chicken")
            animal_dropdown.addItem("Pig", "pig")
            animal_dropdown.addItem("Cow", "cow")
            
            # Set the current index based on employee preferences
            if employee.can_buy_chicken:
                animal_dropdown.setCurrentIndex(0)
            elif employee.can_buy_pig:
                animal_dropdown.setCurrentIndex(1)
            elif employee.can_buy_cow:
                animal_dropdown.setCurrentIndex(2)
            else:
                animal_dropdown.setCurrentIndex(0)
            
            
            animal_dropdown.setStyleSheet("""
                QComboBox {
                    background-color: white;
                    color: #2c3e50;
                    border: 1px solid #bdc3c7;
                    border-radius: 3px;
                    padding: 3px;
                    min-width: 100px;
                }
                QComboBox QAbstractItemView {
                    background-color: white;
                    color: #2c3e50;
                    selection-background-color: #3498db;
                    selection-color: white;
                }
            """)
            
            # Enable/disable the dropdown based on the mode
            animal_dropdown.setEnabled(not employee.buy_randomly)
            
            # event handler for mode change
            def on_mode_changed():
                is_random = random_mode_radio.isChecked()
                animal_dropdown.setEnabled(not is_random)
                
    
                employee.buy_randomly = is_random
                
                if is_random:
                    # Reset all preferences if random mode is selected
                    employee.can_buy_chicken = False
                    employee.can_buy_pig = False
                    employee.can_buy_cow = False
                else:
                    self.update_animal_preference(employee, animal_dropdown.currentData())
                
                employee.save_preferences()
            
            
            random_mode_radio.toggled.connect(on_mode_changed)
            
            
            animal_dropdown.currentIndexChanged.connect(
                lambda index, e=employee: self.update_animal_preference(e, animal_dropdown.currentData()) 
                if not e.buy_randomly else None
            )
            
            
            preferences_layout.addWidget(animal_dropdown)
            preferences_group.setLayout(preferences_layout)
            layout.addWidget(preferences_group)

            button_layout = QHBoxLayout()

            if employee.level < employee.max_level:
                upgrade_btn = QPushButton(f"Upgrade ({employee.get_upgrade_cost()} coins)")
                upgrade_btn.setStyleSheet("""
                    QPushButton {
                        background-color: #2ecc71;
                        color: white;
                        border: none;
                        padding: 5px;
                        border-radius: 3px;
                    }
                    QPushButton:hover {
                        background-color: #27ae60;
                    }
                """)
                self.register_button(
                    upgrade_btn,
                    lambda e=employee: self.handle_upgrade(e)
                )
                button_layout.addWidget(upgrade_btn)

            toggle_btn = QPushButton("Disable" if employee.enabled else "Enable")
            toggle_btn.setStyleSheet("""
                QPushButton {
                    background-color: #e74c3c;
                    color: white;
                    border: none;
                    padding: 5px;
                    border-radius: 3px;
                }
                QPushButton:hover {
                    background-color: #c0392b;
                }
            """)
            self.register_button(
                toggle_btn,
                lambda e=employee: self.handle_toggle(e)
            )
            button_layout.addWidget(toggle_btn)

            layout.addLayout(button_layout)

        else:
            hire_cost = Employee.calculate_hire_cost(x, y)
            field_number = y * GRID_SIZE + x + 1
            header = QLabel(f"📍 Position {chr(64 + field_number)}({x + 1}, {y + 1})")
            header.setStyleSheet("font-size: 14px; font-weight: bold; color: #2c3e50;")
            layout.addWidget(header)

            hire_btn = QPushButton(f"Hire Employee ({hire_cost} coins)")

            hire_btn.setStyleSheet("""
                QPushButton {
                    background-color: #3498db;
                    color: white;
                    border: none;
                    padding: 5px;
                    border-radius: 3px;
                }
                QPushButton:hover {
                    background-color: #2980b9;
                }
            """)
            self.register_button(
                hire_btn,
                lambda x=x, y=y: self.handle_hire(x, y)
            )
            layout.addWidget(hire_btn)

        frame.setLayout(layout)
        return frame

    def update_display(self):
        """表示を更新"""
        # self.cleanup_connections()


        while self.content_layout.count():
            item = self.content_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()


        for y in range(GRID_SIZE):
            for x in range(GRID_SIZE):
                if y * GRID_SIZE + x < self.parent.unlocked_fields:
                    frame = self.create_employee_frame(x, y)
                    self.content_layout.addWidget(frame)

        self.money_label.setText(f"Money: {self.parent.money} coins")


        self.content_layout.addStretch()
        
    def update_animal_preference(self, employee, animal_type):
        """Update which animal an employee can buy (only one type allowed)"""
        
        if not employee.buy_randomly:
            # Reset all preferences
            employee.can_buy_chicken = False
            employee.can_buy_pig = False
            employee.can_buy_cow = False
        
            # Set only the selected preference
            if animal_type == "chicken":
                employee.can_buy_chicken = True
            elif animal_type == "pig":
                employee.can_buy_pig = True
            elif animal_type == "cow":
                employee.can_buy_cow = True
        
        # Save preferences to the save file
        employee.save_preferences()
        

    def handle_hire(self, x: int, y: int):
        hire_cost = Employee.calculate_hire_cost(x, y)
        if self.parent.money >= hire_cost:
            if self.parent.hire_employee(x, y):
                self.parent.money -= hire_cost
                
                # Make sure to load preferences when hiring a new employee
                for emp in self.parent.employees.values():
                    if emp.x == x and emp.y == y:
                        emp.load_preferences()
                        break
                        
                self.parent.save_game()
                self.update_display()

                QMessageBox.information(
                    self,
                    "Hiring Successful",
                    f"New employee has been hired for position ({x + 1}, {y + 1})!"
                )
        else:
            QMessageBox.warning(
                self,
                "Cannot Hire",
                f"Not enough money!\nRequired: {hire_cost} coins"
            )

    def handle_hire(self, x: int, y: int):
        hire_cost = Employee.calculate_hire_cost(x, y)
        if self.parent.money >= hire_cost:
            if self.parent.hire_employee(x, y):
                self.parent.money -= hire_cost
                
                # Find the newly hired employee
                for emp in self.parent.employees.values():
                    if emp.x == x and emp.y == y:
                        # Set default animal buying preferences (default to chicken)
                        emp.can_buy_chicken = True
                        emp.can_buy_pig = False
                        emp.can_buy_cow = False
                        
                        # Save preferences explicitly
                        emp.save_preferences()
                        break
                        
                self.parent.save_game()
                self.update_display()

                QMessageBox.information(
                    self,
                    "Hiring Successful",
                    f"New employee has been hired for position ({x + 1}, {y + 1})!"
                )
        else:
            QMessageBox.warning(
                self,
                "Cannot Hire",
                f"Not enough money!\nRequired: {hire_cost} coins"
            )

    def handle_toggle(self, employee):
        employee.enabled = not employee.enabled
        self.parent.save_game()
        self.update_display()

        status = "enabled" if employee.enabled else "disabled"
        QMessageBox.information(
            self,
            "Status Changed",
            f"Employee {employee.name} has been {status}."
        )