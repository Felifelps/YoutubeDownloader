import flet as ft

from .utils import show_message, storage_get


def settings_tab(page: ft.Page):
    download_dir = storage_get(page, "download_dir")
    download_dir_text = ft.Text(f"Current download dir: {download_dir}")

    def set_download_dir(e: ft.FilePickerResultEvent):
        if not e.path:
            return

        page.client_storage.set("download_dir", e.path)
        message = f"Current download dir: {e.path}"
        download_dir_text.value = message
        show_message(page, message)  # Also updates the page

    file_picker = ft.FilePicker(on_result=set_download_dir)
    page.overlay.append(file_picker)

    def set_playlist_subfolder(e):
        page.client_storage.set("playlist_subfolder", e.control.value)

    playlist_subfolder_switch = ft.Switch(
        label="Save each playlist in a folder named after the playlist",
        value=bool(storage_get(page, "playlist_subfolder", True)),
        on_change=set_playlist_subfolder,
    )

    return ft.Tab(
        tab_content=ft.Text("Settings"),
        content=ft.Container(
            padding=ft.padding.all(15),
            content=ft.Column(
                controls=[
                    ft.Row(
                        controls=[
                            ft.IconButton(
                                icon=ft.Icons.EDIT,
                                on_click=lambda e: file_picker.get_directory_path(),
                            ),
                            download_dir_text,
                        ]
                    ),
                    playlist_subfolder_switch,
                ]
            ),
        ),
    )
