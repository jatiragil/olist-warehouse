# Olist E-Commerce Data Warehouse & ETL Pipeline (Bahasa Indonesia)

Proyek Data Engineering End-to-End: Dari file CSV Kaggle mentah hingga menjadi Dashboard Interaktif yang Otomatis.

## 📸 Pratinjau Dashboard

![Dashboard Top](docs/images/dashboard-top.png)

*Key Performance Indicators dan Tren Pendapatan Bulanan (2017).*

![Dashboard Bottom](docs/images/dashboard-bottom.png)

*Top 10 Kategori Produk dan Top 10 Pelanggan Paling Loyal.*

## 🏗️ Diagram Arsitektur

```text
┌─────────────────┐
│  File CSV Mentah│
└────────┬────────┘
         │
         ▼  (Python + Pandas + SQLAlchemy)
┌─────────────────┐
│ PostgreSQL OLTP │ (Database Operasional)
└────────┬────────┘
         │
         ▼  (Transformasi Star Schema)
┌─────────────────┐
│  Data Warehouse │ (Tabel Fact & Dimension)
└────────┬────────┘
         │
         ▼  (Apache Airflow - LocalExecutor)
┌─────────────────┐
│  Orkestrasi ETL │ (Pipeline Otomatis)
└────────┬────────┘
         │
         ▼  (Streamlit + Plotly)
┌─────────────────┐
│    Dashboard    │ (Business Intelligence)
└─────────────────┘
```

## ⚙️ Orkestrasi Pipeline Airflow

Proses ETL sepenuhnya otomatis dan diorkestrasi menggunakan Apache Airflow. DAG mengatur dependensi, memastikan tabel dimensi dibangun sebelum tabel fakta.

![Airflow Graph](docs/images/airflow-graph.png)

## 🛠️ Tech Stack & Struktur

### Tech Stack

- Bahasa: Python 3.13
- Database: PostgreSQL 18
- Orkestrasi: Apache Airflow 2.9.2
- Visualisasi: Streamlit & Plotly
- Containerization: Docker & Docker Compose
- Pengolahan Data: Pandas & SQLAlchemy

## 📂 Struktur Folder

```text
olist-warehouse/
├── dags/                  # Definisi DAG Apache Airflow
├── dashboard/             # Aplikasi Streamlit (app.py, Dockerfile)
├── data/
│   ├── raw/               # Letakkan 9 file CSV Olist mentah di sini
│   └── batches/           # Batch bulanan yang di-generate (untuk incremental load)
├── scripts/
│   ├── docker-init.sh     # Script auto-init untuk PostgreSQL Docker
│   └── split_csv.py       # Utility untuk memecah data menjadi batch
├── sql/
│   └── 01_create_schema.sql # DDL untuk Star Schema & Watermark
├── src/
│   ├── utils/             # Logger, Retry decorator, Validation
│   ├── load_to_oltp.py    # Ekstrak & Load CSV ke OLTP
│   ├── load_dim_*.py      # Load tabel Dimension
│   ├── load_fact_*.py     # Load tabel Fact
│   └── load_warehouse_incremental.py # Loader batch incremental
├── airflow.Dockerfile     # Image Airflow kustom dengan dependensi
├── docker-compose.yml     # File orkestrasi utama
├── requirements.txt       # Dependensi Python utama
└── README.md
```

## ✨ Keputusan Teknis Penting (Engineering Decisions)

- **Isolasi Jaringan Docker:** Menggunakan environment variable Docker Compose untuk mengganti localhost menjadi nama service postgres. Ini memastikan script Python dan Airflow dapat menemukan alamat database dengan benar di dalam jaringan container.
- **Orkestrasi Ringan (LocalExecutor):** Memilih Airflow LocalExecutor dibanding CeleryExecutor untuk menghemat RAM (di bawah 1GB) dan menghindari kompleksitas infrastruktur yang tidak perlu untuk skala pipeline ini.
- **Auto-Initialize Schema:** Memanfaatkan `docker-entrypoint-initdb.d` untuk otomatis membuat database dan membangun Star Schema saat container pertama kali menyala, menjadikan environment zero-configuration.
- **Idempotent & Tahan Gangguan:** Menerapkan `ON CONFLICT DO NOTHING` dan Watermark Table kustom untuk memastikan pemuatan data incremental aman dari duplikasi meskipun pipeline mati dan menyala kembali.
- **Pencegahan Fan-out via Pre-aggregation:** Saat membangun `fact_orders`, tabel `order_items` dan `order_payments` diagregasi terlebih dahulu per `order_id` sebelum di-JOIN. Ini mencegah duplikasi data (fan-out) yang disebabkan oleh relasi one-to-many, memastikan grain fact table tetap ketat 1 baris per order.
- **Isolasi Inisialisasi Schema:** Mencegah kebocoran schema dengan me-mount script DDL ke direktori kustom (`/docker-init/`) alih-alih direktori default `docker-entrypoint-initdb.d`. Schema secara eksplisit hanya dieksekusi terhadap database `olist_warehouse`, menjaga `olist_oltp` tetap bersih.

## 🚀 Cara Menjalankan (Step-by-Step)

(Catatan: Kami menggunakan sintaks modern `docker compose`. Jika kamu menggunakan Docker Compose V1 lama, ganti dengan `docker-compose`)

### 1. Clone Repository

```bash
git clone https://github.com/jatiragil/olist-warehouse.git
cd olist-warehouse
```

### 2. Setup Environment

Copy file example environment dan isi kredensialmu.

```bash
cp .env.example .env
```

### 3. Download Dataset

Download [Brazilian E-Commerce Public Dataset by Olist](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce) dari Kaggle.

Ekstrak semua 9 file CSV ke dalam folder `data/raw/`.

### 4. Nyalakan Container

Nyalakan PostgreSQL, Airflow, dan Streamlit secara bersamaan.

```bash
docker compose up -d --build
```

### 5. Jalankan Pipeline ETL (via Airflow)

1. Buka Airflow di `http://localhost:8080` (User: `admin`, Pass: `admin`).
2. Unpause DAG `olist_etl_pipeline`.
3. Trigger DAG secara manual untuk menjalankan seluruh pipeline dari OLTP ke Data Warehouse.

### 6. Lihat Dashboard

Buka Streamlit di `http://localhost:8501` untuk melihat insight bisnis.

## 🧠 Tantangan Utama & Solusi (Key Challenges)

- **Jebakan "Localhost" di Docker:** Awalnya, script Python gagal terhubung ke database dari dalam container. Solusi: Mengganti localhost dengan nama service Docker postgres melalui environment variable.
- **Keterbatasan Resource (RAM 3GB):** Menjalankan CeleryExecutor bawaan Airflow membuat laptop freeze. Solusi: Beralih ke LocalExecutor dan memasukkan dependensi ke dalam Dockerfile kustom untuk mengurangi konsumsi memori dan waktu startup secara drastis.
- **Simulasi Incremental Load Produksi:** Dataset Kaggle bersifat statis dan tidak memiliki update harian. Solusi: Membuat `split_csv.py` kustom untuk mempartisi data menjadi batch bulanan dan mengimplementasikan Watermark Table (`etl_watermark`) untuk mendemonstrasikan pemrosesan batch yang tahan gangguan dan idempotent.
- **Realitas Kualitas Data:** Validasi mendeteksi 623 produk tanpa kategori dan 4 order tanpa item. Alih-alih menganggapnya sebagai error pipeline dan memaksakan nilai default, hal ini didokumentasikan sebagai karakteristik dataset yang sebenarnya, membuktikan bahwa validasi adalah tentang memahami data, bukan sekadar mencari bug.
- **Validasi Composite Key:** Logika validasi awal melaporkan 13.984 false duplicates (duplikat palsu) pada `fact_order_items`. Kemudian ditemukan bahwa validasi hanya memeriksa kolom pertama (`order_id`) alih-alih composite primary key (`order_id`, `item_id`). Memperbaiki query validasi menyelesaikan masalah false positive tersebut.

## 🧠 Fitur Lanjutan: Incremental Loading

Meskipun DAG Airflow menangani full load awal, proyek ini juga memiliki fitur Incremental Load. Pipeline dapat memecah CSV mentah menjadi batch bulanan dan memuatnya secara incremental menggunakan Watermark Table (`dw.etl_watermark`) via CLI. Ini mensimulasikan skenario produksi di mana data datang setiap hari.

## Penulis

Jati Ragil

- GitHub: [@jatiragil](https://github.com/jatiragil)
