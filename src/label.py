from src import app
from src import menus
from src import language
from src.qt import *


class Label(QLabel):
    def __init__(self, text=""):
        super().__init__(text)
        self.on_update_language()

    def on_update_language(self):
        alignment = self.alignment()
        if (alignment & Qt.AlignmentFlag.AlignLeft) or (
            alignment & Qt.AlignmentFlag.AlignRight
        ):
            self.setAlignment(
                language.alignment | Qt.AlignmentFlag.AlignVCenter
            )
        self.update()


class SelectableLabel(Label):
    def __init__(self, window):
        super().__init__()
        self.context_menu = menus.LabelContextMenu(window)
        self.setTextInteractionFlags(
            Qt.TextInteractionFlag.TextSelectableByMouse
        )

    def contextMenuEvent(self, event):
        self.context_menu.move(event.globalPos())
        self.context_menu.show()

    def on_copy(self):
        app.clipboard().setText(self.selectedText())

    def on_select_all(self):
        self.setSelection(0, len(self.text()))


class AutoTrimmedLabel(Label):
    def __init__(self):
        super().__init__()
        self.true_text_being_set = True
        self.true_text = None

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.trim_label_to_width()

    def setText(self, text):
        super().setText(text)
        if self.true_text_being_set:
            self.true_text = text
            self.setToolTip(text)
            self.trim_label_to_width()

    def set_text(self, text):
        self.true_text_being_set = False
        self.setText(text)
        self.true_text_being_set = True

    def trim_label_to_width(self):
        width = self.width()
        text_width = self.fontMetrics().horizontalAdvance(self.true_text)
        if text_width < width:
            self.set_text(self.true_text)
        else:
            ratio = width / text_width
            trimmed_len = int(len(self.true_text) * ratio)
            self.set_text(
                language.trim_text_with_ellipsis(
                    self.true_text,
                    trimmed_len,
                )
            )


class AutoTrimmedFileNameLabel(AutoTrimmedLabel):
    def trim_label_to_width(self):
        width = self.width()
        text_width = self.fontMetrics().horizontalAdvance(self.true_text)
        if text_width < width:
            self.set_text(self.true_text)
        else:
            ratio = width / text_width
            trimmed_len = int(len(self.true_text) * ratio)
            ellipsis_in_context = "...{}"
            ellipsis_len = len(ellipsis_in_context)
            self.set_text(
                ellipsis_in_context.format(
                    self.true_text[-trimmed_len + ellipsis_len :]
                )
            )
