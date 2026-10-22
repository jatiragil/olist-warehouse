FROM apache/airflow:2.9.2-python3.11
# Install library tambahan untuk pipeline kita
RUN pip install --no-cache-dir psycopg2-binary python-dotenv requests
