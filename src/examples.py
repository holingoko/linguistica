import os

from src import app_info
from src import dict_database
from src import dict_entry_window
from src import dict_template_entry_window
from src import dict_template_window
from src import dict_settings_window
from src import language
from src import settings
from src import state
from src.language import tr


def no_state_change(f):
    def wrapped_function(*args, **kwargs):
        last_selected_dict = state.last_selected_dict
        f(*args, **kwargs)
        state.last_selected_dict = last_selected_dict

    return wrapped_function


def create_new_dict_path_with_non_existing_name(name):
    path = os.path.join(settings.dict_dir, f"{name}{app_info.db_ext}")
    if not os.path.exists(path):
        return path, name
    name_template = f"{name} {{}}"
    i = 1
    while True:
        path = os.path.join(
            settings.dict_dir, f"{name_template.format(i)}{app_info.db_ext}"
        )
        if os.path.exists(path):
            i = i + 1
        else:
            return path, os.path.splitext(os.path.basename(path))[0]


def open_dict_settings_window(name):
    dict_settings_window_ = dict_settings_window.DictSettingsWindow()
    dict_settings_window_.dict_combo_box.set_name(name)
    dict_settings_window_.show()
    return dict_settings_window_


@no_state_change
def open_windows_for_create_entry_example(
    name,
    db,
    entry_id,
):
    open_dict_settings_window(name)
    dict_entry_window_ = dict_entry_window.DictEntryWindow(db, entry_id)
    dict_entry_window_.show()
    dict_entry_window_.on_data_change()


@no_state_change
def open_windows_for_create_templates_example(
    name,
    db,
    entry_id,
    template_name,
    row_data,
):
    open_dict_settings_window(name)
    dict_template_window_ = dict_template_window.DictTemplateWindow(
        db,
        entry_id,
    )
    dict_template_window_.test_list_edit.set_row_data(row_data)
    dict_template_window_.on_data_change()
    dict_template_window_.on_save(close_if_success=False)
    dict_template_window_.show()
    dict_entry_window_ = dict_entry_window.DictEntryWindow(db)
    template_entry_window = dict_template_entry_window.DictTemplateEntryWindow(
        dict_entry_window_.db,
        dict_entry_window_.on_dict_template_entry_window_save,
    )
    template_entry_window.template_combo_box.setCurrentText(template_name)
    template_entry_window.stem_list_edit.set_row_data(row_data)
    template_entry_window.on_save(close_if_success=False)
    dict_entry_window_.on_save(close_if_success=False)
    dict_entry_window_.add_child_window(template_entry_window)
    dict_entry_window_.show()
    dict_entry_window_.on_data_change()
    template_entry_window.show()
    dict_template_window_.raise_()
    dict_template_window_.on_data_change()


@no_state_change
def open_windows_for_set_format_example(
    name,
    db,
    entry_id,
):
    dict_settings_window_ = open_dict_settings_window(name)
    dict_entry_window_ = dict_entry_window.DictEntryWindow(db, entry_id)
    dict_entry_window_.on_save(close_if_success=False)
    dict_entry_window_.show()
    dict_settings_window_.raise_()


def create_dictionary_english():
    name = tr("English Example")
    path, name = create_new_dict_path_with_non_existing_name(name)
    db = dict_database.DictDatabase(path)
    db.info.set_entry_format(
        f"<b>{{{tr("English")}}}</b><br>"
        f'{{{tr("Part Of Speech")}}}<br>'
        "{"
        + tr("{0} of <b>{1}</b>:").format(
            f"{{{tr("Inflection")}}}", f"{{{tr("Base Form")}}}"
        )
        + "}"
        f"{{{tr("Definitions")}}}"
    )
    db.info.set_entry_joiner("<hr>")
    db.tags.create_tag(tr("English"), True, "{{},... {}}", 0)
    db.tags.create_tag(tr("Part Of Speech"), False, "{{},... {}}", 1)
    db.tags.create_tag(tr("Inflection"), False, "{{},... {}}", 2)
    db.tags.create_tag(tr("Base Form"), False, "{{},... {}}", 3)
    db.tags.create_tag(
        tr("Definitions"),
        False,
        "{<ol><li>{}</li>...<li>{}</li></ol>}",
        4,
    )
    return name, db


def create_dictionary_mandarin_chinese():
    name = tr("Mandarin Chinese Example")
    path, name = create_new_dict_path_with_non_existing_name(name)
    db = dict_database.DictDatabase(path)
    db.info.set_entry_format(
        f"{{{tr("Traditional")}}}<br>"
        f"{{{tr("Simplified")}}}<br>"
        f"{{{tr("Pinyin")}}}<br>"
        f"{{{tr("Zhuyin")}}}<br>"
        f"{{{tr("Part Of Speech")}}}"
        f"{{{tr("Definitions")}}}"
    )
    db.info.set_entry_joiner("<hr>")
    db.tags.create_tag(tr("Traditional"), True, "{{},... {}}", 0)
    db.tags.create_tag(tr("Simplified"), True, "{{},... {}}", 1)
    db.tags.create_tag(tr("Pinyin"), True, "{{},... {}}", 2)
    db.tags.create_tag(tr("Zhuyin"), True, "{{},... {}}", 3)
    db.tags.create_tag(tr("Part Of Speech"), False, "{{},... {}}", 4)
    db.tags.create_tag(
        tr("Definitions"),
        False,
        "{<ol><li>{}</li>...<li>{}</li></ol>}",
        5,
    )
    return name, db


def create_dictionary_hindi():
    name = tr("Hindi Example")
    path, name = create_new_dict_path_with_non_existing_name(name)
    db = dict_database.DictDatabase(path)
    db.info.set_entry_format(
        f"<b>{{{tr("Hindi")}}}</b>"
        f"<p>{{{tr("Urdu")}}}</p>"
        f"{{{tr("Part Of Speech")}}}"
        "{"
        + tr("{0} of <b>{1}</b> /[{2}/]:").format(
            f"{{{tr("Inflection")}}}",
            f"{{{tr("Base Form Hindi")}}}",
            f"{{{tr("Base Form Urdu With Diacritics")}}}",
        )
        + "}"
        f"{{{tr("Definitions")}}}"
    )
    db.info.set_entry_joiner("<hr>")
    db.tags.create_tag(tr("Hindi"), True, "{{},... {}}", 0)
    db.tags.create_tag(tr("Urdu"), True, "{{},... {}}", 1)
    db.tags.create_tag(tr("Part Of Speech"), False, "{{},... {}}", 2)
    db.tags.create_tag(
        tr("Inflection"), False, "{<ul><li>{}</li>...<li>{}</li></ul>}", 3
    )
    db.tags.create_tag(tr("Base Form Hindi"), False, "{{},... {}}", 4)
    db.tags.create_tag(
        tr("Base Form Urdu With Diacritics"), True, "{{},... {}}", 5
    )
    db.tags.create_tag(
        tr("Definitions"),
        False,
        "{<ol><li>{}</li>...<li>{}</li></ol>}",
        6,
    )
    return name, db


def create_dictionary_spanish():
    name = tr("Spanish Example")
    path, name = create_new_dict_path_with_non_existing_name(name)
    db = dict_database.DictDatabase(path)
    db.info.set_entry_format(
        f"<b>{{{tr("Spanish")}}}</b><br>"
        f'{{{tr("Part Of Speech")}}}<br>'
        "{"
        + tr("{0} of <b>{1}</b>:").format(
            f"{{{tr("Inflection")}}}", f"{{{tr("Base Form")}}}"
        )
        + "}"
        f"{{{tr("Definitions")}}}"
    )
    db.info.set_entry_joiner("<hr>")
    db.tags.create_tag(tr("Spanish"), True, "{{},... {}}", 0)
    db.tags.create_tag(tr("Part Of Speech"), False, "{{},... {}}", 1)
    db.tags.create_tag(tr("Inflection"), False, "{{},... {}}", 2)
    db.tags.create_tag(tr("Base Form"), False, "{{},... {}}", 3)
    db.tags.create_tag(
        tr("Definitions"),
        False,
        "{<ol><li>{}</li>...<li>{}</li></ol>}",
        4,
    )
    return name, db


def create_dictionary_arabic():
    name = tr("Arabic Example")
    path, name = create_new_dict_path_with_non_existing_name(name)
    db = dict_database.DictDatabase(path)
    db.info.set_entry_format(
        f"<p><b>{{{tr("Arabic")}}}</b></p>"
        f"{{{tr("Part Of Speech")}}}"
        f"{{{tr("Definitions")}}}"
    )
    db.info.set_entry_joiner("<hr>")
    db.tags.create_tag(tr("Arabic"), True, "{{},... {}}", 0)
    db.tags.create_tag(tr("Part Of Speech"), True, "{{},... {}}", 1)
    db.tags.create_tag(
        tr("Definitions"),
        False,
        "{<ol><li>{}</li>...<li>{}</li></ol>}",
        2,
    )
    return name, db


def create_dictionary_french():
    name = tr("French Example")
    path, name = create_new_dict_path_with_non_existing_name(name)
    db = dict_database.DictDatabase(path)
    db.info.set_entry_format(
        f"<b>{{{tr("French")}}}</b><br>"
        f'{{{tr("Part Of Speech")}}}<br>'
        "{"
        + tr("{0} of <b>{1}</b>:").format(
            f"{{{tr("Inflection")}}}", f"{{{tr("Base Form")}}}"
        )
        + "}"
        f"{{{tr("Definitions")}}}"
    )
    db.info.set_entry_joiner("<hr>")
    db.tags.create_tag(tr("French"), True, "{{},... {}}", 0)
    db.tags.create_tag(tr("Part Of Speech"), False, "{{},... {}}", 1)
    db.tags.create_tag(tr("Inflection"), False, "{{},... {}}", 2)
    db.tags.create_tag(tr("Base Form"), False, "{{},... {}}", 3)
    db.tags.create_tag(
        tr("Definitions"),
        False,
        "{<ol><li>{}</li>...<li>{}</li></ol>}",
        4,
    )
    return name, db


def create_dictionary_bangla():
    name = tr("Bangla Example")
    path, name = create_new_dict_path_with_non_existing_name(name)
    db = dict_database.DictDatabase(path)
    db.info.set_entry_format(
        f"<b>{{{tr("Bangla")}}}</b><br>"
        f"{{{tr("Part Of Speech")}}}"
        f"{{{tr("Definitions")}}}"
    )
    db.info.set_entry_joiner("<hr>")
    db.tags.create_tag(tr("Bangla"), True, "{{},... {}}", 0)
    db.tags.create_tag(tr("Part Of Speech"), False, "{{},... {}}", 1)
    db.tags.create_tag(
        tr("Definitions"),
        False,
        "{<ol><li>{}</li>...<li>{}</li></ol>}",
        2,
    )
    return name, db


def create_dictionary_portuguese():
    name = tr("Portuguese Example")
    path, name = create_new_dict_path_with_non_existing_name(name)
    db = dict_database.DictDatabase(path)
    db.info.set_entry_format(
        f"<b>{{{tr("Portuguese")}}}</b><br>"
        f'{{{tr("Part Of Speech")}}}<br>'
        "{"
        + tr("{0} of <b>{1}</b>:").format(
            f"{{{tr("Inflection")}}}", f"{{{tr("Base Form")}}}"
        )
        + "}"
        f"{{{tr("Definitions")}}}"
    )
    db.info.set_entry_joiner("<hr>")
    db.tags.create_tag(tr("Portuguese"), True, "{{},... {}}", 0)
    db.tags.create_tag(tr("Part Of Speech"), False, "{{},... {}}", 1)
    db.tags.create_tag(tr("Inflection"), False, "{{},... {}}", 2)
    db.tags.create_tag(tr("Base Form"), False, "{{},... {}}", 3)
    db.tags.create_tag(
        tr("Definitions"),
        False,
        "{<ol><li>{}</li>...<li>{}</li></ol>}",
        4,
    )
    return name, db


def create_dictionary_russian():
    name = tr("Russian Example")
    path, name = create_new_dict_path_with_non_existing_name(name)
    db = dict_database.DictDatabase(path)
    db.info.set_entry_format(
        f"<b>{{{tr("Russian With Stress Marks")}}}</b><br>"
        f'{{{tr("Part Of Speech")}}}'
        "{"
        + tr("{0} of <b>{1}</b>:").format(
            f"{{{tr("Inflection")}}}",
            f"{{{tr("Base Form With Stress Marks")}}}",
        )
        + "}"
        f"{{{tr("Definitions")}}}"
    )
    db.info.set_entry_joiner("<hr>")
    db.tags.create_tag(tr("Russian"), True, "{{},... {}}", 0)
    db.tags.create_tag(tr("Russian With Stress Marks"), True, "{{},... {}}", 1)
    db.tags.create_tag(tr("Part Of Speech"), False, "{{},... {}}", 2)
    db.tags.create_tag(
        tr("Inflection"), False, "{<ul><li>{}</li>...<li>{}</li></ul>}", 3
    )
    db.tags.create_tag(
        tr("Base Form With Stress Marks"), False, "{{},... {}}", 4
    )
    db.tags.create_tag(
        tr("Definitions"),
        False,
        "{<ol><li>{}</li>...<li>{}</li></ol>}",
        5,
    )
    return name, db


def create_dictionary_indonesian():
    name = tr("Indonesian Example")
    path, name = create_new_dict_path_with_non_existing_name(name)
    db = dict_database.DictDatabase(path)
    db.info.set_entry_format(
        f"<b>{{{tr("Indonesian")}}}</b><br>"
        f"{{{tr("Part Of Speech")}}}"
        f"{{{tr("Definitions")}}}"
    )
    db.info.set_entry_joiner("<hr>")
    db.tags.create_tag(tr("Indonesian"), True, "{{},... {}}", 0)
    db.tags.create_tag(tr("Part Of Speech"), False, "{{},... {}}", 1)
    db.tags.create_tag(
        tr("Definitions"),
        False,
        "{<ol><li>{}</li>...<li>{}</li></ol>}",
        2,
    )
    return name, db


def create_dictionary_urdu():
    name = tr("Urdu Example")
    path, name = create_new_dict_path_with_non_existing_name(name)
    db = dict_database.DictDatabase(path)
    db.info.set_entry_format(
        f"<p><b>{{{tr("Urdu")}}}</b></p>"
        f"{{{tr("Hindi")}}}<br>"
        f"{{{tr("Part Of Speech")}}}"
        f"{{{tr("Definitions")}}}"
    )
    db.info.set_entry_joiner("<hr>")
    db.tags.create_tag(tr("Urdu"), True, "{{},... {}}", 0)
    db.tags.create_tag(tr("Hindi"), True, "{{},... {}}", 1)
    db.tags.create_tag(tr("Part Of Speech"), True, "{{},... {}}", 2)
    db.tags.create_tag(
        tr("Definitions"),
        False,
        "{<ol><li>{}</li>...<li>{}</li></ol>}",
        3,
    )
    return name, db


def create_dictionary_german():
    name = tr("German Example")
    path, name = create_new_dict_path_with_non_existing_name(name)
    db = dict_database.DictDatabase(path)
    db.info.set_entry_format(
        f"<b>{{{tr("German")}}}</b><br>"
        f'{{{tr("Part Of Speech")}}}'
        "{"
        + tr("{0} of <b>{1}</b>:").format(
            f"{{{tr("Inflection")}}}", f"{{{tr("Base Form")}}}"
        )
        + "}"
        f"{{{tr("Definitions")}}}"
    )
    db.info.set_entry_joiner("<hr>")
    db.tags.create_tag(tr("German"), True, "{{},... {}}", 0)
    db.tags.create_tag(tr("Part Of Speech"), False, "{{},... {}}", 1)
    db.tags.create_tag(
        tr("Inflection"), False, "{<ul><li>{}</li>...<li>{}</li></ul>}", 2
    )
    db.tags.create_tag(tr("Base Form"), False, "{{},... {}}", 3)
    db.tags.create_tag(
        tr("Definitions"),
        False,
        "{<ol><li>{}</li>...<li>{}</li></ol>}",
        4,
    )
    return name, db


def create_dictionary_japanese():
    name = tr("Japanese Example")
    path, name = create_new_dict_path_with_non_existing_name(name)
    db = dict_database.DictDatabase(path)
    db.info.set_entry_format(
        "{"
        + f"{{{tr("Kanji")}}}<br>"
        + "}{"
        + f"{{{tr("Hiragana")}}}<br>"
        + "}{"
        f"{{{tr("Katakana")}}}<br>"
        + "}"
        + f"{{{tr("Part Of Speech")}}}"
        + f"{{{tr("Definitions")}}}"
    )
    db.info.set_entry_joiner("<hr>")
    db.tags.create_tag(tr("Kanji"), True, "{{},... {}}", 0)
    db.tags.create_tag(tr("Hiragana"), True, "{{},... {}}", 1)
    db.tags.create_tag(tr("Katakana"), True, "{{},... {}}", 2)
    db.tags.create_tag(tr("Part Of Speech"), False, "{{},... {}}", 3)
    db.tags.create_tag(
        tr("Definitions"),
        False,
        "{<ol><li>{}</li>...<li>{}</li></ol>}",
        4,
    )
    return name, db


def create_dictionary_latin():
    name = tr("Latin Example")
    path, name = create_new_dict_path_with_non_existing_name(name)
    db = dict_database.DictDatabase(path)
    db.info.set_entry_format(
        f"<b>{{{tr("Latin With Long Vowel Marks")}}}</b><br>"
        f"{{{tr("Part Of Speech")}}}"
        "{"
        + tr("{0} of <b>{1}</b>:").format(
            f"{{{tr("Inflection")}}}",
            f"{{{tr("Base Form With Long Vowel Marks")}}}",
        )
        + "}"
        f"{{{tr("Definitions")}}}"
    )
    db.info.set_entry_joiner("<hr>")
    db.tags.create_tag(tr("Latin"), True, "{{},... {}}", 0)
    db.tags.create_tag(
        tr("Latin With Long Vowel Marks"), True, "{{},... {}}", 1
    )
    db.tags.create_tag(tr("Part Of Speech"), False, "{{},... {}}", 2)
    db.tags.create_tag(
        tr("Inflection"), False, "{<ul><li>{}</li>...<li>{}</li></ul>}", 3
    )
    db.tags.create_tag(
        tr("Base Form With Long Vowel Marks"), False, "{{},... {}}", 4
    )
    db.tags.create_tag(
        tr("Definitions"),
        False,
        "{<ol><li>{}</li>...<li>{}</li></ol>}",
        5,
    )
    return name, db


def create_entry_english():
    name, db = create_dictionary_english()
    entry_id = db.entries.create_entry()
    form_id = db.forms.create_form(entry_id, 0)
    tag_values_list = [
        (
            form_id,
            db.tags.get_tag_id(tr("English")),
            ["example"],
            True,
            False,
        ),
        (
            form_id,
            db.tags.get_tag_id(tr("Part Of Speech")),
            [tr("noun")],
            False,
            False,
        ),
        (
            form_id,
            db.tags.get_tag_id(tr("Inflection")),
            [tr("singular")],
            False,
            False,
        ),
        (
            form_id,
            db.tags.get_tag_id(tr("Base Form")),
            ["example"],
            False,
            False,
        ),
        (
            form_id,
            db.tags.get_tag_id(tr("Definitions")),
            ["example"],
            False,
            False,
        ),
    ]
    for tag_values in tag_values_list:
        db.tag_rows.set_tag_values(*tag_values)
    open_windows_for_create_entry_example(name, db, entry_id)


def create_entry_mandarin_chinese():
    name, db = create_dictionary_mandarin_chinese()
    entry_id = db.entries.create_entry()
    form_id = db.forms.create_form(entry_id, 0)
    tag_values_list = [
        (
            form_id,
            db.tags.get_tag_id(tr("Traditional")),
            ["例子"],
            True,
            False,
        ),
        (
            form_id,
            db.tags.get_tag_id(tr("Simplified")),
            ["例子"],
            True,
            False,
        ),
        (
            form_id,
            db.tags.get_tag_id(tr("Pinyin")),
            ["lìzi"],
            True,
            False,
        ),
        (
            form_id,
            db.tags.get_tag_id(tr("Zhuyin")),
            ["ㄌㄧˋㄗ˙"],
            True,
            False,
        ),
        (
            form_id,
            db.tags.get_tag_id(tr("Part Of Speech")),
            [tr("noun")],
            False,
            False,
        ),
        (
            form_id,
            db.tags.get_tag_id(tr("Definitions")),
            ["example"],
            False,
            False,
        ),
    ]
    for tag_values in tag_values_list:
        db.tag_rows.set_tag_values(*tag_values)
    open_windows_for_create_entry_example(name, db, entry_id)


def create_entry_hindi():
    name, db = create_dictionary_hindi()
    entry_id = db.entries.create_entry()
    form_id = db.forms.create_form(entry_id, 0)
    tag_values_list = [
        (
            form_id,
            db.tags.get_tag_id(tr("Hindi")),
            ["उदाहरण"],
            True,
            False,
        ),
        (
            form_id,
            db.tags.get_tag_id(tr("Urdu")),
            ["اداہرن"],
            True,
            False,
        ),
        (
            form_id,
            db.tags.get_tag_id(tr("Part Of Speech")),
            [tr("masculine noun")],
            False,
            False,
        ),
        (
            form_id,
            db.tags.get_tag_id(tr("Inflection")),
            [
                tr("direct singular"),
                tr("oblique singular"),
                tr("vocative singular"),
                tr("direct plural"),
            ],
            False,
            False,
        ),
        (
            form_id,
            db.tags.get_tag_id(tr("Base Form Hindi")),
            ["उदाहरण"],
            False,
            False,
        ),
        (
            form_id,
            db.tags.get_tag_id(tr("Base Form Urdu With Diacritics")),
            ["اُداہَرَن"],
            False,
            False,
        ),
        (
            form_id,
            db.tags.get_tag_id(tr("Definitions")),
            ["example"],
            False,
            False,
        ),
    ]
    for tag_values in tag_values_list:
        db.tag_rows.set_tag_values(*tag_values)
    open_windows_for_create_entry_example(name, db, entry_id)


def create_entry_spanish():
    name, db = create_dictionary_spanish()
    entry_id = db.entries.create_entry()
    form_id = db.forms.create_form(entry_id, 0)
    tag_values_list = [
        (
            form_id,
            db.tags.get_tag_id(tr("Spanish")),
            ["ejemplo"],
            True,
            False,
        ),
        (
            form_id,
            db.tags.get_tag_id(tr("Part Of Speech")),
            [tr("masculine noun")],
            False,
            False,
        ),
        (
            form_id,
            db.tags.get_tag_id(tr("Inflection")),
            [tr("singular")],
            False,
            False,
        ),
        (
            form_id,
            db.tags.get_tag_id(tr("Base Form")),
            ["ejemplo"],
            False,
            False,
        ),
        (
            form_id,
            db.tags.get_tag_id(tr("Definitions")),
            ["example"],
            False,
            False,
        ),
    ]
    for tag_values in tag_values_list:
        db.tag_rows.set_tag_values(*tag_values)
    open_windows_for_create_entry_example(name, db, entry_id)


def create_entry_arabic():
    name, db = create_dictionary_arabic()
    entry_id = db.entries.create_entry()
    form_id = db.forms.create_form(entry_id, 0)
    tag_values_list = [
        (
            form_id,
            db.tags.get_tag_id(tr("Arabic")),
            ["مثال"],
            True,
            False,
        ),
        (
            form_id,
            db.tags.get_tag_id(tr("Part Of Speech")),
            [tr("masculine noun")],
            False,
            False,
        ),
        (
            form_id,
            db.tags.get_tag_id(tr("Definitions")),
            ["example"],
            False,
            False,
        ),
    ]
    for tag_values in tag_values_list:
        db.tag_rows.set_tag_values(*tag_values)
    open_windows_for_create_entry_example(name, db, entry_id)


def create_entry_french():
    name, db = create_dictionary_french()
    entry_id = db.entries.create_entry()
    form_id = db.forms.create_form(entry_id, 0)
    tag_values_list = [
        (
            form_id,
            db.tags.get_tag_id(tr("French")),
            ["exemple"],
            True,
            False,
        ),
        (
            form_id,
            db.tags.get_tag_id(tr("Part Of Speech")),
            [tr("masculine noun")],
            False,
            False,
        ),
        (
            form_id,
            db.tags.get_tag_id(tr("Inflection")),
            [tr("singular")],
            False,
            False,
        ),
        (
            form_id,
            db.tags.get_tag_id(tr("Base Form")),
            ["exemple"],
            False,
            False,
        ),
        (
            form_id,
            db.tags.get_tag_id(tr("Definitions")),
            ["example"],
            False,
            False,
        ),
    ]
    for tag_values in tag_values_list:
        db.tag_rows.set_tag_values(*tag_values)
    open_windows_for_create_entry_example(name, db, entry_id)


def create_entry_bangla():
    name, db = create_dictionary_bangla()
    entry_id = db.entries.create_entry()
    form_id = db.forms.create_form(entry_id, 0)
    tag_values_list = [
        (
            form_id,
            db.tags.get_tag_id(tr("Bangla")),
            ["উদাহরণ"],
            True,
            False,
        ),
        (
            form_id,
            db.tags.get_tag_id(tr("Part Of Speech")),
            [tr("masculine noun")],
            False,
            False,
        ),
        (
            form_id,
            db.tags.get_tag_id(tr("Definitions")),
            ["example"],
            False,
            False,
        ),
    ]
    for tag_values in tag_values_list:
        db.tag_rows.set_tag_values(*tag_values)
    open_windows_for_create_entry_example(name, db, entry_id)


def create_entry_portuguese():
    name, db = create_dictionary_portuguese()
    entry_id = db.entries.create_entry()
    form_id = db.forms.create_form(entry_id, 0)
    tag_values_list = [
        (
            form_id,
            db.tags.get_tag_id(tr("Portuguese")),
            ["exemplo"],
            True,
            False,
        ),
        (
            form_id,
            db.tags.get_tag_id(tr("Part Of Speech")),
            [tr("masculine noun")],
            False,
            False,
        ),
        (
            form_id,
            db.tags.get_tag_id(tr("Inflection")),
            [tr("singular")],
            False,
            False,
        ),
        (
            form_id,
            db.tags.get_tag_id(tr("Base Form")),
            ["exemplo"],
            False,
            False,
        ),
        (
            form_id,
            db.tags.get_tag_id(tr("Definitions")),
            ["example"],
            False,
            False,
        ),
    ]
    for tag_values in tag_values_list:
        db.tag_rows.set_tag_values(*tag_values)
    open_windows_for_create_entry_example(name, db, entry_id)


def create_entry_russian():
    name, db = create_dictionary_russian()
    entry_id = db.entries.create_entry()
    form_id = db.forms.create_form(entry_id, 0)
    tag_values_list = [
        (
            form_id,
            db.tags.get_tag_id(tr("Russian")),
            ["пример"],
            True,
            False,
        ),
        (
            form_id,
            db.tags.get_tag_id(tr("Russian With Stress Marks")),
            ["приме́р"],
            True,
            False,
        ),
        (
            form_id,
            db.tags.get_tag_id(tr("Part Of Speech")),
            [tr("masculine noun")],
            False,
            False,
        ),
        (
            form_id,
            db.tags.get_tag_id(tr("Inflection")),
            [
                tr("nominative singular"),
                tr("accusative singular"),
            ],
            False,
            False,
        ),
        (
            form_id,
            db.tags.get_tag_id(tr("Base Form With Stress Marks")),
            ["приме́р"],
            False,
            False,
        ),
        (
            form_id,
            db.tags.get_tag_id(tr("Definitions")),
            ["example"],
            False,
            False,
        ),
    ]
    for tag_values in tag_values_list:
        db.tag_rows.set_tag_values(*tag_values)
    open_windows_for_create_entry_example(name, db, entry_id)


def create_entry_indonesian():
    name, db = create_dictionary_indonesian()
    entry_id = db.entries.create_entry()
    form_id = db.forms.create_form(entry_id, 0)
    tag_values_list = [
        (
            form_id,
            db.tags.get_tag_id(tr("Indonesian")),
            ["contoh"],
            True,
            False,
        ),
        (
            form_id,
            db.tags.get_tag_id(tr("Part Of Speech")),
            [tr("noun")],
            False,
            False,
        ),
        (
            form_id,
            db.tags.get_tag_id(tr("Definitions")),
            ["example"],
            False,
            False,
        ),
    ]
    for tag_values in tag_values_list:
        db.tag_rows.set_tag_values(*tag_values)
    open_windows_for_create_entry_example(name, db, entry_id)


def create_entry_urdu():
    name, db = create_dictionary_urdu()
    entry_id = db.entries.create_entry()
    form_id = db.forms.create_form(entry_id, 0)
    tag_values_list = [
        (
            form_id,
            db.tags.get_tag_id(tr("Urdu")),
            ["مثال"],
            True,
            False,
        ),
        (
            form_id,
            db.tags.get_tag_id(tr("Hindi")),
            ["मिसाल"],
            True,
            False,
        ),
        (
            form_id,
            db.tags.get_tag_id(tr("Part Of Speech")),
            [tr("masculine noun")],
            False,
            False,
        ),
        (
            form_id,
            db.tags.get_tag_id(tr("Definitions")),
            ["example"],
            False,
            False,
        ),
    ]
    for tag_values in tag_values_list:
        db.tag_rows.set_tag_values(*tag_values)
    open_windows_for_create_entry_example(name, db, entry_id)


def create_entry_german():
    name, db = create_dictionary_german()
    entry_id = db.entries.create_entry()
    form_id = db.forms.create_form(entry_id, 0)
    tag_values_list = [
        (
            form_id,
            db.tags.get_tag_id(tr("German")),
            ["Beispiel"],
            True,
            False,
        ),
        (
            form_id,
            db.tags.get_tag_id(tr("Part Of Speech")),
            [tr("neuter noun")],
            False,
            False,
        ),
        (
            form_id,
            db.tags.get_tag_id(tr("Inflection")),
            [
                tr("nominative singular"),
                tr("dative singular"),
                tr("accusative singular"),
            ],
            False,
            False,
        ),
        (
            form_id,
            db.tags.get_tag_id(tr("Base Form")),
            ["Beispiel"],
            False,
            False,
        ),
        (
            form_id,
            db.tags.get_tag_id(tr("Definitions")),
            ["example"],
            False,
            False,
        ),
    ]
    for tag_values in tag_values_list:
        db.tag_rows.set_tag_values(*tag_values)
    open_windows_for_create_entry_example(name, db, entry_id)


def create_entry_japanese():
    name, db = create_dictionary_japanese()
    entry_id = db.entries.create_entry()
    form_id = db.forms.create_form(entry_id, 0)
    tag_values_list = [
        (
            form_id,
            db.tags.get_tag_id(tr("Kanji")),
            ["例"],
            True,
            False,
        ),
        (
            form_id,
            db.tags.get_tag_id(tr("Hiragana")),
            ["れい"],
            True,
            False,
        ),
        (
            form_id,
            db.tags.get_tag_id(tr("Katakana")),
            [""],
            True,
            False,
        ),
        (
            form_id,
            db.tags.get_tag_id(tr("Part Of Speech")),
            [tr("noun")],
            False,
            False,
        ),
        (
            form_id,
            db.tags.get_tag_id(tr("Definitions")),
            ["example"],
            False,
            False,
        ),
    ]
    for tag_values in tag_values_list:
        db.tag_rows.set_tag_values(*tag_values)
    open_windows_for_create_entry_example(name, db, entry_id)


def create_entry_latin():
    name, db = create_dictionary_latin()
    entry_id = db.entries.create_entry()
    form_id = db.forms.create_form(entry_id, 0)
    tag_values_list = [
        (
            form_id,
            db.tags.get_tag_id(tr("Latin")),
            ["exemplum"],
            True,
            False,
        ),
        (
            form_id,
            db.tags.get_tag_id(tr("Latin With Long Vowel Marks")),
            ["exemplum"],
            True,
            False,
        ),
        (
            form_id,
            db.tags.get_tag_id(tr("Part Of Speech")),
            [tr("neuter noun")],
            False,
            False,
        ),
        (
            form_id,
            db.tags.get_tag_id(tr("Inflection")),
            [
                tr("nominative singular"),
                tr("accusative singular"),
                tr("vocative singular"),
            ],
            False,
            False,
        ),
        (
            form_id,
            db.tags.get_tag_id(tr("Base Form With Long Vowel Marks")),
            ["exemplum"],
            False,
            False,
        ),
        (
            form_id,
            db.tags.get_tag_id(tr("Definitions")),
            ["example"],
            False,
            False,
        ),
    ]
    for tag_values in tag_values_list:
        db.tag_rows.set_tag_values(*tag_values)
    open_windows_for_create_entry_example(name, db, entry_id)


def create_template_english():
    name, db = create_dictionary_english()
    entry_id = db.entries.create_entry()
    template_name = tr("Create Template Example")
    db.entries.set_template_name(entry_id, template_name)
    form_ids = [db.forms.create_form(entry_id, i) for i in range(2)]
    tag_values_list = [
        (
            form_ids[0],
            db.tags.get_tag_id(tr("English")),
            ["{}"],
            True,
            False,
        ),
        (
            form_ids[1],
            db.tags.get_tag_id(tr("English")),
            ["{}s"],
            True,
            False,
        ),
        *[
            (
                form_id,
                db.tags.get_tag_id(tr("Part Of Speech")),
                [tr("noun")],
                False,
                False,
            )
            for form_id in form_ids
        ],
        (
            form_ids[0],
            db.tags.get_tag_id(tr("Inflection")),
            [tr("singular")],
            False,
            False,
        ),
        (
            form_ids[1],
            db.tags.get_tag_id(tr("Inflection")),
            [tr("plural")],
            False,
            False,
        ),
        *[
            (
                form_id,
                db.tags.get_tag_id(tr("Base Form")),
                ["{}"],
                False,
                False,
            )
            for form_id in form_ids
        ],
        *[
            (
                form_id,
                db.tags.get_tag_id(tr("Definitions")),
                ["{}"],
                False,
                False,
            )
            for form_id in form_ids
        ],
    ]
    for tag_values in tag_values_list:
        db.tag_rows.set_tag_values(*tag_values)
    row_data = [
        (
            None,
            [
                (
                    db.tags.get_tag_id(tr("English")),
                    tr("English"),
                    ["example"],
                ),
                (
                    db.tags.get_tag_id(tr("Part Of Speech")),
                    tr("Part Of Speech"),
                    [""],
                ),
                (
                    db.tags.get_tag_id(tr("Inflection")),
                    tr("Inflection"),
                    [""],
                ),
                (
                    db.tags.get_tag_id(tr("Base Form")),
                    tr("Base Form"),
                    ["example"],
                ),
                (
                    db.tags.get_tag_id(tr("Definitions")),
                    tr("Definitions"),
                    ["example"],
                ),
            ],
        )
    ]
    open_windows_for_create_templates_example(
        name,
        db,
        entry_id,
        template_name,
        row_data,
    )


def create_template_hindi():
    name, db = create_dictionary_hindi()
    entry_id = db.entries.create_entry()
    template_name = tr("Create Template Example")
    db.entries.set_template_name(entry_id, template_name)
    form_ids = [db.forms.create_form(entry_id, i) for i in range(3)]
    tag_values_list = [
        (
            form_ids[0],
            db.tags.get_tag_id(tr("Hindi")),
            ["{}ण"],
            True,
            False,
        ),
        (
            form_ids[1],
            db.tags.get_tag_id(tr("Hindi")),
            ["{}णों"],
            True,
            False,
        ),
        (
            form_ids[2],
            db.tags.get_tag_id(tr("Hindi")),
            ["{}णो"],
            True,
            False,
        ),
        (
            form_ids[0],
            db.tags.get_tag_id(tr("Urdu")),
            ["{}ن"],
            True,
            False,
        ),
        (
            form_ids[1],
            db.tags.get_tag_id(tr("Urdu")),
            ["{}نوں"],
            True,
            False,
        ),
        (
            form_ids[2],
            db.tags.get_tag_id(tr("Urdu")),
            ["{}نو"],
            True,
            False,
        ),
        *[
            (
                form_id,
                db.tags.get_tag_id(tr("Part Of Speech")),
                [tr("masculine noun")],
                False,
                False,
            )
            for form_id in form_ids
        ],
        (
            form_ids[0],
            db.tags.get_tag_id(tr("Inflection")),
            [
                tr("direct singular"),
                tr("oblique singular"),
                tr("vocative singular"),
                tr("direct plural"),
            ],
            False,
            False,
        ),
        (
            form_ids[1],
            db.tags.get_tag_id(tr("Inflection")),
            [tr("oblique plural")],
            False,
            False,
        ),
        (
            form_ids[2],
            db.tags.get_tag_id(tr("Inflection")),
            [tr("vocative plural")],
            False,
            False,
        ),
        *[
            (
                form_id,
                db.tags.get_tag_id(tr("Base Form Hindi")),
                ["{}"],
                False,
                False,
            )
            for form_id in form_ids
        ],
        *[
            (
                form_id,
                db.tags.get_tag_id(tr("Base Form Urdu With Diacritics")),
                ["{}"],
                False,
                False,
            )
            for form_id in form_ids
        ],
        *[
            (
                form_id,
                db.tags.get_tag_id(tr("Definitions")),
                ["{}"],
                False,
                False,
            )
            for form_id in form_ids
        ],
    ]
    for tag_values in tag_values_list:
        db.tag_rows.set_tag_values(*tag_values)
    row_data = [
        (
            None,
            [
                (
                    db.tags.get_tag_id(tr("Hindi")),
                    tr("Hindi"),
                    ["उदाहर"],
                ),
                (
                    db.tags.get_tag_id(tr("Urdu")),
                    tr("Urdu"),
                    ["اداہر"],
                ),
                (
                    db.tags.get_tag_id(tr("Part Of Speech")),
                    tr("Part Of Speech"),
                    [""],
                ),
                (
                    db.tags.get_tag_id(tr("Inflection")),
                    tr("Inflection"),
                    [""],
                ),
                (
                    db.tags.get_tag_id(tr("Base Form Hindi")),
                    tr("Base Form Hindi"),
                    ["उदाहरण"],
                ),
                (
                    db.tags.get_tag_id(tr("Base Form Urdu With Diacritics")),
                    tr("Base Form Urdu With Diacritics"),
                    ["اُداہَرَن"],
                ),
                (
                    db.tags.get_tag_id(tr("Definitions")),
                    tr("Definitions"),
                    ["example"],
                ),
            ],
        )
    ]
    open_windows_for_create_templates_example(
        name,
        db,
        entry_id,
        template_name,
        row_data,
    )


def create_template_spanish():
    name, db = create_dictionary_spanish()
    entry_id = db.entries.create_entry()
    template_name = tr("Create Template Example")
    db.entries.set_template_name(entry_id, template_name)
    form_ids = [db.forms.create_form(entry_id, i) for i in range(2)]
    tag_values_list = [
        (
            form_ids[0],
            db.tags.get_tag_id(tr("Spanish")),
            ["{}"],
            True,
            False,
        ),
        (
            form_ids[1],
            db.tags.get_tag_id(tr("Spanish")),
            ["{}s"],
            True,
            False,
        ),
        *[
            (
                form_id,
                db.tags.get_tag_id(tr("Part Of Speech")),
                [tr("masculine noun")],
                False,
                False,
            )
            for form_id in form_ids
        ],
        (
            form_ids[0],
            db.tags.get_tag_id(tr("Inflection")),
            [tr("singular")],
            False,
            False,
        ),
        (
            form_ids[1],
            db.tags.get_tag_id(tr("Inflection")),
            [tr("plural")],
            False,
            False,
        ),
        *[
            (
                form_id,
                db.tags.get_tag_id(tr("Base Form")),
                ["{}"],
                False,
                False,
            )
            for form_id in form_ids
        ],
        *[
            (
                form_id,
                db.tags.get_tag_id(tr("Definitions")),
                ["{}"],
                False,
                False,
            )
            for form_id in form_ids
        ],
    ]
    for tag_values in tag_values_list:
        db.tag_rows.set_tag_values(*tag_values)
    row_data = [
        (
            None,
            [
                (
                    db.tags.get_tag_id(tr("Spanish")),
                    tr("Spanish"),
                    ["ejemplo"],
                ),
                (
                    db.tags.get_tag_id(tr("Part Of Speech")),
                    tr("Part Of Speech"),
                    [""],
                ),
                (
                    db.tags.get_tag_id(tr("Inflection")),
                    tr("Inflection"),
                    [""],
                ),
                (
                    db.tags.get_tag_id(tr("Base Form")),
                    tr("Base Form"),
                    ["ejemplo"],
                ),
                (
                    db.tags.get_tag_id(tr("Definitions")),
                    tr("Definitions"),
                    ["example"],
                ),
            ],
        )
    ]
    open_windows_for_create_templates_example(
        name,
        db,
        entry_id,
        template_name,
        row_data,
    )


def create_template_french():
    name, db = create_dictionary_french()
    entry_id = db.entries.create_entry()
    template_name = tr("Create Template Example")
    db.entries.set_template_name(entry_id, template_name)
    form_ids = [db.forms.create_form(entry_id, i) for i in range(2)]
    tag_values_list = [
        (
            form_ids[0],
            db.tags.get_tag_id(tr("French")),
            ["{}"],
            True,
            False,
        ),
        (
            form_ids[1],
            db.tags.get_tag_id(tr("French")),
            ["{}s"],
            True,
            False,
        ),
        *[
            (
                form_id,
                db.tags.get_tag_id(tr("Part Of Speech")),
                [tr("masculine noun")],
                False,
                False,
            )
            for form_id in form_ids
        ],
        (
            form_ids[0],
            db.tags.get_tag_id(tr("Inflection")),
            [tr("singular")],
            False,
            False,
        ),
        (
            form_ids[1],
            db.tags.get_tag_id(tr("Inflection")),
            [tr("plural")],
            False,
            False,
        ),
        *[
            (
                form_id,
                db.tags.get_tag_id(tr("Base Form")),
                ["{}"],
                False,
                False,
            )
            for form_id in form_ids
        ],
        *[
            (
                form_id,
                db.tags.get_tag_id(tr("Definitions")),
                ["{}"],
                False,
                False,
            )
            for form_id in form_ids
        ],
    ]
    for tag_values in tag_values_list:
        db.tag_rows.set_tag_values(*tag_values)
    row_data = [
        (
            None,
            [
                (
                    db.tags.get_tag_id(tr("French")),
                    tr("French"),
                    ["exemple"],
                ),
                (
                    db.tags.get_tag_id(tr("Part Of Speech")),
                    tr("Part Of Speech"),
                    [""],
                ),
                (
                    db.tags.get_tag_id(tr("Inflection")),
                    tr("Inflection"),
                    [""],
                ),
                (
                    db.tags.get_tag_id(tr("Base Form")),
                    tr("Base Form"),
                    ["exemple"],
                ),
                (
                    db.tags.get_tag_id(tr("Definitions")),
                    tr("Definitions"),
                    ["example"],
                ),
            ],
        )
    ]
    open_windows_for_create_templates_example(
        name,
        db,
        entry_id,
        template_name,
        row_data,
    )


def create_template_portuguese():
    name, db = create_dictionary_portuguese()
    entry_id = db.entries.create_entry()
    template_name = tr("Create Template Example")
    db.entries.set_template_name(entry_id, template_name)
    form_ids = [db.forms.create_form(entry_id, i) for i in range(2)]
    tag_values_list = [
        (
            form_ids[0],
            db.tags.get_tag_id(tr("Portuguese")),
            ["{}"],
            True,
            False,
        ),
        (
            form_ids[1],
            db.tags.get_tag_id(tr("Portuguese")),
            ["{}s"],
            True,
            False,
        ),
        *[
            (
                form_id,
                db.tags.get_tag_id(tr("Part Of Speech")),
                [tr("masculine noun")],
                False,
                False,
            )
            for form_id in form_ids
        ],
        (
            form_ids[0],
            db.tags.get_tag_id(tr("Inflection")),
            [tr("singular")],
            False,
            False,
        ),
        (
            form_ids[1],
            db.tags.get_tag_id(tr("Inflection")),
            [tr("plural")],
            False,
            False,
        ),
        *[
            (
                form_id,
                db.tags.get_tag_id(tr("Base Form")),
                ["{}"],
                False,
                False,
            )
            for form_id in form_ids
        ],
        *[
            (
                form_id,
                db.tags.get_tag_id(tr("Definitions")),
                ["{}"],
                False,
                False,
            )
            for form_id in form_ids
        ],
    ]
    for tag_values in tag_values_list:
        db.tag_rows.set_tag_values(*tag_values)
    row_data = [
        (
            None,
            [
                (
                    db.tags.get_tag_id(tr("Portuguese")),
                    tr("Portuguese"),
                    ["exemplo"],
                ),
                (
                    db.tags.get_tag_id(tr("Part Of Speech")),
                    tr("Part Of Speech"),
                    [""],
                ),
                (
                    db.tags.get_tag_id(tr("Inflection")),
                    tr("Inflection"),
                    [""],
                ),
                (
                    db.tags.get_tag_id(tr("Base Form")),
                    tr("Base Form"),
                    ["exemplo"],
                ),
                (
                    db.tags.get_tag_id(tr("Definitions")),
                    tr("Definitions"),
                    ["example"],
                ),
            ],
        )
    ]
    open_windows_for_create_templates_example(
        name,
        db,
        entry_id,
        template_name,
        row_data,
    )


def create_template_russian():
    name, db = create_dictionary_russian()
    entry_id = db.entries.create_entry()
    template_name = tr("Create Template Example")
    db.entries.set_template_name(entry_id, template_name)
    form_ids = [db.forms.create_form(entry_id, i) for i in range(10)]
    tag_values_list = [
        (
            form_ids[0],
            db.tags.get_tag_id(tr("Russian")),
            ["{}"],
            True,
            False,
        ),
        (
            form_ids[1],
            db.tags.get_tag_id(tr("Russian")),
            ["{}а"],
            True,
            False,
        ),
        (
            form_ids[2],
            db.tags.get_tag_id(tr("Russian")),
            ["{}у"],
            True,
            False,
        ),
        (
            form_ids[3],
            db.tags.get_tag_id(tr("Russian")),
            ["{}ом"],
            True,
            False,
        ),
        (
            form_ids[4],
            db.tags.get_tag_id(tr("Russian")),
            ["{}е"],
            True,
            False,
        ),
        (
            form_ids[5],
            db.tags.get_tag_id(tr("Russian")),
            ["{}ы"],
            True,
            False,
        ),
        (
            form_ids[6],
            db.tags.get_tag_id(tr("Russian")),
            ["{}ов"],
            True,
            False,
        ),
        (
            form_ids[7],
            db.tags.get_tag_id(tr("Russian")),
            ["{}ам"],
            True,
            False,
        ),
        (
            form_ids[8],
            db.tags.get_tag_id(tr("Russian")),
            ["{}ами"],
            True,
            False,
        ),
        (
            form_ids[9],
            db.tags.get_tag_id(tr("Russian")),
            ["{}ах"],
            True,
            False,
        ),
        (
            form_ids[0],
            db.tags.get_tag_id(tr("Russian With Stress Marks")),
            ["{}"],
            True,
            False,
        ),
        (
            form_ids[1],
            db.tags.get_tag_id(tr("Russian With Stress Marks")),
            ["{}а"],
            True,
            False,
        ),
        (
            form_ids[2],
            db.tags.get_tag_id(tr("Russian With Stress Marks")),
            ["{}у"],
            True,
            False,
        ),
        (
            form_ids[3],
            db.tags.get_tag_id(tr("Russian With Stress Marks")),
            ["{}ом"],
            True,
            False,
        ),
        (
            form_ids[4],
            db.tags.get_tag_id(tr("Russian With Stress Marks")),
            ["{}е"],
            True,
            False,
        ),
        (
            form_ids[5],
            db.tags.get_tag_id(tr("Russian With Stress Marks")),
            ["{}ы"],
            True,
            False,
        ),
        (
            form_ids[6],
            db.tags.get_tag_id(tr("Russian With Stress Marks")),
            ["{}ов"],
            True,
            False,
        ),
        (
            form_ids[7],
            db.tags.get_tag_id(tr("Russian With Stress Marks")),
            ["{}ам"],
            True,
            False,
        ),
        (
            form_ids[8],
            db.tags.get_tag_id(tr("Russian With Stress Marks")),
            ["{}ами"],
            True,
            False,
        ),
        (
            form_ids[9],
            db.tags.get_tag_id(tr("Russian With Stress Marks")),
            ["{}ах"],
            True,
            False,
        ),
        *[
            (
                form_id,
                db.tags.get_tag_id(tr("Part Of Speech")),
                [tr("masculine noun")],
                False,
                False,
            )
            for form_id in form_ids
        ],
        (
            form_ids[0],
            db.tags.get_tag_id(tr("Inflection")),
            [
                tr("nominative singular"),
                tr("accusative singular"),
            ],
            False,
            False,
        ),
        (
            form_ids[1],
            db.tags.get_tag_id(tr("Inflection")),
            [tr("genitive singular")],
            False,
            False,
        ),
        (
            form_ids[2],
            db.tags.get_tag_id(tr("Inflection")),
            [tr("dative singular")],
            False,
            False,
        ),
        (
            form_ids[3],
            db.tags.get_tag_id(tr("Inflection")),
            [tr("instrumental singular")],
            False,
            False,
        ),
        (
            form_ids[4],
            db.tags.get_tag_id(tr("Inflection")),
            [tr("prepositional singular")],
            False,
            False,
        ),
        (
            form_ids[5],
            db.tags.get_tag_id(tr("Inflection")),
            [
                tr("nominative plural"),
                tr("accusative plural"),
            ],
            False,
            False,
        ),
        (
            form_ids[6],
            db.tags.get_tag_id(tr("Inflection")),
            [tr("genitive plural")],
            False,
            False,
        ),
        (
            form_ids[7],
            db.tags.get_tag_id(tr("Inflection")),
            [tr("dative plural")],
            False,
            False,
        ),
        (
            form_ids[8],
            db.tags.get_tag_id(tr("Inflection")),
            [tr("instrumental plural")],
            False,
            False,
        ),
        (
            form_ids[9],
            db.tags.get_tag_id(tr("Inflection")),
            [tr("prepositional plural")],
            False,
            False,
        ),
        *[
            (
                form_id,
                db.tags.get_tag_id(tr("Base Form With Stress Marks")),
                ["{}"],
                False,
                False,
            )
            for form_id in form_ids
        ],
        *[
            (
                form_id,
                db.tags.get_tag_id(tr("Definitions")),
                ["{}"],
                False,
                False,
            )
            for form_id in form_ids
        ],
    ]
    for tag_values in tag_values_list:
        db.tag_rows.set_tag_values(*tag_values)
    row_data = [
        (
            None,
            [
                (
                    db.tags.get_tag_id(tr("Russian")),
                    tr("Russian"),
                    ["пример"],
                ),
                (
                    db.tags.get_tag_id(tr("Russian With Stress Marks")),
                    tr("Russian With Stress Marks"),
                    ["приме́р"],
                ),
                (
                    db.tags.get_tag_id(tr("Part Of Speech")),
                    tr("Part Of Speech"),
                    [""],
                ),
                (
                    db.tags.get_tag_id(tr("Inflection")),
                    tr("Inflection"),
                    [""],
                ),
                (
                    db.tags.get_tag_id(tr("Base Form With Stress Marks")),
                    tr("Base Form With Stress Marks"),
                    ["приме́р"],
                ),
                (
                    db.tags.get_tag_id(tr("Definitions")),
                    tr("Definitions"),
                    ["example"],
                ),
            ],
        )
    ]
    open_windows_for_create_templates_example(
        name,
        db,
        entry_id,
        template_name,
        row_data,
    )


def create_template_german():
    name, db = create_dictionary_german()
    entry_id = db.entries.create_entry()
    template_name = tr("Create Template Example")
    db.entries.set_template_name(entry_id, template_name)
    form_ids = [db.forms.create_form(entry_id, i) for i in range(5)]
    tag_values_list = [
        (
            form_ids[0],
            db.tags.get_tag_id(tr("German")),
            ["{}"],
            True,
            False,
        ),
        (
            form_ids[1],
            db.tags.get_tag_id(tr("German")),
            ["{}s"],
            True,
            False,
        ),
        (
            form_ids[2],
            db.tags.get_tag_id(tr("German")),
            ["{}es"],
            True,
            False,
        ),
        (
            form_ids[3],
            db.tags.get_tag_id(tr("German")),
            ["{}e"],
            True,
            False,
        ),
        (
            form_ids[4],
            db.tags.get_tag_id(tr("German")),
            ["{}en"],
            True,
            False,
        ),
        *[
            (
                form_id,
                db.tags.get_tag_id(tr("Part Of Speech")),
                [tr("neuter noun")],
                False,
                False,
            )
            for form_id in form_ids
        ],
        (
            form_ids[0],
            db.tags.get_tag_id(tr("Inflection")),
            [
                tr("nominative singular"),
                tr("dative singular"),
                tr("accusative singular"),
            ],
            False,
            False,
        ),
        (
            form_ids[1],
            db.tags.get_tag_id(tr("Inflection")),
            [tr("genitive singular")],
            False,
            False,
        ),
        (
            form_ids[2],
            db.tags.get_tag_id(tr("Inflection")),
            [tr("genitive singular")],
            False,
            False,
        ),
        (
            form_ids[3],
            db.tags.get_tag_id(tr("Inflection")),
            [
                tr("nominative plural"),
                tr("genitive plural"),
                tr("accusative plural"),
                tr("dative singular"),
            ],
            False,
            False,
        ),
        (
            form_ids[4],
            db.tags.get_tag_id(tr("Inflection")),
            [tr("dative plural")],
            False,
            False,
        ),
        *[
            (
                form_id,
                db.tags.get_tag_id(tr("Base Form")),
                ["{}"],
                False,
                False,
            )
            for form_id in form_ids
        ],
        *[
            (
                form_id,
                db.tags.get_tag_id(tr("Definitions")),
                ["{}"],
                False,
                False,
            )
            for form_id in form_ids
        ],
    ]
    for tag_values in tag_values_list:
        db.tag_rows.set_tag_values(*tag_values)
    row_data = [
        (
            None,
            [
                (
                    db.tags.get_tag_id(tr("German")),
                    tr("German"),
                    ["Beispiel"],
                ),
                (
                    db.tags.get_tag_id(tr("Part Of Speech")),
                    tr("Part Of Speech"),
                    [""],
                ),
                (
                    db.tags.get_tag_id(tr("Inflection")),
                    tr("Inflection"),
                    [""],
                ),
                (
                    db.tags.get_tag_id(tr("Base Form")),
                    tr("Base Form"),
                    ["Beispiel"],
                ),
                (
                    db.tags.get_tag_id(tr("Definitions")),
                    tr("Definitions"),
                    ["example"],
                ),
            ],
        )
    ]
    open_windows_for_create_templates_example(
        name,
        db,
        entry_id,
        template_name,
        row_data,
    )


def create_template_latin():
    name, db = create_dictionary_latin()
    entry_id = db.entries.create_entry()
    template_name = tr("Create Template Example")
    db.entries.set_template_name(entry_id, template_name)
    form_ids = [db.forms.create_form(entry_id, i) for i in range(6)]
    tag_values_list = [
        (
            form_ids[0],
            db.tags.get_tag_id(tr("Latin")),
            ["{}um"],
            True,
            False,
        ),
        (
            form_ids[1],
            db.tags.get_tag_id(tr("Latin")),
            ["{}i"],
            True,
            False,
        ),
        (
            form_ids[2],
            db.tags.get_tag_id(tr("Latin")),
            ["{}o"],
            True,
            False,
        ),
        (
            form_ids[3],
            db.tags.get_tag_id(tr("Latin")),
            ["{}a"],
            True,
            False,
        ),
        (
            form_ids[4],
            db.tags.get_tag_id(tr("Latin")),
            ["{}orum"],
            True,
            False,
        ),
        (
            form_ids[5],
            db.tags.get_tag_id(tr("Latin")),
            ["{}is"],
            True,
            False,
        ),
        (
            form_ids[0],
            db.tags.get_tag_id(tr("Latin With Long Vowel Marks")),
            ["{}um"],
            True,
            False,
        ),
        (
            form_ids[1],
            db.tags.get_tag_id(tr("Latin With Long Vowel Marks")),
            ["{}ī"],
            True,
            False,
        ),
        (
            form_ids[2],
            db.tags.get_tag_id(tr("Latin With Long Vowel Marks")),
            ["{}ō"],
            True,
            False,
        ),
        (
            form_ids[3],
            db.tags.get_tag_id(tr("Latin With Long Vowel Marks")),
            ["{}a"],
            True,
            False,
        ),
        (
            form_ids[4],
            db.tags.get_tag_id(tr("Latin With Long Vowel Marks")),
            ["{}ōrum"],
            True,
            False,
        ),
        (
            form_ids[5],
            db.tags.get_tag_id(tr("Latin With Long Vowel Marks")),
            ["{}īs"],
            True,
            False,
        ),
        *[
            (
                form_id,
                db.tags.get_tag_id(tr("Part Of Speech")),
                [tr("neuter noun")],
                False,
                False,
            )
            for form_id in form_ids
        ],
        (
            form_ids[0],
            db.tags.get_tag_id(tr("Inflection")),
            [
                tr("nominative singular"),
                tr("accusative singular"),
                tr("vocative singular"),
            ],
            False,
            False,
        ),
        (
            form_ids[1],
            db.tags.get_tag_id(tr("Inflection")),
            [
                tr("genitive singular"),
            ],
            False,
            False,
        ),
        (
            form_ids[2],
            db.tags.get_tag_id(tr("Inflection")),
            [
                tr("dative singular"),
                tr("ablative singular"),
            ],
            False,
            False,
        ),
        (
            form_ids[3],
            db.tags.get_tag_id(tr("Inflection")),
            [
                tr("nominative plural"),
                tr("accusative plural"),
                tr("vocative plural"),
            ],
            False,
            False,
        ),
        (
            form_ids[4],
            db.tags.get_tag_id(tr("Inflection")),
            [
                tr("genitive plural"),
            ],
            False,
            False,
        ),
        (
            form_ids[5],
            db.tags.get_tag_id(tr("Inflection")),
            [
                tr("dative plural"),
                tr("ablative plural"),
            ],
            False,
            False,
        ),
        *[
            (
                form_id,
                db.tags.get_tag_id(tr("Base Form With Long Vowel Marks")),
                ["{}"],
                False,
                False,
            )
            for form_id in form_ids
        ],
        *[
            (
                form_id,
                db.tags.get_tag_id(tr("Definitions")),
                ["{}"],
                False,
                False,
            )
            for form_id in form_ids
        ],
    ]
    for tag_values in tag_values_list:
        db.tag_rows.set_tag_values(*tag_values)
    row_data = [
        (
            None,
            [
                (
                    db.tags.get_tag_id(tr("Latin")),
                    tr("Latin"),
                    ["exempl"],
                ),
                (
                    db.tags.get_tag_id(tr("Latin With Long Vowel Marks")),
                    tr("Latin With Long Vowel Marks"),
                    ["exempl"],
                ),
                (
                    db.tags.get_tag_id(tr("Part Of Speech")),
                    tr("Part Of Speech"),
                    [""],
                ),
                (
                    db.tags.get_tag_id(tr("Inflection")),
                    tr("Inflection"),
                    [""],
                ),
                (
                    db.tags.get_tag_id(tr("Base Form With Long Vowel Marks")),
                    tr("Base Form With Long Vowel Marks"),
                    ["exemplum"],
                ),
                (
                    db.tags.get_tag_id(tr("Definitions")),
                    tr("Definitions"),
                    ["example"],
                ),
            ],
        )
    ]
    open_windows_for_create_templates_example(
        name,
        db,
        entry_id,
        template_name,
        row_data,
    )


def set_entry_format_simple():
    name = tr("Simple Example")
    path, name = create_new_dict_path_with_non_existing_name(name)
    db = dict_database.DictDatabase(path)
    db.info.set_entry_format(
        tr("{0}: {1}").format(
            f"{{{tr("Tag 1")}}}",
            f"{{{tr("Tag 2")}}}",
        )
    )
    db.info.set_entry_joiner("<hr>")
    db.tags.create_tag(tr("Tag 1"), True, "{{},... {}}", 0)
    db.tags.create_tag(tr("Tag 2"), False, "{{},... {}}", 1)

    entry_id = db.entries.create_entry()
    form_id = db.forms.create_form(entry_id, 0)
    tag_values_list = [
        (
            form_id,
            db.tags.get_tag_id(tr("Tag 1")),
            [tr("value 1")],
            True,
            False,
        ),
        (
            form_id,
            db.tags.get_tag_id(tr("Tag 2")),
            [tr("value 2")],
            False,
            False,
        ),
    ]
    for tag_values in tag_values_list:
        db.tag_rows.set_tag_values(*tag_values)
    open_windows_for_set_format_example(name, db, entry_id)


def set_entry_format_conditional_statements():
    name = tr("Conditional Statements Example")
    path, name = create_new_dict_path_with_non_existing_name(name)
    db = dict_database.DictDatabase(path)
    condition1 = tr("Both {0} and {1} are present.").format(
        f"{{{tr("Tag 1")}}}",
        f"{{{tr("Tag 2")}}}",
    )
    condition2 = tr("Only {} is present.").format(
        f"{{{tr("Tag 1")}}}",
    )
    condition3 = tr("Only {} is present.").format(
        f"{{{tr("Tag 2")}}}",
    )
    db.info.set_entry_format(
        f"{{{condition1}}}|{{{condition2}}}|{{{condition3}}}"
    )
    db.info.set_entry_joiner("<hr>")
    db.tags.create_tag(tr("Tag 1"), True, "{{},... {}}", 0)
    db.tags.create_tag(tr("Tag 2"), False, "{{},... {}}", 1)
    entry_id = db.entries.create_entry()
    form_id1 = db.forms.create_form(entry_id, 0)
    form_id2 = db.forms.create_form(entry_id, 1)
    form_id3 = db.forms.create_form(entry_id, 2)
    tag_values_list = [
        (
            form_id1,
            db.tags.get_tag_id(tr("Tag 1")),
            [tr("value 1")],
            True,
            False,
        ),
        (
            form_id1,
            db.tags.get_tag_id(tr("Tag 2")),
            [tr("value 2")],
            False,
            False,
        ),
        (
            form_id2,
            db.tags.get_tag_id(tr("Tag 1")),
            [tr("value 1")],
            True,
            False,
        ),
        (
            form_id2,
            db.tags.get_tag_id(tr("Tag 2")),
            [""],
            False,
            False,
        ),
        (
            form_id3,
            db.tags.get_tag_id(tr("Tag 1")),
            [""],
            True,
            False,
        ),
        (
            form_id3,
            db.tags.get_tag_id(tr("Tag 2")),
            [tr("value 2")],
            False,
            False,
        ),
    ]
    for tag_values in tag_values_list:
        db.tag_rows.set_tag_values(*tag_values)
    open_windows_for_set_format_example(name, db, entry_id)


def set_entry_format_html():
    name = tr("HTML Example")
    path, name = create_new_dict_path_with_non_existing_name(name)
    db = dict_database.DictDatabase(path)
    db.info.set_entry_format(
        '<b>{0}</b><br><i>{1}</i><div style="color:red; background-color:blue; font-size:{3}pt">{2}</div>'.format(
            f"{{{tr("Tag 1")}}}",
            f"{{{tr("Tag 2")}}}",
            f"{{{tr("Tag 3")}}}",
            settings.dict_font_size * 3,
        )
    )
    db.info.set_entry_joiner("<hr>")
    db.tags.create_tag(tr("Tag 1"), True, "{{},... {}}", 0)
    db.tags.create_tag(tr("Tag 2"), True, "{{},... {}}", 1)
    db.tags.create_tag(tr("Tag 3"), True, "{{},... {}}", 2)
    entry_id = db.entries.create_entry()
    form_id = db.forms.create_form(entry_id, 0)
    tag_values_list = [
        (
            form_id,
            db.tags.get_tag_id(tr("Tag 1")),
            [tr("This tag is bold.")],
            True,
            False,
        ),
        (
            form_id,
            db.tags.get_tag_id(tr("Tag 2")),
            [tr("This tag is italic.")],
            True,
            False,
        ),
        (
            form_id,
            db.tags.get_tag_id(tr("Tag 3")),
            [tr("This tag is stylish.")],
            True,
            False,
        ),
    ]
    for tag_values in tag_values_list:
        db.tag_rows.set_tag_values(*tag_values)
    open_windows_for_set_format_example(name, db, entry_id)


def set_entry_format_escaped_curly_braces():
    name = tr("Escaped Curly Braces Example")
    path, name = create_new_dict_path_with_non_existing_name(name)
    db = dict_database.DictDatabase(path)
    db.info.set_entry_format(
        tr("{}").format(r"\{" + f"{{{tr("Tag")}}}" + r"\}")
    )
    db.info.set_entry_joiner("<hr>")
    db.tags.create_tag(tr("Tag"), True, "{{},... {}}", 0)
    entry_id = db.entries.create_entry()
    form_id = db.forms.create_form(entry_id, 0)
    tag_values_list = [
        (
            form_id,
            db.tags.get_tag_id(tr("Tag")),
            [tr("This tag is surrounded by escaped curly braces.")],
            True,
            False,
        ),
    ]
    for tag_values in tag_values_list:
        db.tag_rows.set_tag_values(*tag_values)
    open_windows_for_set_format_example(name, db, entry_id)


def set_tag_values_format_simple():
    name = tr("Simple Example")
    path, name = create_new_dict_path_with_non_existing_name(name)
    db = dict_database.DictDatabase(path)
    db.info.set_entry_format(f"{{{tr("Tag")}}}")
    db.info.set_entry_joiner("<hr>")
    db.tags.create_tag(
        tr("Tag"),
        True,
        "{{},... {}}" + language.rtl_tag_or_empty_string,
        0,
    )
    entry_id = db.entries.create_entry()
    form_id1 = db.forms.create_form(entry_id, 0)
    form_id2 = db.forms.create_form(entry_id, 1)
    form_id3 = db.forms.create_form(entry_id, 2)
    tag_values_list = [
        (
            form_id1,
            db.tags.get_tag_id(tr("Tag")),
            [tr("value 1")],
            True,
            False,
        ),
        (
            form_id2,
            db.tags.get_tag_id(tr("Tag")),
            [
                tr("value 1"),
                tr("value 2"),
            ],
            False,
            False,
        ),
        (
            form_id3,
            db.tags.get_tag_id(tr("Tag")),
            [
                tr("value 1"),
                tr("value 2"),
                tr("value 3"),
            ],
            False,
            False,
        ),
    ]
    for tag_values in tag_values_list:
        db.tag_rows.set_tag_values(*tag_values)
    open_windows_for_set_format_example(name, db, entry_id)


def set_tag_values_format_conditional_statements():
    name = tr("Conditional Statements Example")
    path, name = create_new_dict_path_with_non_existing_name(name)
    db = dict_database.DictDatabase(path)
    db.info.set_entry_format(f"{{{tr("Tag")}}}")
    db.info.set_entry_joiner("<hr>")
    db.tags.create_tag(
        tr("Tag"),
        True,
        tr("{}|{{} and {}}|{{},... {}, and {}}")
        + language.rtl_tag_or_empty_string,
        0,
    )
    entry_id = db.entries.create_entry()
    form_id1 = db.forms.create_form(entry_id, 0)
    form_id2 = db.forms.create_form(entry_id, 1)
    form_id3 = db.forms.create_form(entry_id, 2)
    form_id4 = db.forms.create_form(entry_id, 3)
    tag_values_list = [
        (
            form_id1,
            db.tags.get_tag_id(tr("Tag")),
            [tr("value 1")],
            True,
            False,
        ),
        (
            form_id2,
            db.tags.get_tag_id(tr("Tag")),
            [
                tr("value 1"),
                tr("value 2"),
            ],
            False,
            False,
        ),
        (
            form_id3,
            db.tags.get_tag_id(tr("Tag")),
            [
                tr("value 1"),
                tr("value 2"),
                tr("value 3"),
            ],
            False,
            False,
        ),
        (
            form_id4,
            db.tags.get_tag_id(tr("Tag")),
            [
                tr("value 1"),
                tr("value 2"),
                tr("value 3"),
                tr("value 4"),
            ],
            False,
            False,
        ),
    ]
    for tag_values in tag_values_list:
        db.tag_rows.set_tag_values(*tag_values)
    open_windows_for_set_format_example(name, db, entry_id)


def set_tag_values_format_html():
    name = tr("HTML Example")
    path, name = create_new_dict_path_with_non_existing_name(name)
    db = dict_database.DictDatabase(path)
    db.info.set_entry_format(f"{{{tr("Tag")}}}")
    db.info.set_entry_joiner("<hr>")
    db.tags.create_tag(
        tr("Tag"),
        True,
        "{<ol><li>{}</li>...<li>{}</li></ol>}",
        0,
    )
    entry_id = db.entries.create_entry()
    form_id1 = db.forms.create_form(entry_id, 0)
    form_id2 = db.forms.create_form(entry_id, 1)
    form_id3 = db.forms.create_form(entry_id, 2)
    tag_values_list = [
        (
            form_id1,
            db.tags.get_tag_id(tr("Tag")),
            [tr("value 1")],
            True,
            False,
        ),
        (
            form_id2,
            db.tags.get_tag_id(tr("Tag")),
            [
                tr("value 1"),
                tr("value 2"),
            ],
            False,
            False,
        ),
        (
            form_id3,
            db.tags.get_tag_id(tr("Tag")),
            [
                tr("value 1"),
                tr("value 2"),
                tr("value 3"),
            ],
            False,
            False,
        ),
    ]
    for tag_values in tag_values_list:
        db.tag_rows.set_tag_values(*tag_values)
    open_windows_for_set_format_example(name, db, entry_id)


def set_tag_values_format_escaped_ellipsis():
    name = tr("Escaped Ellipsis Example")
    path, name = create_new_dict_path_with_non_existing_name(name)
    db = dict_database.DictDatabase(path)
    db.info.set_entry_format(f"{{{tr("Tag")}}}")
    db.info.set_entry_joiner("<hr>")
    db.tags.create_tag(
        tr("Tag"),
        True,
        r"{{},... {}\...}" + language.rtl_tag_or_empty_string,
        0,
    )
    entry_id = db.entries.create_entry()
    form_id = db.forms.create_form(entry_id, 0)
    tag_values_list = [
        (
            form_id,
            db.tags.get_tag_id(tr("Tag")),
            [
                tr("value 1"),
                tr("value 2"),
                tr("value 3"),
            ],
            False,
            False,
        ),
    ]
    for tag_values in tag_values_list:
        db.tag_rows.set_tag_values(*tag_values)
    open_windows_for_set_format_example(name, db, entry_id)


def set_tag_values_format_right_to_left_language():
    name = tr("Right To Left Language Example")
    path, name = create_new_dict_path_with_non_existing_name(name)
    db = dict_database.DictDatabase(path)
    db.info.set_entry_format(f"{{{tr("Tag")}}}")
    db.info.set_entry_joiner("<hr>")
    db.tags.create_tag(
        tr("Tag"),
        True,
        "{{},... {}}{<-}",
        0,
    )
    entry_id = db.entries.create_entry()
    form_id1 = db.forms.create_form(entry_id, 0)
    form_id2 = db.forms.create_form(entry_id, 1)
    form_id3 = db.forms.create_form(entry_id, 2)
    tag_values_list = [
        (
            form_id1,
            db.tags.get_tag_id(tr("Tag")),
            [tr("value 1")],
            True,
            False,
        ),
        (
            form_id2,
            db.tags.get_tag_id(tr("Tag")),
            [
                tr("value 1"),
                tr("value 2"),
            ],
            False,
            False,
        ),
        (
            form_id3,
            db.tags.get_tag_id(tr("Tag")),
            [
                tr("value 1"),
                tr("value 2"),
                tr("value 3"),
            ],
            False,
            False,
        ),
    ]
    for tag_values in tag_values_list:
        db.tag_rows.set_tag_values(*tag_values)
    open_windows_for_set_format_example(name, db, entry_id)
