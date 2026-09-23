import psycopg2
import pandas as pd
from config import DB_CONFIG_OLTP, DB_CONFIG_WAREHOUSE

# =====================================================
# 1. Ambil mapping customer_unique_id → customer_key
#    dari WAREHOUSE
# =====================================================
print("🔍 Ambil mapping customer dari warehouse...")

conn_wh = psycopg2.connect(**DB_CONFIG_WAREHOUSE)
cur_wh = conn_wh.cursor()

cur_wh.execute("SELECT customer_unique_id, customer_key FROM dw.dim_customers;")
customer_map = dict(cur_wh.fetchall())
print(f"   Total mapping customer: {len(customer_map):,}")

# =====================================================
# 2. Ambil data dari OLTP (agregasi + JOIN)
# =====================================================
print("🔍 Baca data orders + agregasi dari OLTP...")

conn_oltp = psycopg2.connect(**DB_CONFIG_OLTP)
cur_oltp = conn_oltp.cursor()

cur_oltp.execute("""
    WITH items_agg AS (
        SELECT
            order_id,
            SUM(price)         AS total_item_price,
            SUM(freight_value) AS total_freight_value,
            COUNT(*)           AS total_items_count
        FROM order_items
        GROUP BY order_id
    ),
    payments_agg AS (
        SELECT
            order_id,
            SUM(payment_value)        AS total_payment_value,
            MAX(payment_installments) AS max_payment_installments,
            STRING_AGG(DISTINCT payment_type, ', ' ORDER BY payment_type) AS payment_type
        FROM order_payments
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
    LEFT JOIN customers c   ON o.customer_id = c.customer_id
    LEFT JOIN items_agg ia  ON o.order_id = ia.order_id
    LEFT JOIN payments_agg pa ON o.order_id = pa.order_id
    WHERE o.order_purchase_timestamp IS NOT NULL;
""")

rows_raw = cur_oltp.fetchall()
print(f"   Total orders: {len(rows_raw):,}")

cur_oltp.close()
conn_oltp.close()

# =====================================================
# 3. Transform: lookup customer_key + buat date_key
# =====================================================
print("🔄 Transform data...")

rows_final = []
for row in rows_raw:
    (order_id, customer_unique_id, ts, order_status,
     total_item_price, total_freight_value, total_items_count,
     total_payment_value, max_payment_installments, payment_type) = row

    # Lookup customer_key dari mapping
    customer_key = customer_map.get(customer_unique_id)

    # Skip kalau customer_key tidak ditemukan (harusnya tidak terjadi)
    if customer_key is None:
        continue

    # Buat date_key format YYYYMMDD
    date_key = int(pd.to_datetime(ts).strftime("%Y%m%d"))

    rows_final.append((
        order_id, customer_key, date_key, order_status,
        payment_type, total_item_price, total_freight_value,
        total_payment_value, max_payment_installments, total_items_count
    ))

print(f"   Total baris siap insert: {len(rows_final):,}")

# =====================================================
# 4. Insert ke dw.fact_orders
# =====================================================
print("💾 Insert ke dw.fact_orders...")

cur_wh.executemany("""
    INSERT INTO dw.fact_orders
    (order_id, customer_key, date_key, order_status, payment_type,
     total_item_price, total_freight_value, total_payment_value,
     max_payment_installments, total_items_count)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    ON CONFLICT (order_id) DO NOTHING;
""", rows_final)

conn_wh.commit()
print(f"✅ Selesai. {len(rows_final):,} baris diproses.")

cur_wh.close()
conn_wh.close()