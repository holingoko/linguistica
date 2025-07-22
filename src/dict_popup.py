from src import dict_view
from src import settings
from src import utils
from src.qt import *


class DictPopup(QWidget):
    def __init__(self, parent, db):
        super().__init__(parent)
        self.dict_view = dict_view.PopupDictView(db)
        self.dict_view.setParent(self)
        self.dict_view.show()
        self.dict_view.text_edit.on_focus_in = self.on_focus_in
        self.dict_view.text_edit.on_focus_out = self.on_focus_out
        self.rect_width = 0
        self.rect_height = 0
        self.rect_radius = 0
        self.tri_width = 0
        self.tri_height = 0
        self.rect_y = 0
        self.triangle = None
        self.tri_base_p1 = None
        self.tri_base_p2 = None
        self.hide()
        self.brush = None
        self.pen_yes_focus = None
        self.pen_no_focus = None
        self.pen = None
        self.pen2 = None
        self.update_colors()
        self.raise_()
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

    def hide(self):
        super().hide()
        self.dict_view.text_edit.clearFocus()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        path = QPainterPath()
        path.addRoundedRect(
            0,
            self.rect_y,
            self.rect_width,
            self.rect_height,
            self.rect_radius,
            self.rect_radius,
        )
        painter.fillPath(path, self.brush)
        path = QPainterPath()
        path.addRoundedRect(
            1,
            self.rect_y + 1,
            self.rect_width - 2,
            self.rect_height - 2,
            self.rect_radius,
            self.rect_radius,
        )
        painter.setPen(self.pen)
        painter.drawPath(path)
        painter.setPen(self.pen2)
        painter.setPen(self.pen2)
        painter.drawLine(self.tri_base_p1, self.tri_base_p2)
        path = QPainterPath()
        path.addPolygon(self.triangle)
        painter.fillPath(path, self.brush)
        painter.setPen(self.pen)
        painter.drawPath(path)

    def pop_up(
        self,
        cursor_x,
        line_y_min,
        line_y_max,
        max_x,
        max_y,
        text,
        index,
    ):
        width = self.width()
        half_width = width // 2
        x_so_that_centered = cursor_x - half_width
        x = min(max(0, x_so_that_centered), max_x - width)
        tri_offset_from_center = x_so_that_centered - x
        tri_x_center = half_width + tri_offset_from_center
        diameter = self.rect_radius * 2
        tri_x_center = min(max(diameter, tri_x_center), width - diameter)
        tri_half_width = self.tri_width // 2
        tri_x_left = tri_x_center - tri_half_width
        tri_x_right = tri_x_center + tri_half_width
        height = self.height()
        room_above = line_y_min - height > 0
        room_below = line_y_max + height < max_y
        if room_above and not room_below:
            above = True
        elif room_below and not room_above:
            above = False
        else:
            above = (
                settings.dict_popup_direction
                == settings.DictPopupDirection.ABOVE
            )
        if above:
            y = line_y_min - height
            tri_y_point = height - 1
            tri_y_base = self.rect_height - 1
            self.rect_y = 0
        else:
            y = line_y_max
            tri_y_point = 1
            tri_y_base = self.tri_height + 1
            self.rect_y = self.tri_height
        self.triangle = QPolygon(
            (
                QPoint(tri_x_left, tri_y_base),
                QPoint(tri_x_center, tri_y_point),
                QPoint(tri_x_right, tri_y_base),
            )
        )
        self.tri_base_p1 = QPoint(tri_x_left, tri_y_base)
        self.tri_base_p2 = QPoint(tri_x_right, tri_y_base)
        self.move(x, y)
        half_radius = self.rect_radius // 2
        self.dict_view.move(half_radius, self.rect_y + half_radius)
        self.dict_view.look_up_around_index(text, index)
        if (
            settings.dict_popup_no_show_if_no_match
            and not self.dict_view.entry_ids
        ):
            self.hide()
        else:
            self.show()
        self.update()

    def on_focus_in(self):
        self.pen = self.pen_yes_focus
        self.update()

    def on_focus_out(self):
        self.pen = self.pen_no_focus
        self.update()

    def update_colors(self):
        background_color = self.palette().color(
            QPalette.ColorRole.Base,
        )
        yes_focus_color = self.palette().color(
            QPalette.ColorRole.HighlightedText,
        )
        no_focus_color = self.palette().color(
            QPalette.ColorRole.Text,
        )
        self.brush = QBrush(background_color)
        self.pen_yes_focus = QPen(yes_focus_color)
        self.pen_yes_focus.setJoinStyle(Qt.PenJoinStyle.MiterJoin)
        self.pen_yes_focus.setWidth(2)
        self.pen_no_focus = QPen(no_focus_color)
        self.pen_no_focus.setJoinStyle(Qt.PenJoinStyle.MiterJoin)
        self.pen_no_focus.setWidth(2)
        self.pen = self.pen_no_focus
        self.pen2 = QPen(background_color)
        self.pen2.setJoinStyle(Qt.PenJoinStyle.MiterJoin)
        self.pen2.setWidth(2)
        self.update()

    def on_update_theme(self):
        utils.run_after_current_event(self.update_colors)

    def on_update_settings(self):
        self.rect_width = int(round(settings.dict_popup_rect_width * self.dpi))
        self.rect_height = int(
            round(settings.dict_popup_rect_height * self.dpi)
        )
        self.rect_radius = int(
            round(settings.dict_popup_rect_radius * self.dpi)
        )
        self.tri_width = int(round(settings.dict_popup_tri_width * self.dpi))
        self.tri_height = int(round(settings.dict_popup_tri_height * self.dpi))
        self.setFixedWidth(self.rect_width)
        self.setFixedHeight(self.rect_height + self.tri_height)
        self.dict_view.setFixedWidth(self.rect_width - self.rect_radius)
        self.dict_view.setFixedHeight(self.rect_height - self.rect_radius)
        self.dict_view.move(self.rect_radius, self.rect_radius)
        self.update()
