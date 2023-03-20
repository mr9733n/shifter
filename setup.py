import os
import sys
import ctypes
import subprocess
from distutils.core import setup
import py2exe
import requests


def set_process_name(name):
    if os.name == "nt":
        # Change the console window title on Windows
        ctypes.windll.kernel32.SetConsoleTitleW(name)
    else:
        # Set the process name on Unix-like systems
        if sys.platform.startswith("linux"):
            # Only works on Linux
            from prctl import set_name
            set_name(name)
        elif sys.platform.startswith("darwin"):
            # Only works on macOS
            from ctypes import cdll
            libSystem = cdll.LoadLibrary("libSystem.dylib")
            libSystem.libproc_name(name.encode('utf-8'))


set_process_name("Shifter")
setup(console=["shifter.py"],
      py_modules=["shifter_utils"],
      data_files=[("", ["config.json"])],
      options={"py2exe": {"bundle_files": 1, "includes": ["requests"]}})

while True:
    # Start the script in a new subprocess
    process = subprocess.Popen([sys.executable, "shifter.py"])

    print("File Shifter Started")
    # Wait for the subprocess to finish
    process.communicate()
