import json
import os

from src import app_info
from src import custom_json
from src import settings
from src import system
from src.qt import *

PATH_SEPARATOR = " | "

state = QSettings(
    QSettings.Scope.UserScope,
    app_info.author,
    app_info.name,
)

pre_keys = set(globals().keys())

last_selected_dict = settings.dict_default
last_selected_dir = system.documents_dir
texts = dict()
windows = dict()

post_keys = set(globals().keys())
keys = post_keys - pre_keys - {"pre_keys"}
defaults = {key: globals()[key] for key in keys}


def clean():
    global texts, windows
    for key, value in texts.copy().items():
        if not os.path.exists(key):
            del texts[key]
    for key, value in windows.copy().items():
        for path in key.split(PATH_SEPARATOR):
            if not os.path.exists(path):
                del windows[key]
                break
    texts = dict(
        sorted(texts.items(), key=lambda x: x[1][0], reverse=True)[
            : settings.app_num_recents
        ]
    )
    windows = dict(
        sorted(windows.items(), key=lambda x: x[1][0], reverse=True)[
            : settings.app_num_recents
        ]
    )
    save()


def load():
    for key in keys:
        value = state.value(f"{key}")
        if value is None:
            continue
        value = json.loads(value, cls=custom_json.Decoder)
        globals()[key] = value


def reset():
    state.clear()
    for key in keys:
        globals()[key] = defaults[key]


def save():
    for key in keys:
        value = json.dumps(globals()[key], cls=custom_json.Encoder)
        state.setValue(f"{key}", value)


load()
clean()
