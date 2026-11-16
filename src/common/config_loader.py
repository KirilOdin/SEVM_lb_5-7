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
            'server_port': '12345'
        }
        config_path.parent.mkdir(parents=True, exist_ok=True)
        with open(config_path, 'w') as configfile:
            config.write(configfile)
    else:
        config.read(config_path)

    return config["Default Settings"]["server_ip"], int(config["Default Settings"]["server_port"])


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
