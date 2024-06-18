import flet as ft

from .utils import show_message

def settings_tab(page: ft.Page):
    download_dir = page.client_storage.get('download_dir')
    download_dir_text = ft.Text(f'Current download dir: {download_dir}')

    def set_download_dir(result):
        message = f'Current download dir: {result.path}'
        page.client_storage.set('download_dir', result.path)
        download_dir_text.value = message
        show_message(page, message) # Updates the page

    file_picker = ft.FilePicker(on_result=set_download_dir)

    return ft.Tab(
        tab_content=ft.Text('Settings'),
        content=ft.Container(
            padding=ft.padding.all(15),
            content=ft.Column(
                controls=[
                    ft.Row([
                        file_picker,
                        ft.IconButton(
                            "edit",
                            on_click=lambda e: file_picker.get_directory_path()
                        ),
                        download_dir_text,
                    ])
                    
                ]
            )
        )
    )
