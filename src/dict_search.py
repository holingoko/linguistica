import itertools


class Searcher:
    def __init__(self, db):
        self.db = db

    @staticmethod
    def sort_tag_values(strings):
        return sorted(strings, key=lambda s: (-len(s), s))

    @staticmethod
    def all_substrings(text):
        return [
            text[i:j]
            for i, j in itertools.combinations(
                range(len(text) + 1),
                r=2,
            )
        ]

    @staticmethod
    def substrings_around_index(text, index, max_length):
        if index > len(text) - 1:
            return []
        return [
            text[i : i + length]
            for length in range(1, max_length + 1)
            for i in range(max(index - length + 1, 0), index + 1)
        ]

    @staticmethod
    def substrings_behind_index(text, index, max_length):
        if index > len(text):
            return []
        return [
            text[index - length : index]
            for length in range(1, min(max_length, index) + 1)
        ]

    def search_indexed_tags_around_index(self, text, index):
        if not text:
            return [], set()
        indexed_tag_values = self.db.tag_rows.indexed_tag_values
        matches = set()
        for substring in self.substrings_around_index(
            text,
            index,
            self.db.tag_rows.max_indexed_tag_value_length,
        ) + self.substrings_behind_index(
            text,
            index,
            self.db.tag_rows.max_indexed_tag_value_length,
        ):
            if substring in indexed_tag_values:
                matches.add(substring)
            lower = substring.lower()
            if lower in indexed_tag_values:
                matches.add(lower)
        matches = self.sort_tag_values(matches)
        tag_values_list = []
        entry_ids = set()
        for match in matches:
            form_ids = self.db.tag_rows.get_forms_for_indexed_tag_value(match)
            for form_id in form_ids:
                tag_values_list.append(
                    self.db.tag_rows.get_tag_values_for_form(form_id)
                )
                entry_ids.add(self.db.forms.get_entry_for_form(form_id))
        return tag_values_list, entry_ids

    def search_indexed_tags(self, text, exact=False):
        if not text:
            return [], set()
        indexed_tag_values = self.db.tag_rows.indexed_tag_values
        if exact:
            matches = {text} if text in indexed_tag_values else set()
        else:
            matches = set()
            for substring in self.all_substrings(text):
                if substring in indexed_tag_values:
                    matches.add(substring)
                lower = substring.lower()
                if lower in indexed_tag_values:
                    matches.add(lower)
            matches = self.sort_tag_values(matches)
        tag_values_list = []
        entry_ids = set()
        for match in matches:
            form_ids = self.db.tag_rows.get_forms_for_indexed_tag_value(match)
            for form_id in form_ids:
                tag_values_list.append(
                    self.db.tag_rows.get_tag_values_for_form(form_id)
                )
                entry_ids.add(self.db.forms.get_entry_for_form(form_id))
        return tag_values_list, entry_ids

    def search_tag(self, text, tag_id, exact=False):
        if not text:
            return [], set()
        if exact:
            values_to_check = {text}
        else:
            values_to_check = set()
            for substring in self.all_substrings(text):
                values_to_check.add(substring)
                values_to_check.add(substring.lower())
            values_to_check = self.sort_tag_values(values_to_check)
        tag_values_list = []
        entry_ids = set()
        for tag_value in values_to_check:
            form_ids = self.db.tag_rows.get_forms_for_tag_with_tag_value(
                tag_id,
                tag_value,
            )
            for form_id in form_ids:
                tag_values_list.append(
                    self.db.tag_rows.get_tag_values_for_form(form_id)
                )
                entry_ids.add(self.db.forms.get_entry_for_form(form_id))
        return tag_values_list, entry_ids
