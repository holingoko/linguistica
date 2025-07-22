import collections
import os
import sqlite3


class DictDatabase:
    path_to_connection = dict()
    path_to_change_fns = collections.defaultdict(set)

    def __init__(self, path):
        self.path = os.path.normpath(path)
        os.makedirs(os.path.dirname(self.path), exist_ok=True)
        try:
            self.connection = self.path_to_connection[self.path]
        except KeyError:
            self.connection = sqlite3.connect(
                self.path,
                autocommit=False,
            )
            self.path_to_connection[self.path] = self.connection
        self.info = InfoTable(self.connection)
        self.entries = EntriesTable(self.connection)
        self.forms = FormsTable(self.connection)
        self.tags = TagsTable(self.connection)
        self.tag_rows = TagRowsTable(self.connection)

    def clean(self):
        self.tag_rows.remove_unused_tag_value_ids()

    def on_change(self):
        for fn in self.path_to_change_fns[self.path].copy():
            try:
                fn()
            except RuntimeError:
                self.path_to_change_fns[self.path].remove(fn)

    @property
    def on_change_fns(self):
        return self.path_to_change_fns[self.path]


class InfoTable:
    def __init__(self, connection):
        self.connection = connection
        self.connection.execute(
            """
                CREATE TABLE IF NOT EXISTS "info" (
                    "key" TEXT,
                    "value" TEXT
                ) STRICT;
            """,
        )
        self.connection.commit()

    def set_key_value(self, key, value):
        self.connection.execute(
            """
                DELETE FROM "info"
                WHERE "key" = ?;
            """,
            (key,),
        )
        self.connection.execute(
            """
                INSERT INTO "info" (
                    "key",
                    "value"
                )
                VALUES (?, ?);
            """,
            (key, value),
        )
        self.connection.commit()

    def get_key_value(self, key):
        cursor = self.connection.cursor()
        cursor.execute(
            """
                SELECT "value"
                FROM "info"
                WHERE "key" = ?
                LIMIT 1;
            """,
            (key,),
        )
        try:
            return cursor.fetchone()[0]
        except TypeError:
            return None

    def get_all_keys(self):
        cursor = self.connection.cursor()
        cursor.execute(
            """
                SELECT "key"
                FROM "info"
            """,
            (),
        )
        return {row[0] for row in cursor.fetchall()}

    def set_entry_format(self, value):
        self.set_key_value("entry_format", value)

    def get_entry_format(self):
        return self.get_key_value("entry_format")

    def set_entry_joiner(self, value):
        self.set_key_value("entry_joiner", value)

    def get_entry_joiner(self):
        return self.get_key_value("entry_joiner")


class EntriesTable:
    def __init__(self, connection):
        self.connection = connection
        self.connection.execute(
            """
                CREATE TABLE IF NOT EXISTS "entries" (
                    "entry_id" INTEGER PRIMARY KEY,
                    "template_name" TEXT
                ) STRICT;
            """,
        )
        self.connection.commit()

    def create_entry(self):
        cursor = self.connection.cursor()
        cursor.execute(
            """
                INSERT INTO "entries"
                DEFAULT VALUES;
            """,
            (),
        )
        self.connection.commit()
        entry_id = cursor.lastrowid
        return entry_id

    def delete_entry(self, entry_id):
        self.connection.execute(
            """
                DELETE FROM "entries"
                WHERE "entry_id" = ?;
            """,
            (entry_id,),
        )
        self.connection.commit()

    def get_all_entries(self):
        cursor = self.connection.cursor()
        cursor.execute(
            """
                SELECT "entry_id"
                FROM "entries"
                WHERE "template_name" IS NULL
            """,
            (),
        )
        return {row[0] for row in cursor.fetchall()}

    def get_all_templates(self):
        cursor = self.connection.cursor()
        cursor.execute(
            """
                SELECT "entry_id", "template_name"
                FROM "entries"
                WHERE "template_name" IS NOT NULL
            """,
            (),
        )
        return {row[0]: row[1] for row in cursor.fetchall()}

    def set_template_name(self, entry_id, template_name):
        self.connection.execute(
            """
                UPDATE "entries"
                SET "template_name" = ?
                WHERE "entry_id" = ?;
            """,
            (template_name, entry_id),
        )
        self.connection.commit()

    def get_template_name(self, entry_id):
        cursor = self.connection.cursor()
        cursor.execute(
            """
                SELECT "template_name"
                FROM "entries"
                WHERE "entry_id" = ?
                LIMIT 1;
            """,
            (entry_id,),
        )
        try:
            return cursor.fetchone()[0]
        except TypeError:
            return ""


class FormsTable:
    def __init__(self, connection):
        self.connection = connection
        self.connection.execute(
            """
                CREATE TABLE IF NOT EXISTS "forms" (
                    "form_id" INTEGER PRIMARY KEY,
                    "entry_id" INTEGER,
                    "order" INTEGER
                ) STRICT;
            """,
        )
        self.connection.commit()

    def create_form(self, entry_id, order):
        cursor = self.connection.cursor()
        cursor.execute(
            """
                INSERT INTO "forms" (
                    "entry_id",
                    "order"
                )
                VALUES (?, ?);
            """,
            (entry_id, order),
        )
        self.connection.commit()
        form_id = cursor.lastrowid
        return form_id

    def delete_form(self, form_id):
        self.connection.execute(
            """
                DELETE FROM "forms"
                WHERE "form_id" = ?;
            """,
            (form_id,),
        )
        self.connection.commit()

    def get_entry_for_form(self, form_id):
        cursor = self.connection.cursor()
        cursor.execute(
            """
                SELECT "entry_id"
                FROM "forms"
                WHERE "form_id" = ?
                LIMIT 1;
            """,
            (form_id,),
        )
        return cursor.fetchone()[0]

    def get_forms_for_entry(self, entry_id):
        cursor = self.connection.cursor()
        cursor.execute(
            """
                SELECT "form_id", "order"
                FROM "forms"
                WHERE "entry_id" = ?;
            """,
            (entry_id,),
        )
        sorted_rows = sorted(
            [row for row in cursor.fetchall()],
            key=lambda x: x[-1],
        )
        return [row[0] for row in sorted_rows]

    def update_form(self, form_id, order):
        self.connection.execute(
            """
                UPDATE "forms"
                SET "order" = ?
                WHERE "form_id" = ?;
            """,
            (order, form_id),
        )
        self.connection.commit()


class TagsTable:
    def __init__(self, connection):
        self.connection = connection
        self.connection.execute(
            """
                CREATE TABLE IF NOT EXISTS "tags" (
                    "tag_id" INTEGER PRIMARY KEY,
                    "tag_name" TEXT,
                    "indexed" INTEGER,
                    "tag_values_format" TEXT,
                    "order" INTEGER
                ) STRICT;
            """,
        )
        self.connection.commit()

    def create_tag(
        self,
        tag_name,
        indexed,
        tag_values_format,
        order,
        tag_id=None,
    ):
        if tag_id is None:
            cursor = self.connection.cursor()
            cursor.execute(
                """
                    INSERT INTO "tags" (
                        "tag_name",
                        "indexed",
                        "tag_values_format",
                        "order"
                    )
                    VALUES (?, ?, ?, ?);
                """,
                (tag_name, indexed, tag_values_format, order),
            )
            self.connection.commit()
            tag_id = cursor.lastrowid
        else:
            cursor = self.connection.cursor()
            cursor.execute(
                """
                    INSERT INTO "tags" (
                        "tag_id",
                        "tag_name",
                        "indexed",
                        "tag_values_format",
                        "order"
                    )
                    VALUES (?, ?, ?, ?, ?);
                """,
                (tag_id, tag_name, indexed, tag_values_format, order),
            )
            self.connection.commit()
        return tag_id

    def delete_tag(self, tag_id):
        self.connection.execute(
            """
                DELETE FROM "tags"
                WHERE "tag_id" = ?;
            """,
            (tag_id,),
        )
        self.connection.commit()

    def get_all_tags(self):
        cursor = self.connection.cursor()
        cursor.execute(
            """
                SELECT 
                    "tag_id",
                    "tag_name",
                    "indexed",
                    "tag_values_format",
                    "order"
                FROM "tags"
            """,
            (),
        )
        return [
            row[:-1] for row in sorted(cursor.fetchall(), key=lambda x: x[-1])
        ]

    def update_tag(
        self,
        tag_id,
        tag_name,
        indexed,
        tag_values_format,
        order,
    ):
        self.connection.execute(
            """
                UPDATE "tags"
                SET 
                    "tag_name" = ?,
                    "indexed" = ?,
                    "tag_values_format" = ?,
                    "order" = ?
                WHERE "tag_id" = ?
            """,
            (tag_name, indexed, tag_values_format, order, tag_id),
        )
        self.connection.commit()

    def get_tag_name(self, tag_id):
        cursor = self.connection.cursor()
        cursor.execute(
            """
                SELECT "tag_name"
                FROM "tags"
                WHERE "tag_id" = ?
                LIMIT 1;
            """,
            (tag_id,),
        )
        return cursor.fetchone()[0]

    def get_tag_id(self, tag_name):
        cursor = self.connection.cursor()
        cursor.execute(
            """
                SELECT "tag_id"
                FROM "tags"
                WHERE "tag_name" = ?
                LIMIT 1;
            """,
            (tag_name,),
        )
        return cursor.fetchone()[0]


class TagRowsTable:
    def __init__(self, connection):
        self.connection = connection
        self.connection.execute(
            """
                CREATE TABLE IF NOT EXISTS "tag_rows" (
                    "form_id" INTEGER,
                    "tag_id" INTEGER,
                    "tag_value_id" INTEGER,
                    "indexed" INTEGER,
                    "template" INTEGER,
                    "order" INTEGER
                ) STRICT;
            """,
        )
        self.connection.execute(
            """
                CREATE TABLE IF NOT EXISTS "tag_values" (
                    "tag_value_id"  INTEGER PRIMARY KEY,
                    "tag_value" TEXT UNIQUE
                ) STRICT;
            """,
        )
        self.connection.commit()
        self.properties_need_update = True
        self._indexed_tag_values = set()
        self._max_indexed_tag_value_length = 0

    @property
    def indexed_tag_values(self):
        if self.properties_need_update:
            self.update_properties()
        return self._indexed_tag_values

    @property
    def max_indexed_tag_value_length(self):
        if self.properties_need_update:
            self.update_properties()
        return self._max_indexed_tag_value_length

    def update_properties(self):
        cursor = self.connection.cursor()
        cursor.execute(
            """
                SELECT DISTINCT "tag_value_id"
                FROM "tag_rows"
                WHERE "indexed" = 1
            """,
            (),
        )
        self._indexed_tag_values = {
            self.tag_value(row[0]) for row in cursor.fetchall()
        }
        try:
            self._max_indexed_tag_value_length = max(
                (len(i) for i in self._indexed_tag_values)
            )
        except ValueError:
            self._max_indexed_tag_value_length = 0
        self.properties_need_update = False

    def tag_value_id(self, tag_value, create_if_missing):
        cursor = self.connection.cursor()
        cursor.execute(
            """
                SELECT "tag_value_id"
                FROM "tag_values"
                WHERE "tag_value" = ?
                LIMIT 1;
            """,
            (tag_value,),
        )
        try:
            return cursor.fetchone()[0]
        except TypeError:
            if not create_if_missing:
                return None
            cursor = self.connection.cursor()
            cursor.execute(
                """
                    INSERT INTO "tag_values" (
                        "tag_value"
                    )
                    VALUES (?);
                """,
                (tag_value,),
            )
            self.connection.commit()
            self.properties_need_update = True
            tag_value_id = cursor.lastrowid
            return tag_value_id

    def tag_value(self, tag_value_id):
        cursor = self.connection.cursor()
        cursor.execute(
            """
                SELECT "tag_value"
                FROM "tag_values"
                WHERE "tag_value_id" = ?
                LIMIT 1;
            """,
            (tag_value_id,),
        )
        try:
            return cursor.fetchone()[0]
        except TypeError:
            return None

    def remove_unused_tag_value_ids(self):
        cursor = self.connection.cursor()
        cursor.execute(
            """
                SELECT "tag_value_id"
                FROM "tag_values"
            """,
            (),
        )
        tag_value_ids = {row[0] for row in cursor.fetchall()}
        cursor = self.connection.cursor()
        cursor.execute(
            """
                SELECT DISTINCT "tag_value_id"
                FROM "tag_rows"
            """,
            (),
        )
        used_tag_value_ids = {row[0] for row in cursor.fetchall()}
        unused_tag_value_ids = set.difference(
            tag_value_ids,
            used_tag_value_ids,
        )
        for tag_value_id in unused_tag_value_ids:
            self.connection.execute(
                """
                    DELETE FROM "tag_values"
                    WHERE "tag_value_id" = ?;
                """,
                (tag_value_id,),
            )
        self.connection.commit()
        self.properties_need_update = True

    def set_tag_values(
        self,
        form_id,
        tag_id,
        tag_values,
        indexed,
        template,
    ):
        self.connection.execute(
            """
                DELETE FROM "tag_rows"
                WHERE "form_id" = ? AND "tag_id" = ?;
            """,
            (form_id, tag_id),
        )
        for order, tag_value in enumerate(tag_values):
            self.connection.execute(
                """
                    INSERT INTO "tag_rows" (
                        "form_id",
                        "tag_id",
                        "tag_value_id",
                        "indexed",
                        "template",
                        "order"
                    )
                    VALUES (?, ?, ?, ?, ?, ?);
                """,
                (
                    form_id,
                    tag_id,
                    self.tag_value_id(tag_value, create_if_missing=True),
                    indexed,
                    template,
                    order,
                ),
            )
        self.connection.commit()
        self.properties_need_update = True

    def get_tag_values(self, form_id, tag_id):
        cursor = self.connection.cursor()
        cursor.execute(
            """
                SELECT "tag_value_id", "order"
                FROM "tag_rows"
                WHERE "form_id" = ? AND "tag_id" = ?
            """,
            (form_id, tag_id),
        )
        sorted_rows = sorted(
            [row for row in cursor.fetchall()],
            key=lambda x: x[-1],
        )
        return [self.tag_value(row[0]) for row in sorted_rows]

    def get_tag_values_for_form(self, form_id):
        cursor = self.connection.cursor()
        cursor.execute(
            """
                SELECT "tag_id", "tag_value_id", "order"
                FROM "tag_rows"
                WHERE "form_id" = ?;
            """,
            (form_id,),
        )
        tag_values = collections.defaultdict(list)
        for row in cursor.fetchall():
            tag_values[row[0]].append(row[1:])
        for key in tag_values:
            sorted_values = sorted(tag_values[key], key=lambda x: x[-1])
            sorted_values = [self.tag_value(row[0]) for row in sorted_values]
            tag_values[key] = sorted_values
        return tag_values

    def delete_rows_for_form(self, form_id):
        self.connection.execute(
            """
                DELETE FROM "tag_rows"
                WHERE "form_id" = ?;
            """,
            (form_id,),
        )
        self.connection.commit()
        self.properties_need_update = True

    def delete_rows_for_tag(self, tag_id):
        self.connection.execute(
            """
                DELETE FROM "tag_rows"
                WHERE "tag_id" = ?;
            """,
            (tag_id,),
        )
        self.connection.commit()
        self.properties_need_update = True

    def update_indexed(self, tag_id, indexed):
        self.connection.execute(
            """
                UPDATE "tag_rows"
                SET "indexed" = ?
                WHERE "tag_id" = ?
            """,
            (indexed, tag_id),
        )
        self.connection.commit()
        self.properties_need_update = True

    def get_forms_for_indexed_tag_value(self, tag_value):
        tag_value_id = self.tag_value_id(tag_value, create_if_missing=False)
        if tag_value_id is None:
            return set()
        cursor = self.connection.cursor()
        cursor.execute(
            """
                SELECT "form_id"
                FROM "tag_rows"
                WHERE "tag_value_id" = ? AND "indexed" = 1 AND "template" = 0;
            """,
            (tag_value_id,),
        )
        return {row[0] for row in cursor.fetchall()}

    def get_forms_for_tag_with_tag_value(self, tag_id, tag_value):
        tag_value_id = self.tag_value_id(tag_value, create_if_missing=False)
        if tag_value_id is None:
            return set()
        cursor = self.connection.cursor()
        cursor.execute(
            """
                SELECT "form_id"
                FROM "tag_rows"
                WHERE "tag_id" = ? AND "tag_value_id" = ? AND "template" = 0;
            """,
            (tag_id, tag_value_id),
        )
        return {row[0] for row in cursor.fetchall()}
