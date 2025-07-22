from src import form_list_edit
from src import frame
from src import menus
from src import messages
from src import scroll_area
from src import undo_redo
from src import window
from src.qt import *


class FormListEditWindow(window.Window):
    def __init__(self, db, entry_id=None, template=False):
        super().__init__()
        self.db = db
        self.entry_id = entry_id
        self.is_template = template
        self.setLayout(QVBoxLayout())
        self.layout().setMenuBar(menus.DictMenuBar(self))
        self.undo_redo = undo_redo.UndoRedo()
        self.form_list_edit = form_list_edit.FormListEdit(self)
        self.form_scroll_area = scroll_area.ScrollArea(self.form_list_edit)
        self.form_frame = frame.Frame(
            self.form_scroll_area,
            menus.TagEditOrFormEditContextMenu(self),
        )
        tags = self.db.tags.get_all_tags()
        tag_ids_and_names = [(row[0], row[1]) for row in tags]
        self.indexed = {row[0]: row[2] for row in tags}
        self.empty_form_data = [
            (tag_id, tag_name, [""]) for tag_id, tag_name in tag_ids_and_names
        ]
        if entry_id is None:
            form_row_data = [(None, self.empty_form_data)]
            self.form_ids_at_init = set()
        else:
            form_row_data = []
            form_ids = self.db.forms.get_forms_for_entry(entry_id)
            self.form_ids_at_init = set(form_ids)
            for form_id in form_ids:
                tag_row_data = []
                tag_values = self.db.tag_rows.get_tag_values_for_form(form_id)
                for tag_id, tag_name in tag_ids_and_names:
                    try:
                        tag_values_for_tag_id = tag_values[tag_id]
                    except KeyError:
                        tag_values_for_tag_id = []
                    tag_row_data.append(
                        (
                            tag_id,
                            tag_name,
                            tag_values_for_tag_id,
                        )
                    )
                form_row_data.append((form_id, tag_row_data))
            if not form_row_data:
                form_row_data = [(None, self.empty_form_data)]
        self.name_line_edit_saved_text = ""
        self.form_list_edit_saved_row_data = form_row_data
        self.form_list_edit.set_row_data(form_row_data)
        self.form_list_edit.empty_form_data = self.empty_form_data
        self.form_list_edit.on_data_change = self.on_data_change

    @property
    def no_unsaved_changes(self):
        return (
            self.form_list_edit.get_row_data()
            == self.form_list_edit_saved_row_data
        )

    def closeEvent(self, event):
        def continue_():
            window.Window.closeEvent(self, event)

        def save_and_close():
            if self.on_save():
                continue_()
            else:
                self.raise_()

        if self.no_unsaved_changes:
            continue_()
        else:
            event.ignore()
            if self.is_template:
                messages.UnsavedTemplateWarningMessage(
                    continue_,
                    save_and_close,
                ).show()
            else:
                messages.UnsavedEntryWarningMessage(
                    continue_,
                    save_and_close,
                ).show()

    def on_close(self):
        self.close()

    def on_save(self, close_if_success=True):
        if self.entry_id is None:
            self.entry_id = self.db.entries.create_entry()
        if self.is_template:
            self.db.entries.set_template_name(
                self.entry_id,
                self.name_line_edit.text(),
            )
        row_data = self.form_list_edit.get_row_data()
        form_ids = set()
        for order, (
            form_id,
            form_data,
        ) in enumerate(row_data):
            if form_data == self.empty_form_data:
                continue
            if form_id is None:
                form_id = self.db.forms.create_form(self.entry_id, order)
            form_ids.add(form_id)
            self.db.forms.update_form(form_id, order)
            for tag_id, _, tag_values in form_data:
                tag_values = [
                    tag_value for tag_value in tag_values if tag_value
                ] or [""]
                self.db.tag_rows.set_tag_values(
                    form_id,
                    tag_id,
                    tag_values,
                    self.indexed[tag_id],
                    self.is_template,
                )
        deleted_form_ids = set.difference(self.form_ids_at_init, form_ids)
        for form_id in deleted_form_ids:
            self.db.forms.delete_form(form_id)
            self.db.tag_rows.delete_rows_for_form(form_id)
        if self.is_template:
            self.name_line_edit_saved_text = self.name_line_edit.text()
        self.form_list_edit_saved_row_data = row_data
        if self.form_list_edit.is_empty and (
            not self.is_template or not self.name_line_edit.text()
        ):
            self.db.entries.delete_entry(self.entry_id)
        self.db.clean()
        self.db.on_change()
        if close_if_success:
            self.close()

    def add_rows(self, row_data):
        def redo():
            if self.form_list_edit.is_empty:
                self.form_list_edit.clear_layout()
            self.form_list_edit.clear_selection()
            for data in row_data:
                row = self.form_list_edit.append_row(data)
                row.selected = True
            self.form_list_edit.update_height()

        def undo():
            insertion_index = self.form_list_edit.num_rows - 1
            layout = self.form_list_edit.layout()
            for _ in range(len(row_data)):
                layout.takeAt(insertion_index).widget().deleteLater()
                insertion_index = insertion_index - 1
            if self.form_list_edit.num_rows == 0:
                self.form_list_edit.append_empty_row()
            self.form_list_edit.clear_selection()
            self.form_frame.setFocus()
            self.form_list_edit.update_height()

        self.undo_redo.do(undo, redo)
