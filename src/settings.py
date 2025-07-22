import enum
import json
import os

from src import app
from src import app_info
from src import custom_json
from src import system
from src.qt import *

PHI = (1.0 + 5.0**0.5) / 2.0

settings = QSettings(
    QSettings.Scope.UserScope,
    app_info.author,
    app_info.name,
)


class OpenFileBehavior(enum.StrEnum):
    INSERT = "INSERT"
    REPLACE = "REPLACE"
    NEW_WINDOW = "NEW_WINDOW"


class FontWeight(enum.StrEnum):
    NORMAL = "NORMAL"
    BOLD = "BOLD"

    __str_to_qt = {
        NORMAL: QFont.Weight.Normal,
        BOLD: QFont.Weight.Bold,
    }

    @classmethod
    def qt(cls, value):
        return cls.__str_to_qt[value]


class LanguageDirection(enum.StrEnum):
    AUTOMATIC = "AUTOMATIC"
    LEFT_TO_RIGHT = "LEFT_TO_RIGHT"
    RIGHT_TO_LEFT = "RIGHT_TO_LEFT"


class ScrollTroughBehaviorOnPress(enum.StrEnum):
    CHANGE_PAGE = "CHANGE_PAGE"
    JUMP_TO = "JUMP TO"


class LengthUnit(enum.StrEnum):
    INCHES = "INCHES"
    MILLIMETERS = "MILLIMETERS"


class StartupWindow(enum.StrEnum):
    MOST_RECENTLY_CLOSED = "MOST_RECENTLY_CLOSED"
    NEW_TEXT_EDITOR = "NEW_TEXT_EDITOR"
    DICTIONARY_WINDOW = "DICTIONARY_WINDOW"


class DictPopupDirection(enum.StrEnum):
    ABOVE = "ABOVE"
    BELOW = "BELOW"


class DictPopupShowOn(enum.StrEnum):
    CLICK = "CLICK"
    DOUBLE_CLICK = "DOUBLE_CLICK"
    HOVER = "HOVER"
    NEVER = "NEVER"


class DictPopupHideOn(enum.StrEnum):
    CLICK = "CLICK"
    DOUBLE_CLICK = "DOUBLE_CLICK"
    LEAVE = "LEAVE"
    ESCAPE = "ESCAPE"
    NEVER = "NEVER"


class DictPopupMoveBy(enum.StrEnum):
    CHAR = "CHAR"
    WORD = "WORD"
    DISABLED = "DISABLED"


class Alignment(enum.StrEnum):
    LEFT = "LEFT"
    RIGHT = "RIGHT"
    CENTER = "CENTER"
    JUSTIFY = "JUSTIFY"

    __str_to_qt = {
        LEFT: Qt.AlignmentFlag.AlignLeft,
        RIGHT: Qt.AlignmentFlag.AlignRight,
        CENTER: Qt.AlignmentFlag.AlignCenter,
        JUSTIFY: Qt.AlignmentFlag.AlignJustify,
    }

    @classmethod
    def qt(cls, value):
        return cls.__str_to_qt[value]


class Side(enum.StrEnum):
    LEFT_OF_SELECTED = "LEFT_OF_SELECTED"
    RIGHT_OF_SELECTED = "RIGHT_OF_SELECTED"
    FAR_LEFT = "FAR_LEFT"
    FAR_RIGHT = "FAR_RIGHT"


class Orientation(enum.StrEnum):
    HORIZONTAL = "HORIZONTAL"
    VERTICAL = "VERTICAL"

    __str_to_qt = {
        HORIZONTAL: Qt.Orientation.Horizontal,
        VERTICAL: Qt.Orientation.Vertical,
    }

    @classmethod
    def qt(cls, value):
        return cls.__str_to_qt[value]


pre_keys = set(globals().keys())

app_button_spacing = 0.0859
app_close_time_tolerance = 1.0
app_default_files_dir = ""
app_dialog_window_default_width = 5.0
app_dialog_window_default_height = app_dialog_window_default_width / PHI
app_edit_length_short = 2.5 if app.screens()[0].devicePixelRatio() > 1.0 else 2.0 # fmt:skip
app_enable_logging = False
app_font_family = system.system_font.family()
app_font_size = system.system_font.pointSize()
app_font_size_large = system.system_font.pointSize() + 2
app_font_weight = FontWeight.NORMAL
app_language = "English"
app_language_direction = LanguageDirection.AUTOMATIC
app_layout_content_margin = 0.1375
app_layout_spacing = 0.0859
app_layout_spacing_between_rows = 0.0859
app_layout_splitter_handle_width = 0.0859
app_length_unit = LengthUnit.INCHES
app_logging_dir = os.path.join(system.app_data_dir, "Logs")
app_num_recents = 10
app_remember_window_geometry = True
app_repeated_action_initial_delay = app.keyboardInputInterval()
app_repeated_action_interval = 100
app_scale_sizes_by_device_pixel_ratio = True
app_scroll_bar_min_length_rel_thickness = 3.0
app_scroll_bar_opacity_hover = 0.7
app_scroll_bar_opacity_normal = 0.6
app_scroll_bar_opacity_pressed = 0.8
app_scroll_trough_opacity_hover = 0.7
app_scroll_trough_opacity_normal = 0.0
app_scroll_trough_opacity_pressed = 0.8
app_scroll_bar_visible = True
app_scroll_trough_behavior_on_press = ScrollTroughBehaviorOnPress.CHANGE_PAGE
app_scroll_trough_thickness = 0.1718
app_settings_window_default_width = 12.0
app_settings_window_default_height = app_settings_window_default_width / PHI
app_stacked_window_offset = 0.35
app_startup_window = StartupWindow.MOST_RECENTLY_CLOSED
app_theme = "Dark"
app_user_added_languages_dir = os.path.join(system.app_data_dir, "Languages")
app_user_added_themes_dir = os.path.join(system.app_data_dir, "Themes")
dict_default = ""
dict_dir = os.path.join(system.app_data_dir, "Dictionaries")
dict_entry_window_default_width = 10.5
dict_entry_window_default_height = dict_entry_window_default_width * 1.1
dict_font_family = system.system_font.family()
dict_font_size = system.system_font.pointSize()
dict_font_weight = FontWeight.NORMAL
dict_only_show_exact_matches = False
dict_popup_blocks_clicks = True
dict_popup_direction = DictPopupDirection.BELOW
dict_popup_hide_on = DictPopupHideOn.ESCAPE
dict_popup_hover_delay = 500
dict_popup_hover_delay_skipped_on_click = True
dict_popup_no_show_if_no_match = False
dict_popup_on_shortcut_move_by = DictPopupMoveBy.WORD
dict_popup_on_shortcut_move_cursor = False
dict_popup_rect_height = 2.25
dict_popup_rect_radius = 0.1375
dict_popup_rect_width = 3.50
dict_popup_show_on = DictPopupShowOn.HOVER
dict_popup_tri_height = 0.1181
dict_popup_tri_width = 0.1718
dict_settings_window_default_width = 9.5
dict_settings_window_default_height = dict_settings_window_default_width / PHI
dict_show_preview_for_entries = True
dict_template_entry_window_default_width = 7.5
dict_template_entry_window_default_height = dict_template_entry_window_default_width # fmt:skip
dict_template_window_default_width = 10.5
dict_template_window_default_height = dict_template_window_default_width * 1.1
dict_window_default_width = 5.0
dict_window_default_height = 5.0
action_class_to_shortcut = dict()
message_class_to_choice = dict()
text_editor_alignment = Alignment.LEFT
text_editor_autosave = False
text_editor_autosave_after_idle_interval = 2
text_editor_behavior_on_drag_and_drop_file = OpenFileBehavior.REPLACE
text_editor_behavior_on_new_text_file = OpenFileBehavior.INSERT
text_editor_behavior_on_open_file = OpenFileBehavior.INSERT
text_editor_font_family = system.system_font.family()
text_editor_font_size = system.system_font.pointSize()
text_editor_font_weight = FontWeight.NORMAL
text_editor_find_replace_inactive_opacity = 0.5
text_editor_find_replace_match_case = False
text_editor_find_replace_wrap_around = True
text_editor_look_ahead_lines = 3
text_editor_margin_left = 0.80
text_editor_margin_right = 0.80
text_editor_margin_top = 0.75
text_editor_num_spaces_per_tab = 4
text_editor_use_spaces_for_tab = True
text_editor_open_side_existing_texts = Side.LEFT_OF_SELECTED
text_editor_open_side_new_texts = Side.RIGHT_OF_SELECTED
text_editor_scroll_trough_behavior_on_press = ScrollTroughBehaviorOnPress.JUMP_TO # fmt:skip
text_editor_set_focus_on_hover = False
text_editor_show_file_name_ext = False
text_editor_show_file_name_full_path = False
text_editor_splitter_orientation = Orientation.HORIZONTAL
text_editor_sync_scrolling = True
text_editor_sync_zooming = False
text_editor_window_default_num_views = 1
text_editor_window_default_width_per_view = 8.0
text_editor_window_default_height = 2.0 * text_editor_window_default_width_per_view / PHI # fmt:skip
text_editor_wrap_long_lines = True
text_editor_zoom_factor = 0.1

post_keys = set(globals().keys())
keys = post_keys - pre_keys - {"pre_keys"}


def dict_():
    return {key: globals()[key] for key in keys}


defaults = dict_()
file_name = os.path.splitext(os.path.basename(__file__))[0]


def load():
    for key in keys:
        value = settings.value(f"{key}")
        if value is None:
            continue
        value = json.loads(value, cls=custom_json.Decoder)
        globals()[key] = value


def reset():
    settings.clear()
    for key in keys:
        globals()[key] = defaults[key]


def save():
    for key in keys:
        value = json.dumps(globals()[key], cls=custom_json.Encoder)
        settings.setValue(f"{key}", value)


load()
