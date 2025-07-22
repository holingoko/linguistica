from src import buttons
from src import combo_box
from src import dict_format
from src import dict_template_window
from src import form_list_edit
from src import frame
from src import label
from src import menus
from src import messages
from src import scroll_area
from src import settings
from src import undo_redo
from src import window
from src.language import tr
from src.qt import *


class DictTemplateEntryWindow(window.Window):
    def __init__(self, db, on_save_):
        super().__init__()
        self.db = db
        self.on_save_ = on_save_
        self.setLayout(QVBoxLayout())
        self.undo_redo = undo_redo.UndoRedo()
        self.template_combo_box = combo_box.TemplateComboBox(self.db)
        self.stem_label = label.SelectableLabel(self)
        self.stem_list_edit = form_list_edit.FormListEdit(
            self,
            is_single_form=True,
        )
        self.stem_scroll_area = scroll_area.ScrollArea(self.stem_list_edit)
        self.stem_frame = frame.Frame(
            self.stem_scroll_area,
            menus.TagEditOrFormEditContextMenu(self),
        )
        self.buttons = QWidget()
        self.edit_selected_template_button = buttons.PushButton(
            self.on_edit_selected_template
        )
        self.close_button = buttons.PushButton(self.on_close)
        self.add_to_entry_button = buttons.PushButton(self.on_save)
        self.buttons.setLayout(QHBoxLayout())
        self.buttons.layout().addWidget(self.edit_selected_template_button)
        self.buttons.layout().addStretch()
        self.buttons.layout().addWidget(self.close_button)
        self.buttons.layout().addWidget(self.add_to_entry_button)
        self.layout().addWidget(self.template_combo_box, 0)
        self.layout().addWidget(self.stem_label, 0)
        self.layout().addWidget(self.stem_frame, 1)
        self.layout().addWidget(self.buttons, 0)
        tags = self.db.tags.get_all_tags()
        tag_ids_and_names = [(row[0], row[1]) for row in tags]
        self.empty_form_data = (
            None,
            [
                (tag_id, tag_name, [""])
                for tag_id, tag_name in tag_ids_and_names
            ],
        )
        self.stem_list_edit.set_row_data([self.empty_form_data])
        self.initialize_geometry()
        self.on_update_language()
        self.on_update_settings()

    @property
    def default_width(self):
        return settings.dict_template_entry_window_default_width

    @property
    def default_height(self):
        return settings.dict_template_entry_window_default_height

    def on_activate(self):
        super().on_activate()
        self.template_combo_box.update_items()

    def on_edit_selected_template(self):
        entry_id = self.template_combo_box.selected_template_entry_id
        if entry_id is None:
            messages.NoTemplateSelectedErrorMessage().show()
            return
        dict_template_window.DictTemplateWindow(self.db, entry_id).show()

    def on_close(self):
        self.close()

    def on_save(self, close_if_success=True):
        entry_id = self.template_combo_box.selected_template_entry_id
        if entry_id is None:
            messages.NoTemplateSelectedErrorMessage().show()
            return
        template_forms = []
        form_ids = self.db.forms.get_forms_for_entry(entry_id)
        for form_id in form_ids:
            tag_row_data = []
            tag_values = self.db.tag_rows.get_tag_values_for_form(form_id)
            for tag_id, tag_name, _, _ in self.db.tags.get_all_tags():
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
            template_forms.append(tag_row_data)
        stem_form = self.stem_list_edit.get_row_data()[0][1]
        self.on_save_(
            dict_format.format_template(
                template_forms,
                stem_form,
            )
        )
        if close_if_success:
            self.close()

    def on_update_language(self):
        self.setWindowTitle(tr("Dictionary Template Entry"))
        self.stem_label.setText(tr("Stem:"))
        self.edit_selected_template_button.setText(
            tr("Edit Selected Template...")
        )
        self.close_button.setText(tr("Close"))
        self.add_to_entry_button.setText(tr("Add"))
        self.update()

    def on_update_settings(self):
        content_margin = int(
            round(settings.app_layout_content_margin * self.dpi)
        )
        spacing = int(round(settings.app_layout_spacing * self.dpi))
        self.layout().setContentsMargins(
            content_margin,
            content_margin,
            content_margin,
            content_margin,
        )
        self.layout().setSpacing(spacing)
        button_spacing = int(round(settings.app_button_spacing * self.dpi))
        self.buttons.layout().setContentsMargins(
            content_margin,
            0,
            content_margin,
            content_margin,
        )
        self.buttons.layout().setSpacing(button_spacing)
        self.update()
