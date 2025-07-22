from src import app
from src import clipboard
from src import label
from src import line_edit
from src import menus
from src import selectable_frame
from src import settings
from src import utils
from src.qt import *


class FormEdit(selectable_frame.SelectableFrame):
    def __init__(self, window, form_id):
        super().__init__()
        self.window = window
        self.form_id = form_id
        self.context_menu = menus.TagEditOrFormEditContextMenu(window)
        self.space_between_rows = 0
        self.setLayout(QVBoxLayout())
        self.layout().setSpacing(0)
        self.on_data_change = lambda: None
        self.on_focus_range_change = lambda x, y: None
        self.on_resize = lambda: None
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
    def num_rows(self):
        return self.layout().count()

    @property
    def rows(self):
        layout = self.layout()
        return [layout.itemAt(i).widget() for i in range(layout.count())]

    def contextMenuEvent(self, event):
        try:
            self.context_menu.move(event.globalPos())
            self.context_menu.show()
        except AttributeError:
            pass

    def focusOutEvent(self, event):
        super().focusOutEvent(event)
        self.on_data_change()
        parent = self.parent()
        utils.run_after_current_event(
            parent.clear_selection_if_no_child_has_focus
        )

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.RightButton:
            if not self.selected:
                for row in self.parent().rows:
                    row.selected = False
            self.setFocus()
            self.selected = True
            return
        if app.keyboardModifiers() == Qt.KeyboardModifier.ControlModifier:
            if self.selected:
                self.clearFocus()
                self.selected = False
                for row in reversed(self.parent().rows):
                    if row.selected:
                        row.setFocus()
                        break
            else:
                self.set_focus_inclusive()
        elif app.keyboardModifiers() == Qt.KeyboardModifier.ShiftModifier:
            parent = self.parent()
            layout = parent.layout()
            focus_index = layout.indexOf(app.focusWidget())
            if focus_index == -1:
                self.set_focus_exclusive(update_range=False)
                return
            self_index = layout.indexOf(self)
            parent.set_selected_range(focus_index, self_index)
        else:
            self.set_focus_exclusive(update_range=False)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.on_resize()

    def set_focus_exclusive(self, update_range=True):
        for row in self.parent().rows:
            row.selected = False
        self.setFocus()
        self.selected = True
        y_min = self.y()
        y_max = y_min + self.height()
        y_min = y_min - self.space_between_rows
        y_max = y_max + self.space_between_rows
        if update_range:
            self.on_focus_range_change(y_min, y_max)

    def set_focus_inclusive(self):
        self.setFocus()
        self.selected = True

    def clear_layout(self):
        layout = self.layout()
        while True:
            try:
                layout.takeAt(0).widget().deleteLater()
            except AttributeError:
                break

    def set_row_data(self, row_data):
        self.clear_layout()
        for data in row_data:
            tag_id, tag_name, tag_values = data
            row = TagValuesListEdit(self.window, self, tag_id, tag_name)
            row.set_tag_values(tag_values)
            row.on_data_change = self.data_change
            row.on_focus_range_change = self.focus_range_change
            self.layout().insertWidget(self.num_rows, row)
        self.update_height()

    def get_row_data(self):
        return [
            (row.tag_id, row.tag_name, row.get_tag_values())
            for row in self.rows
        ]

    def data_change(self):
        return self.on_data_change()

    def focus_range_change(self, y_min, y_max):
        y_min = y_min + self.y()
        y_max = y_max + self.y()
        self.on_focus_range_change(y_min, y_max)

    def disable_non_single_form_actions(self):
        self.on_cut = lambda: None
        self.on_paste = lambda: None
        self.on_duplicate = lambda: None
        self.on_add_above = lambda: None
        self.on_add_below = lambda: None
        self.on_delete = lambda: None

    def on_undo(self):
        self.window.undo_redo.undo()

    def on_redo(self):
        self.window.undo_redo.redo()

    def on_cut(self):
        parent = self.parent()
        layout = parent.layout()
        index = layout.indexOf(self)
        selected_indices, row_data = parent.get_selected_indices_and_row_data()

        def redo():
            clipboard.forms = row_data
            for i in reversed(selected_indices):
                layout.takeAt(i).widget().deleteLater()
            parent.update_height()

        def undo():
            for i, data in zip(selected_indices, row_data, strict=True):
                parent.insert_row(i, data)
            parent.set_selected_indices(selected_indices, index)
            parent.update_height()

        self.window.undo_redo.do(undo, redo)

    def on_copy(self):
        clipboard.forms = self.parent().get_selected_row_data()

    def on_paste(self):
        clipboard_value = clipboard.forms
        if not clipboard_value:
            return
        parent = self.parent()
        layout = parent.layout()
        index = layout.indexOf(self)
        selected_indices = parent.get_selected_indices()

        def redo():
            insertion_index = index
            parent.clear_selection()
            for data in clipboard_value:
                row = parent.insert_row(insertion_index, data)
                row.selected = True
                insertion_index = insertion_index + 1
            parent.update_height()

        def undo():
            for _ in range(len(clipboard_value)):
                layout.takeAt(index).widget().deleteLater()
            parent.set_selected_indices(selected_indices, index)
            parent.update_height()

        self.window.undo_redo.do(undo, redo)

    def on_duplicate(self):
        parent = self.parent()
        layout = parent.layout()
        index = layout.indexOf(self)
        selected_indices, row_data = parent.get_selected_indices_and_row_data()

        def redo():
            parent.clear_selection()
            insertion_index = selected_indices[-1] + 1
            for data in row_data:
                row = parent.insert_row(insertion_index, data)
                row.selected = True
                insertion_index = insertion_index + 1
            parent.update_height()

        def undo():
            for i in selected_indices:
                layout.takeAt(i).widget().deleteLater()
            parent.set_selected_indices(selected_indices, index)
            parent.update_height()

        self.window.undo_redo.do(undo, redo)

    def on_select_all(self):
        for row in self.parent().rows:
            row.selected = True
        try:
            row.setFocus()
        except NameError:
            pass

    def on_add_above(self):
        parent = self.parent()
        layout = parent.layout()
        index = layout.indexOf(self)
        selected_indices = parent.get_selected_indices()

        def redo():
            parent.insert_empty_row(index).set_focus_exclusive()
            parent.update_height()

        def undo():
            layout.takeAt(index).widget().deleteLater()
            parent.set_selected_indices(selected_indices, index)
            parent.update_height()

        self.window.undo_redo.do(undo, redo)

    def on_add_below(self):
        parent = self.parent()
        layout = parent.layout()
        index = layout.indexOf(self)
        selected_indices = parent.get_selected_indices()

        def redo():
            parent.insert_empty_row(index + 1).set_focus_exclusive()
            parent.update_height()

        def undo():
            layout.takeAt(index + 1).widget().deleteLater()
            parent.set_selected_indices(selected_indices, index)
            parent.update_height()

        self.window.undo_redo.do(undo, redo)

    def on_move_up(self):
        parent = self.parent()
        layout = parent.layout()
        selected_indices = parent.get_selected_indices()
        if selected_indices[0] == 0:
            return

        def redo():
            for i in selected_indices:
                layout.insertWidget(i - 1, layout.takeAt(i).widget())

        def undo():
            for i in reversed(selected_indices):
                layout.insertWidget(i, layout.takeAt(i - 1).widget())

        self.window.undo_redo.do(undo, redo)

    def on_move_down(self):
        parent = self.parent()
        layout = parent.layout()
        selected_indices = parent.get_selected_indices()
        if selected_indices[-1] == parent.num_rows - 1:
            return

        def redo():
            for i in reversed(selected_indices):
                layout.insertWidget(i + 1, layout.takeAt(i).widget())

        def undo():
            for i in selected_indices:
                layout.insertWidget(i, layout.takeAt(i + 1).widget())

        self.window.undo_redo.do(undo, redo)

    def on_move_to_top(self):
        parent = self.parent()
        layout = parent.layout()
        selected_indices = parent.get_selected_indices()
        shift = selected_indices[0]
        if not shift:
            return

        def redo():
            for i in selected_indices:
                layout.insertWidget(i - shift, layout.takeAt(i).widget())

        def undo():
            for i in reversed(selected_indices):
                layout.insertWidget(i, layout.takeAt(i - shift).widget())

        self.window.undo_redo.do(undo, redo)

    def on_move_to_bottom(self):
        parent = self.parent()
        layout = parent.layout()
        selected_indices = parent.get_selected_indices()
        shift = parent.num_rows - 1 - selected_indices[-1]
        if not shift:
            return

        def redo():
            for i in reversed(selected_indices):
                layout.insertWidget(i + shift, layout.takeAt(i).widget())

        def undo():
            for i in selected_indices:
                layout.insertWidget(i, layout.takeAt(i + shift).widget())

        self.window.undo_redo.do(undo, redo)

    def on_delete(self):
        parent = self.parent()
        layout = parent.layout()
        index = layout.indexOf(self)
        selected_indices, row_data = parent.get_selected_indices_and_row_data()

        def redo():
            for i in reversed(selected_indices):
                layout.takeAt(i).widget().deleteLater()
            try:
                layout.itemAt(max(index - 1, 0)).widget().set_focus_exclusive()
            except AttributeError:
                parent.frame.setFocus()
            parent.update_height()

        def undo():
            for i, data in zip(selected_indices, row_data, strict=True):
                parent.insert_row(i, data)
            parent.set_selected_indices(selected_indices, index)
            parent.update_height()

        self.window.undo_redo.do(undo, redo)

    def on_previous_form(self):
        try:
            utils.prev_widget(self).set_focus_exclusive()
        except AttributeError:
            pass

    def on_next_form(self):
        try:
            utils.next_widget(self).set_focus_exclusive()
        except AttributeError:
            pass

    def on_previous_tag_value(self):
        try:
            utils.bottom_sub_widget(
                utils.bottom_sub_widget(utils.prev_widget(self)).tag_values
            ).setFocus()
        except AttributeError:
            utils.top_sub_widget(
                utils.top_sub_widget(self).tag_values
            ).setFocus()

    def on_next_tag_value(self):
        try:
            utils.top_sub_widget(
                utils.top_sub_widget(utils.next_widget(self)).tag_values
            ).setFocus()
        except AttributeError:
            utils.bottom_sub_widget(
                utils.bottom_sub_widget(self).tag_values
            ).setFocus()

    def update_height(self):
        content_margin = int(
            round(settings.app_layout_content_margin * self.dpi)
        )
        row_height_sum = 0
        for row in self.rows:
            row_height_sum = row_height_sum + row.height()
        self.setFixedHeight(row_height_sum + 2 * content_margin)
        self.on_resize()
        self.update()

    def on_update_settings(self):
        self.space_between_rows = (
            settings.app_layout_spacing_between_rows * self.dpi
        )
        content_margin = int(
            round(settings.app_layout_content_margin * self.dpi)
        )
        self.layout().setContentsMargins(
            content_margin,
            content_margin,
            content_margin,
            content_margin,
        )
        self.layout().setSpacing(0)
        self.update_height()
        self.update()


class TagValuesListEdit(QWidget):
    def __init__(self, window, form_rows, tag_id, tag_name):
        super().__init__()
        self.window = window
        self.form_rows = form_rows
        self.tag_id = tag_id
        self.tag_name = tag_name
        self.label = label.Label(f"{tag_name}:")
        self.tag_values = QWidget()
        self.setLayout(QVBoxLayout())
        self.layout().addWidget(self.label)
        self.layout().addWidget(self.tag_values)
        self.tag_values.setLayout(QVBoxLayout())
        self.on_data_change = lambda: None
        self.on_focus_range_change = lambda x, y: None
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
    def num_rows(self):
        return self.tag_values.layout().count()

    @property
    def rows(self):
        layout = self.tag_values.layout()
        return [layout.itemAt(i).widget() for i in range(layout.count())]

    def clear_layout(self):
        layout = self.tag_values.layout()
        while True:
            try:
                layout.takeAt(0).widget().deleteLater()
            except AttributeError:
                break

    def set_tag_values(self, tag_values):
        self.clear_layout()
        for tag_value in tag_values:
            row = TagValueLineEdit(self.window)
            row.setText(tag_value)
            row.on_data_change = self.data_change
            row.on_focus_range_change = self.focus_range_change
            self.tag_values.layout().insertWidget(self.num_rows, row)
        self.update_height()

    def get_tag_values(self):
        return [row.text() for row in self.rows]

    def append_row(self, text):
        return self.insert_row(self.num_rows, text)

    def append_empty_row(self):
        return self.insert_row(self.num_rows, "")

    def insert_row(self, index, text):
        row = TagValueLineEdit(self.window)
        row.setText(text)
        row.on_data_change = self.data_change
        row.on_focus_range_change = self.focus_range_change
        self.tag_values.layout().insertWidget(index, row)
        row.setFocus()
        return row

    def insert_empty_row(self, index):
        return self.insert_row(index, "")

    def data_change(self):
        return self.on_data_change()

    def focus_range_change(self, y_min, y_max):
        y_min = y_min + self.tag_values.y() + self.y()
        y_max = y_max + self.tag_values.y() + self.y()
        self.on_focus_range_change(y_min, y_max)

    def update_height(self):
        content_margin = int(
            round(settings.app_layout_content_margin * self.dpi)
        )
        spacing = int(round(settings.app_layout_spacing * self.dpi))
        row_spacing = int(
            round(settings.app_layout_spacing_between_rows * self.dpi)
        )
        row_height_sum = 0
        for row in self.rows:
            row_height_sum = row_height_sum + row.height()
        self.setFixedHeight(
            self.label.height()
            + spacing
            + row_height_sum
            + row_spacing * (self.num_rows - 1)
            + 2 * content_margin
        )
        self.form_rows.update_height()
        self.update()

    def on_update_settings(self):
        content_margin = int(
            round(settings.app_layout_content_margin * self.dpi)
        )
        self.layout().setContentsMargins(
            content_margin,
            0,
            content_margin,
            content_margin,
        )
        self.tag_values.layout().setContentsMargins(
            content_margin,
            0,
            content_margin,
            0,
        )
        row_spacing = int(
            round(settings.app_layout_spacing_between_rows * self.dpi)
        )
        self.layout().setSpacing(row_spacing)
        self.tag_values.layout().setSpacing(row_spacing)
        self.label.setFixedHeight(utils.calculate_default_height(QLabel))
        self.update_height()
        self.update()


class TagValueLineEdit(line_edit.LineEdit):
    def __init__(self, window):
        super().__init__(window)
        self.window = window
        self.context_menu = menus.TagEditOrFormEditContextMenu(window)
        self.on_data_change = lambda: None
        self.on_focus_range_change = lambda x, y: None
        self.pre_edit_selection = None
        self.pre_edit_text = ""
        self.prev_key_arrow = False
        self.space_between_rows = 0
        self.textChanged.connect(self.data_change)
        self.on_update_settings()

    @property
    def dpi(self):
        screen = self.screen()
        return screen.physicalDotsPerInch() / (
            screen.devicePixelRatio()
            if settings.app_scale_sizes_by_device_pixel_ratio
            else 1.0
        )

    def contextMenuEvent(self, event):
        self.context_menu.move(event.globalPos())
        self.context_menu.show()

    def event(self, event):
        if event.type() == QEvent.Type.ShortcutOverride:
            event.ignore()
            return False
        return super().event(event)

    def focusInEvent(self, event):
        super().focusInEvent(event)
        y_min = self.y()
        y_max = y_min + self.height()
        y_min = y_min - self.space_between_rows
        y_max = y_max + self.space_between_rows
        utils.run_after_current_event(
            lambda: self.on_focus_range_change(y_min, y_max),
        )

    def focusOutEvent(self, event):
        super().focusOutEvent(event)
        self.on_data_change()
        self.add_text_changes_to_undo_redo()

    def focusNextPrevChild(self, _next):
        return False

    def keyPressEvent(self, event):
        key = event.key()
        if Qt.KeyboardModifier.ControlModifier in event.modifiers():
            return
        elif key in {
            Qt.Key.Key_Up,
            Qt.Key.Key_Down,
            Qt.Key.Key_Tab,
            Qt.Key.Key_Backtab,
        }:
            return
        if key in {Qt.Key.Key_Left, Qt.Key.Key_Right}:
            self.prev_key_arrow = True
        elif self.prev_key_arrow:
            self.add_text_changes_to_undo_redo()
            self.prev_key_arrow = False
        super().keyPressEvent(event)

    def mouseReleaseEvent(self, event):
        super().mouseReleaseEvent(event)
        self.add_text_changes_to_undo_redo()

    def cut(self):
        super().cut()
        self.pre_edit_text = self.text()
        self.pre_edit_selection = self.selection()

    def insert(self, text):
        super().insert(text)
        self.pre_edit_text = self.text()
        self.pre_edit_selection = self.selection()

    def setSelection(self, selection_start, selection_length):
        super().setSelection(selection_start, selection_length)
        self.pre_edit_selection = selection_start, selection_length

    def setText(self, text):
        super().setText(text)
        self.pre_edit_text = text
        self.pre_edit_selection = self.selection()

    def selection(self):
        cursor_position = self.cursorPosition()
        selection_start = self.selectionStart()
        selection_length = self.selectionLength()
        if selection_length == 0:
            return cursor_position, selection_length
        elif cursor_position == selection_start:
            selection_end = selection_start + selection_length
            return selection_end, -selection_length
        else:
            return selection_start, selection_length

    def add_text_changes_to_undo_redo(self):
        pre_edit_text = self.pre_edit_text
        post_edit_text = self.text()
        if pre_edit_text == post_edit_text:
            return
        parent_fn, index = persistent_parent_fn_and_index(self)
        pre_edit_selection = self.pre_edit_selection
        post_edit_selection = self.selection()

        def redo():
            parent = parent_fn()
            layout = parent.tag_values.layout()
            widget = layout.itemAt(index).widget()
            widget.setText(post_edit_text)
            widget.setSelection(*post_edit_selection)

        def undo():
            parent = parent_fn()
            layout = parent.tag_values.layout()
            widget = layout.itemAt(index).widget()
            widget.setText(pre_edit_text)
            widget.setSelection(*pre_edit_selection)

        self.window.undo_redo.do(undo, redo)

    def data_change(self):
        return self.on_data_change()

    def on_undo(self):
        self.add_text_changes_to_undo_redo()
        self.window.undo_redo.undo()

    def on_redo(self):
        self.add_text_changes_to_undo_redo()
        self.window.undo_redo.redo()

    def on_cut(self):
        self.add_text_changes_to_undo_redo()
        selected_text = self.selectedText()
        if not selected_text:
            return
        parent_fn, index = persistent_parent_fn_and_index(self)
        pre_cut_text = self.text()
        selection = self.selection()

        def redo():
            parent = parent_fn()
            layout = parent.tag_values.layout()
            widget = layout.itemAt(index).widget()
            widget.setSelection(*selection)
            widget.cut()

        def undo():
            parent = parent_fn()
            layout = parent.tag_values.layout()
            widget = layout.itemAt(index).widget()
            widget.setText(pre_cut_text)
            widget.setSelection(*selection)

        self.window.undo_redo.do(undo, redo)

    def on_copy(self):
        self.add_text_changes_to_undo_redo()
        selected_text = self.selectedText()
        if not selected_text:
            return
        self.copy()

    def on_paste(self):
        self.add_text_changes_to_undo_redo()
        text = app.clipboard().text()
        if not text:
            return
        parent_fn, index = persistent_parent_fn_and_index(self)
        pre_paste_text = self.text()
        selection = self.selection()

        def redo():
            parent = parent_fn()
            layout = parent.tag_values.layout()
            widget = layout.itemAt(index).widget()
            widget.setSelection(*selection)
            widget.insert(text)

        def undo():
            parent = parent_fn()
            layout = parent.tag_values.layout()
            widget = layout.itemAt(index).widget()
            widget.setText(pre_paste_text)
            widget.setSelection(*selection)

        self.window.undo_redo.do(undo, redo)

    def on_duplicate(self):
        self.add_text_changes_to_undo_redo()
        parent_fn, index = persistent_parent_fn_and_index(self)
        text = self.text()

        def redo():
            parent = parent_fn()
            parent.insert_row(index + 1, text)
            parent.update_height()

        def undo():
            parent = parent_fn()
            layout = parent.tag_values.layout()
            layout.takeAt(index + 1).widget().deleteLater()
            layout.itemAt(index).widget().setFocus()
            parent.update_height()

        self.window.undo_redo.do(undo, redo)

    def on_select_all(self):
        self.add_text_changes_to_undo_redo()
        self.selectAll()

    def on_add_above(self):
        self.add_text_changes_to_undo_redo()
        parent_fn, index = persistent_parent_fn_and_index(self)

        def redo():
            parent = parent_fn()
            parent.insert_empty_row(index)
            parent.update_height()

        def undo():
            parent = parent_fn()
            layout = parent.tag_values.layout()
            layout.takeAt(index).widget().deleteLater()
            layout.itemAt(index).widget().setFocus()
            parent.update_height()

        self.window.undo_redo.do(undo, redo)

    def on_add_below(self):
        self.add_text_changes_to_undo_redo()
        parent_fn, index = persistent_parent_fn_and_index(self)

        def redo():
            parent = parent_fn()
            parent.insert_empty_row(index + 1)
            parent.update_height()

        def undo():
            parent = parent_fn()
            layout = parent.tag_values.layout()
            layout.takeAt(index + 1).widget().deleteLater()
            layout.itemAt(index).widget().setFocus()
            parent.update_height()

        self.window.undo_redo.do(undo, redo)

    def on_move_up(self):
        self.add_text_changes_to_undo_redo()
        parent_fn, index = persistent_parent_fn_and_index(self)
        if index == 0:
            return

        def redo():
            parent = parent_fn()
            layout = parent.tag_values.layout()
            widget = layout.takeAt(index).widget()
            layout.insertWidget(index - 1, widget)

        def undo():
            parent = parent_fn()
            layout = parent.tag_values.layout()
            widget = layout.takeAt(index - 1).widget()
            layout.insertWidget(index, widget)

        self.window.undo_redo.do(undo, redo)

    def on_move_down(self):
        self.add_text_changes_to_undo_redo()
        parent_fn, index = persistent_parent_fn_and_index(self)
        if index == self.parent().parent().num_rows - 1:
            return

        def redo():
            parent = parent_fn()
            layout = parent.tag_values.layout()
            widget = layout.takeAt(index).widget()
            layout.insertWidget(index + 1, widget)

        def undo():
            parent = parent_fn()
            layout = parent.tag_values.layout()
            widget = layout.takeAt(index + 1).widget()
            layout.insertWidget(index, widget)

        self.window.undo_redo.do(undo, redo)

    def on_move_to_top(self):
        self.add_text_changes_to_undo_redo()
        parent_fn, index = persistent_parent_fn_and_index(self)
        if index == 0:
            return

        def redo():
            parent = parent_fn()
            layout = parent.tag_values.layout()
            widget = layout.takeAt(index).widget()
            layout.insertWidget(0, widget)

        def undo():
            parent = parent_fn()
            layout = parent.tag_values.layout()
            widget = layout.takeAt(0).widget()
            layout.insertWidget(index, widget)

        self.window.undo_redo.do(undo, redo)

    def on_move_to_bottom(self):
        self.add_text_changes_to_undo_redo()
        parent_fn, index = persistent_parent_fn_and_index(self)
        if index == self.parent().parent().num_rows - 1:
            return

        def redo():
            parent = parent_fn()
            layout = parent.tag_values.layout()
            widget = layout.takeAt(index).widget()
            layout.insertWidget(parent.num_rows, widget)

        def undo():
            parent = parent_fn()
            layout = parent.tag_values.layout()
            widget = layout.takeAt(parent.num_rows - 1).widget()
            layout.insertWidget(index, widget)

        self.window.undo_redo.do(undo, redo)

    def on_delete(self):
        self.add_text_changes_to_undo_redo()
        parent_fn, index = persistent_parent_fn_and_index(self)
        text = self.text()
        if self.parent().parent().num_rows == 1:
            return

        def redo():
            parent = parent_fn()
            layout = parent.tag_values.layout()
            layout.takeAt(index).widget().deleteLater()
            layout.itemAt(max(index - 1, 0)).widget().setFocus()
            parent.update_height()

        def undo():
            parent = parent_fn()
            parent.insert_row(index, text)
            parent.update_height()

        self.window.undo_redo.do(undo, redo)

    def on_previous_form(self):
        form_edit = self.parent().parent().parent()
        try:
            utils.prev_widget(form_edit).set_focus_exclusive()
        except AttributeError:
            form_edit.set_focus_exclusive()

    def on_next_form(self):
        form_edit = self.parent().parent().parent()
        try:
            utils.next_widget(form_edit).set_focus_exclusive()
        except AttributeError:
            form_edit.set_focus_exclusive()

    def on_previous_tag_value(self):
        prev_widget = utils.prev_widget(self)
        try:
            prev_widget.setFocus()
        except AttributeError:
            tag_values_list_edit = self.parent().parent()
            prev_parent = utils.prev_widget(tag_values_list_edit)
            try:
                utils.bottom_sub_widget(prev_parent.tag_values).setFocus()
            except AttributeError:
                form_edit = tag_values_list_edit.parent()
                prev_parent_parent = utils.prev_widget(form_edit)
                try:
                    utils.bottom_sub_widget(
                        utils.bottom_sub_widget(
                            prev_parent_parent,
                        ).tag_values
                    ).setFocus()
                except AttributeError:
                    pass

    def on_next_tag_value(self):
        next_widget = utils.next_widget(self)
        try:
            next_widget.setFocus()
        except AttributeError:
            tag_values_list_edit = self.parent().parent()
            next_parent = utils.next_widget(tag_values_list_edit)
            try:
                utils.top_sub_widget(next_parent.tag_values).setFocus()
            except AttributeError:
                form_edit = tag_values_list_edit.parent()
                next_parent_parent = utils.next_widget(form_edit)
                try:
                    utils.top_sub_widget(
                        utils.top_sub_widget(
                            next_parent_parent,
                        ).tag_values
                    ).setFocus()
                except AttributeError:
                    pass

    def on_update_settings(self):
        self.space_between_rows = (
            settings.app_layout_spacing_between_rows * self.dpi
        )
        self.setFixedHeight(utils.calculate_default_height(QLineEdit))
        self.update()


def persistent_parent_fn_and_index(tag_value_line_edit):
    tag_value_list_edit = tag_value_line_edit.parent().parent()
    form_edit_ = tag_value_list_edit.parent()
    persistent_form_list_edit = form_edit_.parent()
    tag_value_line_edit_index = (
        tag_value_list_edit.tag_values.layout().indexOf(
            tag_value_line_edit,
        )
    )
    tag_value_list_edit_index = form_edit_.layout().indexOf(
        tag_value_list_edit,
    )
    form_edit_index = persistent_form_list_edit.layout().indexOf(
        form_edit_,
    )

    def parent_fn():
        parent = (
            persistent_form_list_edit.layout()
            .itemAt(form_edit_index)
            .widget()
            .layout()
            .itemAt(tag_value_list_edit_index)
            .widget()
        )

        return parent

    return parent_fn, tag_value_line_edit_index
