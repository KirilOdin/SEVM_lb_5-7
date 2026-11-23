import socket
import threading
from src.common import setup_logger, load_server_config
from src.server.tasks import TaskExecutor
# from pathlib import Path

# Корень проекта
# BASE_DIR = Path(__file__).resolve().parent.parent

class ChatServer:
    def __init__(self, on_message=None, on_user_update=None):
        # Конфиги сервера по умолчанию из файла
        self.host, self.port = load_server_config()

        # Создание и настройка логгера для сервера
        self.logger = setup_logger("ServerLogger", "logs/server.log", add_console=True)

        # Словарь для клиентов
        self.clients = {}
        # Блокировка потока
        self.lock = threading.Lock()

        # Колбэки для GUI
        self.on_message = on_message
        self.on_user_update = on_user_update

        # По умолчанию пуст, ждёт запуска в start()
        self.server_socket = None
        self.is_running = False


    def start(self, host=None, port=None):
        """Запуск сервера через серверный сокет"""
        if host:
            self.host = host
        if port:
            self.port = int(port)

        # Сетевой сокет
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)


        # ДОБАВИТЬ ЭТО:
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        # Привязка сокета к IP и порту
        self.server_socket.bind((self.host, self.port))

        # Для начала "прослушивания"
        self.server_socket.listen()
        self.is_running = True

        start_msg = f"Сервер запущен на адресе {self.host} : {self.port}"
        self.logger.info(start_msg)

        # Дублирование сообщения для gui
        self._notify_gui(start_msg)

        # Прослушивание сокета на "постоянной" основе
        while self.is_running:
            try:
                # Принятие запроса на подключение от клиента
                client_socket, address = self.server_socket.accept()

                self.logger.info(f"Обнаружен новый клиент с адресом {address}.")
                self._notify_gui(f"Обнаружен новый клиент с адресом {address}.")

                # Создание потока для клиента, обработка потока через handle_client()
                thread = threading.Thread(target=self.handle_client, args=(client_socket, address))

                # Работа потока в фоне
                thread.daemon = True
                thread.start()

            except OSError as e:
                self.logger.info(f"Принудительное завершение работы сокета: {e}")

                # Дублирование сообщения для gui
                self._notify_gui(f"Принудительное завершение работы сокета: {e}")
                break



    def handle_client(self, client_socket, address):
        """Взаимодействие с клиентом, обработка входящих данных"""
        username = None
        try:
            while self.is_running:
                # Буфер данных, получаемых от клиента
                data = client_socket.recv(1024)


                if not self.is_running:
                    break

                # Отключение клиента в случае отсутствия данных
                # TODO: Нужно что-то писать в логах?
                if not data:
                    self.logger.info("Закрытие соединения.")
                    # Дублирование сообщения для gui
                    self._notify_gui("Закрытие соединения.")
                    break

                message = data.decode().strip()

                parts = message.split("|")
                if len(parts) < 2:
                    continue

                command = parts[0]
                value = parts[1]

                # TODO: Заменить if на switch (match case)?
                # 1. Аутентификация

                if command == "LOGIN":
                    username = value

                    # Блокировка потока для внесения изменений в словарь клиентов
                    with self.lock:
                        old_sockets = [sock for sock, name in self.clients.items() if name == username]

                        for old_sock in old_sockets:
                            try:
                                old_sock.close()
                            except Exception:
                                pass
                            del self.clients[old_sock]
                            self.logger.info(f"Принудительно закрыта старая сессия пользователя {username}")

                        self.clients[client_socket] = username

                    login_msg = f"{username} вошёл в чат!"
                    self.logger.info(login_msg)

                    # Дублирование сообщения для gui
                    self._notify_gui(login_msg)

                    # Обновление списка клиентов через Callback в GUI
                    if self.on_user_update:
                        self.on_user_update("add", username)

                    # Оповещение всех о новом подключении
                    self.broadcast(f"SERVER|{username} присоединился к чату!")

                # 2. Отправка сообщения
                elif command == "MESSAGE":
                    text = value
                    self.logger.info(f"[MESSAGE] {username} : {text}")

                    # Дублирование сообщения для gui
                    self._notify_gui(f"[MESSAGE] {username} : {text}")

                    self.broadcast(f"{username}|{text}")

                elif command.startswith("TASK"):
                    self.logger.info(f"Задача от клиента {username}: {command}")

                    ans = TaskExecutor.execute(command, value)

                    try:
                        client_socket.sendall(f"SERVER|Результат: {ans}".encode())

                    except Exception as e:
                        self.logger.error(f"Не удалось отправить результат: {e}")


        except Exception as e:
            self.logger.error(f"Ошибка при работе с клиентом {address} : {e}")

            # Дублирование сообщения для gui
            self._notify_gui(f"Ошибка при работе с клиентом {address} : {e}")
        finally:
            self.disconnect_client(client_socket, username)


    def disconnect_client(self, client_socket, username):
        """Отключение клиента от сервера"""
        with self.lock:
            if client_socket in self.clients:
                del self.clients[client_socket]

            is_still_connected = username in self.clients.values()
        client_socket.close()

        if username and not is_still_connected:
            self.logger.info(f"Пользователь {username} отключился!")

            # Дублирование сообщения для gui
            self._notify_gui(f"Пользователь {username} отключился!")

            if self.on_user_update:
                self.on_user_update("remove", username)
            self.broadcast(f"SERVER|{username} покинул чат")


    def broadcast(self, message):
        """Отправка сообщения всем клиентам"""
        # Блокировка изменений на время обработки словаря
        with self.lock:
            for client in list(self.clients.keys()):
                try:
                    client.sendall(message.encode())
                except Exception as e:
                    self.logger.info(f"Принудительное отключение клиентского сокета: {e}")
                    if client in self.clients:
                        del self.clients[client]
                    # Отключаем клиентский сокет при неудачной отправке сообщения
                    client.close()


    def _notify_gui(self, text):
        """Отправка сообщений/уведомление в интерфейс (при его наличии)"""
        if self.on_message:
            self.on_message(text)


    def stop(self):
        """Остановка работы сервера"""
        self.is_running = False
        if self.server_socket:
            try:
                self.server_socket.shutdown(socket.SHUT_RDWR)
            except OSError:
                pass
            self.server_socket.close()
            self.server_socket = None

        with self.lock:
            for client_socket in list(self.clients.keys()):
                try:
                    client_socket.shutdown(socket.SHUT_RDWR)
                    client_socket.close()
                except Exception:
                    pass
                try:
                    client_socket.close()
                except Exception:
                    pass

            self.clients.clear()

        self.logger.info("Сервер остановлен.")
        # Дублирование сообщения для gui
        self._notify_gui("Сервер остановлен.")

        if self.on_user_update:
            self.on_user_update("clear", "")