import os

import flet as ft

from .env import is_android


def default_download_dir() -> str:
    """A friendly place to drop files, inside a ``YoutubeDownloader`` subfolder:
    the shared ``Download`` folder on Android, otherwise the user's
    ``Downloads`` folder (home folder as a last resort).
    """
    if is_android():
        for base in (
            "/storage/emulated/0",
            os.environ.get("EXTERNAL_STORAGE", ""),
            "/sdcard",
        ):
            if base and os.path.isdir(base):
                return os.path.join(base, "Download", "YoutubeDownloader")
        return os.path.join(
            os.path.expanduser("~") or "/data", "YoutubeDownloader"
        )

    home = os.path.expanduser("~")
    downloads = os.path.join(home, "Downloads")
    base = downloads if os.path.isdir(downloads) else home
    return os.path.join(base, "YoutubeDownloader")


def show_message(page: ft.Page, message: str):
    page.open(ft.SnackBar(content=ft.Text(message)))


def storage_get(page: ft.Page, key: str, default=None):
    """``page.client_storage.get`` raises if the stored value was written by a
    different Flet version. Fall back to ``default`` instead of crashing.
    """
    try:
        value = page.client_storage.get(key)
    except Exception:
        return default
    return default if value is None else value
