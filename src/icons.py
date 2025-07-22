import os

from src.qt import *

repo_dir = os.path.dirname(os.path.dirname(__file__))
images_dir = os.path.join(repo_dir, "resources", "images")
fonts_dir = os.path.join(repo_dir, "resources", "fonts")
app_icon_path = os.path.join(images_dir, "icon.png")
app_icon_font_path = os.path.join(fonts_dir, "Cardo", "Cardo-Bold.ttf")


def app_icon_font(icon_size):
    QFontDatabase.addApplicationFont(app_icon_font_path)
    font_size = int(round(3.0 * icon_size / 4.0))
    font = QFont(
        "Cardo",
        font_size,
        QFont.Weight.Bold,
    )
    font.setStyleStrategy(QFont.StyleStrategy.PreferAntialias)
    return font


def generate_app_icon():
    icon_size = 1024
    pixmap1 = QPixmap(icon_size, icon_size)
    pixmap2 = QPixmap(icon_size, icon_size)
    pixmap = QPixmap(icon_size, icon_size)
    transparent = "#00000000"
    pixmap1.fill(transparent)
    pixmap2.fill(transparent)
    pixmap.fill(transparent)
    font = app_icon_font(icon_size)
    color1 = "#EE1111"
    color2 = "#1111EE"
    painter1 = QPainter(pixmap1)
    painter2 = QPainter(pixmap2)
    painter = QPainter(pixmap)
    painter1.setFont(font)
    painter2.setFont(font)
    pen1 = QPen(color1)
    pen2 = QPen(color2)
    painter1.setPen(pen1)
    painter2.setPen(pen2)
    rect = QRect(0, 0, icon_size, icon_size)
    text = "L"
    painter1.drawText(
        rect,
        text,
        Qt.AlignmentFlag.AlignCenter,
    )
    painter2.drawText(
        rect,
        text,
        Qt.AlignmentFlag.AlignCenter,
    )
    y_offset = 145
    polygon1 = QPolygon(
        (
            QPoint(icon_size, icon_size - y_offset),
            QPoint(0, icon_size - y_offset),
            QPoint(icon_size, 0 - y_offset),
        )
    )
    polygon2 = QPolygon(
        (
            QPoint(0, 0 - y_offset),
            QPoint(0, icon_size - y_offset),
            QPoint(icon_size, 0 - y_offset),
        )
    )
    path1 = QPainterPath()
    path2 = QPainterPath()
    path1.addPolygon(polygon1)
    path2.addPolygon(polygon2)
    brush = QBrush(transparent)
    painter1.setCompositionMode(
        QPainter.CompositionMode.CompositionMode_Clear,
    )
    painter2.setCompositionMode(
        QPainter.CompositionMode.CompositionMode_Clear,
    )
    painter1.fillPath(path1, brush)
    painter2.fillPath(path2, brush)
    origin = QPoint(0, 0)
    painter.drawPixmap(origin, pixmap1)
    painter.drawPixmap(origin, pixmap2)
    pixmap.save(app_icon_path)
    painter1.end()
    painter2.end()
    painter.end()
    return


if not os.path.exists(app_icon_path):
    generate_app_icon()
app_icon = QIcon(app_icon_path)
