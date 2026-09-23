import psycopg2
from config import DB_CONFIG_WAREHOUSE

conn = psycopg2.connect(**DB_CONFIG_WAREHOUSE)
conn.autocommit = True

cur = conn.cursor()

sql_file_path = "sql/01_create_schema.sql"

print(f"sedang membaca: {sql_file_path}")

with open (sql_file_path, "r", encoding="utf-8") as f:
    sql = f.read()

print("sedang menjalankan sql..")

cur.execute(sql)

print("✅ Schema dan tabel berhasil dibuat!")

cur.close()
conn.close()

