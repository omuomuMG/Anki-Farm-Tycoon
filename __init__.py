from aqt.qt import *
from aqt import mw, gui_hooks
from .gui.sync_hook import on_sync_complete
from .gui.game_widget import GameWidget


def create_game_dock_widget():
    """Create game widget as a dock widget attached to Anki main window"""
    # Create the game widget
    game_widget = GameWidget()

    # Remove window flags to make it a widget instead of dialog
    game_widget.setWindowFlags(Qt.WindowType.Widget)

    # Create dock widget
    dock = QDockWidget("Anki Farm Tycoon", mw)
    dock.setWidget(game_widget)
    dock.setAllowedAreas(
        Qt.DockWidgetArea.LeftDockWidgetArea |
        Qt.DockWidgetArea.RightDockWidgetArea |
        Qt.DockWidgetArea.TopDockWidgetArea |
        Qt.DockWidgetArea.BottomDockWidgetArea
    )

    # Add dock to main window (right side by default)
    mw.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, dock)

    # Store references for later access
    mw.anki_farm_dock = dock
    mw.anki_farm_widget = game_widget

    return dock


# Create menu item to toggle visibility
def toggle_game_window():
    """Toggle game dock widget visibility"""
    if hasattr(mw, 'anki_farm_dock'):
        dock = mw.anki_farm_dock
        dock.setVisible(not dock.isVisible())
    else:
        create_game_dock_widget()


# Add menu item
action = QAction("Anki Farm Tycoon", mw)
action.triggered.connect(toggle_game_window)
action.setCheckable(True)
action.setChecked(True)
mw.form.menuTools.addAction(action)

# Sync hook
gui_hooks.sync_will_start.append(on_sync_complete)


# ===== Auto-open game dock when Anki starts =====
def on_anki_startup():
    """Automatically create and show game dock after Anki fully initializes"""
    QTimer.singleShot(500, create_game_dock_widget)


gui_hooks.main_window_did_init.append(on_anki_startup)
