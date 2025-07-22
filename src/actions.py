import os

from src import app
from src import dict_database_file
from src import dict_entry_window
from src import dict_settings_window
from src import dict_template_window
from src import dict_view
from src import dict_window
from src import main_window
from src import messages
from src import settings
from src import settings_window
from src import system
from src import text_editor
from src import window
from src.language import tr
from src.qt import *


class Action(QWidget):
    @classmethod
    def instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    @classmethod
    def action(cls):
        return cls.instance().action_

    @classmethod
    def shortcut(cls):
        return cls.instance().shortcut_


class ActionInstance(Action):
    def __init__(self):
        super().__init__()
        self._action = QAction()
        self._shortcut = ""
        self._action.triggered.connect(self.on_action)
        self._action.setMenuRole(QAction.MenuRole.NoRole)
        self.on_update_language()
        self.on_update_settings()

    @property
    def action_(self):
        return self._action

    @property
    def shortcut_(self):
        return self._shortcut

    @shortcut_.setter
    def shortcut_(self, shortcut):
        self._shortcut = shortcut
        self._action.setShortcut(shortcut)
        settings.action_class_to_shortcut[self.__class__.__name__] = shortcut

    def on_update_settings(self):
        try:
            self.shortcut_ = settings.action_class_to_shortcut[
                self.__class__.__name__
            ]
        except KeyError:
            self.shortcut_ = self.default_shortcut
        self.update()


pre_keys = set(globals().keys())


class NewText(ActionInstance):
    _instance = None
    default_shortcut = ""

    @staticmethod
    def on_action():
        active_window = app.activeWindow()
        try:
            fn = active_window.on_new_text
        except AttributeError:
            try:
                fn = active_window.parent_window.on_new_text
            except AttributeError:
                fn = main_window.MainWindow(
                    ([text_editor.TextEditor.default_state()], None, None)
                ).show

        fn()

    def on_update_language(self):
        self._action.setText(tr("New Text"))


class NewTextWindow(ActionInstance):
    _instance = None
    default_shortcut = "ctrl+n"

    @staticmethod
    def on_action():
        main_window.MainWindow().show()

    def on_update_language(self):
        self._action.setText(tr("New Text Window"))


class OpenText(ActionInstance):
    _instance = None
    default_shortcut = "ctrl+o"

    @staticmethod
    def on_action():
        active_window = app.activeWindow()
        try:
            fn = active_window.on_open_text
        except AttributeError:
            try:
                fn = active_window.parent_window.on_open_text
            except AttributeError:
                fn = main_window.MainWindow.create_window_and_open_text
        fn()

    def on_update_language(self):
        self._action.setText(tr("Open Text..."))


class SaveText(ActionInstance):
    _instance = None
    default_shortcut = ""

    @staticmethod
    def on_action():
        active_window = app.activeWindow()
        try:
            fn = active_window.on_save_text
        except AttributeError:
            try:
                fn = active_window.parent_window.on_save_text
            except AttributeError:
                fn = lambda: None
        fn()

    def on_update_language(self):
        self._action.setText(tr("Save Text"))


class SaveTextAs(ActionInstance):
    _instance = None
    default_shortcut = ""

    @staticmethod
    def on_action():
        active_window = app.activeWindow()
        try:
            fn = active_window.on_save_text_as
        except AttributeError:
            try:
                fn = active_window.parent_window.on_save_text_as
            except AttributeError:
                fn = lambda: None
        fn()

    def on_update_language(self):
        self._action.setText(tr("Save Text As..."))


class SaveAllTexts(ActionInstance):
    _instance = None
    default_shortcut = "ctrl+s"

    @staticmethod
    def on_action():
        active_window = app.activeWindow()
        try:
            fn = active_window.on_save_all_texts
        except AttributeError:
            try:
                fn = active_window.parent_window.on_save_all_texts
            except AttributeError:
                fn = lambda: None
        fn()

    def on_update_language(self):
        self._action.setText(tr("Save All Texts"))


class SaveWindow(ActionInstance):
    _instance = None
    default_shortcut = "ctrl+s"

    @staticmethod
    def on_action():
        active_window = app.activeWindow()
        try:
            fn = active_window.on_save
        except AttributeError:
            fn = lambda: None
        fn()

    def on_update_language(self):
        self._action.setText(tr("Save Window"))


class RenameText(ActionInstance):
    _instance = None
    default_shortcut = ""

    @staticmethod
    def on_action():
        active_window = app.activeWindow()
        try:
            fn = active_window.on_rename_text
        except AttributeError:
            try:
                fn = active_window.parent_window.on_rename_text
            except AttributeError:
                fn = lambda: None
        fn()

    def on_update_language(self):
        self._action.setText(tr("Rename Text..."))


class CopyFileName(ActionInstance):
    _instance = None
    default_shortcut = ""

    @staticmethod
    def on_action():
        active_window = app.activeWindow()
        try:
            fn = active_window.on_copy_file_name
        except AttributeError:
            try:
                fn = active_window.parent_window.on_copy_file_name
            except AttributeError:
                fn = lambda: None
        fn()

    def on_update_language(self):
        self._action.setText(tr("Copy File Name"))


class CopyFilePath(ActionInstance):
    _instance = None
    default_shortcut = ""

    @staticmethod
    def on_action():
        active_window = app.activeWindow()
        try:
            fn = active_window.on_copy_file_path
        except AttributeError:
            try:
                fn = active_window.parent_window.on_copy_file_path
            except AttributeError:
                fn = lambda: None
        fn()

    def on_update_language(self):
        self._action.setText(tr("Copy File Path"))


class LockText(ActionInstance):
    _instance = None
    default_shortcut = ""

    @staticmethod
    def on_action():
        active_window = app.activeWindow()
        try:
            fn = active_window.on_lock_text
        except AttributeError:
            try:
                fn = active_window.parent_window.on_lock_text
            except AttributeError:
                fn = lambda: None
        fn()

    def on_update_language(self):
        self._action.setText(tr("Lock Text"))


class LockAllTexts(ActionInstance):
    _instance = None
    default_shortcut = ""

    @staticmethod
    def on_action():
        active_window = app.activeWindow()
        try:
            fn = active_window.on_lock_all_texts
        except AttributeError:
            try:
                fn = active_window.parent_window.on_lock_all_texts
            except AttributeError:
                fn = lambda: None
        fn()

    def on_update_language(self):
        self._action.setText(tr("Lock All Texts"))


class UnlockText(ActionInstance):
    _instance = None
    default_shortcut = ""

    @staticmethod
    def on_action():
        active_window = app.activeWindow()
        try:
            fn = active_window.on_unlock_text
        except AttributeError:
            try:
                fn = active_window.parent_window.on_unlock_text
            except AttributeError:
                fn = lambda: None
        fn()

    def on_update_language(self):
        self._action.setText(tr("Unlock Text"))


class UnlockAllTexts(ActionInstance):
    _instance = None
    default_shortcut = ""

    @staticmethod
    def on_action():
        active_window = app.activeWindow()
        try:
            fn = active_window.on_unlock_all_texts
        except AttributeError:
            try:
                fn = active_window.parent_window.on_unlock_all_texts
            except AttributeError:
                fn = lambda: None
        fn()

    def on_update_language(self):
        self._action.setText(tr("Unlock All Texts"))


class CloseText(ActionInstance):
    _instance = None
    default_shortcut = ""

    @staticmethod
    def on_action():
        active_window = app.activeWindow()
        try:
            fn = active_window.on_close_text
        except AttributeError:
            try:
                fn = active_window.parent_window.on_close_text
            except AttributeError:
                fn = lambda: None
        fn()

    def on_update_language(self):
        self._action.setText(tr("Close Text"))


class CloseWindow(ActionInstance):
    _instance = None
    default_shortcut = "ctrl+w"

    @staticmethod
    def on_action():
        app.activeWindow().close()

    def on_update_language(self):
        self._action.setText(tr("Close Window"))


class CloseAllWindows(ActionInstance):
    _instance = None
    default_shortcut = "ctrl+q"

    @staticmethod
    def on_action():
        for window_ in window.Window.windows.copy():
            window_.close()

    def on_update_language(self):
        self._action.setText(tr("Close All Windows"))


class Settings(ActionInstance):
    _instance = None
    default_shortcut = ""

    @staticmethod
    def on_action():
        settings_window.SettingsWindow().show()

    def on_update_language(self):
        self._action.setText(tr("Settings..."))


class Undo(ActionInstance):
    _instance = None
    default_shortcut = "ctrl+z"

    @staticmethod
    def on_action():
        active_window = app.activeWindow()
        try:
            fn = active_window.focusWidget().on_undo
        except AttributeError:
            try:
                fn = active_window.parent_window.focusWidget().on_undo
            except AttributeError:
                try:
                    fn = active_window.on_undo
                except AttributeError:
                    fn = lambda: None
        fn()

    def on_update_language(self):
        self._action.setText(tr("Undo"))


class Redo(ActionInstance):
    _instance = None
    default_shortcut = "ctrl+y"

    @staticmethod
    def on_action():
        active_window = app.activeWindow()
        try:
            fn = active_window.focusWidget().on_redo
        except AttributeError:
            try:
                fn = active_window.parent_window.focusWidget().on_redo
            except AttributeError:
                try:
                    fn = active_window.on_redo
                except AttributeError:
                    fn = lambda: None
        fn()

    def on_update_language(self):
        self._action.setText(tr("Redo"))


class Cut(ActionInstance):
    _instance = None
    default_shortcut = "ctrl+x"

    @staticmethod
    def on_action():
        active_window = app.activeWindow()
        try:
            fn = active_window.focusWidget().on_cut
        except AttributeError:
            try:
                fn = active_window.on_cut
            except AttributeError:
                fn = lambda: None
        fn()

    def on_update_language(self):
        self._action.setText(tr("Cut"))


class Copy(ActionInstance):
    _instance = None
    default_shortcut = "ctrl+c"

    @staticmethod
    def on_action():
        active_window = app.activeWindow()
        try:
            fn = active_window.focusWidget().on_copy
        except AttributeError:
            try:
                fn = active_window.on_copy
            except AttributeError:
                fn = lambda: None
        fn()

    def on_update_language(self):
        self._action.setText(tr("Copy"))


class Paste(ActionInstance):
    _instance = None
    default_shortcut = "ctrl+v"

    @staticmethod
    def on_action():
        active_window = app.activeWindow()
        try:
            fn = active_window.focusWidget().on_paste
        except AttributeError:
            try:
                fn = active_window.on_paste
            except AttributeError:
                fn = lambda: None
        fn()

    def on_update_language(self):
        self._action.setText(tr("Paste"))


class Duplicate(ActionInstance):
    _instance = None
    default_shortcut = "ctrl+d"

    @staticmethod
    def on_action():
        active_window = app.activeWindow()
        focus_widget = active_window.focusWidget()
        try:
            fn = focus_widget.on_duplicate
        except AttributeError:
            try:
                fn = focus_widget.parent().on_duplicate
            except AttributeError:
                try:
                    fn = active_window.on_duplicate
                except AttributeError:
                    fn = lambda: None
        fn()

    def on_update_language(self):
        self._action.setText(tr("Duplicate"))


class Find(ActionInstance):
    _instance = None
    default_shortcut = "ctrl+f"

    @staticmethod
    def on_action():
        active_window = app.activeWindow()
        try:
            fn = active_window.focusWidget().on_find
        except AttributeError:
            try:
                fn = active_window.parent_window.focusWidget().on_find
            except AttributeError:
                try:
                    fn = active_window.on_find
                except AttributeError:
                    fn = lambda: None
        fn()

    def on_update_language(self):
        self._action.setText(tr("Find"))


class Replace(ActionInstance):
    _instance = None
    default_shortcut = "ctrl+r"

    @staticmethod
    def on_action():
        active_window = app.activeWindow()
        try:
            fn = active_window.focusWidget().on_replace
        except AttributeError:
            try:
                fn = active_window.parent_window.focusWidget().on_replace
            except AttributeError:
                fn = lambda: None
        fn()

    def on_update_language(self):
        self._action.setText(tr("Replace"))


class SelectAll(ActionInstance):
    _instance = None
    default_shortcut = "ctrl+a"

    @staticmethod
    def on_action():
        active_window = app.activeWindow()
        try:
            fn = active_window.focusWidget().on_select_all
        except AttributeError:
            try:
                fn = active_window.on_select_all
            except AttributeError:
                fn = lambda: None
        fn()

    def on_update_language(self):
        self._action.setText(tr("Select All"))


class ZoomIn(ActionInstance):
    _instance = None
    default_shortcut = "ctrl+="

    @staticmethod
    def on_action():
        try:
            fn = app.activeWindow().focusWidget().parent().on_zoom_in
        except AttributeError:
            fn = lambda: None
        fn()

    def on_update_language(self):
        self._action.setText(tr("Zoom In"))


class ZoomOut(ActionInstance):
    _instance = None
    default_shortcut = "ctrl+-"

    @staticmethod
    def on_action():
        try:
            fn = app.activeWindow().focusWidget().parent().on_zoom_out
        except AttributeError:
            fn = lambda: None
        fn()

    def on_update_language(self):
        self._action.setText(tr("Zoom Out"))


class ZoomDefault(ActionInstance):
    _instance = None
    default_shortcut = ""

    @staticmethod
    def on_action():
        try:
            fn = app.activeWindow().focusWidget().parent().on_zoom_default
        except AttributeError:
            fn = lambda: None
        fn()

    def on_update_language(self):
        self._action.setText(tr("Zoom Default"))


class LineUp(ActionInstance):
    _instance = None
    default_shortcut = "ctrl+up"

    @staticmethod
    def on_action():
        try:
            fn = app.activeWindow().focusWidget().parent().scrollbar.on_line_up
        except AttributeError:
            fn = lambda: None
        fn()

    def on_update_language(self):
        self._action.setText(tr("Line Up"))


class LineDown(ActionInstance):
    _instance = None
    default_shortcut = "ctrl+down"

    @staticmethod
    def on_action():
        try:
            fn = app.activeWindow().focusWidget().parent().scrollbar.on_line_down # fmt:skip
        except AttributeError:
            fn = lambda: None
        fn()

    def on_update_language(self):
        self._action.setText(tr("Line Down"))


class PageUp(ActionInstance):
    _instance = None
    default_shortcut = "pgup"

    @staticmethod
    def on_action():
        try:
            fn = app.activeWindow().focusWidget().parent().scrollbar.on_page_up # fmt:skip
        except AttributeError:
            fn = lambda: None
        fn()

    def on_update_language(self):
        self._action.setText(tr("Page Up"))


class PageDown(ActionInstance):
    _instance = None
    default_shortcut = "pgdown"

    @staticmethod
    def on_action():
        try:
            fn = app.activeWindow().focusWidget().parent().scrollbar.on_page_down # fmt:skip
        except AttributeError:
            fn = lambda: None
        fn()

    def on_update_language(self):
        self._action.setText(tr("Page Down"))


class MoveTextLeft(ActionInstance):
    _instance = None
    default_shortcut = ""

    @staticmethod
    def on_action():
        try:
            fn = app.activeWindow().on_move_text_left
        except AttributeError:
            fn = lambda: None
        fn()

    def on_update_language(self):
        if (
            settings.text_editor_splitter_orientation
            == settings.Orientation.HORIZONTAL
        ):
            self._action.setText(tr("Move Text Left"))
        else:
            self._action.setText(tr("Move Text Up"))


class MoveTextRight(ActionInstance):
    _instance = None
    default_shortcut = ""

    @staticmethod
    def on_action():
        try:
            fn = app.activeWindow().on_move_text_right
        except AttributeError:
            fn = lambda: None
        fn()

    def on_update_language(self):
        if (
            settings.text_editor_splitter_orientation
            == settings.Orientation.HORIZONTAL
        ):
            self._action.setText(tr("Move Text Right"))
        else:
            self._action.setText(tr("Move Text Down"))


class CreateEntry(ActionInstance):
    _instance = None
    default_shortcut = ""

    @staticmethod
    def on_action():
        active_window = app.activeWindow()
        dict_views = active_window.findChildren(dict_view.DictView)
        entries_created = 0
        for dict_view_ in dict_views:
            try:
                if dict_view_.db is None:
                    continue
                fn = dict_view_.on_create_entry
                entries_created += 1
            except AttributeError:
                fn = lambda: None
            fn()
        if not entries_created:
            try:
                db = active_window.db
                if db is not None:
                    fn = dict_entry_window.DictEntryWindow(db).show
                    entries_created += 1
                else:
                    fn = lambda: None
            except AttributeError:
                fn = lambda: None
            fn()
        if not entries_created:
            messages.NoDictionarySelectedErrorMessage().show()

    def on_update_language(self):
        self._action.setText(tr("Create Entry..."))


class EditEntry(ActionInstance):
    _instance = None
    default_shortcut = ""

    @staticmethod
    def on_action():
        active_window = app.activeWindow()
        if isinstance(active_window, dict_entry_window.DictEntryWindow):
            return
        dict_views = active_window.findChildren(dict_view.DictView)
        entries_selected = set()
        for dict_view_ in dict_views:
            try:
                if dict_view_.db is None:
                    continue
                fn = dict_view_.on_edit_entry
                entries_selected.update(dict_view_.entry_ids)
            except AttributeError:
                fn = lambda: None
            fn()
        if not entries_selected:
            messages.NoEntrySelectedErrorMessage().show()

    def on_update_language(self):
        self._action.setText(tr("Edit Entry..."))


class CreateTemplate(ActionInstance):
    _instance = None
    default_shortcut = ""

    @staticmethod
    def on_action():
        active_window = app.activeWindow()
        dict_views = active_window.findChildren(dict_view.DictView)
        entries_created = 0
        for dict_view_ in dict_views:
            try:
                fn = dict_view_.on_create_template
                entries_created += 1
            except AttributeError:
                fn = lambda: None
            fn()
        if not entries_created:
            try:
                db = active_window.db
                fn = dict_template_window.DictTemplateWindow(db).show
                entries_created += 1
            except AttributeError:
                fn = lambda: None
            fn()
        if not entries_created:
            messages.NoDictionarySelectedErrorMessage().show()

    def on_update_language(self):
        self._action.setText(tr("Create Template..."))


class EditTemplate(ActionInstance):
    _instance = None
    default_shortcut = ""

    @staticmethod
    def on_action():
        active_window = app.activeWindow()
        if isinstance(active_window, dict_template_window.DictTemplateWindow):
            return
        try:
            fn = active_window.on_edit_selected_template
        except AttributeError:
            fn = lambda: None
            messages.NoTemplateSelectedErrorMessage().show()
        fn()

    def on_update_language(self):
        self._action.setText(tr("Edit Template..."))


class CreateDictionary(ActionInstance):
    _instance = None
    default_shortcut = ""

    @staticmethod
    def on_action():
        name = dict_database_file.on_create_dict_database_file()
        if name is None:
            return
        dict_settings_window_ = dict_settings_window.DictSettingsWindow()
        dict_settings_window_.dict_combo_box.set_name(name)
        dict_settings_window_.show()

    def on_update_language(self):
        self._action.setText(tr("Create Dictionary..."))


class ImportDictionary(ActionInstance):
    _instance = None
    default_shortcut = ""

    @staticmethod
    def on_action():
        def on_success(name):
            dict_settings_window_ = dict_settings_window.DictSettingsWindow()
            dict_settings_window_.dict_combo_box.set_name(name)
            dict_settings_window_.show()

        dict_database_file.on_import_dict_database_file(on_success=on_success)

    def on_update_language(self):
        self._action.setText(tr("Import Dictionary..."))


class ManageDictionaries(ActionInstance):
    _instance = None
    default_shortcut = ""

    @staticmethod
    def on_action():
        os.makedirs(settings.dict_dir, exist_ok=True)
        if system.os_type == system.MAC_OS:
            os.system(f'open "{settings.dict_dir}"')
        else:
            QDesktopServices.openUrl(
                QDir.fromNativeSeparators(settings.dict_dir)
            )

    def on_update_language(self):
        self._action.setText(tr("Manage Dictionaries..."))


class Dictionary(ActionInstance):
    _instance = None
    default_shortcut = ""

    @staticmethod
    def on_action():
        dict_window.DictWindow().show()

    def on_update_language(self):
        self._action.setText(tr("Dictionary"))


class DictionarySettings(ActionInstance):
    _instance = None
    default_shortcut = ""

    @staticmethod
    def on_action():
        dict_settings_window.DictSettingsWindow().show()

    def on_update_language(self):
        self._action.setText(tr("Dictionary Settings..."))


class AddAbove(ActionInstance):
    _instance = None
    default_shortcut = ""

    @staticmethod
    def on_action():
        active_window = app.activeWindow()
        focus_widget = active_window.focusWidget()
        try:
            fn = focus_widget.on_add_above
        except AttributeError:
            try:
                fn = focus_widget.parent().on_add_above
            except AttributeError:
                try:
                    fn = active_window.on_add_above
                except AttributeError:
                    fn = lambda: None
        fn()

    def on_update_language(self):
        self._action.setText(tr("Add Above"))


class AddBelow(ActionInstance):
    _instance = None
    default_shortcut = "ctrl+return"

    @staticmethod
    def on_action():
        active_window = app.activeWindow()
        focus_widget = active_window.focusWidget()
        try:
            fn = focus_widget.on_add_below
        except AttributeError:
            try:
                fn = focus_widget.parent().on_add_below
            except AttributeError:
                try:
                    fn = active_window.on_add_below
                except AttributeError:
                    fn = lambda: None
        fn()

    def on_update_language(self):
        self._action.setText(tr("Add Below"))


class MoveUp(ActionInstance):
    _instance = None
    default_shortcut = ""

    @staticmethod
    def on_action():
        active_window = app.activeWindow()
        focus_widget = active_window.focusWidget()
        try:
            fn = focus_widget.on_move_up
        except AttributeError:
            try:
                fn = focus_widget.parent().on_move_up
            except AttributeError:
                try:
                    fn = active_window.on_move_up
                except AttributeError:
                    fn = lambda: None
        fn()

    def on_update_language(self):
        self._action.setText(tr("Move Up"))


class MoveDown(ActionInstance):
    _instance = None
    default_shortcut = ""

    @staticmethod
    def on_action():
        active_window = app.activeWindow()
        focus_widget = active_window.focusWidget()
        try:
            fn = focus_widget.on_move_down
        except AttributeError:
            try:
                fn = focus_widget.parent().on_move_down
            except AttributeError:
                try:
                    fn = active_window.on_move_down
                except AttributeError:
                    fn = lambda: None
        fn()

    def on_update_language(self):
        self._action.setText(tr("Move Down"))


class MoveToTop(ActionInstance):
    _instance = None
    default_shortcut = ""

    @staticmethod
    def on_action():
        active_window = app.activeWindow()
        focus_widget = active_window.focusWidget()
        try:
            fn = focus_widget.on_move_to_top
        except AttributeError:
            try:
                fn = focus_widget.parent().on_move_to_top
            except AttributeError:
                try:
                    fn = active_window.on_move_to_top
                except AttributeError:
                    fn = lambda: None
        fn()

    def on_update_language(self):
        self._action.setText(tr("Move To Top"))


class MoveToBottom(ActionInstance):
    _instance = None
    default_shortcut = ""

    @staticmethod
    def on_action():
        active_window = app.activeWindow()
        focus_widget = active_window.focusWidget()
        try:
            fn = focus_widget.on_move_to_bottom
        except AttributeError:
            try:
                fn = focus_widget.parent().on_move_to_bottom
            except AttributeError:
                try:
                    fn = active_window.on_move_to_bottom
                except AttributeError:
                    fn = lambda: None
        fn()

    def on_update_language(self):
        self._action.setText(tr("Move To Bottom"))


class Delete(ActionInstance):
    _instance = None
    default_shortcut = "ctrl+backspace"

    @staticmethod
    def on_action():
        active_window = app.activeWindow()
        focus_widget = active_window.focusWidget()
        try:
            fn = focus_widget.on_delete
        except AttributeError:
            try:
                fn = focus_widget.parent().on_delete
            except AttributeError:
                try:
                    fn = active_window.on_delete
                except AttributeError:
                    fn = lambda: None
        fn()

    def on_update_language(self):
        self._action.setText(tr("Delete"))


class AddTag(ActionInstance):
    _instance = None
    default_shortcut = ""

    @staticmethod
    def on_action():
        try:
            fn = app.activeWindow().focusWidget().on_add_tag
        except AttributeError:
            fn = lambda: None
        fn()

    def on_update_language(self):
        self._action.setText(tr("Add Tag"))


class PreviousForm(ActionInstance):
    _instance = None
    default_shortcut = "ctrl+up"

    @staticmethod
    def on_action():
        try:
            fn = app.activeWindow().focusWidget().on_previous_form
        except AttributeError:
            fn = lambda: None
        fn()

    def on_update_language(self):
        self._action.setText(tr("Previous Form"))


class NextForm(ActionInstance):
    _instance = None
    default_shortcut = "ctrl+down"

    @staticmethod
    def on_action():
        try:
            fn = app.activeWindow().focusWidget().on_next_form
        except AttributeError:
            fn = lambda: None
        fn()

    def on_update_language(self):
        self._action.setText(tr("Next Form"))


class PreviousTagValue(ActionInstance):
    _instance = None
    default_shortcut = "up"

    @staticmethod
    def on_action():
        try:
            fn = app.activeWindow().focusWidget().on_previous_tag_value
        except AttributeError:
            fn = lambda: None
        fn()

    def on_update_language(self):
        self._action.setText(tr("Previous Tag Value"))


class PreviousTagValueAlt1(ActionInstance):
    _instance = None
    default_shortcut = "shift+return"

    @staticmethod
    def on_action():
        try:
            fn = app.activeWindow().focusWidget().on_previous_tag_value
        except AttributeError:
            fn = lambda: None
        fn()

    def on_update_language(self):
        self._action.setText(
            f'{tr("Previous Tag Value")} {tr("Alternative 1")}'
        )


class PreviousTagValueAlt2(ActionInstance):
    _instance = None
    default_shortcut = "shift+backtab"

    @staticmethod
    def on_action():
        try:
            fn = app.activeWindow().focusWidget().on_previous_tag_value
        except AttributeError:
            fn = lambda: None
        fn()

    def on_update_language(self):
        self._action.setText(
            f'{tr("Previous Tag Value")} {tr("Alternative 2")}'
        )


class NextTagValue(ActionInstance):
    _instance = None
    default_shortcut = "down"

    @staticmethod
    def on_action():
        try:
            fn = app.activeWindow().focusWidget().on_next_tag_value
        except AttributeError:
            fn = lambda: None
        fn()

    def on_update_language(self):
        self._action.setText(tr("Next Tag Value"))


class NextTagValueAlt1(ActionInstance):
    _instance = None
    default_shortcut = "return"

    @staticmethod
    def on_action():
        try:
            fn = app.activeWindow().focusWidget().on_next_tag_value
        except AttributeError:
            fn = lambda: None
        fn()

    def on_update_language(self):
        self._action.setText(f'{tr("Next Tag Value")} {tr("Alternative 1")}')


class NextTagValueAlt2(ActionInstance):
    _instance = None
    default_shortcut = "tab"

    @staticmethod
    def on_action():
        try:
            fn = app.activeWindow().focusWidget().on_next_tag_value
        except AttributeError:
            fn = lambda: None
        fn()

    def on_update_language(self):
        self._action.setText(f'{tr("Next Tag Value")} {tr("Alternative 2")}')


class MovePopupForward(ActionInstance):
    _instance = None
    default_shortcut = "tab"

    @staticmethod
    def on_action():
        try:
            fn = app.activeWindow().on_move_popup_forward
        except AttributeError:
            fn = lambda: None
        fn()

    def on_update_language(self):
        self._action.setText(tr("Move Popup Forward"))


class MovePopupBackward(ActionInstance):
    _instance = None
    default_shortcut = "shift+backtab"

    @staticmethod
    def on_action():
        try:
            fn = app.activeWindow().on_move_popup_backward
        except AttributeError:
            fn = lambda: None
        fn()

    def on_update_language(self):
        self._action.setText(tr("Move Popup Backward"))


class About(ActionInstance):
    _instance = None
    default_shortcut = ""

    @staticmethod
    def on_action():
        messages.AboutInfoMessage().show()

    def on_update_language(self):
        self._action.setText(tr("About"))


post_keys = set(globals().keys())
class_keys = post_keys - pre_keys - {"pre_keys"}
classes = [globals()[key] for key in class_keys]


def update_shortcuts():
    app.shortcut_to_action_fn.clear()
    for class_ in classes:
        try:
            app.shortcut_to_action_fn[class_.shortcut()].append(
                class_.on_action
            )
        except KeyError:
            app.shortcut_to_action_fn[class_.shortcut()] = [class_.on_action]


update_shortcuts()
