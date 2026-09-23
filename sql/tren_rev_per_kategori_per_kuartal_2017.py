import psycopg2
from config import DB_CONFIG_WAREHOUSE

conn = psycopg2.connect(**DB_CONFIG_WAREHOUSE)
cur = conn.cursor()

query = """
SELECT
    d.year,
    d.quarter,
    p.category_en,
    COALESCE(SUM(f.price), 0) AS total_rev,
    COUNT(*) AS jumlah_items
FROM dw.fact_order_items f
JOIN dw.dim_products p ON f.product_key = p.product_key
JOIN dw.dim_date d ON f.date_key = d.date_key
WHERE d.year = 2017
  AND p.category_en IS NOT NULL
GROUP BY d.year, d.quarter, p.category_en
ORDER BY p.category_en, d.quarter;
"""

cur.execute(query)
rows = cur.fetchall()

print("Tren Revenue per Kategori per Kuartal 2017:")
print(f"{'Tahun':<8} {'Kuartal':<10} {'Kategori':<25} {'Total Revenue':>18} {'Jumlah Item':>12}")
print("-" * 75)
for row in rows:
    print(f"{row[0]:<8} {row[1]:<10} {row[2]:<25} {row[3]:>18,.2f} {row[4]:>12,}")

cur.close()
conn.close()