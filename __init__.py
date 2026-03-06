from aqt.qt import *
from aqt import mw, gui_hooks
from .gui.sync_hook import on_sync_complete
from .gui.game_widget import GameWidget

farm_dock = None
game_widget = None
menu_action = None


def toggle_farm_widget(checked=False):
    """Toggle the display/hide of the farm panel"""
    global farm_dock, game_widget, menu_action

    if farm_dock is None:
        game_widget = GameWidget()

        farm_dock = QDockWidget("Anki Farm Tycoon", mw)
        farm_dock.setWidget(game_widget)

        # Only left and right docking are allowed; bottom docking is prohibited.
        farm_dock.setAllowedAreas(
            Qt.DockWidgetArea.RightDockWidgetArea |
            Qt.DockWidgetArea.LeftDockWidgetArea
            # 移除 BottomDockWidgetArea
        )

        # Docked on the right by default
        mw.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, farm_dock)

        # Set a reasonable width
        farm_dock.setMinimumWidth(350)
        farm_dock.setMaximumWidth(500)

        if menu_action:
            menu_action.setChecked(True)
    else:
        if farm_dock.isVisible():
            farm_dock.hide()
            if menu_action:
                menu_action.setChecked(False)
        else:
            farm_dock.show()
            farm_dock.raise_()
            if menu_action:
                menu_action.setChecked(True)


def setup_ui():
    global menu_action
    menu_action = QAction("Anki Farm Tycoon", mw)
    menu_action.triggered.connect(toggle_farm_widget)
    menu_action.setCheckable(True)
    mw.form.menuTools.addAction(menu_action)
    gui_hooks.sync_will_start.append(on_sync_complete)


setup_ui()

# ========== Auto start ==========
def auto_start_farm():
    """Anki 加载完成后自动打开农场"""
    toggle_farm_widget()

gui_hooks.main_window_did_init.append(auto_start_farm)
