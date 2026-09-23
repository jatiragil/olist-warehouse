import psycopg2
from config import DB_CONFIG_OLTP

conn = psycopg2.connect(**DB_CONFIG_OLTP)
cur = conn.cursor()

# Cari tanggal paling awal dan paling akhir
query = """
SELECT 
    MIN(order_purchase_timestamp)::DATE AS tanggal_awal,
    MAX(order_purchase_timestamp)::DATE AS tanggal_akhir
FROM orders
WHERE order_purchase_timestamp IS NOT NULL;
"""

cur.execute(query)
result = cur.fetchone()

print(f"Tanggal awal  : {result[0]}")
print(f"Tanggal akhir : {result[1]}")

cur.close()
conn.close()