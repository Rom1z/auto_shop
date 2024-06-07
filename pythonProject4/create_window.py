# Функция для установки стартового размера окна по центру
def set_window_geometry(root):
    root.geometry("1200x800")  # Установка стартового размера окна
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    x = (screen_width - 1200) // 2
    y = (screen_height - 800) // 2
    root.geometry(f"1200x800+{x}+{y}")
    root.resizable(True, True)  # Позволяет изменять размер окна