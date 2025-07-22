import os
import unittest
import shutil

from src import dict_database
from src import system


class Tests(unittest.TestCase):
    def setUp(self):
        self.test_data_dir = os.path.join(system.temp_dir, "Tests")
        shutil.rmtree(self.test_data_dir, ignore_errors=True)
        os.makedirs(self.test_data_dir, exist_ok=True)
        test_index = len(dict_database.DictDatabase.path_to_connection)
        self.path = os.path.join(self.test_data_dir, f"Test{test_index}.db")
        self.db = dict_database.DictDatabase(self.path)

    def tearDown(self):
        self.db.connection.close()
        shutil.rmtree(self.test_data_dir, ignore_errors=True)

    def test_info_table(self):
        key = "key"
        value = "value"
        self.assertIsNone(self.db.info.get_key_value(key))
        self.db.info.set_key_value(key, value)
        self.assertEqual(self.db.info.get_key_value(key), value)
        self.assertEqual(self.db.info.get_all_keys(), {key})

    def test_entries_table(self):
        self.assertFalse(self.db.entries.get_all_entries())
        entry_id = self.db.entries.create_entry()
        self.assertEqual(self.db.entries.get_all_entries(), {entry_id})
        self.assertFalse(self.db.entries.get_all_templates())
        self.assertEqual(self.db.entries.get_template_name(entry_id), None)
        template_name = "name"
        self.db.entries.set_template_name(entry_id, template_name)
        self.assertEqual(
            self.db.entries.get_template_name(entry_id),
            template_name,
        )
        self.assertFalse(self.db.entries.get_all_entries())
        self.assertEqual(
            self.db.entries.get_all_templates(),
            {entry_id: template_name},
        )
        self.db.entries.delete_entry(entry_id)
        self.assertFalse(self.db.entries.get_all_entries())
        self.assertFalse(self.db.entries.get_all_templates())

    def test_forms_table(self):
        entry_id = self.db.entries.create_entry()
        self.assertFalse(self.db.forms.get_forms_for_entry(entry_id))
        form_id1 = self.db.forms.create_form(entry_id, 0)
        form_id2 = self.db.forms.create_form(entry_id, 1)
        self.assertEqual(self.db.forms.get_entry_for_form(form_id1), entry_id)
        self.assertEqual(
            self.db.forms.get_forms_for_entry(entry_id), [form_id1, form_id2]
        )
        self.db.forms.update_form(form_id2, 0)
        self.db.forms.update_form(form_id1, 1)
        self.assertEqual(
            self.db.forms.get_forms_for_entry(entry_id), [form_id2, form_id1]
        )
        self.db.forms.delete_form(form_id1)
        self.db.forms.delete_form(form_id2)
        self.assertFalse(self.db.forms.get_forms_for_entry(entry_id))

    def test_tags_table(self):
        self.assertFalse(self.db.tags.get_all_tags())
        tag_name1 = "name1"
        order1 = 0
        indexed1 = True
        values_format1 = "values_format1"
        tag_id1 = self.db.tags.create_tag(
            tag_name1,
            indexed1,
            values_format1,
            order1,
        )
        self.assertEqual(
            self.db.tags.get_all_tags(),
            [
                (tag_id1, tag_name1, indexed1, values_format1),
            ],
        )
        self.assertEqual(self.db.tags.get_tag_name(tag_id1), tag_name1)
        self.assertEqual(self.db.tags.get_tag_id(tag_name1), tag_id1)
        tag_name2 = "name2"
        self.db.tags.update_tag(
            tag_id1,
            tag_name2,
            indexed1,
            values_format1,
            order1,
        )
        self.assertEqual(
            self.db.tags.get_all_tags(),
            [
                (tag_id1, tag_name2, indexed1, values_format1),
            ],
        )
        self.assertEqual(self.db.tags.get_tag_name(tag_id1), tag_name2)
        self.assertEqual(self.db.tags.get_tag_id(tag_name2), tag_id1)
        order2 = 1
        indexed2 = False
        values_format2 = "values_format2"
        tag_id2 = self.db.tags.create_tag(
            tag_name1,
            indexed2,
            values_format2,
            order2,
        )
        self.assertEqual(
            self.db.tags.get_all_tags(),
            [
                (tag_id1, tag_name2, indexed1, values_format1),
                (tag_id2, tag_name1, indexed2, values_format2),
            ],
        )
        self.db.tags.update_tag(
            tag_id2,
            tag_name1,
            indexed1,
            values_format1,
            order1,
        )
        self.db.tags.update_tag(
            tag_id1, tag_name2, indexed2, values_format2, order2
        )
        self.assertEqual(
            self.db.tags.get_all_tags(),
            [
                (tag_id2, tag_name1, indexed1, values_format1),
                (tag_id1, tag_name2, indexed2, values_format2),
            ],
        )
        self.db.tags.delete_tag(tag_id1)
        self.db.tags.delete_tag(tag_id2)
        self.assertFalse(self.db.tags.get_all_tags())

    def test_tag_rows_table(self):
        entry_id = self.db.entries.create_entry()
        form_id1 = self.db.forms.create_form(entry_id, 0)
        form_id2 = self.db.forms.create_form(entry_id, 1)
        form_id3 = self.db.forms.create_form(entry_id, 2)
        form_id_t = self.db.forms.create_form(entry_id, 3)
        tag_id1 = self.db.tags.create_tag("name1", True, "", 0)
        tag_id2 = self.db.tags.create_tag("name2", True, "", 1)
        tag_id3 = self.db.tags.create_tag("name3", True, "", 2)
        tag_id4 = self.db.tags.create_tag("name4", True, "", 3)
        tag_id5 = self.db.tags.create_tag("name5", False, "", 3)
        tag_value1 = "value1"
        tag_value2 = "value2"
        tag_value3 = "value3"
        tag_value41 = "value41"
        tag_value42 = "value42"
        tag_value51 = "value51"
        tag_value52 = "value52"
        tag_value53 = "value53"
        tag_value_t = "template_value"
        self.db.tag_rows.set_tag_values(
            form_id1,
            tag_id1,
            [tag_value1],
            True,
            False,
        )
        self.db.tag_rows.set_tag_values(
            form_id1,
            tag_id3,
            [tag_value3],
            True,
            False,
        )
        self.db.tag_rows.set_tag_values(
            form_id1,
            tag_id4,
            [tag_value41],
            True,
            False,
        )
        self.db.tag_rows.set_tag_values(
            form_id2,
            tag_id2,
            [tag_value2],
            True,
            False,
        )
        self.db.tag_rows.set_tag_values(
            form_id2,
            tag_id3,
            [tag_value3],
            True,
            False,
        )
        self.db.tag_rows.set_tag_values(
            form_id2,
            tag_id4,
            [tag_value42],
            True,
            False,
        )
        self.db.tag_rows.set_tag_values(
            form_id3,
            tag_id5,
            [
                tag_value51,
                tag_value52,
                tag_value53,
            ],
            False,
            False,
        )
        self.assertEqual(
            self.db.tag_rows.get_tag_values_for_form(form_id1),
            {
                tag_id1: [
                    tag_value1,
                ],
                tag_id3: [
                    tag_value3,
                ],
                tag_id4: [
                    tag_value41,
                ],
            },
        )
        self.assertEqual(
            self.db.tag_rows.get_tag_values_for_form(form_id2),
            {
                tag_id2: [
                    tag_value2,
                ],
                tag_id3: [
                    tag_value3,
                ],
                tag_id4: [
                    tag_value42,
                ],
            },
        )
        self.assertEqual(
            self.db.tag_rows.get_tag_values_for_form(form_id3),
            {
                tag_id5: [
                    tag_value51,
                    tag_value52,
                    tag_value53,
                ],
            },
        )
        self.assertEqual(
            self.db.tag_rows.get_forms_for_indexed_tag_value(tag_value3),
            {form_id1, form_id2},
        )
        self.assertFalse(
            self.db.tag_rows.get_forms_for_indexed_tag_value(tag_value51),
        )
        self.assertEqual(
            sorted(self.db.tag_rows.indexed_tag_values),
            [
                tag_value1,
                tag_value2,
                tag_value3,
                tag_value41,
                tag_value42,
            ],
        )
        self.assertEqual(self.db.tag_rows.max_indexed_tag_value_length, 7)
        self.db.tag_rows.update_indexed(tag_id5, True)
        self.assertEqual(
            self.db.tag_rows.get_forms_for_indexed_tag_value(tag_value51),
            {
                form_id3,
            },
        )
        self.assertEqual(
            sorted(self.db.tag_rows.indexed_tag_values),
            [
                tag_value1,
                tag_value2,
                tag_value3,
                tag_value41,
                tag_value42,
                tag_value51,
                tag_value52,
                tag_value53,
            ],
        )
        self.assertEqual(self.db.tag_rows.max_indexed_tag_value_length, 7)
        self.assertEqual(
            self.db.tag_rows.get_forms_for_tag_with_tag_value(
                tag_id4,
                tag_value41,
            ),
            {form_id1},
        )
        self.assertEqual(
            self.db.tag_rows.get_forms_for_tag_with_tag_value(
                tag_id4,
                tag_value42,
            ),
            {form_id2},
        )
        self.assertEqual(
            self.db.tag_rows.get_tag_values(
                form_id2,
                tag_id2,
            ),
            [
                tag_value2,
            ],
        )
        self.db.tag_rows.set_tag_values(
            form_id2,
            tag_id2,
            [
                tag_value1,
            ],
            True,
            False,
        )
        self.assertEqual(
            self.db.tag_rows.get_tag_values(
                form_id2,
                tag_id2,
            ),
            [
                tag_value1,
            ],
        )
        self.db.tag_rows.delete_rows_for_tag(tag_id3)
        self.assertEqual(
            self.db.tag_rows.get_tag_values_for_form(form_id1),
            {
                tag_id1: [
                    tag_value1,
                ],
                tag_id4: [
                    tag_value41,
                ],
            },
        )
        self.assertEqual(
            self.db.tag_rows.get_tag_values_for_form(form_id2),
            {
                tag_id2: [
                    tag_value1,
                ],
                tag_id4: [
                    tag_value42,
                ],
            },
        )
        self.db.tag_rows.delete_rows_for_form(form_id1)
        self.assertFalse(self.db.tag_rows.get_tag_values_for_form(form_id1))
        self.db.tag_rows.set_tag_values(
            form_id_t,
            tag_id1,
            [tag_value_t],
            True,
            False,
        )
        self.assertTrue(
            self.db.tag_rows.get_forms_for_indexed_tag_value(tag_value_t)
        )
        self.assertTrue(
            self.db.tag_rows.get_forms_for_tag_with_tag_value(
                tag_id1,
                tag_value_t,
            )
        )
        self.db.tag_rows.set_tag_values(
            form_id_t,
            tag_id1,
            [tag_value_t],
            True,
            True,
        )
        self.assertFalse(
            self.db.tag_rows.get_forms_for_indexed_tag_value(tag_value_t)
        )
        self.assertFalse(
            self.db.tag_rows.get_forms_for_tag_with_tag_value(
                tag_id1,
                tag_value_t,
            )
        )
