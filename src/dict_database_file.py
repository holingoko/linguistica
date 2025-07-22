import os
import shutil
import sqlite3
import zipfile

from src import app
from src import app_info
from src import dict_database
from src import messages
from src import settings
from src import system
from src import utils
from src.language import tr
from src.qt import *

extraction_dir = os.path.join(system.temp_dir, "Extracted")
shutil.rmtree(extraction_dir, ignore_errors=True)
zipped_dict_name = f"Dictionary{app_info.db_ext}"


def is_dict_database_file(path):
    if not os.path.exists(path):
        return False
    if os.path.splitext(os.path.basename(path))[1] != app_info.db_ext:
        return False
    try:
        dict_database.DictDatabase(path)
        return True
    except sqlite3.DatabaseError:
        return False


def on_create_dict_database_file():
    os.makedirs(settings.dict_dir, exist_ok=True)
    name_template = tr("Dictionary {}")
    i = 1
    while True:
        path = os.path.join(
            settings.dict_dir,
            f"{name_template.format(i)}{app_info.db_ext}",
        )
        if os.path.exists(path):
            i = i + 1
        else:
            break
    path = QFileDialog.getSaveFileName(
        app.activeWindow(),
        caption=tr("Create Dictionary"),
        dir=path,
    )[0]
    if not path:
        return None
    if os.path.splitext(path)[1] != app_info.db_ext:
        path = f"{path}{app_info.db_ext}"
        if os.path.exists(path):
            messages.NoExtNameWithExtTakenErrorMessage(
                os.path.basename(path),
                lambda: on_create_dict_database_file(),
            ).show()
            return None
    try:
        utils.delete_file(path)
    except PermissionError:
        messages.OverwriteDictionaryFailedErrorMessage(
            os.path.splitext(os.path.basename(path))[0]
        ).show()
        return None
    db = dict_database.DictDatabase(path)
    default_indexed_tag = tr("Word")
    default_unindexed_tag = tr("Definition")
    db.info.set_entry_format(
        f"{{{default_indexed_tag}}}: {{{default_unindexed_tag}}}"
    )
    db.info.set_entry_joiner("<hr>")
    db.tags.create_tag(default_indexed_tag, True, "{{},... {}}", 0)
    db.tags.create_tag(
        default_unindexed_tag,
        False,
        "{<ol><li>{}</li>...<li>{}</li></ol>}",
        1,
    )
    if os.path.normpath(
        os.path.dirname(path),
    ) != os.path.normpath(
        settings.dict_dir,
    ):
        messages.DictionaryNotInDictionaryDirectoryWarningMessage().show()
    return os.path.splitext(os.path.basename(path))[0]


def on_import_dict_database_file(
    src="",
    error_msg_class=messages.FileIsNotDictionaryErrorMessage,
    on_success=lambda _: None,
):
    if not src:
        src = utils.get_open_file_name(
            app.activeWindow(),
            caption=tr("Import Dictionary"),
        )
    if not src:
        return
    if zipfile.is_zipfile(src):
        with zipfile.ZipFile(src, mode="r") as zip_file:
            zip_file.extractall(extraction_dir)
        name = os.path.splitext(os.path.basename(src))[0]
        src = os.path.join(extraction_dir, zipped_dict_name)
        dst = os.path.join(extraction_dir, f"{name}{app_info.db_ext}")
        shutil.move(src, dst)
        src = dst
    if not is_dict_database_file(src):
        error_msg_class(src).show()
        return
    else:
        dst = os.path.join(settings.dict_dir, os.path.basename(src))
        name = os.path.splitext(os.path.basename(src))[0]
        if os.path.exists(dst):

            def continue_():
                try:
                    utils.delete_file(dst)
                except PermissionError:
                    messages.OverwriteDictionaryFailedErrorMessage(
                        os.path.splitext(os.path.basename(dst))[0]
                    ).show()
                    return
                try:
                    shutil.copyfile(src, dst)
                except shutil.SameFileError:
                    pass
                shutil.rmtree(extraction_dir, ignore_errors=True)
                on_success(name)

            messages.ExistingDictionaryOverwriteWarningMessage(
                name,
                continue_,
            ).show()
            return
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        shutil.copyfile(src, dst)
        shutil.rmtree(extraction_dir, ignore_errors=True)
    on_success(name)


def on_export_dict_database_file(name):
    db_path = os.path.join(settings.dict_dir, f"{name}{app_info.db_ext}")
    zip_path = utils.get_save_file_name(
        app.activeWindow(),
        tr("Export Dictionary"),
        f"{name}{app_info.zip_ext}",
    )
    if not zip_path:
        return
    with zipfile.ZipFile(
        zip_path,
        mode="w",
        compression=zipfile.ZIP_DEFLATED,
        compresslevel=9,
    ) as zip_file:
        zip_file.write(db_path, zipped_dict_name)
