"""Load add-on modules without requiring an Anki installation."""

from __future__ import annotations

import importlib
import sys
import types
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PACKAGE_NAME = "anki_farm_tycoon_test_target"


class _ProfileManager:
    def __init__(self):
        self.profile_folder = str(ROOT)

    def profileFolder(self):
        return self.profile_folder


profile_manager = _ProfileManager()


def _install_target_package():
    if PACKAGE_NAME not in sys.modules:
        package = types.ModuleType(PACKAGE_NAME)
        package.__path__ = [str(ROOT)]
        sys.modules[PACKAGE_NAME] = package


def _install_aqt_stub():
    if "aqt" not in sys.modules:
        aqt = types.ModuleType("aqt")
        aqt.mw = types.SimpleNamespace(pm=profile_manager)
        sys.modules["aqt"] = aqt


def _install_pyqt_stub():
    if "PyQt6" in sys.modules:
        return

    class QPixmap:
        def __init__(self, path=None):
            self.path = path

        def fill(self, _color):
            pass

        def rect(self):
            return None

    class QPainter:
        def __init__(self, _pixmap):
            pass

        def setFont(self, _font):
            pass

        def drawText(self, *_args):
            pass

        def end(self):
            pass

    class QFont:
        def setPointSize(self, _size):
            pass

    class Qt:
        class GlobalColor:
            transparent = object()

        class AlignmentFlag:
            AlignCenter = object()

    pyqt = types.ModuleType("PyQt6")
    qt_core = types.ModuleType("PyQt6.QtCore")
    qt_gui = types.ModuleType("PyQt6.QtGui")
    qt_core.Qt = Qt
    qt_gui.QFont = QFont
    qt_gui.QPainter = QPainter
    qt_gui.QPixmap = QPixmap
    sys.modules["PyQt6"] = pyqt
    sys.modules["PyQt6.QtCore"] = qt_core
    sys.modules["PyQt6.QtGui"] = qt_gui


_install_target_package()
_install_aqt_stub()
_install_pyqt_stub()


def import_target(module_name: str):
    return importlib.import_module(f"{PACKAGE_NAME}.{module_name}")


def set_profile_folder(path: Path):
    profile_manager.profile_folder = str(path)
