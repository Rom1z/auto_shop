import customtkinter as ctk
from tkinter import ttk , messagebox
import tkinter.messagebox as mb
import tkinter as tk
import tkinter.messagebox as messagebox

def adjust_columns_width(tree):
    # Проходим по всем столбцам
    for col in tree["columns"]:
        # Устанавливаем ширину столбца равной максимальной длине текста
        tree.column(col, width=max([len(tree.set(item, col)) for item in tree.get_children('')]) * 9)


# Функция для обновления таблицы "Запчасти"
def update_parts_table(tree, connection):
    # Очистка таблицы
    for row in tree.get_children():
        tree.delete(row)
    # Получение данных из базы данных
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM parts")
    rows = cursor.fetchall()
    # Вставка данных в таблицу
    for row in rows:
        tree.insert("", "end", values=row)

# Функция для добавления записи в таблицу "Запчасти"
def add_part_entry(tree, connection):
    # Create the dialog window for data input
    dialog = ctk.CTkToplevel()
    dialog.title("Добавление записи")
    dialog.configure(bg="#2c2f33")  # Set the background color to dark

    # Create labels and entry fields for data input
    labels = ["Компания", "Артикул", "Описание", "Количество", "Стоимость"]
    entries = []

    for idx, label_text in enumerate(labels):
        label = ctk.CTkLabel(dialog, text=label_text, text_color="white")
        label.grid(row=idx, column=0, sticky="w", padx=10, pady=5)

        entry = ctk.CTkEntry(dialog)
        entry.grid(row=idx, column=1, sticky="we", padx=10, pady=5)

        entries.append(entry)

    # Function to add a record
    def add():
        # Get data from input fields
        new_values = [entry.get() for entry in entries]

        # Check if all fields are filled
        if not all(new_values):
            ctk.CTkMessagebox(title="Ошибка", message="Не все поля заполнены!").show()
            return

        # Insert a new record into the database
        cursor = connection.cursor()
        cursor.execute("INSERT INTO parts (company, article, description, quantity, cost) VALUES (?, ?, ?, ?, ?)", new_values)
        connection.commit()

        # Update the table
        update_parts_table(tree, connection)

        # Close the dialog window
        dialog.destroy()

    # Button to add a record
    button_add = ctk.CTkButton(dialog, text="Добавить", command=add)
    button_add.grid(row=len(labels), column=0, columnspan=2, pady=10)

    # Set the size of the window
    dialog.geometry("400x250")

    # Calculate the window size for centering
    dialog.update_idletasks()
    width = dialog.winfo_width()
    height = dialog.winfo_height()
    x = (dialog.winfo_screenwidth() // 2) - (width // 2)
    y = (dialog.winfo_screenheight() // 2) - (height // 2)

    # Center the window
    dialog.geometry(f"+{x}+{y}")
    dialog.resizable(False, False)

    # Display the dialog window
    dialog.mainloop()

def update_parts_table(tree, connection):
    # Clear the current contents of the treeview
    for row in tree.get_children():
        tree.delete(row)

    # Query the database and insert new data into the treeview
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM parts")
    rows = cursor.fetchall()

    for row in rows:
        tree.insert("", tk.END, values=row)

    # Adjust columns width
    adjust_columns_width(tree)

def adjust_columns_width(tree):
    for col in tree["columns"]:
        tree.column(col, width=tk.font.Font().measure(col))
# Функция для редактирования записи в таблице "Запчасти"
def open_part_info_dialog(tree, connection):
    # Получение выделенной строки
    selected_item = tree.focus()
    if selected_item:
        # Получение данных о запчасти из выбранной строки
        part_info = tree.item(selected_item)['values']

        # Создание диалогового окна
        dialog = ctk.CTkToplevel()
        dialog.title("Информация о запчасти")

        # Переменные для хранения данных
        company_var = tk.StringVar(value=part_info[1])
        article_var = tk.StringVar(value=part_info[2])
        description_var = tk.StringVar(value=part_info[3])
        quantity_var = tk.StringVar(value=part_info[4])
        cost_var = tk.StringVar(value=part_info[5])

        # Создание меток и полей для ввода
        ctk.CTkEntry(dialog, textvariable=company_var).grid(row=0, column=1, padx=5, pady=5, sticky='we')
        ctk.CTkLabel(dialog, text="Компания:").grid(row=0, column=0, padx=5, pady=5, sticky='w')

        ctk.CTkEntry(dialog, textvariable=article_var).grid(row=1, column=1, padx=5, pady=5, sticky='we')
        ctk.CTkLabel(dialog, text="Артикул:").grid(row=1, column=0, padx=5, pady=5, sticky='w')

        ctk.CTkEntry(dialog, textvariable=description_var).grid(row=2, column=1, padx=5, pady=5, sticky='we')
        ctk.CTkLabel(dialog, text="Описание:").grid(row=2, column=0, padx=5, pady=5, sticky='w')

        ctk.CTkEntry(dialog, textvariable=quantity_var).grid(row=3, column=1, padx=5, pady=5, sticky='we')
        ctk.CTkLabel(dialog, text="Количество:").grid(row=3, column=0, padx=5, pady=5, sticky='w')

        ctk.CTkEntry(dialog, textvariable=cost_var).grid(row=4, column=1, padx=5, pady=5, sticky='we')
        ctk.CTkLabel(dialog, text="Стоимость:").grid(row=4, column=0, padx=5, pady=5, sticky='w')

        # Установка центрирования окна
        dialog_width = 500
        dialog_height = 250
        screen_width = dialog.winfo_screenwidth()
        screen_height = dialog.winfo_screenheight()
        x_coordinate = (screen_width - dialog_width) / 5
        y_coordinate = (screen_height - dialog_height) / 5
        dialog.geometry("%dx%d+%d+%d" % (dialog_width, dialog_height, x_coordinate, y_coordinate))
        dialog.resizable(False, False)

        # Кнопки "Готово" и "Отмена"
        def update_data():
            # Обновление данных в выбранной строке
            tree.item(selected_item, values=(
                part_info[0], company_var.get(), article_var.get(), description_var.get(), quantity_var.get(), cost_var.get()))

            # Обновление данных в базе данных
            cursor = connection.cursor()
            cursor.execute("""
                UPDATE parts SET company=?, article=?, description=?, quantity=?, cost=? WHERE id=?
            """, (company_var.get(), article_var.get(), description_var.get(), quantity_var.get(), cost_var.get(), part_info[0]))
            connection.commit()

            dialog.destroy()

        ctk.CTkButton(dialog, text="Готово", command=update_data, fg_color="green").grid(row=5, column=0, padx=(70, 5), pady=5, columnspan=1)
        ctk.CTkButton(dialog, text="Отмена", command=dialog.destroy).grid(row=5, column=1, padx=(5, 70), pady=5,columnspan=1)
        # Отображение диалогового окна
        dialog.mainloop()


# Функция для удаления записи из таблицы "Запчасти"
def delete_part_entry(tree , connection):
    # Получение выделенной записи
    selected_item = tree.selection ()
    if selected_item:
        # Получение ID записи
        item_id = tree.item ( selected_item , "values" )[0]

        # Подтверждение удаления
        confirm = messagebox.askyesno ( "Подтверждение удаления" , "Вы уверены, что хотите удалить эту запись?" )
        if confirm:
            # Удаление записи из базы данных
            cursor = connection.cursor ()
            cursor.execute ( "DELETE FROM parts WHERE id=?" , (item_id ,) )
            connection.commit ()
            # Обновление таблицы
            update_parts_table ( tree , connection )


# Функция для создания интерфейса на вкладке "Запчасти"
def create_parts_tab(tab, connection):
    # Создание фрейма для вкладки "Запчасти"
    parts_frame = ctk.CTkFrame(tab)
    parts_frame.pack(expand=True, fill='both')

    # Создание заголовков таблицы
    columns = ("ID", "Компания", "Артикул", "Описание", "Количество", "Стоимость")

    # Создание и заполнение таблицы
    tree = ttk.Treeview(parts_frame, columns=columns, show="headings", selectmode="browse")
    tree.pack(side="left", fill="both", expand=True)

    # Установка ширины столбцов
    for col in columns:
        tree.heading(col, text=col)
        tree.column(col, width=100, anchor="center")  # Задайте желаемую ширину

    # Вставка данных в таблицу
    update_parts_table(tree, connection)

    # Проверка наличия данных для выполнения автоматической подгонки ширины столбцов
    if tree.get_children():
        # Автоматическое подгонка ширины столбцов
        adjust_columns_width(tree)

    # Создание кнопок для добавления, редактирования и удаления записей
    button_add = ctk.CTkButton(parts_frame, text="Добавить", command=lambda: add_part_entry(tree, connection))
    button_add.pack(side="top", padx=5, pady=5)
    button_edit = ctk.CTkButton(parts_frame, text="Редактировать", command=lambda: open_part_info_dialog(tree, connection))
    button_edit.pack(side="top", padx=5, pady=5)
    button_delete = ctk.CTkButton(parts_frame, text="Удалить", command=lambda: delete_part_entry(tree, connection))
    button_delete.pack(side="top", padx=5, pady=5)

    return tree