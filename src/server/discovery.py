import socket
import threading
from src.common import load_server_discovery_config, setup_logger

class ServerDiscovery:
    def __init__(self, on_message=None):
        # Конфиги сервера по умолчанию из файла
        self.host, self.port, self.timeout = load_server_discovery_config()

        # Создание и настройка логера для сервера
        self.logger = setup_logger("ServerDiscoveryLogger", "logs/server_discovery.log", add_console=True)

        # Колбеки для GUI
        self.on_message = on_message

        self.server_udp_socket = None
        self.is_running = False
        # self.thread = None

    def start(self,host=None, port=None):
        """Запуск сервера через серверный сокет"""
        if host:
            self.host = host
        if port:
            self.port = int(port)

        # Сетевой сокет
        self.server_udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.server_udp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)


        # Привязка сокета к IP и порту
        self.server_udp_socket.bind((self.host, self.port))

        self.server_udp_socket.settimeout(self.timeout)

        self.is_running = True

        start_msg = f"Слушатель обнаружения запущен на адресе {self.host} : {self.port}"
        self.logger.info(start_msg)

        # Дублирование сообщения для gui
        self._notify_gui(start_msg)


        while self.is_running:
            try:
                # Ждем данные от клиента
                data, client_addr = self.server_udp_socket.recvfrom(1024)

                # Если пришел запрос на обнаружение
                if data.decode() == "DISCOVER":
                    self.logger.info(f"Получен DISCOVER от {client_addr}")

                    # Передаем не просто SERVER, а с инфой о нашей задаче
                    response = "SERVER|TASK6| Вычисление суммы и наименьшего делителя + чат"

                    self.server_udp_socket.sendto(response.encode(), client_addr)
                    self._notify_gui(f"[UDP] Отправлен ответ на {client_addr}")
            except socket.timeout:
                continue
            except OSError:
                break
            except Exception as e:
                if self.is_running:
                    self.logger.error(f"Ошибка UDP: {e}")
                    self._notify_gui(f"[UDP] Ошибка: {e}")


                # client_udp_socket, address = self.server_udp_socket.accept()
                #
                # self.logger.info(f"Обнаружен новый клиент с адресом {address}.")
                # self._notify_gui(f"Обнаружен новый клиент с адресом {address}.")
                #
                # # Создание потока для клиента, обработка потока через handle_client()
                # thread = threading.Thread(target=self._listen)
                #
                # thread.daemon = True
                # thread.start()


    def _notify_gui(self, text):
        """Отправка сообщений/уведомление в интерфейс (при его наличии)"""
        if self.on_message:
            self.on_message(text)


    def _listen(self):
        try:
            self.server_udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.server_udp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server_udp_socket.bind((self.host, self.port))
            self.server_udp_socket.settimeout(None)
        except Exception as e:
            if self.is_running:
                self._notify_gui(f"Ошибка при работе с UDP-слушателем: {e}")

    def stop(self):
        """Остановка работы UDP-слушателя"""
        self.is_running = False
        if self.server_udp_socket:
            try:
                self.server_udp_socket.close()
            except Exception:
                pass
            self.server_udp_socket = None

        self.logger.info("UDP-слушатель остановлен.")
        self._notify_gui("UDP-слушатель остановлен.")




