# gui/shop_window.py

from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel,
                             QPushButton, QGridLayout, QFrame, QMessageBox)
from PyQt6.QtCore import Qt
from ..models.animal_type import AnimalType


class ShopWindow(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.setWindowTitle("Animal Shop")
        self.setMinimumWidth(400)

        # メインレイアウトを保持
        self.main_layout = QVBoxLayout()
        self.setLayout(self.main_layout)

        self.initUI()

    def create_animal_frame(self, animal_type):
        breed = self.parent.breeds[animal_type]

        frame = QFrame()
        frame.setFrameStyle(QFrame.Shape.Box | QFrame.Shadow.Raised)
        frame.setStyleSheet("""
            QFrame {
                background-color: #ffffff;
                border: 1px solid #bdc3c7;
                border-radius: 5px;
                margin: 5px;
                padding: 5px;
            }
        """)

        layout = QVBoxLayout()

        header = QLabel(f"{animal_type.emoji} {animal_type.label}")
        header.setStyleSheet("font-size: 14px; font-weight: bold; color: #2c3e50;")
        layout.addWidget(header)


        info_layout = QGridLayout()

        info_text_style = """
                QLabel {
                    color: #2c3e50;
                    font-size: 12px;
                }
            """

        if breed.is_unlocked:
            level_label = QLabel(f"Level: {breed.level}/{breed.max_level}")
            chance_label = QLabel(f"Production chance: {breed.get_production_chance() * 100:.1f}%")
            level_label.setStyleSheet(info_text_style)
            chance_label.setStyleSheet(info_text_style)
            info_layout.addWidget(level_label, 0, 0)
            info_layout.addWidget(chance_label, 1, 0)


            if breed.level < breed.max_level:
                upgrade_cost = breed.get_upgrade_cost()
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
                    lambda checked, at=animal_type: self.upgrade_breed(at))
                info_layout.addWidget(upgrade_btn, 0, 1)
            else:
                max_level_label = QLabel("Maximum Level Reached!")
                max_level_label.setStyleSheet("color: #27ae60; font-weight: bold;")
                info_layout.addWidget(max_level_label, 0, 1)
        else:
            unlock_cost = breed.get_unlock_cost()

            info_text_style = """
                    QLabel {
                        color: #2c3e50;
                        font-size: 12px;
                    }
                """

            lockInfoLabel = QLabel("Status: Locked")
            lockInfoLabel.setStyleSheet(info_text_style)

            info_layout.addWidget(lockInfoLabel, 0, 0)
            unlock_btn = QPushButton(f"Unlock ({unlock_cost} coins)")
            unlock_btn.setStyleSheet("""
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
            unlock_btn.clicked.connect(
                lambda checked, at=animal_type: self.unlock_breed(at))
            info_layout.addWidget(unlock_btn, 1, 0)

        layout.addLayout(info_layout)
        frame.setLayout(layout)
        return frame

    def initUI(self):

        title_style = "font-size: 16px; font-weight: bold; margin: 10px;"

        title = QLabel("🏪 Animal Shop")
        title.setStyleSheet(title_style)
        self.main_layout.addWidget(title)


        self.money_label = QLabel(f"Your money: {self.parent.money} coins")
        self.money_label.setStyleSheet("font-size: 14px; color: white; margin: 5px;")
        self.main_layout.addWidget(self.money_label)


        self.frames = {}

        for animal_type in [AnimalType.CHICKEN, AnimalType.PIG, AnimalType.COW]:
            frame = self.create_animal_frame(animal_type)
            self.frames[animal_type] = frame
            self.main_layout.addWidget(frame)


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
        self.main_layout.addWidget(close_btn)

    def update_display(self):
        self.money_label.setText(f"Your money: {self.parent.money} coins")


        for frame in self.frames.values():
            frame.setParent(None)
            frame.deleteLater()
        self.frames.clear()


        for animal_type in [AnimalType.CHICKEN, AnimalType.PIG, AnimalType.COW]:
            frame = self.create_animal_frame(animal_type)
            self.frames[animal_type] = frame
            self.main_layout.insertWidget(self.main_layout.count() - 1, frame)

    def unlock_breed(self, animal_type):
        breed = self.parent.breeds[animal_type]
        cost = breed.get_unlock_cost()

        if self.parent.money >= cost:
            self.parent.money -= cost
            breed.is_unlocked = True
            self.parent.save_game()

            QMessageBox.information(
                self,
                "Unlock Successful",
                f"{animal_type.label} has been unlocked!\nYou can now purchase and upgrade this animal."
            )

            # 表示を更新
            self.update_display()
        else:
            QMessageBox.warning(
                self,
                "Cannot Unlock",
                f"Not enough money!\nRequired: {cost} coins"
            )

    def upgrade_breed(self, animal_type):
        breed = self.parent.breeds[animal_type]
        cost = breed.get_upgrade_cost()

        if breed.level >= breed.max_level:
            QMessageBox.information(
                self,
                "Maximum Level",
                "This breed is already at maximum level!"
            )
            return

        if self.parent.money >= cost:
            self.parent.money -= cost
            breed.level += 1
            self.parent.save_game()

            QMessageBox.information(
                self,
                "Upgrade Successful",
                f"{animal_type.label} breed has been upgraded to level {breed.level}!\n"
                f"New production chance: {breed.get_production_chance() * 100:.1f}%"
            )

            # 表示を更新
            self.update_display()
        else:
            QMessageBox.warning(
                self,
                "Cannot Upgrade",
                f"Not enough money!\nRequired: {cost} coins"
            )