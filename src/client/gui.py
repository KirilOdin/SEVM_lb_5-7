import tkinter as tk
from tkinter import ttk
import threading
from src.client.network import ChatClient

class ClientGUI:
    def __init__(self):
        # Создание главного окна
        self.root = tk.Tk()
        # Указание заголовка
        self.root.title("Клиентская часть чата на основе TCP-сокетов")
        # Указание размера окна
        self.root.geometry("800x600")


        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

        # Создание клиента
        self.client = ChatClient(
            on_message=self.update_messages,
            on_connected=self.on_connected,
            on_disconnected=self.on_disconnected
        )

        # Создание интерфейса
        self.create_widgets()



    def create_widgets(self):
        # ========== Верхняя панель с настройками ==========
        connection_frame = ttk.LabelFrame(self.root, text="Настройки сервера", padding=10)
        connection_frame.pack(fill=tk.X, padx=10, pady=5)

        # IP адрес
        ttk.Label(connection_frame, text="IP-адрес:").grid(row=0, column=0, padx=5, pady=5)
        self.ip_entry = ttk.Entry(connection_frame, width=15)
        self.ip_entry.grid(row=0, column=1, padx=5, pady=5)
        self.ip_entry.insert(0, "127.0.0.1")
        self.ip_entry.grid(row=0, column=1, padx=5, pady=5)

        # Порт
        ttk.Label(connection_frame, text="Порт:").grid(row=0, column=2, padx=5, pady=5)
        self.port_entry = ttk.Entry(connection_frame, width=10)
        self.port_entry.insert(0, "12345")
        self.port_entry.grid(row=0, column=3, padx=5, pady=5)

        # Логин
        ttk.Label(connection_frame, text="Логин:").grid(row=0, column=4, padx=5, pady=5)
        self.login_entry = ttk.Entry(connection_frame, width=20)
        self.login_entry.insert(0, "Александр Астафьев")
        self.login_entry.grid(row=0, column=5, padx=5, pady=5)

        # Кнопка подключения
        self.connect_button = ttk.Button(connection_frame, text="Подключиться", command=self.start_client_in_thread)
        self.connect_button.grid(row=0, column=6, padx=5, pady=5)

        # ========== Основная область ==========
        main_panel = ttk.Frame(self.root)
        main_panel.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # ----- Колонка - сообщения пользователей -----
        messages_frame = ttk.LabelFrame(main_panel, text="Сообщения пользователей", padding=5)
        messages_frame.pack(fill=tk.BOTH, expand=True)

        # Область для сообщений пользователей
        self.messages_area = tk.Listbox(messages_frame, font=("Arial", 10))
        self.messages_area.pack(fill=tk.BOTH, expand=True)

        # ========== Нижняя панель (Отправка) ==========
        send_frame = ttk.Frame(self.root, padding=10)
        send_frame.pack(fill=tk.X)

        self.message_entry = ttk.Entry(send_frame, font=("Arial", 10))
        self.message_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        self.message_entry.bind("<Return>", lambda e: self.send_message())
        self.message_entry.config(state="disabled")  # Изначально выключено

        self.send_button = ttk.Button(send_frame, text="Отправить", command=self.send_message)
        self.send_button.pack(side=tk.RIGHT)
        self.send_button.config(state="disabled")  # Изначально выключено


    def start_client_in_thread(self):
        """Запуск интерфейса"""

        username = self.login_entry.get().strip()

        if not username:
            self.messages_area.insert(tk.END, "[ОШИБКА] Введите логин!")
            return

        self.connect_button.config(state="disabled")
        self.messages_area.insert(tk.END, "Подключение к серверу...")

        thread = threading.Thread(target=self.client.connect, args=(username, ))
        thread.daemon = True
        thread.start()

    def send_message(self):
        """Отправка сообщений"""
        text = self.message_entry.get().strip()

        if text:
            success = self.client.send_message(text)

            if success:
                self.message_entry.delete(0, tk.END)
            else:
                self.message_entry.delete(tk.END, "[ОШИБКА] Не удалось отправить сообщение.")


    def update_messages(self, text):
        self.root.after(0, lambda: self.messages_area.insert(tk.END, text))

    def on_connected(self):
        def _update():
            self.message_entry.config(state="normal")
            self.send_button.config(state="normal")
            self.login_entry.config(state="disabled")
            self.ip_entry.config(state="disabled")
            self.port_entry.config(state="disabled")
            self.message_entry.focus()
        self.root.after(0, _update)

    def on_disconnected(self):
        def _update():
            self.message_entry.config(state="disabled")
            self.send_button.config(state="disabled")
            self.login_entry.config(state="normal")
            self.ip_entry.config(state="normal")
            self.port_entry.config(state="normal")
            self.connect_button.config(state="normal")
        self.root.after(0, _update)

    def on_closing(self):
        self.client.disconnect()
        self.root.destroy()


    def run(self):
        self.root.mainloop()
