import os

from src import app_info
from src import settings
from src import state
from src import window
from src.qt import *

widget_class_to_default_height = dict()


def calculate_default_height(widget_class):
    try:
        return widget_class_to_default_height[widget_class.__name__]
    except KeyError:
        pass
    window_ = window.Window()
    window_.setAttribute(Qt.WA_DontShowOnScreen)
    window_.setLayout(QVBoxLayout())
    widget = widget_class(window_)
    window_.layout().addWidget(widget)
    window_.show()
    height = widget.size().height()
    window_.close()
    window_.deleteLater()
    widget_class_to_default_height[widget_class.__name__] = height
    return height


def delete_file(path):
    try:
        os.remove(path)
    except FileNotFoundError:
        pass


def get_dict_list():
    dict_list = []
    try:
        for file_name in os.listdir(settings.dict_dir):
            dict_name, extension = os.path.splitext(file_name)
            if extension == app_info.db_ext:
                dict_list.append(dict_name)
    except FileNotFoundError:
        pass
    return sorted(dict_list)


def get_open_file_name(parent, caption):
    path = QFileDialog.getOpenFileName(
        parent,
        caption=caption,
        dir=settings.app_default_files_dir or state.last_selected_dir,
    )[0]
    if path:
        path = os.path.normpath(path)
        state.last_selected_dir = os.path.dirname(path)
    return path


def get_save_file_name(parent, caption, name):
    path = QFileDialog.getSaveFileName(
        parent,
        caption=caption,
        dir=os.path.join(
            settings.app_default_files_dir or state.last_selected_dir,
            name,
        ),
    )[0]
    if path:
        path = os.path.normpath(path)
        state.last_selected_dir = os.path.dirname(path)
    return path


def run_after_current_event(fn):
    def try_fn():
        try:
            fn()
        except RuntimeError:
            pass

    QTimer.singleShot(0, try_fn)


def sign(x):
    return (x > 0) - (x < 0)


def prev_widget(widget):
    layout = widget.parent().layout()
    prev_index = layout.indexOf(widget) - 1
    if prev_index == -1:
        return None
    else:
        return layout.itemAt(prev_index).widget()


def next_widget(widget):
    layout = widget.parent().layout()
    next_index = layout.indexOf(widget) + 1
    if next_index == layout.count():
        return None
    else:
        return layout.itemAt(next_index).widget()


def top_sub_widget(widget):
    return widget.layout().itemAt(0).widget()


def bottom_sub_widget(widget):
    layout = widget.layout()
    return layout.itemAt(layout.count() - 1).widget()
