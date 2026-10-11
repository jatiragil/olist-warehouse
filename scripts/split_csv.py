import os
import pandas as pd
from src.utils.logger import get_logger

logger = get_logger(__name__)

RAW_DIR = "data/raw"
BATCH_DIR = "data/batches"


def split_orders():
    """Pecah olist_orders_dataset.csv per bulan berdasarkan order_purchase_timestamp."""
    logger.info("Mulai pecah orders per bulan")

    source = os.path.join(RAW_DIR, "olist_orders_dataset.csv")
    df = pd.read_csv(source)
    logger.info(f"Total baris asli: {len(df):,}")

    df["order_purchase_timestamp"] = pd.to_datetime(
        df["order_purchase_timestamp"], errors="coerce"
    )
    df = df.dropna(subset=["order_purchase_timestamp"])
    logger.info(f"Setelah buang NULL: {len(df):,}")

    df["bulan"] = df["order_purchase_timestamp"].dt.strftime("%Y-%m")

    grouped = df.groupby("bulan")
    logger.info(f"Total bulan: {len(grouped)}")

    output_dir = os.path.join(BATCH_DIR, "orders")
    os.makedirs(output_dir, exist_ok=True)

    total_saved = 0
    for bulan, group in grouped:
        group_clean = group.drop(columns=["bulan"])
        output_path = os.path.join(output_dir, f"{bulan}.csv")
        group_clean.to_csv(output_path, index=False)
        total_saved += len(group_clean)
        logger.info(f"  orders/{bulan}: {len(group_clean):,} baris")

    logger.info(f"Total orders tersimpan: {total_saved:,}")


def split_by_join(table_name, filename):
    """Pecah tabel yang tidak punya tanggal, dengan JOIN ke orders."""
    logger.info(f"Mulai pecah {table_name} per bulan (via JOIN orders)")

    # Baca tabel yang akan dipecah
    source = os.path.join(RAW_DIR, filename)
    df_table = pd.read_csv(source)
    logger.info(f"Total baris {table_name}: {len(df_table):,}")

    # Baca orders untuk dapat tanggal
    orders_path = os.path.join(RAW_DIR, "olist_orders_dataset.csv")
    df_orders = pd.read_csv(orders_path)
    df_orders["order_purchase_timestamp"] = pd.to_datetime(
        df_orders["order_purchase_timestamp"], errors="coerce"
    )
    df_orders["bulan"] = df_orders["order_purchase_timestamp"].dt.strftime("%Y-%m")

    # Mapping order_id -> bulan
    order_to_bulan = df_orders.set_index("order_id")["bulan"].to_dict()

    # Tambahkan kolom bulan
    df_table["bulan"] = df_table["order_id"].map(order_to_bulan)

    # Buang baris tanpa bulan
    null_count = df_table["bulan"].isna().sum()
    if null_count > 0:
        logger.warning(f"{table_name}: {null_count} baris tanpa bulan (di-skip)")
    df_table = df_table.dropna(subset=["bulan"])

    # Group dan simpan
    grouped = df_table.groupby("bulan")
    logger.info(f"Total bulan: {len(grouped)}")

    output_dir = os.path.join(BATCH_DIR, table_name)
    os.makedirs(output_dir, exist_ok=True)

    total_saved = 0
    for bulan, group in grouped:
        group_clean = group.drop(columns=["bulan"])
        output_path = os.path.join(output_dir, f"{bulan}.csv")
        group_clean.to_csv(output_path, index=False)
        total_saved += len(group_clean)
        logger.info(f"  {table_name}/{bulan}: {len(group_clean):,} baris")

    logger.info(f"Total {table_name} tersimpan: {total_saved:,}")


if __name__ == "__main__":
    split_orders()

    split_by_join(
        "order_items",
        "olist_order_items_dataset.csv"
    )

    split_by_join(
        "order_payments",
        "olist_order_payments_dataset.csv"
    )

    split_by_join(
        "order_reviews",
        "olist_order_reviews_dataset.csv"
    )

    logger.info("Semua split selesai")