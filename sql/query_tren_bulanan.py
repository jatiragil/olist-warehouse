import psycopg2
from config import DB_CONFIG_WAREHOUSE

conn = psycopg2.connect(**DB_CONFIG_WAREHOUSE)
cur_wh = conn.cursor()

cur_wh.execute("""
SELECT 
d.year, 
d.month, 
d.month_name,
SUM(f.total_item_price) AS total_penjualan,
COUNT (*) AS jumlah_order
FROM dw.fact_orders f
JOIN dw.dim_date d ON f.date_key = d.date_key
WHERE d.year = 2017
GROUP BY d.year, d.month, d.month_name
ORDER BY d.month;
"""
)

rows = cur_wh.fetchall()
print("Tren Penjualan 2017:")
print(f"{'Bulan':<15} {'Penjualan':>15} {'Order':>10}")
print("-" * 45)
for row in rows:
    print(f"{row[2]:<15} {row[3]:>15,.2f} {row[4]:>10,}")

cur_wh.close()
conn.close()
