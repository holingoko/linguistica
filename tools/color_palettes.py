from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *

app = QApplication()

# color_group = QPalette.ColorGroup.Active
#
# color_roles = (
#     QPalette.ColorRole.Window,
#     QPalette.ColorRole.WindowText,
# )
#
#
# widget = QWidget()
# palette = widget.palette()
# for color_role in color_roles:
#     print(palette.color(color_group, color_role))
# app.setStyleSheet(
#     "QWidget {" f"    color: red;" f"    background-color: blue;" "}"
# )
# widget = QWidget()
# palette = widget.palette()
# for color_role in color_roles:
#     print(palette.color(color_group, color_role))

color_roles = [color_role.name for color_role in QPalette.ColorRole]
print(color_roles)


class Window(QWidget):
    def __init__(self):
        super().__init__()
        self.setFixedWidth(800)
        self.setLayout(QVBoxLayout())
        for color_role in color_roles:
            label1 = QLabel(color_role)
            label2 = QLabel(color_role)
            label1.setTextInteractionFlags(
                Qt.TextInteractionFlag.TextSelectableByMouse
            )
            label2.setTextInteractionFlags(
                Qt.TextInteractionFlag.TextSelectableByMouse
            )
            # label1.setDisabled(True)
            # label2.setDisabled(True)
            # print(
            #     self.palette().color(
            #         QPalette.ColorGroup.Active,
            #         QPalette.ColorRole[color_role],
            #     )
            # )
            label1.setStyleSheet(
                f"color: orange; "
                + f"background-color: palette({color_role}); "
            )
            label2.setStyleSheet(
                f"color: palette({color_role}); "
                + f"background-color: orange; "
            )
            labels = QWidget()
            labels.setLayout(QHBoxLayout())
            labels.layout().addWidget(label1)
            labels.layout().addWidget(label2)
            labels.layout().setSpacing(0)
            labels.layout().setContentsMargins(0, 0, 0, 0)
            self.layout().addWidget(labels)


window = Window()
window.show()

app.exec()
