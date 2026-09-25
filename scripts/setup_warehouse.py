import psycopg2
from config import DB_CONFIG_WAREHOUSE
from src.utils.logger import get_logger

logger = get_logger(__name__)

conn = psycopg2.connect(**DB_CONFIG_WAREHOUSE)
conn.autocommit = True
cur = conn.cursor()

sql_file_path = "sql/01_create_schema.sql"

logger.info(f"Membaca: {sql_file_path}")

with open (sql_file_path, "r", encoding="utf-8") as f:
    sql = f.read()

logger.info("Menjalankan sql..")

cur.execute(sql)

logger.info("Schema dan tabel berhasil dibuat.")

cur.close()
conn.close()

