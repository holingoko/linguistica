import os

from src import app_info
from src import combo_box
from src import dict_database
from src import dict_database_file
from src import dict_view
from src import label
from src import line_edit
from src import menus
from src import settings
from src import state
from src import window
from src.language import tr
from src.qt import *


class DictWindow(window.Window):
    def __init__(self):
        super().__init__()
        self.db = None
        self.dict_view = dict_view.DictView()
        self.dictionary_label = label.SelectableLabel(self)
        self.dict_combo_box = combo_box.DictComboBox(self.on_dict_changed)
        self.dict_combo_box.set_name(
            settings.dict_default or state.last_selected_dict
        )
        self.dictionary = QWidget()
        self.dictionary.setLayout(QVBoxLayout())
        self.dictionary.layout().addWidget(self.dictionary_label)
        self.dictionary.layout().addWidget(self.dict_combo_box)
        self.dictionary.layout().setContentsMargins(0, 0, 0, 0)
        self.tags_label = label.SelectableLabel(self)
        self.tags_combo = combo_box.ComboBox(self.tag_populate_fn)
        self.tags_combo.currentTextChanged.connect(
            lambda _: self.on_search(self.search_line_edit.text())
        )
        self.tags = QWidget()
        self.tags.setLayout(QVBoxLayout())
        self.tags.layout().addWidget(self.tags_label)
        self.tags.layout().addWidget(self.tags_combo)
        self.tags.layout().setContentsMargins(0, 0, 0, 0)
        self.top = QWidget()
        self.top.setLayout(QHBoxLayout())
        self.top.layout().addWidget(self.dictionary)
        self.top.layout().addStretch()
        self.top.layout().addWidget(self.tags)
        self.top.layout().setContentsMargins(0, 0, 0, 0)
        self.search_label = label.SelectableLabel(self)
        self.search_line_edit = line_edit.LineEdit(self)
        self.search_line_edit.textChanged.connect(self.on_search)
        self.search = QWidget()
        self.search.setLayout(QVBoxLayout())
        self.search.layout().addWidget(self.search_label)
        self.search.layout().addWidget(self.search_line_edit)
        self.search.layout().setContentsMargins(0, 0, 0, 0)
        self.search_row = QWidget()
        self.search_row.setLayout(QVBoxLayout())
        self.search_row.layout().addWidget(self.search)
        self.search_row.layout().setContentsMargins(0, 0, 0, 0)
        self.dict_view_container = QWidget()
        self.dict_view_container.setLayout(QVBoxLayout())
        self.dict_view_container.layout().setContentsMargins(0, 0, 0, 0)
        self.dict_view_container.layout().setSpacing(0)
        self.dict_view_container.layout().addWidget(self.dict_view)
        self.dict_view_row = QWidget()
        self.dict_view_row.setLayout(QVBoxLayout())
        self.dict_view_row.layout().addWidget(self.dict_view_container)
        self.dict_view_row.layout().setContentsMargins(0, 0, 0, 0)
        self.setLayout(QVBoxLayout())
        self.layout().setMenuBar(menus.DictMenuBar(self))
        self.layout().addWidget(self.top, 0)
        self.layout().addWidget(self.search_row, 0)
        self.layout().addWidget(self.dict_view_row, 1)
        self.on_update_language()
        self.on_update_settings()
        self.initialize_geometry()

    @property
    def default_width(self):
        return settings.dict_window_default_width

    @property
    def default_height(self):
        return settings.dict_window_default_height

    def dropEvent(self, event):
        for url in event.mimeData().urls():
            path = url.path()[1:]
            if os.path.exists(path):
                dict_database_file.on_import_dict_database_file(
                    os.path.normpath(path),
                    on_success=self.dict_combo_box.set_name,
                )

    def tag_populate_fn(self):
        return [tr("All Indexed Tags")] + (
            [i[1] for i in self.db.tags.get_all_tags()]
            if self.db is not None
            else []
        )

    def on_activate(self):
        super().on_activate()
        self.on_search(self.search_line_edit.text())

    def on_dict_changed(self, name):
        path = os.path.join(settings.dict_dir, f"{name}{app_info.db_ext}")
        if not os.path.exists(path):
            self.db = None
            self.dict_view.deleteLater()
            self.dict_view = dict_view.DictView()
            self.dict_view_container.layout().addWidget(self.dict_view)
            return
        if self.db and self.db.path == os.path.normpath(path):
            return
        self.db = dict_database.DictDatabase(path)
        self.dict_view.deleteLater()
        self.dict_view = dict_view.DictView(
            self.db,
            show_no_entries_text=False,
        )
        self.dict_view_container.layout().addWidget(self.dict_view)
        self.on_search(self.search_line_edit.text())

    def on_search(self, text):
        if self.db is None:
            return
        if self.tags_combo.currentIndex() == 0:
            self.dict_view.look_up(text)
        else:
            tag_name = self.tags_combo.currentText()
            try:
                tag_id = self.db.tags.get_tag_id(tag_name)
            except TypeError:
                return
            self.dict_view.look_up_for_tag(text, tag_id)

    def on_update_language(self):
        self.setWindowTitle(tr("Dictionary"))
        self.dictionary_label.setText(tr("Dictionary:"))
        self.tags_label.setText(tr("Tags:"))
        self.search_label.setText(tr("Search:"))
        self.update()

    def on_update_settings(self):
        content_margin = int(
            round(settings.app_layout_content_margin * self.dpi)
        )
        spacing = int(round(settings.app_layout_spacing * self.dpi))
        self.dictionary.layout().setSpacing(spacing)
        self.tags.layout().setSpacing(spacing)
        self.search.layout().setSpacing(spacing)
        self.top.layout().setSpacing(content_margin)
        self.search_row.layout().setSpacing(spacing)
        self.dict_view_row.layout().setSpacing(spacing)
        self.layout().setContentsMargins(
            content_margin,
            content_margin,
            content_margin,
            content_margin,
        )
        self.layout().setSpacing(2 * spacing)
        self.search_line_edit.setMinimumWidth(
            int(round(settings.app_edit_length_short * self.dpi))
        )
        popup_height = int(round(settings.dict_popup_rect_height * self.dpi))
        popup_width = int(round(settings.dict_popup_rect_width * self.dpi))
        popup_radius = int(round(settings.dict_popup_rect_radius * self.dpi))
        width = popup_width - popup_radius
        height = popup_height - popup_radius
        self.dict_view_container.setMinimumWidth(width)
        self.dict_view_container.setMinimumHeight(height)
        self.update()
