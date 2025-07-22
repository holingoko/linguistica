from src import dict_entry_window
from src import dict_format
from src import dict_search
from src import dict_template_window
from src import menus
from src import settings
from src import text_edit
from src.language import tr
from src.qt import *


class DictViewTextEdit(QTextEdit):
    def __init__(self, window):
        super().__init__(window)
        self.setReadOnly(True)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.on_focus_in = lambda: None
        self.on_focus_out = lambda: None

    def focusInEvent(self, event):
        super().focusInEvent(event)
        self.on_focus_in()

    def focusOutEvent(self, event):
        super().focusOutEvent(event)
        self.on_focus_out()

    def wheelEvent(self, event):
        self.setFocus()
        super().wheelEvent(event)
        event.accept()

    def on_copy(self):
        self.copy()

    def on_select_all(self):
        self.selectAll()


class PopupDictViewTextEdit(DictViewTextEdit):
    pass


class DictViewScrollbarSignaler(QScrollBar):
    def __init__(self, parent):
        super().__init__(Qt.Orientation.Vertical, parent)
        self.on_slider_change = lambda x: None

    def sliderChange(self, change):
        self.on_slider_change(change)

    def set_value(self, value):
        return self.setValue(value)


class DictViewScrollbar(QWidget):
    def __init__(self, text_edit_):
        super().__init__(text_edit_)
        self.text_edit = text_edit_
        self.scrollbar = text_edit_.verticalScrollBar()
        self.trough = text_edit.Trough(self.scrollbar, lambda: None)
        self.setLayout(QVBoxLayout())
        self.layout().addWidget(self.trough)
        self.layout().setSpacing(0)
        self.layout().setContentsMargins(0, 0, 0, 0)
        self.on_update_settings()

    @property
    def dpi(self):
        screen = self.screen()
        return screen.physicalDotsPerInch() / (
            screen.devicePixelRatio()
            if settings.app_scale_sizes_by_device_pixel_ratio
            else 1.0
        )

    def wheelEvent(self, event):
        self.text_edit.wheelEvent(event)

    def on_update_settings(self):
        self.setVisible(settings.app_scroll_bar_visible)
        self.setFixedWidth(
            int(round(settings.app_scroll_trough_thickness * self.dpi))
        )
        self.update()


class DictView(QWidget):
    def __init__(self, db=None, show_outline=True, show_no_entries_text=True):
        super().__init__()
        self.context_menu = menus.DictViewContextMenu(self)
        if show_outline:
            self.text_edit = DictViewTextEdit(self)
        else:
            self.text_edit = PopupDictViewTextEdit(self)
        self.show_no_entries_text = show_no_entries_text
        self.text_edit.contextMenuEvent = self.contextMenuEvent
        self.text_edit.setVerticalScrollBar(
            DictViewScrollbarSignaler(self.text_edit)
        )
        self.scrollbar = DictViewScrollbar(self.text_edit)
        self.scrollbar.raise_()
        self.setLayout(QVBoxLayout())
        self.layout().addWidget(self.text_edit)
        self.layout().setSpacing(0)
        self.layout().setContentsMargins(0, 0, 0, 0)
        self.db = db
        self.formatter = None
        self.searcher = None
        self.entry_joiner = None
        self.prev_html = None
        self.tag_values_list = None
        self.entry_ids = []
        if self.db is not None:
            self.db.on_change_fns.add(self.set_db_dependent_objects)
            self.set_db_dependent_objects()

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
        self.text_edit.setFocus()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        size = event.size()
        width = size.width()
        height = size.height()
        scrollbar_width = self.scrollbar.width()
        self.scrollbar.setGeometry(
            width - scrollbar_width - 2,
            2,
            scrollbar_width,
            height - 4,
        )

    def set_db_dependent_objects(self):
        self.formatter = dict_format.Formatter(
            self.db.info.get_entry_format(),
            self.db.tags.get_all_tags(),
        )
        self.searcher = dict_search.Searcher(self.db)
        self.entry_joiner = self.db.info.get_entry_joiner()
        self.prev_html = None
        self.tag_values_list = None

    def look_up_around_index(self, text, index):
        (
            tag_id_to_tag_values_list,
            self.entry_ids,
        ) = self.searcher.search_indexed_tags_around_index(text, index)
        self.update_entries_(tag_id_to_tag_values_list)

    def look_up(self, text):
        (
            tag_id_to_tag_values_list,
            self.entry_ids,
        ) = self.searcher.search_indexed_tags(
            text,
            exact=settings.dict_only_show_exact_matches,
        )
        self.update_entries_(tag_id_to_tag_values_list)

    def look_up_for_tag(self, text, tag_id):
        (
            tag_id_to_tag_values_list,
            self.entry_ids,
        ) = self.searcher.search_tag(
            text,
            tag_id,
            exact=settings.dict_only_show_exact_matches,
        )
        self.update_entries_(tag_id_to_tag_values_list)

    def update_entries_(self, tag_id_to_tag_values_list):
        if not tag_id_to_tag_values_list:
            if self.show_no_entries_text:
                html = f'<div style="text-align: center;">{tr("No matching entries found.")}</div>'
            else:
                html = ""
            if html != self.prev_html:
                self.text_edit.setHtml(html)
                self.prev_html = html
            return
        tag_id_to_tag_name = {
            tag_id: tag_name
            for tag_id, tag_name, _, _ in self.db.tags.get_all_tags()
        }
        tag_values_list = []
        for tag_id_to_tag_values in tag_id_to_tag_values_list:
            tag_values_list.append(
                [
                    (
                        tag_id,
                        tag_id_to_tag_name[tag_id],
                        tag_id_to_tag_values[tag_id],
                    )
                    for tag_id in tag_id_to_tag_name
                ]
            )
        self.update_entries(tag_values_list)

    def update_entries(self, tag_values_list):
        self.tag_values_list = tag_values_list
        html = self.entry_joiner.join(
            self.formatter.format(
                {key: values for _, key, values in tag_values}
            )
            for tag_values in tag_values_list
        )
        if html != self.prev_html:
            self.text_edit.setHtml(html)
            self.prev_html = html

    def on_create_entry(self):
        dict_entry_window.DictEntryWindow(self.db).show()

    def on_edit_entry(self):
        for entry_id in self.entry_ids:
            dict_entry_window.DictEntryWindow(self.db, entry_id).show()

    def on_create_template(self):
        dict_template_window.DictTemplateWindow(self.db).show()

    def on_update_settings(self):
        self.scrollbar.line_height = self.fontMetrics().height()
        if self.tag_values_list is not None:
            self.update_entries(self.tag_values_list)
        self.update()


class PopupDictView(DictView):
    def __init__(self, db):
        super().__init__(db, show_outline=False)
