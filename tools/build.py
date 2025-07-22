import os
import platform
import shutil
import subprocess

from tools import checkpoint
from tools import file_prefix

WINDOWS = "Windows"
MAC_OS = "Darwin"
LINUX = "Linux"

repo_dir = os.path.dirname(os.path.dirname(__file__))
out_dir = os.path.join(
    repo_dir,
    "build",
    "_{}_built".format(file_prefix.prefix),
)
resources_dir = os.path.join(repo_dir, "resources")
if platform.system() == WINDOWS:
    python_path = os.path.join(repo_dir, ".venv", "Scripts", "python.exe")
elif platform.system() == MAC_OS:
    python_path = os.path.join(repo_dir, ".venv", "bin", "python")
else:
    assert False
main_path = os.path.join(repo_dir, "Linguistica.py")
icon_path = os.path.join(resources_dir, "images", "icon.png")
shutil.rmtree(out_dir, ignore_errors=True)
checkpoint.make_checkpoint(out_dir)
command = [
    python_path,
    "-m",
    "nuitka",
    main_path,
    # "--disable-cache=all",  # !!!
    "--enable-plugin=pyside6",
    f"--include-data-dir={resources_dir}=resources",
    "--macos-create-app-bundle",
    f"--macos-app-icon={icon_path}",
    "--standalone",
    "--show-scons",
    "--windows-console-mode=disable",
    f"--windows-icon-from-ico={icon_path}",
]
print(f"\n{" ".join(command)}\n")
subprocess.check_output(command, cwd=out_dir)
