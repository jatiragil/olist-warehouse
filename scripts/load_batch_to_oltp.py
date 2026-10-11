import os
import sys
import pandas as pd
from sqlalchemy import create_engine
from config import OLTP_URL
from src.utils.logger import get_logger
from src.utils.retry import retry

logger = get_logger(__name__)

engine = create_engine(OLTP_URL)

BATCH_DIR = "data/batches"


@retry(max_attempts=3, delay=2)
def load_batch_file(file_path, table_name):
    """Load satu file batch ke tabel OLTP."""
    df = pd.read_csv(file_path)

    df.to_sql(
        table_name,
        engine,
        if_exists="append",   # ← append, bukan replace!
        index=False,
        method="multi",
        chunksize=5000,
    )

    logger.info(f"  {os.path.basename(file_path)} → {table_name}: {len(df):,} baris")


def load_batch_to_oltp(batch_name):
    """
    Load batch (per bulan) ke OLTP.
    
    Args:
        batch_name: Nama batch (format YYYY-MM, misal '2016-09')
    """
    logger.info(f"Load batch {batch_name} ke OLTP")

    # Daftar file batch dan tabel tujuan
    BATCH_FILES = [
        ("orders", "olist_orders_dataset.csv"),
        ("order_items", "olist_order_items_dataset.csv"),
        ("order_payments", "olist_order_payments_dataset.csv"),
        ("order_reviews", "olist_order_reviews_dataset.csv"),
    ]

    total = 0
    for table_name, _ in BATCH_FILES:
        batch_file = os.path.join(BATCH_DIR, table_name, f"{batch_name}.csv")

        # Cek file ada
        if not os.path.exists(batch_file):
            logger.warning(f"  File tidak ada: {batch_file} (skip)")
            continue

        # Load
        load_batch_file(batch_file, table_name)

        # Hitung
        df = pd.read_csv(batch_file)
        total += len(df)

    logger.info(f"Selesai load batch {batch_name}. Total: {total:,} baris")
    return total


if __name__ == "__main__":
    if len(sys.argv) < 2:
        logger.error("Pakai: python -m scripts.load_batch_to_oltp <batch_name>")
        logger.error("Contoh: python -m scripts.load_batch_to_oltp 2016-09")
        sys.exit(1)

    batch_name = sys.argv[1]
    load_batch_to_oltp(batch_name)