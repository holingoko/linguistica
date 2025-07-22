import unittest

from src import settings
from src import settings_window


class Tests(unittest.TestCase):
    def setUp(self):
        self.window = settings_window.SettingsWindow()
        self.window.show()

    def tearDown(self):
        self.window.close()

    def test_all_settings_in_settings_window(self):
        settings_window_key_list = list()
        for scroll_widget in self.window.tab_widgets.values():
            tab_widget = scroll_widget.widget
            for widget in tab_widget.widgets:
                if widget.key is None:
                    continue
                settings_window_key_list.append(widget.key)
        special_settings_keys = {
            "action_class_to_shortcut",
            "message_class_to_choice",
        }
        settings_window_key_set = set(settings_window_key_list)
        self.assertEqual(
            sorted(settings_window_key_list),
            sorted(settings_window_key_set),
        )
        settings_keys = settings.keys - special_settings_keys
        missing_keys = sorted(settings_keys - settings_window_key_set)
        self.assertFalse(missing_keys)
