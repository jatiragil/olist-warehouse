import psycopg2
from config import DB_CONFIG_OLTP, DB_CONFIG_WAREHOUSE
from src.utils.logger import get_logger
from src.utils.validation import validate_rows

logger = get_logger(__name__)


# Extract: baca customer unik dari OLTP
# ======================================

logger.info("Baca data customers dari OLTP")

conn_oltp = psycopg2.connect(**DB_CONFIG_OLTP)
cur_oltp = conn_oltp.cursor()

cur_oltp.execute("""
    SELECT DISTINCT ON (customer_unique_id)
        customer_unique_id,
        customer_zip_code_prefix,
        customer_city,
        customer_state
    FROM customers
    ORDER BY customer_unique_id, customer_id;
""")

rows = cur_oltp.fetchall()
logger.info(f"Total customer unik: {len(rows):,}")

cur_oltp.close()
conn_oltp.close()

# Validasi
# ========
validate_rows(
    rows,
    "dw.dim_customers",
    pk_columns=[0],
    not_null_columns=[0],
)

# Load: insert ke dw.dim_customers
# ================================

logger.info("Insert ke dw.dim_customers")

conn_wh = psycopg2.connect(**DB_CONFIG_WAREHOUSE)
cur_wh = conn_wh.cursor()

cur_wh.executemany("""
    INSERT INTO dw.dim_customers
    (customer_unique_id, customer_zip_code_prefix, customer_city, customer_state)
    VALUES (%s, %s, %s, %s)
    ON CONFLICT (customer_unique_id) DO NOTHING;
""", rows)

conn_wh.commit()
logger.info("Selesai. Cek database untuk hasil")

cur_wh.close()
conn_wh.close()