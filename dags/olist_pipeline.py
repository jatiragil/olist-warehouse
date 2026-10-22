from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.bash import BashOperator

# 1. Default Arguments
default_args = {
    'owner': 'jati',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=1),
}

# 2. Define DAG
with DAG(
    dag_id='olist_etl_pipeline',
    default_args=default_args,
    description='End-to-End ETL Pipeline from CSV to Data Warehouse',
    schedule_interval=None,  # Only run when manually triggered
    start_date=datetime(2024, 1, 1),
    catchup=False,
    tags=['olist', 'etl', 'production'],
) as dag:

    # 3. Task Definitions
    # Note: We use python3 to avoid "command not found" in the container
    # cwd='/opt/airflow' ensures we are at the project root

    load_to_oltp = BashOperator(
        task_id='load_to_oltp',
        bash_command='python3 -m src.load_to_oltp',
        cwd='/opt/airflow',
    )

    load_dim_date = BashOperator(
        task_id='load_dim_date',
        bash_command='python3 -m src.load_dim_date',
        cwd='/opt/airflow',
    )

    load_dim_customers = BashOperator(
        task_id='load_dim_customers',
        bash_command='python3 -m src.load_dim_customers',
        cwd='/opt/airflow',
    )

    load_dim_products = BashOperator(
        task_id='load_dim_products',
        bash_command='python3 -m src.load_dim_products',
        cwd='/opt/airflow',
    )

    load_dim_sellers = BashOperator(
        task_id='load_dim_sellers',
        bash_command='python3 -m src.load_dim_sellers',
        cwd='/opt/airflow',
    )

    load_fact_orders = BashOperator(
        task_id='load_fact_orders',
        bash_command='python3 -m src.load_fact_orders',
        cwd='/opt/airflow',
    )

    load_fact_order_items = BashOperator(
        task_id='load_fact_order_items',
        bash_command='python3 -m src.load_fact_order_items',
        cwd='/opt/airflow',
    )

    # 4. Define Dependencies (Pipeline Flow)
    # Step 1: Load raw data to OLTP
    # Step 2: Build all Dimensions (can run in parallel or sequence)
    # Step 3: Build Facts (requires Dimensions to be ready)
    
    load_to_oltp >> [load_dim_date, load_dim_customers, load_dim_products, load_dim_sellers]
    
    # We can chain the facts after the dimensions are done
    [load_dim_date, load_dim_customers, load_dim_products, load_dim_sellers] >> load_fact_orders >> load_fact_order_items