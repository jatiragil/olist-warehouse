import time
from src.utils.retry import retry
from src.utils.logger import get_logger

logger = get_logger(__name__)


# Fungsi yang sengaja gagal 2×, berhasil di ke-3
call_count = 0

@retry(max_attempts=3, delay=2)
def fungsi_gagal():
    global call_count
    call_count += 1
    logger.info(f"Percobaan ke-{call_count}")

    if call_count < 3:
        raise Exception(f"Error sengaja di attempt {call_count}")

    logger.info("Berhasil!")
    return "Sukses"


# Jalankan
if __name__ == "__main__":
    hasil = fungsi_gagal()
    logger.info(f"Hasil akhir: {hasil}")