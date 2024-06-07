import customtkinter as ctk
from tkinter import ttk
import tkinter as tk
import tkinter.messagebox as mb


def adjust_columns_width(tree):
    # Проходим по всем столбцам
    for col in tree["columns"]:
        # Устанавливаем ширину столбца равной максимальной длине текста
        tree.column(col, width=max([len(tree.set(item, col)) for item in tree.get_children('')]) * 9)


# Функция для добавления записи
def add_entry(tree, connection):
    # Создание диалогового окна для ввода данных
    dialog = ctk.CTkToplevel()
    dialog.title("Добавление записи")

    # Настройка цвета фона и других параметров
    dialog.configure(fg_color="#2c2f33")

    # Создание меток и полей для ввода данных
    labels = ["ФИО:", "Номер телефона:", "Автомобиль:", "Проблема:", "Статус:"]
    entries = []

    for idx, label_text in enumerate(labels):
        label = ctk.CTkLabel(dialog, text=label_text, text_color="white")
        label.grid(row=idx, column=0, sticky="w", padx=10, pady=5)

        entry = ctk.CTkEntry(dialog)
        entry.grid(row=idx, column=1, sticky="we", padx=10, pady=5)
        entries.append(entry)

    # Функция для добавления записи
    def add():
        # Получение данных из полей ввода
        new_values = [entry.get() for entry in entries]
        if new_values[4] in ["Принято", "Отказано", "На рассмотрении"]:
            # Вставка новой записи в базу данных
            cursor = connection.cursor()
            cursor.execute("INSERT INTO orders (id, name, phone, car, problem, status) VALUES (NULL, ?, ?, ?, ?, ?)", new_values)
            connection.commit()
        else:
            mb.showerror("Ошибка", "Вы ввели некорректный статус.")

        # Обновление таблицы
        update_table(tree, connection)
        adjust_columns_width(tree)
        # Закрытие диалогового окна
        dialog.destroy()

    # Кнопка для добавления записи
    button_add = ctk.CTkButton(dialog, text="Добавить", command=add)
    button_add.grid(row=len(labels) + 1, column=0, columnspan=2, pady=10)

    # Увеличение размера диалогового окна
    dialog_width = 400
    dialog_height = 300

    # Вычисление размера окна для центрирования
    dialog.update_idletasks()
    x = (dialog.winfo_screenwidth() // 2) - (dialog_width // 2)
    y = (dialog.winfo_screenheight() // 2) - (dialog_height // 2)

    # Центрирование окна и установка размеров
    dialog.geometry(f"{dialog_width}x{dialog_height}+{x}+{y}")
    dialog.resizable(False, False)

    # Отображение диалогового окна
    dialog.mainloop()


def edit_entry(tree, connection):
    # Получение выделенной строки
    selected_item = tree.focus()
    if selected_item:
        # Получение данных о работе из выбранной строки
        work_info = tree.item(selected_item)['values']

        # Создание диалогового окна
        dialog = ctk.CTkToplevel()
        dialog.title("Информация о заказе")

        # Переменные для хранения данных
        name_var = tk.StringVar(value=work_info[1])
        phone_var = tk.StringVar(value=work_info[2])
        car_var = tk.StringVar(value=work_info[3])
        problem_var = tk.StringVar(value=work_info[4])
        status_var = tk.StringVar(value=work_info[5])

        # Создание меток и полей для ввода
        labels = ["ФИО:", "Номер телефона:", "Автомобиль:", "Проблема:", "Статус:"]
        variables = [name_var, phone_var, car_var, problem_var, status_var]

        for idx, label_text in enumerate(labels):
            label = ctk.CTkLabel(dialog, text=label_text)
            label.grid(row=idx, column=0, padx=10, pady=5, sticky="w")

            entry = ctk.CTkEntry(dialog, textvariable=variables[idx])
            entry.grid(row=idx, column=1, padx=10, pady=5, sticky="we")

        # Установка центрирования окна
        dialog_width = 400
        dialog_height = 300
        screen_width = dialog.winfo_screenwidth()
        screen_height = dialog.winfo_screenheight()
        x_coordinate = (screen_width - dialog_width) // 2
        y_coordinate = (screen_height - dialog_height) // 2
        dialog.geometry(f"{dialog_width}x{dialog_height}+{x_coordinate}+{y_coordinate}")
        dialog.resizable(False, False)

        # Кнопки "Готово" и "Отмена"
        def update_data():
            # Обновление данных в выбранной строке
            tree.item(selected_item, values=(
                work_info[0], name_var.get(), phone_var.get(), car_var.get(), problem_var.get(), status_var.get()))

            # Обновление данных в базе данных
            cursor = connection.cursor()
            cursor.execute("""
                UPDATE orders SET name=?, phone=?, car=?, problem=?, status=? WHERE id=?
            """, (name_var.get(), phone_var.get(), car_var.get(), problem_var.get(), status_var.get(), work_info[0]))
            connection.commit()

            dialog.destroy()

        button_frame = ctk.CTkFrame(dialog)
        button_frame.grid(row=5, column=0, columnspan=2, pady=10, sticky="we")

        button_done = ctk.CTkButton(button_frame, text="Готово", command=update_data, fg_color="green", text_color="white")
        button_done.pack(side="left", padx=10)

        button_cancel = ctk.CTkButton(button_frame, text="Отмена", command=dialog.destroy, fg_color="red", text_color="white")
        button_cancel.pack(side="right", padx=10)

        # Заполнение пространства между кнопками цветом, совпадающим с цветом окна
        button_frame.configure(fg_color=dialog.cget("fg_color"))

        # Отображение диалогового окна
        dialog.mainloop()

# Функция для обновления таблицы
def update_table(tree, connection):
    # Очистка таблицы
    for row in tree.get_children():
        tree.delete(row)
    # Получение данных из базы данных
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM orders")
    rows = cursor.fetchall()
    # Вставка данных в таблицу
    for row in rows:
        tree.insert("", "end", values=row)



# Функция для создания вкладки "Заявки"
def create_orders_tab(tab, connection):
    # Создание фрейма для вкладки "Заявки"
    orders_frame = ctk.CTkFrame(tab)
    orders_frame.pack(expand=True, fill='both')

    # Создание заголовков таблицы
    columns = ("ID", "ФИО", "Номер телефона", "Автомобиль", "Проблема", "Статус")

    # Создание и заполнение таблицы
    tree = ttk.Treeview(orders_frame, columns=columns, show="headings", selectmode="browse")
    tree.pack(side="left", fill="both", expand=True)

    # Установка ширины столбцов
    for col in columns:
        tree.heading(col, text=col)
        tree.column(col, width=100)  # Задайте желаемую ширину

    # Вставка данных в таблицу
    update_table(tree, connection)

    # Проверяем, есть ли данные в таблице перед вызовом adjust_columns_width
    if tree.get_children():
        # Автоматическое подгонка ширины столбцов
        adjust_columns_width(tree)

    # Создание фрейма для кнопок и упаковка его справа от таблицы
    buttons_frame = ctk.CTkFrame(orders_frame)
    buttons_frame.pack(side="top", padx=5, pady=5)

    # Создание кнопок для добавления, обновления и удаления записи и упаковка их во фрейм с кнопками
    button_add = ctk.CTkButton(buttons_frame, text="Добавить", command=lambda: add_entry(tree, connection))
    button_add.pack(side="top", padx=5, pady=5)
    button_edit = ctk.CTkButton(buttons_frame, text="Редактировать", command=lambda: edit_entry(tree, connection))
    button_edit.pack(side="top", padx=5, pady=5)
    button_delete = ctk.CTkButton(buttons_frame, text="Удалить", command=lambda: delete_entry(tree, connection))
    button_delete.pack(side="top", padx=5, pady=5)


def delete_entry(tree, connection):
    # Получение выделенной записи
    selected_item = tree.selection()
    if selected_item:
        # Получение ID записи
        item_id = tree.item(selected_item, "values")[0]

        # Отображение подтверждающего диалогового окна
        from tkinter import messagebox
        confirm = messagebox.askyesno("Подтверждение удаления", "Вы точно хотите удалить эту запись?")
        if confirm:
            # Удаление записи из базы данных
            cursor = connection.cursor()
            cursor.execute("DELETE FROM orders WHERE id=?", (item_id,))
            connection.commit()
            # Обновление таблицы
            update_table(tree, connection)

def update_table(tree, connection):
    # Очистка таблицы перед обновлением
    for row in tree.get_children():
        tree.delete(row)

    cursor = connection.cursor()
    cursor.execute("SELECT id, name, phone, car, problem, status, date_start, date_end, stage FROM orders")
    rows = cursor.fetchall()

    for row in rows:
        tree.insert("", "end", values=row)