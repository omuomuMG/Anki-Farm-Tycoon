from aqt import mw, gui_hooks
from aqt.qt import *
from aqt.utils import showInfo

from aqt import mw
from .gui.game_widget import GameWidget

def game_window():
    mw.myWidget = widget = GameWidget()
    widget.show()

action = QAction("Ranch launch", mw)
action.triggered.connect(game_window)


mw.form.menuTools.addAction(action)
