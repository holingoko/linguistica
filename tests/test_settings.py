import unittest

from src import settings


class Tests(unittest.TestCase):
    def setUp(self):
        settings.reset()

    def tearDown(self):
        settings.reset()

    def test_save_load_round_trip(self):
        values_pre_save = [getattr(settings, key) for key in settings.keys]
        settings.save()
        settings.load()
        values_post_load = [getattr(settings, key) for key in settings.keys]
        self.assertEqual(values_post_load, values_pre_save)
