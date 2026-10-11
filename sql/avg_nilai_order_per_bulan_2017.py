import psycopg2
from config import DB_CONFIG_WAREHOUSE

conn = psycopg2.connect(**DB_CONFIG_WAREHOUSE)
cur = conn.cursor()

query = """
SELECT 
    d.year,
    d.month,
    d.month_name,
    COUNT(*) AS jumlah_order,
    AVG(f.total_payment_value) AS rata_rata_order
FROM dw.fact_orders f
JOIN dw.dim_date d ON f.date_key = d.date_key
WHERE d.year = 2017
GROUP BY d.year, d.month, d.month_name
ORDER BY d.month;
"""

cur.execute(query)
rows = cur.fetchall()

print("Rata-rata Nilai Order per Bulan Tahun 2017:")
print(f"{'Tahun':<10} {'Bulan':<10} {'Nama Bulan':<15} {'Jumlah Order':>15} {'Rata-rata Order':>20}")
print("-" * 80)
for row in rows:
    print(f"{row[0]:<10} {row[1]:<10} {row[2]:<15} {row[3]:>15,} {row[4]:>20,.2f}")

cur.close()
conn.close()