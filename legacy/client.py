import socket
import threading
import sys
import tkinter as tk
from tkinter import ttk


from conn_params import SERVER_HOST, SERVER_PORT

ip_entry = None
port_entry = None
messages_area = None
login_entry = None

message_entry = None
send_button = None
client = None
connected = False


def create_gui():
    # Определяем глобальные переменные, чтобы передавать данные на глобальном уровне
    global ip_entry, port_entry, messages_area, login_entry
    # Создание главного окна
    window = tk.Tk()
    # Указание заголовка
    window.title("Клиентская часть чата на основе TCP-сокетов")
    # Указание размера окна
    window.geometry("800x600")
    # ========== Верхняя панель с настройками ==========
    connection_frame = ttk.LabelFrame(window, text="Настройки сервера", padding=10)
    connection_frame.pack(fill=tk.X, padx=10, pady=5)
    # IP адрес
    ttk.Label(connection_frame, text="IP-адрес:").grid(row=0, column=0, padx=5, pady=5)
    ip_entry = ttk.Entry(connection_frame, width=20)
    ip_entry.grid(row=0, column=1, padx=5, pady=5)
    ip_entry.insert(0, "127.0.0.1")
    ip_entry.grid(row=0, column=1, padx=5, pady=5)
    # Порт
    ttk.Label(connection_frame, text="Порт:").grid(row=0, column=2, padx=5, pady=5)
    port_entry = ttk.Entry(connection_frame, width=15)
    port_entry.insert(0, "12345")
    port_entry.grid(row=0, column=3, padx=5, pady=5)
    # Кнопка подключения
    start_button = ttk.Button(connection_frame, text="Подключиться",
    width=30, command=start_client_in_thread)
    start_button.grid(row=0, column=4, padx=5, pady=5)
    # Логин
    ttk.Label(connection_frame, text="Логин:").grid(row=0, column=5, padx=5,
    pady=5)
    login_entry = ttk.Entry(connection_frame, width=20)
    login_entry.insert(0, "Александр Астафьев")
    login_entry.grid(row=0, column=6, padx=5, pady=5)
    # ========== Основная область ==========
    main_panel = ttk.Frame(window)
    main_panel.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
    # ----- Колонка - сообщения пользователей -----
    messages_frame = ttk.LabelFrame(main_panel, text="Сообщения пользователей", padding=5)
    messages_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5, 5))
    # Область для сообщений пользователей
    messages_area = tk.Listbox(messages_frame, width=50, height=15,
    font=("Arial", 10))
    messages_area.pack(fill=tk.BOTH, expand=True)
    # Запуск приложения
    window.mainloop()
def start_client_in_thread():
    # Получаем значения из полей ввода
    ip = ip_entry.get() # Получаем IP из поля
    port = port_entry.get() # Получаем порт из поля
    # Создаём поток путем создания экземпляра класса Thread
    # Исполняемая функция start_client
    thread = threading.Thread(target=start_client, args=(ip, port))
    # Переводим поток в фоновый режим
    thread.daemon = False
    # Запускаем поток
    thread.start()

def start_client(ip, port):
    # username = input("Введите логин для входа: ")
    username = login_entry.get()

    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        client.connect((str(ip), int(port)))
        client.sendall(f"LOGIN|{username}".encode())

    except Exception as e:
        print(f"Не удалось установить соединение с сервером: {e}")
        return

    thread = threading.Thread(target=receive_messages, args=(client,))
    thread.daemon = True

    thread.start()
    send_message(client)


def receive_messages(client_socket):

    while True:

        try:
            data = client_socket.recv(1024)

            if not data:
                print("Отключение от сервера...")
                break

            message = data.decode().strip()

            print("\n" + message)

            print("> ", end="", flush=True)

        except:
            print("Соединение закрыто.")
            break

    client_socket.close()
    sys.exit()

def send_message(client):
    while True:
        # Ожидаем ввода сообщения пользователя
        message = input()
        # Отправим сообщение на сервер
        client.sendall(f"MESSAGE|{message}".encode())
        print("> ", end="", flush=True)
