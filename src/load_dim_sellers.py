import psycopg2
from config import DB_CONFIG_OLTP, DB_CONFIG_WAREHOUSE

# =====================================================
# 1. Baca data sellers dari OLTP
# =====================================================
print("🔍 Baca data sellers dari OLTP...")

conn_oltp = psycopg2.connect(**DB_CONFIG_OLTP)
cur_oltp = conn_oltp.cursor()

cur_oltp.execute("""
    SELECT
        seller_id,
        seller_zip_code_prefix,
        seller_city,
        seller_state
    FROM sellers;
""")

rows = cur_oltp.fetchall()
print(f"   Total sellers: {len(rows):,}")

cur_oltp.close()
conn_oltp.close()

# =====================================================
# 2. Insert ke warehouse
# =====================================================
print("💾 Insert ke dw.dim_sellers...")

conn_wh = psycopg2.connect(**DB_CONFIG_WAREHOUSE)
cur_wh = conn_wh.cursor()

cur_wh.executemany("""
    INSERT INTO dw.dim_sellers
    (seller_id, seller_zip_code_prefix, seller_city, seller_state)
    VALUES (%s, %s, %s, %s)
    ON CONFLICT (seller_id) DO NOTHING;
""", rows)

conn_wh.commit()
print(f"✅ Selesai. Cek database untuk hasil.")

cur_wh.close()
conn_wh.close()