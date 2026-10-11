import os
from dotenv import load_dotenv

load_dotenv()

DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")

DB_OLTP = os.getenv("DB_OLTP")
DB_WAREHOUSE = os.getenv("DB_WAREHOUSE")

OLTP_URL = f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_OLTP}"
WAREHOUSE_URL = f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_WAREHOUSE}"



DB_CONFIG_OLTP = {
    "host": DB_HOST,
    "port": DB_PORT,
    "database": DB_OLTP,
    "user": DB_USER,
    "password": DB_PASSWORD
}

DB_CONFIG_WAREHOUSE = {
    "host": DB_HOST,
    "port": DB_PORT,
    "database": DB_WAREHOUSE,
    "user": DB_USER,
    "password": DB_PASSWORD
}