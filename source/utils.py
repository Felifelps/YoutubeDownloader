import os

import flet as ft


def default_download_dir() -> str:
    """A friendly place to drop files: the user's ``Downloads`` folder (or the
    home folder as a fallback), inside a ``YoutubeDownloader`` subfolder.
    """
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
