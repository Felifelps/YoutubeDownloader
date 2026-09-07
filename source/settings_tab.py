import flet as ft

from .env import is_android
from .utils import default_download_dir, show_message, storage_get


def settings_tab(page: ft.Page):
    download_dir = storage_get(page, "download_dir") or default_download_dir()
    download_dir_text = ft.Text(f"Current download dir: {download_dir}")

    controls = []

    if is_android():
        # Directory picking isn't available on Android; the location is fixed.
        controls.append(download_dir_text)
    else:
        def set_download_dir(e: ft.FilePickerResultEvent):
            if not e.path:
                return

            page.client_storage.set("download_dir", e.path)
            message = f"Current download dir: {e.path}"
            download_dir_text.value = message
            show_message(page, message)  # Also updates the page

        file_picker = ft.FilePicker(on_result=set_download_dir)
        page.overlay.append(file_picker)

        controls.append(
            ft.Row(
                controls=[
                    ft.IconButton(
                        icon=ft.Icons.EDIT,
                        on_click=lambda e: file_picker.get_directory_path(),
                    ),
                    download_dir_text,
                ]
            )
        )

    def set_playlist_subfolder(e):
        page.client_storage.set("playlist_subfolder", e.control.value)

    controls.append(
        ft.Switch(
            label="Save each playlist in a folder named after the playlist",
            value=bool(storage_get(page, "playlist_subfolder", True)),
            on_change=set_playlist_subfolder,
        )
    )

    controls.append(ft.Divider())
    controls.append(
        ft.TextButton(
            content=ft.Row(
                tight=True,
                controls=[
                    ft.Icon(ft.Icons.CODE, size=18),
                    ft.Text("github.com/Felifelps"),
                ],
            ),
            url="https://github.com/Felifelps",
        )
    )

    return ft.Tab(
        tab_content=ft.Text("Settings"),
        content=ft.Container(
            padding=ft.padding.all(8 if is_android() else 15),
            content=ft.Column(controls=controls),
        ),
    )
