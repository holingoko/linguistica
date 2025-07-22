import os
import time

from src import app
from src import app_info
from src import dict_database_file
from src import menus
from src import messages
from src import settings
from src import splitter
from src import state
from src import text_editor
from src import utils
from src import window
from src.language import tr
from src.qt import *


class MainWindow(window.Window):
    def __init__(self, window_state=None):
        super().__init__()
        try:
            text_editor_states, geometry, splitter_state = window_state
        except TypeError:
            text_editor_states = [
                text_editor.TextEditor.default_state()
                for _ in range(settings.text_editor_window_default_num_views)
            ]
            geometry = None
            splitter_state = None
        self.setWindowTitle(app_info.name)
        self.splitter = splitter.Splitter()
        self.setLayout(QVBoxLayout())
        self.layout().setMenuBar(menus.MenuBar(self))
        self.layout().addWidget(self.splitter)
        self.layout().setSpacing(0)
        self.text_edits = set()
        self.scrollbar_signalers = set()
        for text_editor_state in text_editor_states:
            self.splitter.addWidget(
                text_editor.TextEditor(
                    self,
                    text_editor_state,
                )
            )
        self.on_update_settings()
        if (
            settings.app_remember_window_geometry
            and geometry is not None
            and splitter_state is not None
        ):
            self.restoreGeometry(geometry)
            self.splitter.restoreState(splitter_state)
        else:
            self.initialize_geometry()

    @property
    def default_width(self):
        return (
            settings.text_editor_window_default_width_per_view
            * self.splitter.count()
        )

    @property
    def default_height(self):
        return settings.text_editor_window_default_height

    @property
    def text_editors(self):
        return [self.splitter.widget(i) for i in range(self.splitter.count())]

    @property
    def text_editor_with_focus(self):
        for text_editor_ in self.text_editors:
            if text_editor_.text_edit.text_edit.hasFocus():
                return text_editor_
        return None

    @staticmethod
    def x_or_y(position):
        if (
            settings.text_editor_splitter_orientation
            == settings.Orientation.HORIZONTAL
        ):
            return position.x()
        else:
            return position.y()

    def closeEvent(self, event):
        text_editors = self.text_editors

        def continue_():
            text_editor_paths = []
            text_editor_states = []
            close_time = time.time()
            for text_editor_ in text_editors:
                state.texts[text_editor_.path] = (
                    close_time,
                    text_editor_.state,
                )
                text_editor_paths.append(text_editor_.path)
                text_editor_states.append(text_editor_.state)
            state.windows[state.PATH_SEPARATOR.join(text_editor_paths)] = (
                close_time,
                (
                    text_editor_states,
                    self.saveGeometry(),
                    self.splitter.saveState(),
                ),
            )
            state.save()
            window.Window.closeEvent(self, event)

        def on_save_and_close():
            if self.on_save_all_texts():
                continue_()
            else:
                self.raise_()

        unsaved_paths = [
            text_editor_.path
            for text_editor_ in text_editors
            if text_editor_.unsaved
        ]
        if unsaved_paths:
            event.ignore()
            messages.UnsavedFilesWarningMessage(
                unsaved_paths,
                continue_,
                on_save_and_close,
            ).show()
        else:
            continue_()

    def dropEvent(self, event):
        for url in event.mimeData().urls():
            path = url.path()[1:]
            if os.path.exists(path):
                self.handle_dropped_file(
                    os.path.normpath(path),
                    None,
                    position=event.position(),
                )

    def handle_dropped_file(self, path, text_editor_, position=None):
        try:
            with open(path, mode="r", encoding="utf-8") as file:
                file.read()
        except UnicodeDecodeError:
            dict_database_file.on_import_dict_database_file(
                path,
                error_msg_class=messages.FileIsNotTextOrDictionaryErrorMessage,
                on_success=(
                    text_editor_.dict_combo_box.set_name
                    if text_editor_
                    else lambda _: None
                ),
            )
            return
        if position is not None:
            x_or_y = self.x_or_y(position)
            for index, text_editor_ in enumerate(self.text_editors):
                if x_or_y < self.x_or_y(
                    text_editor_.pos()
                    + QPoint(text_editor_.width(), text_editor_.height()) / 2.0
                ):
                    self.splitter.insertWidget(
                        index,
                        text_editor.TextEditor(
                            self,
                            self.get_state_or_default(path),
                        ),
                    )
                    break
        if (
            settings.text_editor_behavior_on_drag_and_drop_file
            == settings.OpenFileBehavior.NEW_WINDOW
        ):
            MainWindow(([self.get_state_or_default(path)], None, None)).show()
        elif (
            settings.text_editor_behavior_on_drag_and_drop_file
            == settings.OpenFileBehavior.INSERT
            or text_editor_ is None
        ):
            self.open_insert(text_editor_, path)
        else:
            self.open_replace(text_editor_, path)

    def insertion_index(self, open_side, text_editor_):
        side = settings.Side
        if open_side == side.FAR_LEFT:
            return 0
        if open_side == side.FAR_RIGHT:
            return self.splitter.count()
        index = self.splitter.indexOf(text_editor_)
        if open_side == side.LEFT_OF_SELECTED:
            if index == -1:
                return 0
            else:
                return index
        if open_side == settings.Side.RIGHT_OF_SELECTED:
            if index == -1:
                return self.splitter.count()
            else:
                return index + 1

    @staticmethod
    def get_state_or_default(path):
        try:
            return state.texts[path][1]
        except KeyError:
            return text_editor.TextEditor.default_state(path)

    def open_insert(self, text_editor_, path):
        self.splitter.insertWidget(
            self.insertion_index(
                settings.text_editor_open_side_existing_texts,
                text_editor_,
            ),
            text_editor.TextEditor(self, self.get_state_or_default(path)),
        )
        self.splitter.equalize_widget_sizes()

    def open_replace(self, text_editor_, path):
        index = self.splitter.indexOf(text_editor_)

        def if_close_successful():
            self.splitter.insertWidget(
                index,
                text_editor.TextEditor(self, self.get_state_or_default(path)),
            )

        text_editor_.on_close(if_close_successful)
        self.splitter.equalize_widget_sizes()

    def on_new_text(self):
        text_editor_ = self.text_editor_with_focus
        if (
            settings.text_editor_behavior_on_new_text_file
            == settings.OpenFileBehavior.NEW_WINDOW
        ):
            MainWindow(
                ([text_editor.TextEditor.default_state()], None, None)
            ).show()
            return
        if (
            settings.text_editor_behavior_on_new_text_file
            == settings.OpenFileBehavior.INSERT
            or text_editor_ is None
        ):
            self.splitter.insertWidget(
                self.insertion_index(
                    settings.text_editor_open_side_new_texts,
                    text_editor_,
                ),
                text_editor.TextEditor(
                    self,
                    text_editor.TextEditor.default_state(),
                ),
            )
            self.splitter.equalize_widget_sizes()
        else:
            index = self.splitter.indexOf(text_editor_)

            def if_close_successful():
                self.splitter.insertWidget(
                    index,
                    text_editor.TextEditor(
                        self,
                        text_editor.TextEditor.default_state(),
                    ),
                )

            text_editor_.on_close(if_close_successful)
            self.splitter.equalize_widget_sizes()

    def on_open_text(self, path=""):
        text_editor_ = self.text_editor_with_focus
        if not path:
            path = utils.get_open_file_name(
                self,
                tr("Open Text"),
            )
        if not path:
            return
        if (
            settings.text_editor_behavior_on_open_file
            == settings.OpenFileBehavior.NEW_WINDOW
        ):
            MainWindow(([self.get_state_or_default(path)], None, None)).show()
            return
        if (
            settings.text_editor_behavior_on_open_file
            == settings.OpenFileBehavior.INSERT
            or text_editor_ is None
        ):
            self.open_insert(text_editor_, path)
        else:
            self.open_replace(text_editor_, path)

    @classmethod
    def create_window_and_open_text(cls, path=""):
        if not path:
            path = utils.get_open_file_name(
                None,
                tr("Open Text"),
            )
        if not path:
            return
        MainWindow(([cls.get_state_or_default(path)], None, None)).show()

    def on_save_text(self):
        try:
            self.text_editor_with_focus.on_save()
        except AttributeError:
            messages.NoTextEditorSelectedErrorMessage().show()

    def on_save_text_as(self):
        try:
            self.text_editor_with_focus.on_save_as()
        except AttributeError:
            messages.NoTextEditorSelectedErrorMessage().show()

    def on_save_all_texts(self):
        return all(
            text_editor_.on_save() for text_editor_ in self.text_editors
        )

    def on_copy_file_name(self):
        try:
            app.clipboard().setText(self.text_editor_with_focus.file_name)
        except AttributeError:
            messages.NoTextEditorSelectedErrorMessage().show()

    def on_copy_file_path(self):
        try:
            app.clipboard().setText(self.text_editor_with_focus.path)
        except AttributeError:
            messages.NoTextEditorSelectedErrorMessage().show()

    def on_rename_text(self):
        try:
            text_editor_ = self.text_editor_with_focus
            path = text_editor_.on_save_as()
        except AttributeError:
            messages.NoTextEditorSelectedErrorMessage().show()
            return
        if not path:
            return
        index = self.splitter.indexOf(text_editor_)
        state_ = text_editor_.state
        text_editor_.remove()
        self.splitter.insertWidget(
            index,
            text_editor.TextEditor(
                self,
                (path, *state_[1:]),
            ),
        )
        self.splitter.equalize_widget_sizes()

    def on_lock_text(self):
        try:
            self.text_editor_with_focus.locked = True
        except AttributeError:
            messages.NoTextEditorSelectedErrorMessage().show()

    def on_lock_all_texts(self):
        for text_editor_ in self.text_editors:
            text_editor_.locked = True

    def on_unlock_text(self):
        try:
            self.text_editor_with_focus.locked = False
        except AttributeError:
            messages.NoTextEditorSelectedErrorMessage().show()

    def on_unlock_all_texts(self):
        for text_editor_ in self.text_editors:
            text_editor_.locked = False

    def on_close_text(self):
        is_last_text_in_window = self.splitter.count() == 1
        try:
            self.text_editor_with_focus.on_close(
                if_close_successful=lambda: (
                    self.close() if is_last_text_in_window else None
                )
            )
        except AttributeError:
            messages.NoTextEditorSelectedErrorMessage().show()

    def on_move_text_left(self):
        text_editor_with_focus = self.text_editor_with_focus
        if text_editor_with_focus is None:
            messages.NoTextEditorSelectedErrorMessage().show()
            return
        scrollbar_values = {
            text_editor_: text_editor_.get_scrollbar_value()
            for text_editor_ in self.text_editors
        }
        index = self.splitter.indexOf(text_editor_with_focus)
        if index == 0:
            return
        sizes = self.splitter.sizes()
        size = sizes.pop(index)
        index = index - 1
        sizes.insert(index, size)
        text_editor_with_focus.setParent(None)
        self.splitter.insertWidget(index, text_editor_with_focus)
        self.splitter.setSizes(sizes)
        for text_editor_, scrollbar_value in scrollbar_values.items():
            text_editor_.set_scrollbar_value(scrollbar_value)
        text_editor_with_focus.setFocus()

    def on_move_text_right(self):
        text_editor_with_focus = self.text_editor_with_focus
        if text_editor_with_focus is None:
            messages.NoTextEditorSelectedErrorMessage().show()
            return
        scrollbar_values = {
            text_editor_: text_editor_.get_scrollbar_value()
            for text_editor_ in self.text_editors
        }
        index = self.splitter.indexOf(text_editor_with_focus)
        if index == self.splitter.count() - 1:
            return
        sizes = self.splitter.sizes()
        size = sizes.pop(index)
        index = index + 1
        sizes.insert(index, size)
        text_editor_with_focus.setParent(None)
        self.splitter.insertWidget(index, text_editor_with_focus)
        self.splitter.setSizes(sizes)
        for text_editor_, scrollbar_value in scrollbar_values.items():
            text_editor_.set_scrollbar_value(scrollbar_value)
        text_editor_with_focus.setFocus()

    def on_move_popup_forward(self):
        for text_editor_ in self.text_editors:
            text_editor_.text_edit.text_edit.pop_forward()

    def on_move_popup_backward(self):
        for text_editor_ in self.text_editors:
            text_editor_.text_edit.text_edit.pop_backward()

    def on_update_settings(self):
        content_margin = int(
            round(settings.app_layout_content_margin * self.dpi)
        )
        handle_width = int(
            round(settings.app_layout_splitter_handle_width * self.dpi)
        )
        half_handle_width = handle_width // 2
        self.layout().setContentsMargins(
            content_margin + half_handle_width,
            content_margin,
            content_margin + half_handle_width,
            content_margin,
        )
        if (
            settings.text_editor_splitter_orientation
            == settings.Orientation.HORIZONTAL
        ):
            self.splitter.setOrientation(Qt.Orientation.Horizontal)
        else:
            self.splitter.setOrientation(Qt.Orientation.Vertical)
        self.update()
