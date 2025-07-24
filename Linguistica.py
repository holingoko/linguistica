#!!!
from src import system

if not system.running_built_app:
    from tools import checkpoint  #!!!

    checkpoint.make_checkpoint()

from src import settings
from src.log import log

from src import state

settings.reset()  #!!!
state.reset()  #!!!

settings.message_class_to_choice = {"UnsavedFilesWarningMessage": 0}  # !!!
# settings.dict_popup_show_on = settings.DictPopupShowOn.CLICK
# settings.dict_popup_on_shortcut_move_by = settings.DictPopupMoveBy.CHAR
# settings.app_theme = "System"
# settings.app_theme = "Light"
settings.app_enable_logging = True
# settings.text_editor_set_focus_on_hover = True
# settings.text_editor_wrap_long_lines = False
# settings.text_editor_scroll_trough_behavior_on_press = (
#     settings.ScrollTroughBehaviorOnPress.CHANGE_PAGE
# )
# settings.text_editor_behavior_on_new_text_file = (
#     settings.OpenFileBehavior.REPLACE
# )
# settings.text_editor_behavior_on_open_file = settings.OpenFileBehavior.REPLACE
# settings.text_editor_behavior_on_drag_and_drop_file = (
#     settings.OpenFileBehavior.REPLACE
# )
# settings.text_editor_show_file_name_full_path = True


def run():
    from src import app
    from src import dict_window
    from src import main_window
    from src import state
    from src import window

    if settings.app_startup_window == settings.StartupWindow.NEW_TEXT_EDITOR:
        main_window.MainWindow().show()
    elif (
        settings.app_startup_window
        == settings.StartupWindow.MOST_RECENTLY_CLOSED
    ):
        prev_close_time = None
        for close_time, window_state in sorted(
            state.windows.values(),
            reverse=True,
        ):
            if (
                prev_close_time is None
                or prev_close_time - close_time
                < settings.app_close_time_tolerance
            ):
                main_window.MainWindow(window_state).show()
                prev_close_time = close_time
        if not window.Window.windows:
            main_window.MainWindow().show()
    elif (
        settings.app_startup_window == settings.StartupWindow.DICTIONARY_WINDOW
    ):
        dict_window.DictWindow().show()

    # window.hide()

    from src import examples

    # examples.create_entry_japanese()
    # examples.create_template_latin()

    # settings.dict_default = "English Example"
    #
    # from src import dict_window
    #
    # dict_window_ = dict_window.DictWindow()
    #
    # dict_window_.show()
    from src import actions

    # actions.Settings.on_action()
    # actions.CreateDictionary.on_action()
    app.exec()


if settings.app_enable_logging:
    log(run)
else:
    run()

#!!!
from src import system

if not system.running_built_app:
    import shutil

    shutil.rmtree(settings.app_logging_dir, ignore_errors=True)  # !!!
    shutil.rmtree(settings.dict_dir, ignore_errors=True)  # !!!
