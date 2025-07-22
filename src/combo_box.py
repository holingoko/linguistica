from src import dict_database_file
from src import dict_settings_window
from src import dict_template_window
from src import settings
from src import state
from src import utils
from src.language import tr
from src.qt import *


class ComboBox(QComboBox):
    def __init__(self, populate_fn):
        super().__init__()
        self.populate_fn = populate_fn
        self.setEditable(False)
        self.setMaxVisibleItems(999)
        self.on_update_settings()

    @property
    def dpi(self):
        screen = self.screen()
        return screen.physicalDotsPerInch() / (
            screen.devicePixelRatio()
            if settings.app_scale_sizes_by_device_pixel_ratio
            else 1.0
        )

    def enterEvent(self, event):
        self.update_items()
        self.view().setMinimumWidth(
            self.minimumSizeHint().width() + self.iconSize().width()
        )

    def wheelEvent(self, event):
        event.ignore()

    def update_items(self):
        current_text = self.currentText()
        self.clear()
        self.addItems(self.populate_fn())
        self.setCurrentText(current_text)

    def on_update_settings(self):
        self.setFixedWidth(
            int(round(settings.app_edit_length_short * self.dpi)),
        )
        self.update_items()
        self.update()


class FontComboBox(ComboBox):
    def __init__(self):
        self.row_height = 0
        super().__init__(QFontDatabase.families)

    def update_items(self):
        current_text = self.currentText()
        self.clear()
        for i, text in enumerate(self.populate_fn()):
            self.addItem(text)
            font = QFont(text)
            font.setPixelSize(self.row_height)
            self.setItemData(i, font, Qt.ItemDataRole.FontRole)
        self.setCurrentText(current_text)

    def on_update_settings(self):
        self.row_height = 4 * utils.calculate_default_height(QLineEdit) // 5
        super().on_update_settings()


class TemplateComboBox(ComboBox):
    def __init__(self, db):
        self.db = db
        super().__init__(populate_fn=self.item_list)
        self.updating_items = False
        self.currentTextChanged.connect(self.on_current_text_changed)
        utils.run_after_current_event(self.update_items)

    @property
    def template_dict(self):
        return self.db.entries.get_all_templates()

    @property
    def template_name_to_entry_id(self):
        return {value: key for key, value in self.template_dict.items()}

    @property
    def selected_template_entry_id(self):
        try:
            return self.template_name_to_entry_id[self.currentText()]
        except KeyError:
            return None

    def item_list(self):
        return (
            [tr("Select Template...")]
            + sorted(self.template_dict.values())
            + [tr("Create Template...")]
        )

    def update_items(self):
        self.updating_items = True
        super().update_items()
        self.insertSeparator(1)
        self.insertSeparator(self.count() - 1)
        self.updating_items = False

    def on_current_text_changed(self):
        if self.updating_items:
            return
        current_text = self.currentText()
        if not current_text:
            return
        if self.currentIndex() == self.count() - 1:
            self.setCurrentIndex(0)
            dict_template_window.DictTemplateWindow(self.db).show()

    def on_update_language(self):
        self.update_items()
        self.update()


class DictComboBox(ComboBox):
    def __init__(self, on_hide_popup):
        super().__init__(populate_fn=self.item_list)
        self.updating_items = False
        self.on_hide_popup = on_hide_popup
        self.prev_text = self.currentText()
        self.currentTextChanged.connect(self.on_current_text_changed)
        utils.run_after_current_event(self.update_items)

    @staticmethod
    def item_list():
        return (
            [tr("Select Dictionary...")]
            + utils.get_dict_list()
            + [tr("Create Dictionary..."), tr("Import Dictionary...")]
        )

    def hidePopup(self):
        super().hidePopup()

        def on_hide_popup():
            self.on_hide_popup(self.currentText())

        utils.run_after_current_event(on_hide_popup)

    def set_name(self, name):
        self.update_items()
        self.setCurrentText(name)
        self.hidePopup()
        if name in utils.get_dict_list():
            state.last_selected_dict = name

    def update_items(self):
        self.updating_items = True
        super().update_items()
        self.insertSeparator(1)
        self.insertSeparator(self.count() - 2)
        self.updating_items = False

    def on_current_text_changed(self):
        if self.updating_items:
            return
        current_text = self.currentText()
        if not current_text or current_text == self.prev_text:
            return
        if self.currentIndex() == self.count() - 1:
            self.setCurrentText(self.prev_text)
            dict_database_file.on_import_dict_database_file(
                on_success=self.set_name
            )
        elif self.currentIndex() == self.count() - 2:
            name = dict_database_file.on_create_dict_database_file()
            if name is not None:
                self.set_name(name)
                if not isinstance(
                    self.parent(), dict_settings_window.DictSettingsWindow
                ):
                    window_ = dict_settings_window.DictSettingsWindow()
                    window_.dict_combo_box.set_name(name)
                    window_.show()
            else:
                self.set_name(self.prev_text)
        else:
            self.prev_text = current_text

    def on_update_language(self):
        self.update_items()
        self.update()
