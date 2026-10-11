import psycopg2
from config import DB_CONFIG_WAREHOUSE

conn = psycopg2.connect(**DB_CONFIG_WAREHOUSE)
cur = conn.cursor()

query = """
SELECT
    s.seller_id,
    s.seller_state,
    SUM(f.price) AS total_revenue,
    COUNT(*) AS jumlah_item
FROM dw.fact_order_items f
JOIN dw.dim_sellers s ON f.seller_key = s.seller_key
GROUP BY s.seller_id, s.seller_state
ORDER BY SUM(f.price) DESC
LIMIT 10;
"""
cur.execute(query)
rows = cur.fetchall()

print("Top 10 Penjual berdasarkan Revenue:")
print(f"{'Seller ID':<30} {'Seller State':<15} {'Revenue':>15} {'Item':>10}")
print("-" * 80)
for row in rows:
    print(f"{row[0]:<30} {row[1]:<15} {row[2]:>15,.2f} {row[3]:>10,}") 

cur.close()
conn.close()