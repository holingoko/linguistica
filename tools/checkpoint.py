import os
import shutil
import zipfile

from src import app_info
from tools import file_prefix

repo_dir = os.path.dirname(os.path.dirname(__file__))
current_out_dir = os.path.join(
    repo_dir,
    "build",
    "_{}_repo".format(file_prefix.prefix),
)
resources_dir = os.path.join(repo_dir, "resources")
source_code_dir_name = app_info.name.lower()
zip_name = f"{source_code_dir_name}.zip"


def make_checkpoint(out_dir=current_out_dir):
    try:
        os.makedirs(out_dir, exist_ok=False)
    except FileExistsError:
        return
    skip_set = {
        ".DS_Store",
        ".git",
        ".idea",
        ".venv",
        "build",
    }
    for name in os.listdir(repo_dir):
        if name in skip_set:
            continue
        try:
            shutil.copytree(
                src=os.path.join(repo_dir, name),
                dst=os.path.join(out_dir, name),
            )
        except NotADirectoryError:
            shutil.copyfile(
                src=os.path.join(repo_dir, name),
                dst=os.path.join(out_dir, name),
            )
    for root, dir_names, file_names in os.walk(out_dir):
        for dir_name in dir_names:
            if "__pycache__" in dir_name:
                path = os.path.join(root, dir_name)
                shutil.rmtree(path)


def paths_in_dir_recursive(base):
    paths = []
    for name in os.listdir(base):
        path = os.path.join(base, name)
        if os.path.isdir(path):
            paths.extend(paths_in_dir_recursive(path))
        else:
            paths.append(path)
    return paths


def update_source_code_resource():
    out_dir = os.path.join(
        repo_dir,
        "resources",
        source_code_dir_name,
    )
    shutil.rmtree(out_dir, ignore_errors=True)
    try:
        os.makedirs(out_dir, exist_ok=False)
    except FileExistsError:
        return
    skip_set = {
        ".DS_Store",
        ".git",
        ".idea",
        ".venv",
        "build",
        "resources",
        source_code_dir_name,
        zip_name,
    }
    for name in os.listdir(repo_dir):
        if name in skip_set:
            continue
        try:
            shutil.copytree(
                src=os.path.join(repo_dir, name),
                dst=os.path.join(out_dir, name),
            )
        except NotADirectoryError:
            shutil.copyfile(
                src=os.path.join(repo_dir, name),
                dst=os.path.join(out_dir, name),
            )
    for name in os.listdir(resources_dir):
        if name in skip_set:
            continue
        try:
            shutil.copytree(
                src=os.path.join(resources_dir, name),
                dst=os.path.join(out_dir, "resources", name),
            )
        except NotADirectoryError:
            shutil.copyfile(
                src=os.path.join(resources_dir, name),
                dst=os.path.join(out_dir, "resources", name),
            )
    for root, dir_names, file_names in os.walk(out_dir):
        for dir_name in dir_names:
            if "__pycache__" in dir_name:
                path = os.path.join(root, dir_name)
                shutil.rmtree(path)
    for root, dir_names, file_names in os.walk(
        os.path.join(
            out_dir,
            "resources",
        )
    ):
        for dir_name in dir_names:
            if "__pycache__" in dir_name:
                path = os.path.join(root, dir_name)
                shutil.rmtree(path)
    zip_path = os.path.join(resources_dir, zip_name)
    zip_file = zipfile.ZipFile(
        zip_path,
        mode="w",
        compression=zipfile.ZIP_DEFLATED,
        compresslevel=9,
    )
    source_code_dir = os.path.join(
        repo_dir,
        "resources",
        source_code_dir_name,
    )
    for path in paths_in_dir_recursive(source_code_dir):
        zip_file.write(
            path,
            arcname=path.replace(
                out_dir,
                source_code_dir_name,
            ),
        )
    shutil.rmtree(out_dir)


update_source_code_resource()
