import flet as ft

from .control import Control
from .utils import show_message

def download_tab(page: ft.Page):
    progress_ring = ft.ProgressRing(visible=False)

    url_field = ft.TextField(
        label="Video/playlist url",
        multiline=True,
    )

    download_type_field = ft.RadioGroup(
        value='video',
        content=ft.Row([
            ft.Radio(value="video", label="Video"),
            ft.Radio(value="audio", label="Audio"),
        ])
    )

    log_field = ft.TextField(
        value="No download started",
        label="Download logs",
        multiline=True,
        read_only=True,
    )

    download_button = ft.FilledButton('Download')

    cancel_button = ft.FilledButton(
        'Cancel',
        visible=False,
        style=ft.ButtonStyle(
            bgcolor=ft.colors.INVERSE_SURFACE
        )
    )

    def clear_output(_):
        log_field.value = ""
        page.update()

    def cancel_download(_):
        page.client_storage.set('cancelled', True)
        cancel_button.disabled = True
        cancel_button.text = "Cancelling..."
        page.update()

    def download(_):
        if not url_field.value:
            return
        download_button.text = "Downloading..."
        download_button.disabled = True
        progress_ring.visible = True
        log_field.value = f"Starting download:\n{url_field.value}\n\nDownloaded:\n"
        cancel_button.visible = True
        cancel_button.text = "Cancel"

        page.update()

        final_message = f"Download done on {page.client_storage.get('download_dir')}"

        for url in url_field.value.split('\n'):
            for r in Control.download(
                url,
                page.client_storage.get('download_dir'),
                download_type_field.value == "audio"
            ):
                if page.client_storage.get('cancelled'):
                    page.client_storage.remove('cancelled')
                    final_message = "Download cancelled by user"
                    break

                log_field.value += f"{r}\n"
                page.update()

        progress_ring.visible = False
        download_button.text = "Download"
        download_button.disabled = False
        cancel_button.visible = False
        cancel_button.disabled = False
        cancel_button.text = "Cancel"

        url_field.value = ""

        log_field.value += f"\n{final_message}"

        show_message(page, final_message)

    download_button.on_click = download
    cancel_button.on_click = cancel_download

    return ft.Tab(
        tab_content=ft.Text('Download'),
        content=ft.Container(
            padding=ft.padding.all(15),
            content=ft.Column(
                scroll=ft.ScrollMode.AUTO,
                controls=[
                    ft.Row(
                        [progress_ring],
                        alignment=ft.MainAxisAlignment.CENTER
                    ),
                    url_field,
                    download_type_field,
                    ft.Row([
                        cancel_button,
                        download_button,
                    ]),
                    ft.Divider(),
                    log_field,
                    ft.Row([
                        ft.FilledButton(
                            'Clear output',
                            on_click=clear_output
                        ),
                        ft.FilledButton(
                            'Open output folder',
                            on_click=lambda e: Control.open_output_path(
                                page.client_storage.get('download_dir')
                            )
                        )
                    ])
                ]
            )
        )
    )
