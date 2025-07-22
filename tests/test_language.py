import unittest

from src import system

system.running_unit_test = True

from src import main_window as avoid_circular_import
from src import language


class Tests(unittest.TestCase):
    def test_get_texts_to_translate(self):
        source_texts_and_expected = {
            """\ntr("This is a test.")\n""": ["This is a test."],
            """    tr("This is a test.")\n""": ["This is a test."],
            """    tr(\n"""
            """        "This is a test.",\n"""
            """    )""": ["This is a test."],
            """    tr(\n"""
            """        "This "\n"""
            """        "is "\n"""
            """        "a "\n"""
            """        "test."\n"""
            """    )\n""": ["This is a test."],
            """    f'{tr("This is a test.")}'\n""": ["This is a test."],
            """    [tr("This is a test.")]\n""": ["This is a test."],
            """    (tr("This is a test."))\n""": ["This is a test."],
            """    =tr('This is a test.')\n""": ["This is a test."],
            """    tr('This is a "test".')\n""": ['This is a \\"test\\".'],
            """    tr('This is a /[test/].')\n""": ["This is a (test)."],
            """    not_tr("This text should not be included.")\n""": [],
            """    tr("{} ")\n""": ["{} "],
            """    tr('{}: "{}"')\n""": ['{}: \\"{}\\"'],
            """    tr("{} [{}]: ")\n""": ["{} [{}]: "],
        }
        for source_text, expected in source_texts_and_expected.items():
            calculated = language.get_texts_to_translate(source_text)
            self.assertEqual(calculated, expected)

    def test_get_translations(self):
        po_text = (
            """msgid ""\n"""
            """msgstr ""\n"""
            """\n"""
            """\n"""
            """msgid "key1"\n"""
            """msgstr "value1"\n"""
            """\n"""
            """msgid "key2"\n"""
            """msgstr "value2"\n"""
            """\n"""
            """msgid "\\"{}\\""\n"""
            """msgstr "\\"{}\\""\n"""
            """\n"""
            """msgid "key3"\n"""
            """msgstr "value3"\n"""
            """\n"""
        )
        calculated = language.get_translations(po_text)
        expected = {
            "": "",
            "key1": "value1",
            "key2": "value2",
            '"{}"': '"{}"',
            "key3": "value3",
        }
        self.assertEqual(calculated, expected)
