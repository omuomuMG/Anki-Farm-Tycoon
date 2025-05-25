from aqt.qt import *
from aqt import mw, gui_hooks
from .gui.sync_hook import on_sync_complete
from .gui.game_widget import GameWidget

def game_window():
    mw.myWidget = widget = GameWidget()
    widget.show()

action = QAction("Anki Farm Tycoon", mw)
action.triggered.connect(game_window)

mw.form.menuTools.addAction(action)
gui_hooks.sync_will_start.append(on_sync_complete)