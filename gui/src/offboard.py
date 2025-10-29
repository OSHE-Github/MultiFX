"""Manages offboard (USB) configuration loading"""
import fs
import fs.base
import os
from utils import config_dir, root_dir

SCAN_FOR_DIR: str = "multifx"

# Scans for a test directory under gui root when true
MOCK = False

USB_DIR = f"/run/media/{os.getlogin()}"
if MOCK:
    USB_DIR = f"{root_dir}/.mockdev"


def scan_devices() -> fs.base.FS | None:
    """
    Scan for media drives, then returns the first directory that contains
    SCAN_FOR_DIR
    """
    dev_fs = fs.open_fs(USB_DIR)
    for dir in dev_fs.scandir(""):
        # Skip files
        if not dir.is_dir:
            continue
        print(f"Checking {USB_DIR}/{dir.name} for {SCAN_FOR_DIR}")
        for final_dir in dev_fs.filterdir(dir.name, dirs=[SCAN_FOR_DIR]):
            if not final_dir.is_dir:
                break
            print(f"{SCAN_FOR_DIR} found in {dir.name}!")
            return fs.open_fs(f"{USB_DIR}/{dir.name}/{SCAN_FOR_DIR}")
        print(f"{SCAN_FOR_DIR} directory not found in {USB_DIR}/{dir.name}")
    return None


def try_load() -> bool:
    """
    Attempts to load data from a USB, returns True if successful
    """
    extcfg_fs = scan_devices()
    if not extcfg_fs:
        return False
    # Copy to on-board config directory
    incfg_fs = fs.open_fs(config_dir)
    fs.copy.copy_dir(extcfg_fs, "", incfg_fs, "")

    return True


def try_save() -> bool:
    """
    Attempts to write on-board data to a USB, returns True if successful
    """
    extcfg_fs = scan_devices()
    if not extcfg_fs:
        return False
    # Copy from config to off-board drive
    incfg_fs = fs.open_fs(config_dir)
    fs.copy.copy_dir(incfg_fs, "", extcfg_fs, "")

    return True
