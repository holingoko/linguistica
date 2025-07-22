from src import buttons
from src import dict_template_entry_window
from src import dict_view
from src import form_list_edit_window
from src import label
from src import settings
from src import splitter
from src.language import tr
from src.qt import *


class DictEntryWindow(form_list_edit_window.FormListEditWindow):
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
        super().__init__(db, entry_id)
        self.forms_label = label.SelectableLabel(self)
        self.preview_label = label.SelectableLabel(self)
        self.dict_view = dict_view.DictView(db)
        self.left = QWidget()
        self.left.setLayout(QVBoxLayout())
        self.left.layout().addWidget(self.forms_label)
        self.left.layout().addWidget(self.form_frame)
        self.right = QWidget()
        self.right.setLayout(QVBoxLayout())
        self.right.layout().addWidget(self.preview_label, 0)
        self.right.layout().addWidget(self.dict_view, 1)
        self.splitter = splitter.Splitter()
        self.splitter.setOrientation(Qt.Orientation.Horizontal)
        self.left.sizeHint = lambda: QSize(self.screen().size().width(), 0)
        self.splitter.addWidget(self.left)
        self.splitter.addWidget(self.right)
        self.buttons = QWidget()
        self.add_from_template_button = buttons.PushButton(
            self.on_add_from_template,
        )
        self.close_button = buttons.PushButton(self.on_close)
        self.save_button = buttons.PushButton(self.on_save)
        self.buttons.setLayout(QHBoxLayout())
        self.buttons.layout().addWidget(self.add_from_template_button)
        self.buttons.layout().addStretch()
        self.buttons.layout().addWidget(self.close_button)
        self.buttons.layout().addWidget(self.save_button)
        self.layout().addWidget(self.splitter, 1)
        self.layout().addWidget(self.buttons, 0)
        self.initialize_geometry()
        self.on_data_change()
        self.on_update_language()
        self.on_update_settings()

    @property
    def default_width(self):
        return settings.dict_entry_window_default_width

    @property
    def default_height(self):
        return settings.dict_entry_window_default_height

    def on_data_change(self):
        self.dict_view.update_entries(
            [i[1] for i in self.form_list_edit.get_row_data()]
        )

    def on_add_from_template(self):
        window = dict_template_entry_window.DictTemplateEntryWindow(
            self.db,
            self.on_dict_template_entry_window_save,
        )
        self.add_child_window(window)
        window.show()
        return

    def on_dict_template_entry_window_save(self, forms):
        self.add_rows(forms)

    def on_update_language(self):
        self.setWindowTitle(tr("Dictionary Entry"))
        self.forms_label.setText(tr("Forms:"))
        self.add_from_template_button.setText(tr("Add From Template..."))
        self.preview_label.setText(tr("Preview:"))
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
        self.left.layout().setContentsMargins(
            content_margin,
            content_margin,
            content_margin - handle_width,
            content_margin,
        )
        self.right.layout().setContentsMargins(
            content_margin - handle_width,
            content_margin,
            content_margin,
            content_margin,
        )
        self.left.layout().setSpacing(spacing)
        self.right.layout().setSpacing(spacing)
        popup_height = int(round(settings.dict_popup_rect_height * self.dpi))
        popup_width = int(round(settings.dict_popup_rect_width * self.dpi))
        popup_radius = int(round(settings.dict_popup_rect_radius * self.dpi))
        width = popup_width - popup_radius
        height = popup_height - popup_radius
        self.dict_view.setMinimumWidth(width)
        self.dict_view.setMinimumHeight(height)
        self.right.setVisible(settings.dict_show_preview_for_entries)
        self.buttons.layout().setContentsMargins(
            content_margin,
            0,
            content_margin,
            content_margin,
        )
        self.buttons.layout().setSpacing(
            int(round(settings.app_button_spacing * self.dpi))
        )
        self.update()
