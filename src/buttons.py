from src import utils
from src.qt import *


class PushButton(QPushButton):
    def __init__(self, action):
        super().__init__()
        self.action = action
        self.mouse = False
        self.release = False
        self.pressed.connect(self.on_pressed)
        self.released.connect(self.on_release)

    def mousePressEvent(self, event):
        self.mouse = True
        self.release = False
        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        self.release = True
        super().mouseReleaseEvent(event)
        self.mouse = False

    def on_pressed(self):
        self.setDown(True)
        if not self.mouse:
            self.action()

    def on_release(self):
        self.setDown(False)
        if self.mouse and self.release:
            self.action()


class FocusedIsDefaultPushButton(PushButton):
    def __init__(self, action, button_list):
        super().__init__(action)
        self.button_list = button_list
        self.button_list.append(self)
        self.prev_default = None

    def enterEvent(self, event):
        super().enterEvent(event)
        self.prev_default = self.default_button()
        self.make_default()

    def leaveEvent(self, event):
        super().leaveEvent(event)
        self.prev_default.make_default()

    def focusInEvent(self, event):
        self.make_default()

    def mouseReleaseEvent(self, event):
        super().mouseReleaseEvent(event)
        self.prev_default = self

    def default_button(self):
        for button in self.button_list:
            if button.isDefault():
                return button
        else:
            return None

    def make_default(self):
        for button in self.button_list:
            button.setDefault(False)
        self.setDefault(True)


class TextButton(QLabel):
    def __init__(self, action):
        super().__init__()
        self.action = action
        self._hover = False
        self._pressed = False

    @property
    def hover(self):
        return self._hover

    @hover.setter
    def hover(self, hover):
        self._hover = hover
        self.setProperty("hover", hover)
        self.setProperty("hover_and_pressed", hover and self.pressed)
        self.style().polish(self)

    @property
    def pressed(self):
        return self._pressed

    @pressed.setter
    def pressed(self, pressed):
        self._pressed = pressed
        self.setProperty("pressed", pressed)
        self.setProperty("hover_and_pressed", self.hover and pressed)
        self.style().polish(self)

    def enterEvent(self, event):
        self.hover = True

    def leaveEvent(self, event):
        self.hover = False

    def mousePressEvent(self, event):
        self.pressed = True

    def mouseReleaseEvent(self, event):
        if self.hover:
            self.action()
        self.pressed = False

    def mouseMoveEvent(self, event):
        if self.rect().contains(event.pos()):
            self.hover = True
        else:
            self.hover = False

    def setText(self, text):
        super().setText(f" {text} ")


class TabButton(QLabel):
    def __init__(self, on_mouse_press):
        super().__init__()
        self.on_mouse_press = on_mouse_press
        self._is_active = False
        self.on_update_settings()

    @property
    def height_(self):
        return utils.calculate_default_height(QLabel) * 1.75

    @property
    def is_active(self):
        return self._is_active

    @is_active.setter
    def is_active(self, is_active):
        self._is_active = is_active
        self.setProperty("is_active", is_active)
        self.style().polish(self)

    def mousePressEvent(self, event):
        self.on_mouse_press()

    def on_update_settings(self):
        self.setFixedHeight(self.height_)
        self.update()
