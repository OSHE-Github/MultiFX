"""Manages offboard (USB) configuration loading"""
from fs import open_fs
import re

SCAN_FOR_DIR: str = "multifx"


def scan_devices() -> str | None:
    """
    Scan for /dev/sd*/ for possible USB drives, then returns the first
    directory that contains SCAN_FOR_DIR
    """
    dev_fs = open_fs("/dev/")
    reg = re.compile("sd*")
    for dir in filter(lambda d: reg.match(str(d)), dev_fs.scandir("")):
        print(f"Checking /dev/{dir} for {SCAN_FOR_DIR}")
        if SCAN_FOR_DIR in dev_fs.scandir(dir):
            print(f"{SCAN_FOR_DIR} found in {dir}!")
            return f"{dir}/{SCAN_FOR_DIR}"
    return None


def try_load() -> bool:
    """
    Attempts to load data from a USB, returns True if successful
    """
    extcfgdir = scan_devices()
    if not extcfgdir:
        return False
    # Copy to on-board config directory


def try_save() -> bool:
    """
    Attempts to write on-board data to a USB, returns True if successful
    """
    extcfgdir = scan_devices()
