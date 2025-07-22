from src import app
from src import buttons
from src import settings
from src.language import tr
from src.qt import *


class ShortcutEdit(QWidget):
    def __init__(self):
        super().__init__()
        self.key_sequence_edit = KeySequenceEdit()
        self.clear_button = buttons.TextButton(self.on_clear)
        self.setLayout(QHBoxLayout())
        self.layout().addWidget(self.key_sequence_edit)
        self.layout().addWidget(self.clear_button)
        self.layout().addStretch()
        self.layout().setContentsMargins(0, 0, 0, 0)
        self.on_update_language()
        self.on_update_settings()

    @property
    def dpi(self):
        screen = self.screen()
        return screen.physicalDotsPerInch() / (
            screen.devicePixelRatio()
            if settings.app_scale_sizes_by_device_pixel_ratio
            else 1.0
        )

    def set_text(self, text):
        self.key_sequence_edit.setText(text.title())

    def get_text(self):
        return self.key_sequence_edit.text()

    def on_clear(self):
        self.key_sequence_edit.setText("")

    def on_update_language(self):
        self.clear_button.setText(tr("Clear"))

    def on_update_settings(self):
        self.key_sequence_edit.setFixedWidth(
            int(round(settings.app_edit_length_short * self.dpi)),
        )
        self.layout().setSpacing(
            int(round(settings.app_layout_spacing * self.dpi)),
        )
        self.update()


class KeySequenceEdit(QLineEdit):
    def __init__(self):
        super().__init__()

    def contextMenuEvent(self, event):
        pass

    def focusInEvent(self, event):
        app.ignore_shortcuts = True
        super().focusInEvent(event)

    def focusOutEvent(self, event):
        super().focusOutEvent(event)
        app.ignore_shortcuts = False

    def focusNextPrevChild(self, _next):
        return False

    def keyPressEvent(self, event):
        if event.key() in {
            Qt.Key.Key_Shift,
            Qt.Key.Key_Control,
            Qt.Key.Key_Alt,
            Qt.Key.Key_Meta,
        }:
            return
        self.setText(QKeySequence(event.keyCombination()).toString())
