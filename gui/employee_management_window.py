from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel,
                             QPushButton, QGridLayout, QFrame, QScrollArea, QWidget, QMessageBox)
from PyQt6.QtCore import Qt

from ..constants import GRID_SIZE
from ..models.emploee import Employee


class EmployeeManagementWindow(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.setWindowTitle("Employee Management")
        self.setMinimumWidth(400)
        self.setMinimumHeight(500)


        main_layout = QVBoxLayout(self)

        title = QLabel("👥 Employee Management")
        title.setStyleSheet("font-size: 16px; font-weight: bold; margin: 10px;")
        main_layout.addWidget(title)

        self.money_label = QLabel(f"Money: {self.parent.money} coins")
        self.money_label.setStyleSheet("font-size: 14px; color: #white; margin: 5px;")
        main_layout.addWidget(self.money_label)


        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)


        content_widget = QWidget()
        self.content_layout = QVBoxLayout(content_widget)


        self.update_display()

        scroll.setWidget(content_widget)
        main_layout.addWidget(scroll)

        # 閉じるボタン
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
        close_btn.clicked.connect(self.close)
        main_layout.addWidget(close_btn)

    def get_position_name(self, x: int, y: int) -> str:
        field_number = y * GRID_SIZE + x
        pos_name = chr(65 + field_number)
        return f"{pos_name}"

    def create_employee_frame(self, x: int, y: int):
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

        if employee:
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

            # ボタンレイアウト
            button_layout = QHBoxLayout()

            if employee.level < employee.max_level:
                upgrade_cost = employee.get_upgrade_cost()
                upgrade_btn = QPushButton(f"Upgrade ({upgrade_cost} coins)")
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
                upgrade_btn.clicked.connect(
                    lambda: self.parent.upgrade_employee(employee))
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
            toggle_btn.clicked.connect(
                lambda: self.parent.toggle_employee(employee))
            button_layout.addWidget(toggle_btn)

            layout.addLayout(button_layout)

        else:
            hire_cost = Employee.calculate_hire_cost(x, y)
            header = QLabel(f"📍 Position {self.get_position_name(x, y)}")
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
            hire_btn.clicked.connect(lambda: self.try_hire_employee(x, y))
            layout.addWidget(hire_btn)

        frame.setLayout(layout)
        return frame

    def update_display(self):
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

    def try_hire_employee(self, x: int, y: int):
        hire_cost = Employee.calculate_hire_cost(x, y)
        if self.parent.money >= hire_cost:
            if self.parent.hire_employee(x, y):
                self.parent.money -= hire_cost
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