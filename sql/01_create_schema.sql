-- =====================================================
-- Schema: dw (Data Warehouse)
-- Database: olist_warehouse
-- File: 01_create_schema.sql
-- Deskripsi: Setup Star Schema untuk data Olist
-- =====================================================

-- Buat schema khusus untuk warehouse
CREATE SCHEMA IF NOT EXISTS dw;

-- =====================================================
-- DIMENSION: dim_customers
-- =====================================================
CREATE TABLE IF NOT EXISTS dw.dim_customers (
    customer_key SERIAL PRIMARY KEY,
    customer_unique_id VARCHAR(50) NOT NULL UNIQUE,
    customer_zip_code_prefix INTEGER,
    customer_city VARCHAR(50),
    customer_state VARCHAR(10)
);

-- =====================================================
-- DIMENSION: dim_products
-- =====================================================
CREATE TABLE IF NOT EXISTS dw.dim_products (
    product_key SERIAL PRIMARY KEY,
    product_id VARCHAR(50) NOT NULL UNIQUE,
    category_pt VARCHAR(50),
    category_en VARCHAR(50),
    weight_g INTEGER,
    length_cm NUMERIC(10, 2),
    height_cm NUMERIC(10, 2),
    width_cm NUMERIC(10, 2)
);

-- =====================================================
-- DIMENSION: dim_sellers
-- =====================================================
CREATE TABLE IF NOT EXISTS dw.dim_sellers (
    seller_key SERIAL PRIMARY KEY,
    seller_id VARCHAR(50) NOT NULL UNIQUE,
    seller_zip_code_prefix INTEGER,
    seller_city VARCHAR(50),
    seller_state VARCHAR(10)
);

-- =====================================================
-- DIMENSION: dim_date
-- =====================================================
CREATE TABLE IF NOT EXISTS dw.dim_date (
    date_key INTEGER PRIMARY KEY,
    full_date DATE NOT NULL,
    year INTEGER NOT NULL,
    quarter INTEGER NOT NULL,
    month INTEGER NOT NULL,
    month_name VARCHAR(20) NOT NULL,
    day INTEGER NOT NULL,
    day_of_week INTEGER NOT NULL,
    day_name VARCHAR(20) NOT NULL,
    is_weekend BOOLEAN NOT NULL
);

-- =====================================================
-- FACT: fact_orders (grain: 1 order)
-- =====================================================
CREATE TABLE IF NOT EXISTS dw.fact_orders (
    order_id VARCHAR(50) PRIMARY KEY,
    customer_key INTEGER NOT NULL REFERENCES dw.dim_customers(customer_key),
    date_key INTEGER NOT NULL REFERENCES dw.dim_date(date_key),
    order_status VARCHAR(20),
    payment_type VARCHAR(100),
    total_item_price NUMERIC(10, 2),
    total_freight_value NUMERIC(10, 2),
    total_payment_value NUMERIC(10, 2),
    max_payment_installments INTEGER,
    total_items_count INTEGER,
    etl_loaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- =====================================================
-- FACT: fact_order_items (grain: 1 order item)
-- =====================================================
CREATE TABLE IF NOT EXISTS dw.fact_order_items (
    order_id VARCHAR(50) NOT NULL,
    order_item_id INTEGER NOT NULL,
    product_key INTEGER NOT NULL REFERENCES dw.dim_products(product_key),
    seller_key INTEGER NOT NULL REFERENCES dw.dim_sellers(seller_key),
    date_key INTEGER NOT NULL REFERENCES dw.dim_date(date_key),
    order_status VARCHAR(20),
    price NUMERIC(10, 2),
    freight_value NUMERIC(10, 2),
    etl_loaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (order_id, order_item_id)
   
);