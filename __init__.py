from aqt.qt import *
from aqt import mw, gui_hooks
from .gui.sync_hook import on_sync_complete
from .gui.game_widget import GameWidget
from .utils.save_manager import SaveManager


def game_settings():
    return SaveManager.load_settings()


def set_game_action_checked(checked):
    if "action" in globals():
        action.setChecked(checked)


def current_game_is_visible():
    dock = getattr(mw, "anki_farm_dock", None)
    if dock is not None:
        return dock.isVisible()

    game_window = getattr(mw, "anki_farm_window", None)
    if game_window is not None:
        return game_window.isVisible()

    return False


def clear_dock_reference(dock, game_widget=None):
    if getattr(mw, "anki_farm_dock", None) is dock:
        delattr(mw, "anki_farm_dock")
        if not current_game_is_visible():
            set_game_action_checked(False)

    if game_widget is not None and getattr(mw, "anki_farm_widget", None) is game_widget:
        delattr(mw, "anki_farm_widget")


def clear_window_reference(game_window):
    if getattr(mw, "anki_farm_window", None) is game_window:
        delattr(mw, "anki_farm_window")
        if not current_game_is_visible():
            set_game_action_checked(False)

    if getattr(mw, "anki_farm_widget", None) is game_window:
        delattr(mw, "anki_farm_widget")


def delete_game_dock():
    dock = getattr(mw, "anki_farm_dock", None)
    if dock is None:
        return

    game_widget = dock.widget()
    clear_dock_reference(dock, game_widget)
    if game_widget is not None and hasattr(game_widget, "unregister_reviewer_hook"):
        game_widget.unregister_reviewer_hook()

    dock.hide()
    dock.deleteLater()


def delete_game_window():
    game_window = getattr(mw, "anki_farm_window", None)
    if game_window is None:
        return

    clear_window_reference(game_window)
    if hasattr(game_window, "unregister_reviewer_hook"):
        game_window.unregister_reviewer_hook()

    game_window.hide()
    game_window.deleteLater()


def resize_floating_game_dock(dock):
    """Resize a floating dock to the game's natural window size."""
    if not dock.isFloating():
        return

    game_widget = dock.widget()
    if game_widget is None:
        return

    game_widget.updateGeometry()
    game_widget.resize_floating_container_to_game_size()
    game_widget.update()


def schedule_floating_game_dock_resize(dock):
    """Wait for Qt to finish undocking before resizing the floating window."""
    QTimer.singleShot(0, lambda: resize_floating_game_dock(dock))
    QTimer.singleShot(100, lambda: resize_floating_game_dock(dock))


def create_game_dock_widget():
    """Create game widget as a dock widget attached to Anki main window"""
    delete_game_window()

    if hasattr(mw, 'anki_farm_dock'):
        dock = mw.anki_farm_dock
        dock.setVisible(True)
        set_game_action_checked(True)
        if dock.isFloating():
            schedule_floating_game_dock_resize(dock)
        return dock

    # Create the game widget
    game_widget = GameWidget()

    # Remove window flags to make it a widget instead of dialog
    game_widget.setWindowFlags(Qt.WindowType.Widget)

    # Create dock widget
    dock = QDockWidget("Anki Farm Tycoon", mw)
    dock.setWidget(game_widget)
    dock.topLevelChanged.connect(
        lambda floating: schedule_floating_game_dock_resize(dock) if floating else None
    )
    dock.visibilityChanged.connect(set_game_action_checked)
    dock.destroyed.connect(lambda: clear_dock_reference(dock, game_widget))
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
    set_game_action_checked(True)

    return dock


def create_game_window():
    settings = game_settings()
    if settings["dock_widget"]:
        return create_game_dock_widget()
    return create_standalone_game_window()


def create_standalone_game_window():
    """Create game widget as an independent window."""
    delete_game_dock()

    if hasattr(mw, "anki_farm_window"):
        game_window = mw.anki_farm_window
        game_window.show()
        game_window.raise_()
        game_window.activateWindow()
        set_game_action_checked(True)
        return game_window

    game_window = GameWidget(mw)
    game_window.setWindowFlags(Qt.WindowType.Window)
    game_window.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose, True)
    game_window.resize(game_window.sizeHint())
    game_window.destroyed.connect(lambda: clear_window_reference(game_window))
    game_window.show()

    mw.anki_farm_window = game_window
    mw.anki_farm_widget = game_window
    set_game_action_checked(True)

    return game_window


def apply_game_window_settings():
    """Apply display-mode settings to the currently open game window."""
    settings = game_settings()
    was_visible = current_game_is_visible()

    if settings["dock_widget"]:
        if hasattr(mw, "anki_farm_window"):
            delete_game_window()
            if was_visible:
                create_game_dock_widget()
        elif hasattr(mw, "anki_farm_dock"):
            set_game_action_checked(mw.anki_farm_dock.isVisible())
    else:
        if hasattr(mw, "anki_farm_dock"):
            delete_game_dock()
            if was_visible:
                create_standalone_game_window()
        elif hasattr(mw, "anki_farm_window"):
            set_game_action_checked(mw.anki_farm_window.isVisible())


# Create menu item to toggle visibility
def toggle_game_window():
    """Toggle game dock widget visibility"""
    settings = game_settings()

    if settings["dock_widget"]:
        if hasattr(mw, "anki_farm_window"):
            delete_game_window()

        if not hasattr(mw, "anki_farm_dock"):
            create_game_dock_widget()
            return

        dock = mw.anki_farm_dock
        dock.setVisible(not dock.isVisible())
        set_game_action_checked(dock.isVisible())
    else:
        if hasattr(mw, "anki_farm_dock"):
            delete_game_dock()

        if not hasattr(mw, "anki_farm_window"):
            create_standalone_game_window()
            return

        game_window = mw.anki_farm_window
        game_window.setVisible(not game_window.isVisible())
        if game_window.isVisible():
            game_window.raise_()
            game_window.activateWindow()
        set_game_action_checked(game_window.isVisible())


# Add menu item
action = QAction("Anki Farm Tycoon", mw)
action.triggered.connect(toggle_game_window)
action.setCheckable(True)
action.setChecked(False)
mw.form.menuTools.addAction(action)
mw.anki_farm_apply_window_settings = apply_game_window_settings

# Sync hook
gui_hooks.sync_will_start.append(on_sync_complete)


# ===== Auto-open game dock when Anki starts =====
def on_anki_startup():
    """Automatically create and show game dock after Anki fully initializes"""
    if game_settings()["auto_start"]:
        QTimer.singleShot(500, create_game_window)


gui_hooks.main_window_did_init.append(on_anki_startup)
