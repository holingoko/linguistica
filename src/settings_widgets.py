import os

from src import buttons
from src import combo_box
from src import label
from src import language
from src import line_edit
from src import shortcut_edit
from src import settings
from src import theme
from src import utils
from src.language import tr
from src.qt import *

IN_TO_MM = 25.4
NUM_DIGITS = 9


class SettingsWidget(QWidget):
    def __init__(self, key, translated_text_fn):
        super().__init__()
        self.key = key
        self.translated_text_fn = translated_text_fn
        self.label = label.AutoTrimmedLabel()
        self.right = QWidget()
        self.right.setLayout(QHBoxLayout())
        self.right.layout().setContentsMargins(0, 0, 0, 0)
        self.setLayout(QHBoxLayout())
        self.layout().addStretch()
        self.layout().addWidget(self.label)
        self.layout().addWidget(self.right)
        self.layout().setContentsMargins(0, 0, 0, 0)
        self.is_visible = True

    @property
    def dpi(self):
        screen = self.screen()
        return screen.physicalDotsPerInch() / (
            screen.devicePixelRatio()
            if settings.app_scale_sizes_by_device_pixel_ratio
            else 1.0
        )

    def update_translated_text(self):
        self.label.setText(tr("{}: ").format(self.translated_text_fn()))

    def resizeEvent(self, event):
        self.label.setFixedWidth(7 * self.width() // 16)
        self.right.setFixedWidth(9 * self.width() // 16)

    def on_update_language(self):
        if language.direction == settings.LanguageDirection.RIGHT_TO_LEFT:
            self.label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        else:
            self.label.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.update()

    def on_update_settings(self):
        self.setFixedHeight(utils.calculate_default_height(line_edit.LineEdit))
        spacing = int(round(settings.app_layout_spacing * self.dpi))
        self.layout().setSpacing(spacing)
        self.right.layout().setSpacing(spacing)
        self.update()


class Bool(SettingsWidget):
    def __init__(self, key, translated_text_fn):
        super().__init__(key, translated_text_fn)
        self.check_box = QCheckBox()
        self.right.layout().addWidget(self.check_box)
        self.right.layout().addStretch()
        self.check_box.setChecked(bool(getattr(settings, key)))
        self.update_translated_text()
        self.on_update_language()
        self.on_update_settings()

    def on_save(self):
        setattr(
            settings,
            self.key,
            self.check_box.isChecked(),
        )


class UntranslatedChoice(SettingsWidget):
    def __init__(self, key, translated_text_fn, populate_fn):
        super().__init__(key, translated_text_fn)
        self.combo_box = combo_box.ComboBox(populate_fn)
        self.right.layout().addWidget(self.combo_box)
        self.right.layout().addStretch()
        try:
            self.combo_box.setCurrentText(getattr(settings, key))
        except TypeError:
            pass
        self.update_translated_text()
        self.on_update_settings()

    def on_save(self):
        setattr(
            settings,
            self.key,
            self.combo_box.currentText(),
        )


class TranslatedChoice(UntranslatedChoice):
    def __init__(self, key, translated_text_fn, populate_dict_fn):
        super().__init__(key, translated_text_fn, lambda: [])
        self.populate_dict_fn = populate_dict_fn
        self.choices_to_translation = None
        self.translation_to_choices = None
        self.update_translated_text()
        self.on_update_language()
        self.on_update_settings()

    def on_save(self):
        setattr(
            settings,
            self.key,
            self.translation_to_choices[self.combo_box.currentText()],
        )

    def on_update_language(self):
        super().on_update_language()
        self.choices_to_translation = self.populate_dict_fn()
        self.translation_to_choices = {
            value: key for key, value in self.choices_to_translation.items()
        }
        self.combo_box.clear()
        self.combo_box.populate_fn = (
            lambda: self.choices_to_translation.values()
        )
        self.combo_box.update_items()
        self.combo_box.setCurrentText(
            self.choices_to_translation[getattr(settings, self.key)]
        )
        self.update()


class LanguageChoice(UntranslatedChoice):
    def __init__(self, key, translated_text_fn):
        super().__init__(
            key,
            translated_text_fn,
            language.get_available_languages,
        )
        self.on_update_language()


class ThemeChoice(UntranslatedChoice):
    def __init__(self, key, translated_text_fn):
        super().__init__(
            key,
            translated_text_fn,
            theme.get_available_themes,
        )
        self.on_update_language()


class DictionaryChoice(UntranslatedChoice):
    def __init__(self, key, translated_text_fn):
        super().__init__(
            key,
            translated_text_fn,
            lambda: [""] + utils.get_dict_list(),
        )
        self.on_update_language()


class AlignmentChoice(TranslatedChoice):
    def __init__(self, key, translated_text_fn):
        super().__init__(
            key,
            translated_text_fn,
            lambda: {
                settings.Alignment.LEFT: tr("Left"),
                settings.Alignment.RIGHT: tr("Right"),
                settings.Alignment.CENTER: tr("Center"),
                settings.Alignment.JUSTIFY: tr("Justify"),
            },
        )


class CreateEntryIfNoMatchOnChoice(TranslatedChoice):
    def __init__(self, key, translated_text_fn):
        super().__init__(
            key,
            translated_text_fn,
            lambda: {
                settings.CreateEntryIfNoMatchOn.CLICK: tr("On Click"),
                settings.CreateEntryIfNoMatchOn.DOUBLE_CLICK: tr("On Double Click"),
                settings.CreateEntryIfNoMatchOn.NEVER: tr("Never"),
            }, # fmt:skip
        )


class DictPopupDirectionChoice(TranslatedChoice):
    def __init__(self, key, translated_text_fn):
        super().__init__(
            key,
            translated_text_fn,
            lambda: {
                settings.DictPopupDirection.ABOVE: tr("Above"),
                settings.DictPopupDirection.BELOW: tr("Below"),
            },
        )


class DictPopupHideOnChoice(TranslatedChoice):
    def __init__(self, key, translated_text_fn):
        super().__init__(
            key,
            translated_text_fn,
            lambda: {
                settings.DictPopupHideOn.CLICK: tr("On Click"),
                settings.DictPopupHideOn.DOUBLE_CLICK: tr("On Double Click"),
                settings.DictPopupHideOn.LEAVE: tr("When Leaving Text Editor"),
                settings.DictPopupHideOn.ESCAPE: tr("On Escape Key"),
                settings.DictPopupHideOn.NEVER: tr("Never"),
            }, # fmt:skip
        )


class DictPopupMoveByChoice(TranslatedChoice):
    def __init__(self, key, translated_text_fn):
        super().__init__(
            key,
            translated_text_fn,
            lambda: {
                settings.DictPopupMoveBy.CHAR: tr("Character"),
                settings.DictPopupMoveBy.WORD: tr("Word"),
                settings.DictPopupMoveBy.DISABLED: tr("Disabled"),
            }, # fmt:skip
        )


class DictPopupShowOnChoice(TranslatedChoice):
    def __init__(self, key, translated_text_fn):
        super().__init__(
            key,
            translated_text_fn,
            lambda: {
                settings.DictPopupShowOn.CLICK: tr("On Click"),
                settings.DictPopupShowOn.DOUBLE_CLICK: tr("On Double Click"),
                settings.DictPopupShowOn.HOVER: tr("On Hover Over"),
                settings.DictPopupShowOn.NEVER: tr("Never"),
            }, # fmt:skip
        )


class FontWeightChoice(TranslatedChoice):
    def __init__(self, key, translated_text_fn):
        super().__init__(
            key,
            translated_text_fn,
            lambda: {
                settings.FontWeight.NORMAL: tr("Normal"),
                settings.FontWeight.BOLD: tr("Bold"),
            },
        )


class LanguageDirectionChoice(TranslatedChoice):
    def __init__(self, key, translated_text_fn):
        super().__init__(
            key,
            translated_text_fn,
            lambda: {
                settings.LanguageDirection.AUTOMATIC: tr("Automatic"),
                settings.LanguageDirection.LEFT_TO_RIGHT: tr("Left To Right"),
                settings.LanguageDirection.RIGHT_TO_LEFT: tr("Right To Left"),
            },
        )


class LengthUnitChoice(TranslatedChoice):
    def __init__(self, key, translated_text_fn):
        super().__init__(
            key,
            translated_text_fn,
            lambda: {
                settings.LengthUnit.INCHES: tr("Inches"),
                settings.LengthUnit.MILLIMETERS: tr("Millimeters"),
            },
        )


class OpenFileBehaviorChoice(TranslatedChoice):
    def __init__(self, key, translated_text_fn):
        super().__init__(
            key,
            translated_text_fn,
            lambda: {
                settings.OpenFileBehavior.INSERT: tr("Insert"),
                settings.OpenFileBehavior.REPLACE: tr("Replace"),
                settings.OpenFileBehavior.NEW_WINDOW: tr("New Window"),
            },
        )


class OrientationChoice(TranslatedChoice):
    def __init__(self, key, translated_text_fn):
        super().__init__(
            key,
            translated_text_fn,
            lambda: {
                settings.Orientation.HORIZONTAL: tr("Horizontal"),
                settings.Orientation.VERTICAL: tr("Vertical"),
            },
        )


class ScrollTroughBehaviorOnPressChoice(TranslatedChoice):
    def __init__(self, key, translated_text_fn):
        super().__init__(
            key,
            translated_text_fn,
            lambda: {
                settings.ScrollTroughBehaviorOnPress.CHANGE_PAGE: tr("Change Page"),
                settings.ScrollTroughBehaviorOnPress.JUMP_TO: tr("Jump To"),
            }, # fmt:skip
        )


class SideChoice(TranslatedChoice):
    def __init__(self, key, translated_text_fn):
        super().__init__(
            key,
            translated_text_fn,
            lambda: {
                settings.Side.LEFT_OF_SELECTED: tr("Left Of Selected Text"),
                settings.Side.RIGHT_OF_SELECTED: tr("Right Of Selected Text"),
                settings.Side.FAR_LEFT: tr("Far Left"),
                settings.Side.FAR_RIGHT: tr("Far Right"),
            },
        )


class StartupWindowChoice(TranslatedChoice):
    def __init__(self, key, translated_text_fn):
        super().__init__(
            key,
            translated_text_fn,
            lambda: {
                settings.StartupWindow.MOST_RECENTLY_CLOSED: tr("Most Recently Closed"),
                settings.StartupWindow.NEW_TEXT_EDITOR: tr("New Text Editor"),
                settings.StartupWindow.DICTIONARY_WINDOW: tr("Dictionary Window"),
            }, # fmt:skip
        )


class FontChoice(SettingsWidget):
    def __init__(self, key, translated_text_fn):
        super().__init__(key, translated_text_fn)
        self.font_combo_box = combo_box.FontComboBox()
        self.right.layout().addWidget(self.font_combo_box)
        self.right.layout().addStretch()
        self.font_combo_box.setCurrentText(getattr(settings, key))
        self.update_translated_text()
        self.on_update_language()
        self.on_update_settings()

    def on_save(self):
        setattr(
            settings,
            self.key,
            self.font_combo_box.currentText(),
        )


class MessageChoice(UntranslatedChoice):
    def __init__(self, message_class):
        self.message_class = message_class
        super().__init__(
            None,
            lambda: tr('"{}"').format(self.message_class.message_text()),
            self.populate_fn,
        )
        self.update_translated_text()
        self.on_update_language()
        self.on_update_settings()

    @staticmethod
    def default_choice():
        return tr("Always Show Message")

    def resizeEvent(self, event):
        self.label.setFixedWidth(int(self.width() * 0.69))
        self.right.setFixedWidth(int(self.width() * 0.30))

    def update_translated_text(self):
        self.label.setText(tr("{} ").format(self.translated_text_fn()))

    def populate_fn(self):
        return [self.default_choice()] + [
            tr('{0}: "{1}"').format(tr("Always Select"), button_text)
            for button_text in self.message_class.button_texts()
        ]

    def on_save(self):
        index = self.combo_box.currentIndex()
        if index:
            index = index - 1
            settings.message_class_to_choice[self.message_class.__name__] = (
                index
            )

    def on_update_language(self):
        super().on_update_language()
        self.combo_box.update_items()
        try:
            index = settings.message_class_to_choice[
                self.message_class.__name__
            ]
            index = index + 1
            self.combo_box.setCurrentIndex(index)
        except KeyError:
            self.combo_box.setCurrentIndex(0)
        self.update()


class Number(SettingsWidget):
    def __init__(self, key, translated_text_fn):
        super().__init__(key, translated_text_fn)
        self.line_edit = line_edit.ValidatedLineEdit(self)
        self.right.layout().addWidget(self.line_edit)
        self.update_translated_text()
        self.on_update_language()
        self.on_update_settings()

    def on_save(self):
        setattr(
            settings,
            self.key,
            self.line_edit.text(),
        )


class PositiveInt(Number):
    def __init__(self, key, translated_text_fn):
        super().__init__(key, translated_text_fn)
        self.line_edit.setText(str(round(getattr(settings, key))))
        self.line_edit.setValidator(QIntValidator(bottom=0))
        self.right.layout().addStretch()

    def on_update_settings(self):
        super().on_update_settings()
        self.line_edit.setMaximumWidth(
            int(round(settings.app_edit_length_short * self.dpi))
        )
        self.update()

    def on_save(self):
        setattr(
            settings,
            self.key,
            int(self.line_edit.text().replace(",", "")),
        )


class NaturalInt(PositiveInt):
    def __init__(self, key, translated_text_fn):
        super().__init__(key, translated_text_fn)
        self.line_edit.setValidator(QIntValidator(bottom=1))


class PositiveDouble(Number):
    def __init__(self, key, translated_text_fn):
        super().__init__(key, translated_text_fn)
        self.line_edit.setText(str(round(getattr(settings, key), NUM_DIGITS)))
        self.line_edit.setValidator(QDoubleValidator(bottom=0.0))
        self.right.layout().addStretch()

    def on_update_settings(self):
        super().on_update_settings()
        self.line_edit.setMaximumWidth(
            int(round(settings.app_edit_length_short * self.dpi))
        )
        self.update()

    def on_save(self):
        setattr(
            settings,
            self.key,
            float(self.line_edit.text().replace(",", "")),
        )


class ZeroToOneDouble(PositiveDouble):
    def __init__(self, key, translated_text_fn):
        super().__init__(key, translated_text_fn)
        self.line_edit.setValidator(QDoubleValidator(bottom=0.0, top=1.0))


class Length(PositiveDouble):
    def __init__(self, key, translated_text_fn):
        super().__init__(key, translated_text_fn)
        self.length_unit_at_init = settings.app_length_unit
        if settings.app_length_unit == settings.LengthUnit.MILLIMETERS:
            value = str(round(getattr(settings, key) * IN_TO_MM, NUM_DIGITS))
        else:
            value = str(round(getattr(settings, key), NUM_DIGITS))
        self.line_edit.setText(value)

    def update_translated_text(self):
        if settings.app_length_unit == settings.LengthUnit.MILLIMETERS:
            units = tr("mm")
        else:
            units = tr("in.")
        self.label.setText(
            tr("{0} /[{1}/]: ").format(
                self.translated_text_fn(),
                units,
            )
        )

    def on_save(self):
        if self.length_unit_at_init == settings.LengthUnit.MILLIMETERS:
            setattr(
                settings,
                self.key,
                float(self.line_edit.text()) / IN_TO_MM,
            )
        else:
            setattr(
                settings,
                self.key,
                float(self.line_edit.text()),
            )


class FileDirectory(SettingsWidget):
    def __init__(self, key, translated_text_fn):
        super().__init__(key, translated_text_fn)
        self.line_edit = line_edit.LineEdit(self)
        path = str(getattr(settings, key))
        self.line_edit.setText(os.path.normpath(path) if path else path)
        self.select_button = buttons.TextButton(self.on_select)
        self.extra_space = QWidget()
        self.right.layout().takeAt(0)
        self.right.layout().addWidget(self.line_edit, 1)
        self.right.layout().addWidget(self.select_button)
        self.right.layout().addWidget(self.extra_space)
        self.right.layout().addStretch()
        self.update_translated_text()
        self.on_update_language()
        self.on_update_settings()

    def on_select(self):
        prev_dir = self.line_edit.text()
        if prev_dir:
            os.makedirs(prev_dir, exist_ok=True)
        path = QFileDialog.getExistingDirectory(
            self,
            caption=tr("Select Directory"),
            dir=prev_dir,
        )
        if path:
            self.line_edit.setText(os.path.normpath(path))

    def on_save(self):
        path = self.line_edit.text()
        setattr(
            settings,
            self.key,
            os.path.normpath(path) if path else path,
        )

    def on_update_language(self):
        super().on_update_language()
        self.select_button.setText(tr("Select"))
        self.update()

    def on_update_settings(self):
        super().on_update_settings()
        self.extra_space.setFixedWidth(
            int(round(settings.app_scroll_trough_thickness * self.dpi))
        )
        self.update()


class Shortcut(SettingsWidget):
    def __init__(self, action_class):
        self.action = action_class.instance()
        super().__init__(
            None,
            lambda: tr("{} ").format(self.action.action_.text()),
        )
        self.shortcut_edit = shortcut_edit.ShortcutEdit()
        self.right.layout().addWidget(self.shortcut_edit)
        self.right.layout().addStretch()
        self.shortcut_edit.set_text(self.action.shortcut_)
        self.update_translated_text()
        self.on_update_language()
        self.on_update_settings()

    def on_save(self):
        self.action.shortcut_ = self.shortcut_edit.get_text().lower()
