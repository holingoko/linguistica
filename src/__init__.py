import sys

from src.qt import *


class Application(QApplication):
    ignore_shortcuts = False
    shortcut_to_action_fn = dict()
    mouse_event_widget = None

    def eventFilter(self, watched, event):
        if self.mouse_event_widget is not None and isinstance(
            watched,
            QWindow,
        ):
            event_type = event.type()
            if event_type == QEvent.Type.MouseMove:
                self.mouse_event_widget.global_mouse_move_event(event)
            elif event_type == QEvent.Type.MouseButtonPress:
                self.mouse_event_widget.global_mouse_press_event(event)
            elif event_type == QEvent.Type.MouseButtonDblClick:
                self.mouse_event_widget.global_mouse_double_click_event(event)
        if getattr(watched, "is_window", False):
            event_type = event.type()
            if (
                event_type == QEvent.Type.ShortcutOverride
                and not self.ignore_shortcuts
                and event.text()
            ):
                key_sequence = (
                    QKeySequence(event.keyCombination())
                    .toString()
                    .lower()
                    .replace("num+", "")
                )
                try:
                    action_fns = self.shortcut_to_action_fn[key_sequence]
                    for action_fn in action_fns:
                        action_fn()
                    event.accept()
                    return True
                except KeyError:
                    pass
            elif event_type == QEvent.Type.WindowActivate:
                watched.on_activate()
            elif event_type == QEvent.Type.ThemeChange:
                reinit_app()
        return False


app = Application(sys.argv)
app.setEffectEnabled(Qt.UIEffect.UI_AnimateMenu, False)
app.setEffectEnabled(Qt.UIEffect.UI_FadeMenu, False)
app.setEffectEnabled(Qt.UIEffect.UI_AnimateCombo, False)
app.installEventFilter(app)


def update_language():
    for widget in app.allWidgets():
        try:
            widget.on_update_language()
        except (AttributeError, RuntimeError):
            pass


def update_settings():
    for widget in app.allWidgets():
        try:
            widget.on_update_settings()
        except (AttributeError, RuntimeError):
            pass


def update_theme():
    for widget in app.allWidgets():
        try:
            widget.on_update_theme()
        except (AttributeError, RuntimeError):
            pass


def pre_update():
    from src import text_edit

    for widget in app.allWidgets():
        if isinstance(widget, text_edit.TextEdit):
            widget.pre_on_update()


def post_update():
    from src import text_edit

    for widget in app.allWidgets():
        if isinstance(widget, text_edit.TextEdit):
            widget.post_on_update()


def reinit_app():
    from src import actions
    from src import language
    from src import settings_window
    from src import theme
    from src import utils

    try:
        settings_window.SettingsWindow.instance[0].close()
    except AttributeError:
        pass
    utils.widget_class_to_default_height.clear()
    actions.update_shortcuts()
    language.load_language()
    theme.load_theme()
    pre_update()
    update_language()
    update_settings()
    update_theme()
    post_update()
