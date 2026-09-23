from datetime import date, timedelta
import psycopg2
from config import DB_CONFIG_WAREHOUSE, DB_CONFIG_OLTP

# =====================================================
# 1. Cari rentang tanggal dari OLTP
# =====================================================
print("🔍 Cari rentang tanggal dari OLTP...")

conn_oltp = psycopg2.connect(**DB_CONFIG_OLTP)
cur_oltp = conn_oltp.cursor()

cur_oltp.execute("""
    SELECT 
        MIN(order_purchase_timestamp)::DATE,
        MAX(order_purchase_timestamp)::DATE
    FROM orders
    WHERE order_purchase_timestamp IS NOT NULL;
""")

tanggal_awal, tanggal_akhir = cur_oltp.fetchone()
print(f"   Rentang: {tanggal_awal} sampai {tanggal_akhir}")

cur_oltp.close()
conn_oltp.close()

# =====================================================
# 2. Generate semua tanggal
# =====================================================
print("📅 Generate daftar tanggal...")

DAFTAR_HARI = ["Senin", "Selasa", "Rabu", "Kamis", "Jumat", "Sabtu", "Minggu"]
DAFTAR_BULAN = [
    "", "Januari", "Februari", "Maret", "April", "Mei", "Juni",
    "Juli", "Agustus", "September", "Oktober", "November", "Desember"
]

rows = []
tanggal = tanggal_awal

while tanggal <= tanggal_akhir:
    date_key = int(tanggal.strftime("%Y%m%d"))
    year = tanggal.year
    month = tanggal.month
    day = tanggal.day
    quarter = (month - 1) // 3 + 1
    day_of_week = tanggal.weekday()
    day_name = DAFTAR_HARI[day_of_week]
    month_name = DAFTAR_BULAN[month]
    is_weekend = day_of_week >= 5

    rows.append((
        date_key, tanggal, year, quarter, month,
        month_name, day, day_of_week, day_name, is_weekend
    ))

    tanggal += timedelta(days=1)

print(f"   Total hari: {len(rows)}")

# =====================================================
# 3. Insert ke dw.dim_date
# =====================================================
print("💾 Insert ke dw.dim_date...")

conn_wh = psycopg2.connect(**DB_CONFIG_WAREHOUSE)
cur_wh = conn_wh.cursor()

cur_wh.executemany("""
    INSERT INTO dw.dim_date
    (date_key, full_date, year, quarter, month, month_name,
     day, day_of_week, day_name, is_weekend)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    ON CONFLICT (date_key) DO NOTHING;
""", rows)

conn_wh.commit()
print(f"✅ Selesai. Cek database untuk hasil.")

cur_wh.close()
conn_wh.close()