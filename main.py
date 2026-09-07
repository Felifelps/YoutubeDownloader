import flet as ft

from source import main

# Runs on import so `flet build` / `flet run` pick it up, and also when this
# file is executed directly (`python main.py`).
ft.app(target=main)
