from src.load_warehouse_incremental import (
    load_fact_orders_batch,
    load_fact_order_items_batch,
)
from src.utils.logger import get_logger

logger = get_logger(__name__)


def run_all():
    """Loop: load fact_orders + fact_order_items per batch."""
    logger.info("=" * 60)
    logger.info("Mulai loop incremental load")
    logger.info("=" * 60)

    batch_count = 0

    while True:
        # Load kedua fact
        rows_orders = load_fact_orders_batch()
        rows_items = load_fact_order_items_batch()

        # Kalau dua-duanya kosong → selesai
        if rows_orders == 0 and rows_items == 0:
            logger.info("Tidak ada batch baru lagi. Selesai.")
            break

        batch_count += 1
        logger.info(f"Batch #{batch_count}: orders={rows_orders}, items={rows_items}")

    logger.info("=" * 60)
    logger.info(f"Total batch diproses: {batch_count}")
    logger.info("=" * 60)


if __name__ == "__main__":
    run_all()