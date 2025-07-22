import os
import unittest
import shutil

from src import dict_database
from src import dict_search
from src import system


class Tests(unittest.TestCase):
    def setUp(self):
        self.test_data_dir = os.path.join(system.temp_dir, "Tests")
        shutil.rmtree(self.test_data_dir, ignore_errors=True)
        os.makedirs(self.test_data_dir, exist_ok=True)
        self.path = os.path.join(self.test_data_dir, "Test.db")
        self.db = dict_database.DictDatabase(self.path)
        self.searcher = dict_search.Searcher(self.db)

    def tearDown(self):
        self.db.connection.close()
        dict_database.DictDatabase.path_to_connection.clear()
        shutil.rmtree(self.test_data_dir, ignore_errors=True)

    def test_sort_tag_values(self):
        strings = ["a", "aa", "aaa", "A", "AA", "AAA"]
        calculated = dict_search.Searcher.sort_tag_values(strings)
        expected = [
            "AAA",
            "aaa",
            "AA",
            "aa",
            "A",
            "a",
        ]
        self.assertEqual(calculated, expected)

    def test_all_substrings(self):
        text = "123"
        calculated = dict_search.Searcher.all_substrings(text)
        expected = [
            "1",
            "2",
            "3",
            "12",
            "23",
            "123",
        ]
        self.assertEqual(sorted(calculated), sorted(expected))

    def test_substrings_around_index(self):
        text = "0123456789"
        index = 2
        max_length = 4
        calculated = dict_search.Searcher.substrings_around_index(
            text,
            index,
            max_length,
        )
        expected = [
            "2",
            "12",
            "23",
            "012",
            "123",
            "234",
            "0123",
            "1234",
            "2345",
        ]
        self.assertEqual(sorted(calculated), sorted(expected))

    def test_substrings_behind_index(self):
        text = "0123456789"
        index = 5
        max_length = 4
        calculated = dict_search.Searcher.substrings_behind_index(
            text,
            index,
            max_length,
        )
        expected = [
            "1234",
            "234",
            "34",
            "4",
        ]
        self.assertEqual(sorted(calculated), sorted(expected))

    def test_search_indexed_tags_around_index(self):
        entry_id = self.db.entries.create_entry()
        indexed = True
        template = False
        tag_id = self.db.tags.create_tag("Tag", indexed, "{{},... {}}", 0)
        tag_values_list = [["1" * i] for i in range(1, 11)]
        for order, tag_values in enumerate(tag_values_list):
            form_id = self.db.forms.create_form(entry_id, order)
            self.db.tag_rows.set_tag_values(
                form_id,
                tag_id,
                tag_values,
                indexed,
                template,
            )
        block_text = " ".join(["1" * i for i in range(1, 11)])
        block_index_and_expected = {
            0: ["1"],
            1: ["1"],
            2: ["11", "1"],
            3: ["11", "1"],
            4: ["11", "1"],
            5: ["111", "11", "1"],
            6: ["111", "11", "1"],
            7: ["111", "11", "1"],
            8: ["111", "11", "1"],
            9: ["1111", "111", "11", "1"],
            10: ["1111", "111", "11", "1"],
            11: ["1111", "111", "11", "1"],
            12: ["1111", "111", "11", "1"],
            13: ["1111", "111", "11", "1"],
            14: ["11111", "1111", "111", "11", "1"],
            15: ["11111", "1111", "111", "11", "1"],
            16: ["11111", "1111", "111", "11", "1"],
            17: ["11111", "1111", "111", "11", "1"],
            18: ["11111", "1111", "111", "11", "1"],
        }
        for block_index, expected in block_index_and_expected.items():
            calculated = [
                list(i.values())[0][0]
                for i in self.searcher.search_indexed_tags_around_index(
                    block_text,
                    block_index,
                )[0]
            ]
            self.assertEqual(sorted(calculated), sorted(expected))

    def test_search_indexed_tags_around_index2(self):
        entry_id = self.db.entries.create_entry()
        indexed = True
        template = False
        tag_id = self.db.tags.create_tag("Tag", indexed, "{{},... {}}", 0)
        tag_values_list = [
            [""],
            ["abc"],
            ["abcde"],
        ]
        for order, tag_values in enumerate(tag_values_list):
            form_id = self.db.forms.create_form(entry_id, order)
            self.db.tag_rows.set_tag_values(
                form_id,
                tag_id,
                tag_values,
                indexed,
                template,
            )
        text_index_and_expected = [
            ("", 0, []),
            ("abc", 0, ["abc"]),
            ("abc", 1, ["abc"]),
            ("abc", 2, ["abc"]),
            ("abc", 3, ["abc"]),
            ("abc", 4, []),
            ("abcde", 3, ["abcde", "abc"]),
            ("abcde", 4, ["abcde"]),
            ("abcde", 5, ["abcde"]),
            ("abcde", 6, []),
        ]
        for text, index, expected in text_index_and_expected:
            calculated = [
                list(i.values())[0][0]
                for i in self.searcher.search_indexed_tags_around_index(
                    text,
                    index,
                )[0]
            ]
            self.assertEqual(calculated, expected)

    def test_search_indexed_tags(self):
        entry_id = self.db.entries.create_entry()
        indexed = True
        template = False
        tag_id = self.db.tags.create_tag("Tag", indexed, "{{},... {}}", 0)
        tag_values_list = [
            ["word"],
            ["words"],
            ["A"],
            ["AA"],
            ["B"],
            ["BB"],
            ["a"],
            ["aa"],
            ["b"],
            ["bb"],
        ]
        for order, tag_values in enumerate(tag_values_list):
            form_id = self.db.forms.create_form(entry_id, order)
            self.db.tag_rows.set_tag_values(
                form_id,
                tag_id,
                tag_values,
                indexed,
                template,
            )
        text_and_expected = {
            "": [],
            "missing": [],
            "word": ["word"],
            "words": ["words", "word"],
            "ords": [],
            "aab": ["aa", "a", "b"],
            "abb": ["bb", "a", "b"],
            "AAB": ["AA", "aa", "A", "B", "a", "b"],
            "ABB": ["BB", "bb", "A", "B", "a", "b"],
        }
        for text, expected in text_and_expected.items():
            calculated = [
                list(i.values())[0][0]
                for i in self.searcher.search_indexed_tags(
                    text,
                )[0]
            ]
            self.assertEqual(calculated, expected)

    def test_search_tag(self):
        entry_id = self.db.entries.create_entry()
        indexed = False
        template = False
        tag_id1 = self.db.tags.create_tag("Tag1", indexed, "{{},... {}}", 0)
        tag_id2 = self.db.tags.create_tag("Tag2", indexed, "{{},... {}}", 1)
        tag_values_list = [
            (["0"], ["0"]),
            (["0"], ["3"]),
            (["1"], ["2"]),
        ]
        for order, (tag_values1, tag_values2) in enumerate(tag_values_list):
            form_id = self.db.forms.create_form(entry_id, order)
            self.db.tag_rows.set_tag_values(
                form_id,
                tag_id1,
                tag_values1,
                indexed,
                template,
            )
            self.db.tag_rows.set_tag_values(
                form_id,
                tag_id2,
                tag_values2,
                indexed,
                template,
            )
        text_tag_id_and_expected = {
            ("", tag_id1): [],
            ("", tag_id2): [],
            ("missing", tag_id1): [],
            ("missing", tag_id2): [],
            ("0", tag_id1): [[["0"], ["0"]], [["0"], ["3"]]],
            ("0", tag_id2): [[["0"], ["0"]]],
            ("1", tag_id1): [[["1"], ["2"]]],
            ("1", tag_id2): [],
            ("2", tag_id1): [],
            ("2", tag_id2): [[["1"], ["2"]]],
        }
        for (text, tag_id), expected in text_tag_id_and_expected.items():
            calculated = [
                list(i.values())
                for i in self.searcher.search_tag(
                    text,
                    tag_id,
                )[0]
            ]
            self.assertEqual(calculated, expected)
