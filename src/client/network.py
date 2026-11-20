import socket
import threading
from src.common.logger_setup import setup_logger
from src.common.config_loader import load_client_config

class ChatClient:
    def __init__(self, on_message=None, on_connected=None, on_disconnected=None):
        # Конфиги клиента по умолчанию из файла
        self.host, self.port, self.username = load_client_config()

        # TODO: Оставить файл лога один для "всех клиентов" или
        #  спрашивать логин, который будет "хэшироваться"
        #  (преобразовываться) как префикс имени ClientLogger?
        # Создание и настройка логгера для клиента
        self.logger = setup_logger("ClientLogger","logs/client.log")

        # Колбэки для GUI
        self.on_message = on_message
        self.on_connected = on_connected
        self.on_disconnected = on_disconnected

        # По умолчанию пуст, ждёт запуска в connect()
        self.client_socket = None
        self.is_running = False

    def connect(self, username):
        """Подключение к серверу"""
        # Сетевой сокет
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        try:
            # Подключение к серверу через IP и порт
            self.client_socket.connect((self.host, self.port))
            self.is_running = True

            # 1. Аутентификация на сервере
            self.client_socket.sendall(f"LOGIN|{username}".encode("utf-8"))
            self.logger.info(f"Успешное подключение к серверу {self.host}:{self.port} под именем {username}!")

            # Дублирование сообщения для gui
            self._notify_gui(f"Успешное подключение к серверу {self.host}:{self.port} под именем {username}!")

            # Информация для GUI (колбек), передаваемая при успешном подключении
            if self.on_connected:
                self.on_connected()

            # Поток для прослушивания входящих сообщений
            thread = threading.Thread(target=self.receive_messages)

            # Работа потока в фоне
            thread.daemon = True
            thread.start()

        except Exception as e:
            self.logger.error(f"Не удалось установить соединение: {e}")
            self._notify_gui(f"[ОШИБКА] Не удалось подключиться: {e}")
            self.disconnect()

    def receive_messages(self):
        """Получение сообщений от сервера и их дальнейшая обработка"""
        try:
            while self.is_running:
                # Буфер данных, получаемых от клиента
                data = self.client_socket.recv(1024)

                # Отключение клиента в случае отсутствия данных
                if not data:
                    self.logger.info("Сервер разорвал соединение.")
                    # Дублирование сообщения для gui
                    self._notify_gui("Сервер разорвал соединение.")
                    break

                message = data.decode().strip()

                # Сообщение от сервера
                if message.startswith("SERVER|"):
                    text = message.split("|", 1)[1]
                    self.logger.info(f"Система: {text}")
                    self._notify_gui(text)

                # Сообщение от другого(-их) клиента(-ов)
                else:
                    # Обычное сообщение от другого пользователя
                    self.logger.info(f"Получено: {message}")

                    # Дублирование сообщения для gui
                    self._notify_gui(message)



        except Exception as e:
            if self.is_running:
                self.logger.info(f"Ошибка при получении сообщения: {e}")

                # Дублирование сообщения для gui
                self._notify_gui(f"Ошибка при получении сообщения: {e}")
        finally:
            self.disconnect()


    def send_message(self, text):
        """Отправка сообщения на сервер"""
        if not self.is_running or not self.client_socket:
            return False

        try:
            self.client_socket.sendall(f"MESSAGE|{text}".encode())
            return True
        except Exception as e:
            self.logger.error(f"Ошибка при отправке: {e}")
            return False


    def disconnect(self):
        """Отключение от сервера"""
        self.is_running = False
        if self.client_socket:
            try:
                self.client_socket.close()
            except Exception as e:
                self.logger.info(f"Ошибка при закрытии сокета: {e}")
                pass

            finally:
                self.client_socket = None

            self.logger.info("Отключено от сервера.")

            # Дублирование сообщения для gui
            self._notify_gui("Отключено от сервера.")

            if self.on_disconnected:
                self.on_disconnected()

    def _notify_gui(self, text):
        """Отправка сообщений/уведомление в интерфейс (при его наличии)"""
        if self.on_message:
            self.on_message(text)

    def send_task(self, command, data_string):
        """Отправка команды на сервер (например, TASK1|данные)"""
        if not self.is_running or not self.client_socket:
            return False
        try:
            message = f"{command}|{data_string}"
            self.client_socket.sendall(message.encode())
            return True
        except Exception as e:
            self.logger.error(f"Ошибка при отправке задачи: {e}")
            return False


    def is_connected(self):
        """Возвращает True, если соединение активно"""
        return self.is_running and self.client_socket is not None