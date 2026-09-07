import os

import flet as ft

from .download_tab import download_tab
from .settings_tab import settings_tab
from .utils import default_download_dir, storage_get

# Old builds defaulted here, which happens to be this project's own folder.
_LEGACY_DIR = os.path.join(os.path.expanduser("~"), "YoutubeDownloader")


def _shared_url_from_route(route):
    """Best-effort: when the app is opened from a shared/handled YouTube (Music)
    link, Flet delivers it as ``page.route`` (path + query, without the host).
    Rebuild something yt-dlp can use.
    """
    if not route:
        return None
    route = route.strip()
    if route.startswith("http"):
        return route
    if "watch" in route and "v=" in route:
        if not route.startswith("/"):
            route = "/" + route
        return "https://music.youtube.com" + route
    return None


def main(page: ft.Page):
    page.title = "YoutubeDownloader"
    page.theme = ft.Theme(color_scheme_seed="red")
    page.auto_scroll = True

    download_dir = storage_get(page, "download_dir")
    if not download_dir or os.path.normpath(download_dir) == os.path.normpath(
        _LEGACY_DIR
    ):
        download_dir = default_download_dir()
        os.makedirs(download_dir, exist_ok=True)
        page.client_storage.set("download_dir", download_dir)

    page.add(
        ft.Row(
            alignment=ft.MainAxisAlignment.CENTER,
            controls=[
                ft.Icon(ft.Icons.VIDEO_LIBRARY, size=40),
                ft.Text("YoutubeDownloader", size=40),
            ],
        ),
        ft.Container(
            expand=True,
            content=ft.Tabs(
                selected_index=0,
                scrollable=True,
                tabs=[
                    download_tab(page),
                    settings_tab(page),
                ],
            ),
        ),
    )

    def handle_route(_=None):
        url = _shared_url_from_route(page.route)
        prefill = getattr(page, "prefill_download_url", None)
        if url and prefill:
            prefill(url)

    page.on_route_change = handle_route
    handle_route()
