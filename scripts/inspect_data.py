import pandas as pd
import os

# Folder tempat file CSV berada
DATA_DIR = "data/raw"

# Daftar file CSV
files = [
    "olist_customers_dataset.csv",
    "olist_geolocation_dataset.csv",
    "olist_order_items_dataset.csv",
    "olist_order_payments_dataset.csv",
    "olist_order_reviews_dataset.csv",
    "olist_orders_dataset.csv",
    "olist_products_dataset.csv",
    "olist_sellers_dataset.csv",
    "product_category_name_translation.csv"
]

for filename in files:
    path = os.path.join(DATA_DIR, filename)
    print("=" * 80)
    print(f"FILE: {filename}")
    print("=" * 80)

    df = pd.read_csv(path)

    print(f"Jumlah baris: {len(df):,}")
    print(f"Jumlah kolom: {len(df.columns)}")
    print(f"Kolom: {list(df.columns)}")
    print("\nContoh 3 baris:")
    print(df.head(3))
    print("\n")