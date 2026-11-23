import threading
from src.server.network import ChatServer
from src.server.discovery import ServerDiscovery
import tkinter as tk
from tkinter import ttk


class ServerGUI:
    def __init__(self):
        # Создание главного окна
        self.root = tk.Tk()
        # Указание заголовка
        self.root.title("Серверная часть чата на основе TCP-сокетов")
        # Указание размера окна
        self.root.geometry("1000x600")

        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

        self.discovery = ServerDiscovery(on_message=self.update_message)

        # Создание сервера
        self.server = ChatServer(
            on_message=self.update_message,
            on_user_update=self.on_user_update
        )

        self.create_widgets()


    def create_widgets(self):
        # ========== Верхняя панель ==========
        connection_frame = ttk.LabelFrame(self.root, text="Настройка сервера", padding=10)
        connection_frame.pack(fill=tk.X, padx=10, pady=5)

        # IP адрес
        ttk.Label(connection_frame, text="IP-адрес:").grid(row=0, column=0, padx=5, pady=5)
        self.ip_entry = ttk.Entry(connection_frame, width=20)
        self.ip_entry.insert(0, self.server.host)
        self.ip_entry.grid(row=0, column=1, padx=5, pady=5)

        # Порт
        ttk.Label(connection_frame, text="Порт:").grid(row=0, column=2, padx=5, pady=5)
        self.port_entry = ttk.Entry(connection_frame, width=15)
        self.port_entry.insert(0, self.server.port)
        self.port_entry.grid(row=0, column=3, padx=5, pady=5)

        # Кнопки
        self.start_button = ttk.Button(connection_frame, text="Запустить сервер", width=30, command=self.start_server_in_thread)
        self.start_button.grid(row=0, column=4, padx=5, pady=5)

        self.stop_button = ttk.Button(connection_frame, text="Остановить сервер", width=30, command=self.stop_server, state="disabled")
        self.stop_button.grid(row=0, column=5, padx=5, pady=5)

        # ========== Основная область (две колонки) ==========
        main_panel = ttk.Frame(self.root)
        main_panel.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # ----- Левая колонка - пользователи -----
        users_frame = ttk.LabelFrame(main_panel, text="Активные пользователи", padding=5)
        users_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(5,5))

        # Список пользователей
        self.users_listbox = tk.Listbox(users_frame, height=15, font=("Arial", 10))
        self.users_listbox.pack(fill=tk.BOTH, expand=True)

        # ----- Правая колонка - сообщения пользователей -----
        messages_frame = ttk.LabelFrame(main_panel, text="Сообщения пользователей", padding=5)
        messages_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5,5))

        # Область для сообщений пользователей
        self.messages_area = tk.Listbox(messages_frame, width=50, height=15, font=("Arial", 10))
        self.messages_area.pack(fill=tk.BOTH, expand=True)

    def start_server_in_thread(self):
        """Запуск интерфейса"""
        ip = self.ip_entry.get().strip()
        port = self.port_entry.get().strip()

        if not ip or not port:
            self.messages_area.insert(tk.END, "[ОШИБКА] Заполните IP и порт!")
            return

        self.start_button.config(state="disabled")
        self.stop_button.config(state="normal")
        self.ip_entry.config(state="disabled")
        self.port_entry.config(state="disabled")

        thread = threading.Thread(target=self.server.start, args=(ip, port))
        thread.daemon = True
        thread.start()

        thread_udp = threading.Thread(target=self.discovery.start, args=(ip, port))
        thread_udp.daemon = True
        thread_udp.start()


    def stop_server(self):
        """Остановка сервера"""
        self.server.stop()
        self.discovery.stop()

        self.start_button.config(state="normal")
        self.stop_button.config(state="disabled")
        self.ip_entry.config(state="normal")
        self.port_entry.config(state="normal")

    def update_message(self, text):
        """Обновление списка сообщений"""
        self.root.after(0, lambda: self.messages_area.insert(tk.END, text))
        self.root.after(0, lambda: self.messages_area.see(tk.END))


    def on_user_update(self, action, username):
        """Управление клиентами: удаление или добавление"""

        def _update():
            if action == "add":
                # Получаем текущий список, чтобы не добавить дубликат
                current_users = self.users_listbox.get(0, tk.END)
                if username not in current_users:
                    self.users_listbox.insert(tk.END, username)

            elif action == "remove":
                # Получаем список всех пользователей
                current_users = self.users_listbox.get(0, tk.END)
                if username in current_users:
                    index = current_users.index(username)
                    self.users_listbox.delete(index)  # Удаляем по индексу

            elif action == "clear":
                self.users_listbox.delete(0, tk.END)

        self.root.after(0, _update)

    def on_closing(self):
        """Отключение сервера"""
        self.server.stop()
        self.discovery.stop()
        self.root.destroy()


    def run(self):
        self.root.mainloop()