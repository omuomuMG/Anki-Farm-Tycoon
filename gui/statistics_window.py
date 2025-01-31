from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton
from PyQt6.QtCore import Qt


class StatisticsWindow(QDialog):
    def __init__(self, global_stats, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Global Statistics")
        self.setMinimumWidth(300)

        layout = QVBoxLayout()


        title_style = "font-size: 16px; font-weight: bold; margin-bottom: 10px;"
        section_style = "font-size: 14px; font-weight: bold; color: #444;"
        stat_style = "font-size: 12px; margin-left: 10px;"


        title = QLabel("🏆 Global Statistics")
        title.setStyleSheet(title_style)
        layout.addWidget(title)


        records = QLabel("📊 Records")
        records.setStyleSheet(section_style)
        layout.addWidget(records)

        layout.addWidget(QLabel(f"Highest Money: {global_stats.highest_money} coins"))
        layout.addWidget(QLabel(f"Highest Day: {global_stats.highest_day}"))


        animals = QLabel("🐾 Animal Statistics")
        animals.setStyleSheet(section_style)
        layout.addWidget(animals)


        pig_stats = QLabel("🐷 Pig:")
        pig_stats.setStyleSheet(stat_style)
        layout.addWidget(pig_stats)
        layout.addWidget(QLabel(f"    Sold: {global_stats.total_animals_sold_by_type.get('PIG', 0)}"))
        layout.addWidget(QLabel(f"    Deaths: {global_stats.total_animals_died_by_type.get('PIG', 0)}"))


        chicken_stats = QLabel("🐔 Chicken:")
        chicken_stats.setStyleSheet(stat_style)
        layout.addWidget(chicken_stats)
        layout.addWidget(QLabel(f"    Sold: {global_stats.total_animals_sold_by_type.get('CHICKEN', 0)}"))
        layout.addWidget(QLabel(f"    Deaths: {global_stats.total_animals_died_by_type.get('CHICKEN', 0)}"))


        cow_stats = QLabel("🐮 Cow:")
        cow_stats.setStyleSheet(stat_style)
        layout.addWidget(cow_stats)
        layout.addWidget(QLabel(f"    Sold: {global_stats.total_animals_sold_by_type.get('COW', 0)}"))
        layout.addWidget(QLabel(f"    Deaths: {global_stats.total_animals_died_by_type.get('COW', 0)}"))


        totals = QLabel("📈 Totals")
        totals.setStyleSheet(section_style)
        layout.addWidget(totals)
        layout.addWidget(QLabel(f"Total Animals Sold: {global_stats.total_animals_sold}"))
        layout.addWidget(QLabel(f"Total Money Earned: {global_stats.total_money_earned} coins"))


        close_button = QPushButton("Close")
        close_button.clicked.connect(self.close)
        close_button.setStyleSheet("""
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
        layout.addWidget(close_button)

        self.setLayout(layout)