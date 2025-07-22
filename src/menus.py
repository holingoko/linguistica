import os
import shutil

from src import actions
from src import app_info
from src import dict_database_file
from src import examples
from src import main_window
from src import settings
from src import state
from src import utils
from src.language import tr
from src.qt import *


class MenuBar(QMenuBar):
    def __init__(self, window_):
        super().__init__()
        self.window = window_
        self.file = FileMenu(window_)
        self.edit = EditMenu(window_)
        self.view = ViewMenu(window_)
        self.dictionary = DictionaryMenu(window_)
        self.help = HelpMenu(window_)
        self.addMenu(self.file)
        self.addMenu(self.edit)
        self.addMenu(self.view)
        self.addMenu(self.dictionary)
        self.addMenu(self.help)


class DictMenuBar(QMenuBar):
    def __init__(self, window_):
        super().__init__()
        self.window = window_
        self.file = DictFileMenu(window_)
        self.dictionary = DictionaryMenu(window_)
        self.help = HelpMenu(window_)
        self.addMenu(self.file)
        self.addMenu(self.dictionary)
        self.addMenu(self.help)


class FileMenu(QMenu):
    def __init__(self, window_):
        super().__init__(window_)
        self.open_recent_text = OpenRecentTextMenu(window_)
        self.open_recent_window = OpenRecentWindowMenu(window_)
        self.addAction(actions.NewText.action())
        self.addAction(actions.NewTextWindow.action())
        self.addSeparator()
        self.addAction(actions.OpenText.action())
        self.addMenu(self.open_recent_text)
        self.addMenu(self.open_recent_window)
        self.addSeparator()
        self.addAction(actions.SaveText.action())
        self.addAction(actions.SaveTextAs.action())
        self.addAction(actions.SaveAllTexts.action())
        self.addSeparator()
        self.addAction(actions.RenameText.action())
        self.addSeparator()
        self.addAction(actions.CopyFileName.action())
        self.addAction(actions.CopyFilePath.action())
        self.addSeparator()
        self.addAction(actions.LockText.action())
        self.addAction(actions.LockAllTexts.action())
        self.addSeparator()
        self.addAction(actions.UnlockText.action())
        self.addAction(actions.UnlockAllTexts.action())
        self.addSeparator()
        self.addAction(actions.CloseText.action())
        self.addAction(actions.CloseWindow.action())
        self.addAction(actions.CloseAllWindows.action())
        self.addSeparator()
        self.addAction(actions.Settings.action())
        self.addSeparator()
        self.on_update_language()

    def on_update_language(self):
        self.setTitle(tr("File"))


class DictFileMenu(QMenu):
    def __init__(self, window_):
        super().__init__(window_)
        self.open_recent_text = OpenRecentTextMenu(window_)
        self.open_recent_window = OpenRecentWindowMenu(window_)
        self.addAction(actions.NewText.action())
        self.addAction(actions.NewTextWindow.action())
        self.addSeparator()
        self.addAction(actions.OpenText.action())
        self.addMenu(self.open_recent_text)
        self.addMenu(self.open_recent_window)
        self.addSeparator()
        self.addAction(actions.SaveWindow.action())
        self.addSeparator()
        self.addAction(actions.CloseWindow.action())
        self.addAction(actions.CloseAllWindows.action())
        self.addSeparator()
        self.addAction(actions.Settings.action())
        self.addSeparator()
        self.on_update_language()

    def on_update_language(self):
        self.setTitle(tr("File"))


class EditMenu(QMenu):
    def __init__(self, window_):
        super().__init__(window_)
        self.addAction(actions.Undo.action())
        self.addAction(actions.Redo.action())
        self.addSeparator()
        self.addAction(actions.Cut.action())
        self.addAction(actions.Copy.action())
        self.addAction(actions.Paste.action())
        self.addSeparator()
        self.addAction(actions.Find.action())
        self.addAction(actions.Replace.action())
        self.addSeparator()
        self.addAction(actions.SelectAll.action())
        self.addSeparator()
        self.on_update_language()

    def on_update_language(self):
        self.setTitle(tr("Edit"))


class ViewMenu(QMenu):
    def __init__(self, window_):
        super().__init__(window_)
        self.addAction(actions.ZoomIn.action())
        self.addAction(actions.ZoomOut.action())
        self.addAction(actions.ZoomDefault.action())
        self.addSeparator()
        self.addAction(actions.LineUp.action())
        self.addAction(actions.LineDown.action())
        self.addSeparator()
        self.addAction(actions.PageUp.action())
        self.addAction(actions.PageDown.action())
        self.addSeparator()
        self.addAction(actions.MoveTextLeft.action())
        self.addAction(actions.MoveTextRight.action())
        self.addSeparator()
        self.on_update_language()

    def on_update_language(self):
        self.setTitle(tr("View"))


class DictionaryMenu(QMenu):
    def __init__(self, window_):
        super().__init__(window_)
        self.export_dictionary = ExportDictionaryMenu(window_)
        self.addAction(actions.CreateEntry.action())
        self.addAction(actions.EditEntry.action())
        self.addSeparator()
        self.addAction(actions.CreateTemplate.action())
        self.addAction(actions.EditTemplate.action())
        self.addSeparator()
        self.addAction(actions.CreateDictionary.action())
        self.addAction(actions.ImportDictionary.action())
        self.addMenu(self.export_dictionary)
        self.addAction(actions.ManageDictionaries.action())
        self.addSeparator()
        self.addAction(actions.Dictionary.action())
        self.addAction(actions.DictionarySettings.action())
        self.addSeparator()
        self.on_update_language()

    def on_update_language(self):
        self.setTitle(tr("Dictionary"))


class HelpMenu(QMenu):
    def __init__(self, window_):
        super().__init__(window_)
        self.examples = Examples(window_)
        self.source_code = SourceCode(window_)
        self.addAction(actions.About.action())
        self.addMenu(self.examples)
        self.addMenu(self.source_code)
        self.addSeparator()
        self.on_update_language()

    def on_update_language(self):
        self.setTitle(tr("Help"))


class TextEditorContextMenu(QMenu):
    def __init__(self, window_):
        super().__init__(window_)
        self.addAction(actions.NewText.action())
        self.addSeparator()
        self.addAction(actions.OpenText.action())
        self.addSeparator()
        self.addAction(actions.SaveText.action())
        self.addAction(actions.SaveTextAs.action())
        self.addSeparator()
        self.addAction(actions.RenameText.action())
        self.addSeparator()
        self.addAction(actions.CopyFileName.action())
        self.addAction(actions.CopyFilePath.action())
        self.addSeparator()
        self.addAction(actions.LockText.action())
        self.addAction(actions.UnlockText.action())
        self.addSeparator()
        self.addAction(actions.MoveTextLeft.action())
        self.addAction(actions.MoveTextRight.action())
        self.addSeparator()
        self.addAction(actions.CloseText.action())
        self.addSeparator()


class LineEditContextMenu(QMenu):
    def __init__(self, window_):
        super().__init__(window_)
        self.addAction(actions.Undo.action())
        self.addAction(actions.Redo.action())
        self.addSeparator()
        self.addAction(actions.Cut.action())
        self.addAction(actions.Copy.action())
        self.addAction(actions.Paste.action())
        self.addSeparator()
        self.addAction(actions.SelectAll.action())
        self.addSeparator()


class LabelContextMenu(QMenu):
    def __init__(self, window_):
        super().__init__(window_)
        self.addAction(actions.Copy.action())
        self.addAction(actions.SelectAll.action())
        self.addSeparator()


class TagEditOrFormEditContextMenu(QMenu):
    def __init__(self, window_):
        super().__init__(window_)
        self.addAction(actions.Undo.action())
        self.addAction(actions.Redo.action())
        self.addSeparator()
        self.addAction(actions.Cut.action())
        self.addAction(actions.Copy.action())
        self.addAction(actions.Paste.action())
        self.addSeparator()
        self.addAction(actions.Duplicate.action())
        self.addSeparator()
        self.addAction(actions.AddAbove.action())
        self.addAction(actions.AddBelow.action())
        self.addSeparator()
        self.addAction(actions.MoveUp.action())
        self.addAction(actions.MoveDown.action())
        self.addSeparator()
        self.addAction(actions.MoveToTop.action())
        self.addAction(actions.MoveToBottom.action())
        self.addSeparator()
        self.addAction(actions.Delete.action())
        self.addSeparator()


class TagFrameContextMenu(QMenu):
    def __init__(self, window_):
        super().__init__(window_)
        self.addAction(actions.Undo.action())
        self.addAction(actions.Redo.action())
        self.addSeparator()
        self.addAction(actions.AddTag.action())
        self.addSeparator()


class DictViewContextMenu(QMenu):
    def __init__(self, window_):
        super().__init__(window_)
        self.addAction(actions.Copy.action())
        self.addAction(actions.SelectAll.action())
        self.addSeparator()
        self.addAction(actions.CreateEntry.action())
        self.addAction(actions.EditEntry.action())
        self.addSeparator()


class OpenRecentTextMenu(QMenu):
    def __init__(self, window_):
        super().__init__(window_)
        self.window = window_
        self.action_list = []
        self.clear_ = QAction()
        self.clear_.triggered.connect(self.on_clear)
        self.aboutToShow.connect(self.on_about_to_show)
        self.on_update_language()

    def on_about_to_show(self):
        self.clear()
        self.action_list.clear()
        for path, _ in sorted(
            state.texts.items(),
            key=lambda x: x[1][0],
            reverse=True,
        )[: settings.app_num_recents]:
            if not os.path.exists(path):
                continue
            action = QAction(path)
            self.action_list.append(action)
            self.addAction(action)
            action.triggered.connect(
                lambda _, path_=path: self.on_action(path_)
            )
        self.addSeparator()
        self.addAction(self.clear_)

    def on_action(self, path):
        try:
            fn = self.window.on_open_text
        except AttributeError:
            fn = main_window.MainWindow.create_window_and_open_text
        fn(path)

    @staticmethod
    def on_clear():
        state.texts.clear()

    def on_update_language(self):
        self.setTitle(tr("Open Recent Text"))
        self.clear_.setText(tr("Clear"))


class OpenRecentWindowMenu(QMenu):
    def __init__(self, window_):
        super().__init__(window_)
        self.action_list = []
        self.clear_ = QAction()
        self.clear_.triggered.connect(self.on_clear)
        self.aboutToShow.connect(self.on_about_to_show)
        self.on_update_language()

    def on_about_to_show(self):
        self.clear()
        self.action_list.clear()
        for paths, (_, window_state) in sorted(
            state.windows.items(),
            key=lambda x: x[1][0],
            reverse=True,
        )[: settings.app_num_recents]:
            continue_ = False
            for path in paths.split(state.PATH_SEPARATOR):
                if not os.path.exists(path):
                    continue_ = True
                    break
            if continue_:
                continue
            action = QAction(paths)
            self.action_list.append(action)
            self.addAction(action)
            action.triggered.connect(
                lambda _, window_state_=window_state: self.on_action(
                    window_state_
                )
            )
        self.addSeparator()
        self.addAction(self.clear_)

    @staticmethod
    def on_action(window_state):
        main_window.MainWindow(window_state).show()

    @staticmethod
    def on_clear():
        state.windows.clear()

    def on_update_language(self):
        self.setTitle(tr("Open Recent Window"))
        self.clear_.setText(tr("Clear"))


class ExportDictionaryMenu(QMenu):
    def __init__(self, window_):
        super().__init__(window_)
        self.action_list = []
        self.aboutToShow.connect(self.on_about_to_show)
        self.on_update_language()

    def on_about_to_show(self):
        self.clear()
        self.action_list.clear()
        for name in utils.get_dict_list():
            action = QAction(name)
            self.action_list.append(action)
            self.addAction(action)
            action.triggered.connect(
                lambda _, name_=name: self.on_action(name_)
            )

    @staticmethod
    def on_action(name):
        dict_database_file.on_export_dict_database_file(name)

    def on_update_language(self):
        self.setTitle(tr("Export Dictionary..."))


class Examples(QMenu):
    def __init__(self, window_):
        super().__init__(window_)
        self.addMenu(CreateEntryMenu(window_))
        self.addMenu(CreateTemplateMenu(window_))
        self.addMenu(SetEntryFormat(window_))
        self.addMenu(SetTagValuesFormat(window_))
        self.addSeparator()
        self.on_update_language()

    def on_update_language(self):
        self.setTitle(tr("Examples"))


class CreateEntryMenu(QMenu):
    def __init__(self, window_):
        super().__init__(window_)
        self.english = QAction()
        self.mandarin_chinese = QAction()
        self.hindi = QAction()
        self.spanish = QAction()
        self.arabic = QAction()
        self.french = QAction()
        self.bangla = QAction()
        self.portuguese = QAction()
        self.russian = QAction()
        self.indonesian = QAction()
        self.urdu = QAction()
        self.german = QAction()
        self.japanese = QAction()
        self.latin = QAction()
        self.addAction(self.english)
        self.addAction(self.mandarin_chinese)
        self.addAction(self.hindi)
        self.addAction(self.spanish)
        self.addAction(self.arabic)
        self.addAction(self.french)
        self.addAction(self.bangla)
        self.addAction(self.portuguese)
        self.addAction(self.russian)
        self.addAction(self.indonesian)
        self.addAction(self.urdu)
        self.addAction(self.german)
        self.addAction(self.japanese)
        self.addAction(self.latin)
        self.addSeparator()
        self.english.triggered.connect(self.on_english)
        self.mandarin_chinese.triggered.connect(self.on_mandarin_chinese) # fmt:skip
        self.hindi.triggered.connect(self.on_hindi)
        self.spanish.triggered.connect(self.on_spanish)
        self.arabic.triggered.connect(self.on_arabic)
        self.french.triggered.connect(self.on_french)
        self.bangla.triggered.connect(self.on_bangla)
        self.portuguese.triggered.connect(self.on_portuguese)
        self.russian.triggered.connect(self.on_russian)
        self.indonesian.triggered.connect(self.on_indonesian)
        self.urdu.triggered.connect(self.on_urdu)
        self.german.triggered.connect(self.on_german)
        self.japanese.triggered.connect(self.on_japanese)
        self.latin.triggered.connect(self.on_latin)
        self.on_update_language()

    @staticmethod
    def on_english():
        examples.create_entry_english()

    @staticmethod
    def on_mandarin_chinese():
        examples.create_entry_mandarin_chinese()

    @staticmethod
    def on_hindi():
        examples.create_entry_hindi()

    @staticmethod
    def on_spanish():
        examples.create_entry_spanish()

    @staticmethod
    def on_arabic():
        examples.create_entry_arabic()

    @staticmethod
    def on_french():
        examples.create_entry_french()

    @staticmethod
    def on_bangla():
        examples.create_entry_bangla()

    @staticmethod
    def on_portuguese():
        examples.create_entry_portuguese()

    @staticmethod
    def on_russian():
        examples.create_entry_russian()

    @staticmethod
    def on_indonesian():
        examples.create_entry_indonesian()

    @staticmethod
    def on_urdu():
        examples.create_entry_urdu()

    @staticmethod
    def on_german():
        examples.create_entry_german()

    @staticmethod
    def on_japanese():
        examples.create_entry_japanese()

    @staticmethod
    def on_latin():
        examples.create_entry_latin()

    def on_update_language(self):
        self.setTitle(tr("Create Entry"))
        self.english.setText(tr("English"))
        self.mandarin_chinese.setText(tr("Mandarin Chinese"))
        self.hindi.setText(tr("Hindi"))
        self.spanish.setText(tr("Spanish"))
        self.arabic.setText(tr("Arabic"))
        self.french.setText(tr("French"))
        self.bangla.setText(tr("Bangla"))
        self.portuguese.setText(tr("Portuguese"))
        self.russian.setText(tr("Russian"))
        self.indonesian.setText(tr("Indonesian"))
        self.urdu.setText(tr("Urdu"))
        self.german.setText(tr("German"))
        self.japanese.setText(tr("Japanese"))
        self.latin.setText(tr("Latin"))


class CreateTemplateMenu(CreateEntryMenu):
    def __init__(self, window_):
        super().__init__(window_)
        self.removeAction(self.mandarin_chinese)
        self.removeAction(self.arabic)
        self.removeAction(self.bangla)
        self.removeAction(self.indonesian)
        self.removeAction(self.urdu)
        self.removeAction(self.japanese)

    @staticmethod
    def on_english():
        examples.create_template_english()

    @staticmethod
    def on_hindi():
        examples.create_template_hindi()

    @staticmethod
    def on_spanish():
        examples.create_template_spanish()

    @staticmethod
    def on_french():
        examples.create_template_french()

    @staticmethod
    def on_portuguese():
        examples.create_template_portuguese()

    @staticmethod
    def on_russian():
        examples.create_template_russian()

    @staticmethod
    def on_german():
        examples.create_template_german()

    @staticmethod
    def on_latin():
        examples.create_template_latin()

    def on_update_language(self):
        super().on_update_language()
        self.setTitle(tr("Create Template"))


class SetEntryFormat(QMenu):
    def __init__(self, window_):
        super().__init__(window_)
        self.simple = QAction()
        self.conditional_statements = QAction()
        self.html = QAction()
        self.escaped_characters = QAction()
        self.right_to_left_language = QAction()
        self.addAction(self.simple)
        self.addAction(self.conditional_statements)
        self.addAction(self.html)
        self.addAction(self.escaped_characters)
        self.simple.triggered.connect(self.on_simple)
        self.conditional_statements.triggered.connect(self.on_conditional_statements) # fmt:skip
        self.html.triggered.connect(self.on_html)
        self.escaped_characters.triggered.connect(self.on_escaped_characters)
        self.on_update_language()

    @staticmethod
    def on_simple():
        examples.set_entry_format_simple()

    @staticmethod
    def on_conditional_statements():
        examples.set_entry_format_conditional_statements()

    @staticmethod
    def on_html():
        examples.set_entry_format_html()

    @staticmethod
    def on_escaped_characters():
        examples.set_entry_format_escaped_curly_braces()

    def on_update_language(self):
        self.setTitle(tr("Set Entry Format"))
        self.simple.setText(tr("Simple"))
        self.conditional_statements.setText(tr("Conditional Statements"))
        self.html.setText(tr("HTML"))
        self.escaped_characters.setText(tr("Escaped Curly Braces"))


class SetTagValuesFormat(SetEntryFormat):
    def __init__(self, window_):
        super().__init__(window_)
        self.addAction(self.right_to_left_language)
        self.right_to_left_language.triggered.connect(self.on_right_to_left_language) # fmt:skip

    @staticmethod
    def on_simple():
        examples.set_tag_values_format_simple()

    @staticmethod
    def on_conditional_statements():
        examples.set_tag_values_format_conditional_statements()

    @staticmethod
    def on_html():
        examples.set_tag_values_format_html()

    @staticmethod
    def on_escaped_characters():
        examples.set_tag_values_format_escaped_ellipsis()

    @staticmethod
    def on_right_to_left_language():
        examples.set_tag_values_format_right_to_left_language()

    def on_update_language(self):
        super().on_update_language()
        self.setTitle(tr("Set Tag Values Format"))
        self.escaped_characters.setText(tr("Escaped Ellipsis"))
        self.right_to_left_language.setText("Right To Left Language")


class SourceCode(QMenu):
    def __init__(self, window_):
        super().__init__(window_)
        self.local = QAction()
        self.remote = QAction()
        self.addAction(self.local)
        self.addAction(self.remote)
        self.addSeparator()
        self.local.triggered.connect(self.on_local)
        self.remote.triggered.connect(self.on_remote)
        self.on_update_language()

    def on_local(self):
        repo_dir = os.path.dirname(os.path.dirname(__file__))
        zip_name = f"{app_info.name.lower()}.zip"
        zip_path = os.path.join(repo_dir, "resources", zip_name)
        path = utils.get_save_file_name(
            self,
            tr("Save"),
            zip_name,
        )
        if not path:
            return
        shutil.copyfile(zip_path, path)

    @staticmethod
    def on_remote():
        QDesktopServices.openUrl(QUrl(app_info.github))

    def on_update_language(self):
        self.setTitle(tr("Source Code"))
        self.local.setText(tr("Local"))
        self.remote.setText(tr("Remote"))
