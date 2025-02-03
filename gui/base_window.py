from PyQt6.QtWidgets import QDialog


class BaseWindow(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.button_connections = {}
        self.setup_ui()

    def setup_ui(self):
        pass

    def register_button(self, button, handler):
        if button in self.button_connections:
            button.clicked.disconnect(self.button_connections[button])

        wrapper = lambda checked, h=handler: h()

        button.clicked.connect(wrapper)
        self.button_connections[button] = wrapper
