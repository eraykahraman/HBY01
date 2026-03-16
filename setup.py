from cx_Freeze import setup, Executable
import sys
import os

# Dependencies are automatically detected, but it might need fine tuning.
build_exe_options = {
    "packages": [
        "PyQt5", 
        "sqlalchemy", 
        "cantools", 
        "psycopg2", 
        "pydantic",
        "deepdiff",
        "orjson",
        "textparser",
        "bitstruct",
        "can",
        "openpyxl"
    ],
    "excludes": [
        "matplotlib", 
        "numpy", 
        "pandas",
        "tkinter",
        "test",
        "distutils",
        "PyQt5.QtQml",
        "PyQt5.QtQuick"
    ],
    "include_files": [],
    "optimize": 0
}

# GUI applications require a different base on Windows
base = None
if sys.platform == "win32":
    base = "Win32GUI"

setup(
    name="DBC Master",
    version="1.0.0",
    description="DBC File Management Application",
    options={"build_exe": build_exe_options},
    executables=[
        Executable(
            "main.py", 
            base=base,
            target_name="DBC_Master.exe",
            icon=None  # Add icon path if you have one
        )
    ]
) 