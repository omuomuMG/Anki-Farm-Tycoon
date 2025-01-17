from aqt import mw, gui_hooks
from aqt.qt import *
from aqt.utils import showInfo

from .utils import game_window

action = QAction("Ranch launch", mw)
action.triggered.connect(game_window)





# Ankiのツールメニューにアクションを追加
mw.form.menuTools.addAction(action)
