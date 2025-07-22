from src import buttons
from src import label
from src import line_edit
from src import settings
from src import utils
from src import window
from src.language import tr
from src.qt import *


class FindReplaceWindow(window.Window):
    @property
    def default_width(self):
        return settings.app_dialog_window_default_width

    @property
    def default_height(self):
        return settings.app_dialog_window_default_height

    def changeEvent(self, event):
        if event.type() == QEvent.Type.ActivationChange:
            if self.isActiveWindow():
                self.setWindowOpacity(1.0)
            else:
                self.setWindowOpacity(
                    settings.text_editor_find_replace_inactive_opacity
                )

    def closeEvent(self, event):
        self.on_close(self.geometry())
        super().closeEvent(event)

    def find_next(self):
        self.on_find_next(
            self.find_line_edit.text(),
            self.match_case_check_box.isChecked(),
            self.wrap_around_check_box.isChecked(),
        )

    def find_prev(self):
        self.on_find_prev(
            self.find_line_edit.text(),
            self.match_case_check_box.isChecked(),
            self.wrap_around_check_box.isChecked(),
        )

    def replace_next(self):
        self.on_replace_next(
            self.find_line_edit.text(),
            self.replace_line_edit.text(),
            self.match_case_check_box.isChecked(),
            self.wrap_around_check_box.isChecked(),
        )

    def replace_prev(self):
        self.on_replace_prev(
            self.find_line_edit.text(),
            self.replace_line_edit.text(),
            self.match_case_check_box.isChecked(),
            self.wrap_around_check_box.isChecked(),
        )

    def replace_all(self):
        self.on_replace_all(
            self.find_line_edit.text(),
            self.replace_line_edit.text(),
            self.match_case_check_box.isChecked(),
        )

    def move_to_text_editor_center(self, text_editor):
        title_bar_height = (
            QApplication.style().pixelMetric(QStyle.PM_TitleBarHeight) + 1
        )
        center_x = text_editor.x() + text_editor.width() // 2
        center_y = text_editor.y() + text_editor.height() // 2
        global_pos = text_editor.mapToGlobal(QPoint(center_x, center_y))
        center_x, center_y = global_pos.x(), global_pos.y()
        self_center_x, self_center_y = self.center
        self_center_y = self_center_y + title_bar_height // 2
        shift_x = center_x - self_center_x
        shift_y = center_y - self_center_y
        self.move(self.x() + shift_x, self.y() + shift_y)

    def on_checked_state_changed(self):
        settings.text_editor_find_replace_match_case = (
            self.match_case_check_box.isChecked()
        )
        settings.text_editor_find_replace_wrap_around = (
            self.wrap_around_check_box.isChecked()
        )

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
        self.left.layout().setContentsMargins(
            content_margin,
            content_margin,
            content_margin,
            content_margin,
        )
        self.buttons.layout().setContentsMargins(
            content_margin,
            content_margin,
            content_margin,
            content_margin,
        )
        self.layout().setSpacing(spacing)
        self.left.layout().setSpacing(spacing)
        self.buttons.layout().setSpacing(spacing)
        self.update()


class FindWindow(FindReplaceWindow):
    def __init__(
        self,
        on_close,
        on_find_next,
        on_find_prev,
        on_find_text_edited,
    ):
        super().__init__()
        self.on_close = on_close
        self.on_find_next = on_find_next
        self.on_find_prev = on_find_prev
        self.find_label = label.Label()
        self.find_line_edit = FindReplaceLineEdit(self)
        self.match_case_check_box = QCheckBox()
        self.wrap_around_check_box = QCheckBox()
        self.match_case_check_box.setChecked(
            settings.text_editor_find_replace_match_case
        )
        self.wrap_around_check_box.setChecked(
            settings.text_editor_find_replace_wrap_around
        )
        self.left = QWidget()
        self.left.setLayout(QVBoxLayout())
        self.left.layout().addWidget(self.find_label)
        self.left.layout().addWidget(self.find_line_edit)
        self.left.layout().addStretch()
        self.left.layout().addWidget(self.match_case_check_box)
        self.left.layout().addWidget(self.wrap_around_check_box)
        self.button_list = []
        self.find_next_button = buttons.FocusedIsDefaultPushButton(
            self.find_next,
            self.button_list,
        )
        self.find_prev_button = buttons.FocusedIsDefaultPushButton(
            self.find_prev,
            self.button_list,
        )
        self.close_button = buttons.FocusedIsDefaultPushButton(
            self.close,
            self.button_list,
        )
        self.buttons = QWidget()
        self.buttons.setLayout(QVBoxLayout())
        self.buttons.layout().addWidget(self.find_next_button)
        self.buttons.layout().addWidget(self.find_prev_button)
        self.buttons.layout().addWidget(self.close_button)
        self.buttons.layout().addStretch()
        self.default_button = self.find_next_button.default_button
        self.find_next_button.setDefault(True)
        utils.run_after_current_event(self.find_line_edit.setFocus)
        self.setLayout(QHBoxLayout())
        self.layout().addWidget(self.left)
        self.layout().addWidget(self.buttons)
        self.find_line_edit.textEdited.connect(on_find_text_edited)
        self.match_case_check_box.checkStateChanged.connect(
            self.on_checked_state_changed
        )
        self.wrap_around_check_box.checkStateChanged.connect(
            self.on_checked_state_changed
        )
        self.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint)
        self.initialize_geometry()
        self.on_update_language()
        self.on_update_settings()

    def on_update_language(self):
        self.setWindowTitle(tr("Find"))
        self.find_label.setText(tr("Find:"))
        self.match_case_check_box.setText(tr("Match Case"))
        self.wrap_around_check_box.setText(tr("Wrap Around"))
        self.find_next_button.setText(tr("Find Next"))
        self.find_prev_button.setText(tr("Find Previous"))
        self.close_button.setText(tr("Close"))
        self.update()


class ReplaceWindow(FindReplaceWindow):
    def __init__(
        self,
        on_close,
        on_find_next,
        on_find_prev,
        on_find_text_edited,
        on_replace_next,
        on_replace_prev,
        on_replace_all,
        on_replace_text_edited,
    ):
        super().__init__()
        self.on_close = on_close
        self.on_find_next = on_find_next
        self.on_find_prev = on_find_prev
        self.on_replace_next = on_replace_next
        self.on_replace_prev = on_replace_prev
        self.on_replace_all = on_replace_all
        self.find_label = label.Label()
        self.find_line_edit = FindReplaceLineEdit(self)
        self.replace_label = label.Label()
        self.replace_line_edit = FindReplaceLineEdit(self)
        self.match_case_check_box = QCheckBox()
        self.wrap_around_check_box = QCheckBox()
        self.match_case_check_box.setChecked(
            settings.text_editor_find_replace_match_case
        )
        self.wrap_around_check_box.setChecked(
            settings.text_editor_find_replace_wrap_around
        )
        self.left = QWidget()
        self.left.setLayout(QVBoxLayout())
        self.left.layout().addWidget(self.find_label)
        self.left.layout().addWidget(self.find_line_edit)
        self.left.layout().addWidget(self.replace_label)
        self.left.layout().addWidget(self.replace_line_edit)
        self.left.layout().addStretch()
        self.left.layout().addWidget(self.match_case_check_box)
        self.left.layout().addWidget(self.wrap_around_check_box)
        self.button_list = []
        self.find_next_button = buttons.FocusedIsDefaultPushButton(
            self.find_next,
            self.button_list,
        )
        self.find_prev_button = buttons.FocusedIsDefaultPushButton(
            self.find_prev,
            self.button_list,
        )
        self.replace_next_button = buttons.FocusedIsDefaultPushButton(
            self.replace_next,
            self.button_list,
        )
        self.replace_prev_button = buttons.FocusedIsDefaultPushButton(
            self.replace_prev,
            self.button_list,
        )
        self.replace_all_button = buttons.FocusedIsDefaultPushButton(
            self.replace_all,
            self.button_list,
        )
        self.close_button = buttons.FocusedIsDefaultPushButton(
            self.close,
            self.button_list,
        )
        self.buttons = QWidget()
        self.buttons.setLayout(QVBoxLayout())
        self.buttons.layout().addWidget(self.find_next_button)
        self.buttons.layout().addWidget(self.find_prev_button)
        self.buttons.layout().addWidget(self.replace_next_button)
        self.buttons.layout().addWidget(self.replace_prev_button)
        self.buttons.layout().addWidget(self.replace_all_button)
        self.buttons.layout().addWidget(self.close_button)
        self.buttons.layout().addStretch()
        self.default_button = self.find_next_button.default_button
        self.find_next_button.setDefault(True)
        utils.run_after_current_event(self.find_line_edit.setFocus)
        self.setLayout(QHBoxLayout())
        self.layout().addWidget(self.left)
        self.layout().addWidget(self.buttons)
        self.find_line_edit.textEdited.connect(on_find_text_edited)
        self.replace_line_edit.textEdited.connect(on_replace_text_edited)
        self.match_case_check_box.checkStateChanged.connect(
            self.on_checked_state_changed
        )
        self.wrap_around_check_box.checkStateChanged.connect(
            self.on_checked_state_changed
        )
        self.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint)
        self.initialize_geometry()
        self.on_update_language()
        self.on_update_settings()

    def on_update_language(self):
        self.setWindowTitle(tr("Replace"))
        self.find_label.setText(tr("Find:"))
        self.replace_label.setText(tr("Replace:"))
        self.match_case_check_box.setText(tr("Match Case"))
        self.wrap_around_check_box.setText(tr("Wrap Around"))
        self.find_next_button.setText(tr("Find Next"))
        self.find_prev_button.setText(tr("Find Previous"))
        self.replace_next_button.setText(tr("Replace Next"))
        self.replace_prev_button.setText(tr("Replace Previous"))
        self.replace_all_button.setText(tr("Replace All"))
        self.close_button.setText(tr("Close"))


class FindReplaceLineEdit(line_edit.LineEdit):
    def __init__(self, window_):
        super().__init__(window_)
        self.window = window_

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Return:
            self.window.default_button().pressed.emit()
            return
        super().keyPressEvent(event)

    def keyReleaseEvent(self, event):
        if event.key() == Qt.Key.Key_Return:
            self.window.default_button().released.emit()
            return
        super().keyReleaseEvent(event)
