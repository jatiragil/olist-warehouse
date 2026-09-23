import psycopg2
import pandas as pd
from config import DB_CONFIG_OLTP, DB_CONFIG_WAREHOUSE

# =====================================================
# 1. Ambil mapping dari warehouse
# =====================================================
print("🔍 Ambil mapping product & seller dari warehouse...")

conn_wh = psycopg2.connect(**DB_CONFIG_WAREHOUSE)
cur_wh = conn_wh.cursor()

cur_wh.execute("SELECT product_id, product_key FROM dw.dim_products;")
product_map = dict(cur_wh.fetchall())
print(f"   Total mapping product: {len(product_map):,}")

cur_wh.execute("SELECT seller_id, seller_key FROM dw.dim_sellers;")
seller_map = dict(cur_wh.fetchall())
print(f"   Total mapping seller: {len(seller_map):,}")

# =====================================================
# 2. Baca data order_items + orders dari OLTP
# =====================================================
print("🔍 Baca data order_items + orders dari OLTP...")

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
print(f"   Total order items: {len(rows_raw):,}")

cur_oltp.close()
conn_oltp.close()

# =====================================================
# 3. Transform
# =====================================================
print("🔄 Transform data...")

rows_final = []
skipped = 0

for row in rows_raw:
    (order_id, order_item_id, product_id, seller_id,
     ts, order_status, price, freight_value) = row

    # Lookup product_key
    product_key = product_map.get(product_id)
    if product_key is None:
        skipped += 1
        continue

    # Lookup seller_key
    seller_key = seller_map.get(seller_id)
    if seller_key is None:
        skipped += 1
        continue

    # Konversi timestamp ke date_key
    date_key = int(pd.to_datetime(ts).strftime("%Y%m%d"))

    rows_final.append((
        order_id, order_item_id, product_key, seller_key,
        date_key, order_status, price, freight_value
    ))

print(f"   Total baris siap insert: {len(rows_final):,}")
if skipped > 0:
    print(f"   ⚠️  Baris di-skip: {skipped}")

# =====================================================
# 4. Insert ke dw.fact_order_items
# =====================================================
print("💾 Insert ke dw.fact_order_items...")

cur_wh.executemany("""
    INSERT INTO dw.fact_order_items
    (order_id, order_item_id, product_key, seller_key,
     date_key, order_status, price, freight_value)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    ON CONFLICT (order_id, order_item_id) DO NOTHING;
""", rows_final)

conn_wh.commit()
print(f"✅ Selesai. {len(rows_final):,} baris diproses.")

cur_wh.close()
conn_wh.close()