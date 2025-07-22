from src.qt import *


class SelectableFrame(QFrame):
    def __init__(self):
        super().__init__()
        self._selected = False

    @property
    def selected(self):
        return self._selected

    @selected.setter
    def selected(self, selected):
        self._selected = selected
        self.setProperty("selected", selected)
        self.style().polish(self)
        self.update()
