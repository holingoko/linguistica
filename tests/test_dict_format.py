import unittest

from src import dict_format

indexed_tag = "Word"
unindexed_tag = "Definition"
indexed_tag_values = ["word"]
unindexed_tag_values = [
    "definition 1",
    "definition 2",
    "definition 3",
]


class Tests(unittest.TestCase):
    def test_formatter_simple_colon_ordered_list(self):
        entry_format = f"{{{indexed_tag}}}: {{{unindexed_tag}}}"
        tags = [
            (1, indexed_tag, True, "{{},... {}}"),
            (
                2,
                unindexed_tag,
                False,
                "{<ol><li>{}</li>...<li>{}</li></ol>}",
            ),
        ]
        tag_values = [
            (1, indexed_tag, indexed_tag_values),
            (2, unindexed_tag, unindexed_tag_values),
        ]
        formatter = dict_format.Formatter(entry_format, tags)
        tag_values_ = {key: values for _, key, values in tag_values}
        calculated = formatter.format(tag_values_)
        expected = "{}: <ol><li>{}</li><li>{}</li><li>{}</li></ol>".format(
            *tag_values[0][-1],
            *tag_values[1][-1],
        )
        self.assertEqual(calculated, expected)

    def test_formatter_simple_bold_comma_italics_semicolon(self):
        entry_format = f"<b>{{{indexed_tag}}}</b>, <i>{{{unindexed_tag}}}</i>"
        tags = [
            (1, indexed_tag, True, "{{},... {}}"),
            (
                2,
                unindexed_tag,
                False,
                "{{};... {}.}",
            ),
        ]
        tag_values = [
            (1, indexed_tag, indexed_tag_values),
            (2, unindexed_tag, unindexed_tag_values),
        ]
        formatter = dict_format.Formatter(entry_format, tags)
        tag_values_ = {key: values for _, key, values in tag_values}
        calculated = formatter.format(tag_values_)
        expected = "<b>{}</b>, <i>definition 1; definition 2; definition 3.</i>".format(
            *tag_values[0][-1],
            *tag_values[1][-1],
        )
        self.assertEqual(calculated, expected)

    def test_formatter_missing_tags_empty(self):
        entry_format = f"{{<b>{{{indexed_tag}}}</b>, <i>{{{unindexed_tag}}}</i>}}"
        tags = [
            (1, indexed_tag, True, "{{},... {}}"),
            (
                2,
                unindexed_tag,
                False,
                "{{};... {}.}",
            ),
        ]
        formatter = dict_format.Formatter(entry_format, tags)
        tag_values_list = [
            {
                indexed_tag: [],
                unindexed_tag: [],
            },
            {
                indexed_tag: [],
                unindexed_tag: unindexed_tag_values,
            },
            {indexed_tag: indexed_tag_values, unindexed_tag: []},
        ]
        for tag_values in tag_values_list:
            calculated = formatter.format(tag_values)
            expected = ""
            self.assertEqual(calculated, expected)

    def test_format_template(self):
        in_and_expected = [
            (
                [
                    [
                        (1, "Word", ["{}1"]),
                        (2, "Definition", ["{}"]),
                    ],
                    [
                        (1, "Word", ["{}2"]),
                        (2, "Definition", ["{}"]),
                    ],
                ],
                [
                    (1, "Word", ["form"]),
                    (2, "Definition", ["definition"]),
                ],
                [
                    [
                        (1, "Word", ["form1"]),
                        (2, "Definition", ["definition"]),
                    ],
                    [
                        (1, "Word", ["form2"]),
                        (2, "Definition", ["definition"]),
                    ],
                ],
            ),
            (
                [
                    [
                        (1, "Word", ["{}1"]),
                        (2, "Definition", ["{}"]),
                    ],
                    [
                        (1, "Word", ["{}2"]),
                        (2, "Definition", ["{}"]),
                    ],
                ],
                [
                    (1, "Word", ["form"]),
                    (
                        2,
                        "Definition",
                        [
                            "definition1",
                            "definition2",
                            "definition3",
                        ],
                    ),
                ],
                [
                    [
                        (1, "Word", ["form1"]),
                        (
                            2,
                            "Definition",
                            [
                                "definition1",
                                "definition2",
                                "definition3",
                            ],
                        ),
                    ],
                    [
                        (1, "Word", ["form2"]),
                        (
                            2,
                            "Definition",
                            [
                                "definition1",
                                "definition2",
                                "definition3",
                            ],
                        ),
                    ],
                ],
            ),
        ]
        for template_form_data, stem_form_data, expected in in_and_expected:
            calculated = dict_format.format_template(
                template_form_data,
                stem_form_data,
            )
            self.assertEqual(calculated, expected)

    def test_entry_format_tags(self):
        tag1 = "tag1"
        tag2 = "tag2"
        tag3 = "tag3"
        tag4 = "tag4"
        entry_format = "{{" + tag1 + "}{" + tag2 + "}}|{" + tag3 + "}{" + tag4 + "}"
        calculated = dict_format.Formatter.entry_format_tags(entry_format)
        expected = {tag1, tag2, tag3, tag4}
        self.assertEqual(calculated, expected)

    def test_format_multiple_values(self):
        tag1 = "tag1"
        tag2 = "tag2"
        tag3 = "tag3"
        tag4 = "tag4"
        multiple_values_format = "{}|{{} and {}}|{{},... {}, and {}}"
        in_and_expected = {
            (tag1,): f"{tag1}",
            (tag1, tag2): f"{tag1} and {tag2}",
            (tag1, tag2, tag3): f"{tag1}, {tag2}, and {tag3}",
            (tag1, tag2, tag3, tag4): f"{tag1}, {tag2}, {tag3}, and {tag4}",
        }
        for in_, expected in in_and_expected.items():
            calculated = dict_format.Formatter.format_multiple_values(
                in_,
                multiple_values_format,
            )
            self.assertEqual(calculated, expected)

    def test_format_multiple_values_too_many(self):
        tag1 = "tag1"
        tag2 = "tag2"
        tag3 = "tag3"
        tag4 = "tag4"
        multiple_values_format = "{}|{{}, {}, and {}}"
        in_and_expected = {
            (tag1,): f"{tag1}",
            (tag1, tag2): f"{tag1}",
            (tag1, tag2, tag3): f"{tag1}, {tag2}, and {tag3}",
            (tag1, tag2, tag3, tag4): f"{tag1}, {tag2}, and {tag3}",
        }
        for in_, expected in in_and_expected.items():
            calculated = dict_format.Formatter.format_multiple_values(
                in_,
                multiple_values_format,
            )
            self.assertEqual(calculated, expected)

    def test_format_multiple_values_too_many2(self):
        tag1 = "tag1"
        tag2 = "tag2"
        tag3 = "tag3"
        tag4 = "tag4"
        multiple_values_format = "{{},... {}, and {}}"
        in_and_expected = {
            (tag1,): "",
            (tag1, tag2): f"{tag1}, and {tag2}",
            (tag1, tag2, tag3): f"{tag1}, {tag2}, and {tag3}",
            (tag1, tag2, tag3, tag4): f"{tag1}, {tag2}, {tag3}, and {tag4}",
        }
        for in_, expected in in_and_expected.items():
            calculated = dict_format.Formatter.format_multiple_values(
                in_,
                multiple_values_format,
            )
            self.assertEqual(calculated, expected)
