import streamlit as st
import pandas as pd
import plotly.express as px
from sqlalchemy import create_engine, text
import os
from dotenv import load_dotenv

# =====================================================
# 1. Configuration
# =====================================================
load_dotenv()

# Build connection URL from environment variables
DB_URL = f"postgresql+psycopg2://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_WAREHOUSE')}"
engine = create_engine(DB_URL)

# Page config
st.set_page_config(
    page_title="Olist E-Commerce Dashboard",
    page_icon="📊",
    layout="wide"
)

# =====================================================
# 2. Data Loading
# =====================================================
@st.cache_data
def load_kpi_data():
    query = """
        SELECT 
            COUNT(DISTINCT order_id) AS total_orders,
            SUM(total_payment_value) AS total_revenue
        FROM dw.fact_orders
        WHERE order_status = 'delivered';
    """
    return pd.read_sql(query, engine)

@st.cache_data
def load_monthly_sales():
    query = """
        SELECT 
            d.year,
            d.month,
            d.month_name,
            SUM(f.total_payment_value) AS revenue
        FROM dw.fact_orders f
        JOIN dw.dim_date d ON f.date_key = d.date_key
        WHERE d.year = 2017
        GROUP BY d.year, d.month, d.month_name
        ORDER BY d.month;
    """
    return pd.read_sql(query, engine)

@st.cache_data
def load_top_categories():
    query = """
        SELECT 
            p.category_en,
            SUM(f.price) AS revenue
        FROM dw.fact_order_items f
        JOIN dw.dim_products p ON f.product_key = p.product_key
        WHERE p.category_en IS NOT NULL
        GROUP BY p.category_en
        ORDER BY revenue DESC
        LIMIT 10;
    """
    return pd.read_sql(query, engine)

@st.cache_data
def load_top_customers():
    query = """
        SELECT 
            c.customer_unique_id,
            c.customer_city,
            SUM(f.total_payment_value) AS total_spent
        FROM dw.fact_orders f
        JOIN dw.dim_customers c ON f.customer_key = c.customer_key
        GROUP BY c.customer_unique_id, c.customer_city
        ORDER BY total_spent DESC
        LIMIT 10;
    """
    return pd.read_sql(query, engine)

# =====================================================
# 3. Header & KPI Cards
# =====================================================
st.title("📊 Olist E-Commerce Dashboard")
st.markdown("**Business Intelligence dashboard** — powered by PostgreSQL & Streamlit")

kpi = load_kpi_data()
col1, col2 = st.columns(2)
col1.metric("Total Delivered Orders", f"{int(kpi['total_orders'][0]):,}")
col2.metric("Total Revenue (Delivered)", f"${kpi['total_revenue'][0]:,.2f}")

st.divider()

# =====================================================
# 4. Monthly Sales Chart (2017)
# =====================================================
st.subheader("📈 Monthly Revenue Trend (2017)")
df_monthly = load_monthly_sales()
fig = px.line(
    df_monthly, 
    x="month_name", 
    y="revenue",
    markers=True,
    title="Monthly Revenue in 2017"
)
fig.update_layout(xaxis_title="Month", yaxis_title="Revenue (USD)")
st.plotly_chart(fig, use_container_width=True)

st.divider()

# =====================================================
# 5. Top Categories & Top Customers
# =====================================================
col_left, col_right = st.columns(2)

with col_left:
    st.subheader("🏆 Top 10 Product Categories")
    df_categories = load_top_categories()
    fig2 = px.bar(
        df_categories,
        x="revenue",
        y="category_en",
        orientation="h",
        title="Revenue by Category"
    )
    fig2.update_layout(yaxis_title="Category", xaxis_title="Revenue (USD)")
    st.plotly_chart(fig2, use_container_width=True)

with col_right:
    st.subheader("👑 Top 10 Loyal Customers")
    df_customers = load_top_customers()
    st.dataframe(
        df_customers.rename(columns={
            "customer_unique_id": "Customer ID",
            "customer_city": "City",
            "total_spent": "Total Spent (USD)"
        }),
        use_container_width=True
    )
