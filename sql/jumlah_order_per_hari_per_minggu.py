import psycopg2
from config import DB_CONFIG_WAREHOUSE

conn = psycopg2.connect(**DB_CONFIG_WAREHOUSE)
cur = conn.cursor()

query = """
SELECT
    d.day_name AS nama_hari,
    d.day_of_week AS nomor_hari,
    COUNT(*) AS jumlah_order
FROM dw.fact_orders f
JOIN dw.dim_date d ON f.date_key = d.date_key
GROUP BY d.day_name, d.day_of_week
ORDER BY d.day_of_week;
"""

cur.execute(query)
rows = cur.fetchall()

print("Jumlah Order per Hari dalam Seminggu:")
print(f"{'Nama Hari':<15} {'Nomor Hari':<15} {'Jumlah Order':>15}")
print("-" * 50)
for row in rows:
    print(f"{row[0]:<15} {row[1]:<15} {row[2]:>15,}")

cur.close()
conn.close()