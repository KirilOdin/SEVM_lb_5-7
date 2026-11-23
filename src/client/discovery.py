import socket
import threading

from src.common import setup_logger
from src.common.config_loader import load_client_discovery_config

class ClientDiscovery:
    def __init__(self, on_message=None, on_user_update=None):
        self.port, self.timeout, self.username = load_client_discovery_config()

        self.logger = setup_logger("ClientDiscoveryLogger", "logs/client_discovery.log")
        #
        # # Словарь для списка серверов
        # self.server_list = {}
        #
        # #
        # self.selected_server = None
        #
        # # Колбеки для GUI
        # self.on_message = on_message
        # self.on_user_update = on_user_update
        #
        # # По умолчанию пуст, ждёт запуска в connect()
        # self.udp_client_socket = None
        # self.isRunning = False


    def get_interfaces(self):
        """Возвращает список доступный IP интерфейсов"""
        ips = ['127.0.0.1']
        hostname = socket.gethostname()
        try:
            ips.extend(socket.gethostbyname_ex(hostname)[2])
        except Exception as e:
            self.logger.error(f"Не удалось установить соединение: {e}")

        return list(set(ips))

        # udp_client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # udp_client.sendto("Hello, UDP!".encode(), ('192.168.1.100', 12345))
        # udp_client.close()
        #
        # try:
        #     self.udp_client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        #     self.udp_client_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        #     self.udp_client_socket.settimeout(self.timeout)
        #
        #     self.udp_client_socket.connect((self.port, self.port))
        #
        #
        # except Exception as e:
        #     self.logger.error(f"Не удалось установить соединение: {e}")
        #     # self._notify_gui(f"[ОШИБКА] Не удалось подключиться: {e}")
        #     # self.disconnect()



    # def receive_messages(self):
    #     """Получение сообщений от клиента и их дальнейшая обработка"""
    #     udp_server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    #     udp_server.bind(('0.0.0.0', 12345))
    #     data, client_addr = udp_server.recvfrom(1024)
    #     print(f"Получено от {client_addr}: {data.decode()}")


    def discovery_server(self, interface_ip):
        """Получение сообщений от сервера и их дальнейшая обработка"""
        servers = []
        udp_socket = None
        try:
            # Создаём UDP-сокет
            udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

            # Разрешаем широковещательную рассылку
            udp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

            # Устанавливаем таймаут ожидания ответов
            udp_socket.settimeout(self.timeout)

            # Привязываемся к выбранному интерфейсу (если выбран не 0.0.0.0)
            if interface_ip != "0.0.0.0":
                udp_socket.bind((interface_ip, 0))

            # Отправляем запрос на широковещательный адрес
            udp_socket.sendto("DISCOVER".encode(), ('<broadcast>', self.port))
            self.logger.info(f"Отправлен DISCOVER на порт {self.port}")

            # Собираем ответы
            while True:
                try:
                    data, (addr, _) = udp_socket.recvfrom(1024)
                    message = data.decode().split("|")

                    if message[0] == "SERVER":
                        # Извлекаем информацию о задаче (вариант 6)
                        task_info = message[2] if len(message) > 2 else "Нет данных"

                        # Проверяем, чтобы не добавить дубликат
                        if not any(s["ip"] == addr for s in servers):
                            servers.append({
                                "ip": addr,
                                "task": task_info
                            })
                            self.logger.info(f"Найден сервер: {addr} ({task_info})")

                except socket.timeout:
                    break  # Время вышло, прекращаем слушать



        except Exception as e:
            self.logger.error(f"Ошибка при поиске серверов: {e}")
            # Можно вывести сообщение в GUI
        finally:
            if udp_socket:
                udp_socket.close()

        return servers



    # def log_error():
    #     messages_area.insert(tk.END, f"[UDP] Не удалось запустить слушатель:{e}")
    #     messages_area.see(tk.END)
    #     if messages_area:
    #         messages_area.after(0, log_error)

    # def log_message():
    #     messages_area.insert(tk.END, f"[UDP] Слушатель обнаружения запущен на порту {port}")
    #     messages_area.see(tk.END)
    #     if messages_area:
    #         messages_area.after(0, log_message)
    #
    # while udp_running:
    #     try:
    #         # Устанавливаем таймаут, чтобы периодически проверять флаг
    #         udp_running
    #         udp_socket.settimeout(1.0)
    #         # Принимаем данные (блокирующий вызов с таймаутом)
    #         data, client_addr = udp_socket.recvfrom(1024)
    #         # Проверяем, что это запрос на обнаружение
    #         if data.decode() == "DISCOVER":
    #             # Отправляем ответ клиенту
    #             udp_socket.sendto("SERVER".encode(), client_addr)
    #     except socket.timeout:
    #         # Таймаут — просто продолжаем цикл
    #         continue
    #     except Exception as e:
    #         if udp_running:  # Игнорируем ошибки при закрытии
    #             def log_error():
    #                 messages_area.insert(tk.END, f"[UDP] Не удалось запустить слушатель:{e}")
    #                 messages_area.see(tk.END)
    #             if messages_area:
    #                 messages_area.after(0, log_error)
    #         break
    #




    # В GUI!
    # self.server_list <- форма
    #
    # Функция обработки выбора сервера
    # def on_server_select(event):
    #     global selected_server, ip_entry
    #
    #     # Получаем индекс выбранного элемента в списке
    #     selected_server = server_list.curselection()
    #     # Если он определен, то извлекаем данные
    #     if selected_server:
    #         # Получаем элемент списка
    #         selected_text = server_list.get(selected_server[0])
    #         # Проводим валидацию данных. Формат "Сервер: ip:port"
    #         if selected_text.startswith("Сервер: "):
    #             # Убираем "Сервер: " из текста, чтобы оставить только ip и port
    #             ip_port_text = selected_text.replace("Сервер: ", "")
    #             # Извлекаем только ip
    #             ip_text = ip_port_text.split(":")[0]
    #             # Очищаем поле ввоа адреса и заполяем его информацией о выбранном ip
    #             ip_entry.delete(0, len(ip_entry.get()))
    #             ip_entry.insert(0, ip_text)