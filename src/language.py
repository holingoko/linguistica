import os
import re

from src import app
from src import dict_re
from src import messages
from src import settings
from src import system
from src.qt import *

repo_dir = os.path.dirname(os.path.dirname(__file__))
languages_dir = os.path.join(repo_dir, "resources", "languages")
pot_path = os.path.join(languages_dir, "Language.pot")
os.makedirs(languages_dir, exist_ok=True)
os.makedirs(settings.app_user_added_languages_dir, exist_ok=True)
text_to_be_translated_regex = r"[ \{\[\(=]tr\([^\)]*\)"
text_to_be_translated_pattern = re.compile(text_to_be_translated_regex)
unjoined_strings_regex = r"[\"'][ ]+[\"']"
unjoined_strings_pattern = re.compile(unjoined_strings_regex)
quoted_string_regex = r"[\"']+.*[\"']+"
quoted_string_pattern = re.compile(quoted_string_regex)
msgid_regex = r'msgid ".*"'
msgid_pattern = re.compile(msgid_regex)
msgstr_regex = r'msgstr ".*"'
msgstr_pattern = re.compile(msgstr_regex)
language_direction_key = "Language Direction (translate as either -> for left to right or <- for right to left)"


def escape_quote(string):
    return string.replace('"', '\\"')


def unescape_quote(string):
    return string.replace('\\"', '"')


def restore_parenthesis(string):
    return string.replace("/[", "(").replace("/]", ")")


def get_texts_to_translate(source_text):
    source_text = source_text.replace(
        "\n",
        " ",
    ).replace(
        "\r",
        " ",
    )
    source_text = unjoined_strings_pattern.sub("", source_text)
    texts_to_translate = []
    for match in text_to_be_translated_pattern.findall(source_text):
        match = quoted_string_pattern.search(match).group()
        texts_to_translate.append(
            restore_parenthesis(
                escape_quote(
                    match[1:-1],
                )
            )
        )
    return texts_to_translate


def get_texts_to_translate_():
    texts_to_translate = set()
    dir_path = os.path.dirname(__file__)
    for file_name in os.listdir(dir_path):
        if os.path.splitext(file_name)[1] != ".py":
            continue
        file_path = os.path.join(dir_path, file_name)
        try:
            with open(file_path, mode="r", encoding="utf-8") as file:
                source_code = file.read()
                texts_to_translate.update(get_texts_to_translate(source_code))
        except PermissionError:
            continue
    return texts_to_translate


def update_translation_files():
    texts_to_translate = sorted(get_texts_to_translate_())
    po_lines = [
        'msgid ""\n',
        'msgstr ""\n',
        "\n",
    ]
    pot_lines = [
        'msgid ""\n',
        'msgstr ""\n',
        "\n",
    ]
    for text in texts_to_translate:
        po_lines.extend(
            (
                f'msgid "{text}"\n',
                f'msgstr "{text}"\n',
                "\n",
            )
        )
        pot_lines.extend(
            (
                f'msgid "{text}"\n',
                'msgstr ""\n',
                "\n",
            )
        )
    po_lines.extend(
        (
            f'msgid "{language_direction_key}"\n',
            f'msgstr "->"\n',
            "\n",
        )
    )
    pot_lines.extend(
        (
            f'msgid "{language_direction_key}"\n',
            'msgstr ""\n',
            "\n",
        )
    )
    po_path = os.path.join(languages_dir, "English.po")
    with open(po_path, mode="w", encoding="utf-8") as file:
        file.writelines(po_lines)
    with open(pot_path, mode="w", encoding="utf-8") as file:
        file.writelines(pot_lines)


if not system.running_built_app and not system.running_unit_test:
    update_translation_files()
translations = dict()


def get_translations(po_text):
    return {
        unescape_quote(msgid[7:-1]): unescape_quote(msgstr[8:-1])
        for msgid, msgstr in zip(
            msgid_pattern.findall(po_text),
            msgstr_pattern.findall(po_text),
            strict=True,
        )
    }


direction = None
alignment = None
rtl_tag_or_empty_string = None


def update_alignment():
    global direction, alignment, rtl_tag_or_empty_string
    if settings.app_language_direction == settings.LanguageDirection.AUTOMATIC:
        language_direction_value = translate(language_direction_key)
        if language_direction_value == "<-":
            direction = settings.LanguageDirection.RIGHT_TO_LEFT
        else:
            direction = settings.LanguageDirection.LEFT_TO_RIGHT
    elif (
        settings.app_language_direction
        == settings.LanguageDirection.RIGHT_TO_LEFT
    ):
        direction = settings.LanguageDirection.RIGHT_TO_LEFT
    else:
        direction = settings.LanguageDirection.LEFT_TO_RIGHT
    if direction == settings.LanguageDirection.RIGHT_TO_LEFT:
        alignment = Qt.AlignmentFlag.AlignRight
        rtl_tag_or_empty_string = dict_re.reversed_tag
        app.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
    else:
        alignment = Qt.AlignmentFlag.AlignLeft
        rtl_tag_or_empty_string = ""
        app.setLayoutDirection(Qt.LayoutDirection.LeftToRight)


def get_available_languages():
    languages = []
    for file_name in os.listdir(languages_dir):
        language, ext = os.path.splitext(file_name)
        if ext.lower() == ".po":
            languages.append(language)
    for file_name in os.listdir(settings.app_user_added_languages_dir):
        language, ext = os.path.splitext(file_name)
        if ext.lower() == ".po":
            languages.append(language)
    return sorted(languages)


def load_language():
    global translations
    translations = dict()
    try:
        with open(
            os.path.join(languages_dir, f"{settings.app_language}.po"),
            mode="r",
            encoding="utf-8",
        ) as file:
            po_text = file.read()
    except FileNotFoundError:
        try:
            with open(
                os.path.join(
                    settings.app_user_added_languages_dir,
                    f"{settings.app_language}.po",
                ),
                mode="r",
                encoding="utf-8",
            ) as file:
                po_text = file.read()
        except FileNotFoundError:
            missing_language = settings.app_language
            settings.app_language = settings.defaults["app_language"]
            settings.save()
            load_language()
            error_message = messages.MissingLanguageErrorMessage(
                missing_language
            )
            error_message.show()
            error_message.move_to_center()
            return
    translations.clear()
    translations.update(get_translations(po_text))
    update_alignment()
    check_for_missing_translations()


def check_for_missing_translations():
    with open(
        os.path.join(languages_dir, f"{settings.defaults['app_language']}.po"),
        mode="r",
        encoding="utf-8",
    ) as file:
        po_text = file.read()
    default_translations = get_translations(po_text)
    missing_translation = False
    for key in default_translations:
        if key not in translations:
            missing_translation = True
            print(
                f'{settings.app_language}.po is missing translation for "{key}".'
            )
    if missing_translation:
        messages.MissingTranslationsWarningMessage(
            settings.app_language
        ).show()


def translate(text):
    try:
        return translations[text]
    except KeyError:
        try:
            return translations[restore_parenthesis(text)]
        except KeyError:
            return text


tr = translate
if not system.running_unit_test:
    load_language()


def trim_text_with_ellipsis(text, trimmed_len):
    ellipsis_in_context = tr("{}...")
    ellipsis_len = len(ellipsis_in_context)
    if direction == settings.LanguageDirection.LEFT_TO_RIGHT:
        return ellipsis_in_context.format(text[: trimmed_len - ellipsis_len])
    else:
        return ellipsis_in_context.format(text[-trimmed_len + ellipsis_len :])
