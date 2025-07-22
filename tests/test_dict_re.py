import unittest

from src import dict_re


class Tests(unittest.TestCase):
    def test_parse_format_flat(self):
        test_string = "{0} {1}{2} {3}|{4} {5}|{6}|{7}  {8}  {9}"
        calculated1, calculated2 = dict_re.parse_format(test_string)
        expected1 = "{} {}{} {} {}  {}  {}"
        expected2 = [
            "{0}",
            "{1}",
            "{2}",
            "{3}|{4}",
            "{5}|{6}|{7}",
            "{8}",
            "{9}",
        ]
        self.assertEqual(calculated1, expected1)
        self.assertEqual(calculated2, expected2)

    def test_parse_format_nested(self):
        test_string = "{{0}} {1}|{{2}} {{3}{4}}|{5}|{ {6} {7} } {{8}|{9}}"
        calculated1, calculated2 = dict_re.parse_format(test_string)
        expected1 = "{} {} {} {}"
        expected2 = [
            "{{0}}",
            "{1}|{{2}}",
            "{{3}{4}}|{5}|{ {6} {7} }",
            "{{8}|{9}}",
        ]
        self.assertEqual(calculated1, expected1)
        self.assertEqual(calculated2, expected2)

    def test_parse_conditional(self):
        in_and_expected = {
            "{0}": [("{}", ["0"])],
            "{{0}}": [("{}", ["0"])],
            "{0}|{1}": [("{}", ["0"]), ("{}", ["1"])],
            "{0}|{{1}{2}{3}}": [("{}", ["0"]), ("{}{}{}", ["1", "2", "3"])],
            "{0}|{1}|{ {2} {3} }": [
                ("{}", ["0"]),
                ("{}", ["1"]),
                (" {} {} ", ["2", "3"]),
            ],
            "{0}|{1}|{|{2}|{3}|}": [
                ("{}", ["0"]),
                ("{}", ["1"]),
                ("|{}|{}|", ["2", "3"]),
            ],
        }
        for in_, expected in in_and_expected.items():
            calculated = dict_re.parse_conditional(in_)
            self.assertEqual(calculated, expected)

    def test_replace_non_conditional_vertical_bar(self):
        in_and_expected = {
            "{|}": "{" + dict_re.vertical_bar + "}",
            "{||}": ("{" + dict_re.vertical_bar + dict_re.vertical_bar + "}"),
            "{|{}|}": ("{" + dict_re.vertical_bar + "{}" + dict_re.vertical_bar + "}"),
        }
        for in_, expected in in_and_expected.items():
            calculated = dict_re.replace_non_conditional_vertical_bar(in_)
            self.assertEqual(calculated, expected)

    def test_parse_expression(self):
        in_and_expected = {
            "{0}": ("{}", ["0"]),
            "{{0}}": ("{}", ["0"]),
            "{ {0} }": (" {} ", ["0"]),
            "{{0}{1}{2}}": ("{}{}{}", ["0", "1", "2"]),
            "{ {0} {1} {2} }": (" {} {} {} ", ["0", "1", "2"]),
            "{{0}|{1}|{2}}": ("{}|{}|{}", ["0", "1", "2"]),
        }
        for in_, expected in in_and_expected.items():
            calculated = dict_re.parse_expression(in_)
            self.assertEqual(calculated, expected)

    def test_parse_info_tags(self):
        in_and_expected = {
            "{}": ("{}", (False,)),
            "{<-}": ("", (True,)),
            "{}{<-}": ("{}", (True,)),
            "{<-}{}": ("{}", (True,)),
            "{}{<-}{}": ("{}{}", (True,)),
        }
        for in_, expected in in_and_expected.items():
            calculated = dict_re.parse_option_tags(in_)
            self.assertEqual(calculated, expected)

    def test_expand_tag_values_format_expression(self):
        in_and_expected = {
            ("", 0): "",
            ("{}", 0): "",
            ("", 1): "",
            ("{}", 1): "{}",
            ("{}", 2): "",
            ("{} and {}", 1): "",
            ("{} and {}", 2): "{} and {}",
            ("{}...{}", 1): "{}",
            ("{}...{}", 2): "{}{}",
            ("{}...{}", 3): "{}{}{}",
            ("{},... {}", 1): "{}",
            ("{},... {}", 2): "{}, {}",
            ("{},... {}", 3): "{}, {}, {}",
            ("{}..., {}", 2): "{}, {}",
            ("{}, ...{}", 2): "{}, {}",
            (r"{}\...{}", 2): "{}...{}",
            ("{},... {}, and {}", 3): "{}, {}, and {}",
            ("{},... {}, and {}", 4): "{}, {}, {}, and {}",
            ("{}, and {},... {}", 3): "{}, and {}, {}",
            ("{}, and {},... {}", 4): "{}, and {}, {}, {}",
            (r"{},... {}, \... {}", 3): "{}, {}, ... {}",
            (r"{},... {}, \... {}", 4): "{}, {}, {}, ... {}",
            ("s...e", 1): "s{}e",
            ("s...e", 2): "s{}{}e",
            ("s...e", 3): "s{}{}{}e",
            ("s..., {}e", 1): "s{}e",
            ("s..., {}e", 2): "s{}, {}e",
            ("s..., {}e", 3): "s{}, {}, {}e",
            ("s{}, ...e", 1): "s{}e",
            ("s{}, ...e", 2): "s{}, {}e",
            ("s{}, ...e", 3): "s{}, {}, {}e",
            ("s..., {}, and {}e", 3): "s{}, {}, and {}e",
            ("s..., {}, and {}e", 4): "s{}, {}, {}, and {}e",
            ("s{} and {}, ...e", 3): "s{} and {}, {}e",
            ("s{} and {}, ...e", 4): "s{} and {}, {}, {}e",
            ("s{}, {} and ...e", 1): "",
            ("s{}, {} and ...e", 2): "s{}, {}e",
            ("s{}, {} and ...e", 3): "s{}, {} and {}e",
            ("s{}, {} and ...e", 4): "s{}, {} and {} and {}e",
            ("s... and {}, {}e", 1): "",
            ("s... and {}, {}e", 2): "s{}, {}e",
            ("s... and {}, {}e", 3): "s{} and {}, {}e",
            ("s... and {}, {}e", 4): "s{} and {} and {}, {}e",
            (
                "{}st, {}nd, {}rd, {}th,... {}th",
                9,
            ): "{}st, {}nd, {}rd, {}th, {}th, {}th, {}th, {}th, {}th",
        }
        for in_, expected in in_and_expected.items():
            calculated = dict_re.expand_tag_values_format_expression(*in_)
            self.assertEqual(calculated, expected)

    def test_replace_non_continuation_ellipsis(self):
        in_and_expected = {
            r"\...": dict_re.ellipsis_,
            r"{}...\...{}": f"{{}}...{dict_re.ellipsis_}{{}}",
            r"{}, {}, \... {}": f"{{}}, {{}}, {dict_re.ellipsis_} {{}}",
        }
        for in_, expected in in_and_expected.items():
            calculated = dict_re.replace_non_continuation_ellipsis(in_)
            self.assertEqual(calculated, expected)

    def test_replace_and_restore_non_tag_curly_braces(self):
        in_and_expected = {
            r"\{\}": (
                f"{dict_re.left_curly_brace}{dict_re.right_curly_brace}",
                "{}",
            ),
            r"\{{}\}": (
                f"{dict_re.left_curly_brace}{{}}{dict_re.right_curly_brace}",
                "{{}}",
            ),
            r"{\{\}}": (
                f"{{{dict_re.left_curly_brace}{dict_re.right_curly_brace}}}",
                "{{}}",
            ),
            r"{}\{\}{}": (
                f"{{}}{dict_re.left_curly_brace}{dict_re.right_curly_brace}{{}}",
                "{}{}{}",
            ),
            r"\{\}{}\{\}": (
                f"{dict_re.left_curly_brace}{dict_re.right_curly_brace}{{}}{dict_re.left_curly_brace}{dict_re.right_curly_brace}",
                "{}{}{}",
            ),
        }
        for in_, (expected1, expected2) in in_and_expected.items():
            calculated1 = dict_re.replace_non_tag_curly_braces(in_)
            calculated2 = dict_re.restore_non_tag_curly_braces(calculated1)
            self.assertEqual(calculated1, expected1)
            self.assertEqual(calculated2, expected2)

    def test_check_tag_valid(self):
        in_and_expected = {
            "": False,
            "a": True,
            "A": True,
            "1": True,
            " ": True,
            "_": True,
            "字": True,
            ".": False,
            "?": False,
            "!": False,
            ",": False,
            ";": False,
            ":": False,
            '"': False,
            "|": False,
            "{}": False,
            "abcABC123": True,
            "abcABC123.": False,
            "{abcABC123}": False,
        }
        for in_, expected in in_and_expected.items():
            calculated = dict_re.check_tag_valid(in_)
            self.assertEqual(calculated, expected)
