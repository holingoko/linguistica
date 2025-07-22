from src.qt import *


class Frame(QFrame):
    def __init__(self, scroll_area, context_menu):
        super().__init__()
        self.scroll_area = scroll_area
        self.widget = scroll_area.widget
        self.widget.frame = self
        self.widget.is_window = False
        self.context_menu = context_menu
        self.setLayout(QVBoxLayout())
        self.layout().addWidget(scroll_area)
        self.layout().setContentsMargins(0, 0, 0, 0)
        self.layout().setSpacing(0)

    def __getattr__(self, name):
        return getattr(self.widget, name)

    def contextMenuEvent(self, event):
        self.context_menu.move(event.globalPos())
        self.context_menu.show()

    def mousePressEvent(self, event):
        self.setFocus()
