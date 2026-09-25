import psycopg2
import pandas as pd
from config import DB_CONFIG_OLTP, DB_CONFIG_WAREHOUSE
from src.utils.logger import get_logger

logger = get_logger(__name__)


# Extract: mapping product & seller dari warehouse
# =================================================

logger.info("Ambil mapping product & seller dari warehouse")

conn_wh = psycopg2.connect(**DB_CONFIG_WAREHOUSE)
cur_wh = conn_wh.cursor()

cur_wh.execute("SELECT product_id, product_key FROM dw.dim_products;")
product_map = dict(cur_wh.fetchall())
logger.info(f"Total mapping product: {len(product_map):,}")

cur_wh.execute("SELECT seller_id, seller_key FROM dw.dim_sellers;")
seller_map = dict(cur_wh.fetchall())
logger.info(f"Total mapping seller: {len(seller_map):,}")


# Extract: order_items + orders dari OLTP
# ========================================

logger.info("Baca data order_items + orders dari OLTP")

conn_oltp = psycopg2.connect(**DB_CONFIG_OLTP)
cur_oltp = conn_oltp.cursor()

cur_oltp.execute("""
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
    WHERE o.order_purchase_timestamp IS NOT NULL;
""")

rows_raw = cur_oltp.fetchall()
logger.info(f"Total order items: {len(rows_raw):,}")

cur_oltp.close()
conn_oltp.close()


# Transform: lookup product_key, seller_key, date_key
# ===================================================

logger.info("Transform data")

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


# Load: insert ke dw.fact_order_items
# ===================================

logger.info("Insert ke dw.fact_order_items")

cur_wh.executemany("""
    INSERT INTO dw.fact_order_items
    (order_id, order_item_id, product_key, seller_key,
     date_key, order_status, price, freight_value)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    ON CONFLICT (order_id, order_item_id) DO NOTHING;
""", rows_final)

conn_wh.commit()
logger.info(f"Selesai. {len(rows_final):,} baris diproses")

cur_wh.close()
conn_wh.close()