import tkinter as tk
from tkinter import ttk
import threading

from src.client.discovery import ClientDiscovery
from src.common.config_loader import save_client_username
from src.client import ChatClient


class ClientGUI:
    def __init__(self):
        # Создание главного окна
        self.root = tk.Tk()
        # Указание заголовка
        self.root.title("Клиентская часть чата на основе TCP-сокетов")
        # Указание размера окна
        self.root.geometry("850x700")


        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

        self.discovery = ClientDiscovery()

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
        self.ip_entry.insert(0, self.client.host)
        self.ip_entry.grid(row=0, column=1, padx=5, pady=5)

        # Порт
        ttk.Label(connection_frame, text="Порт:").grid(row=0, column=2, padx=5, pady=5)
        self.port_entry = ttk.Entry(connection_frame, width=10)
        self.port_entry.insert(0, self.client.port)
        self.port_entry.grid(row=0, column=3, padx=5, pady=5)

        # Логин
        ttk.Label(connection_frame, text="Логин:").grid(row=0, column=4, padx=5, pady=5)
        self.login_entry = ttk.Entry(connection_frame, width=20)
        self.login_entry.insert(0, self.client.username)
        self.login_entry.grid(row=0, column=5, padx=5, pady=5)

        # Кнопка подключения
        self.connect_button = ttk.Button(connection_frame, text="Подключиться", command=self.start_client_in_thread)
        self.connect_button.grid(row=0, column=6, padx=5, pady=5)

        # Кнопка отключения
        self.disconnect_button = ttk.Button(connection_frame, text="Отключиться", command=self.stop_client, state="disabled")
        self.disconnect_button.grid(row=0, column=7, padx=5, pady=5)

        # ========== Панель интерфейсов (НОВАЯ) ==========
        interfaces_frame = ttk.LabelFrame(self.root, text="Сетевые интерфейсы", padding=5)
        interfaces_frame.pack(fill=tk.X, padx=10, pady=5)

        self.interfaces_listbox = tk.Listbox(interfaces_frame, height=3, font=("Arial", 10))
        self.interfaces_listbox.pack(fill=tk.X)
        self.interfaces_listbox.bind('<<ListboxSelect>>', self.on_interface_select)

        # ========== Панель серверов (НОВАЯ) ==========
        discovery_frame = ttk.LabelFrame(self.root, text="Найденные серверы", padding=5)
        discovery_frame.pack(fill=tk.X, padx=10, pady=5)

        self.server_listbox = tk.Listbox(discovery_frame, height=3, font=("Arial", 10))
        self.server_listbox.pack(fill=tk.X, side=tk.LEFT, expand=True)
        self.server_listbox.bind('<<ListboxSelect>>', self.on_server_select)
        self.server_listbox.bind('<Double-Button-1>', self.on_server_double_click)

        self.discover_button = ttk.Button(discovery_frame, text="Найти серверы", command=self.start_discovery)
        self.discover_button.pack(side=tk.RIGHT, padx=5)

        # ========== Основная область ==========
        main_panel = ttk.Frame(self.root)
        main_panel.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # ----- Колонка - сообщения пользователей -----
        messages_frame = ttk.LabelFrame(main_panel, text="Сообщения пользователей", padding=5)
        messages_frame.pack(fill=tk.BOTH, expand=True)

        # Область для сообщений пользователей
        self.messages_area = tk.Listbox(messages_frame, font=("Arial", 10))
        self.messages_area.pack(fill=tk.BOTH, expand=True)


        # ========== Панель задач (индивидуальный вариант) ==========
        task_frame = ttk.LabelFrame(self.root, text="Задание: Найти сумму и наименьший делитель", padding=10)
        task_frame.pack(fill=tk.X, padx=10, pady=5)

        ttk.Label(task_frame, text="Числа (через запятую):").pack(side=tk.LEFT)
        self.task_entry = ttk.Entry(task_frame, width=40)
        self.task_entry.pack(side=tk.LEFT, padx=5)
        self.task_entry.insert(0, "4,6,8") # Значение для примера
        self.task_entry.config(state="disabled")

        self.task_button = ttk.Button(task_frame, text="Выполнить", command=self.send_task)
        self.task_button.pack(side=tk.LEFT, padx=5)
        self.task_button.config(state="disabled") # Пока нет подключения - выключено


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

        if self.client.is_connected():
            self.messages_area.insert(tk.END, "[СИСТЕМА] Вы уже подключены к серверу.")
            return

        username = self.login_entry.get().strip()

        if not username:
            self.messages_area.insert(tk.END, "[ОШИБКА] Введите логин!")
            return

        save_client_username(username)

        self.connect_button.config(state="disabled")
        self.messages_area.insert(tk.END, "Подключение к серверу...")

        thread = threading.Thread(target=self.client.connect, args=(username, ))
        thread.daemon = True
        thread.start()

    def send_message(self):
        """Отправка сообщений"""

        if not self.client.is_connected():
            self.messages_area.insert(tk.END, "[ОШИБКА] Нет соединения с сервером.")
            return

        text = self.message_entry.get().strip()

        if text:
            success = self.client.send_message(text)

            if success:
                self.message_entry.delete(0, tk.END)
            else:
                self.message_entry.insert(tk.END, "[ОШИБКА] Не удалось отправить сообщение.")


    def update_messages(self, text):
        self.root.after(0, lambda: self.messages_area.insert(tk.END, text))

    def on_connected(self):
        def _update():
            self.message_entry.config(state="normal")
            self.send_button.config(state="normal")
            self.login_entry.config(state="disabled")
            self.ip_entry.config(state="disabled")
            self.port_entry.config(state="disabled")
            self.task_button.config(state="normal")
            self.task_entry.config(state="normal")
            self.connect_button.config(state="disabled")
            self.disconnect_button.config(state="normal")
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
            self.task_button.config(state="disabled")
            self.task_entry.config(state="disabled")
            self.connect_button.config(state="normal")
            self.disconnect_button.config(state="disabled")
        self.root.after(0, _update)

    def send_task(self):
        """Отправка данных на сервер для выполнения задачи"""
        data = self.task_entry.get().strip()
        if not data:
            self.messages_area.insert(tk.END, "[ОШИБКА] Введите числа для задачи!")
            return

        # Вызываем метод из network.py
        success = self.client.send_task("TASK6", data)

        if success:
            # Отображаем в чате, что мы отправили
            self.messages_area.insert(tk.END, f"Вы отправили задачу: TASK6|{data}")
            self.messages_area.see(tk.END)  # Прокрутка вниз
        else:
            self.messages_area.insert(tk.END, "[ОШИБКА] Не удалось отправить задачу.")

    def on_closing(self):
        self.client.disconnect()
        self.root.destroy()


    def run(self):
        self.root.mainloop()

    def stop_client(self):
        """Ручное отключение от сервера"""
        self.client.disconnect()


    def start_discovery(self):
        """Запуск поиска серверов при нажатии на кнопку"""
        self.interfaces_listbox.delete(0, tk.END)
        self.server_listbox.delete(0, tk.END)
        self.server_listbox.insert(tk.END, "Поиск серверов...")

        # Получаем интерфейсы
        interfaces = self.discovery.get_interfaces()
        for ip in interfaces:
            self.interfaces_listbox.insert(tk.END, ip)

        # Выбираем первый интерфейс и запускаем поиск
        if interfaces:
            self.interfaces_listbox.selection_set(0)
            self._run_search(interfaces[0])


    def _run_search(self, interface_ip):
        """Запускает поиск в отдельном потоке, чтобы не зависал GUI"""

        def task():
            servers = self.discovery.discovery_server(interface_ip)

            def update_gui():
                self.server_listbox.delete(0, tk.END)
                if not servers:
                    self.server_listbox.insert(tk.END, "Серверы не найдены")
                for srv in servers:
                    # Формат: "IP | Описание задачи"
                    self.server_listbox.insert(tk.END, f"{srv['ip']} | {srv['task']}")

            self.root.after(0, update_gui)

        threading.Thread(target=task, daemon=True).start()


    def on_interface_select(self, event):
        """При клике на интерфейс — перезапускаем поиск"""
        selection = self.interfaces_listbox.curselection()
        if selection:
            ip = self.interfaces_listbox.get(selection[0])
            self.server_listbox.delete(0, tk.END)
            self.server_listbox.insert(tk.END, "Поиск серверов...")
            self._run_search(ip)


    def on_server_select(self, event):
        """При клике на найденный сервер — подставляем его IP в поле ввода"""
        selection = self.server_listbox.curselection()
        if selection:
            text = self.server_listbox.get(selection[0])
            if "|" in text:
                ip = text.split("|")[0].strip()
                self.ip_entry.delete(0, tk.END)
                self.ip_entry.insert(0, ip)


    def on_server_double_click(self, event):
        self.on_server_select(event) # Сначала подставляем IP

        if not self.client.is_connected():
            self.start_client_in_thread() # Потом сразу подключаемся по TCP
