import os

import flet as ft

from .download_tab import download_tab
from .settings_tab import settings_tab

def main(page: ft.Page):
    page.title = "YoutubeDownloader"
    page.theme = ft.Theme(color_scheme_seed='red')
    page.auto_scroll = True

    page.snack_bar = ft.SnackBar(content=ft.Text('None'))

    if not page.client_storage.get('download_dir'):
        download_dir = os.path.join(
            os.path.expanduser('~'), 'YoutubeDownloader'
        )
        if not os.path.exists(download_dir):
            os.mkdir(download_dir)

        page.client_storage.set('download_dir', download_dir)

    page.add(
        ft.Row(
            alignment=ft.MainAxisAlignment.CENTER,
            controls=[
                ft.Icon(ft.icons.VIDEO_LIBRARY, size=40),
                ft.Text('YoutubeDownloader', size=40),
            ]
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
        ft.Container(
            alignment=ft.alignment.bottom_center,
            content=ft.Column(
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    ft.TextButton(
                        content=ft.Text(
                            '@felifelps.dev',
                            text_align=ft.TextAlign.CENTER,
                        ),
                        url="https://www.instagram.com/felifelps.dev/",
                    ),
                    
                ]
            )
        )
    )
