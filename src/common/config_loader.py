import configparser
import os
from pathlib import Path

# Корень проекта
BASE_DIR = Path(__file__).resolve().parent.parent.parent


def load_client_config():
    config = configparser.ConfigParser()

    # config_path = "config/client_config.ini"
    config_path = BASE_DIR / "config" / "client_config.ini"

    if not os.path.exists(config_path):
        config["Default Settings"] = {
            'server_ip': '127.0.0.1',
            'server_port': '12345',
            'username': 'Александр Астафьев',
        }
        config_path.parent.mkdir(parents=True, exist_ok=True)
        with open(config_path, 'w') as configfile:
            config.write(configfile)
    else:
        config.read(config_path)

    host = config["Default Settings"]["server_ip"]
    port = int(config["Default Settings"]["server_port"])
    username = config["Default Settings"].get("username", "Новый пользователь")

    return host, port, username


def save_client_username(username):
    """Сохраняет логин пользователя в конфиг-файл"""
    config = configparser.ConfigParser()
    config_path = BASE_DIR / "config" / "client_config.ini"

    # Читаем текущий файл (если он есть)
    if config_path.exists():
        config.read(config_path, encoding='utf-8')

    if "Default Settings" not in config:
        config["Default Settings"] = {}

    # Обновляем только логин
    config["Default Settings"]["username"] = username

    # Записываем обратно
    with open(config_path, 'w', encoding='utf-8') as configfile:
        config.write(configfile)

def load_server_config():
    config = configparser.ConfigParser()

    # config_path = "config/server_config.ini"
    config_path = BASE_DIR / "config" / "server_config.ini"

    if not os.path.exists(config_path):
        config["Default Settings"] = {
            'server_ip': '0.0.0.0',
            'server_port': '12345'
        }
        config_path.parent.mkdir(parents=True, exist_ok=True)
        with open(config_path, 'w') as configfile:
            config.write(configfile)
    else:
        config.read(config_path)

    return config["Default Settings"]["server_ip"], int(config["Default Settings"]["server_port"])
