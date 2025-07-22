import math
import os
import time

from src import app
from src import app_info
from src import combo_box
from src import dict_database
from src import dict_popup
from src import label
from src import menus
from src import messages
from src import settings
from src import state
from src import text_edit
from src import utils
from src.language import tr
from src.qt import *


class TextEditor(QWidget):
    def __init__(self, main_window, state_):
        super().__init__()
        self.main_window = main_window
        self.context_menu = menus.TextEditorContextMenu(main_window)
        self.top = QWidget()
        self.top.setLayout(QHBoxLayout())
        self.widget = QWidget()
        self.label = label.AutoTrimmedFileNameLabel()
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.dummy_label = QLabel()
        self.dict_combo_box = combo_box.DictComboBox(
            self.on_dict_combo_hide_popup
        )
        self.dict_combo_resize_event = self.dict_combo_box.resizeEvent
        self.dict_combo_box.resizeEvent = self.on_dict_combo_resize_event
        self.text_edit = text_edit.TextEdit(main_window)
        self.top.layout().addWidget(self.widget, 0)
        self.top.layout().addWidget(self.dummy_label, 1)
        self.top.layout().addWidget(self.dict_combo_box, 0)
        self.setLayout(QVBoxLayout())
        self.layout().addWidget(self.top)
        self.layout().addWidget(self.text_edit)
        self.layout().setSpacing(0)
        self.label.setParent(self.top)
        self.label.show()
        self.label.raise_()
        self.prev_unsaved = False
        self.saved_text = ""
        self.prev_dict_path = None
        self.text_most_recently_modified_time = math.inf
        self.text_edit.text_edit.on_focus_in = self.on_focus_in
        self.text_edit.text_edit.on_focus_out = self.on_focus_out
        self.text_edit.text_edit.on_text_modified = self.on_text_modified
        path, locked, dictionary, selection, scroll_value = state_
        if path:
            self.path = os.path.normpath(path)
            self.on_open()
        else:
            self.path = self.temp_file_name()
        self.locked = locked
        self.dictionary = dictionary
        self.text_edit.set_selection(selection)
        self.text_edit.set_scroll_value(scroll_value)
        self.update_label_text(self.unsaved)
        utils.run_after_current_event(self.setFocus)
        self.setAcceptDrops(True)
        self.on_update_settings()

    @property
    def dpi(self):
        screen = self.screen()
        return screen.physicalDotsPerInch() / (
            screen.devicePixelRatio()
            if settings.app_scale_sizes_by_device_pixel_ratio
            else 1.0
        )

    @property
    def file_name(self):
        return self.format_file_name(self.path)

    @property
    def unsaved(self):
        return self.saved_text != self.text_edit.text_edit.toPlainText()

    @property
    def locked(self):
        return self.text_edit.text_edit.isReadOnly()

    @locked.setter
    def locked(self, status):
        self.text_edit.text_edit.setReadOnly(status)

    @property
    def dictionary(self):
        return self.dict_combo_box.currentText()

    @dictionary.setter
    def dictionary(self, text):
        self.dict_combo_box.set_name(text)

    @property
    def state(self):
        return (
            self.path,
            self.locked,
            self.dictionary,
            self.text_edit.selection(),
            self.text_edit.scroll_value(),
        )

    @staticmethod
    def default_state(path=""):
        return (
            path,
            False,
            settings.dict_default or state.last_selected_dict,
            (0, 0, 0),
            0,
        )

    @staticmethod
    def format_file_name(path):
        if settings.text_editor_show_file_name_full_path:
            return path
        elif settings.text_editor_show_file_name_ext:
            return os.path.basename(path)
        else:
            return os.path.splitext(os.path.basename(path))[0]

    def contextMenuEvent(self, event):
        self.context_menu.move(event.globalPos())
        self.context_menu.show()

    def dragEnterEvent(self, event):
        event.accept()

    def dropEvent(self, event):
        for url in event.mimeData().urls():
            path = url.path()[1:]
            if os.path.exists(path):
                self.main_window.handle_dropped_file(
                    os.path.normpath(path),
                    self,
                )

    def enterEvent(self, event):
        if settings.text_editor_set_focus_on_hover:
            self.setFocus()

    def mousePressEvent(self, event):
        self.text_edit.text_edit.setFocus()
        super().mousePressEvent(event)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.widget.setFixedWidth(self.dict_combo_box.width())
        self.label.setGeometry(self.dummy_label.geometry())

    def setFocus(self):
        self.text_edit.text_edit.setFocus()

    def set_scrollbar_value(self, value):
        self.text_edit.scrollbar_signaler.set_value(value)

    def get_scrollbar_value(self):
        return self.text_edit.scrollbar_signaler.value()

    def set_text(self, text):
        self.text_edit.text_edit.setPlainText(text)
        self.text_edit.on_update_settings()

    def file_names_in_use(self):
        return {
            widget.file_name
            for widget in app.allWidgets()
            if isinstance(widget, TextEditor) and not widget is self
        }

    def temp_file_name(self):
        try:
            os.makedirs(settings.app_default_files_dir, exist_ok=True)
        except:
            pass
        file_name = tr("Untitled {}.txt")
        i = 1
        file_names_in_use = self.file_names_in_use()
        while True:
            file_name_i = file_name.format(i)
            if (
                os.path.exists(
                    os.path.join(
                        settings.app_default_files_dir,
                        file_name_i,
                    )
                )
                or self.format_file_name(file_name_i) in file_names_in_use
            ):
                i = i + 1
            else:
                return file_name_i

    def update_label_text(self, unsaved):
        self.label.setText(self.file_name + ("*" if unsaved else ""))

    def auto_save_once_done_typing(self):
        if (
            time.time() - self.text_most_recently_modified_time
            >= settings.text_editor_autosave_after_idle_interval
        ):
            if os.path.exists(self.path):
                self.on_save()
        else:
            QTimer.singleShot(1000, self.auto_save_once_done_typing)

    def remove(self):
        self.main_window.text_edits.remove(self.text_edit)
        self.main_window.scrollbar_signalers.remove(
            self.text_edit.scrollbar_signaler
        )
        state.texts[self.path] = (time.time(), self.state)
        state.save()
        self.deleteLater()

    def on_dict_combo_hide_popup(self, name):
        self.text_edit.text_edit.setFocus()
        path = os.path.join(settings.dict_dir, f"{name}{app_info.db_ext}")
        if path == self.prev_dict_path:
            return
        if os.path.exists(path):
            if self.text_edit.text_edit.popup is not None:
                self.text_edit.text_edit.popup.deleteLater()
            db = dict_database.DictDatabase(path)
            self.text_edit.text_edit.popup = dict_popup.DictPopup(
                self.text_edit.text_edit,
                db,
            )
            db.on_change_fns.add(self.text_edit.text_edit.pop_refresh)
            state.last_selected_dict = name
            self.prev_dict_path = path
        else:
            if self.text_edit.text_edit.popup is not None:
                self.text_edit.text_edit.popup.deleteLater()
            self.text_edit.text_edit.popup = None
            self.prev_dict_path = None

    def on_dict_combo_resize_event(self, event):
        self.dict_combo_resize_event(event)
        self.widget.setFixedWidth(event.size().width())
        self.dummy_label.setMinimumWidth(event.size().width())
        self.label.setGeometry(self.dummy_label.geometry())

    def on_focus_in(self):
        text = self.text_edit.text_edit.toPlainText()
        try:
            with open(self.path, mode="r", encoding="utf-8") as file:
                loaded_text = file.read()
        except FileNotFoundError:
            return
        if text == loaded_text:
            return
        if loaded_text == self.saved_text:
            return

        selection = self.text_edit.selection()
        scroll_value = self.text_edit.scroll_value()

        def on_reload():
            self.saved_text = loaded_text
            self.set_text(loaded_text)
            self.text_edit.set_selection(selection)
            self.text_edit.set_scroll_value(scroll_value)

        def on_ignore():
            self.saved_text = loaded_text
            self.on_save_status_changed()

        if self.unsaved:
            messages.ReloadUnsavedTextWarningMessage(
                self.file_name,
                on_reload,
                on_ignore,
            ).show()
        else:
            messages.ReloadTextWarningMessage(
                self.file_name,
                on_reload,
                on_ignore,
            ).show()

    def on_focus_out(self):
        if settings.text_editor_autosave:
            if os.path.exists(self.path):
                self.on_save()

    def on_save_status_changed(self):
        unsaved = self.unsaved
        self.update_label_text(unsaved)
        if unsaved and settings.text_editor_autosave:
            self.auto_save_once_done_typing()
        self.prev_unsaved = self.unsaved

    def on_text_modified(self):
        self.text_most_recently_modified_time = time.time()
        if self.unsaved != self.prev_unsaved:
            self.on_save_status_changed()

    def on_open(self):
        try:
            with open(self.path, mode="r", encoding="utf-8") as file:
                text = file.read()
                self.saved_text = text
                self.set_text(text)
        except FileNotFoundError:
            messages.FileDoesNotExistErrorMessage(self.path).show()
            self.remove()

    def on_save(self):
        if not os.path.exists(self.path):
            path = utils.get_save_file_name(
                self,
                tr("Save Text"),
                self.path,
            )
            if not path:
                return path
            self.path = path
            if not os.path.splitext(self.path)[1]:
                self.path = self.path + ".txt"
        text = self.text_edit.text_edit.toPlainText()
        with open(self.path, mode="w", encoding="utf-8") as file:
            file.write(text)
        self.saved_text = text
        self.on_save_status_changed()
        return self.path

    def on_save_as(self):
        path = utils.get_save_file_name(
            self,
            tr("Save Text As"),
            os.path.basename(self.path),
        )
        if not path:
            return path
        if not os.path.splitext(path)[1]:
            path = path + ".txt"
        with open(path, mode="w", encoding="utf-8") as file:
            file.write(self.text_edit.text_edit.toPlainText())
        return path

    def on_close(self, if_close_successful=lambda: None):
        def close():
            self.remove()
            if_close_successful()

        def save_and_close():
            if self.on_save():
                close()

        if self.unsaved:
            messages.UnsavedFilesWarningMessage(
                [self.path],
                close,
                save_and_close,
            ).show()
            return
        else:
            close()

    def on_update_settings(self):
        self.update_label_text(self.unsaved)
        content_margin = int(
            round(settings.app_layout_content_margin * self.dpi)
        )
        handle_width = int(
            round(settings.app_layout_splitter_handle_width * self.dpi)
        )
        half_handle_width = handle_width // 2
        self.layout().setContentsMargins(
            content_margin - half_handle_width,
            content_margin,
            content_margin - half_handle_width,
            content_margin,
        )
        self.top.layout().setContentsMargins(
            0,
            0,
            0,
            content_margin,
        )
        self.update()
