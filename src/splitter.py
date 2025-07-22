from src import settings
from src.qt import *


class Splitter(QSplitter):
    def __init__(self):
        super().__init__()
        self.on_update_settings()

    @property
    def dpi(self):
        screen = self.screen()
        return screen.physicalDotsPerInch() / (
            screen.devicePixelRatio()
            if settings.app_scale_sizes_by_device_pixel_ratio
            else 1.0
        )

    def createHandle(self):
        return SplitterHandle(self.orientation(), self)

    def equalize_widget_sizes(self):
        sizes = self.sizes()
        same_size = max(sizes)
        self.setSizes([same_size for _ in range(len(sizes))])

    def on_mouse_double_click_event(self):
        self.equalize_widget_sizes()

    def on_update_settings(self):
        self.setHandleWidth(
            settings.app_layout_splitter_handle_width * self.dpi
        )
        self.update()


class SplitterHandle(QSplitterHandle):
    def __init__(self, orientation, parent):
        super().__init__(orientation, parent)

    def mouseDoubleClickEvent(self, event):
        self.parent().on_mouse_double_click_event()
