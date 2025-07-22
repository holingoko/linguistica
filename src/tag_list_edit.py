from src import app
from src import label
from src import language
from src import line_edit
from src import menus
from src import settings
from src import utils
from src.language import tr
from src.qt import *


class TagListHeader(QWidget):
    def __init__(self):
        super().__init__()
        self.name_label = label.SelectableLabel(self)
        self.tag_values_format_label = label.SelectableLabel(self)
        self.indexed_label = label.SelectableLabel(self)
        self.setLayout(QHBoxLayout())
        self.layout().addWidget(self.name_label, 1)
        self.layout().addWidget(self.tag_values_format_label, 1)
        self.layout().addWidget(self.indexed_label, 0)
        self.on_update_language()
        self.on_update_settings()

    @property
    def dpi(self):
        screen = self.screen()
        return screen.physicalDotsPerInch() / (
            screen.devicePixelRatio()
            if settings.app_scale_sizes_by_device_pixel_ratio
            else 1.0
        )

    def on_update_language(self):
        self.name_label.setText(tr("Name"))
        self.tag_values_format_label.setText(tr("Tag Values Format"))
        self.indexed_label.setText(tr("Indexed"))
        self.name_label.setAlignment(
            language.alignment | Qt.AlignmentFlag.AlignBottom,
        )
        self.tag_values_format_label.setAlignment(
            language.alignment | Qt.AlignmentFlag.AlignBottom,
        )
        self.indexed_label.setAlignment(
            language.alignment | Qt.AlignmentFlag.AlignBottom,
        )
        self.update()

    def on_update_settings(self):
        content_margin = int(
            round(settings.app_layout_content_margin * self.dpi)
        )
        if language.direction == settings.LanguageDirection.RIGHT_TO_LEFT:
            self.layout().setContentsMargins(
                0,
                0,
                int(
                    round(
                        (
                            (
                                content_margin
                                + 2
                                + settings.app_scroll_trough_thickness
                                * self.dpi
                            )
                        )
                    )
                ),
                0,
            )
        else:
            self.layout().setContentsMargins(
                content_margin,
                0,
                0,
                0,
            )
        spacing = int(round(settings.app_layout_spacing * self.dpi))
        self.layout().setSpacing(spacing)
        self.update()


class TagListEdit(QWidget):
    def __init__(self, window):
        super().__init__()
        self.window = window
        self.header = window.tag_list_header
        self.setLayout(QVBoxLayout())
        self.layout().setSpacing(0)
        self.block_add_row = False
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

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.on_resize()

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
            row = TagEdit(self.window, self)
            row.set_row_data(data)
            row.on_focus_range_change = self.focus_range_change
            self.layout().insertWidget(self.num_rows, row)
        self.update_height()

    def get_row_data(self):
        row_data = []
        for i in range(self.num_rows):
            row = self.layout().itemAt(i).widget()
            row_data.append(row.get_row_data())
        return row_data

    def tag_name_list(self):
        return [
            self.layout().itemAt(i).widget().tag_name_line_edit.text()
            for i in range(self.num_rows)
        ]

    def make_default_tag_data(self):
        return None, "", False, ""

    def append_row(self, row_data):
        return self.insert_row(self.num_rows, row_data)

    def append_empty_row(self):
        self.insert_row(self.num_rows, self.make_default_tag_data())

    def insert_row(self, index, row_data):
        if self.block_add_row:
            return
        row = TagEdit(self.window, self)
        row.set_row_data(row_data)
        row.on_focus_range_change = self.focus_range_change
        self.layout().insertWidget(index, row)
        row.tag_name_line_edit.setFocus()
        return row

    def insert_empty_row(self, index):
        self.insert_row(index, self.make_default_tag_data())

    def focus_range_change(self, y_min, y_max):
        y_min = y_min + self.y()
        y_max = y_max + self.y()
        self.on_focus_range_change(y_min, y_max)

    def update_height(self):
        content_margin = int(
            round(settings.app_layout_content_margin * self.dpi)
        )
        row_spacing = int(
            round(settings.app_layout_spacing_between_rows * self.dpi)
        )
        rows = [self.layout().itemAt(i).widget() for i in range(self.num_rows)]
        row_height_sum = 0
        for row in rows:
            row_height_sum = row_height_sum + row.height()
        self.setFixedHeight(
            row_height_sum + row_spacing * (len(rows) - 1) + 2 * content_margin
        )
        self.on_resize()

    def on_undo(self):
        self.window.undo_redo.undo()

    def on_redo(self):
        self.window.undo_redo.redo()

    def on_add_tag(self):
        layout = self.layout()

        def redo():
            self.insert_empty_row(self.num_rows)
            self.update_height()

        def undo():
            bottom_index = self.num_rows - 1
            layout.takeAt(bottom_index).widget().deleteLater()
            try:
                layout.itemAt(
                    bottom_index - 1,
                ).widget().layout().itemAt(0).widget().setFocus()
            except AttributeError:
                pass
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


class TagEdit(QWidget):
    def __init__(self, window, rows):
        super().__init__()
        self.window = window
        self.rows = rows
        self.rows_layout = rows.layout()
        self.tag_id = None
        self.setLayout(QHBoxLayout())
        self.tag_name_line_edit = TagLineEdit(window)
        self.tag_values_format_line_edit = TagLineEdit(window)
        self.indexed_check_box = UndoableCheckBox(window)
        self.layout().addWidget(self.tag_name_line_edit)
        self.layout().addWidget(self.tag_values_format_line_edit)
        self.layout().addWidget(self.indexed_check_box)
        self.on_focus_range_change = lambda x, y: None
        self.on_geometry_change = lambda x: None
        self.on_update_settings()

    @property
    def dpi(self):
        screen = self.screen()
        return screen.physicalDotsPerInch() / (
            screen.devicePixelRatio()
            if settings.app_scale_sizes_by_device_pixel_ratio
            else 1.0
        )

    def moveEvent(self, event):
        self.on_geometry_change(self)

    def resizeEvent(self, event):
        self.on_geometry_change(self)

    def set_row_data(self, row_data):
        self.tag_id, tag_name, indexed, tag_values_format = row_data
        self.tag_name_line_edit.setText(tag_name)
        self.tag_values_format_line_edit.setText(tag_values_format)
        self.indexed_check_box.setChecked(indexed)
        self.tag_name_line_edit.on_focus_range_change = self.focus_range_change
        self.tag_values_format_line_edit.on_focus_range_change = (
            self.focus_range_change
        )

    def get_row_data(self):
        return (
            self.tag_id,
            self.tag_name_line_edit.text(),
            self.indexed_check_box.isChecked(),
            self.tag_values_format_line_edit.text(),
        )

    def set_focus_down_creating_new_row_if_at_bottom(self):
        layout = self.rows.layout()
        focus_index = layout.indexOf(self) + 1
        if focus_index == self.rows.num_rows:
            self.rows.append_empty_row()
        self.transfer_focus_to(layout.itemAt(focus_index).widget())

    def transfer_focus_to(self, other):
        if self.tag_name_line_edit.hasFocus():
            other.tag_name_line_edit.setFocus()
        elif self.tag_values_format_line_edit.hasFocus():
            other.tag_values_format_line_edit.setFocus()
        elif self.indexed_check_box.hasFocus():
            other.indexed_check_box.setFocus()

    def set_focus_up(self):
        layout = self.rows.layout()
        self.transfer_focus_to(
            layout.itemAt(
                max(layout.indexOf(self) - 1, 0),
            ).widget()
        )

    def set_focus_down(self):
        layout = self.rows.layout()
        self.transfer_focus_to(
            layout.itemAt(
                min(layout.indexOf(self) + 1, self.rows.num_rows - 1),
            ).widget()
        )

    def set_focus_left(self):
        if self.tag_values_format_line_edit.hasFocus():
            self.tag_name_line_edit.setFocus()
        elif self.tag_name_line_edit.hasFocus():
            self.set_focus_right()
            self.set_focus_up()

    def set_focus_right(self):
        if self.tag_name_line_edit.hasFocus():
            self.tag_values_format_line_edit.setFocus()
        elif self.tag_values_format_line_edit.hasFocus():
            self.set_focus_left()
            self.set_focus_down()

    def focus_range_change(self, y_min, y_max):
        y_min = y_min + self.y()
        y_max = y_max + self.y()
        self.on_focus_range_change(y_min, y_max)

    def on_duplicate(self):
        parent = self.parent()
        layout = parent.layout()
        index = layout.indexOf(self)
        tag_id, tag_name, indexed, tag_values_format = self.get_row_data()
        row_data = (None, tag_name, indexed, tag_values_format)

        def redo():
            row = parent.insert_row(index + 1, row_data)
            row.tag_name_line_edit.selectAll()
            parent.update_height()

        def undo():
            layout.takeAt(index + 1).widget().deleteLater()
            layout.itemAt(
                index,
            ).widget().tag_name_line_edit.setFocus()
            parent.update_height()

        self.window.undo_redo.do(undo, redo)

    def on_add_above(self):
        parent = self.parent()
        layout = parent.layout()
        index = layout.indexOf(self)

        def redo():
            parent.insert_empty_row(index)
            parent.update_height()

        def undo():
            layout.takeAt(index).widget().deleteLater()
            try:
                layout.itemAt(
                    index,
                ).widget().layout().itemAt(0).widget().setFocus()
            except AttributeError:
                pass
            parent.update_height()

        self.window.undo_redo.do(undo, redo)

    def on_add_below(self):
        parent = self.parent()
        layout = parent.layout()
        index = layout.indexOf(self)

        def redo():
            parent.insert_empty_row(index + 1)
            parent.update_height()

        def undo():
            layout.takeAt(index + 1).widget().deleteLater()
            try:
                layout.itemAt(
                    index,
                ).widget().layout().itemAt(0).widget().setFocus()
            except AttributeError:
                pass
            parent.update_height()

        self.window.undo_redo.do(undo, redo)

    def on_move_up(self):
        parent = self.parent()
        layout = parent.layout()
        index = layout.indexOf(self)
        if index == 0:
            return

        def redo():
            layout.insertWidget(index - 1, layout.takeAt(index).widget())

        def undo():
            layout.insertWidget(index, layout.takeAt(index - 1).widget())

        self.window.undo_redo.do(undo, redo)

    def on_move_down(self):
        parent = self.parent()
        layout = parent.layout()
        index = layout.indexOf(self)
        if index == parent.num_rows - 1:
            return

        def redo():
            layout.insertWidget(index + 1, layout.takeAt(index).widget())

        def undo():
            layout.insertWidget(index, layout.takeAt(index + 1).widget())

        self.window.undo_redo.do(undo, redo)

    def on_move_to_top(self):
        parent = self.parent()
        layout = parent.layout()
        index = layout.indexOf(self)
        if index == 0:
            return

        def redo():
            layout.insertWidget(0, layout.takeAt(index).widget())

        def undo():
            layout.insertWidget(index, layout.takeAt(0).widget())

        self.window.undo_redo.do(undo, redo)

    def on_move_to_bottom(self):
        parent = self.parent()
        layout = parent.layout()
        index = layout.indexOf(self)
        bottom_index = parent.num_rows - 1
        if index == bottom_index:
            return

        def redo():
            layout.insertWidget(bottom_index, layout.takeAt(index).widget())

        def undo():
            layout.insertWidget(index, layout.takeAt(bottom_index).widget())

        self.window.undo_redo.do(undo, redo)

    def on_delete(self):
        parent = self.parent()
        layout = parent.layout()
        index = layout.indexOf(self)
        row_data = self.get_row_data()

        def redo():
            layout.takeAt(index).widget().deleteLater()
            try:
                self.rows_layout.itemAt(
                    min(index, self.rows.num_rows - 1)
                ).widget().tag_name_line_edit.setFocus()
            except AttributeError:
                parent.frame.setFocus()
            parent.update_height()

        def undo():
            parent.insert_row(index, row_data)
            parent.update_height()

        self.window.undo_redo.do(undo, redo)

    def on_update_settings(self):
        self.layout().setContentsMargins(
            0,
            0,
            settings.app_scroll_trough_thickness * self.dpi,
            0,
        )
        spacing = int(round(settings.app_layout_spacing * self.dpi))
        self.layout().setSpacing(spacing)
        self.setFixedHeight(utils.calculate_default_height(QLineEdit))
        self.update()


class TagLineEdit(line_edit.LineEdit):
    def __init__(self, window):
        super().__init__(window)
        self.window = window
        self.context_menu = menus.TagEditOrFormEditContextMenu(window)
        self.on_focus_range_change = lambda x, y: None
        self.pre_edit_selection = None
        self.pre_edit_text = ""
        self.prev_key_arrow = False
        self.space_between_rows = 0
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

    def focusInEvent(self, event):
        super().focusInEvent(event)
        y_min = self.y()
        y_max = y_min + self.height()
        y_min = y_min - self.space_between_rows
        y_max = y_max + self.space_between_rows
        utils.run_after_current_event(
            lambda: self.on_focus_range_change(y_min, y_max),
        )

    def focusNextPrevChild(self, _next):
        return False

    def focusOutEvent(self, event):
        super().focusOutEvent(event)
        self.add_text_changes_to_undo_redo()

    def keyPressEvent(self, event):
        key = event.key()
        if key == Qt.Key.Key_Return:
            self.parent().set_focus_down_creating_new_row_if_at_bottom()
        elif key == Qt.Key.Key_Up:
            self.parent().set_focus_up()
        elif key == Qt.Key.Key_Down:
            self.parent().set_focus_down()
        elif key == Qt.Key.Key_Backtab:
            self.parent().set_focus_left()
        elif key == Qt.Key.Key_Tab:
            self.parent().set_focus_right()
        else:
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

    def add_text_changes_to_undo_redo(self):
        pre_edit_text = self.pre_edit_text
        post_edit_text = self.text()
        if pre_edit_text == post_edit_text:
            return
        parent_ = self.parent()
        parent_parent = parent_.parent()
        index = parent_parent.layout().indexOf(parent_)
        sub_index = parent_.layout().indexOf(self)
        pre_edit_selection = self.pre_edit_selection
        post_edit_selection = self.selection()

        def redo():
            parent = parent_parent.layout().itemAt(index).widget()
            widget = parent.layout().itemAt(sub_index).widget()
            widget.setText(post_edit_text)
            widget.setSelection(*post_edit_selection)

        def undo():
            parent = parent_parent.layout().itemAt(index).widget()
            widget = parent.layout().itemAt(sub_index).widget()
            widget.setText(pre_edit_text)
            widget.setSelection(*pre_edit_selection)

        self.window.undo_redo.do(undo, redo)

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
        parent_ = self.parent()
        parent_parent = parent_.parent()
        index = parent_parent.layout().indexOf(parent_)
        sub_index = parent_.layout().indexOf(self)
        pre_cut_text = self.text()
        selection = self.selection()

        def redo():
            parent = parent_parent.layout().itemAt(index).widget()
            widget = parent.layout().itemAt(sub_index).widget()
            widget.setSelection(*selection)
            widget.cut()

        def undo():
            parent = parent_parent.layout().itemAt(index).widget()
            widget = parent.layout().itemAt(sub_index).widget()
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
        parent_ = self.parent()
        parent_parent = parent_.parent()
        index = parent_parent.layout().indexOf(parent_)
        sub_index = parent_.layout().indexOf(self)
        pre_paste_text = self.text()
        selection = self.selection()

        def redo():
            parent = parent_parent.layout().itemAt(index).widget()
            widget = parent.layout().itemAt(sub_index).widget()
            widget.setSelection(*selection)
            widget.insert(text)

        def undo():
            parent = parent_parent.layout().itemAt(index).widget()
            widget = parent.layout().itemAt(sub_index).widget()
            widget.setText(pre_paste_text)
            widget.setSelection(*selection)

        self.window.undo_redo.do(undo, redo)

    def on_select_all(self):
        self.add_text_changes_to_undo_redo()
        self.selectAll()

    def on_update_settings(self):
        self.space_between_rows = (
            settings.app_layout_spacing_between_rows * self.dpi
        )
        self.setFixedHeight(utils.calculate_default_height(QLineEdit))
        self.update()


class _UndoableCheckBox(QCheckBox):
    def __init__(self, window):
        super().__init__()
        self.window = window

    def mouseReleaseEvent(self, event):
        super().mouseReleaseEvent(event)
        if event.button() == Qt.MouseButton.LeftButton:
            parent_ = self.parent().parent()
            parent_parent = parent_.parent()
            index = parent_parent.layout().indexOf(parent_)
            state = self.checkState()
            if state == Qt.CheckState.Unchecked:
                prev_state = Qt.CheckState.Checked
            else:
                prev_state = Qt.CheckState.Unchecked

            def redo():
                parent = parent_parent.layout().itemAt(index).widget()
                widget = parent.indexed_check_box
                widget.setCheckState(state)

            def undo():
                parent = parent_parent.layout().itemAt(index).widget()
                widget = parent.indexed_check_box
                widget.setCheckState(prev_state)

            self.window.undo_redo.do(undo, redo)


class UndoableCheckBox(QWidget):
    def __init__(self, window):
        super().__init__()
        self.check_box = _UndoableCheckBox(window)
        self.setLayout(QVBoxLayout())
        self.layout().addWidget(self.check_box)
        self.layout().setContentsMargins(0, 0, 0, 0)

    def __getattr__(self, name):
        return getattr(self.check_box, name)
