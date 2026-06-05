from PyQt6.QtWidgets import (
    QCheckBox,
    QDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
)

from ..utils.save_manager import SaveManager


class SettingsWindow(QDialog):
    def __init__(self, game_widget, parent=None):
        super().__init__(parent)
        self.game_widget = game_widget
        self.original_settings = SaveManager.load_settings()
        self.settings_changed = False
        self.setup_ui()

    def setup_ui(self):
        self.setWindowTitle("Settings")
        self.setMinimumWidth(320)

        layout = QVBoxLayout()
        layout.setSpacing(12)
        layout.setContentsMargins(18, 18, 18, 18)

        title = QLabel("Anki Farm Tycoon")
        title.setStyleSheet("font-size: 18px; font-weight: bold;")
        layout.addWidget(title)

        self.auto_start_checkbox = QCheckBox("Auto Start")
        self.auto_start_checkbox.setChecked(self.original_settings["auto_start"])
        layout.addWidget(self.auto_start_checkbox)

        self.dock_widget_checkbox = QCheckBox("Dock Widget")
        self.dock_widget_checkbox.setChecked(self.original_settings["dock_widget"])
        layout.addWidget(self.dock_widget_checkbox)

        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setFrameShadow(QFrame.Shadow.Sunken)
        layout.addWidget(separator)

        reset_button = QPushButton("Reset Game")
        reset_button.clicked.connect(self.reset_game)
        reset_button.setStyleSheet("""
            QPushButton {
                background-color: #8e3b23;
                color: white;
                border: none;
                padding: 7px;
                border-radius: 3px;
            }
            QPushButton:hover {
                background-color: #b74d2e;
            }
        """)
        layout.addWidget(reset_button)

        button_layout = QHBoxLayout()
        button_layout.addStretch()

        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(cancel_button)

        save_button = QPushButton("Save")
        save_button.clicked.connect(self.save_settings)
        save_button.setDefault(True)
        button_layout.addWidget(save_button)

        layout.addLayout(button_layout)
        self.setLayout(layout)

    def current_settings(self):
        return {
            "auto_start": self.auto_start_checkbox.isChecked(),
            "dock_widget": self.dock_widget_checkbox.isChecked(),
        }

    def save_settings(self):
        settings = self.current_settings()
        self.settings_changed = settings != self.original_settings
        SaveManager.save_settings(settings)
        self.accept()

    def reset_game(self):
        self.game_widget.reset_game()
