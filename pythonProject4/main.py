import os
import sqlite3
from PIL import Image , ImageTk
import customtkinter as ctk
from fpdf import FPDF
import qrcode
import tkinter as tk
from tkinter import messagebox

from create_window import *
from orders_tab import *
from clients_tab import *
from parts_tab import *
from svodka import *

# Создание соединения с базой данных SQLite
connection = sqlite3.connect ( 'repair_shop.db' )
cursor = connection.cursor ()

# Создание таблиц, если они не существуют
cursor.execute ( '''CREATE TABLE IF NOT EXISTS orders (
                  id INTEGER PRIMARY KEY,
                  name TEXT,
                  phone TEXT,
                  car TEXT,
                  problem TEXT,
                  status TEXT,
                  date_start TEXT,
                  date_end TEXT,
                  stage TEXT)''' )

cursor.execute ( '''CREATE TABLE IF NOT EXISTS parts (
                  id INTEGER PRIMARY KEY,
                  company TEXT,
                  article TEXT,
                  description TEXT,
                  quantity INTEGER,
                  cost INTEGER)''' )


def generate_pdf_order(client_info , parts_list , total_cost):
    try:
        # Создаем QR-код
        qr = qrcode.QRCode ( version=1 , box_size=10 , border=5 )
        qr.add_data ( client_info )
        qr.make ( fit=True )
        img = qr.make_image ( fill='black' , back_color='white' )

        # Сохраняем QR-код как изображение
        qr_code_path = "qr_code.png"
        img.save ( qr_code_path )

        # Создаем PDF-документ
        pdf = FPDF ()
        pdf.add_page ()

        # Добавляем заголовок
        pdf.set_font ( "Arial" , size=16 )
        pdf.cell ( 200 , 10 , txt="Заказ на ремонт автомобиля" , ln=True , align='C' )

        # Добавляем информацию о клиенте
        pdf.set_font ( "Arial" , size=12 )
        pdf.multi_cell ( 0 , 10 , txt=client_info )

        # Добавляем QR-код
        pdf.image ( qr_code_path , x=10 , y=pdf.get_y () , w=50 )

        # Добавляем информацию о деталях
        pdf.set_y ( pdf.get_y () + 60 )
        pdf.cell ( 0 , 10 , txt="Детали:" , ln=True )
        for part in parts_list:
            pdf.cell ( 0 , 10 , txt=part , ln=True )

        # Добавляем общую стоимость
        pdf.cell ( 0 , 10 , txt=f"Общая стоимость: {total_cost}" , ln=True )

        # Сохраняем PDF
        pdf.output ( "order.pdf" )

        # Удаляем временный QR-код
        os.remove ( qr_code_path )

        messagebox.showinfo ( "Успех" , "Заказ успешно сохранен в PDF." )
    except Exception as e:
        messagebox.showerror ( "Ошибка" , f"Ошибка при сохранении в PDF: {str ( e )}" )


# Функция для создания интерфейса на вкладке "Стартовая страница"
def create_startup_tab(tab):
    startup_frame = ctk.CTkFrame ( tab , corner_radius=10 )
    startup_frame.pack ( expand=True , fill='both' , padx=20 , pady=20 )

    # Загрузка логотипа
    logo = Image.open ( "logo.png" )
    logo = logo.resize ( (150 , 150) , Image.Resampling.LANCZOS )
    logo_image = ImageTk.PhotoImage ( logo )

    # Отображение логотипа
    logo_label = ctk.CTkLabel ( startup_frame , image=logo_image , text="" )
    logo_label.image = logo_image
    logo_label.place ( relx=0.5 , rely=0.2 , anchor='center' )

    # Создание и добавление надписи в центре фрейма
    start = ctk.CTkLabel ( startup_frame , text="Добро пожаловать!" , font=("Helvetica" , 36 , "bold") )
    start.place ( relx=0.5 , rely=0.4 , anchor='center' )
    label = ctk.CTkLabel ( startup_frame ,
                           text="Приложение \"Система учета в авторемонтной мастерской\" разработано студентом\nМаруповым Ромизом Алимухаммадовичем.\n\nДля начала работы, пожалуйста, выберите вкладку в навигационной панели сверху." ,
                           font=("Helvetica" , 18) )
    label.place ( relx=0.5 , rely=0.6 , anchor='center' )


# Функция для создания вкладок и добавления на вкладочный контрол
def create_tabs(connection):
    tab_control = ctk.CTkTabview ( root )

    # Создание вкладок для разделов
    tab_startup = tab_control.add ( "Стартовая страница" )
    tab_orders = tab_control.add ( "Заявки" )
    tab_clients = tab_control.add ( "Клиенты" )
    tab_parts = tab_control.add ( "Запчасти" )
    tab_summary = tab_control.add ( "Сводка заказов" )

    create_startup_tab ( tab_startup )
    create_orders_tab ( tab_orders , connection )
    create_clients_tab ( tab_clients , connection )
    treesv = create_parts_tab ( tab_parts , connection )
    create_summary_tab ( tab_summary , treesv )

    return tab_control , tab_startup


# Функция для создания окна заказа
def open_order_window(selected_client_text , selected_parts_listbox , tree):
    text_data = selected_client_text.get ( "1.0" , "end" )
    if text_data.strip () != '':  # Проверяем, что клиент выбран
        # Создаем новое окно для формирования заказа
        order_window = tk.Toplevel ()
        order_window.title ( "Формирование заказа" )

        # Установка центрирования окна
        dialog_width = 500
        dialog_height = 480
        screen_width = order_window.winfo_screenwidth ()
        screen_height = order_window.winfo_screenheight ()
        x_coordinate = (screen_width - dialog_width) / 2
        y_coordinate = (screen_height - dialog_height) / 2
        order_window.geometry ( "%dx%d+%d+%d" % (dialog_width , dialog_height , x_coordinate , y_coordinate) )
        order_window.resizable ( False , False )

        # Добавляем метку для отображения выбранного клиента
        selected_client_label = tk.Label ( order_window , text="Выбранный клиент с проблемой:" , font=("Arial" , 18) )
        selected_client_label.pack ( pady=10 )

        # Получаем текст из виджета selected_client_text
        client_text_content = selected_client_text.get ( "1.0" , "end-1c" )

        selected_client_display = tk.Text ( order_window , height=5 , width=50 )
        selected_client_display.insert ( tk.END , client_text_content )
        selected_client_display.pack ( pady=10 )

        # Увеличение шрифта
        selected_client_display.config ( font=("Arial" , 16) )

        # Добавляем метку для отображения выбранных деталей
        selected_parts_label = tk.Label ( order_window , text="Выбранные детали:" , font=("Arial" , 16) )
        selected_parts_label.pack ( pady=10 )

        # Добавляем текстовое поле для отображения выбранных деталей
        selected_parts_text = tk.Text ( order_window , height=10 , width=50 , font=("Arial" , 16) )
        selected_parts_text.pack ( pady=10 )
        selected_parts_text.insert ( "end" , "\n".join ( selected_parts_listbox.get ( 0 , "end" ) ) )

        # Вычисляем общую стоимость
        total_cost = sum ( int ( detail.split ( ", " )[-1] ) for detail in selected_parts_listbox.get ( 0 , "end" ) )

        # Добавляем метку для отображения общей стоимости
        total_cost_label = tk.Label ( order_window , text=f"Общая стоимость: {total_cost}" , font=("Arial" , 18) )
        total_cost_label.pack ( pady=10 )

        # Кнопка для сохранения заказа в PDF
        save_pdf_button = ctk.CTkButton ( order_window , text="Сохранить в PDF" , height=40 , width=150 ,
                                          font=("Arial" , 16) ,
                                          command=lambda: (generate_pdf_order ( client_text_content ,
                                                                                selected_parts_listbox.get ( 0 ,
                                                                                                             "end" ) ,
                                                                                total_cost ) ,
                                                           order_window.destroy ()) )
        save_pdf_button.pack ( pady=20 )

        # Вставка данных в таблицу
        update_parts_table ( tree , connection )
    else:
        messagebox.showwarning ( "Ошибка" , "Сначала необходимо выбрать клиента" )


# Создание основного окна
root = ctk.CTk ()

# Установка темы
ctk.set_appearance_mode ( "system" )
ctk.set_default_color_theme ( "blue" )

# Настройка заголовка окна
root.title ( "Система складского учета для автосервиса" )

# Установка стартового размера окна
set_window_geometry ( root )

# Создание вкладок и добавление на вкладочный контрол
tab_control , tab_startup = create_tabs ( connection )

# Размещение вкладочного контрола на главном окне
tab_control.pack ( expand=1 , fill="both" , padx=20 , pady=20 )

# Запуск главного цикла обработки событий
root.mainloop ()