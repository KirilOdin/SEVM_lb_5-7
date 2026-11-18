import logging
from pathlib import Path

# Корень проекта
BASE_DIR = Path(__file__).resolve().parent.parent.parent

def setup_logger(name, log_file, log_level=logging.INFO, add_console=False):
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    log_file_path = BASE_DIR / log_file
    log_file_path.parent.mkdir(parents=True, exist_ok=True)

    logger = logging.getLogger(name)

    if not logger.handlers:
        logger.setLevel(level=log_level)

        handler = logging.FileHandler(log_file_path, encoding='utf-8')
        handler.setFormatter(formatter)
        logger.addHandler(handler)

        # Включение вывода в консоль в зависимости от параметра add_console
        if add_console:
            console = logging.StreamHandler()
            console.setFormatter(formatter)
            logger.addHandler(console)

    return logger
