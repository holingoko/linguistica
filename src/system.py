import os
import platform

from src import app_info
from src.qt import *

WINDOWS = "Windows"
MAC_OS = "Darwin"
LINUX = "Linux"

os_type = platform.system()
os_release = platform.release()
os_ = f"{os_type} {os_release}"
processor = platform.machine()
python = platform.python_version()
running_built_app = "__compiled__" in globals()
running_unit_test = False
system_font = QFontDatabase.systemFont(QFontDatabase.SystemFont.GeneralFont)
app_data_dir = os.path.join(
    os.path.normpath(
        QStandardPaths.writableLocation(
            QStandardPaths.StandardLocation.AppLocalDataLocation,
        )
    ),
    app_info.author,
    app_info.name,
)
documents_dir = os.path.normpath(
    QStandardPaths.writableLocation(
        QStandardPaths.StandardLocation.DocumentsLocation,
    )
)
temp_dir = os.path.join(
    os.path.normpath(
        QStandardPaths.writableLocation(
            QStandardPaths.StandardLocation.TempLocation,
        )
    ),
    app_info.author,
    app_info.name,
)
