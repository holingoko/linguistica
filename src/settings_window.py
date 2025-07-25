import os
import shutil

from src import actions
from src import app_info
from src import buttons
from src import label
from src import line_edit
from src import messages
from src import reinit_app
from src import scroll_area
from src import settings
from src import settings_widgets
from src import window
from src.language import tr
from src.qt import *


APPLICATION_TAB = "APPLICATION_TAB"
TEXT_EDITOR_TAB = "TEXT_EDITOR_TAB"
DICTIONARY_TAB = "DICTIONARY_TAB"
SHORTCUTS_TAB = "SHORTCUTS_TAB"
MESSAGES_TAB = "MESSAGES_TAB"


class SettingsWindow(window.Window):
    instance = [None]

    def __init__(self):
        if self.instance[0] is None:
            self.instance[0] = self
        else:
            self.show = self.instance[0].raise_
            return
        super().__init__()
        self.filter = QWidget()
        self.filter_label = label.Label()
        self.filter_line_edit = line_edit.LineEdit(self)
        self.filter.setLayout(QHBoxLayout())
        self.filter.layout().addStretch()
        self.filter.layout().addWidget(self.filter_label)
        self.filter.layout().addWidget(self.filter_line_edit)
        self.filter.layout().addStretch()
        self.application_button = buttons.TabButton(
            lambda: self.on_tab(APPLICATION_TAB)
        )
        self.text_editor_button = buttons.TabButton(
            lambda: self.on_tab(TEXT_EDITOR_TAB)
        )
        self.dictionary_button = buttons.TabButton(
            lambda: self.on_tab(DICTIONARY_TAB)
        )
        self.shortcuts_button = buttons.TabButton(
            lambda: self.on_tab(SHORTCUTS_TAB)
        )
        self.messages_button = buttons.TabButton(
            lambda: self.on_tab(MESSAGES_TAB)
        )
        self.tab_side_bar = TabSideBar()
        self.tab_side_bar.setLayout(QVBoxLayout())
        self.tab_side_bar.layout().addWidget(self.application_button)
        self.tab_side_bar.layout().addWidget(self.text_editor_button)
        self.tab_side_bar.layout().addWidget(self.dictionary_button)
        self.tab_side_bar.layout().addWidget(self.shortcuts_button)
        self.tab_side_bar.layout().addWidget(self.messages_button)
        self.tab_side_bar.layout().addStretch()
        self.tab_side_bar.layout().setSpacing(0)
        self.tab_side_bar.layout().setContentsMargins(0, 0, 0, 0)
        self.tab_widgets = {
            APPLICATION_TAB: scroll_area.ScrollArea(ApplicationTab()),
            TEXT_EDITOR_TAB: scroll_area.ScrollArea(TextEditorTab()),
            DICTIONARY_TAB: scroll_area.ScrollArea(DictionaryTab()),
            SHORTCUTS_TAB: scroll_area.ScrollArea(ShortcutsTab()),
            MESSAGES_TAB: scroll_area.ScrollArea(MessagesTab()),
        }
        self.tab_buttons = {
            APPLICATION_TAB: self.application_button,
            TEXT_EDITOR_TAB: self.text_editor_button,
            DICTIONARY_TAB: self.dictionary_button,
            SHORTCUTS_TAB: self.shortcuts_button,
            MESSAGES_TAB: self.messages_button,
        }
        self.active_tab = QWidget()
        self.active_tab.setLayout(QVBoxLayout())
        self.active_tab.layout().setContentsMargins(0, 0, 0, 0)
        self.active_tab.layout().setSpacing(0)
        self.middle = QWidget()
        self.middle.setLayout(QHBoxLayout())
        self.middle.layout().addWidget(self.tab_side_bar, 0)
        self.middle.layout().addWidget(self.active_tab, 1)
        self.middle.layout().setContentsMargins(0, 0, 0, 0)
        self.middle.layout().setSpacing(0)
        self.close_button = buttons.PushButton(self.on_close)
        self.save_and_close_button = buttons.PushButton(self.on_save)
        self.buttons = QWidget()
        self.buttons.setLayout(QHBoxLayout())
        self.buttons.layout().addStretch()
        self.buttons.layout().addWidget(self.close_button)
        self.buttons.layout().addWidget(self.save_and_close_button)
        self.setLayout(QVBoxLayout())
        self.layout().addWidget(self.filter, 0)
        self.layout().addWidget(HorizontalLine(), 0)
        self.layout().addWidget(self.middle, 1)
        self.layout().addWidget(HorizontalLine(), 0)
        self.layout().addWidget(self.buttons, 0)
        self.layout().setContentsMargins(0, 0, 0, 0)
        self.layout().setSpacing(0)
        self.on_tab(APPLICATION_TAB)
        self.filter_line_edit.textChanged.connect(self.on_filter)
        self.setWindowModality(Qt.WindowModality.ApplicationModal)
        self.initialize_geometry()
        self.on_update_language()
        self.on_update_settings()

    @property
    def default_width(self):
        return settings.app_settings_window_default_width

    @property
    def default_height(self):
        return settings.app_settings_window_default_height

    @staticmethod
    def pad_text(text):
        return f"    {text}    "

    def closeEvent(self, event):
        self.instance[0] = None
        super().closeEvent(event)

    def on_find(self):
        self.filter_line_edit.setFocus()

    def resizeEvent(self, event):
        self.filter_line_edit.setFixedWidth(self.width() // 3)

    def on_filter(self):
        filter_str = self.filter_line_edit.text()
        visible_active_tab_key = None
        visible_tab_key = None
        for tab_key, tab_widget in reversed(self.tab_widgets.items()):
            tab_visible = False
            for widget in tab_widget.widget.widgets:
                text = widget.label.text()
                if filter_str.lower() in text.lower():
                    widget.show()
                    widget.is_visible = True
                    tab_visible = True
                else:
                    widget.hide()
                    widget.is_visible = False
            tab_widget.widget.on_update_settings()
            tab_button = self.tab_buttons[tab_key]
            if tab_visible:
                visible_tab_key = tab_key
                if tab_button.is_active:
                    visible_active_tab_key = tab_key
                tab_button.setFixedHeight(tab_button.height_)
            else:
                tab_button.setFixedHeight(0)
        if visible_active_tab_key is not None:
            self.on_tab(visible_active_tab_key)
        elif visible_tab_key is not None:
            self.on_tab(visible_tab_key)

    def on_tab(self, tab_key):
        for key, button in self.tab_buttons.items():
            if key == tab_key:
                button.is_active = True
            else:
                button.is_active = False
            button.update()
        self.active_tab.layout().takeAt(0)
        for tab_widget in self.tab_widgets.values():
            tab_widget.hide()
        active_widget = self.tab_widgets[tab_key]
        self.active_tab.layout().addWidget(active_widget)
        active_widget.show()

    def on_close(self):
        self.close()

    def on_save(self):
        pre_dict_dir = settings.dict_dir
        for tab_widget in self.tab_widgets.values():
            tab_widget.widget.on_save()
        self.close()
        reinit_app()
        settings.save()
        post_dict_dir = settings.dict_dir
        if pre_dict_dir != post_dict_dir:

            def on_copy_automatically():
                os.makedirs(post_dict_dir, exist_ok=True)
                show_error_message = False
                for file_name in os.listdir(pre_dict_dir):
                    dict_name, extension = os.path.splitext(file_name)
                    if extension == app_info.db_ext:
                        src = os.path.join(pre_dict_dir, file_name)
                        dst = os.path.join(post_dict_dir, file_name)
                        if os.path.exists(dst):
                            show_error_message = True
                            continue
                        try:
                            shutil.copyfile(src, dst)
                        except PermissionError:
                            show_error_message = True
                            continue
                if show_error_message:
                    messages.DictionaryDirectoryCopyAutomaticallyFailedErrorMessage().show()

            messages.DictionaryDirectoryChangedWarningMessage(
                on_copy_automatically
            ).show()

    def on_update_language(self):
        self.setWindowTitle(tr("Settings"))
        self.filter_label.setText(tr("Filter: "))
        self.application_button.setText(self.pad_text(tr("Application")))
        self.text_editor_button.setText(self.pad_text(tr("Text Editor")))
        self.dictionary_button.setText(self.pad_text(tr("Dictionary")))
        self.shortcuts_button.setText(self.pad_text(tr("Shortcuts")))
        self.messages_button.setText(self.pad_text(tr("Messages")))
        self.close_button.setText(tr("Close"))
        self.save_and_close_button.setText(tr("Save And Close"))
        self.update()

    def on_update_settings(self):
        content_margin = int(
            round(settings.app_layout_content_margin * self.dpi)
        )
        self.filter.layout().setContentsMargins(
            content_margin,
            content_margin,
            content_margin,
            content_margin,
        )
        self.filter.layout().setSpacing(
            int(round(settings.app_layout_spacing * self.dpi))
        )
        self.buttons.layout().setContentsMargins(
            content_margin,
            content_margin,
            content_margin,
            content_margin,
        )
        button_spacing = int(round(settings.app_button_spacing * self.dpi))
        self.buttons.layout().setSpacing(button_spacing)
        self.update()


class Tab(QWidget):
    def __init__(self):
        super().__init__()
        self.setLayout(QVBoxLayout())
        self.on_focus_range_change = lambda x, y: None
        self.on_resize = lambda: None
        self.widgets = []

    @property
    def dpi(self):
        screen = self.screen()
        return screen.physicalDotsPerInch() / (
            screen.devicePixelRatio()
            if settings.app_scale_sizes_by_device_pixel_ratio
            else 1.0
        )

    def focus_range_change(self, y_min, y_max):
        y_min = y_min + self.y()
        y_max = y_max + self.y()
        self.on_focus_range_change(y_min, y_max)

    def clear_layout(self):
        layout = self.layout()
        while True:
            try:
                layout.takeAt(0).widget().deleteLater()
            except AttributeError:
                break

    def visible_widgets(self):
        widgets = []
        layout = self.layout()
        for i in range(layout.count()):
            widget = layout.itemAt(i).widget()
            if widget.is_visible:
                widgets.append(widget)
        return widgets

    def on_save(self):
        for widget in self.widgets:
            widget.on_save()

    def on_update_language(self):
        for widget in self.widgets:
            widget.update_translated_text()
        self.clear_layout()
        for widget in sorted(self.widgets, key=lambda x: x.label.text()):
            self.layout().addWidget(widget)
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
        visible_widgets = self.visible_widgets()
        height = (
            sum((widget.height() for widget in visible_widgets))
            + spacing * (len(visible_widgets) - 1)
            + 2 * content_margin
        )
        self.setFixedHeight(height)
        self.update()
        self.on_resize()


class ApplicationTab(Tab):
    def __init__(self):
        super().__init__()
        self.widgets = [
            class_(key, translated_text_fn)
            for class_, key, translated_text_fn in (
                (
                    settings_widgets.Length,
                    "app_button_spacing",
                    lambda: tr("Space Between Buttons"),
                ),
                (
                    settings_widgets.PositiveDouble,
                    "app_close_time_tolerance",
                    lambda: f"{tr("Most Recently Closed Window Time Tolerance /[s/]")}", # fmt:skip
                ),
                (
                    settings_widgets.FileDirectory,
                    "app_default_files_dir",
                    lambda: tr("Default File Directory"),
                ),
                (
                    settings_widgets.Length,
                    "app_dialog_window_default_width",
                    lambda: tr("Dialog Window Default Width"),
                ),
                (
                    settings_widgets.Length,
                    "app_dialog_window_default_height",
                    lambda: tr("Dialog Window Default Height"),
                ),
                (
                    settings_widgets.Length,
                    "app_edit_length_short",
                    lambda: tr("Short Entry Length"),
                ),
                (
                    settings_widgets.Bool,
                    "app_enable_logging",
                    lambda: tr("Enable Logging"),
                ),
                (
                    settings_widgets.FontChoice,
                    "app_font_family",
                    lambda: tr("Font Family"),
                ),
                (
                    settings_widgets.NaturalInt,
                    "app_font_size",
                    lambda: tr("Font Size"),
                ),
                (
                    settings_widgets.NaturalInt,
                    "app_font_size_large",
                    lambda: tr("Large Font Size"),
                ),
                (
                    settings_widgets.FontWeightChoice,
                    "app_font_weight",
                    lambda: tr("Font Weight"),
                ),
                (
                    settings_widgets.LanguageChoice,
                    "app_language",
                    lambda: tr("Language"),
                ),
                (
                    settings_widgets.LanguageDirectionChoice,
                    "app_language_direction",
                    lambda: tr("Language Direction"),
                ),
                (
                    settings_widgets.Length,
                    "app_layout_content_margin",
                    lambda: tr("Space Around Widgets"),
                ),
                (
                    settings_widgets.Length,
                    "app_layout_spacing",
                    lambda: tr("Space Between Widgets"),
                ),
                (
                    settings_widgets.Length,
                    "app_layout_spacing_between_rows",
                    lambda: tr("Space Between Rows"),
                ),
                (
                    settings_widgets.Length,
                    "app_layout_splitter_handle_width",
                    lambda: tr("Splitter Handle Width"),
                ),
                (
                    settings_widgets.LengthUnitChoice,
                    "app_length_unit",
                    lambda: tr("Length Unit"),
                ),
                (
                    settings_widgets.FileDirectory,
                    "app_logging_dir",
                    lambda: tr("Logging Directory"),
                ),
                (
                    settings_widgets.PositiveInt,
                    "app_num_recents",
                    lambda: tr("Number Of Recents"),
                ),
                (
                    settings_widgets.Bool,
                    "app_remember_window_geometry",
                    lambda: tr("Remember Window Geometry"),
                ),
                (
                    settings_widgets.PositiveInt,
                    "app_repeated_action_initial_delay",
                    lambda: f"{tr("Repeated Action Initial Delay /[ms/]")}",
                ),
                (
                    settings_widgets.NaturalInt,
                    "app_repeated_action_interval",
                    lambda: f"{tr("Repeated Action Interval /[ms/]")}",
                ),
                (
                    settings_widgets.Bool,
                    "app_scale_sizes_by_device_pixel_ratio",
                    lambda: tr("Scale Sizes By Device Pixel Ratio"),
                ),
                (
                    settings_widgets.PositiveDouble,
                    "app_scroll_bar_min_length_rel_thickness",
                    lambda: tr("Scrollbar Minimum Length Relative To Thickness"), # fmt:skip
                ),
                (
                    settings_widgets.ZeroToOneDouble,
                    "app_scroll_bar_opacity_hover",
                    lambda: tr("Scrollbar Opacity When Hovered Over"),
                ),
                (
                    settings_widgets.ZeroToOneDouble,
                    "app_scroll_bar_opacity_normal",
                    lambda: tr("Scrollbar Opacity When Inactive"),
                ),
                (
                    settings_widgets.ZeroToOneDouble,
                    "app_scroll_bar_opacity_pressed",
                    lambda: tr("Scrollbar Trough Opacity When Pressed"),
                ),
                (
                    settings_widgets.ZeroToOneDouble,
                    "app_scroll_trough_opacity_hover",
                    lambda: tr("Scrollbar Trough Opacity When Hovered Over"),
                ),
                (
                    settings_widgets.ZeroToOneDouble,
                    "app_scroll_trough_opacity_normal",
                    lambda: tr("Scrollbar Trough Opacity When Inactive"),
                ),
                (
                    settings_widgets.ZeroToOneDouble,
                    "app_scroll_trough_opacity_pressed",
                    lambda: tr("Scrollbar Opacity When Pressed"),
                ),
                (
                    settings_widgets.Bool,
                    "app_scroll_bar_visible",
                    lambda: tr("Show Scrollbars"),
                ),
                (
                    settings_widgets.ScrollTroughBehaviorOnPressChoice,
                    "app_scroll_trough_behavior_on_press",
                    lambda: tr("Scroll Trough Behavior On Press"),
                ),
                (
                    settings_widgets.Length,
                    "app_scroll_trough_thickness",
                    lambda: tr("Scroll Trough Thickness"),
                ),
                (
                    settings_widgets.Length,
                    "app_settings_window_default_width",
                    lambda: tr("Settings Window Default Width"),
                ),
                (
                    settings_widgets.Length,
                    "app_settings_window_default_height",
                    lambda: tr("Settings Window Default Height"),
                ),
                (
                    settings_widgets.Length,
                    "app_stacked_window_offset",
                    lambda: tr("Stacked Window Offset"),
                ),
                (
                    settings_widgets.StartupWindowChoice,
                    "app_startup_window",
                    lambda: tr("Window On Startup"),
                ),
                (
                    settings_widgets.ThemeChoice,
                    "app_theme",
                    lambda: tr("Theme"),
                ),
                (
                    settings_widgets.FileDirectory,
                    "app_user_added_languages_dir",
                    lambda: tr("User-Added Languages Directory"),
                ),
                (
                    settings_widgets.FileDirectory,
                    "app_user_added_themes_dir",
                    lambda: tr("User-Added Themes Directory"),
                ),
            )
        ]
        self.on_update_language()
        self.on_update_settings()


class TextEditorTab(Tab):
    def __init__(self):
        super().__init__()
        self.widgets = [
            class_(key, translated_text_fn)
            for class_, key, translated_text_fn in (
                (
                    settings_widgets.AlignmentChoice,
                    "text_editor_alignment",
                    lambda: tr("Text Alignment"),
                ),
                (
                    settings_widgets.Bool,
                    "text_editor_autosave",
                    lambda: tr("Automatically Save Files"),
                ),
                (
                    settings_widgets.NaturalInt,
                    "text_editor_autosave_after_idle_interval",
                    lambda: tr("Automatically Save After Idle Interval /[s/]"),
                ),
                (
                    settings_widgets.OpenFileBehaviorChoice,
                    "text_editor_behavior_on_drag_and_drop_file",
                    lambda: tr("Behaviour On Drag And Drop File"),
                ),
                (
                    settings_widgets.OpenFileBehaviorChoice,
                    "text_editor_behavior_on_new_text_file",
                    lambda: tr("Behaviour On New Text File"),
                ),
                (
                    settings_widgets.OpenFileBehaviorChoice,
                    "text_editor_behavior_on_open_file",
                    lambda: tr("Behaviour On Open File"),
                ),
                (
                    settings_widgets.PositiveDouble,
                    "text_editor_find_replace_inactive_opacity",
                    lambda: tr("Find / Replace Inactive Window Opacity"),
                ),
                (
                    settings_widgets.Bool,
                    "text_editor_find_replace_match_case",
                    lambda: tr("Find / Replace Match Case Default Value"),
                ),
                (
                    settings_widgets.Bool,
                    "text_editor_find_replace_wrap_around",
                    lambda: tr("Find / Replace Wrap Around Default Value"),
                ),
                (
                    settings_widgets.FontChoice,
                    "text_editor_font_family",
                    lambda: tr("Font Family"),
                ),
                (
                    settings_widgets.NaturalInt,
                    "text_editor_font_size",
                    lambda: tr("Font Size"),
                ),
                (
                    settings_widgets.FontWeightChoice,
                    "text_editor_font_weight",
                    lambda: tr("Font Weight"),
                ),
                (
                    settings_widgets.PositiveInt,
                    "text_editor_look_ahead_lines",
                    lambda: tr("Number Of Look Ahead Lines"),
                ),
                (
                    settings_widgets.Length,
                    "text_editor_margin_left",
                    lambda: tr("Left Margin"),
                ),
                (
                    settings_widgets.Length,
                    "text_editor_margin_right",
                    lambda: tr("Right Margin"),
                ),
                (
                    settings_widgets.Length,
                    "text_editor_margin_top",
                    lambda: tr("Top Margin"),
                ),
                (
                    settings_widgets.NaturalInt,
                    "text_editor_num_spaces_per_tab",
                    lambda: tr("Number Of Spaces Per Tab"),
                ),
                (
                    settings_widgets.SideChoice,
                    "text_editor_open_side_existing_texts",
                    lambda: tr("Side On Which To Open Existing Texts"),
                ),
                (
                    settings_widgets.SideChoice,
                    "text_editor_open_side_new_texts",
                    lambda: tr("Side On Which To Open New Texts"),
                ),
                (
                    settings_widgets.ScrollTroughBehaviorOnPressChoice,
                    "text_editor_scroll_trough_behavior_on_press",
                    lambda: tr("Scroll Trough Behavior On Press"),
                ),
                (
                    settings_widgets.Bool,
                    "text_editor_set_focus_on_hover",
                    lambda: tr("Focus On Text Editor Under Cursor"),
                ),
                (
                    settings_widgets.Bool,
                    "text_editor_show_file_name_ext",
                    lambda: tr("Show File Name With Extension"),
                ),
                (
                    settings_widgets.Bool,
                    "text_editor_show_file_name_full_path",
                    lambda: tr("Show File Name As Full Path"),
                ),
                (
                    settings_widgets.OrientationChoice,
                    "text_editor_splitter_orientation",
                    lambda: tr("Split View Orientation"),
                ),
                (
                    settings_widgets.Bool,
                    "text_editor_sync_scrolling",
                    lambda: tr("Sync Vertical Scrolling"),
                ),
                (
                    settings_widgets.Bool,
                    "text_editor_sync_zooming",
                    lambda: tr("Sync Zooming"),
                ),
                (
                    settings_widgets.Bool,
                    "text_editor_use_spaces_for_tab",
                    lambda: tr("Use Spaces For Tab"),
                ),
                (
                    settings_widgets.NaturalInt,
                    "text_editor_window_default_num_views",
                    lambda: tr("Default Number of Views Per Window"),
                ),
                (
                    settings_widgets.Length,
                    "text_editor_window_default_width_per_view",
                    lambda: tr("Text Editor Window Default Width Per View"), # fmt:skip
                ),
                (
                    settings_widgets.Length,
                    "text_editor_window_default_height",
                    lambda: tr("Text Editor Window Default Height"),
                ),
                (
                    settings_widgets.Bool,
                    "text_editor_wrap_long_lines",
                    lambda: tr("Wrap Long Lines"),
                ),
                (
                    settings_widgets.PositiveDouble,
                    "text_editor_zoom_factor",
                    lambda: tr("Zoom Factor"),
                ),
            )
        ]
        self.on_update_language()
        self.on_update_settings()


class DictionaryTab(Tab):
    def __init__(self):
        super().__init__()
        self.widgets = [
            class_(key, translated_text_fn)
            for class_, key, translated_text_fn in (
                (
                    settings_widgets.DictionaryChoice,
                    "dict_default",
                    lambda: tr("Default Dictionary"),
                ),
                (
                    settings_widgets.FileDirectory,
                    "dict_dir",
                    lambda: tr("Dictionary Directory"),
                ),
                (
                    settings_widgets.Length,
                    "dict_entry_window_default_width",
                    lambda: tr("Entry Window Default Width"),
                ),
                (
                    settings_widgets.Length,
                    "dict_entry_window_default_height",
                    lambda: tr("Entry Window Default Height"),
                ),
                (
                    settings_widgets.FontChoice,
                    "dict_font_family",
                    lambda: tr("Font Family"),
                ),
                (
                    settings_widgets.NaturalInt,
                    "dict_font_size",
                    lambda: tr("Font Size"),
                ),
                (
                    settings_widgets.FontWeightChoice,
                    "dict_font_weight",
                    lambda: tr("Font Weight"),
                ),
                (
                    settings_widgets.Bool,
                    "dict_only_show_exact_matches",
                    lambda: tr("Only Show Exact Matches"),
                ),
                (
                    settings_widgets.Bool,
                    "dict_popup_blocks_clicks",
                    lambda: tr("Popup Blocks Clicks"),
                ),
                (
                    settings_widgets.DictPopupDirectionChoice,
                    "dict_popup_direction",
                    lambda: tr("Popup Direction"),
                ),
                (
                    settings_widgets.DictPopupHideOnChoice,
                    "dict_popup_hide_on",
                    lambda: tr("Hide Popup"),
                ),
                (
                    settings_widgets.NaturalInt,
                    "dict_popup_hover_delay",
                    lambda: tr("Popup Hover Delay /[ms/]"),
                ),
                (
                    settings_widgets.Bool,
                    "dict_popup_hover_delay_skipped_on_click",
                    lambda: tr("Show Popup Without Hover Delay On Click"),
                ),
                (
                    settings_widgets.Bool,
                    "dict_popup_no_show_if_no_match",
                    lambda: tr("Do Not Show Popup If No Matching Entries Found"), # fmt:skip
                ),
                (
                    settings_widgets.DictPopupMoveByChoice,
                    "dict_popup_on_shortcut_move_by",
                    lambda: tr("On Move Popup Shortcut Keys, Move By"),
                ),
                (
                    settings_widgets.Bool,
                    "dict_popup_on_shortcut_move_cursor",
                    lambda: tr("On Move Popup Shortcut Keys, Move Cursor Also"), # fmt:skip
                ),
                (
                    settings_widgets.Length,
                    "dict_popup_rect_height",
                    lambda: tr("Popup Height"),
                ),
                (
                    settings_widgets.Length,
                    "dict_popup_rect_radius",
                    lambda: tr("Popup Radius"),
                ),
                (
                    settings_widgets.Length,
                    "dict_popup_rect_width",
                    lambda: tr("Popup Width"),
                ),
                (
                    settings_widgets.DictPopupShowOnChoice,
                    "dict_popup_show_on",
                    lambda: tr("Show Popup"),
                ),
                (
                    settings_widgets.Length,
                    "dict_popup_tri_height",
                    lambda: tr("Popup Tail Height"),
                ),
                (
                    settings_widgets.Length,
                    "dict_popup_tri_width",
                    lambda: tr("Popup Tail Width"),
                ),
                (
                    settings_widgets.Length,
                    "dict_settings_window_default_width",
                    lambda: tr("Settings Window Default Width"),
                ),
                (
                    settings_widgets.Length,
                    "dict_settings_window_default_height",
                    lambda: tr("Settings Window Default Height"),
                ),
                (
                    settings_widgets.Bool,
                    "dict_show_preview_for_entries",
                    lambda: tr("Show Previews For Entries"),
                ),
                (
                    settings_widgets.Length,
                    "dict_template_entry_window_default_width",
                    lambda: tr("Template Entry Window Default Width"),
                ),
                (
                    settings_widgets.Length,
                    "dict_template_entry_window_default_height",
                    lambda: tr("Template Entry Window Default Height"),
                ),
                (
                    settings_widgets.Length,
                    "dict_template_window_default_width",
                    lambda: tr("Template Window Default Width"),
                ),
                (
                    settings_widgets.Length,
                    "dict_template_window_default_height",
                    lambda: tr("Template Window Default Height"),
                ),
                (
                    settings_widgets.Length,
                    "dict_window_default_width",
                    lambda: tr("Dictionary Window Default Width"),
                ),
                (
                    settings_widgets.Length,
                    "dict_window_default_height",
                    lambda: tr("Dictionary Window Default Height"),
                ),
            )
        ]
        self.on_update_language()
        self.on_update_settings()


class ShortcutsTab(Tab):
    def __init__(self):
        super().__init__()
        self.widgets = [
            settings_widgets.Shortcut(action_class)
            for action_class in actions.classes
        ]
        self.on_update_language()
        self.on_update_settings()


class MessagesTab(Tab):
    def __init__(self):
        super().__init__()
        self.widgets = [
            settings_widgets.MessageChoice(message_class)
            for message_class in messages.classes
        ]
        self.on_update_language()
        self.on_update_settings()


class TabSideBar(QFrame):
    pass


class HorizontalLine(QFrame):
    def __init__(self):
        super().__init__()
        self.setFixedHeight(1)
