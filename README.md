# Olist E-Commerce Data Warehouse & ETL Pipeline

An end-to-end Data Engineering project that extracts raw e-commerce data, loads it into a PostgreSQL OLTP database, and transforms it into a Star Schema Data Warehouse. The entire pipeline is fully containerized using Docker.

## 🏗️ Architecture

```text
[Raw CSV Files]
      │
      ▼ (Python + Pandas)
[PostgreSQL OLTP] ──────── (Schema: public)
      │
      ▼ (Python + SQLAlchemy)
[PostgreSQL DW] ────────── (Schema: dw)
      │
      ▼
[Star Schema: Fact & Dimension Tables]
```

## ✨ Key Features

- **Dockerized Environment:** Run the entire stack (PostgreSQL + Python App) with a single `docker-compose up -d`.
- **Auto-Initialized Schema:** Database schemas, tables, and watermark trackers are automatically created on the first run via `docker-entrypoint-initdb.d`.
- **Incremental Loading:** Supports batch processing using a watermark table (`dw.etl_watermark`) to prevent reloading historical data.
- **Production-Ready Code:** Implements structured logging, error handling with retries, and data validation (checking for NULLs, duplicates, and composite Pks).
- **Star Schema Design:** Normalized dimensions and denormalized facts for fast analytical queries.

## 🛠️ Tech Stack

- **Language:** Python 3.13
- **Database:** PostgreSQL 18
- **Containerization:** Docker & docker-compose
- **Data Processing:** Pandas
- **Database Toolkit:** SQLAlchemy & Psycopg2
- **Environment:** python-dotenv

## 📂 Project Structure

```text
olist-warehouse/
├── data/
│   ├── raw/               # Place the 9 Olist CSV files here
│   └── batches/           # Generated monthly batch files (for incremental load)
├── scripts/
│   ├── docker-init.sh     # Auto-init script for Docker PostgreSQL
│   └── setup_warehouse.py # Creates DW tables (if run manually)
├── sql/
│   └── 01_create_schema.sql # DDL for Star Schema & Watermark
├── src/
│   ├── utils/             # Logger, Retry decorator, Validation
│   ├── load_to_oltp.py    # Extract & Load CSV to OLTP
│   ├── load_dim_*.py      # Load Dimension tables
│   ├── load_fact_*.py     # Load Fact tables
│   └── load_warehouse_incremental.py # Incremental batch loader
├── Dockerfile
├── docker-compose.yml
└── requirements.txt
```

## 🚀 How to Run (Step-by-Step)

### 1. Clone the Repository

```bash
git clone https://github.com/jatiragil/olist-warehouse.git
cd olist-warehouse
```

### 2. Setup Environment

Copy the example environment file. It contains both host and Docker variables.

```bash
cp .env.example .env
```

### 3. Download the Dataset

This project uses the Brazilian E-Commerce Public Dataset by Olist.
Download the dataset from Kaggle.
Extract all 9 CSV files into the `data/raw/` directory.

### 4. Start the Containers

Spin up PostgreSQL and the Python App container in detached mode.

```bash
docker-compose up -d
```

Note: The database and the Star Schema will be automatically initialized by PostgreSQL on the first run.

### 5. Run the ETL Pipeline

Execute the pipelines inside the running app container.

**Load CSV to OLTP:**

```bash
docker-compose exec app python -m src.load_to_oltp
```

**Build Dimensions:**

```bash
docker-compose exec app python -m src.load_dim_date
docker-compose exec app python -m src.load_dim_customers
docker-compose exec app python -m src.load_dim_products
docker-compose exec app python -m src.load_dim_sellers
```

**Build Facts:**

```bash
docker-compose exec app python -m src.load_fact_orders
docker-compose exec app python -m src.load_fact_order_items
```

## 📊 Data Warehouse Schema

- **Dimension Tables:** `dim_date`, `dim_customers`, `dim_products`, `dim_sellers`
- **Fact Tables:** `fact_orders` (grain: 1 order), `fact_order_items` (grain: 1 item)
- **ETL Tracking:** `etl_watermark`

## 📝 Development Notes & Lessons Learned

(This project was built from scratch as part of a Data Engineering learning path)

- **Composite Primary Keys:** Fixed false positives in validation by implementing pk_columns handling for tables like fact_order_items.
- **Schema Separation:** Strictly separated OLTP (public) and Data Warehouse (dw) schemas to prevent analytical queries from scanning transactional tables.
- **PostgreSQL 18 Volume Mount:** Adapted to the new PostgreSQL 18 data directory structure (/var/lib/postgresql instead of /var/lib/postgresql/data)
