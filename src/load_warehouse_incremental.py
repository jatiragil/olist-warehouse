import os
import sys
import glob
import pandas as pd
import psycopg2
from config import DB_CONFIG_OLTP, DB_CONFIG_WAREHOUSE
from src.utils.logger import get_logger
from src.utils.validation import validate_rows

logger = get_logger(__name__)

BATCH_DIR = "data/batches"


def get_watermark(cur, table_name):
    """Ambil batch terakhir dari watermark."""
    cur.execute(
        "SELECT last_batch FROM dw.etl_watermark WHERE table_name = %s",
        (table_name,),
    )
    result = cur.fetchone()
    return result[0] if result else None


def get_next_batch(batch_dir, last_batch):
    """Cari batch berikutnya setelah watermark."""
    files = sorted(glob.glob(os.path.join(batch_dir, "*.csv")))
    batches = [os.path.basename(f).replace(".csv", "") for f in files]

    if last_batch is None:
        return batches[0] if batches else None

    # Cari yang setelah last_batch
    try:
        idx = batches.index(last_batch)
        return batches[idx + 1] if idx + 1 < len(batches) else None
    except ValueError:
        # last_batch tidak ada di daftar → cari yang lebih besar
        for b in batches:
            if b > last_batch:
                return b
        return None


def update_watermark(cur, table_name, batch_name):
    """Update watermark."""
    cur.execute("""
        UPDATE dw.etl_watermark
        SET last_batch = %s, last_loaded_at = CURRENT_TIMESTAMP
        WHERE table_name = %s
    """, (batch_name, table_name))


def load_fact_orders_batch():
    """Load fact_orders untuk batch berikutnya."""
    logger.info("=== Load fact_orders (incremental) ===")

    # Koneksi ke warehouse
    conn_wh = psycopg2.connect(**DB_CONFIG_WAREHOUSE)
    conn_wh.autocommit = False
    cur_wh = conn_wh.cursor()

    # 1. Baca watermark
    last_batch = get_watermark(cur_wh, "orders")
    logger.info(f"Watermark orders: {last_batch or '(belum ada)'}")

    # 2. Cari batch berikutnya
    batch_dir = os.path.join(BATCH_DIR, "orders")
    next_batch = get_next_batch(batch_dir, last_batch)

    if next_batch is None:
        logger.info("Tidak ada batch baru untuk orders. Skip.")
        cur_wh.close()
        conn_wh.close()
        return 0

    logger.info(f"Batch berikutnya: {next_batch}")

    # 3. Ambil order_id dari batch CSV
    batch_file = os.path.join(batch_dir, f"{next_batch}.csv")
    df_batch = pd.read_csv(batch_file)
    order_ids = df_batch["order_id"].tolist()
    logger.info(f"Total order di batch: {len(order_ids):,}")

    # 4. Ambil mapping customer_key
    cur_wh.execute("SELECT customer_unique_id, customer_key FROM dw.dim_customers;")
    customer_map = dict(cur_wh.fetchall())

    # 5. Ambil data dari OLTP
    conn_oltp = psycopg2.connect(**DB_CONFIG_OLTP)
    cur_oltp = conn_oltp.cursor()

    # Pakai IN (...) dengan placeholder
    placeholders = ",".join(["%s"] * len(order_ids))
    cur_oltp.execute(f"""
        WITH items_agg AS (
            SELECT order_id,
                   SUM(price) AS total_item_price,
                   SUM(freight_value) AS total_freight_value,
                   COUNT(*) AS total_items_count
            FROM order_items
            WHERE order_id IN ({placeholders})
            GROUP BY order_id
        ),
        payments_agg AS (
            SELECT order_id,
                   SUM(payment_value) AS total_payment_value,
                   MAX(payment_installments) AS max_payment_installments,
                   STRING_AGG(DISTINCT payment_type, ', ' ORDER BY payment_type) AS payment_type
            FROM order_payments
            WHERE order_id IN ({placeholders})
            GROUP BY order_id
        )
        SELECT
            o.order_id,
            c.customer_unique_id,
            o.order_purchase_timestamp,
            o.order_status,
            ia.total_item_price,
            ia.total_freight_value,
            ia.total_items_count,
            pa.total_payment_value,
            pa.max_payment_installments,
            pa.payment_type
        FROM orders o
        LEFT JOIN customers c ON o.customer_id = c.customer_id
        LEFT JOIN items_agg ia ON o.order_id = ia.order_id
        LEFT JOIN payments_agg pa ON o.order_id = pa.order_id
        WHERE o.order_id IN ({placeholders})
          AND o.order_purchase_timestamp IS NOT NULL;
    """, order_ids * 3)   # 3× karena ada 3 placeholder

    rows_raw = cur_oltp.fetchall()
    logger.info(f"Total baris dari OLTP: {len(rows_raw):,}")

    cur_oltp.close()
    conn_oltp.close()

    # 6. Transform
    rows_final = []
    skipped = 0
    for row in rows_raw:
        (order_id, customer_unique_id, ts, order_status,
         total_item_price, total_freight_value, total_items_count,
         total_payment_value, max_payment_installments, payment_type) = row

        customer_key = customer_map.get(customer_unique_id)
        if customer_key is None:
            skipped += 1
            continue

        date_key = int(pd.to_datetime(ts).strftime("%Y%m%d"))

        rows_final.append((
            order_id, customer_key, date_key, order_status, payment_type,
            total_item_price, total_freight_value, total_payment_value,
            max_payment_installments, total_items_count
        ))

    logger.info(f"Total baris siap insert: {len(rows_final):,}")
    if skipped > 0:
        logger.warning(f"Baris di-skip: {skipped}")

    # 7. Kalau kosong, skip
    if not rows_final:
        logger.warning(f"Tidak ada baris baru untuk batch {next_batch}")
        update_watermark(cur_wh, "orders", next_batch)
        conn_wh.commit()
        cur_wh.close()
        conn_wh.close()
        return 0

    # 8. Validasi
    validate_rows(rows_final, "dw.fact_orders", pk_columns=[0], not_null_columns=[0, 1, 2])

    # 9. Insert
    cur_wh.executemany("""
        INSERT INTO dw.fact_orders
        (order_id, customer_key, date_key, order_status, payment_type,
         total_item_price, total_freight_value, total_payment_value,
         max_payment_installments, total_items_count)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (order_id) DO NOTHING;
    """, rows_final)

    # 10. Update watermark
    update_watermark(cur_wh, "orders", next_batch)

    conn_wh.commit()
    logger.info(f"Selesai batch {next_batch}: {len(rows_final):,} baris")

    cur_wh.close()
    conn_wh.close()
    return len(rows_final)


def load_fact_order_items_batch():
    """Load fact_order_items untuk batch berikutnya."""
    logger.info("=== Load fact_order_items (incremental) ===")

    # Koneksi warehouse
    conn_wh = psycopg2.connect(**DB_CONFIG_WAREHOUSE)
    conn_wh.autocommit = False
    cur_wh = conn_wh.cursor()

    # 1. Baca watermark
    last_batch = get_watermark(cur_wh, "order_items")
    logger.info(f"Watermark order_items: {last_batch or '(belum ada)'}")

    # 2. Cari batch berikutnya
    batch_dir = os.path.join(BATCH_DIR, "order_items")
    next_batch = get_next_batch(batch_dir, last_batch)

    if next_batch is None:
        logger.info("Tidak ada batch baru untuk order_items. Skip.")
        cur_wh.close()
        conn_wh.close()
        return 0

    logger.info(f"Batch berikutnya: {next_batch}")

    # 3. Baca CSV batch → dapat order_id
    batch_file = os.path.join(batch_dir, f"{next_batch}.csv")
    df_batch = pd.read_csv(batch_file)
    order_ids = df_batch["order_id"].tolist()
    logger.info(f"Total order di batch: {len(order_ids):,}")

    # 4. Ambil mapping product_key & seller_key
    cur_wh.execute("SELECT product_id, product_key FROM dw.dim_products;")
    product_map = dict(cur_wh.fetchall())

    cur_wh.execute("SELECT seller_id, seller_key FROM dw.dim_sellers;")
    seller_map = dict(cur_wh.fetchall())

    # 5. Ambil data dari OLTP
    conn_oltp = psycopg2.connect(**DB_CONFIG_OLTP)
    cur_oltp = conn_oltp.cursor()

    placeholders = ",".join(["%s"] * len(order_ids))
    cur_oltp.execute(f"""
        SELECT
            oi.order_id,
            oi.order_item_id,
            oi.product_id,
            oi.seller_id,
            o.order_purchase_timestamp,
            o.order_status,
            oi.price,
            oi.freight_value
        FROM order_items oi
        JOIN orders o ON oi.order_id = o.order_id
        WHERE oi.order_id IN ({placeholders})
          AND o.order_purchase_timestamp IS NOT NULL;
    """, order_ids)

    rows_raw = cur_oltp.fetchall()
    logger.info(f"Total baris dari OLTP: {len(rows_raw):,}")

    cur_oltp.close()
    conn_oltp.close()

    # 6. Transform
    rows_final = []
    skipped = 0
    for row in rows_raw:
        (order_id, order_item_id, product_id, seller_id,
         ts, order_status, price, freight_value) = row

        product_key = product_map.get(product_id)
        if product_key is None:
            skipped += 1
            continue

        seller_key = seller_map.get(seller_id)
        if seller_key is None:
            skipped += 1
            continue

        date_key = int(pd.to_datetime(ts).strftime("%Y%m%d"))

        rows_final.append((
            order_id, order_item_id, product_key, seller_key,
            date_key, order_status, price, freight_value
        ))

    logger.info(f"Total baris siap insert: {len(rows_final):,}")
    if skipped > 0:
        logger.warning(f"Baris di-skip: {skipped}")

    # 7. Kalau kosong, skip
    if not rows_final:
        logger.warning(f"Tidak ada baris baru untuk batch {next_batch}")
        update_watermark(cur_wh, "order_items", next_batch)
        conn_wh.commit()
        cur_wh.close()
        conn_wh.close()
        return 0

    # 8. Validasi
    validate_rows(
        rows_final, "dw.fact_order_items",
        pk_columns=[0, 1],           # composite PK: order_id + order_item_id
        not_null_columns=[0, 1, 2, 3, 4],
    )

    # 9. Insert
    cur_wh.executemany("""
        INSERT INTO dw.fact_order_items
        (order_id, order_item_id, product_key, seller_key,
         date_key, order_status, price, freight_value)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (order_id, order_item_id) DO NOTHING;
    """, rows_final)

    # 10. Update watermark
    update_watermark(cur_wh, "order_items", next_batch)

    conn_wh.commit()
    logger.info(f"Selesai batch {next_batch}: {len(rows_final):,} baris")

    cur_wh.close()
    conn_wh.close()
    return len(rows_final)


if __name__ == "__main__":
    load_fact_orders_batch()