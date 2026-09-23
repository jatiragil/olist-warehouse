import psycopg2
from config import DB_CONFIG_OLTP, DB_CONFIG_WAREHOUSE

# =====================================================
# 1. Baca data produk dari OLTP (JOIN dengan translation)
# =====================================================
print("🔍 Baca data produk dari OLTP...")

conn_oltp = psycopg2.connect(**DB_CONFIG_OLTP)
cur_oltp = conn_oltp.cursor()

cur_oltp.execute("""
    SELECT
        p.product_id,
        p.product_category_name AS category_pt,
        ct.product_category_name_english AS category_en,
        p.product_weight_g,
        p.product_length_cm,
        p.product_height_cm,
        p.product_width_cm
    FROM products p
    LEFT JOIN category_translation ct
        ON p.product_category_name = ct.product_category_name;
""")

rows = cur_oltp.fetchall()
print(f"   Total produk: {len(rows):,}")

cur_oltp.close()
conn_oltp.close()

# =====================================================
# 2. Insert ke warehouse
# =====================================================
print("💾 Insert ke dw.dim_products...")

conn_wh = psycopg2.connect(**DB_CONFIG_WAREHOUSE)
cur_wh = conn_wh.cursor()

cur_wh.executemany("""
    INSERT INTO dw.dim_products
    (product_id, category_pt, category_en, weight_g, length_cm, height_cm, width_cm)
    VALUES (%s, %s, %s, %s, %s, %s, %s)
    ON CONFLICT (product_id) DO NOTHING;
""", rows)

conn_wh.commit()
print(f"✅ Selesai. Cek database untuk hasil.")

cur_wh.close()
conn_wh.close()