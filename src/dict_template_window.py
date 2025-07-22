from src import buttons
from src import dict_format
from src import dict_view
from src import form_list_edit
from src import form_list_edit_window
from src import frame
from src import label
from src import line_edit
from src import menus
from src import messages
from src import scroll_area
from src import settings
from src import splitter
from src.language import tr
from src.qt import *


class DictTemplateWindow(form_list_edit_window.FormListEditWindow):
    def __init__(self, db, entry_id=None):
        for window in self.windows:
            if entry_id is not None:
                try:
                    window_db_path = window.db.path
                    window_entry_id = window.entry_id
                except AttributeError:
                    continue
                if window_db_path == db.path and window_entry_id == entry_id:
                    window.activateWindow()
                    self.show = window.raise_
                    return
        super().__init__(db, entry_id, template=True)
        self.name_label = label.SelectableLabel(self)
        self.name_line_edit = line_edit.LineEdit(self)
        self.forms_label = label.SelectableLabel(self)
        self.test_label = label.SelectableLabel(self)
        self.test_list_edit = form_list_edit.FormListEdit(
            self,
            is_single_form=True,
        )
        self.test_scroll_area = scroll_area.ScrollArea(self.test_list_edit)
        self.test_frame = frame.Frame(
            self.test_scroll_area,
            menus.TagEditOrFormEditContextMenu(self),
        )
        self.preview_label = label.SelectableLabel(self)
        self.dict_view = dict_view.DictView(db)
        self.top = QWidget()
        self.top.setLayout(QVBoxLayout())
        self.top.layout().addWidget(self.name_label)
        self.top.layout().addWidget(self.name_line_edit)
        self.form = QWidget()
        self.test = QWidget()
        self.form.setLayout(QVBoxLayout())
        self.test.setLayout(QVBoxLayout())
        self.form.layout().addWidget(self.forms_label)
        self.form.layout().addWidget(self.form_frame)
        self.test.layout().addWidget(self.test_label)
        self.test.layout().addWidget(self.test_frame)
        self.test.sizeHint = lambda: QSize(
            self.form.sizeHint().width(),
            self.form.sizeHint().height() // 2,
        )
        self.left_splitter = splitter.Splitter()
        self.left_splitter.setOrientation(Qt.Orientation.Vertical)
        self.left_splitter.addWidget(self.form)
        self.left_splitter.addWidget(self.test)
        self.right = QWidget()
        self.right.setLayout(QVBoxLayout())
        self.right.layout().addWidget(self.preview_label, 0)
        self.right.layout().addWidget(self.dict_view, 1)
        self.splitter = splitter.Splitter()
        self.splitter.setOrientation(Qt.Orientation.Horizontal)
        self.left_splitter.sizeHint = lambda: QSize(
            self.screen().size().width(), 0
        )
        self.splitter.addWidget(self.left_splitter)
        self.splitter.addWidget(self.right)
        self.buttons = QWidget()
        self.delete_button = buttons.PushButton(self.on_delete)
        self.close_button = buttons.PushButton(self.on_close)
        self.save_button = buttons.PushButton(self.on_save)
        self.buttons.setLayout(QHBoxLayout())
        self.buttons.layout().addWidget(self.delete_button)
        self.buttons.layout().addStretch()
        self.buttons.layout().addWidget(self.close_button)
        self.buttons.layout().addWidget(self.save_button)
        self.layout().addWidget(self.top, 0)
        self.layout().addWidget(self.splitter, 1)
        self.layout().addWidget(self.buttons, 0)
        self.name_line_edit.setText(
            self.db.entries.get_template_name(entry_id)
        )
        self.name_line_edit_saved_text = self.name_line_edit.text()
        self.test_list_edit.set_row_data([(None, self.empty_form_data)])
        self.test_list_edit.on_data_change = self.on_data_change
        self.test_list_edit.on_data_change = self.on_data_change
        self.initialize_geometry()
        self.on_data_change()
        self.on_update_language()
        self.on_update_settings()

    @property
    def default_width(self):
        return settings.dict_template_window_default_width

    @property
    def default_height(self):
        return settings.dict_template_window_default_height

    @property
    def no_unsaved_changes(self):
        return (
            super().no_unsaved_changes
            and self.name_line_edit.text() == self.name_line_edit_saved_text
        )

    def on_data_change(self):
        template_forms = [i[1] for i in self.form_list_edit.get_row_data()]
        test_form = self.test_list_edit.get_row_data()[0][1]
        self.dict_view.update_entries(
            dict_format.format_template(
                template_forms,
                test_form,
            )
        )

    def on_delete(self):
        def continue_():
            self.form_list_edit.clear_layout()
            self.name_line_edit.setText("")
            self.on_save()

        messages.DeleteTemplateWarningMessage(continue_).show()

    def on_update_language(self):
        self.setWindowTitle(tr("Dictionary Template"))
        self.name_label.setText(tr("Name:"))
        self.forms_label.setText(tr("Forms:"))
        self.test_label.setText(tr("Test:"))
        self.preview_label.setText(tr("Preview:"))
        self.delete_button.setText(tr("Delete"))
        self.close_button.setText(tr("Close"))
        self.save_button.setText(tr("Save"))
        self.update()

    def on_update_settings(self):
        content_margin = int(
            round(settings.app_layout_content_margin * self.dpi)
        )
        spacing = int(round(settings.app_layout_spacing * self.dpi))
        handle_width = int(
            round(settings.app_layout_splitter_handle_width * self.dpi)
        )
        self.layout().setContentsMargins(
            content_margin,
            content_margin,
            content_margin,
            content_margin,
        )
        self.top.layout().setContentsMargins(
            content_margin,
            content_margin,
            content_margin,
            0,
        )
        self.form.layout().setContentsMargins(0, 0, 0, 0)
        self.test.layout().setContentsMargins(0, 0, 0, 0)
        self.left_splitter.setContentsMargins(
            content_margin,
            content_margin,
            content_margin,
            content_margin,
        )
        self.right.layout().setContentsMargins(
            content_margin - handle_width,
            content_margin,
            content_margin,
            content_margin,
        )
        self.top.layout().setSpacing(spacing)
        self.form.layout().setSpacing(spacing)
        self.test.layout().setSpacing(spacing)
        self.right.layout().setSpacing(spacing)
        popup_height = int(round(settings.dict_popup_rect_height * self.dpi))
        popup_width = int(round(settings.dict_popup_rect_width * self.dpi))
        popup_radius = int(round(settings.dict_popup_rect_radius * self.dpi))
        width = popup_width - popup_radius
        height = popup_height - popup_radius
        self.dict_view.setMinimumWidth(width)
        self.dict_view.setMinimumHeight(height)
        self.right.setVisible(settings.dict_show_preview_for_entries)
        button_spacing = int(round(settings.app_button_spacing * self.dpi))
        self.buttons.layout().setContentsMargins(
            content_margin,
            0,
            content_margin,
            content_margin,
        )
        self.buttons.layout().setSpacing(button_spacing)
        self.update()
