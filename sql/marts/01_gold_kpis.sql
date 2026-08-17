CREATE OR REPLACE TABLE gold_kpis AS
SELECT
    COUNT(*) AS order_count,
    COUNT(DISTINCT customer_id) AS customer_count,
    ROUND(SUM(amount), 2) AS revenue,
    ROUND(AVG(amount), 2) AS avg_order,
    MAX(ordered_at) AS latest_order_at,
    MAX(_ingested_at) AS freshness_at
FROM silver_orders;
