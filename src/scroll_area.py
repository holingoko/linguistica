from src import app
from src import settings
from src import utils
from src.qt import *


class ScrollArea(QFrame):
    def __init__(self, widget):
        super().__init__()
        self.widget = widget
        self.widget.setParent(self)
        self.widget.show()
        self.scrollbar = Scrollbar(self, widget)
        self.scrollbar.show()
        self.scrollbar.raise_()
        self.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Expanding,
        )
        self.widget.on_focus_range_change = self.focus_range_change
        self.widget.on_resize = self.on_widget_resize
        self.on_update_settings()

    @property
    def dpi(self):
        screen = self.screen()
        return screen.physicalDotsPerInch() / (
            screen.devicePixelRatio()
            if settings.app_scale_sizes_by_device_pixel_ratio
            else 1.0
        )

    def show(self):
        self.scrollbar.trough.update_brush()
        self.scrollbar.trough.bar.update_brush()
        super().show()

    def resizeEvent(self, event):
        new_width = self.width()
        new_height = self.height()
        self.widget.setFixedWidth(new_width)
        scrollbar_width = self.scrollbar.width()
        self.scrollbar.setGeometry(
            new_width - scrollbar_width - 1,
            1,
            scrollbar_width,
            new_height - 2,
        )
        self.scrollbar.page_step = new_height
        self.update_scrollbar_maximum()
        self.scrollbar.trough.bar.update_geometry()

    def wheelEvent(self, event):
        self.scrollbar.on_scroll(event.angleDelta().y())

    def update_scrollbar_maximum(self):
        widget_height = self.widget.height()
        if self.height() < widget_height:
            self.scrollbar.maximum = (
                widget_height - 2 * self.scrollbar.single_step
            )
        else:
            self.scrollbar.maximum = 0

    def focus_range_change(self, y_min, y_max):
        if y_min < 0:
            self.scrollbar.value = self.scrollbar.value + y_min
        else:
            y_max_diff = y_max - self.height()
            if y_max_diff > 0:
                self.scrollbar.value = self.scrollbar.value + y_max_diff

    def on_widget_resize(self):
        self.update_scrollbar_maximum()
        self.scrollbar.trough.bar.update_geometry()
        self.scrollbar.value = self.scrollbar.value

    def on_update_settings(self):
        self.scrollbar.setVisible(settings.app_scroll_bar_visible)
        self.scrollbar.setFixedWidth(
            int(round(settings.app_scroll_trough_thickness * self.dpi))
        )
        self.update()


class Scrollbar(QWidget):
    def __init__(self, parent, widget):
        super().__init__(parent)
        self.widget = widget
        self.trough = Trough(self)
        self.setLayout(QVBoxLayout())
        self.layout().addWidget(self.trough)
        self.layout().setSpacing(0)
        self.layout().setContentsMargins(0, 0, 0, 0)
        self._value = 0
        self.maximum = 0
        self.single_step = 0
        self.scroll_step = 0
        self.page_step = 0
        self.on_update_settings()

    @property
    def dpi(self):
        screen = self.screen()
        return screen.physicalDotsPerInch() / (
            screen.devicePixelRatio()
            if settings.app_scale_sizes_by_device_pixel_ratio
            else 1.0
        )

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value):
        self._value = min(max(value, 0), self.maximum)
        self.trough.bar.update_position()
        self.widget.move(self.widget.x(), -self.value)

    def resizeEvent(self, event):
        self.page_step = self.parent().height()

    def on_scroll(self, delta):
        self.value = (
            self.value
            - self.single_step * app.wheelScrollLines() * delta / 120.0
        )

    def on_update_settings(self):
        self.widget.on_update_settings()
        self.single_step = int(
            round(settings.app_layout_spacing_between_rows * self.dpi)
        ) + utils.calculate_default_height(QLineEdit)
        self.update()


class Trough(QWidget):
    def __init__(self, scrollbar):
        super().__init__()
        self.bar = Bar(self, scrollbar)
        self.timer = QTimer()
        self.cursor_within = False
        self._hover = False
        self._pressed = False
        self.setMouseTracking(True)
        self.timer.timeout.connect(self.page_up)
        self.timer.timeout.connect(self.page_down)
        self.brush = None
        self.update_brush()
        self.on_update_settings()
        self.on_update_theme()

    @property
    def dpi(self):
        screen = self.screen()
        return screen.physicalDotsPerInch() / (
            screen.devicePixelRatio()
            if settings.app_scale_sizes_by_device_pixel_ratio
            else 1.0
        )

    @property
    def hover(self):
        return self._hover

    @hover.setter
    def hover(self, hover):
        self._hover = hover
        self.setProperty("hover", hover)
        self.style().polish(self)

    @property
    def pressed(self):
        return self._pressed

    @pressed.setter
    def pressed(self, pressed):
        self._pressed = pressed
        self.setProperty("pressed", pressed)
        self.style().polish(self)

    def enterEvent(self, event):
        self.cursor_within = True

    def leaveEvent(self, event):
        self.cursor_within = False
        bar = self.bar
        bar.hover = False
        bar.on_update_theme()
        self.hover = False
        self.on_update_settings()
        self.on_update_theme()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.fillRect(self.rect(), self.brush)

    def mouseMoveEvent(self, event):
        bar = self.bar
        press_position = event.position().y()
        if bar.pressed:
            delta_pos = press_position - bar.offset_at_press
            new_pos = bar.position_at_press + delta_pos
            scrollable_span = bar.height() - bar.span
            if not scrollable_span:
                return
            new_rel_pos = new_pos / scrollable_span
            scrollbar = bar.scrollbar
            new_value = new_rel_pos * scrollbar.maximum
            scrollbar.value = new_value
        elif self.cursor_within and not self.pressed:
            if bar.position <= press_position < bar.position + bar.span:
                bar.hover = True
                self.hover = False
                bar.on_update_theme()
                self.on_update_theme()
            else:
                bar.hovered_over = False
                self.hover = True
                bar.on_update_theme()
                self.on_update_theme()

    def mousePressEvent(self, event):
        if event.button() != Qt.MouseButton.LeftButton:
            return
        bar = self.bar
        press_position = event.position().y()
        if bar.position <= press_position < bar.position + bar.span:
            bar.pressed = True
            bar.on_update_theme()
            bar.offset_at_press = press_position
            bar.position_at_press = bar.position
        else:
            self.pressed = True
            self.on_update_theme()
            if (
                settings.text_editor_scroll_trough_behavior_on_press
                == settings.ScrollTroughBehaviorOnPress.JUMP_TO
            ):
                new_pos = press_position - bar.span / 2.0
                scrollable_span = bar.height() - bar.span
                if not scrollable_span:
                    return
                new_rel_pos = new_pos / scrollable_span
                scrollbar = bar.scrollbar
                new_value = new_rel_pos * scrollbar.maximum
                scrollbar.value = new_value
                bar.pressed = True
                bar.on_update_theme()
                bar.offset_at_press = press_position
                bar.position_at_press = bar.position
            else:
                self.timer.stop()
                if press_position < bar.position:
                    self.page_up()
                else:
                    self.page_down()
                QTimer.singleShot(
                    settings.app_repeated_action_initial_delay,
                    lambda: (
                        self.timer.start() if self.pressed else lambda: None
                    ),
                )

    def mouseReleaseEvent(self, event):
        button = event.button()
        if button == Qt.MouseButton.LeftButton:
            self.timer.stop()
            bar = self.bar
            bar.pressed = False
            bar.on_update_theme()
            self.pressed = False
            self.on_update_theme()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        size = event.size()
        self.bar.setGeometry(
            0,
            0,
            size.width(),
            size.height(),
        )

    def page_up(self):
        bar = self.bar
        scrollbar = bar.scrollbar
        cursor_position = self.mapFromGlobal(QCursor.pos()).y()
        if cursor_position >= bar.position:
            return
        scrollbar.on_page_up()

    def page_down(self):
        bar = self.bar
        scrollbar = bar.scrollbar
        cursor_position = self.mapFromGlobal(QCursor.pos()).y()
        if cursor_position <= bar.position + bar.span:
            return
        scrollbar.on_page_down()

    def on_update_settings(self):
        self.timer.setInterval(settings.app_repeated_action_interval)
        self.bar.setGeometry(
            0,
            0,
            self.width(),
            self.height(),
        )
        self.update()

    def update_brush(self):
        color = self.palette().color(QPalette.ColorRole.Base)
        if self.pressed:
            color.setAlphaF(settings.app_scroll_trough_opacity_pressed)
        elif self.hover:
            color.setAlphaF(settings.app_scroll_trough_opacity_hover)
        else:
            color.setAlphaF(settings.app_scroll_trough_opacity_normal)
        self.brush = QBrush(color)
        self.update()

    def on_update_theme(self):
        utils.run_after_current_event(self.update_brush)


class Bar(QWidget):
    def __init__(self, parent, scrollbar):
        super().__init__(parent)
        self.scrollbar = scrollbar
        self._hover = False
        self._pressed = False
        self.position = 0
        self.span = 0
        self.offset_at_press = 0
        self.position_at_press = 0
        self.setAttribute(Qt.WA_TransparentForMouseEvents)
        self.brush = None
        self.update_brush()
        self.on_update_theme()

    @property
    def hover(self):
        return self._hover

    @hover.setter
    def hover(self, hover):
        self._hover = hover
        self.setProperty("hover", hover)
        self.style().polish(self)

    @property
    def pressed(self):
        return self._pressed

    @pressed.setter
    def pressed(self, pressed):
        self._pressed = pressed
        self.setProperty("pressed", pressed)
        self.style().polish(self)

    @property
    def min_bar_length(self):
        return int(
            round(
                self.width() * settings.app_scroll_bar_min_length_rel_thickness
            )
        )

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter_path = QPainterPath()
        thickness = self.width()
        radius = thickness / 2.0
        bar_geometry = QRect(0, self.position, thickness, self.span)
        painter_path.addRoundedRect(bar_geometry, radius, radius)
        painter.fillPath(painter_path, self.brush)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.update_geometry()

    def update_geometry(self):
        scrollbar = self.scrollbar
        maximum = scrollbar.maximum
        length = self.height()
        if not maximum:
            self.span = length
            self.position = 0
            self.setVisible(False)
            return
        else:
            self.setVisible(True)
        page_step = scrollbar.page_step
        rel_span = page_step / (maximum + page_step)
        self.span = max(
            int(round(rel_span * length)),
            self.min_bar_length,
        )
        rel_pos = scrollbar.value / maximum
        scrollable_span = length - self.span
        self.position = int(round(rel_pos * scrollable_span))
        self.update()

    def update_position(self):
        scrollbar = self.scrollbar
        maximum = scrollbar.maximum
        if not maximum:
            self.position = 0
            self.setVisible(False)
            return
        else:
            self.setVisible(True)
        rel_pos = scrollbar.value / maximum
        scrollable_span = self.height() - self.span
        self.position = int(round(rel_pos * scrollable_span))
        self.update()

    def update_brush(self):
        color = self.palette().color(QPalette.ColorRole.Base)
        if self.pressed:
            color.setAlphaF(settings.app_scroll_bar_opacity_pressed)
        elif self.hover:
            color.setAlphaF(settings.app_scroll_bar_opacity_hover)
        else:
            color.setAlphaF(settings.app_scroll_bar_opacity_normal)
        self.brush = QBrush(color)
        self.update()

    def on_update_theme(self):
        utils.run_after_current_event(self.update_brush)
