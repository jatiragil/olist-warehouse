import pandas as pd
from sqlalchemy import create_engine, text
from config import OLTP_URL

engine = create_engine(OLTP_URL)

# Daftar tabel yang dicek
TABLES = [
    "customers",
    "geolocation",
    "order_items",
    "order_payments",
    "order_reviews",
    "orders",
    "products",
    "sellers",
    "category_translation"
]

print("Jumlah baris per tabel di PostgreSQL:\n")

with engine.connect() as conn:
    for table in TABLES:
        result = conn.execute(text(f"SELECT COUNT(*) FROM {table}"))
        count = result.scalar()
        print(f"  {table:25} → {count:>10,} baris")