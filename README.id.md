# Olist E-Commerce Data Warehouse & ETL Pipeline (Bahasa Indonesia)

Proyek Data Engineering end-to-end yang mengekstrak data e-commerce mentah, memasukkannya ke database PostgreSQL OLTP, dan mentransformasikannya menjadi Data Warehouse (Star Schema). Seluruh pipeline sepenuhnya terisolasi menggunakan Docker.

## 🏗️ Arsitektur

```text
[File CSV Mentah]
      │
      ▼ (Python + Pandas)
[PostgreSQL OLTP] ──────── (Schema: public)
      │
      ▼ (Python + SQLAlchemy)
[PostgreSQL DW] ────────── (Schema: dw)
      │
      ▼
[Star Schema: Tabel Fact & Dimension]
```

## ✨ Fitur Utama

- **Environment Docker:** Jalankan seluruh sistem (PostgreSQL + App Python) hanya dengan satu perintah `docker-compose up -d`.
- **Auto-Initialize Schema:** Skema database, tabel, dan tabel watermark otomatis dibuat saat pertama kali dijalankan via `docker-entrypoint-initdb.d`.
- **Incremental Loading:** Mendukung pemrosesan per batch menggunakan tabel watermark (`dw.etl_watermark`) agar tidak memuat ulang data historis.
- **Kode Siap Produksi:** Menerapkan structured logging, error handling dengan retry, dan validasi data (mengecek NULL, duplikat, dan composite PK).
- **Desain Star Schema:** Dimensi ternormalisasi dan fakta terdenormalisasi untuk query analitik yang cepat.

## 🛠️ Tech Stack

- **Bahasa:** Python 3.13
- **Database:** PostgreSQL 18
- **Containerization:** Docker & docker-compose
- **Pengolahan Data:** Pandas
- **Database Toolkit:** SQLAlchemy & Psycopg2
- **Environment:** python-dotenv

## 📂 Struktur Proyek

```text
olist-warehouse/
├── data/
│   ├── raw/               # Letakkan 9 file CSV Olist di sini
│   └── batches/           # File batch bulanan yang di-generate (untuk incremental load)
├── scripts/
│   ├── docker-init.sh     # Script auto-init untuk PostgreSQL Docker
│   └── setup_warehouse.py # Membuat tabel DW (jika dijalankan manual)
├── sql/
│   └── 01_create_schema.sql # DDL untuk Star Schema & Watermark
├── src/
│   ├── utils/             # Logger, Retry decorator, Validation
│   ├── load_to_oltp.py    # Ekstrak & Load CSV ke OLTP
│   ├── load_dim_*.py      # Load tabel Dimension
│   ├── load_fact_*.py     # Load tabel Fact
│   └── load_warehouse_incremental.py # Loader batch incremental
├── Dockerfile
├── docker-compose.yml
└── requirements.txt
```

## 🚀 Cara Menjalankan (Step-by-Step)

### 1. Clone Repository

```bash
git clone https://github.com/jatiragil/olist-warehouse.git
cd olist-warehouse
```

### 2. Setup Environment

Copy file example environment. File ini berisi variabel untuk host dan Docker.

```bash
cp .env.example .env
```

### 3. Download Dataset

Proyek ini menggunakan Brazilian E-Commerce Public Dataset by Olist.

Download dataset dari Kaggle.

Ekstrak semua 9 file CSV ke dalam folder `data/raw/`.

### 4. Jalankan Container

Nyalakan PostgreSQL dan App Python di background.

```bash
docker-compose up -d
```

Catatan: Database dan Star Schema akan otomatis diinisialisasi oleh PostgreSQL pada saat pertama kali dijalankan.

### 5. Jalankan Pipeline ETL

Eksekusi pipeline di dalam container app.

**Load CSV ke OLTP:**

```bash
docker-compose exec app python -m src.load_to_oltp
```

**Build Dimensi:**

```bash
docker-compose exec app python -m src.load_dim_date
docker-compose exec app python -m src.load_dim_customers
docker-compose exec app python -m src.load_dim_products
docker-compose exec app python -m src.load_dim_sellers
```

**Build Fakta:**

```bash
docker-compose exec app python -m src.load_fact_orders
docker-compose exec app python -m src.load_fact_order_items
```

## 📊 Skema Data Warehouse

- **Tabel Dimensi:** `dim_date`, `dim_customers`, `dim_products`, `dim_sellers`
- **Tabel Fakta:** `fact_orders` (grain: 1 order), `fact_order_items` (grain: 1 item)
- **Tracking ETL:** `etl_watermark`

## 📝 Catatan Pengembangan & Pembelajaran

(Proyek ini dibangun dari nol sebagai bagian dari perjalanan belajar Data Engineering)

- **Composite Primary Keys:** Memperbaiki false positive pada validasi dengan mengimplementasikan penanganan `pk_columns` untuk tabel seperti `fact_order_items`.
- **Pemisahan Schema:** Memisahkan secara ketat schema OLTP (`public`) dan Data Warehouse (`dw`) agar query analitik tidak mengganggu tabel transaksional.
- **Volume Mount PostgreSQL 18:** Beradaptasi dengan struktur direktori data PostgreSQL 18 yang baru (`/var/lib/postgresql` alih-alih `/var/lib/postgresql/data`).
