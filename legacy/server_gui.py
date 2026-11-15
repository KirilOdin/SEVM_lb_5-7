# import threading
# import tkinter as tk
# from tkinter import ttk
# from server import start_server
#
#
# ip_entry = None
# port_entry = None
# users_listbox = None
# messages_area = None
#
#
# def create_gui():
#
#     global ip_entry, port_entry, users_listbox, messages_area
#
#     window = tk.Tk()
#
#     window.title("Серверная часть чата на основе TCP-сокетов")
#
#     window.geometry("800x600")
#
#     window.mainloop()
#
#     connection_frame = ttk.LabelFrame(window, text="Настройки сервера", padding=10)
#     connection_frame.pack(fill=tk.X, padx=10, pady=5)
#     # IP адрес
#     ttk.Label(connection_frame, text="IP-адрес:").grid(row=0, column=0, padx=5, pady=5)
#     ip_entry = ttk.Entry(connection_frame, width=20)
#     ip_entry.insert(0, "0.0.0.0")
#     ip_entry.grid(row=0, column=1, padx=5, pady=5)
#
#     # Порт
#     ttk.Label(connection_frame, text="Порт:").grid(row=0, column=2, padx=5, pady=5)
#     port_entry = ttk.Entry(connection_frame, width=15)
#     port_entry.insert(0, "12345")
#     port_entry.grid(row=0, column=3, padx=5, pady=5)
#
#     # Кнопки
#     start_button = ttk.Button(connection_frame, text="Запустить сервер", width=30)
#     start_button.grid(row=0, column=4, padx=5, pady=5)
#     stop_button = ttk.Button(connection_frame, text="Остановить сервер", width=30)
#     stop_button.grid(row=0, column=5, padx=5, pady=5)
#
#
# def start_server_in_thread():
#     # Получаем значения из полей ввода
#     ip = ip_entry.get() # Получаем IP из поля
#     port = port_entry.get() # Получаем порт из поля
#     # Создаём поток путем создания экземпляра класса Thread
#     # Исполняемая функция start_server
#     thread = threading.Thread(target=start_server, args=(ip, port))
#     # Переводим поток в фоновый режим
#     thread.daemon = False
#     # Запускаем поток
#     thread.start()
#
