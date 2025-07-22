from src import clipboard
from src import form_edit
from src import settings
from src.qt import *


class FormListEdit(QWidget):
    def __init__(self, window_, is_single_form=False):
        super().__init__()
        self.window = window_
        self.is_single_form = is_single_form
        if is_single_form:
            self.disable_non_single_form_actions()
        self.setLayout(QVBoxLayout())
        self.layout().setSpacing(0)
        self.empty_form_data = None
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
    def is_empty(self):
        num_forms = self.num_rows
        if num_forms == 0:
            return True
        elif num_forms > 1:
            return False
        form_data = self.get_row_data()[0][1]
        return form_data == self.empty_form_data

    @property
    def num_rows(self):
        return self.layout().count()

    @property
    def rows(self):
        layout = self.layout()
        return [layout.itemAt(i).widget() for i in range(layout.count())]

    def resizeEvent(self, event):
        self.on_resize()
        super().resizeEvent(event)

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
            form_id, form_data = data
            row = form_edit.FormEdit(self.window, form_id)
            row.set_row_data(form_data)
            row.on_data_change = self.data_change
            row.on_focus_range_change = self.focus_range_change
            row.on_resize = self.resize_
            if self.is_single_form:
                row.disable_non_single_form_actions()
            self.layout().insertWidget(self.num_rows, row)
        self.update_height()

    def get_row_data(self):
        return [(row.form_id, row.get_row_data()) for row in self.rows]

    def get_selected_indices_and_row_data(self):
        layout = self.layout()
        selected_indices = []
        row_data = []
        for i in range(self.num_rows):
            row = layout.itemAt(i).widget()
            if row.selected:
                selected_indices.append(i)
                row_data.append(row.get_row_data())
        return selected_indices, row_data

    def get_selected_indices(self):
        layout = self.layout()
        selected_indices = []
        for i in range(self.num_rows):
            row = layout.itemAt(i).widget()
            if row.selected:
                selected_indices.append(i)
        return selected_indices

    def get_selected_row_data(self):
        layout = self.layout()
        row_data = []
        for i in range(self.num_rows):
            row = layout.itemAt(i).widget()
            if row.selected:
                row_data.append(row.get_row_data())
        return row_data

    def clear_selection_if_no_child_has_focus(self):
        for row in self.rows:
            if row.hasFocus():
                return
        self.clear_selection()

    def clear_selection(self):
        for row in self.rows:
            row.selected = False

    def set_selected_indices(self, selected_indices, focus_index):
        layout = self.layout()
        for i in range(self.num_rows):
            row = layout.itemAt(i).widget()
            if i in selected_indices:
                row.selected = True
            if i == focus_index:
                row.setFocus()

    def set_selected_range(self, start_index, end_index):
        layout = self.layout()
        step = 1 if end_index > start_index else -1
        for i in range(start_index, end_index, step):
            layout.itemAt(i).widget().selected = True
        last_row = layout.itemAt(end_index).widget()
        last_row.selected = True
        last_row.setFocus()

    def insert_row(self, index, form_data):
        row = form_edit.FormEdit(self.window, form_id=None)
        row.set_row_data(form_data)
        row.on_data_change = self.data_change
        row.on_focus_range_change = self.focus_range_change
        row.on_resize = self.resize_
        if self.is_single_form:
            row.disable_non_single_form_actions()
        self.layout().insertWidget(index, row)
        row.setFocus()
        return row

    def insert_empty_row(self, index):
        return self.insert_row(index, self.empty_form_data)

    def append_row(self, form_data):
        return self.insert_row(self.num_rows, form_data)

    def append_empty_row(self):
        return self.insert_row(self.num_rows, self.empty_form_data)

    def data_change(self):
        return self.on_data_change()

    def focus_range_change(self, y_min, y_max):
        y_min = y_min + self.y()
        y_max = y_max + self.y()
        self.on_focus_range_change(y_min, y_max)

    def resize_(self):
        self.update_height()

    def update_height(self):
        content_margin = int(
            round(settings.app_layout_content_margin * self.dpi)
        )
        row_spacing = int(
            round(settings.app_layout_spacing_between_rows * self.dpi)
        )
        row_height_sum = 0
        for row in self.rows:
            row_height_sum = row_height_sum + row.height()
        self.setFixedHeight(
            row_height_sum
            + row_spacing * (self.num_rows - 1)
            + 2 * content_margin
        )
        self.on_resize()
        self.data_change()
        self.update()

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
        row_data = [row.get_row_data() for row in self.rows]

        def redo():
            clipboard.forms = row_data
            self.clear_layout()
            self.update_height()

        def undo():
            for data in row_data:
                self.append_row(data)
            self.frame.setFocus()
            self.update_height()

        self.window.undo_redo.do(undo, redo)

    def on_copy(self):
        clipboard.forms = [row.get_row_data() for row in self.rows]

    def on_paste(self):
        clipboard_value = clipboard.forms
        if not clipboard_value:
            return

        def redo():
            if self.is_empty:
                self.clear_layout()
            insertion_index = self.num_rows
            self.clear_selection()
            for data in clipboard_value:
                row = self.insert_row(insertion_index, data)
                row.selected = True
                insertion_index = insertion_index + 1
            self.update_height()

        def undo():
            insertion_index = self.num_rows - 1
            layout = self.layout()
            for _ in range(len(clipboard_value)):
                layout.takeAt(insertion_index).widget().deleteLater()
                insertion_index = insertion_index - 1
            self.frame.setFocus()
            self.update_height()

        self.window.undo_redo.do(undo, redo)

    def on_duplicate(self):
        row_data = [row.get_row_data() for row in self.rows]

        def redo():
            self.clear_selection()
            for data in row_data:
                row = self.append_row(data)
                row.selected = True
            self.update_height()

        def undo():
            insertion_index = self.num_rows - 1
            layout = self.layout()
            for _ in range(len(row_data)):
                layout.takeAt(insertion_index).widget().deleteLater()
                insertion_index = insertion_index - 1
            self.frame.setFocus()
            self.update_height()

        self.window.undo_redo.do(undo, redo)

    def on_select_all(self):
        for row in self.rows:
            row.selected = True
        try:
            row.setFocus()
        except NameError:
            pass

    def on_add_above(self):
        def redo():
            self.insert_empty_row(0).set_focus_exclusive()
            self.update_height()

        def undo():
            self.layout().takeAt(0).widget().deleteLater()
            self.frame.setFocus()
            self.update_height()

        self.window.undo_redo.do(undo, redo)

    def on_add_below(self):
        def redo():
            self.append_empty_row().set_focus_exclusive()
            self.update_height()

        def undo():
            self.layout().takeAt(
                self.num_rows - 1,
            ).widget().deleteLater()
            self.frame.setFocus()
            self.update_height()

        self.window.undo_redo.do(undo, redo)

    def on_move_up(self):
        return

    def on_move_down(self):
        return

    def on_move_to_top(self):
        return

    def on_move_to_bottom(self):
        return

    def on_delete(self):
        row_data = [row.get_row_data() for row in self.rows]

        def redo():
            self.clear_layout()
            self.update_height()

        def undo():
            for data in row_data:
                self.append_row(data)
            self.frame.setFocus()
            self.update_height()

        self.window.undo_redo.do(undo, redo)

    def on_update_settings(self):
        content_margin = int(
            round(settings.app_layout_content_margin * self.dpi)
        )
        self.layout().setContentsMargins(
            content_margin,
            content_margin,
            content_margin,
            content_margin,
        )
        row_spacing = int(
            round(settings.app_layout_spacing_between_rows * self.dpi)
        )
        self.layout().setSpacing(row_spacing)
        self.update_height()
        self.update()
