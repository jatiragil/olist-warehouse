import os
import pandas as pd
from sqlalchemy import create_engine
from config import OLTP_URL
from src.utils.logger import get_logger
from src.utils.retry import retry

logger = get_logger(__name__)

# Daftar CSV → tabel tujuan
# ==========================

FILES = {
    "olist_customers_dataset.csv": "customers",
    "olist_geolocation_dataset.csv": "geolocation",
    "olist_order_items_dataset.csv": "order_items",
    "olist_order_payments_dataset.csv": "order_payments",
    "olist_order_reviews_dataset.csv": "order_reviews",
    "olist_orders_dataset.csv": "orders",
    "olist_products_dataset.csv": "products",
    "olist_sellers_dataset.csv": "sellers",
    "product_category_name_translation.csv": "category_translation",
}

DATA_DIR = "data/raw"

# Koneksi
# ========

engine = create_engine(OLTP_URL)


# Fungsi load satu CSV ke tabel
# ==============================

@retry(max_attempts=3, delay=1)
def load_csv_to_table(filename, table_name):
    path = os.path.join(DATA_DIR, filename)
    logger.info(f"Loading {filename} → {table_name}")

    df = pd.read_csv(path)
    df.to_sql(
        table_name,
        engine,
        if_exists="replace",
        index=False,
        method="multi",
        chunksize=5000,
    )

    logger.info(f"{table_name}: {len(df):,} baris")


# Main
# ====

if __name__ == "__main__":
    logger.info("Mulai load data ke OLTP")

    for filename, table_name in FILES.items():
        load_csv_to_table(filename, table_name)

    logger.info("Selesai")