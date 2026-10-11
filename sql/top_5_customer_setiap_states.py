import psycopg2
from config import DB_CONFIG_WAREHOUSE

conn = psycopg2.connect(**DB_CONFIG_WAREHOUSE)
cur = conn.cursor()

query = """
WITH customer_revenue AS (
    SELECT
        c.customer_unique_id,
        c.customer_state,
        COALESCE(SUM(f.total_payment_value), 0) AS total_revenue,
        COUNT(*) AS jumlah_order
    FROM dw.fact_orders f
    JOIN dw.dim_customers c ON f.customer_key = c.customer_key
    GROUP BY c.customer_unique_id, c.customer_state
),
ranked AS (
    SELECT
        customer_unique_id,
        customer_state,
        total_revenue,
        jumlah_order,
        RANK() OVER (PARTITION BY customer_state ORDER BY total_revenue DESC) AS rank_per_state
    FROM customer_revenue
)
SELECT
    customer_unique_id,
    customer_state,
    total_revenue,
    jumlah_order
FROM ranked
WHERE rank_per_state <= 5
ORDER BY customer_state, rank_per_state;
"""

cur.execute(query)
rows = cur.fetchall()

print("Top 5 Customer per State berdasarkan Revenue:")
print(f"{'Customer ID':<35} {'State':<8} {'Revenue':>15} {'Order':>8}")
print("-" * 70)
for row in rows:
    print(f"{row[0]:<35} {row[1]:<8} {row[2]:>15,.2f} {row[3]:>8,}")

cur.close()
conn.close()