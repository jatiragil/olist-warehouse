import psycopg2
from config import DB_CONFIG_WAREHOUSE

conn = psycopg2.connect(**DB_CONFIG_WAREHOUSE)
cur = conn.cursor()

query = """
SELECT
    p.category_en,
    SUM(f.price) AS total_revenue,
    COUNT(*) AS jumlah_item
FROM dw.fact_order_items f
JOIN dw.dim_products p ON f.product_key = p.product_key
WHERE p.category_en IS NOT NULL
GROUP BY p.category_en
ORDER BY total_revenue DESC
LIMIT 10;
"""

cur.execute(query)
rows = cur.fetchall()

print("Top 10 Kategori Produk berdasarkan Revenue:")
print(f"{'Kategori':<30} {'Revenue':>15} {'Item':>10}")
print("-" * 60)
for row in rows:
    print(f"{row[0]:<30} {row[1]:>15,.2f} {row[2]:>10,}")

cur.close()
conn.close()