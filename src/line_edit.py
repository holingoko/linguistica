from src import menus
from src.qt import *


class LineEdit(QLineEdit):
    def __init__(self, window):
        super().__init__()
        self.context_menu = menus.LineEditContextMenu(window)

    def contextMenuEvent(self, event):
        self.context_menu.move(event.globalPos())
        self.context_menu.show()

    def event(self, event):
        if event.type() == QEvent.Type.ShortcutOverride:
            event.ignore()
            return False
        return super().event(event)

    def keyPressEvent(self, event):
        if Qt.KeyboardModifier.ControlModifier in event.modifiers():
            return
        elif event.key() == Qt.Key.Key_Escape:
            self.clearFocus()
            return
        super().keyPressEvent(event)

    def on_undo(self):
        self.undo()

    def on_redo(self):
        self.redo()

    def on_cut(self):
        self.cut()

    def on_copy(self):
        self.copy()

    def on_paste(self):
        self.paste()

    def on_select_all(self):
        self.selectAll()


class ValidatedLineEdit(LineEdit):
    def __init__(self, window):
        super().__init__(window)
        self.prev_text = ""
        self.editingFinished.connect(self.on_editing_finished)

    def focusOutEvent(self, event):
        if self.validator().validate(self.text(), 0)[0] in {
            QValidator.State.Intermediate,
            QValidator.State.Invalid,
        }:
            self.setText(self.prev_text)
        super().focusOutEvent(event)

    def setText(self, event):
        super().setText(event)
        self.prev_text = self.text()

    def on_editing_finished(self):
        self.prev_text = self.text()
