import psycopg2
from config import DB_CONFIG_WAREHOUSE

conn = psycopg2.connect(**DB_CONFIG_WAREHOUSE)
cur = conn.cursor()

query = """
WITH penjualan_bulanan AS(
SELECT
    d.year,
    d.month,
    d.month_name,
    SUM(f.total_payment_value) AS total_bulanan
FROM dw.fact_orders f
JOIN dw.dim_date d ON f.date_key = d.date_key
WHERE d.year = 2017
GROUP BY d.year, d.month, d.month_name
)
SELECT
    year,
    month,
    month_name,
    total_bulanan,
    SUM(total_bulanan) OVER(ORDER BY month) AS kumulatif
FROM penjualan_bulanan
ORDER BY month;
"""

cur.execute(query)
rows = cur.fetchall()

print("Penjualan Bulanan & Kumulatif Tahun 2017:")
print(f"{'Bulan':<12} {'Bulan Ini':>15} {'Kumulatif':>15}")
print("-" * 45)
for row in rows:
    print(f"{row[2]:<12} {row[3]:>15,.2f} {row[4]:>15,.2f}")

cur.close()
conn.close()