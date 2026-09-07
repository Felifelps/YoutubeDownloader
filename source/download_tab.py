import flet as ft

from .control import Control
from .env import is_android
from .utils import default_download_dir, show_message, storage_get

DEFAULT_DIR = default_download_dir()


def download_tab(page: ft.Page):
    progress_ring = ft.ProgressRing(visible=False)

    url_field = ft.TextField(
        label="Video/playlist url (one per line)",
        multiline=True,
    )

    def prefill_download_url(url):
        current = url_field.value or ""
        if url and url not in current:
            url_field.value = (
                f"{current}\n{url}".strip() if current.strip() else url
            )
            page.update()

    # Used by main.py when the app is opened from a shared link.
    page.prefill_download_url = prefill_download_url

    download_type_field = ft.RadioGroup(
        value="video",
        content=ft.Row(
            controls=[
                ft.Radio(value="video", label="Video"),
                ft.Radio(value="audio", label="Audio"),
            ]
        ),
    )

    log_field = ft.TextField(
        value="No download started",
        label="Download logs",
        multiline=True,
        read_only=True,
    )

    download_button = ft.FilledButton("Download")

    cancel_button = ft.FilledButton(
        "Cancel",
        visible=False,
        style=ft.ButtonStyle(bgcolor=ft.Colors.INVERSE_SURFACE),
    )

    def clear_output(e):
        log_field.value = ""
        page.update()

    def cancel_download(e):
        page.client_storage.set("cancelled", True)
        cancel_button.disabled = True
        cancel_button.text = "Cancelling..."
        page.update()

    def is_cancelled():
        if storage_get(page, "cancelled"):
            page.client_storage.remove("cancelled")
            return True
        return False

    def download(e):
        if not url_field.value or not url_field.value.strip():
            return

        download_dir = storage_get(page, "download_dir") or DEFAULT_DIR
        playlist_subfolder = storage_get(page, "playlist_subfolder", True)

        download_button.text = "Downloading..."
        download_button.disabled = True
        progress_ring.visible = True
        cancel_button.visible = True
        cancel_button.disabled = False
        cancel_button.text = "Cancel"
        log_field.value = (
            f"Starting download:\n{url_field.value.strip()}\n\nDownloaded:\n"
        )

        # Clears a flag left over from a previous run.
        page.client_storage.remove("cancelled")
        page.update()

        final_message = f"Download done on {download_dir}"

        for url in url_field.value.split("\n"):
            url = url.strip()
            if not url:
                continue

            try:
                for name in Control.download(
                    url,
                    download_dir,
                    download_type_field.value == "audio",
                    playlist_subfolder,
                ):
                    if is_cancelled():
                        final_message = "Download cancelled by user"
                        break

                    log_field.value += f"{name}\n"
                    page.update()
            except Exception as ex:
                log_field.value += f"Error on {url}: {ex}\n"
                page.update()
                continue

            if is_cancelled():
                final_message = "Download cancelled by user"
                break

        progress_ring.visible = False
        download_button.text = "Download"
        download_button.disabled = False
        cancel_button.visible = False
        cancel_button.disabled = False
        cancel_button.text = "Cancel"
        url_field.value = ""
        log_field.value += f"\n{final_message}"
        page.update()

        show_message(page, final_message)

    def open_output_folder(e):
        target = storage_get(page, "download_dir") or DEFAULT_DIR
        if is_android():
            # No reliable "open this folder" intent from Flet on Android; show
            # the path (and try a launch as a best effort).
            try:
                page.launch_url(f"file://{target}")
            except Exception:
                pass
            show_message(page, f"Files are saved to: {target}")
            return
        Control.open_output_path(target)

    download_button.on_click = download
    cancel_button.on_click = cancel_download

    return ft.Tab(
        tab_content=ft.Text("Download"),
        content=ft.Container(
            padding=ft.padding.all(15),
            content=ft.Column(
                scroll=ft.ScrollMode.AUTO,
                controls=[
                    ft.Row(
                        controls=[progress_ring],
                        alignment=ft.MainAxisAlignment.CENTER,
                    ),
                    url_field,
                    download_type_field,
                    ft.Row(controls=[cancel_button, download_button]),
                    ft.Divider(),
                    log_field,
                    ft.Row(
                        controls=[
                            ft.FilledButton(
                                "Clear output", on_click=clear_output
                            ),
                            ft.FilledButton(
                                "Open output folder",
                                on_click=open_output_folder,
                            ),
                        ]
                    ),
                ],
            ),
        ),
    )
