import os
import sys
import time
import traceback

from PySide6.QtCore import __version__ as qt_version

from src import app_info
from src import settings
from src import system

original_std_out_write = sys.stdout.write


def log(run):
    os.makedirs(settings.app_logging_dir, exist_ok=True)
    date = time.strftime("%Y-%m-%d_%H_%M_%S")
    log_path = os.path.join(settings.app_logging_dir, f"{date}.txt")
    with open(log_path, mode="w", buffering=1, encoding="utf-8") as log_file:
        log_file.write(f"Version:\t\t{app_info.version}\n")
        log_file.write(f"Python:\t\t\t{system.python}\n")
        log_file.write(f"Qt: \t\t\t{qt_version}\n")
        log_file.write(f"System:\t\t\t{system.os_}\n")
        log_file.write(f"Processor:\t\t{system.processor}\n")
        log_file.write(time.strftime("Log Start:\t\t%H:%M:%S\n\n"))

        def capture_output(output):
            log_file.write(output)
            original_std_out_write(output)

        sys.stdout.write = capture_output
        sys.stderr.write = capture_output
        try:
            run()
        except:
            exception = traceback.format_exc()
            print(exception)
        log_file.write(time.strftime("\n\nLog End:\t\t%H:%M:%S\n"))
