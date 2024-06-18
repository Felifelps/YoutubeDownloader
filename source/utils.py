def show_message(page, message):
    page.snack_bar.content.value = message
    page.snack_bar.open = True
    page.update()
