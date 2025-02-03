from aqt.qt import *

from aqt import mw
from .gui.game_widget import GameWidget

def game_window():
    mw.myWidget = widget = GameWidget()
    widget.show()

action = QAction("Anki Farm Tycoon", mw)
action.triggered.connect(game_window)

mw.form.menuTools.addAction(action)
