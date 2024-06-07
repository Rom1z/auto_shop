from turtledemo.forest import tree

import customtkinter as ctk
from tkinter import ttk
import sqlite3
import tkinter as tk
from tkinter import messagebox
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

from parts_tab import update_parts_table, adjust_columns_width

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
import tkinter as tk
from tkinter import messagebox
import os
from datetime import datetime

connection = sqlite3.connect('repair_shop.db')
cursor = connection.cursor()

def update_table_sv(tree, connection):
    for row in tree.get_children():
        tree.delete(row)
    cursor = connection.cursor()
    cursor.execute("SELECT id, name, phone, car, date_start, date_end, stage FROM orders WHERE status=\"Принято\"")
    rows = cursor.fetchall()
    for row in rows:
        tree.insert("", "end", values=row)

def create_summary_tab(tab, tree):
    summary_frame = ctk.CTkFrame(tab)
    summary_frame.pack(expand=True, fill='both')

    clients_label = tk.Label(summary_frame, bg="#1C6CA4", text="Выберите клиента для формирования заказа на ремонт его автомобиля.")
    clients_label.pack(side="top", pady=10)

    select_client_button = ctk.CTkButton(summary_frame, text="Выбрать клиента",
                                         command=lambda: (select_client(selected_client_text, selected_client_text_var,
                                                                       connection), update_parts_table(parts_tree, connection)))
    select_client_button.pack(pady=10)

    selected_client_frame = tk.Frame(summary_frame, bd=2, relief=tk.GROOVE)
    selected_client_frame.pack(pady=5, padx=350, fill=tk.X)
    selected_client_text = tk.Text(selected_client_frame, wrap="word", height=5)
    selected_client_text.pack(side="left", fill="both", expand=True)

    selected_client_text_var = tk.StringVar()
    selected_client_label = tk.Label(selected_client_frame, textvariable=selected_client_text_var)
    selected_client_label.pack(pady=5, padx=5, anchor="w")

    def write_to_text():
        data = f"Выбранный клиент:  \n\nПроблема:  "
        selected_client_text.tag_configure("fontstyle", font=("Arial", 16))
        selected_client_text.insert("end", data + "\n\n", "fontstyle")
        return data

    datasv = write_to_text()

    detail_label = tk.Label(summary_frame, bg="#1C6CA4", text="Выберите необходимые для ремонта запчасти.")
    detail_label.pack(padx=(1, 480), pady=10)

    selected_details_frame = tk.Frame(summary_frame, bd=2, relief=tk.GROOVE)
    selected_details_frame.pack(side="left", fill="both", expand=True, padx=(0, 10), pady=(0, 10))

    parts_columns = ("ID", "Компания", "Артикул", "Описание", "Количество", "Цена")
    parts_tree = ttk.Treeview(selected_details_frame, columns=parts_columns, show="headings", selectmode="browse")
    parts_tree.pack(side="left", fill="both", expand=True)

    column_widths = {
        "ID": 30,
        "Компания": 100,
        "Артикул": 100,
        "Описание": 240,
        "Количество": 60,
        "Цена": 50
    }
    for col, width in column_widths.items():
        parts_tree.column(col, width=width, anchor="center")

    for col in parts_columns:
        parts_tree.heading(col, text=col)

    update_parts_table(parts_tree, connection)

    # Создание фрейма для кнопок с черным фоном
    button_frame = tk.Frame ( summary_frame , bg="#333333" )  # Устанавливаем черный цвет фона
    button_frame.pack ( side="top" , pady=5 )

    add_detail_button = ctk.CTkButton(button_frame, text="Добавить деталь", fg_color="#008c08",
                                      command=lambda: add_detail(selected_parts_listbox, parts_tree, connection))
    add_detail_button.pack(side="left", padx=(0, 5))

    remove_button = ctk.CTkButton(button_frame, text="Удалить деталь", fg_color="#b80000",
                                  command=lambda: remove_detail(selected_parts_listbox, parts_tree, connection))
    remove_button.pack(side="left", padx=(5, 0))

    selected_details_frame = tk.Frame(summary_frame, bd=2, relief=tk.GROOVE)
    selected_details_frame.pack(pady=5)

    selected_parts_listbox = tk.Listbox(selected_details_frame, width=50, height=10)
    selected_parts_listbox.pack(side="top", fill="both", expand=True)

    def add_detail(selected_parts_listbox, parts_tree, connection):
        text_data = selected_client_text.get("1.0", "end")
        if text_data[21] != 'П':
            selected_item = parts_tree.focus()
            if selected_item:
                selected_part = parts_tree.item(selected_item)['values']
                selected_part_str = ', '.join(map(str, selected_part[:-2])) + ', ' + str(selected_part[-1])

                cursor = connection.cursor()
                cursor.execute("SELECT quantity FROM parts WHERE id = ?", (selected_part[0],))
                quantity = cursor.fetchone()[0]
                if int(quantity) > 0:
                    decrease_quantity(selected_part[0], connection)
                    selected_parts_listbox.insert(tk.END, selected_part_str)
                else:
                    messagebox.showwarning("Ошибка", "Недостаточное количество на складе")
        else:
            messagebox.showwarning("Ошидка", "Сначало необходимо выбрать клиента")

    def remove_detail(selected_parts_listbox, parts_tree, connection):
        text_data = selected_client_text.get("1.0", "end")
        if text_data[21] != 'П':
            try:
                selected_item = parts_tree.focus()
                if selected_item:
                    selected_part = parts_tree.item(selected_item)['values']
                    selected_string = ', '.join(map(str, selected_part[:-2])) + ', ' + str(selected_part[-1])
                    for i in range(selected_parts_listbox.size()):
                        if selected_string == selected_parts_listbox.get(i):
                            selected_parts_listbox.delete(i)
                            increase_quantity(selected_part[0], connection)
                            break
            except Exception as e:
                messagebox.showwarning("Ошибка", f"Ошибка удаления: {str(e)}")
        else:
            messagebox.showwarning("Ошибка", "Сначало необходимо выбрать клиента")

    def decrease_quantity(part_id, connection):
        try:
            cursor.execute("UPDATE parts SET quantity = quantity - 1 WHERE id = ?", (part_id,))
            connection.commit()
            update_parts_table(parts_tree, connection)
        except sqlite3.Error as e:
            messagebox.showwarning("Ошибка", f"Ошибка при уменьшении количества: {str(e)}")

    def increase_quantity(part_id, connection):
        try:
            cursor = connection.cursor()
            cursor.execute("UPDATE parts SET quantity = quantity + 1 WHERE id = ?", (part_id,))
            connection.commit()
            update_parts_table(parts_tree, connection)
        except sqlite3.Error as e:
            print("Ошибка при увеличении количества:", e)

    def clear_widgets():
        selected_client_text.delete("1.0", tk.END)
        data = f"Выбранный клиент:  \n\nПроблема:  "
        selected_client_text.tag_configure("fontstyle", font=("Arial", 16))
        selected_client_text.insert("end", data + "\n\n", "fontstyle")
        selected_parts_listbox.delete(0, tk.END)

    create_order_button = ctk.CTkButton(summary_frame, text="Сформировать заказ", height=100, width=300,
                                        font=("Arial", 22, "bold"), fg_color="green",
                                        command=lambda: (generate_pdf(selected_client_text, selected_parts_listbox),
                                                         clear_widgets()))
    create_order_button.pack(pady=100)

def select_client(selected_client_text, selected_client_text_var, connection):
    def write_to_text(data):
        selected_client_text.delete("1.0", "end")
        selected_client_text.tag_configure("fontstyle", font=("Arial", 16))
        selected_client_text.insert("end", data + "\n\n", "fontstyle")

    client_window = tk.Toplevel()
    client_window.title("Выбор клиента")

    dialog_width = 900
    dialog_height = 200
    screen_width = client_window.winfo_screenwidth()
    screen_height = client_window.winfo_screenheight()
    x_coordinate = (screen_width - dialog_width) / 2
    y_coordinate = (screen_height - dialog_height) / 2
    client_window.geometry("%dx%d+%d+%d" % (dialog_width, dialog_height, x_coordinate, y_coordinate))
    client_window.resizable(False, False)

    columns = ("ID", "ФИО", "Номер телефона", "Автомобиль", "Проблема", "Статус", "Дата приема", "Дата завершения", "Этап работы")
    used_columns = (columns[0], columns[1], columns[2], columns[3], columns[6], columns[7], columns[8])

    client_tree = ttk.Treeview(client_window, columns=used_columns, show="headings", selectmode="browse")
    client_tree.pack(side="left", fill="both", expand=True)

    for col in used_columns:
        client_tree.column(col, width=100)

    for col in used_columns:
        client_tree.heading(col, text=col)

    update_table_sv(client_tree, connection)
    if client_tree.get_children():
        adjust_columns_width(client_tree)

    def select():
        selected_item = client_tree.focus()
        if selected_item:
            selected_client = client_tree.item(selected_item)['values']
            selected_client_text_var.set(f"Выбранный клиент: {selected_client[1]}")
            problem = get_problem(connection, selected_client[0])
            write_to_text(f"Выбранный клиент: {selected_client[1]}\n\nПроблема: {problem}")
            client_window.destroy()

    select_button = tk.Button(client_window, text="Принять", command=select)
    select_button.pack(side="top", padx=5, pady=1)
    select_button = tk.Button(client_window, text="Закрыть", command=client_window.destroy)
    select_button.pack(side="top", padx=5, pady=1)

def get_problem(connection, client_id):
    cursor = connection.cursor()
    cursor.execute("SELECT problem FROM orders WHERE id=?", (client_id,))
    problem = cursor.fetchone()
    if problem:
        return problem[0]
    else:
        return "Проблема не найдена"





def generate_pdf(selected_client_text , selected_parts_listbox):
    text_data = selected_client_text.get ( "1.0" , "end" ).strip ()
    if text_data[21] != 'П':
        # Измените путь на рабочий стол пользователя
        desktop_path = os.path.join ( os.path.join ( os.environ['USERPROFILE'] ) , 'Desktop' )

        # Создайте уникальное имя файла, используя временную метку
        timestamp = datetime.now ().strftime ( "%Y%m%d_%H%M%S" )
        file_name = os.path.join ( desktop_path , f"order_{timestamp}.pdf" )

        c = canvas.Canvas ( file_name , pagesize=A4 )

        # Регистрация шрифта DejaVuSans
        pdfmetrics.registerFont ( TTFont ( 'DejaVuSans' , 'DejaVuSans.ttf' ) )
        c.setFont ( "DejaVuSans" , 20 )

        width , height = A4

        # Добавление заголовка
        c.drawString ( 50 , height - 50 , "Заказ на ремонт автомобиля" )

        # Добавление информации о клиенте
        c.setFont ( "DejaVuSans" , 14 )
        client_info = selected_client_text.get ( "1.0" , "end-1c" )
        y_position = height - 100
        for line in client_info.split ( '\n' ):
            c.drawString ( 50 , y_position , line )
            y_position -= 20

        # Добавление информации о деталях
        parts_info = selected_parts_listbox.get ( 0 , "end" )
        y_position -= 20
        c.setFont ( "DejaVuSans" , 16 )
        c.drawString ( 50 , y_position , "Выбранные детали:" )
        y_position -= 20
        c.setFont ( "DejaVuSans" , 12 )
        for part in parts_info:
            c.drawString ( 50 , y_position , part )
            y_position -= 15

        # Добавление общей стоимости
        total_cost = sum ( int ( detail.split ( ", " )[-1] ) for detail in parts_info )
        c.setFont ( "DejaVuSans" , 14 )
        c.drawString ( 50 , y_position - 20 , f"Общая стоимость: {total_cost} руб." )

        c.save ()
        messagebox.showinfo ( "Успех" , f"Заказ сохранен в {file_name}" )
    else:
        messagebox.showwarning ( "Ошибка" , "Сначала необходимо выбрать клиента" )
def open_order_window(selected_client_text, selected_parts_listbox):
    text_data = selected_client_text.get("1.0", "end")
    if text_data[21] != 'П':
        order_window = tk.Toplevel()
        order_window.title("Формирование заказа")

        dialog_width = 500
        dialog_height = 480
        screen_width = order_window.winfo_screenwidth()
        screen_height = order_window.winfo_screenheight()
        x_coordinate = (screen_width - dialog_width) / 2
        y_coordinate = (screen_height - dialog_height) / 2
        order_window.geometry("%dx%d+%d+%d" % (dialog_width, dialog_height, x_coordinate, y_coordinate))
        order_window.resizable(False, False)

        selected_client_label = tk.Label(order_window, text="Выбранный клиент с проблемой:", font=("Arial", 18))
        selected_client_label.pack(pady=10)

        client_text_content = selected_client_text.get("1.0", "end-1c")

        selected_client_display = tk.Text(order_window, height=5, width=50)
        selected_client_display.insert(tk.END, client_text_content)
        selected_client_display.pack(pady=10)

        selected_client_display.config(font=("Arial", 16))

        selected_parts_label = tk.Label(order_window, text="Выбранные детали:", font=("Arial", 16))
        selected_parts_label.pack(pady=10)

        selected_parts_text = tk.Text(order_window, height=10, width=50, font=("Arial", 16))
        selected_parts_text.pack(pady=10)
        selected_parts_text.insert("end", "\n".join(selected_parts_listbox.get(0, "end")))

        total_cost = sum(int(detail.split(", ")[-1]) for detail in selected_parts_listbox.get(0, "end"))

        total_cost_label = tk.Label(order_window, text=f"Общая стоимость: {total_cost}", font=("Arial", 18))
        total_cost_label.pack(pady=10)

        update_parts_table(tree, connection)
    else:
        messagebox.showwarning("Ошибка", "Сначало необходимо выбрать клиента")