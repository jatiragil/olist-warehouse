import os
import glob
import pandas as pd
from src.utils.logger import get_logger

logger = get_logger(__name__)

RAW_DIR = "data/raw"
BATCH_DIR = "data/batches"

# Daftar tabel dan file CSV asli
TABLES = {
    "orders": "olist_orders_dataset.csv",
    "order_items": "olist_order_items_dataset.csv",
    "order_payments": "olist_order_payments_dataset.csv",
    "order_reviews": "olist_order_reviews_dataset.csv",
}


def verify_split():
    """Verifikasi hasil split untuk semua tabel."""

    logger.info("=" * 60)
    logger.info("Verifikasi split CSV")
    logger.info("=" * 60)

    for table_name, filename in TABLES.items():
        logger.info(f"\n📊 Tabel: {table_name}")

        # 1. Baca CSV asli
        source = os.path.join(RAW_DIR, filename)
        df_original = pd.read_csv(source)
        total_original = len(df_original)
        logger.info(f"  CSV asli: {total_original:,} baris")

        # 2. Baca semua batch
        batch_files = sorted(glob.glob(os.path.join(BATCH_DIR, table_name, "*.csv")))
        total_batch = 0
        for f in batch_files:
            df = pd.read_csv(f)
            total_batch += len(df)

        logger.info(f"  Batch: {total_batch:,} baris ({len(batch_files)} file)")

        # 3. Bandingkan
        if total_original == total_batch:
            logger.info(f"  ✅ SAMA!")
        else:
            logger.error(f"  ❌ BEDA! Selisih: {total_batch - total_original}")


if __name__ == "__main__":
    verify_split()