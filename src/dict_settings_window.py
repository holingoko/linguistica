import os

from src import app_info
from src import buttons
from src import combo_box
from src import dict_database
from src import dict_database_file
from src import dict_entry_window
from src import dict_format
from src import dict_re
from src import dict_template_entry_window
from src import dict_template_window
from src import frame
from src import label
from src import line_edit
from src import menus
from src import messages
from src import scroll_area
from src import settings
from src import state
from src import tag_list_edit
from src import undo_redo
from src import window
from src.language import tr
from src.qt import *


class NoOpDictComboBox:
    def set_name(self, _):
        return


class DictSettingsWindow(window.Window):
    def __init__(self):
        super().__init__()
        self.undo_redo = undo_redo.UndoRedo()
        self.dict_label = label.SelectableLabel(self)
        self.dict_combo_box = combo_box.DictComboBox(
            self.on_dict_changed_pending
        )
        self.entry_format_label = label.SelectableLabel(self)
        self.entry_format_line_edit = line_edit.LineEdit(self)
        self.entry_joiner_label = label.SelectableLabel(self)
        self.entry_joiner_line_edit = line_edit.LineEdit(self)
        self.tags_label = label.SelectableLabel(self)
        self.tag_list_header = tag_list_edit.TagListHeader()
        self.tag_list_edit = tag_list_edit.TagListEdit(self)
        self.tag_scroll_area = scroll_area.ScrollArea(self.tag_list_edit)
        self.tag_frame = frame.Frame(
            self.tag_scroll_area,
            menus.TagFrameContextMenu(self),
        )
        self.buttons = QWidget()
        self.close_button = buttons.PushButton(self.on_close)
        self.save_and_close_button = buttons.PushButton(self.on_save)
        self.buttons.setLayout(QHBoxLayout())
        self.buttons.layout().addStretch()
        self.buttons.layout().addWidget(self.close_button)
        self.buttons.layout().addWidget(self.save_and_close_button)
        self.buttons.layout().setContentsMargins(0, 0, 0, 0)
        self.setLayout(QVBoxLayout())
        self.layout().setMenuBar(menus.DictMenuBar(self))
        self.layout().addWidget(self.dict_label)
        self.layout().addWidget(self.dict_combo_box)
        self.layout().addWidget(self.entry_format_label)
        self.layout().addWidget(self.entry_format_line_edit)
        self.layout().addWidget(self.entry_joiner_label)
        self.layout().addWidget(self.entry_joiner_line_edit)
        self.layout().addWidget(self.tags_label)
        self.layout().addWidget(self.tag_list_header)
        self.layout().addWidget(self.tag_frame)
        self.layout().addWidget(self.buttons)
        self.db = None
        self.name = ""
        self.saved_data = self.get_data()
        self.dict_combo_box.set_name(
            settings.dict_default or state.last_selected_dict
        )
        self.initialize_geometry()
        self.on_update_language()
        self.on_update_settings()

    @property
    def default_width(self):
        return settings.dict_settings_window_default_width

    @property
    def default_height(self):
        return settings.dict_settings_window_default_height

    def closeEvent(self, event):
        def continue_():
            window.Window.closeEvent(self, event)

        def save_and_close():
            if self.on_save():
                continue_()
            else:
                self.raise_()

        if self.get_data() == self.saved_data:
            continue_()
        else:
            event.ignore()
            messages.UnsavedDictionaryOnCloseWarningMessage(
                self.name,
                continue_,
                save_and_close,
            ).show()

    def dropEvent(self, event):
        for url in event.mimeData().urls():
            path = url.path()[1:]
            if os.path.exists(path):
                dict_database_file.on_import_dict_database_file(
                    os.path.normpath(path),
                    on_success=self.dict_combo_box.set_name,
                )

    def get_data(self):
        return (
            self.entry_format_line_edit.text(),
            self.entry_joiner_line_edit.text(),
            self.tag_list_edit.get_row_data(),
        )

    def on_activate(self):
        super().on_activate()
        self.dict_combo_box.update_items()

    def on_dict_changed_pending(self, name):
        if self.name == name:
            return
        if self.get_data() == self.saved_data:
            self.on_dict_changed(name)
        else:

            def on_save_and_switch():
                if self.on_save(close_if_success=False):
                    self.on_dict_changed(name)

            def on_cancel():
                self.dict_combo_box.setCurrentText(self.name)

            messages.UnsavedDictionaryOnChangeWarningMessage(
                self.name,
                lambda: self.on_dict_changed(name),
                on_save_and_switch,
                on_cancel,
            ).show()

    def on_dict_changed(self, name):
        self.name = name
        path = os.path.join(settings.dict_dir, f"{name}{app_info.db_ext}")
        if not os.path.exists(path):
            self.db = None
            self.tag_list_edit.set_row_data([])
            self.entry_format_line_edit.setText("")
            self.entry_joiner_line_edit.setText("")
            self.tag_list_edit.block_add_row = True
            self.entry_format_line_edit.setReadOnly(True)
            self.entry_joiner_line_edit.setReadOnly(True)
        else:
            self.db = dict_database.DictDatabase(path)
            tags = self.db.tags.get_all_tags()
            self.tag_list_edit.set_row_data(tags)
            self.entry_format_line_edit.setText(
                self.db.info.get_entry_format()
            )
            self.entry_joiner_line_edit.setText(
                self.db.info.get_entry_joiner()
            )
            self.tag_list_edit.block_add_row = False
            self.entry_format_line_edit.setReadOnly(False)
            self.entry_joiner_line_edit.setReadOnly(False)
        self.saved_data = self.get_data()

    def on_close(self):
        self.close()

    def on_warning(
        self,
        warnings_ignored,
        warning_class,
        *warning_args,
    ):
        def continue_():
            warnings_ignored_ = warnings_ignored + (warning_class,)
            self.on_save(warnings_ignored=warnings_ignored_)

        warning = warning_class(
            *warning_args,
            continue_,
        )
        if warning.show.__name__ == "<lambda>":
            warnings_ignored = warnings_ignored + (warning_class,)
        if warning_class not in warnings_ignored:
            warning.show()
            return False
        warning.close()
        return True

    def on_save(
        self,
        close_if_success=True,
        warnings_ignored=(),
    ):
        for window_ in self.windows:
            if window_.__class__ in {
                dict_entry_window.DictEntryWindow,
                dict_template_entry_window.DictTemplateEntryWindow,
                dict_template_window.DictTemplateWindow,
            }:
                messages.CannotSaveDictionarySettingsWhileEntryOrTemplateOpenErrorMessage().show()
                return False
        tag_data = self.tag_list_edit.get_row_data()
        tag_names = [i[1] for i in tag_data]
        if not tag_names:
            messages.NoTagsErrorMessage().show()
            return False
        tag_names_set = set(tag_names)
        if len(tag_names) > len(tag_names_set):
            messages.DuplicateTagNameErrorMessage().show()
            return False
        invalid_tag_names = []
        empty_tag_values_format_tag_names = []
        non_arbitrary_tag_values_format_tag_names = []
        has_indexed_tags = False
        for _, tag_name, indexed, tag_values_format in tag_data:
            has_indexed_tags = has_indexed_tags or indexed
            if not dict_re.check_tag_valid(tag_name):
                invalid_tag_names.append(tag_name)
            if not tag_values_format:
                empty_tag_values_format_tag_names.append(tag_name)
            elif not "..." in tag_values_format:
                non_arbitrary_tag_values_format_tag_names.append(tag_name)
        if invalid_tag_names:
            messages.InvalidTagErrorMessage(invalid_tag_names).show()
            return False
        if not has_indexed_tags:
            if not self.on_warning(
                warnings_ignored,
                messages.NoIndexedTagsWarningMessage,
            ):
                return False
        if empty_tag_values_format_tag_names:
            if not self.on_warning(
                warnings_ignored,
                messages.EmptyTagValuesFormatWarningMessage,
                empty_tag_values_format_tag_names,
            ):
                return False
        if non_arbitrary_tag_values_format_tag_names:
            if not self.on_warning(
                warnings_ignored,
                messages.NonArbitraryTagValuesFormatWarningMessage,
                non_arbitrary_tag_values_format_tag_names,
            ):
                return False
        prev_tag_data = self.db.tags.get_all_tags()
        prev_tag_id_to_name = {i[0]: i[1] for i in prev_tag_data}
        prev_tag_ids = set(prev_tag_id_to_name.keys())
        tag_ids = {i[0] for i in tag_data}
        potentially_deleted_tag_ids = prev_tag_ids - tag_ids
        potentially_deleted_tag_names = {
            prev_tag_id_to_name[i] for i in potentially_deleted_tag_ids
        }
        deleted_tag_names = potentially_deleted_tag_names - tag_names_set
        prev_tag_name_to_id = {i[1]: i[0] for i in prev_tag_data}
        if deleted_tag_names:
            if not self.on_warning(
                warnings_ignored,
                messages.DeletedTagsWarningMessage,
                deleted_tag_names,
            ):
                return False
            for tag_name in deleted_tag_names:
                tag_id = prev_tag_name_to_id[tag_name]
                self.db.tags.delete_tag(tag_id)
                self.db.tag_rows.delete_rows_for_tag(tag_id)
        entry_format = self.entry_format_line_edit.text()
        entry_format_tags = dict_format.Formatter.entry_format_tags(
            entry_format
        )
        missing_tags = entry_format_tags - tag_names_set
        if missing_tags:
            if not self.on_warning(
                warnings_ignored,
                messages.MissingTagsWarningMessage,
                missing_tags,
            ):
                return False
        self.db.info.set_entry_format(entry_format)
        self.db.info.set_entry_joiner(self.entry_joiner_line_edit.text())
        for order, (
            tag_id,
            tag_name,
            indexed,
            tag_values_format,
        ) in enumerate(self.tag_list_edit.get_row_data()):
            if tag_id is None:
                tag_id = prev_tag_name_to_id.get(tag_name, None)
            if tag_id is not None:
                self.db.tags.update_tag(
                    tag_id,
                    tag_name,
                    indexed,
                    tag_values_format,
                    order,
                )
            else:
                self.db.tags.create_tag(
                    tag_name,
                    indexed,
                    tag_values_format,
                    order,
                )
        self.saved_data = self.get_data()
        self.db.on_change()
        if close_if_success:
            self.close()
        return True

    def on_update_language(self):
        self.setWindowTitle(tr("Dictionary Settings"))
        self.dict_label.setText(tr("Dictionary:"))
        self.entry_format_label.setText(tr("Entry Format:"))
        self.entry_joiner_label.setText(tr("Entry Joiner:"))
        self.tags_label.setText(tr("Tags:"))
        self.close_button.setText(tr("Close"))
        self.save_and_close_button.setText(tr("Save And Close"))
        self.update()

    def on_update_settings(self):
        self.buttons.layout().setSpacing(
            int(round(settings.app_button_spacing * self.dpi))
        )
        self.update()
