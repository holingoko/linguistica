from src import app_info
from src import buttons
from src import dict_format
from src import label
from src import language
from src import settings
from src import utils
from src import window
from src.language import tr
from src.qt import *


def quote(value):
    return tr('"{}"').format(value)


def format_multiple_quoted_values(values):
    quoted_values = [quote(value) for value in values]
    multiple_values_format = (
        tr("{}|{{} and {}}|{{},... {}, and {}}")
        + language.rtl_tag_or_empty_string
    )

    return dict_format.Formatter.format_multiple_values(
        quoted_values,
        multiple_values_format,
    )


class MessageLabel(label.SelectableLabel):
    def __init__(self, window_):
        super().__init__(window_)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setWordWrap(True)


class UnFocusableCheckBox(QCheckBox):
    def __init__(self):
        super().__init__()
        self.setFocusPolicy(Qt.FocusPolicy.NoFocus)


class Message(window.Window):
    def __init__(self, format_args=(), is_plural=False):
        try:
            index = settings.message_class_to_choice[self.__class__.__name__]
            try:
                self.button_actions()[index]()
                self.show = lambda: None
                return
            except IndexError:
                pass
        except KeyError:
            pass
        super().__init__()
        self.format_args = format_args
        self.is_plural = is_plural
        self.top = QWidget()
        self.top.setLayout(QVBoxLayout())
        self.message = MessageLabel(self)
        self.check_box = UnFocusableCheckBox()
        self.top.layout().addWidget(self.message, 1)
        self.top.layout().addWidget(self.check_box, 0)
        self.button_list = []
        for i in range(len(self.button_texts())):
            buttons.FocusedIsDefaultPushButton(
                lambda i_=i: self.on_action(i_),
                self.button_list,
            )
        self.buttons = QWidget()
        self.buttons.setLayout(QHBoxLayout())
        self.buttons.layout().addStretch()
        for button in self.button_list:
            self.buttons.layout().addWidget(button)
        self.default_button = button.default_button
        if len(self.button_list) == 1:
            self.buttons.layout().addStretch()
        self.buttons.layout().setContentsMargins(0, 0, 0, 0)
        utils.run_after_current_event(self.button_list[-1].setFocus)
        self.setLayout(QVBoxLayout())
        self.layout().addWidget(self.top, 1)
        self.layout().addWidget(self.buttons, 0)
        self.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint)
        self.setWindowModality(Qt.WindowModality.ApplicationModal)
        self.initialize_geometry()
        self.on_update_language()
        self.on_update_settings()

    @property
    def default_width(self):
        return settings.app_dialog_window_default_width

    @property
    def default_height(self):
        return settings.app_dialog_window_default_height

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Return:
            self.default_button().pressed.emit()
            return
        super().keyPressEvent(event)

    def keyReleaseEvent(self, event):
        if event.key() == Qt.Key.Key_Return:
            self.default_button().released.emit()
            return
        super().keyReleaseEvent(event)

    def on_action(self, index):
        if self.check_box.isChecked():
            settings.message_class_to_choice[self.__class__.__name__] = index
            settings.save()
        self.close()
        self.button_actions()[index]()

    def on_update_language(self):
        if self.is_plural:
            self.message.setText(
                self.message_text_plural().format(*self.format_args),
            )
        else:
            self.message.setText(
                self.message_text().format(*self.format_args),
            )
        self.check_box.setText(tr("Don't show this message again."))
        for button, text in zip(
            self.button_list,
            self.button_texts(),
            strict=True,
        ):
            button.setText(text)
        self.update()

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
        self.layout().setSpacing(round(settings.app_layout_spacing * self.dpi))
        self.top.layout().setContentsMargins(
            content_margin,
            content_margin,
            content_margin,
            content_margin,
        )
        self.top.layout().setSpacing(
            round(settings.app_layout_spacing * self.dpi)
        )
        self.buttons.layout().setSpacing(
            round(settings.app_button_spacing * self.dpi)
        )
        self.update()


class InfoMessage(Message):
    def on_update_language(self):
        super().on_update_language()
        self.setWindowTitle(tr("Info"))
        self.update()


class WarningMessage(Message):
    def on_update_language(self):
        super().on_update_language()
        self.setWindowTitle(tr("Warning"))
        self.update()


class ErrorMessage(Message):
    def on_update_language(self):
        super().on_update_language()
        self.setWindowTitle(tr("Error"))
        self.update()


class AboutInfoMessage(InfoMessage):
    def __init__(self):
        super().__init__()
        self.check_box.hide()

    @staticmethod
    def message_text():
        return f'<b>{app_info.name}</b><div style="font-size: {settings.app_font_size}pt;">{tr("Version")} {app_info.version}</div>'

    @staticmethod
    def button_texts():
        return [tr("OK")]

    @staticmethod
    def button_actions():
        return [lambda: None]


pre_keys = set(globals().keys())


class TextNotFoundInfoMessage(InfoMessage):
    def __init__(self, text):
        super().__init__([quote(text)])

    @staticmethod
    def message_text():
        return tr("The text {} was not found.")

    @staticmethod
    def button_texts():
        return [tr("OK")]

    @staticmethod
    def button_actions():
        return [lambda: None]


class DictionaryImportSuccessInfoMessage(InfoMessage):
    def __init__(self, name):
        super().__init__([quote(name)])

    @staticmethod
    def message_text():
        return tr("The dictionary {} was successfully imported.")

    @staticmethod
    def button_texts():
        return [tr("OK")]

    @staticmethod
    def button_actions():
        return [lambda: None]


class DeletedTagsWarningMessage(WarningMessage):
    def __init__(self, tags, on_continue):
        self.on_continue = on_continue
        super().__init__(
            (format_multiple_quoted_values(tags),),
            is_plural=len(tags) > 1,
        )

    @staticmethod
    def message_text():
        return tr(
            "The tag {} is about to be permanently deleted and will be removed from all entries."
        )

    @staticmethod
    def message_text_plural():
        return tr(
            "The tags {} are about to be permanently deleted and will be removed from all entries."
        )

    @staticmethod
    def button_texts():
        return [
            tr("Continue"),
            tr("Cancel"),
        ]

    def button_actions(self):
        return [
            self.on_continue,
            lambda: None,
        ]


class DeleteTemplateWarningMessage(WarningMessage):
    def __init__(self, on_continue):
        self.on_continue = on_continue
        super().__init__()

    @staticmethod
    def message_text():
        return tr("The template will be permanently deleted.")

    @staticmethod
    def button_texts():
        return [
            tr("Continue"),
            tr("Cancel"),
        ]

    def button_actions(self):
        return [
            self.on_continue,
            lambda: None,
        ]


class DictionaryDirectoryChangedWarningMessage(WarningMessage):
    def __init__(self, on_copy_automatically):
        self.on_copy_automatically = on_copy_automatically
        super().__init__()

    @staticmethod
    def message_text():
        return tr(
            "The dictionary directory has been changed. Existing dictionaries will no longer be visible to the application unless they are moved into the new directory."
        )

    @staticmethod
    def button_texts():
        return [
            tr("Copy Automatically"),
            tr("OK"),
        ]

    def button_actions(self):
        return [
            self.on_copy_automatically,
            lambda: None,
        ]


class DictionaryNotInDictionaryDirectoryWarningMessage(WarningMessage):
    def __init__(self):
        super().__init__()

    @staticmethod
    def message_text():
        return tr(
            "The dictionary was created in a directory other than the dictionary directory and so will not be visible to the application. The dictionary directory can be changed via settings."
        )

    @staticmethod
    def button_texts():
        return [tr("OK")]

    @staticmethod
    def button_actions():
        return [lambda: None]


class EmptyTagValuesFormatWarningMessage(WarningMessage):
    def __init__(self, tags, on_continue):
        self.on_continue = on_continue
        super().__init__(
            (format_multiple_quoted_values(tags),),
            is_plural=len(tags) > 1,
        )

    @staticmethod
    def message_text():
        return tr(
            "The tag values format string for the tag {} is empty. Expressions containing this tag will be empty even when there are values for this tag."
        )

    @staticmethod
    def message_text_plural():
        return tr(
            "The tag values format strings for the tags {} are empty. Expressions containing these tags will be empty even when there are values for these tags."
        )

    @staticmethod
    def button_texts():
        return [
            tr("Continue"),
            tr("Cancel"),
        ]

    def button_actions(self):
        return [
            self.on_continue,
            lambda: None,
        ]


class ExistingDictionaryOverwriteWarningMessage(WarningMessage):
    def __init__(self, name, on_continue):
        self.on_continue = on_continue
        super().__init__([quote(name)])

    @staticmethod
    def message_text():
        return tr(
            "Importing the dictionary {} will overwrite an existing dictionary with the same name."
        )

    @staticmethod
    def button_texts():
        return [
            tr("Continue"),
            tr("Cancel"),
        ]

    def button_actions(self):
        return [
            self.on_continue,
            lambda: None,
        ]


class MissingTagsWarningMessage(WarningMessage):
    def __init__(self, tags, on_continue):
        self.on_continue = on_continue
        super().__init__(
            (format_multiple_quoted_values(tags),),
            is_plural=len(tags) > 1,
        )

    @staticmethod
    def message_text():
        return tr(
            "The tag {} is in the entry format string but not in the dictionary tag list. Expressions containing this tag will always be empty."
        )

    @staticmethod
    def message_text_plural():
        return tr(
            "The tags {} are in the entry format string but not in the dictionary tag list. Expressions containing these tags will always be empty."
        )

    @staticmethod
    def button_texts():
        return [
            tr("Continue"),
            tr("Cancel"),
        ]

    def button_actions(self):
        return [
            self.on_continue,
            lambda: None,
        ]


class MissingTranslationsWarningMessage(WarningMessage):
    def __init__(self, name):
        super().__init__([quote(name)])

    @staticmethod
    def message_text():
        return tr(
            "The language {} is missing one or more translations, so some text in the application may not be properly translated."
        )

    @staticmethod
    def button_texts():
        return [tr("OK")]

    @staticmethod
    def button_actions():
        return [lambda: None]


class NoIndexedTagsWarningMessage(WarningMessage):
    def __init__(self, on_continue):
        self.on_continue = on_continue
        super().__init__()

    @staticmethod
    def message_text():
        return tr(
            "The dictionary has no indexed tags, so the popup window for this dictionary will never have any matching entries."
        )

    @staticmethod
    def button_texts():
        return [
            tr("Continue"),
            tr("Cancel"),
        ]

    def button_actions(self):
        return [
            self.on_continue,
            lambda: None,
        ]


class NonArbitraryTagValuesFormatWarningMessage(WarningMessage):
    def __init__(self, tags, on_continue):
        self.on_continue = on_continue
        super().__init__(
            (format_multiple_quoted_values(tags),),
            is_plural=len(tags) > 1,
        )

    @staticmethod
    def message_text():
        return tr(
            "The tag values format string for the tag {} is not set up to handle an arbitrary number of values. Expressions containing this tag may be empty even when tag values for this tag are present."
        )

    @staticmethod
    def message_text_plural():
        return tr(
            "The tag values format strings for the tags {} are not set up to handle an arbitrary number of values. Expressions containing these tags may be empty even when tag values for these tags are present."
        )

    @staticmethod
    def button_texts():
        return [
            tr("Continue"),
            tr("Cancel"),
        ]

    def button_actions(self):
        return [
            self.on_continue,
            lambda: None,
        ]


class ReloadTextWarningMessage(WarningMessage):
    def __init__(self, name, on_reload, on_ignore):
        self.on_reload = on_reload
        self.on_ignore = on_ignore
        super().__init__([quote(name)])

    @staticmethod
    def message_text():
        return tr(
            "The file {} has been modified outside of the current text editor. Should the file be reloaded?"
        )

    @staticmethod
    def button_texts():
        return [
            tr("Yes"),
            tr("No"),
        ]

    def button_actions(self):
        return [
            self.on_reload,
            self.on_ignore,
        ]


class ReloadUnsavedTextWarningMessage(WarningMessage):
    def __init__(self, name, on_reload, on_ignore):
        self.on_reload = on_reload
        self.on_ignore = on_ignore
        super().__init__([quote(name)])

    @staticmethod
    def message_text():
        return tr(
            "The file {} has been modified outside of the current text editor. Should the file be reloaded? Note that there are unsaved changes that will be overwritten if the file is reloaded."
        )

    @staticmethod
    def button_texts():
        return [
            tr("Yes"),
            tr("No"),
        ]

    def button_actions(self):
        return [
            self.on_reload,
            self.on_ignore,
        ]


class TextLockedWarningMessage(WarningMessage):
    def __init__(self, name, on_unlock_text):
        self.on_unlock_text = on_unlock_text
        super().__init__([quote(name)])

    @staticmethod
    def message_text():
        return tr("The file {} cannot be edited because it is locked.")

    @staticmethod
    def button_texts():
        return [
            tr("Unlock"),
            tr("Cancel"),
        ]

    def button_actions(self):
        return [
            self.on_unlock_text,
            lambda: None,
        ]


class UnsavedDictionaryOnChangeWarningMessage(WarningMessage):
    def __init__(self, name, on_switch, on_save_and_switch, on_cancel):
        self.on_switch = on_switch
        self.on_save_and_switch = on_save_and_switch
        self.on_cancel = on_cancel
        super().__init__([quote(name)])

    @staticmethod
    def message_text():
        return tr(
            "The dictionary {} has unsaved changes that will be lost when switching to another dictionary."
        )

    @staticmethod
    def button_texts():
        return [
            tr("Switch"),
            tr("Save And Switch"),
            tr("Cancel"),
        ]

    def button_actions(self):
        return [
            self.on_switch,
            self.on_save_and_switch,
            self.on_cancel,
        ]


class UnsavedDictionaryOnCloseWarningMessage(WarningMessage):
    def __init__(self, name, on_close, on_save_and_close):
        self.on_close = on_close
        self.on_save_and_close = on_save_and_close
        super().__init__([quote(name)])

    @staticmethod
    def message_text():
        return tr(
            "The dictionary {} has unsaved changes that will be lost if the window is closed."
        )

    @staticmethod
    def button_texts():
        return [
            tr("Close"),
            tr("Save And Close"),
            tr("Cancel"),
        ]

    def button_actions(self):
        return [
            self.on_close,
            self.on_save_and_close,
            lambda: None,
        ]


class UnsavedEntryWarningMessage(WarningMessage):
    def __init__(self, on_close, on_save_and_close):
        self.on_close = on_close
        self.on_save_and_close = on_save_and_close
        super().__init__()

    @staticmethod
    def message_text():
        return tr(
            "The dictionary entry has unsaved changes that will be lost if the window is closed."
        )

    @staticmethod
    def button_texts():
        return [
            tr("Close"),
            tr("Save And Close"),
            tr("Cancel"),
        ]

    def button_actions(self):
        return [
            self.on_close,
            self.on_save_and_close,
            lambda: None,
        ]


class UnsavedFilesWarningMessage(WarningMessage):
    def __init__(self, paths, on_close_without_saving, on_save_and_close):
        self.on_close_without_saving = on_close_without_saving
        self.on_save_and_close = on_save_and_close
        super().__init__(
            (format_multiple_quoted_values(paths),),
            is_plural=len(paths) > 1,
        )

    @staticmethod
    def message_text():
        return tr("The file {} is about to be closed without saving.")

    @staticmethod
    def message_text_plural():
        return tr("The files {} are about to be closed without saving.")

    @staticmethod
    def button_texts():
        return [
            tr("Close"),
            tr("Save And Close"),
            tr("Cancel"),
        ]

    def button_actions(self):
        return [
            self.on_close_without_saving,
            self.on_save_and_close,
            lambda: None,
        ]


class UnsavedTemplateWarningMessage(WarningMessage):
    def __init__(self, on_close, on_save_and_close):
        self.on_close = on_close
        self.on_save_and_close = on_save_and_close
        super().__init__()

    @staticmethod
    def message_text():
        return tr(
            "The dictionary template has unsaved changes that will be lost if the window is closed."
        )

    @staticmethod
    def button_texts():
        return [
            tr("Close"),
            tr("Save And Close"),
            tr("Cancel"),
        ]

    def button_actions(self):
        return [
            self.on_close,
            self.on_save_and_close,
            lambda: None,
        ]


class CannotSaveDictionarySettingsWhileEntryOrTemplateOpenErrorMessage(
    ErrorMessage
):
    def __init__(self):
        super().__init__()

    @staticmethod
    def message_text():
        return tr(
            "Dictionary settings cannot be saved while dictionary entry or template windows are open."
        )

    @staticmethod
    def button_texts():
        return [tr("OK")]

    @staticmethod
    def button_actions():
        return [lambda: None]


class DictionaryDirectoryCopyAutomaticallyFailedErrorMessage(ErrorMessage):
    def __init__(self):
        super().__init__()

    @staticmethod
    def message_text():
        return tr(
            "One or more dictionaries could not be automatically copied into the new dictionary directory. Please copy any missing dictionaries from the old dictionary directory manually."
        )

    @staticmethod
    def button_texts():
        return [tr("OK")]

    @staticmethod
    def button_actions():
        return [lambda: None]


class DuplicateTagNameErrorMessage(ErrorMessage):
    def __init__(self):
        super().__init__()

    @staticmethod
    def message_text():
        return tr("Multiple tags cannot have the same name.")

    @staticmethod
    def button_texts():
        return [tr("OK")]

    @staticmethod
    def button_actions():
        return [lambda: None]


class FileDoesNotExistErrorMessage(ErrorMessage):
    def __init__(self, path):
        super().__init__([quote(path)])

    @staticmethod
    def message_text():
        return tr("The file {} cannot be opened because it does not exist.")

    @staticmethod
    def button_texts():
        return [tr("OK")]

    @staticmethod
    def button_actions():
        return [lambda: None]


class FileIsNotDictionaryErrorMessage(ErrorMessage):
    def __init__(self, path):
        super().__init__([quote(path)])

    @staticmethod
    def message_text():
        return tr("The file {} is not a dictionary.")

    @staticmethod
    def button_texts():
        return [tr("OK")]

    @staticmethod
    def button_actions():
        return [lambda: None]


class FileIsNotTextOrDictionaryErrorMessage(ErrorMessage):
    def __init__(self, path):
        super().__init__([quote(path)])

    @staticmethod
    def message_text():
        return tr("The file {} is not a text file or a dictionary.")

    @staticmethod
    def button_texts():
        return [tr("OK")]

    @staticmethod
    def button_actions():
        return [lambda: None]


class InvalidTagErrorMessage(ErrorMessage):
    def __init__(self, tags):
        super().__init__(
            (format_multiple_quoted_values(tags),),
            is_plural=len(tags) > 1,
        )

    @staticmethod
    def message_text():
        return tr(
            "The tag name {} is invalid. Tag names may only contain characters, numbers, spaces, and underscores."
        )

    @staticmethod
    def message_text_plural():
        return tr(
            "The tag names {} are invalid. Tag names may only contain characters, numbers, spaces, and underscores."
        )

    @staticmethod
    def button_texts():
        return [tr("OK")]

    @staticmethod
    def button_actions():
        return [lambda: None]


class InvalidThemeErrorMessage(ErrorMessage):
    def __init__(self, name):
        super().__init__([quote(name)])

    @staticmethod
    def message_text():
        return tr(
            "The theme {} could not be applied because it has an invalid style sheet. The application theme has been reset to the default."
        )

    @staticmethod
    def button_texts():
        return [tr("OK")]

    @staticmethod
    def button_actions():
        return [lambda: None]


class MissingLanguageErrorMessage(ErrorMessage):
    def __init__(self, name):
        super().__init__([quote(name)])

    @staticmethod
    def message_text():
        return tr(
            "The language {} could not be found. The application language has been reset to the default."
        )

    @staticmethod
    def button_texts():
        return [tr("OK")]

    @staticmethod
    def button_actions():
        return [lambda: None]


class MissingThemeErrorMessage(ErrorMessage):
    def __init__(self, name):
        super().__init__([quote(name)])

    @staticmethod
    def message_text():
        return tr(
            "The theme {} could not be found. The application theme has been reset to the default."
        )

    @staticmethod
    def button_texts():
        return [tr("OK")]

    @staticmethod
    def button_actions():
        return [lambda: None]


class NoDictionarySelectedErrorMessage(ErrorMessage):
    def __init__(self):
        super().__init__()

    @staticmethod
    def message_text():
        return tr("No dictionary is selected.")

    @staticmethod
    def button_texts():
        return [tr("OK")]

    @staticmethod
    def button_actions():
        return [lambda: None]


class NoEntrySelectedErrorMessage(ErrorMessage):
    def __init__(self):
        super().__init__()

    @staticmethod
    def message_text():
        return tr("No entry is selected.")

    @staticmethod
    def button_texts():
        return [tr("OK")]

    @staticmethod
    def button_actions():
        return [lambda: None]


class NoExtNameWithExtTakenErrorMessage(ErrorMessage):
    def __init__(self, name, on_ok):
        self.on_ok = on_ok
        super().__init__(
            (
                quote(app_info.db_ext),
                quote(name),
            )
        )

    @staticmethod
    def message_text():
        return tr(
            "Dictionary files must end in {0}, but the file {1} already exists. Enter file name as {1} to overwrite, or choose a new name."
        )

    @staticmethod
    def button_texts():
        return [tr("OK")]

    def button_actions(self):
        return [self.on_ok]


class NoTagsErrorMessage(ErrorMessage):
    def __init__(self):
        super().__init__()

    @staticmethod
    def message_text():
        return tr("The dictionary must have at least one tag.")

    @staticmethod
    def button_texts():
        return [tr("OK")]

    @staticmethod
    def button_actions():
        return [lambda: None]


class NoTemplateSelectedErrorMessage(ErrorMessage):
    def __init__(self):
        super().__init__()

    @staticmethod
    def message_text():
        return tr("No template is selected.")

    @staticmethod
    def button_texts():
        return [tr("OK")]

    @staticmethod
    def button_actions():
        return [lambda: None]


class NoTextEditorSelectedErrorMessage(ErrorMessage):
    def __init__(self):
        super().__init__()

    @staticmethod
    def message_text():
        return tr(
            "No action was performed because no text editor is selected."
        )

    @staticmethod
    def button_texts():
        return [tr("OK")]

    @staticmethod
    def button_actions():
        return [lambda: None]


class OverwriteDictionaryFailedErrorMessage(ErrorMessage):
    def __init__(self, name):
        super().__init__([quote(name)])

    @staticmethod
    def message_text():
        return tr(
            "The dictionary {} cannot be overwritten because its database file is being used by some program."
        )

    @staticmethod
    def button_texts():
        return [tr("OK")]

    @staticmethod
    def button_actions():
        return [lambda: None]


post_keys = set(globals().keys())
class_keys = post_keys - pre_keys - {"pre_keys"}
classes = [globals()[key] for key in class_keys]
