from aqt.qt import *
from aqt import mw, gui_hooks
from .gui.sync_hook import on_sync_complete
from .gui.game_widget import GameWidget

# Configuration: Auto-start on launch (can be loaded from config file)
AUTO_START_ON_LAUNCH = True  # Set to False to disable auto-start


def game_window():
    mw.myWidget = widget = GameWidget()
    widget.show()


# Create menu item
action = QAction("Anki Farm Tycoon", mw)
action.triggered.connect(game_window)
mw.form.menuTools.addAction(action)

# Sync hook
gui_hooks.sync_will_start.append(on_sync_complete)

# Auto-start (if enabled)
if AUTO_START_ON_LAUNCH:
    def on_anki_startup():
        """Automatically open game window after Anki fully initializes"""
        QTimer.singleShot(500, game_window)  # Delay to ensure UI readiness


    gui_hooks.main_window_did_init.append(on_anki_startup)
