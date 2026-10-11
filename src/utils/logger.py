import logging
import os
from logging.handlers import RotatingFileHandler


# Konfigurasi

LOG_DIR = "logs"
LOG_FILE = os.path.join(LOG_DIR, "pipeline.log")
LOG_LEVEL = logging.INFO

# Format log
LOG_FORMAT = "%(asctime)s [%(levelname)s] %(name)s - %(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"


def get_logger(name: str) -> logging.Logger:
    """
    Bikin logger dengan konfigurasi standar.
    
    Args:
        name: Nama logger (biasanya __name__ dari modul yang memanggil)
    
    Returns:
        Logger yang sudah dikonfigurasi
    """
    logger = logging.getLogger(name)
    
    # Kalau logger sudah pernah dikonfigurasi, return saja
    if logger.handlers:
        return logger
    
    logger.setLevel(LOG_LEVEL) #harus dipanggil karena defaultnya adalah "warning"
    
    # Buat folder logs kalau belum ada
    os.makedirs(LOG_DIR, exist_ok=True)
    
    # Formatter
    formatter = logging.Formatter(LOG_FORMAT, datefmt=DATE_FORMAT)
    
    # Handler 1: Console (stdout)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(LOG_LEVEL)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # Handler 2: File (rotating)
    file_handler = RotatingFileHandler(
        LOG_FILE,
        maxBytes=5 * 1024 * 1024,   # 5 MB per file
        backupCount=3,               # simpan 3 file lama
        encoding="utf-8"
    )
    file_handler.setLevel(LOG_LEVEL)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    
    return logger
