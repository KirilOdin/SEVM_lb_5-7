import logging
from pathlib import Path

# Корень проекта
BASE_DIR = Path(__file__).resolve().parent.parent.parent

def setup_logger(name, log_file, log_level=logging.INFO):
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    log_file_path = BASE_DIR / log_file
    handler = logging.FileHandler(log_file_path, encoding='utf-8')
    handler.setFormatter(formatter)
    logger = logging.getLogger(name)
    logger.setLevel(level=log_level)
    logger.addHandler(handler)
    console = logging.StreamHandler()
    console.setFormatter(formatter)
    logger.addHandler(console)
    return logger