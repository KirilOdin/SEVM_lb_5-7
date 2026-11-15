import socket
import threading
import tkinter as tk
from tkinter import ttk
from server_params import HOST, PORT

clients = {}
lock = threading.Lock()

ip_entry = None
port_entry = None
users_listbox = None
messages_area = None


def create_gui():

    global ip_entry, port_entry, users_listbox, messages_area

    window = tk.Tk()

    window.title("Серверная часть чата на основе TCP-сокетов")

    window.geometry("800x600")

    connection_frame = ttk.LabelFrame(window, text="Настройки сервера", padding=10)
    connection_frame.pack(fill=tk.X, padx=10, pady=5)
    # IP адрес
    ttk.Label(connection_frame, text="IP-адрес:").grid(row=0, column=0, padx=5, pady=5)
    ip_entry = ttk.Entry(connection_frame, width=20)
    ip_entry.insert(0, "0.0.0.0")
    ip_entry.grid(row=0, column=1, padx=5, pady=5)

    # Порт
    ttk.Label(connection_frame, text="Порт:").grid(row=0, column=2, padx=5, pady=5)
    port_entry = ttk.Entry(connection_frame, width=15)
    port_entry.insert(0, "12345")
    port_entry.grid(row=0, column=3, padx=5, pady=5)

    # Кнопки
    start_button = ttk.Button(connection_frame, text="Запустить сервер", width=30, command=start_server_in_thread)
    start_button.grid(row=0, column=4, padx=5, pady=5)
    stop_button = ttk.Button(connection_frame, text="Остановить сервер", width=30)
    stop_button.grid(row=0, column=5, padx=5, pady=5)


    # ========== Основная область (две колонки) ==========
    main_panel = ttk.Frame(window)
    main_panel.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
    # ----- Левая колонка - пользователи -----
    users_frame = ttk.LabelFrame(main_panel, text="Активные пользователи", padding=5)
    users_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(5, 5))
    # Список пользователей
    users_listbox = tk.Listbox(users_frame, height=15, font=("Arial", 10))
    users_listbox.pack(fill=tk.BOTH, expand=True)
    # ----- Правая колонка - сообщения пользователей -----
    messages_frame = ttk.LabelFrame(main_panel, text="Сообщения пользователей", padding=5)
    messages_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5, 5))
    # Область для сообщений пользователей
    messages_area = tk.Listbox(messages_frame, width=50, height=15,font=("Arial", 10))
    messages_area.pack(fill=tk.BOTH, expand=True)

    window.mainloop()


def start_server_in_thread():
    # Получаем значения из полей ввода
    ip = ip_entry.get() # Получаем IP из поля
    port = port_entry.get() # Получаем порт из поля
    # Создаём поток путем создания экземпляра класса Thread
    # Исполняемая функция start_server
    thread = threading.Thread(target=start_server, args=(ip, port))
    # Переводим поток в фоновый режим
    thread.daemon = False
    # Запускаем поток
    thread.start()


def start_server(ip, port):
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((str(ip), int(port)))

    server.listen()

    print(f"Сервер запущен на адресе {ip} : {port}")

    while True:
        client_socket, address = server.accept()

        thread = threading.Thread(target=handle_client, args=(client_socket, address))

        thread.daemon = True

        thread.start()


def handle_client(client_socket, address):
    global users_listbox, messages_area

    messages_area.insert(messages_area.size(), f"Обнаружен новый клиент с адресом {address}.")
    print(f"Обнаружен новый клиент с адресом {address}!")

    username = None

    try:
        while True:
            data = client_socket.recv(1024)

            if not data:
                break

            message = data.decode().strip()

            parts = message.split("|")

            command = parts[0]

            if command == "LOGIN":
                username = parts[1]
                with lock:
                    clients[client_socket] = username

                print(f"{username} вошёл в чат!")
                messages_area.insert(messages_area.size(), f"Имя пользователя {username}.")
                broadcast(f"SERVER|{username} присоединился к чату")

            elif command == "MESSAGE":
                text = parts[1]
                print(f"[MESSAGE] {username}: {text}")
                broadcast(f"{username}|{text}")
                messages_area.insert(messages_area.size(), f"[MESSAGE] {username}: {text}")

    except Exception as e:
        print(f"[ERROR] {e}")


def broadcast(message):
    with lock:
        for client in clients:
            try:
                client.sendall(message.encode())
            except:
                client.close()




def stop_server():
    pass
