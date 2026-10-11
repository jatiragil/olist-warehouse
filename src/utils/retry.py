import time
import functools
from src.utils.logger import get_logger

logger = get_logger(__name__)


def retry(max_attempts: int = 3, delay: int = 5):
    """
    Decorator untuk retry fungsi yang gagal.

    Args:
        max_attempts: Jumlah percobaan maksimum.
        delay: Jeda antar percobaan (detik).
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(1, max_attempts + 1):
                try:
                    return func(*args, **kwargs)

                except Exception as e:
                    if attempt == max_attempts:
                        logger.error(
                            f"{func.__name__} gagal setelah {max_attempts} percobaan: {e}"
                        )
                        raise

                    logger.warning(
                        f"{func.__name__} gagal (attempt {attempt}/{max_attempts}): {e}"
                    )
                    logger.info(f"Retry dalam {delay} detik...")
                    time.sleep(delay)

        return wrapper
    return decorator