#!/bin/bash
set -e

echo "=== Docker init: creating olist_warehouse database ==="

# Create warehouse database
psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
    CREATE DATABASE olist_warehouse;
EOSQL

echo "=== Docker init: applying schema to olist_warehouse ==="

# Apply schema to warehouse database
psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "olist_warehouse" -f /docker-init/01_create_schema.sql

echo "=== Docker init: done ==="
