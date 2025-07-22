import os

from src import messages
from src import settings
from src.qt import *

repo_dir = os.path.dirname(os.path.dirname(__file__))
themes_dir = os.path.join(repo_dir, "resources", "themes")
os.makedirs(settings.app_user_added_themes_dir, exist_ok=True)


def get_available_themes():
    themes = []
    for file_name in os.listdir(themes_dir):
        theme, ext = os.path.splitext(file_name)
        if ext.lower() == ".qss":
            themes.append(theme)
    for file_name in os.listdir(settings.app_user_added_themes_dir):
        theme, ext = os.path.splitext(file_name)
        if ext.lower() == ".qss":
            themes.append(theme)
    return sorted(themes)


style_sheet = None


def load_theme():
    global style_sheet
    try:
        with open(
            os.path.join(themes_dir, f"{settings.app_theme}.qss"),
            mode="r",
            encoding="utf-8",
        ) as file:
            style_sheet = file.read()
    except FileNotFoundError:
        try:
            with open(
                os.path.join(
                    settings.app_user_added_themes_dir,
                    f"{settings.app_theme}.qss",
                ),
                mode="r",
                encoding="utf-8",
            ) as file:
                style_sheet = file.read()
        except FileNotFoundError:
            missing_theme = settings.app_theme
            settings.app_theme = settings.defaults["app_theme"]
            settings.save()
            load_theme()

            def ensure_messages_module_loaded():
                error_message = messages.MissingThemeErrorMessage(
                    missing_theme
                )
                error_message.show()
                error_message.move_to_center()

            QTimer.singleShot(0, ensure_messages_module_loaded)


load_theme()
