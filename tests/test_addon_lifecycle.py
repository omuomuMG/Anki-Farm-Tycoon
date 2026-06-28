import importlib.util
import sys
import types
import unittest
from unittest.mock import patch

from tests._bootstrap import ROOT


class Signal:
    def __init__(self):
        self.callbacks = []

    def connect(self, callback):
        self.callbacks.append(callback)


class HookList(list):
    pass


class FakeGameWidget:
    instances = []

    def __init__(self, _parent=None):
        self.visible = False
        self.delete_on_close = None
        self.destroyed = Signal()
        self.__class__.instances.append(self)

    def unregister_reviewer_hook(self):
        pass

    def setWindowFlags(self, _flags):
        pass

    def setAttribute(self, _attribute, value):
        self.delete_on_close = value

    def sizeHint(self):
        return (800, 600)

    def resize(self, _size):
        pass

    def setVisible(self, visible):
        self.visible = visible

    def isVisible(self):
        return self.visible

    def hide(self):
        self.visible = False

    def deleteLater(self):
        pass

    def raise_(self):
        pass

    def activateWindow(self):
        pass


class AddonLifecycleTests(unittest.TestCase):
    def load_addon(self, settings):
        class QAction:
            def __init__(self, *_args):
                self.triggered = Signal()
                self.checked = False

            def setCheckable(self, _checkable):
                pass

            def setChecked(self, checked):
                self.checked = checked

        class QTimer:
            @staticmethod
            def singleShot(_delay, callback):
                callback()

        class Qt:
            class WindowType:
                Widget = 1
                Window = 2

            class WidgetAttribute:
                WA_DeleteOnClose = 3

            class DockWidgetArea:
                LeftDockWidgetArea = 1
                RightDockWidgetArea = 2
                TopDockWidgetArea = 4
                BottomDockWidgetArea = 8

        class QDockWidget:
            def __init__(self, *_args):
                self._widget = None
                self.visible = False
                self.destroyed = Signal()
                self.topLevelChanged = Signal()
                self.visibilityChanged = Signal()

            def setWidget(self, widget):
                self._widget = widget

            def widget(self):
                return self._widget

            def setAllowedAreas(self, _areas):
                pass

            def setVisible(self, visible):
                self.visible = visible

            def isVisible(self):
                return self.visible

            def isFloating(self):
                return False

            def hide(self):
                self.visible = False

            def deleteLater(self):
                pass

        hooks = types.SimpleNamespace(
            sync_will_start=HookList(),
            main_window_did_init=HookList(),
        )
        menu = types.SimpleNamespace(addAction=lambda _action: None)
        mw = types.SimpleNamespace(
            form=types.SimpleNamespace(menuTools=menu),
            addDockWidget=lambda *_args: None,
        )

        class SaveManager:
            @classmethod
            def load_settings(cls):
                return dict(settings)

        package_name = "anki_farm_tycoon_lifecycle_target"
        aqt = types.ModuleType("aqt")
        aqt.mw = mw
        aqt.gui_hooks = hooks
        qt = types.ModuleType("aqt.qt")
        qt.QAction = QAction
        qt.QTimer = QTimer
        qt.QDockWidget = QDockWidget
        qt.Qt = Qt
        aqt.qt = qt

        gui = types.ModuleType(f"{package_name}.gui")
        gui.__path__ = []
        utils = types.ModuleType(f"{package_name}.utils")
        utils.__path__ = []
        sync_hook = types.ModuleType(f"{package_name}.gui.sync_hook")
        sync_hook.on_sync_complete = lambda: None
        game_widget = types.ModuleType(f"{package_name}.gui.game_widget")
        game_widget.GameWidget = FakeGameWidget
        save_manager = types.ModuleType(f"{package_name}.utils.save_manager")
        save_manager.SaveManager = SaveManager

        spec = importlib.util.spec_from_file_location(
            package_name,
            ROOT / "__init__.py",
            submodule_search_locations=[str(ROOT)],
        )
        module = importlib.util.module_from_spec(spec)
        stubs = {
            package_name: module,
            "aqt": aqt,
            "aqt.qt": qt,
            f"{package_name}.gui": gui,
            f"{package_name}.utils": utils,
            f"{package_name}.gui.sync_hook": sync_hook,
            f"{package_name}.gui.game_widget": game_widget,
            f"{package_name}.utils.save_manager": save_manager,
        }
        with patch.dict(sys.modules, stubs):
            spec.loader.exec_module(module)

        return module, mw

    def setUp(self):
        FakeGameWidget.instances.clear()

    def test_auto_start_off_still_creates_hidden_game_engine(self):
        addon, mw = self.load_addon({"auto_start": False, "dock_widget": False})
        addon.on_anki_startup()

        self.assertIs(mw.anki_farm_widget, FakeGameWidget.instances[-1])
        self.assertFalse(mw.anki_farm_widget.isVisible())
        self.assertFalse(mw.anki_farm_widget.delete_on_close)

    def test_hidden_window_can_be_toggled_without_recreating_engine(self):
        addon, mw = self.load_addon({"auto_start": False, "dock_widget": False})
        addon.on_anki_startup()
        engine = mw.anki_farm_widget

        addon.toggle_game_window()
        self.assertTrue(engine.isVisible())
        addon.toggle_game_window()
        self.assertFalse(engine.isVisible())
        self.assertIs(mw.anki_farm_widget, engine)
        self.assertEqual(len(FakeGameWidget.instances), 1)


if __name__ == "__main__":
    unittest.main()
