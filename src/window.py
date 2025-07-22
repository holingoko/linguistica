import os

from src import dict_database_file
from src import icons
from src import messages
from src import settings
from src import theme
from src import state
from src.qt import *


class Window(QWidget):
    windows = []
    is_window = True

    def __init__(self):
        super().__init__()
        self.windows.append(self)
        self.setWindowIcon(icons.app_icon)
        self.parent_window = None
        self.child_windows = set()
        self.setAcceptDrops(True)
        self.on_update_theme()

    @property
    def center(self):
        return self.x() + self.width() // 2, self.y() + self.height() // 2

    @property
    def dpi(self):
        screen = self.screen()
        return screen.physicalDotsPerInch() / (
            screen.devicePixelRatio()
            if settings.app_scale_sizes_by_device_pixel_ratio
            else 1.0
        )

    def closeEvent(self, event):
        self.remove()
        self.windows.remove(self)
        self.deleteLater()
        for child_window in self.child_windows.copy():
            child_window.close()

    def dragEnterEvent(self, event):
        if self.windowModality() == Qt.WindowModality.NonModal:
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event):
        for url in event.mimeData().urls():
            path = url.path()[1:]
            if os.path.exists(path):
                dict_database_file.on_import_dict_database_file(
                    os.path.normpath(path),
                    on_success=lambda name: messages.DictionaryImportSuccessInfoMessage(
                        name
                    ).show(),
                )

    def add_child_window(self, child_window):
        self.child_windows.add(child_window)
        child_window.parent_window = self

    def remove(self):
        try:
            self.parent_window.child_windows.discard(self)
        except AttributeError:
            pass

    def initialize_geometry(self):
        self.set_default_geometry()
        self.center_or_stack_rel_prev_window()

    def set_default_geometry(self):
        title_bar_height = (
            QApplication.style().pixelMetric(QStyle.PM_TitleBarHeight) + 1
        )
        (
            screen_x,
            screen_y,
            screen_width,
            screen_height,
        ) = (
            self.screen().availableVirtualGeometry().getRect()
        )
        width = min(int(round(self.default_width * self.dpi)), screen_width)
        height = min(int(round(self.default_height * self.dpi)), screen_height)
        width = width + width % 2
        height = height + height % 2
        x = int(round(screen_x + (screen_width - width) / 2.0))
        y = (
            int(
                round(
                    screen_y
                    + (screen_height - height + title_bar_height) / 2.0
                )
            )
            - 1
        )
        x = max(x, screen_x)
        y = max(y, screen_y)
        self.setGeometry(x, y, width, height)

    def center_or_stack_rel_prev_window(self):
        try:
            prev_window = self.windows[-2]
        except IndexError:
            return
        title_bar_height = QApplication.style().pixelMetric(
            QStyle.PM_TitleBarHeight
        )
        (
            screen_x,
            screen_y,
            screen_width,
            screen_height,
        ) = (
            self.screen().availableVirtualGeometry().getRect()
        )
        width, height = self.width(), self.height()
        if prev_window.width() == width and prev_window.height() == height:
            offset = int(round(settings.app_stacked_window_offset * self.dpi))
            x = prev_window.x() + offset
            y = prev_window.y() + offset
            max_x = screen_width - width
            max_y = screen_height - height
            if x > max_x:
                x = offset
                y = offset + title_bar_height // 2
            if y > max_y:
                y = offset + title_bar_height // 2
            self.setGeometry(x, y, width, height)
        else:
            prev_center_x, prev_center_y = prev_window.center
            self_center_x, self_center_y = self.center
            shift_x = prev_center_x - self_center_x
            shift_y = prev_center_y - self_center_y
            self.move(self.x() + shift_x, self.y() + shift_y)
        x = max(self.x(), screen_x)
        y = max(self.y(), screen_y)
        self.move(x, y)

    def move_to_center(self):
        (
            screen_x,
            screen_y,
            screen_width,
            screen_height,
        ) = (
            self.screen().availableVirtualGeometry().getRect()
        )
        screen_center_x = screen_x + screen_width // 2
        screen_center_y = screen_y + screen_height // 2
        self_center_x, self_center_y = self.center
        shift_x = screen_center_x - self_center_x
        shift_y = screen_center_y - self_center_y
        self.move(self.x() + shift_x, self.y() + shift_y)

    def on_activate(self):
        try:
            self.windows.remove(self)
            self.windows.append(self)
        except ValueError:
            pass

    def on_update_theme(self):
        try:
            self.setStyleSheet(theme.style_sheet.format_map(settings.dict_()))
        except:
            invalid_theme = settings.app_theme
            settings.app_theme = settings.defaults["app_theme"]
            settings.save()
            theme.load_theme()
            self.on_update_theme()
            error_message = messages.InvalidThemeErrorMessage(invalid_theme)
            error_message.show()
            error_message.move_to_center()
            return
        self.update()
