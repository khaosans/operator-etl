CREATE OR REPLACE TABLE gold_volume_daily AS
SELECT
    CAST(ordered_at AS DATE) AS order_date,
    COUNT(*) AS orders,
    ROUND(SUM(amount), 2) AS revenue
FROM silver_orders
GROUP BY 1
ORDER BY 1;
